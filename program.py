from cola import Cola
from camion import Camion
from evento import Evento
from numpy import random
from tiempo import Tiempo


class Simulacion:

    INFINITO = 99999999
    PROB_DESCOMPOSTURA = 0.1
    OCUPADO = 1
    DESOCUPADO = 0

    def start(self, tiempo_simulacion=200):
        self.inicializacion()
        for i in range(tiempo_simulacion):
            evento, camion = self.tiempos()

            # Ejecutar la rutina de evento
            getattr(self, evento)(camion)

        self.reportes()

    def partida_pala(self, camion):
        numero_aleatorio = random.random_sample()

        if numero_aleatorio < Simulacion.PROB_DESCOMPOSTURA:
            camion.lugar_descompostura = 'partida_aplastador'
            self.descompostura(camion)
        else:
            # Generar arribo al aplastador del camion que parte (tiempo de viaje)
            tiempo = camion.tiempo_de_viaje() + self.reloj_simulacion
            self.lista_de_eventos['arribo_aplastador'].agregar(tiempo, camion)

        # Si hay camiones en la cola de la pala nro_pala
        cola_pala = self.colas_pala[camion.nro_pala]
        if cola_pala.cola:

            # Quitar al primer camion de la cola i
            camion_cola = cola_pala.cola.pop(0)

            # Generar la partida (tiempo de carga) del camión que sale de la cola de la pala i
            tiempo = camion_cola.tiempo_de_carga() + self.reloj_simulacion
            self.lista_de_eventos['partida_pala'].agregar(tiempo, camion)

            self.estado_pala = Simulacion.OCUPADO
        else:
            self.estado_pala = Simulacion.DESOCUPADO

    def arribo_aplastador(self, camion):
        numero_aleatorio = random.random_sample()

        if numero_aleatorio < Simulacion.PROB_DESCOMPOSTURA:
            camion.lugar_descompostura = 'arribo_aplastador'
            self.descompostura(camion)

        elif self.estado_aplastador == Simulacion.DESOCUPADO:

            # Generar partida del camion del aplastador
            tiempo = camion.tiempo_de_descarga() + self.reloj_simulacion
            self.lista_de_eventos['partida_aplastador'].agregar(tiempo, camion)
            self.estado_aplastador = Simulacion.OCUPADO

        else:
            self.cola_aplastador.agregar(camion)

    def partida_aplastador(self, camion):
        numero_aleatorio = random.random_sample()

        if numero_aleatorio < Simulacion.PROB_DESCOMPOSTURA:
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
            self.estado_aplastador = Simulacion.OCUPADO

        else:
            self.estado_aplastador = Simulacion.DESOCUPADO

    def arribo_pala(self, camion):
        numero_aleatorio = random.random_sample()

        if numero_aleatorio < Simulacion.PROB_DESCOMPOSTURA:
            camion.lugar_descompostura = 'arribo_pala'
            self.descompostura(camion)

        elif self.estado_pala == Simulacion.DESOCUPADO:
            # Generar partida del camion que sale de la cola nro_pala
            tiempo = camion.tiempo_de_carga() + self.reloj_simulacion
            self.lista_de_eventos['partida_pala'][camion.nro_pala].agregar(tiempo, camion)
            self.estado_pala[camion.nro_pala] = Simulacion.OCUPADO

        else:
            self.colas_pala[camion.nro_pala].agregar(camion)

    def descompostura(self, camion):
        if self.estado_mecanico == Simulacion.DESOCUPADO:
            # TODO reveer si la comparacion para ver donde esta el mecanico se puede hacer facil y sin usar comparacion
            # de strings
            # Generar partida del camion, teniendo en cuenta donde se encuentra
            tiempo_de_viaje = 0
            if ('aplastador' in self.ult_localizacion_mecanico and 'aplastador' not in camion.lugar_descompostura) \
                    or ('pala' in self.ult_localizacion_mecanico and 'pala' not in camion.lugar_descompostura):
                    tiempo_de_viaje = 1

            tiempo = tiempo_de_viaje + camion.tiempo_de_reparacion() + self.reloj_simulacion
            self.lista_de_eventos["fin_de_reparacion"].agregar(tiempo, camion)

            self.estado_mecanico = Simulacion.OCUPADO
        else:
            self.cola_mecanico.agregar(camion)

    def fin_de_reparacion(self, camion):

        self.ult_localizacion_mecanico = camion.lugar_descompostura

        if camion.lugar_descompostura == 'partida_pala':
            camion.lugar_descompostura = None

            # Generar arribo al aplastador del camion que parte (tiempo de viaje)
            tiempo = camion.tiempo_de_viaje() + self.reloj_simulacion
            self.lista_de_eventos['arribo_aplastador'].agregar(tiempo, camion)

        elif camion.lugar_descompostura == 'arribo_pala':
            camion.lugar_descompostura = None
            if self.colas_pala[camion.nro_pala].cola:

                # Generar partida del camion del aplastador
                tiempo = camion.tiempo_de_descarga() + self.reloj_simulacion
                self.lista_de_eventos['partida_aplastador'].agregar(tiempo, camion)

                self.estado_pala[camion.nro_pala] = Simulacion.OCUPADO

            else:
                self.colas_pala[camion.nro_pala].agregar(camion)

        elif camion.lugar_descompostura == 'partida_aplstador':
            camion.lugar_descompostura = None

            # Generar arribo a la pala del camion que parte (tiempo de regreso)
            tiempo = camion.tiempo_de_regreso() + self.reloj_simulacion
            self.lista_de_eventos['arribo_pala'][camion.nro_pala].agregar(tiempo, camion)

        elif camion.lugar_descompostura == 'arribo_aplstador':
            camion.lugar_descompostura = None
            if self.cola_aplastador.cola:

                # Generar partida del camion que sale de la cola nro_pala
                tiempo = camion.tiempo_de_carga() + self.reloj_simulacion
                self.lista_de_eventos['partida_pala'][camion.nro_pala].agregar(tiempo, camion)

                self.estado_aplastador = Simulacion.OCUPADO
            else:
                self.cola_aplastador.agregar(camion)

        if self.cola_mecanico.cola:
            camion_cola = self.cola_mecanico.cola.pop(0)

            # Generar partida del camion, teniendo en cuenta donde se encuentra
            tiempo_de_viaje = 0
            if ('aplastador' in self.ult_localizacion_mecanico and 'aplastador' not in camion_cola.lugar_descompostura) \
                    or ('pala' in self.ult_localizacion_mecanico and 'pala' not in camion_cola.lugar_descompostura):
                tiempo_de_viaje = 1

            tiempo = tiempo_de_viaje + camion.tiempo_de_reparacion() + self.reloj_simulacion
            self.lista_de_eventos["fin_de_reparacion"].agregar(tiempo, camion)

        else:
            self.estado_mecanico = Simulacion.DESOCUPADO

    def reportes(self):
        # TODO Implement
        PLACEHOLDER = 0

    def tiempos(self):
        # TODO refactorizar codigo repetido
        tiempo_mas_reciente = Tiempo(Simulacion.INFINITO, None)
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

    def inicializacion(self):

        # Contadores Estadisticos
        self.tiempo_ocioso = 0
        self.total_material_transportado = 0
        self.total_descomposturas = 0

        # Variables de estado

        self.reloj_simulacion = 0
        self.estado_pala = [Simulacion.DESOCUPADO, Simulacion.DESOCUPADO, Simulacion.DESOCUPADO]
        self.estado_aplastador = Simulacion.DESOCUPADO
        self.estado_mecanico = Simulacion.DESOCUPADO
        self.ult_localizacion_mecanico = 'pala'
        self.dcrt = 0

        self.colas_pala = []
        for i in range(3):
            cola_pala = Cola('pala')
            cola_pala.agregar(Camion(50, i))
            cola_pala.agregar(Camion(20, i))
            self.colas_pala.append(cola_pala)

        self.cola_aplastador = Cola('aplastador')
        self.cola_mecanico = Cola('mecanico')

        # Lista de eventos

        # Generar evento desencadenador
        # Deshabilitar temporalmente la probabilidad de descompostura

        temp_descompostura = Simulacion.PROB_DESCOMPOSTURA
        Simulacion.PROB_DESCOMPOSTURA = -1

        for i in range(3):
            self.arribo_pala(Camion(20, i))

        # Devolver el valor original
        Simulacion.PROB_DESCOMPOSTURA = temp_descompostura

        self.lista_de_eventos = {'arribo_pala': [Evento('arribo_pala'),
                                                 Evento('arribo_pala'),
                                                 Evento('arribo_pala')],
                                 'partida_pala': [Evento('partida_pala'),
                                                  Evento('partida_pala'),
                                                  Evento('partida_pala')],
                                 'arribo_aplastador': Evento('arribo_aplastador'),
                                 'partida_aplastador': Evento('partida_aplastador'),
                                 'fin_de_reparacion': Evento('fin_de_reparacion')}

    def __init__(self, duracion_simulacion):
        self.duracion_simulacion = duracion_simulacion

        # Contadores estadisticos
        self.tiempo_ocioso = None
        self.total_material_transportado = None
        self.total_descomposturas = None

        # Variables de estado
        self.reloj_simulacion = None
        self.estado_pala = None
        self.estado_aplastador = None
        self.estado_mecanico = None
        self.ult_localizacion_mecanico = None
        self.ubicacion_mecanico = None
        self.dcrt = None
        self.colas_pala = None
        self.cola_aplastador = None
        self.cola_mecanico = None
        self.lista_de_eventos = None
