import Camion


class Cola:

    def __init__(self, tipo):
        """
        :param tipo: 'aplastador', 'pala', 'mecanico'
        """

        self.cola = []
        self.tipo = tipo

    def agregar(self, camion):
        """
        Agrega el camion a la cola teniendo en cuenta la politica de la cola

        :param camion: Camion
        """

        if self.tipo == 'aplastador':
            if camion.tamaño == 50:
                # Agregar el camion al principio de la cola, si hay otros hacerlo de forma FIFO

                indice = self._obtener_indice_ultima_ocurrencia(camion.tamaño)

                if indice:
                    self.cola.insert(indice + 1, camion)
                else:
                    self.cola.insert(0, camion)
            else:
                self.cola.append(camion)
        else:
            self.cola.append(camion)

    def _obtener_indice_ultima_ocurrencia(self, tamaño):
        """
        Busca el indice de la ultima ocurrencia de un camion del tamaño ingresado en la cola
        Si no encuentra el indice devuelve None

        :param tamaño: '20tn' o '50tn'
        :return ultimoindice: int
        """
        ultimoindice = None
        for i in range(len(self.cola)):
            if self.cola[i].tamaño == tamaño:
                ultimoindice = i
        return ultimoindice
