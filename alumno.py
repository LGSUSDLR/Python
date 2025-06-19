import json
from arreglo import Arreglo
from mongo_repositorio import MongoRepositorio


class Alumno(Arreglo):
    def __init__(self, nombre=None, apellido=None, edad=None, matricula=None, promedio=None, id=None):
        if nombre is None and apellido is None and edad is None and matricula is None and promedio is None:
            super().__init__()
            self.es_arreglo = True
        else:
            self.id = id  # ID interno único
            self.nombre = nombre
            self.apellido = apellido
            self.edad = edad
            self.matricula = matricula
            self.promedio = promedio
            self.es_arreglo = False


    repositorio = MongoRepositorio()

    def guardar_en_mongodb(self, coleccion="alumnos"):
        if not self.es_arreglo:
            raise Exception("Solo se puede usar desde una instancia arreglo")
    
        repo = MongoRepositorio()
        documentos = [alumno.convADiccionario() for alumno in self.items]
        repo.guardar_todos(coleccion, documentos)

    def leer_desde_mongodb(self, coleccion="alumnos"):
        if not self.es_arreglo:
            raise Exception("Solo se puede usar desde una instancia arreglo")
    
        repo = MongoRepositorio()
        documentos = repo.leer_todos(coleccion)
    
        self.items = []
        for d in documentos:
            self.agregar(Alumno(**d))



    def es_alumno(self, dic):
        campos_obligatorios = {"id", "nombre", "apellido", "edad", "matricula", "promedio"}
        return campos_obligatorios.issubset(dic.keys())

    def actualizarPromedio(self, promedio):
        self.promedio = promedio

    def convADiccionario(self):
        if self.es_arreglo:
            return super().mostrar_diccionario()
        diccionario = self.__dict__.copy()
        diccionario.pop('es_arreglo', None)
        return diccionario

    def imprimir_diccionario(self):
        if not self.es_arreglo:
            print(json.dumps(self.convADiccionario(), indent=4))

    def __str__(self):
        if self.es_arreglo:
            return super().__str__()
        return (
            f"ID: {self.id}\n"
            f"Alumno: {self.nombre} {self.apellido}\n"
            f"Edad: {self.edad}\n"
            f"Matrícula: {self.matricula}\n"
            f"Promedio: {self.promedio}"
        )


    def eliminar(self, id_alumno):
        """Elimina un alumno del arreglo basado en su ID"""
        if not self.es_arreglo:
         return False
    
        try:
         id_int = int(id_alumno)
        except ValueError:
            return False  # id_alumno no es un número válido
    
        for i, alumno in enumerate(self.items):
         if alumno.id == id_int:
            del self.items[i]  # Elimina el alumno de la lista
            return True
        return False  # No se encontró el alumno


    def instanciarDesdeJson(self, datos):
        if isinstance(datos, list):
            for d in datos:
                if self.es_alumno(d):
                    alumno = Alumno(**d)
                    self.agregar(alumno)
                else:
                    return False
        elif isinstance(datos, dict):
            if self.es_alumno(datos):
                alumno = Alumno(**datos)
                self.agregar(alumno)
        else:
            return False

        return True

    def leerJson(self, archivo):
        with open(archivo, 'r') as f:
            datos = json.load(f)
            return self.instanciarDesdeJson(datos)

if __name__ == "__main__":
    a1 = Alumno("Alberto", "Trejo", 18, 23170093, 10, id=1)
    a2 = Alumno("Jesus", "De la rosa", 19, 23170119, 10, id=2)
    a2.actualizarPromedio(9.3)

    alumnos = Alumno()
    alumnos.agregar(a1)
    alumnos.agregar(a2)
    alumnos.agregar(Alumno("Saul", "Sanchez", 20, 23170000, 10, id=3))
    
    print("Antes de eliminar:")
    print(f"Número de alumnos: {len(alumnos.items)}")
    
    resultado = alumnos.eliminar(3)
    print(f"Resultado de eliminación: {resultado}")
    
    print("Después de eliminar:")
    print(f"Número de alumnos: {len(alumnos.items)}")

    alumnos.crearJson("alumnos.json")
    alumnos.guardar_en_mongodb()

    instanciaTemporal = Alumno()
    instanciaTemporal.leerJson("alumnos.json")
    instanciaTemporal.mostrar_diccionario()

    # Leer desde MongoDB
    nuevos_alumnos = Alumno()
    nuevos_alumnos.leer_desde_mongodb()
    nuevos_alumnos.mostrar_diccionario()