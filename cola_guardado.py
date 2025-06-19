import json
import threading
from datetime import datetime
from mongo_repositorio import MongoRepositorio

class ColaGuardado:
    def __init__(self, archivo_cola="cola_guardado.json"):
        self.archivo_cola = archivo_cola
        self.timer = None
        self.lock = threading.Lock()
        
    def agregar_a_cola(self, coleccion, datos):
        with self.lock:
            cola = self._leer_cola()
            nuevo_elemento = {
                "coleccion": coleccion,
                "datos": datos,
                "timestamp": datetime.now().isoformat()
            }
            cola.append(nuevo_elemento)
            self._escribir_cola(cola)
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
                print("Sin conexión a MongoDB. Reintentando en 20 segundos...")
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
                    repo.guardar_todos(coleccion, datos)
                    print(f"Sincronizado: {len(datos)} elementos en {coleccion}")
                self._escribir_cola([])
                print("Cola procesada exitosamente y limpiada")
                if self.timer:
                    self.timer.cancel()
                    self.timer = None
            except Exception as e:
                print(f"Error al procesar cola: {e}")
                print("Reintentando en 20 segundos...")
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
