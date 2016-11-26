from Cola import Cola
from Camion import Camion

INFINITO = 99999999
PROB_DESCOMPOSICION = 0.1
OCUPADO = 1
DESOCUPADO = 0


class Simulacion:

    def start(self, tiempo_simulacion = 200):
        self.inicializacion()
        for i in range(tiempo_simulacion):
            evento, camion = self.tiempos()

            # Ejecutar la rutina de evento
            getattr(self, evento)(camion)

        self.reportes()

    def partida_pala(self, camion):
        # TODO Generar variable aleatoria
        numero_aleatorio = 0

        if numero_aleatorio < PROB_DESCOMPOSICION:
            camion.lugar_descompostura = 'partida_aplastador'
            self.descompostura(camion)
        else:
            # TODO Generar arribo aplastador
            PLACEHOLDER = 0

        # Si hay camiones en la cola de la pala nro_pala
        cola_pala = self.colas_pala[camion.nro_pala]
        if cola_pala.cola:
            camion_cola = cola_pala.cola.pop(0)
            # TODO Generar partida pala
            self.estado_pala = OCUPADO
        else:
            self.estado_pala = DESOCUPADO

    def arribo_aplastador(self, camion):
        # TODO Generar variable aleatoria
        numero_aleatorio = 0

        if numero_aleatorio < PROB_DESCOMPOSICION:
            camion.lugar_descompostura = 'arribo_aplastador'
            self.descompostura(camion)
        elif self.estado_aplastador == DESOCUPADO:
            # TODO generar partida del camion del aplastador
            self.estado_aplastador = OCUPADO
        else:
            self.cola_aplastador.agregar(camion)

    def partida_aplastador(self, camion):
        # TODO Generar variable aleatoria
        numero_aleatorio = 0

        if numero_aleatorio < PROB_DESCOMPOSICION:
            camion.lugar_descompostura = 'partida_aplastador'
            self.descompostura(camion)
        else:
            # TODO Generar arribo en la pala correspondiente
            PLACEHOLDER = 0
        if self.cola_aplastador.cola:
            camion_cola = self.cola_aplastador.cola.pop(0)
            # TODO Generar partida aplastador
            self.estado_aplastador = OCUPADO
        else:
            self.estado_aplastador = DESOCUPADO

    def arribo_pala(self, camion):
        # TODO Generar variable aleatoria
        numero_aleatorio = 0

        if numero_aleatorio < PROB_DESCOMPOSICION:
            camion.lugar_descompostura = 'arribo_pala'
            self.descompostura(camion)
        elif self.estado_pala == DESOCUPADO:
            #TODO generar partida del camion que sale de la cola nro_pala
            self.estado_pala[camion.nro_pala] = OCUPADO
        else:
            self.colas_pala[camion.nro_pala].agregar(camion)

    def descompostura(self, camion):
        if self.estado_mecanico == DESOCUPADO:
            # TODO generar partida del camion, tener en cuenta donde se encuentra
            self.estado_mecanico = OCUPADO
        else:
            self.cola_mecanico.agregar(camion)

    def fin_de_reparacion(self, camion):
        if camion.lugar_descompostura == 'partida_pala':
            camion.lugar_descompostura = None
            # TODO Generar arribo en aplastador

        elif camion.lugar_descompostura == 'arribo_pala':
            camion.lugar_descompostura = None
            if self.colas_pala[camion.nro_pala].cola:
                # TODO generar partida del camion que sale de la pala nro_pala
                self.estado_pala[camion.nro_pala] = OCUPADO
            else:
                self.colas_pala[camion.nro_pala].agregar(camion)

        elif camion.lugar_descompostura == 'partida_aplstador':
            camion.lugar_descompostura = None
            # TODO Generar arribo en la pala i

        elif camion.lugar_descompostura == 'arribo_aplstador':
            camion.lugar_descompostura = None
            if self.cola_aplastador.cola:
                # TODO generar partida del camion del aplastador
                self.estado_aplastador = OCUPADO
            else:
                self.cola_aplastador.agregar(camion)

        if self.cola_mecanico.cola:
            camion_cola = self.cola_mecanico.cola.pop(0)
            # TODO generar partida del camion, tener en cuenta donde se encuentra
        else:
            self.estado_mecanico = DESOCUPADO

    def reportes(self):
        # TODO Implement
        PLACEHOLDER = 0

    def tiempos(self):
        tiempo_mas_reciente = INFINITO
        key_mas_reciente = None
        camion_mas_reciente = None

        for key, value in self.lista_de_eventos.items():
            if type(value) is list:
                for i in range(len(value)):
                    if value[i]['tiempo'] < tiempo_mas_reciente:
                        tiempo_mas_reciente = value[i]
                        key_mas_reciente = key
                        camion_mas_reciente = value[i]['camion']
            else:
                if value['tiempo'] < tiempo_mas_reciente:
                    tiempo_mas_reciente = value
                    key_mas_reciente = key
                    camion_mas_reciente = value['camion']

        self.reloj_simulacion = tiempo_mas_reciente

        return key_mas_reciente, camion_mas_reciente

    def inicializacion(self):

        # Contadores Estadisticos
        self.tiempo_ocioso = 0
        self.total_material_transportado = 0
        self.total_descomposturas = 0

        # Variables de estado

        self.reloj_simulacion = 0
        self.estado_pala = [DESOCUPADO, DESOCUPADO, DESOCUPADO]
        self.estado_aplastador = DESOCUPADO
        self.estado_mecanico = DESOCUPADO
        self.dcrt = 0

        self.colas_pala = []
        for i in range(3):
            cola_pala = Cola('pala')
            cola_pala.agregar(Camion(50, i))
            cola_pala.agregar(Camion(20, i))
            cola_pala.agregar(Camion(20, i))
            self.colas_pala.append(cola_pala)

        self.cola_aplastador = Cola('aplastador')
        self.cola_mecanico = Cola('mecanico')

        # Lista de eventos
        # TODO generar partidas de la pala
        self.lista_de_eventos = {'arribo_pala': [{'tiempo': INFINITO, 'camion': None},
                                                 {'tiempo': INFINITO, 'camion': None},
                                                 {'tiempo': INFINITO, 'camion': None}],
                                 'partida_pala': [],
                                 'arribo_aplastador': {'tiempo': INFINITO, 'camion': None},
                                 'partida_aplastador:': {'tiempo': INFINITO, 'camion': None},
                                 'fin_de_reparacion': {'tiempo': INFINITO, 'camion': None}}

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
        self.ubicacion_mecanico = None
        self.dcrt = None
        self.colas_pala = None
        self.cola_aplastador = None
        self.cola_mecanico = None
        self.lista_de_eventos = None


