from simulacion import Simulacion
from altmod import sim2mec, simInsp, simUnaCola, simUnaCola2Mec, simUnaColaInsp
from scipy.stats import t
import numpy
import csv
import math
import multiprocessing
from functools import partial

#
# Me disculpo por adelantado si alguien intenta entender el código que está debajo
#


def observaciones():
    numpy.random.seed(504983980)

    seeds = numpy.random.randint(1, high=numpy.iinfo(numpy.int32).max, size=20)

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    func = partial(worker_welch, 72500, 0, seeds)

    results = pool.imap_unordered(func, range(20))

    pool.close()
    pool.join()

    return list(results)


def observaciones_no_mp(n=4, t=72500, k=0):
    numpy.random.seed(504983980)

    seeds = numpy.random.randint(1, high=numpy.iinfo(numpy.int32).max, size=20)

    result = []

    for i in range(n):
        result.append(worker_welch(t, k, seeds, i))

    return result


def welch():
    replicas = observaciones()
    for i in range(3):
        if i == 0:
            path = 'ocioso.csv'
        elif i == 1:
            path = 'material.csv'
        else:
            path = 'descompuestos.csv'
        save_to_file_welch(replicas, path, i)


def worker_welch(t, k, seeds, i):
    numpy.random.seed(seeds[i])
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
    sim.start(t)
    print(i)
    return sim.reportes_por_mes


def saveRankingSeleccion():

    t = 432500

    for i in range(6):
        lot = obs_a_lotes(observaciones_no_mp(1, t, i))
        save_to_file_relativa(lot, str(i) + '.csv')


def ranking_selection():

    lotes = list()

    n0 = 20
    indiferencia = [2, 100, 2, 0.05]
    h1 = 3.337
    k = 6

    for i in range(k):
        lotes.append(read_from_file(str(i)+'.csv'))

    for m in range(3):
        medias = []
        medias2 = []
        media_sample = []
        varianzas = []
        N = []
        W = []

        for i in range(k):

            # Media 1
            suma = 0
            for value in lotes[i][0:n0]:
                suma += value[m]
            medias.append(suma / n0)

            # Varianza
            suma = 0
            for value in lotes[i][0:n0]:
                suma += math.pow(value[m] - medias[i], 2)

            varianzas.append(suma / (n0-1))

            temp_calc = math.pow(h1, 2)*varianzas[i]/math.pow(indiferencia[m], 2)

            temp_calc = int(math.ceil(temp_calc))

            if n0 + 1 > temp_calc:
                N.append(n0 + 1)
            else:
                N.append(temp_calc)

            # Segunda Etapa

            # Media 2
            suma = 0
            for value in lotes[i][n0:N[i]]:
                suma += value[m]
            medias2.append(suma / (N[i] - n0))

            # Pesos
            uno = n0 / N[i]
            dos = N[i] / n0
            tres = (N[i] - n0) * math.pow(indiferencia[m], 2)/(math.pow(h1, 2)*varianzas[i])

            W.append(uno * (1 + math.sqrt(1 - dos*(1 - tres))))

            media_sample.append(W[i]*medias[i] + (1-W[i])*medias2[i])

        # Agregar breakpoint aca


def read_from_file(inputfilepath):
    print("Reading :", inputfilepath)

    # CSV Fields
    ocioso = 1
    materiales = 2
    descomposturas = 3

    lotes = []
    with open(inputfilepath, encoding="utf8") as inputFile:
        # Skips header
        next(inputFile)

        reader = csv.reader(inputFile, delimiter=",")
        for line in reader:
            lot = list()
            lot.append(float(line[ocioso]))
            lot.append(float(line[materiales]))
            lot.append(float(line[descomposturas]))
            lotes.append(lot)

    return lotes


def obs_a_lotes(obser, v =3):

    replicas = []

    obs = obser[0]

    k = 4

    l = 4

    for i in range(len(obs)):

        # Sacar sesgo
        if i + 1 <= l:
            continue

        if i % k == 0 and i < len(obs):
            suma = [0, 0, 0]
            prom = [0, 0, 0]
            for j in range(i, i+k):

                for m in range(v):
                    suma[m] += obs[j][m]

            for m in range(v):
                prom[m] = suma[m]/k
            replicas.append(prom)

    return replicas


def get_n():
    """
    Obtener el n* necesario para que las variables tengan en conjunto un error de 0.15
    """
    error = 0.05

    lotes = obs_a_lotes(observaciones_no_mp())
    n = 2
    v = 3

    while True and n < 25:

        media = []
        varianza = []
        delta = []
        stop = 0

        # Para cada variable
        for m in range(v):
            suma = 0
            for value in lotes[0:n]:
                suma += value[m]

            media.append(suma / n)

            suma = 0
            for value in lotes[0:n]:
                suma += math.pow(value[m] - media[m], 2)

            varianza.append(suma / (n-1))

            tstud = t.ppf(1 - (error /2 ), n - 1)
            sq = math.sqrt(varianza[m] / n)
            delta.append(t.ppf(1 - (error / 2), n - 1) * math.sqrt(varianza[m] / n))

            if (delta[m] / abs(media[m])) <= error:
                if m == 0:
                    asd = 2
                stop += 1

        print('n= ', n, '   stop:', stop)

        if stop == v:
            break

        n += 1


def save_to_file_welch(replicas, outputfilepath, k):
    print("Saving to:", outputfilepath)

    with open(outputfilepath, "w", encoding='utf-8') as saveFile:
        for i in range(1, len(replicas[0])):
            saveFile.write("Mes " + str(i) + ",")
        saveFile.write("Mes " + str((len(replicas[0]))) + "\n")
        writer = csv.writer(saveFile, delimiter=",", lineterminator='\n')

        for rep in replicas:
            temp = []
            for re in rep:
                temp.append(re[k])

            writer.writerow(temp)


def save_to_file_relativa(obs, outputfilepath):
    print("Saving to:", outputfilepath)

    with open(outputfilepath, "w", encoding='utf-8') as saveFile:

        saveFile.write("Lote,ocioso,material,descompuestos\n")
        for i in range(len(obs)):

            writer = csv.writer(saveFile, delimiter=",", lineterminator='\n')

            row = list()
            row.append(i + 1)

            for k in range(3):
                row.append(obs[i][k])

            writer.writerow(row)


def save_to_file_ranking_seleccion(obs, outputfilepath):
    print("Saving to:", outputfilepath)

    with open(outputfilepath, "w", encoding='utf-8') as saveFile:
        for i in range(1, len(obs)):
            saveFile.write("Lote " + str(i) + ",")
        saveFile.write("Lote " + str(len(obs)) + "\n")
        writer = csv.writer(saveFile, delimiter=",", lineterminator='\n')

        for k in range(3):
            row = list()
            for ob in obs:
                row.append(ob[k])

            writer.writerow(row)

if __name__ == "__main__":
    # get_n()

    # lot = obs_a_lotes(observaciones_no_mp())
    #
    # # save_to_file_relativa(lot, 'lotes.csv')
    # save_to_file_ranking_seleccion(lot, 'lotestrans.csv')

    # ranking_selection()

    # saveRankingSeleccion()
    # ranking_selection()
    welch()
