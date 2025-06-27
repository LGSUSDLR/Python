from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

class MongoRepositorio:
    def __init__(self):
        from pymongo import MongoClient
        self.client = MongoClient("mongodb+srv://sau:871212@cluster0.rwlvrjg.mongodb.net/", serverSelectionTimeoutMS=2000) 
        self.db = self.client["Ejemplo"]

    def test_connection(self):
        self.client.server_info()

    def guardar_todos(self, coleccion, lista_datos):
        coll = self.db[coleccion]
        coll.delete_many({}) 
        if lista_datos:
            coll.insert_many(lista_datos)


    def leer_todos(self, coleccion):
        documentos = list(self.db[coleccion].find())
        for doc in documentos:
            doc.pop('_id', None)  
        return documentos

