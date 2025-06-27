from interfazalumno import InterfazAlumno
from interfazmaestro import InterfazMaestro
from interfazgrupo import InterfazGrupo

class InterfazGeneral:
    def __init__(self):
        self.interfaz_alumno = InterfazAlumno()
        self.interfaz_maestro = InterfazMaestro()
        self.interfaz_grupo = InterfazGrupo()


    def menu_principal(self):
        while True:
            print("\n=== MENÚ PRINCIPAL ===")
            print("1. Gestión de Alumnos")
            print("2. Gestión de Maestros")
            print("3. Gestión de Grupos")
            print("4. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                self.interfaz_alumno.menu_interactivo()
            elif opcion == "2":
                self.interfaz_maestro.menu_interactivo()
            elif opcion == "3":
                self.interfaz_grupo.menu_interactivo()
            elif opcion == "4":
                print("Saliendo del programa...")
                break
            else:
                print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    interfaz = InterfazGeneral()
    interfaz.menu_principal()
