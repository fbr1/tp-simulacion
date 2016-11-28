from numpy import random


class Camion:

    def __init__(self, capacidad, nro_pala=None, idn=None):
        """
        :param capacidad: int, capacidad de carga del camion en toneladas
        :param nro_pala: int, nro de cola al que corresponde
        """
        self.nro_pala = nro_pala
        self.capacidad = capacidad
        self.tiempo_de_descompostura = None
        self.lugar_descompostura = None
        self.idn = idn

    def tiempo_de_carga(self):
        if self.capacidad == 20:
            return random.exponential(5)
        else:
            return random.exponential(10)

    def tiempo_de_viaje(self):
        if self.capacidad == 20:
            return 2.5
        else:
            return 3

    def tiempo_de_descarga(self):
        if self.capacidad == 20:
            return random.exponential(2)
        else:
            return random.exponential(5)

    def tiempo_de_regreso(self):
        if self.capacidad == 20:
            return 1.5
        else:
            return 2

    def tiempo_de_reparacion(self):
        return random.uniform(1, 6)

    def tiempo_de_mantenimiento(self):
        while True:
            tiempo = random.normal(1, 1.5)
            if tiempo > 0:
                return tiempo
