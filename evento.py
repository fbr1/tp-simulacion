from collections import deque
from tiempo import Tiempo


class Evento:

    def __init__(self, nombre_funcion):
        """
        :param nombre_funcion: string, tiene que corresponderse con una funcion existente
        """
        self.nombre_funcion = nombre_funcion
        self.tiempos = deque()

    def agregar(self, tiempo, camion):
        self.tiempos.append(Tiempo(tiempo, camion))

    def popleft(self):
        self.tiempos.popleft()
