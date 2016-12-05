from simulacion import Simulacion
from cola import Cola
from evento import Evento


class Simulacion2mec(Simulacion):

    PALA = 0
    APLASTADOR = 1

    def descompostura(self, camion):

        self.total_descomposturas += 1
        camion.tiempo_de_descompostura = self.reloj_simulacion

        if 'aplastador' in camion.lugar_descompostura:
            lugar = Simulacion2mec.APLASTADOR
        else:
            lugar = Simulacion2mec.PALA

        # Acumulada de descompuestos en el tiempo
        self.acrt += (self.reloj_simulacion - self.ultima_medicion_descomposturas) \
            * (len(self.cola_mecanico[lugar].cola) + self.estado_mecanico[lugar])
        self.ultima_medicion_descomposturas = self.reloj_simulacion

        if self.estado_mecanico[lugar] == Simulacion.DESOCUPADO:

            tiempo = camion.tiempo_de_reparacion() + self.reloj_simulacion
            self.lista_de_eventos["fin_de_reparacion"][lugar].agregar(tiempo, camion)

            self.estado_mecanico[lugar] = Simulacion.OCUPADO
        else:
            self.cola_mecanico[lugar].agregar(camion)

    def fin_de_reparacion(self, camion):

        lugar_descompostura = camion.lugar_descompostura
        self.tiempo_ocioso += self.reloj_simulacion - camion.tiempo_de_descompostura

        if 'aplastador' in camion.lugar_descompostura:
            lugar = Simulacion2mec.APLASTADOR
        else:
            lugar = Simulacion2mec.PALA

        camion.lugar_descompostura = None
        camion.tiempo_de_descompostura = None

        # Acumulada de descompuestos en el tiempo
        self.acrt += (self.reloj_simulacion - self.ultima_medicion_descomposturas) \
            * (len(self.cola_mecanico[lugar].cola) + self.estado_mecanico[lugar])
        self.ultima_medicion_descomposturas = self.reloj_simulacion

        if lugar_descompostura == 'partida_pala':

            # Generar arribo al aplastador del camion que parte (tiempo de viaje)
            tiempo = camion.tiempo_de_viaje() + self.reloj_simulacion
            self.lista_de_eventos['arribo_aplastador'].agregar(tiempo, camion)

        elif lugar_descompostura == 'arribo_pala':

            if self.estado_pala[camion.nro_pala] == Simulacion.DESOCUPADO:
                # Generar partida del camion que sale de la cola nro_pala
                tiempo = camion.tiempo_de_carga() + self.reloj_simulacion
                self.lista_de_eventos['partida_pala'][camion.nro_pala].agregar(tiempo, camion)
                self.estado_pala[camion.nro_pala] = Simulacion.OCUPADO

            else:
                self.colas_pala[camion.nro_pala].agregar(camion)

        elif lugar_descompostura == 'partida_aplastador':

            # Generar arribo a la pala del camion que parte (tiempo de regreso)
            tiempo = camion.tiempo_de_regreso() + self.reloj_simulacion
            self.lista_de_eventos['arribo_pala'][camion.nro_pala].agregar(tiempo, camion)

        elif lugar_descompostura == 'arribo_aplastador':
            if self.estado_aplastador == Simulacion.DESOCUPADO:

                # Generar partida del camion del aplastador
                tiempo = camion.tiempo_de_descarga() + self.reloj_simulacion
                self.lista_de_eventos['partida_aplastador'].agregar(tiempo, camion)
                self.estado_aplastador = Simulacion.OCUPADO

            else:
                self.cola_aplastador.agregar(camion)

        if self.cola_mecanico[lugar].cola:
            camion_cola = self.cola_mecanico[lugar].cola.pop(0)

            # Generar partida del camion
            tiempo = camion.tiempo_de_reparacion() + self.reloj_simulacion
            self.lista_de_eventos["fin_de_reparacion"][lugar].agregar(tiempo, camion_cola)

        else:
            self.estado_mecanico[lugar] = Simulacion.DESOCUPADO

    def inicializacion(self, duracion_simulacion):

        super(Simulacion2mec, self).inicializacion(duracion_simulacion)

        self.estado_mecanico = [Simulacion.DESOCUPADO, Simulacion.DESOCUPADO]

        self.cola_mecanico = [Cola('mecanico'), Cola('mecanico')]

        # Lista de eventos
        self.lista_de_eventos = {'arribo_pala': [Evento('arribo_pala'),
                                                 Evento('arribo_pala'),
                                                 Evento('arribo_pala')],
                                 'partida_pala': [Evento('partida_pala'),
                                                  Evento('partida_pala'),
                                                  Evento('partida_pala')],
                                 'arribo_aplastador': Evento('arribo_aplastador'),
                                 'partida_aplastador': Evento('partida_aplastador'),
                                 'fin_de_reparacion': [Evento('fin_de_reparacion'),
                                                       Evento('fin_de_reparacion')]}
