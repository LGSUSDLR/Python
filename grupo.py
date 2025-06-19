import json
from alumno import Alumno
from maestro import Maestro
from arreglo import Arreglo
from mongo_repositorio import MongoRepositorio

class Grupo(Arreglo):
    def __init__(self, nombre=None, maestro=None, id=None):
        if nombre is None and maestro is None:
            super().__init__()
            self.es_arreglo = True
        else:
            if id is None:
                raise ValueError("Debe proporcionar un id para el grupo")
            self.id = str(id)  # convertimos a str para consistencia
            self.nombre = nombre
            self.maestro = maestro
            self.alumnos = Alumno()
            self.es_arreglo = False

    def asignar_maestro(self, maestro):
        self.maestro = maestro

    def cambiarNombre(self, nombre):
        self.nombre = nombre

    def convADiccionario(self):
        if self.es_arreglo:
            return [grupo.convADiccionario() for grupo in self.items]
        return {
            "id": self.id,
            "nombre": self.nombre,
            "maestro": self.maestro.convADiccionario() if self.maestro else None,
            "alumnos": [alumno.convADiccionario() for alumno in self.alumnos.items]
        }

    def imprimir_diccionario(self):
        if not self.es_arreglo:
            print(json.dumps(self.convADiccionario(), indent=4))

    def mostrar_diccionario(self):
        if self.es_arreglo:
            for grupo in self.items:
                grupo.imprimir_diccionario()
        else:
            self.imprimir_diccionario()

    def es_grupo(self, dic):
        campos_obligatorios = {"id", "nombre", "maestro", "alumnos"}
        return campos_obligatorios.issubset(dic.keys())

    def instanciarDesdeJson(self, datos):
        if isinstance(datos, list):
            for d in datos:
                if self.es_grupo(d):
                    grupo = self._crear_grupo_desde_diccionario(d)
                    self.agregar(grupo)
                else:
                    print("ERROR: Uno de los objetos no es un grupo válido.")
                    return False
        elif isinstance(datos, dict):
            if self.es_grupo(datos):
                grupo = self._crear_grupo_desde_diccionario(datos)
                self.nombre = grupo.nombre
                self.maestro = grupo.maestro
                self.alumnos = grupo.alumnos
                self.id = grupo.id
                self.es_arreglo = False
            else:
                print("ERROR: El JSON no corresponde a un grupo válido.")
                return False
        else:
            print("ERROR: Formato JSON inválido.")
            return False
        return True

    def leerJson(self, archivo):
        with open(archivo, 'r') as f:
            datos = json.load(f)
            return self.instanciarDesdeJson(datos)

    def crearJson(self, archivo):
        if self.es_arreglo:
            datos = [grupo.convADiccionario() for grupo in self.items]
        else:
            datos = self.convADiccionario()

        with open(archivo, 'w') as f:
            json.dump(datos, f, indent=4)

    def _crear_grupo_desde_diccionario(self, d):
        grupo = Grupo(nombre=d["nombre"], id=d["id"])
        grupo.maestro = Maestro(**d["maestro"]) if d["maestro"] else None
        grupo.alumnos = Alumno()
        if d["alumnos"]:
            grupo.alumnos.instanciarDesdeJson(d["alumnos"])
        grupo.es_arreglo = False
        return grupo

    def eliminar(self, id_grupo):
        if not self.es_arreglo:
            return False
        for i, grupo in enumerate(self.items):
            if grupo.id == str(id_grupo):
                del self.items[i]
                return True
        return False

    # MÉTODOS PARA MONGODB

    def guardar_en_mongodb(self, coleccion="grupos"):
        if not self.es_arreglo:
            raise Exception("Solo se puede usar desde una instancia arreglo")

        repo = MongoRepositorio()
        documentos = [grupo.convADiccionario() for grupo in self.items]
        repo.guardar_todos(coleccion, documentos)

    def leer_desde_mongodb(self, coleccion="grupos"):
        if not self.es_arreglo:
            raise Exception("Solo se puede usar desde una instancia arreglo")

        repo = MongoRepositorio()
        documentos = repo.leer_todos(coleccion)

        self.items = []
        for d in documentos:
            self.agregar(self._crear_grupo_desde_diccionario(d))
