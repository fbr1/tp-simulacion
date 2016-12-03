from simulacion import Simulacion
from simulacionAlt import SimulacionAlt
from scipy.stats import t
import numpy
import csv
import math


def main():
    for k in range(2):
        reportes = []

        i = 1
        while i < 101:
            numpy.random.seed(i)
            sim = Simulacion() if k == 0 else SimulacionAlt()
            sim.start(200)
            reportes.append((sim.reportes()))
            i += 1

        save_to_file(reportes, 'modelo_original.csv' if k == 0 else 'modelo_alternativo.csv')


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

        print('ocioso: ' , ocioso /100)
        print('material: ' , material/100)
        print('descomposturas: ' , descomposturas/100)
        print('descompuestos_tiempo: ' , descompuestos_tiempo/100)


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
    get_n()
