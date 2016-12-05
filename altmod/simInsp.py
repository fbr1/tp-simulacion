from cola import Cola
from evento import Evento
from simulacion import Simulacion


class SimulacionInsp(Simulacion):

    PROB_DESCOMPOSTURA = 0.01

    def partida_pala(self, camion):

        camion.tiempo_de_inspeccion = self.reloj_simulacion

        if self.estado_inspeccion[camion.nro_pala] == SimulacionInsp.DESOCUPADO:

            # Generar el fin de inspeccion
            tiempo = camion.tiempo_de_mantenimiento() + self.reloj_simulacion
            self.lista_de_eventos['fin_de_inspeccion'][camion.nro_pala].agregar(tiempo, camion)
            self.estado_inspeccion[camion.nro_pala] = SimulacionInsp.OCUPADO

        else:
            self.cola_inspeccion[camion.nro_pala].agregar(camion)

        # Si hay camiones en la cola de la pala nro_pala
        cola_pala = self.colas_pala[camion.nro_pala]
        if cola_pala.cola:

            # Quitar al primer camion de la cola i
            camion_cola = cola_pala.cola.pop(0)

            # Generar la partida (tiempo de carga) del camion que sale de la cola de la pala i
            tiempo = camion_cola.tiempo_de_carga() + self.reloj_simulacion
            self.lista_de_eventos['partida_pala'][camion.nro_pala].agregar(tiempo, camion_cola)

        else:
            self.estado_pala[camion.nro_pala] = SimulacionInsp.DESOCUPADO

    def fin_de_inspeccion(self, camion):

        self.tiempo_ocioso += self.reloj_simulacion - camion.tiempo_de_inspeccion
        camion.tiempo_de_inspeccion = None

        # Generar arribo al aplastador del camion que parte (tiempo de viaje)
        tiempo = camion.tiempo_de_viaje() + self.reloj_simulacion
        self.lista_de_eventos['arribo_aplastador'].agregar(tiempo, camion)

        if self.cola_inspeccion[camion.nro_pala].cola:

            camion_cola = self.cola_inspeccion[camion.nro_pala].cola.pop(0)

            # Generar el fin de inspeccion
            tiempo = camion_cola.tiempo_de_mantenimiento() + self.reloj_simulacion
            self.lista_de_eventos['fin_de_inspeccion'][camion.nro_pala].agregar(tiempo, camion_cola)

        else:
            self.estado_inspeccion[camion.nro_pala] = SimulacionInsp.DESOCUPADO

    def fin_de_reparacion(self, camion):

        self.ult_ubicacion_mecanico = camion.lugar_descompostura
        self.tiempo_ocioso += self.reloj_simulacion - camion.tiempo_de_descompostura

        camion.lugar_descompostura = None
        camion.tiempo_de_descompostura = None

        # Acumulada de descompuestos en el tiempo
        self.acrt += (self.reloj_simulacion - self.ultima_medicion_descomposturas) \
            * (len(self.cola_mecanico.cola) + self.estado_mecanico)
        self.ultima_medicion_descomposturas = self.reloj_simulacion

        if self.ult_ubicacion_mecanico == 'arribo_pala':
            if self.estado_pala[camion.nro_pala] == SimulacionInsp.DESOCUPADO:
                # Generar partida del camion que sale de la cola nro_pala
                tiempo = camion.tiempo_de_carga() + self.reloj_simulacion
                self.lista_de_eventos['partida_pala'][camion.nro_pala].agregar(tiempo, camion)
                self.estado_pala[camion.nro_pala] = SimulacionInsp.OCUPADO

            else:
                self.colas_pala[camion.nro_pala].agregar(camion)

        elif self.ult_ubicacion_mecanico == 'partida_aplastador':

            # Generar arribo a la pala del camion que parte (tiempo de regreso)
            tiempo = camion.tiempo_de_regreso() + self.reloj_simulacion
            self.lista_de_eventos['arribo_pala'][camion.nro_pala].agregar(tiempo, camion)

        elif self.ult_ubicacion_mecanico == 'arribo_aplastador':
            if self.estado_aplastador == SimulacionInsp.DESOCUPADO:

                # Generar partida del camion del aplastador
                tiempo = camion.tiempo_de_descarga() + self.reloj_simulacion
                self.lista_de_eventos['partida_aplastador'].agregar(tiempo, camion)
                self.estado_aplastador = SimulacionInsp.OCUPADO

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
            self.estado_mecanico = SimulacionInsp.DESOCUPADO

    def inicializacion(self, duracion_simulacion):

        super(SimulacionInsp, self).inicializacion(duracion_simulacion)

        self.estado_inspeccion = [SimulacionInsp.DESOCUPADO, SimulacionInsp.DESOCUPADO, SimulacionInsp.DESOCUPADO]
        self.cola_inspeccion = [Cola('inspeccion'), Cola('inspeccion'), Cola('inspeccion')]

        # Lista de eventos
        self.lista_de_eventos = {'arribo_pala': [Evento('arribo_pala'),
                                                 Evento('arribo_pala'),
                                                 Evento('arribo_pala')],
                                 'partida_pala': [Evento('partida_pala'),
                                                  Evento('partida_pala'),
                                                  Evento('partida_pala')],
                                 'arribo_aplastador': Evento('arribo_aplastador'),
                                 'partida_aplastador': Evento('partida_aplastador'),
                                 'fin_de_reparacion': Evento('fin_de_reparacion'),
                                 'fin_de_inspeccion': [Evento('fin_de_inspeccion'),
                                                       Evento('fin_de_inspeccion'),
                                                       Evento('fin_de_inspeccion')]}

    def __init__(self):
        super(SimulacionInsp, self).__init__()

        # Variables de estado
        self.estado_inspeccion = None
        self.cola_inspeccion = None
