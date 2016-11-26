class Camion:

    def __init__(self, capacidad, nro_pala=None, idn=None):
        """
        :param capacidad: int, capacidad de carga del camion en toneladas
        :param nro_pala: int, nro de cola al que corresponde
        """
        self.nro_pala = nro_pala
        self.capacidad = capacidad
        self.lugar_descompostura = None
        self.idn = idn

