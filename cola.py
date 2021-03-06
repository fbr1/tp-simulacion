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

        lista_capacidades_cola = [cam.capacidad for cam in self.cola]

        if self.tipo == 'aplastador':
            if camion.capacidad == 50:
                # Agregar el camion al principio de la cola, si hay otros hacerlo de forma FIFO

                if 50 in lista_capacidades_cola:
                    self.cola.insert(self._obtener_indice_ultima_ocurrencia(50) + 1, camion)
                else:
                    self.cola.insert(0, camion)
            else:
                self.cola.append(camion)
        else:
            self.cola.append(camion)

    def _obtener_indice_ultima_ocurrencia(self, capacidad):
        """
        Para que se mas parecido al metodo rindex (que no sirve para listas)
        Busca el indice de la ultima ocurrencia de un camion de la capacidad ingresada en la cola
        Si no encuentra el indice devuelve None

        :param capacidad: '20tn' o '50tn'
        :return ultimoindice: int
        """
        lista_capacidades = [cam.capacidad for cam in self.cola]
        if capacidad in lista_capacidades:
            return len(lista_capacidades) - lista_capacidades[::-1].index(capacidad) - 1
        else:
            return None
