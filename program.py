from simulacion import Simulacion
from altmod import sim2mec, simInsp, simUnaCola, simUnaCola2Mec, simUnaColaInsp
from scipy.stats import t
import numpy
import csv
import math
import multiprocessing
from functools import partial


def main():
    for k in range(6):
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        func = partial(worker, k)

        reportes = pool.imap_unordered(func, range(1333))

        pool.close()
        pool.join()

        if k == 0:
            path = 'modelo_original.csv'
        elif k == 1:
            path = 'modelo_UnaCola.csv'
        elif k == 2:
            path = 'modelo_Insp.csv'
        elif k == 3:
            path = 'modelo_UnaColaInsp.csv'
        elif k == 4:
            path = 'modelo_2Mec.csv'
        else:
            path = 'modelo_UnaCola2Mec.csv'
        save_to_file(reportes, path)


def worker(k, i):
    m = i + 1
    numpy.random.seed(m)
    if k == 0:
        sim = Simulacion()
    elif k == 1:
        sim = simUnaCola.SimulacionUnaCola()
    elif k == 2:
        sim = simInsp.SimulacionInsp()
    elif k == 3:
        sim = simUnaColaInsp.SimulacionUnaColaInsp()
    elif k == 4:
        sim = sim2mec.Simulacion2mec()
    else:
        sim = simUnaCola2Mec.SimulacionUnaCola2mec()
    sim.start(200)
    return sim.reportes()


def save_to_file(reportes, outputfilepath):
    print("Saving to:", outputfilepath)

    with open(outputfilepath, "w", encoding='utf-8') as saveFile:
        saveFile.write("tiempo_ocioso,material,descomposturas,descompuestos_tiempo\n")
        writer = csv.writer(saveFile, delimiter=",", lineterminator='\n')
        ocioso = 0
        material = 0
        descomposturas = 0
        descompuestos_tiempo = 0
        for re in reportes:
            ocioso += re[0]
            material += re[1]
            descomposturas += re[2]
            descompuestos_tiempo += re[3]

            writer.writerow([re[0], re[1], re[2], re[3]])

        print('ocioso: ', ocioso/1333)
        print('material: ', material/1333)
        print('descomposturas: ', descomposturas/1333)
        print('descompuestos_tiempo: ', descompuestos_tiempo/1333)


def ranking_selection():

    n0 = 40
    k = 6
    indiferencia = [1, 2, 0.10, 0.05]
    h1 = 3.260

    for m in range(4):
        reportes = []
        medias = []
        medias2 = []
        media_sample = []
        varianzas = []
        N = []
        W = []

        for i in range(k):
            if i == 0:
                sim = Simulacion()
            elif i == 1:
                sim = simUnaCola.SimulacionUnaCola()
            elif i == 2:
                sim = simInsp.SimulacionInsp()
            elif i == 3:
                sim = simUnaColaInsp.SimulacionUnaColaInsp()
            elif i == 4:
                sim = sim2mec.Simulacion2mec()
            else:
                sim = simUnaCola2Mec.SimulacionUnaCola2mec()

            # Primera Etapa
            j = 1
            reportes_parciales = []
            while j < n0 + 1:
                numpy.random.seed(j)
                sim.start(200)
                reportes_parciales.append(sim.reportes()[m])
                j += 1

            reportes.append(reportes_parciales)

            # Media 1
            suma = 0
            for value in reportes_parciales:
                suma += value
            medias.append(suma / n0)

            # Varianza
            suma = 0
            for value in reportes_parciales:
                suma += math.pow(value - medias[i], 2)

            varianzas.append(suma / (n0-1))

            temp_calc = math.pow(h1, 2)*varianzas[i]/math.pow(indiferencia[m], 2)

            temp_calc = int(math.ceil(temp_calc))

            if n0 + 1 > temp_calc:
                N.append(n0 + 1)
            else:
                N.append(temp_calc)

            # Segunda Etapa
            j = n0 + 1
            while j < N[i] + 1:
                numpy.random.seed(j)
                sim.start(200)
                reportes_parciales.append(sim.reportes()[m])
                j += 1

            # Media 2
            suma = 0
            for value in reportes_parciales[n0:N[i]]:
                suma += value
            medias2.append(suma / (N[i] - n0))

            # Pesos
            uno = n0 / N[i]
            dos = N[i] / n0
            tres = (N[i] - n0) * math.pow(indiferencia[m], 2)/(math.pow(h1, 2)*varianzas[i])

            W.append(uno * (1 + math.sqrt(1 - dos*(1 - tres))))

            media_sample.append(W[i]*medias[i] + (1-W[i])*medias2[i])

        # Agregar breakpoint aca


def get_n():
    """
    Obtener el n* necesario para que las variables tengan en conjunto un error de 0.10
    """
    error = 0.025
    n = 10
    i = 1
    reportes = []
    while i < n:
        numpy.random.seed(i)
        sim = Simulacion()
        sim.start(200)
        reportes.append((sim.reportes()))
        i += 1

    while True:

        media = []
        varianza = []
        delta = []
        stop = 0

        numpy.random.seed(n)
        sim = Simulacion()
        sim.start(200)
        reportes.append((sim.reportes()))

        for k in range(4):
            suma = 0
            for value in reportes:
                suma += value[k]

            media.append(suma / n)

            suma = 0
            for value in reportes:
                suma += math.pow(value[k]-media[k], 2)

            varianza.append(suma/n)

            delta.append((t.ppf(1-0.0125, n-1)) * math.sqrt(varianza[k]/n))

            if (delta[k] / abs(media[k])) <= error:
                stop += 1

        print('n= ', n, '   stop:', stop)

        if stop == 4:
            break

        n += 1

if __name__ == "__main__":
    main()
