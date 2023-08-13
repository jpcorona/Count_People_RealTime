class TrackableObject:
    def __init__(self, IDObjeto, centroide):
        # almacenar el ID de objeto y luego inicializar una lista de centroides
        # usando el centroide actual
        self.IDObjeto = IDObjeto
        self.centroides = [centroide]

        # inicializar un booleano utilizado para indicar si el objeto ya ha
        # sido contado o no
        self.contado = False
