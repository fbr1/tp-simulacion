from simulacion import Simulacion
from simulacionAlt import SimulacionAlt
import numpy
import csv


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
        for re in reportes:

            writer.writerow([re[0], re[1], re[2], re[3]])

if __name__ == "__main__":
    main()

