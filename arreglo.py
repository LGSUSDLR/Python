import json

class Arreglo:
    def __init__(self):
        self.items = []

    def agregar(self, *items):
        for item in items:
            self.items.append(item)

    def eliminar(self, id):
        for i, elem in enumerate(self.items):
            if hasattr(elem, 'id') and str(elem.id) == str(id):
                del self.items[i]
            return True
        return False



    def actualizar(self, id, clave, nuevo_valor):
        for elem in self.items:
            if hasattr(elem, '__dict__') and elem.__dict__.get("id") == id:
                if clave in elem.__dict__:
                    setattr(elem, clave, nuevo_valor)
                    return True
        return False

    def convADiccionarios(self):
        arreglo_convertido = []
        for item in self.items:
            if hasattr(item, 'convADiccionario'):
                diccionario = item.convADiccionario()
            else:
                diccionario = item.__dict__.copy()

            diccionario.pop('es_arreglo', None)

            if 'maestro' in diccionario and diccionario['maestro'] is not None:
                diccionario['maestro'] = diccionario['maestro'].convADiccionario()

            if 'alumnos' in diccionario and hasattr(item.alumnos, 'items'):
                diccionario['alumnos'] = [
                    alumno.convADiccionario() for alumno in item.alumnos.items
                ]

            arreglo_convertido.append(diccionario)
        return arreglo_convertido

    def mostrar_diccionario(self):
        if not self.items:
            print("No hay elementos")
        else:
            print(json.dumps(self.convADiccionarios(), indent=4, ensure_ascii=False))

    def to_dict(self):
        return [item.convADiccionario() for item in self.items]

    def crearJson(self, nombre_archivo):
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(self.to_dict(), archivo, indent=4, ensure_ascii=False)


    def __str__(self):
        if not self.items:
            return "No hay elementos"
        return str(len(self.items))
