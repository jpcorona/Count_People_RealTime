from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np

class CentroidTracker:
    def __init__(self, maxDesaparecidos=50, maxDistancia=50):
        # Inicializar el próximo ID de objeto único junto con dos diccionarios ordenados
        # para hacer un seguimiento del mapeo de un ID de objeto dado a su centroide y el número de fotogramas consecutivos
        # en los que se ha marcado como "desaparecido", respectivamente.
        self.siguienteIDObjeto = 0
        self.objetos = OrderedDict()
        self.desaparecidos = OrderedDict()

        # Almacenar el número máximo de fotogramas consecutivos en los que se permite que un
        # objeto dado sea marcado como "desaparecido" hasta que necesitemos eliminarlo del seguimiento.
        self.maxDesaparecidos = maxDesaparecidos

        # Almacenar la distancia máxima entre centroides para asociar un objeto.
        # Si la distancia es mayor que esta distancia máxima, comenzaremos a marcar el objeto como "desaparecido".
        self.maxDistancia = maxDistancia

    def registrar(self, centroide):
        # Al registrar un objeto, usamos el siguiente ID de objeto disponible para almacenar el centroide.
        self.objetos[self.siguienteIDObjeto] = centroide
        self.desaparecidos[self.siguienteIDObjeto] = 0
        self.siguienteIDObjeto += 1

    def eliminar_registro(self, IDObjeto):
        # Para eliminar el registro de un ID de objeto, eliminamos el ID de objeto de ambos de nuestros respectivos diccionarios.
        del self.objetos[IDObjeto]
        del self.desaparecidos[IDObjeto]

    def actualizar(self, rectangulos):
        # Comprobar si la lista de rectángulos de cuadros delimitadores de entrada está vacía.
        if len(rectangulos) == 0:
            # Recorrer los objetos rastreados existentes y marcarlos como "desaparecidos".
            for IDObjeto in list(self.desaparecidos.keys()):
                self.desaparecidos[IDObjeto] += 1

                # Si hemos alcanzado un número máximo de fotogramas consecutivos en los que
                # un objeto dado ha sido marcado como ausente, eliminar su registro.
                if self.desaparecidos[IDObjeto] > self.maxDesaparecidos:
                    self.eliminar_registro(IDObjeto)

            # Retornar temprano ya que no hay centroides ni información de seguimiento para actualizar.
            return self.objetos

        # Inicializar una matriz de centroides de entrada para el fotograma actual.
        centroidesEntrada = np.zeros((len(rectangulos), 2), dtype="int")

        # Recorrer los rectángulos de cuadros delimitadores.
        for (i, (inicioX, inicioY, finX, finY)) in enumerate(rectangulos):
            # Utilizar las coordenadas del cuadro delimitador para derivar el centroide.
            cX = int((inicioX + finX) / 2.0)
            cY = int((inicioY + finY) / 2.0)
            centroidesEntrada[i] = (cX, cY)

        # Si actualmente no estamos siguiendo ningún objeto, tomar los centroides de entrada y registrar cada uno de ellos.
        if len(self.objetos) == 0:
            for i in range(0, len(centroidesEntrada)):
                self.registrar(centroidesEntrada[i])

        # De lo contrario, estamos siguiendo objetos actualmente, por lo que necesitamos intentar
        # hacer coincidir los centroides de entrada con los centroides de objetos existentes.
        else:
            # Obtener el conjunto de ID de objetos y centroides correspondientes.
            IDsObjeto = list(self.objetos.keys())
            centroidesObjeto = list(self.objetos.values())

            # Calcular la distancia entre cada par de centroides de objetos e centroides de entrada, respectivamente.
            D = dist.cdist(np.array(centroidesObjeto), centroidesEntrada)

            # Para realizar esta coincidencia, debemos (1) encontrar el valor más pequeño en cada fila y luego (2) ordenar los índices de fila
            # en función de sus valores mínimos para que la fila con el valor más pequeño esté al frente de la lista de índices.
            filas = D.min(axis=1).argsort()

            # Luego, realizamos un proceso similar en las columnas encontrando el valor más pequeño en cada columna y luego
            # ordenando usando la lista de índices de fila calculada previamente.
            columnas = D.argmin(axis=1)[filas]

            # Para determinar si necesitamos actualizar, registrar o eliminar el registro de un objeto,
            # debemos realizar un seguimiento de cuáles de las filas y columnas ya hemos examinado.
            filasUtilizadas = set()
            columnasUtilizadas = set()

            # Recorrer la combinación de las tuplas de índices (fila, columna).
            for (fila, columna) in zip(filas, columnas):
                # Si ya hemos examinado antes el valor de fila o columna, ignorarlo.
                if fila in filasUtilizadas or columna in columnasUtilizadas:
                    continue

                # Si la distancia entre los centroides es mayor que la distancia máxima, no asociar los dos centroides al mismo objeto.
                if D[fila, columna] > self.maxDistancia:
                    continue

                # De lo contrario, obtener el ID de objeto para la fila actual,
                # establecer su nuevo centroide y reiniciar el contador de desaparecidos.
                IDObjeto = IDsObjeto[fila]
                self.objetos[IDObjeto] = centroidesEntrada[columna]
                self.desaparecidos[IDObjeto] = 0

                # Indicar que hemos examinado cada uno de los índices de fila y columna, respectivamente.
                filasUtilizadas.add(fila)
                columnasUtilizadas.add(columna)

            # Calcular tanto el índice de fila como el índice de columna que AÚN no hemos examinado.
            filasNoUtilizadas = set(range(0, D.shape[0])).difference(filasUtilizadas)
            columnasNoUtilizadas = set(range(0, D.shape[1])).difference(columnasUtilizadas)

            # En el caso de que el número de centroides de objetos sea igual o mayor que el número de centroides de entrada,
            # necesitamos verificar si algunos de estos objetos han desaparecido potencialmente.
            if D.shape[0] >= D.shape[1]:
                # Recorrer los índices de fila no utilizados
                for fila in filasNoUtilizadas:
                    # Obtener el ID de objeto para el índice de fila correspondiente
                    # e incrementar el contador de desaparecidos.
                    IDObjeto = IDsObjeto[fila]
                    self.desaparecidos[IDObjeto] += 1

                    # Comprobar si el número de fotogramas consecutivos en los que el objeto ha sido marcado como "desaparecido"
                    # justifica eliminar el objeto del seguimiento.
                    if self.desaparecidos[IDObjeto] > self.maxDesaparecidos:
                        self.eliminar_registro(IDObjeto)

            # De lo contrario, si el número de centroides de entrada es mayor que el número de centroides de objetos existentes,
            # necesitamos registrar cada nuevo centroide de entrada como un objeto rastreable.
            else:
                for columna in columnasNoUtilizadas:
                    self.registrar(centroidesEntrada[columna])

        # Devolver el conjunto de objetos rastreables.
        return self.objetos
