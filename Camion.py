class Camion:

    def __init__(self, capacidad, nro_cola):
        """
        :param capacidad: int, capacidad de carga del camion en toneladas
        :param nro_cola: int, nro de cola al que corresponde
        """
        self.nro_cola = nro_cola
        self.capacidad = capacidad
        self.accion_despues_descompostura = None

