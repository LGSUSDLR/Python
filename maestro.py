import json
from arreglo import Arreglo
from mongo_repositorio import MongoRepositorio


class Maestro(Arreglo):
    repositorio = MongoRepositorio()  # Repositorio como propiedad de clase

    def __init__(self, nombre=None, apellido=None, edad=None, especialidad=None, id=None):
        if nombre is None and apellido is None and edad is None and especialidad is None:
            super().__init__()
            self.es_arreglo = True
        else:
            self.id = id  # ID único
            self.nombre = nombre
            self.apellido = apellido
            self.edad = edad
            self.especialidad = especialidad
            self.es_arreglo = False

    def guardar_en_mongodb(self, coleccion="maestros"):
        if not self.es_arreglo:
            raise Exception("Solo se puede usar desde una instancia arreglo")
        documentos = [maestro.convADiccionario() for maestro in self.items]
        self.repositorio.guardar_todos(coleccion, documentos)

    def leer_desde_mongodb(self, coleccion="maestros"):
        if not self.es_arreglo:
            raise Exception("Solo se puede usar desde una instancia arreglo")
        documentos = self.repositorio.leer_todos(coleccion)
        self.items = []
        for d in documentos:
            self.agregar(Maestro(**d))

    def convADiccionario(self):
        if self.es_arreglo:
            return super().mostrar_diccionario()
        diccionario = self.__dict__.copy()
        diccionario.pop('es_arreglo', None)
        return diccionario

    def lista_diccionarios(self):
        return [maestro.convADiccionario() for maestro in self.items]

    def imprimir_diccionario(self):
        if not self.es_arreglo:
            print(json.dumps(self.convADiccionario(), indent=4))

    def __str__(self):
        if self.es_arreglo:
            return super().__str__()
        return (
            f"ID: {self.id}\n"
            f"Maestro: {self.nombre} {self.apellido}\n"
            f"Edad: {self.edad}\n"
            f"Especialidad: {self.especialidad}"
        )

    def es_maestro(self, dic):
        campos_obligatorios = {"id", "nombre", "apellido", "edad", "especialidad"}
        return campos_obligatorios.issubset(dic.keys())

    def instanciarDesdeJson(self, datos):
        if isinstance(datos, list):
            for d in datos:
                if self.es_maestro(d):
                    self.agregar(Maestro(**d))
                else:
                    return False
        elif isinstance(datos, dict):
            if self.es_maestro(datos):
                self.agregar(Maestro(**datos))
            else:
                return False
        else:
            return False
        return True

    def leerJson(self, archivo):
        with open(archivo, 'r') as f:
            datos = json.load(f)
            return self.instanciarDesdeJson(datos)

    def eliminar(self, id_maestro):
        if not self.es_arreglo:
            return False
        try:
            id_int = int(id_maestro)
        except ValueError:
            return False
        for i, maestro in enumerate(self.items):
            if maestro.id == id_int:
                del self.items[i]
                return True
        return False

    def cambiarEdad(self, edad):
        self.edad = edad


# Pruebas
if __name__ == "__main__":
    maestro1 = Maestro("Ramiro", "Esquivel", 40, "1", "Android")
    maestro2 = Maestro("Jesus", "Burciaga", 40, "2", "iOS")

    maestro1.cambiarEdad(56)


  
    maestros = Maestro()
    maestros.agregar(maestro1)
    maestros.agregar(maestro2)
    maestros.eliminar("1") 

    maestros.crearJson("maestros.json")


    maestrodesdeJson = Maestro() 
    maestrodesdeJson.leerJson("maestros.json")
    maestrodesdeJson.mostrar_diccionario()
