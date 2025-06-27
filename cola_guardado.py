import json
import threading
from datetime import datetime
from mongo_repositorio import MongoRepositorio

class ColaGuardado:
    def __init__(self, nombre_entidad, archivo_cola=None):
        """
        Args:
            nombre_entidad: Nombre de la entidad (ej: "alumnos", "maestros", "grupos")
            archivo_cola: Nombre del archivo de cola (opcional, se genera automáticamente)
        """
        self.nombre_entidad = nombre_entidad
        if archivo_cola is None:
            self.archivo_cola = f"cola_guardado_{nombre_entidad}.json"
        else:
            self.archivo_cola = archivo_cola
        
        self.timer = None
        self.lock = threading.Lock()
        
    def agregar_a_cola(self, coleccion, datos):
     with self.lock:
        self._escribir_cola([{
            "coleccion": coleccion,
            "datos": datos,
            "timestamp": datetime.now().isoformat(),
            "entidad": self.nombre_entidad
        }])
        self._reiniciar_timer()

    
    def intentar_conexion(self):
        try:
            repo = MongoRepositorio()
            repo.test_connection()
            return True
        except Exception:
            return False
    
    def procesar_cola(self):
        with self.lock:
            if not self.intentar_conexion():
                print(f"Sin conexión a MongoDB para {self.nombre_entidad}. Reintentando en 20 segundos...")
                self._reiniciar_timer()
                return
            
            cola = self._leer_cola()
            if not cola:
                return
            
            try:
                repo = MongoRepositorio()
                for elemento in cola:
                    coleccion = elemento["coleccion"]
                    datos = elemento["datos"]
                    entidad = elemento.get("entidad", self.nombre_entidad)
                    repo.guardar_todos(coleccion, datos)
                    print(f"Sincronizado ({entidad}): {len(datos)} elementos en {coleccion}")
                
                self._escribir_cola([])
                print(f"Cola de {self.nombre_entidad} procesada exitosamente y limpiada")
                
                if self.timer:
                    self.timer.cancel()
                    self.timer = None
                    
            except Exception as e:
                print(f"Error al procesar cola de {self.nombre_entidad}: {e}")
                print(f"Reintentando cola de {self.nombre_entidad} en 20 segundos...")
                self._reiniciar_timer()
    
    def _leer_cola(self):
        try:
            with open(self.archivo_cola, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _escribir_cola(self, cola):
        with open(self.archivo_cola, 'w') as f:
            json.dump(cola, f, indent=2)
    
    def _reiniciar_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(20.0, self.procesar_cola)
        self.timer.start()
    
    def tiene_elementos_pendientes(self):
        cola = self._leer_cola()
        return len(cola) > 0
    
    def obtener_info_cola(self):
        """Retorna información detallada sobre la cola"""
        cola = self._leer_cola()
        if not cola:
            return f"Cola de {self.nombre_entidad}: vacía"
        
        total_elementos = sum(len(elemento["datos"]) for elemento in cola)
        return f"Cola de {self.nombre_entidad}: {len(cola)} operaciones pendientes, {total_elementos} elementos totales"