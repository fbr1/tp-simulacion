from cola import Cola
from camion import Camion
from evento import Evento
from numpy import random
from simulacion import Simulacion


class SimulacionUnaCola(Simulacion):

    def partida_pala(self, camion):
        numero_aleatorio = random.random_sample()

        if numero_aleatorio < Simulacion.PROB_DESCOMPOSTURA:
            camion.lugar_descompostura = 'partida_pala'
            self.descompostura(camion)
        else:
            # Generar arribo al aplastador del camion que parte (tiempo de viaje)
            tiempo = camion.tiempo_de_viaje() + self.reloj_simulacion
            self.lista_de_eventos['arribo_aplastador'].agregar(tiempo, camion)

        # Si hay camiones en la cola de la pala
        cola_pala = self.cola_pala
        if cola_pala.cola:

            # Quitar al primer camion de la cola i
            camion_cola = cola_pala.cola.pop(0)
            camion_cola.nro_pala = camion.nro_pala

            # Generar la partida (tiempo de carga) del camion que sale de la cola de la pala i
            tiempo = camion_cola.tiempo_de_carga() + self.reloj_simulacion
            self.lista_de_eventos['partida_pala'][camion.nro_pala].agregar(tiempo, camion_cola)

        else:
            self.estado_pala[camion.nro_pala] = Simulacion.DESOCUPADO

    def partida_aplastador(self, camion):

        self.total_material_transportado += camion.capacidad

        numero_aleatorio = random.random_sample()

        if numero_aleatorio < Simulacion.PROB_DESCOMPOSTURA:
            camion.lugar_descompostura = 'partida_aplastador'
            self.descompostura(camion)
        else:
            # Generar arribo a la pala del camion que parte (tiempo de regreso)
            tiempo = camion.tiempo_de_regreso() + self.reloj_simulacion
            self.lista_de_eventos['arribo_pala'].agregar(tiempo, camion)

        if self.cola_aplastador.cola:
            camion_cola = self.cola_aplastador.cola.pop(0)

            # Generar partida del camion del aplastador
            tiempo = camion_cola.tiempo_de_descarga() + self.reloj_simulacion
            self.lista_de_eventos['partida_aplastador'].agregar(tiempo, camion_cola)

        else:
            self.estado_aplastador = Simulacion.DESOCUPADO

    def arribo_pala(self, camion):
        numero_aleatorio = random.random_sample()

        if numero_aleatorio < SimulacionUnaCola.PROB_DESCOMPOSTURA:
            camion.lugar_descompostura = 'arribo_pala'
            self.descompostura(camion)
        else:
            desocupado = False

            for i in range(len(self.estado_pala)):
                if self.estado_pala[i] == SimulacionUnaCola.DESOCUPADO:
                    desocupado = True
                    camion.nro_pala = i
                    # Generar partida del camion que sale de la cola nro_pala
                    tiempo = camion.tiempo_de_carga() + self.reloj_simulacion
                    self.lista_de_eventos['partida_pala'][camion.nro_pala].agregar(tiempo, camion)
                    self.estado_pala[camion.nro_pala] = SimulacionUnaCola.OCUPADO

                    break
            if not desocupado:
                self.cola_pala.agregar(camion)

    def fin_de_reparacion(self, camion):

        self.ult_ubicacion_mecanico = camion.lugar_descompostura
        self.tiempo_ocioso += self.reloj_simulacion - camion.tiempo_de_descompostura

        camion.lugar_descompostura = None
        camion.tiempo_de_descompostura = None

        # Acumulada de descompuestos en el tiempo
        self.acrt += (self.reloj_simulacion - self.ultima_medicion_descomposturas) \
            * (len(self.cola_mecanico.cola) + self.estado_mecanico)
        self.ultima_medicion_descomposturas = self.reloj_simulacion

        if self.ult_ubicacion_mecanico == 'partida_pala':

            # Generar arribo al aplastador del camion que parte (tiempo de viaje)
            tiempo = camion.tiempo_de_viaje() + self.reloj_simulacion
            self.lista_de_eventos['arribo_aplastador'].agregar(tiempo, camion)

        elif self.ult_ubicacion_mecanico == 'arribo_pala':

            desocupado = False

            for i in range(len(self.estado_pala)):
                if self.estado_pala[i] == SimulacionUnaCola.DESOCUPADO:
                    desocupado = True
                    camion.nro_pala = i
                    # Generar partida del camion que sale de la cola nro_pala
                    tiempo = camion.tiempo_de_carga() + self.reloj_simulacion
                    self.lista_de_eventos['partida_pala'][camion.nro_pala].agregar(tiempo, camion)
                    self.estado_pala[camion.nro_pala] = SimulacionUnaCola.OCUPADO

                    break
            if not desocupado:
                self.cola_pala.agregar(camion)

        elif self.ult_ubicacion_mecanico == 'partida_aplastador':

            # Generar arribo a la pala del camion que parte (tiempo de regreso)
            tiempo = camion.tiempo_de_regreso() + self.reloj_simulacion
            self.lista_de_eventos['arribo_pala'].agregar(tiempo, camion)

        elif self.ult_ubicacion_mecanico == 'arribo_aplastador':
            if self.estado_aplastador == Simulacion.DESOCUPADO:

                # Generar partida del camion del aplastador
                tiempo = camion.tiempo_de_descarga() + self.reloj_simulacion
                self.lista_de_eventos['partida_aplastador'].agregar(tiempo, camion)
                self.estado_aplastador = Simulacion.OCUPADO

            else:
                self.cola_aplastador.agregar(camion)

        if self.cola_mecanico.cola:
            camion_cola = self.cola_mecanico.cola.pop(0)

            # Generar partida del camion, teniendo en cuenta donde se encuentra
            tiempo_de_viaje = 0
            if ('aplastador' in self.ult_ubicacion_mecanico and 'aplastador' not in camion_cola.lugar_descompostura) \
                    or ('pala' in self.ult_ubicacion_mecanico and 'pala' not in camion_cola.lugar_descompostura):
                tiempo_de_viaje = 1

            tiempo = tiempo_de_viaje + camion.tiempo_de_reparacion() + self.reloj_simulacion
            self.lista_de_eventos["fin_de_reparacion"].agregar(tiempo, camion_cola)

        else:
            self.estado_mecanico = Simulacion.DESOCUPADO

    def inicializacion(self, duracion_simulacion):

        super(SimulacionUnaCola, self).inicializacion(duracion_simulacion)

        self.cola_pala = Cola('pala')

        for i in range(3):
            self.cola_pala.agregar(Camion(50))
            for k in range(2):
                self.cola_pala.agregar(Camion(20))

        # Lista de eventos

        self.lista_de_eventos = {'arribo_pala': Evento('arribo_pala'),
                                 'partida_pala': [Evento('partida_pala'),
                                                  Evento('partida_pala'),
                                                  Evento('partida_pala')],
                                 'arribo_aplastador': Evento('arribo_aplastador'),
                                 'partida_aplastador': Evento('partida_aplastador'),
                                 'fin_de_reparacion': Evento('fin_de_reparacion')}

    def generar_evento_desencadenador(self):
        for i in range(3):
            cola_pala = self.cola_pala
            # Quitar al primer camion de la cola i
            camion_cola = cola_pala.cola.pop(0)
            camion_cola.nro_pala = i

            # Generar la partida (tiempo de carga) del camion que sale de la cola de la pala i
            tiempo = camion_cola.tiempo_de_carga() + self.reloj_simulacion
            self.lista_de_eventos['partida_pala'][i].agregar(tiempo, camion_cola)

            self.estado_pala[i] = SimulacionUnaCola.OCUPADO

    def __init__(self):
        super(SimulacionUnaCola, self).__init__()
        self.cola_pala = None
