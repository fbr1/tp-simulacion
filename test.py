from Cola import Cola
from Camion import Camion


def main():

    # Test Cola Pala
    cola_pala = Cola('pala')
    lista = [Camion(20, idn=1), Camion(50, idn=2), Camion(20, idn=3), Camion(50, idn=4)]
    for item in lista:
        cola_pala.agregar(item)

    lista_ids = [cam.idn for cam in cola_pala.cola]
    if lista_ids != [1, 2, 3, 4]:
        print(lista_ids)
        print([1, 2, 3, 4])
        return False

    # Test _obtener_indice_ultima_ocurrencia
    cola_indices = Cola('asd')
    cola_indices.cola = [Camion(20, idn=1), Camion(50, idn=2), Camion(20, idn=3), Camion(50, idn=4)]
    indice = cola_pala._obtener_indice_ultima_ocurrencia(50)

    if indice != 3:
        print(indice)
        print(3)
        return False

    # Test Cola aplastador
    cola_aplanador = Cola('aplastador')
    for item in lista:
        cola_aplanador.agregar(item)

    lista_ids = [cam.idn for cam in cola_aplanador.cola]
    if lista_ids != [2, 4, 1, 3]:
        print(lista_ids)
        print([2, 4, 1, 3])
        return False

    # TODO test cola mecanico

    return True

if __name__ == "__main__":
    if main():
        print('Test Passed')
    else:
        print('Test Failed')
