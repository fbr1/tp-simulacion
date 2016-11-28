from cola import Cola
from camion import Camion
from evento import Evento
from numpy import random
from tiempo import Tiempo


class SimulacionAlt:

    INFINITO = 99999999
    PROB_DESCOMPOSTURA = 0.01
    OCUPADO = 1
    DESOCUPADO = 0

    def start(self, duracion_simulacion=200):
        self.inicializacion(duracion_simulacion)
        while self.reloj_simulacion < self.duracion_simulacion:

            evento, camion = self.tiempos()

            # Ejecutar la rutina de evento
            getattr(self, evento)(camion)

    def partida_pala(self, camion):

        camion.tiempo_de_inspeccion = self.reloj_simulacion

        if self.estado_inspeccion[camion.nro_pala] == SimulacionAlt.DESOCUPADO:

            # Generar el fin de inspeccion
            tiempo = camion.tiempo_de_mantenimiento() + self.reloj_simulacion
            self.lista_de_eventos['fin_de_inspeccion'][camion.nro_pala].agregar(tiempo, camion)
            self.estado_inspeccion[camion.nro_pala] = SimulacionAlt.OCUPADO

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
            self.estado_pala[camion.nro_pala] = SimulacionAlt.DESOCUPADO

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
            self.estado_inspeccion[camion.nro_pala] = SimulacionAlt.DESOCUPADO

    def arribo_aplastador(self, camion):
        numero_aleatorio = random.random_sample()

        if numero_aleatorio < SimulacionAlt.PROB_DESCOMPOSTURA:
            camion.lugar_descompostura = 'arribo_aplastador'
            self.descompostura(camion)

        elif self.estado_aplastador == SimulacionAlt.DESOCUPADO:

            # Generar partida del camion del aplastador
            tiempo = camion.tiempo_de_descarga() + self.reloj_simulacion
            self.lista_de_eventos['partida_aplastador'].agregar(tiempo, camion)
            self.estado_aplastador = SimulacionAlt.OCUPADO

        else:
            self.cola_aplastador.agregar(camion)

    def partida_aplastador(self, camion):

        self.total_material_transportado += camion.capacidad

        numero_aleatorio = random.random_sample()

        if numero_aleatorio < SimulacionAlt.PROB_DESCOMPOSTURA:
            camion.lugar_descompostura = 'partida_aplastador'
            self.descompostura(camion)
        else:
            # Generar arribo a la pala del camion que parte (tiempo de regreso)
            tiempo = camion.tiempo_de_regreso() + self.reloj_simulacion
            self.lista_de_eventos['arribo_pala'][camion.nro_pala].agregar(tiempo, camion)

        if self.cola_aplastador.cola:
            camion_cola = self.cola_aplastador.cola.pop(0)

            # Generar partida del camion del aplastador
            tiempo = camion_cola.tiempo_de_descarga() + self.reloj_simulacion
            self.lista_de_eventos['partida_aplastador'].agregar(tiempo, camion_cola)

        else:
            self.estado_aplastador = SimulacionAlt.DESOCUPADO

    def arribo_pala(self, camion):
        numero_aleatorio = random.random_sample()

        if numero_aleatorio < SimulacionAlt.PROB_DESCOMPOSTURA:
            camion.lugar_descompostura = 'arribo_pala'
            self.descompostura(camion)

        elif self.estado_pala[camion.nro_pala] == SimulacionAlt.DESOCUPADO:
            # Generar partida del camion que sale de la cola nro_pala
            tiempo = camion.tiempo_de_carga() + self.reloj_simulacion
            self.lista_de_eventos['partida_pala'][camion.nro_pala].agregar(tiempo, camion)
            self.estado_pala[camion.nro_pala] = SimulacionAlt.OCUPADO

        else:
            self.colas_pala[camion.nro_pala].agregar(camion)

    def descompostura(self, camion):

        self.total_descomposturas += 1
        camion.tiempo_de_descompostura = self.reloj_simulacion

        # Acumulada de descompuestos en el tiempo
        self.acrt += (self.reloj_simulacion - self.ultima_medicion_descomposturas) \
            * (len(self.cola_mecanico.cola) + self.estado_mecanico)
        self.ultima_medicion_descomposturas = self.reloj_simulacion

        if self.estado_mecanico == SimulacionAlt.DESOCUPADO:
            # TODO reveer si la comparacion para ver donde esta el mecanico se puede hacer facil y sin usar comparacion
            # de strings
            # Generar partida del camion, teniendo en cuenta donde se encuentra
            tiempo_de_viaje = 0
            if ('aplastador' in self.ult_ubicacion_mecanico and 'aplastador' not in camion.lugar_descompostura) \
                    or ('pala' in self.ult_ubicacion_mecanico and 'pala' not in camion.lugar_descompostura):
                    tiempo_de_viaje = 1

            tiempo = tiempo_de_viaje + camion.tiempo_de_reparacion() + self.reloj_simulacion
            self.lista_de_eventos["fin_de_reparacion"].agregar(tiempo, camion)

            self.estado_mecanico = SimulacionAlt.OCUPADO
        else:
            self.cola_mecanico.agregar(camion)

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
            if self.colas_pala[camion.nro_pala].cola:

                # Generar partida del camion que sale de la cola nro_pala
                tiempo = camion.tiempo_de_carga() + self.reloj_simulacion
                self.lista_de_eventos['partida_pala'][camion.nro_pala].agregar(tiempo, camion)

                self.estado_pala[camion.nro_pala] = SimulacionAlt.OCUPADO

            else:
                self.colas_pala[camion.nro_pala].agregar(camion)

        elif self.ult_ubicacion_mecanico == 'partida_aplastador':

            # Generar arribo a la pala del camion que parte (tiempo de regreso)
            tiempo = camion.tiempo_de_regreso() + self.reloj_simulacion
            self.lista_de_eventos['arribo_pala'][camion.nro_pala].agregar(tiempo, camion)

        elif self.ult_ubicacion_mecanico == 'arribo_aplastador':
            if self.cola_aplastador.cola:

                # Generar partida del camion del aplastador
                tiempo = camion.tiempo_de_descarga() + self.reloj_simulacion
                self.lista_de_eventos['partida_aplastador'].agregar(tiempo, camion)

                self.estado_aplastador = SimulacionAlt.OCUPADO
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
            self.estado_mecanico = SimulacionAlt.DESOCUPADO

    def reportes(self):
        return self.tiempo_ocioso / 9, self.total_material_transportado / 9, \
            self.total_descomposturas / 9, self.acrt / self.reloj_simulacion

    def tiempos(self):
        # TODO refactorizar codigo repetido
        tiempo_mas_reciente = Tiempo(SimulacionAlt.INFINITO, None)
        evento_mas_reciente = None

        for key, value in self.lista_de_eventos.items():
            if type(value) is list:
                for i in range(len(value)):
                    if value[i].tiempos:
                        if value[i].tiempos[0].tiempo < tiempo_mas_reciente.tiempo:
                            evento_mas_reciente = value[i]
                            tiempo_mas_reciente = value[i].tiempos[0]
            else:
                if value.tiempos:
                    if value.tiempos[0].tiempo < tiempo_mas_reciente.tiempo:
                        evento_mas_reciente = value
                        tiempo_mas_reciente = value.tiempos[0]

        self.reloj_simulacion = tiempo_mas_reciente.tiempo
        evento_mas_reciente.popleft()

        return evento_mas_reciente.nombre_funcion, tiempo_mas_reciente.camion

    def inicializacion(self, duracion_simulacion):

        self.duracion_simulacion = duracion_simulacion

        # Contadores Estadisticos
        self.tiempo_ocioso = 0
        self.total_material_transportado = 0
        self.total_descomposturas = 0
        self.acrt = 0

        # Variables de estado

        self.reloj_simulacion = 0
        self.estado_pala = [SimulacionAlt.DESOCUPADO, SimulacionAlt.DESOCUPADO, SimulacionAlt.DESOCUPADO]
        self.estado_aplastador = SimulacionAlt.DESOCUPADO
        self.estado_mecanico = SimulacionAlt.DESOCUPADO
        self.estado_inspeccion = [SimulacionAlt.DESOCUPADO, SimulacionAlt.DESOCUPADO, SimulacionAlt.DESOCUPADO]
        self.ult_ubicacion_mecanico = 'pala'
        self.ultima_medicion_descomposturas = 0
        self.dcrt = 0

        self.colas_pala = []
        for i in range(3):
            cola_pala = Cola('pala')
            cola_pala.agregar(Camion(50, i))
            cola_pala.agregar(Camion(20, i))
            self.colas_pala.append(cola_pala)

        self.cola_aplastador = Cola('aplastador')
        self.cola_mecanico = Cola('mecanico')
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

        # Generar evento desencadenador
        # Deshabilitar temporalmente la probabilidad de descompostura

        temp_descompostura = SimulacionAlt.PROB_DESCOMPOSTURA
        SimulacionAlt.PROB_DESCOMPOSTURA = -1

        for i in range(3):
            self.arribo_pala(Camion(20, i))

        # Devolver el valor original
        SimulacionAlt.PROB_DESCOMPOSTURA = temp_descompostura

    def __init__(self):
        self.duracion_simulacion = None

        # Contadores estadisticos
        self.tiempo_ocioso = None
        self.total_material_transportado = None
        self.total_descomposturas = None
        self.acrt = None

        # Variables de estado
        self.reloj_simulacion = None
        self.estado_pala = None
        self.estado_aplastador = None
        self.estado_mecanico = None
        self.estado_inspeccion = None
        self.ult_ubicacion_mecanico = None
        self.ultima_medicion_descomposturas = None
        self.dcrt = None
        self.colas_pala = None
        self.cola_aplastador = None
        self.cola_mecanico = None
        self.cola_inspeccion = None
        self.lista_de_eventos = None
