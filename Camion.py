class Camion:

    def __init__(self, tamaño, nro_cola):
        """
        :param tamaño: int, tamaño de carga del camion en toneladas
        :param nro_cola: int, nro de cola al que corresponde
        """
        self.nro_cola = nro_cola
        self.tamaño = tamaño
        self.vino_de = None

