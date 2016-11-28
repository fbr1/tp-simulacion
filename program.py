from simulacion import Simulacion
import numpy


def main():
    numpy.random.seed(43)
    sim = Simulacion()
    sim.start(200)


def mainloop():
    i = 0
    while True:
        print('Seed: ', i)
        numpy.random.seed(i)
        sim = Simulacion()
        sim.start(30)
        i += 1

if __name__ == "__main__":
    main()
