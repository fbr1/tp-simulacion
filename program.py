from Cola import Cola
from Camion import Camion

INFINITO = 99999999

class Simulacion:

    def start(self, tiempo_simulacion = 200):
        self.inicializacion()
        for i in range(tiempo_simulacion):
            evento, nro_pala = self.tiempos()

            # Ejecutar la rutina de evento
            if not nro_pala:
                getattr(self, evento)()
            else:
                getattr(self, evento)(nro_pala)

        self.reportes()

    def arribo_pala(self, nro_pala):
        # TODO Implement
        PLACEHOLDER = 0

    def partida_pala(self, nro_pala):
        # TODO Implement
        PLACEHOLDER = 0

    def arribo_aplastador(self):
        # TODO Implement
        PLACEHOLDER = 0

    def partida_aplastador(self):
        # TODO Implement
        PLACEHOLDER = 0

    def descompostura(self):
        # TODO Implement
        PLACEHOLDER = 0

    def fin_de_reparacion(self):
        # TODO Implement
        PLACEHOLDER = 0

    def reportes(self):
        # TODO Implement
        PLACEHOLDER = 0

    def tiempos(self):
        tiempo_mas_reciente = INFINITO
        key_mas_reciente = None
        indice_pala = None

        for key, value in self.lista_de_eventos.items():
            if type(value) is list:
                for i in range(len(value)):
                    if value[i] < tiempo_mas_reciente:
                        tiempo_mas_reciente = value[i]
                        indice_pala = i
                        key_mas_reciente = key
            else:
                if value < tiempo_mas_reciente:
                    tiempo_mas_reciente = value
                    indice_pala = None
                    key_mas_reciente = key

        self.reloj_simulacion = tiempo_mas_reciente

        return key_mas_reciente, indice_pala

    def inicializacion(self):

        # Contadores Estadisticos
        self.tiempo_ocioso = 0
        self.total_material_transportado = 0
        self.total_descomposturas = 0

        # Variables de estado

        self.reloj_simulacion = 0
        self.estado_pala = [0, 0, 0]
        self.estado_aplastador = 0
        self.estado_mecanico = 0
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
        self.lista_de_eventos = {'arribo_pala': [INFINITO, INFINITO, INFINITO],
                                 'partida_pala': [],
                                 'arribo_aplastador': INFINITO,
                                 'partida_aplastador:': INFINITO,
                                 'descompostura': INFINITO,
                                 'fin_de_reparacion': INFINITO}

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
        self.dcrt = None
        self.colas_pala = None
        self.cola_aplastador = None
        self.cola_mecanico = None
        self.lista_de_eventos = None


