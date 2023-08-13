import cv2
import threading
import queue

class ClaseHilos:
    # Iniciar la clase de hilos
    def __init__(self, nombre):
        self.cap = cv2.VideoCapture(nombre)
        # Definir una cola vacía y un hilo
        self.cola = queue.Queue()
        t = threading.Thread(target=self._lector)
        t.daemon = True
        t.start()

    # Leer los fotogramas tan pronto como estén disponibles
    # Este enfoque elimina el búfer interno de OpenCV y reduce el retardo de los fotogramas
    def _lector(self):
        while True:
            ret, frame = self.cap.read()  # Leer los fotogramas y ---
            if not ret:
                break
            if not self.cola.empty():
                try:
                    self.cola.get_nowait()
                except queue.Empty:
                    pass
            self.cola.put(frame)  # --- almacenarlos en una cola (en lugar del búfer)

    def leer(self):
        return self.cola.get()  # Obtener fotogramas de la cola uno por uno

    def liberar(self):
        return self.cap.release()  # Liberar el recurso de hardware
