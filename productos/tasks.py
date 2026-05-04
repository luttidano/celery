import time 

from celery import shared_task

@shared_task
def tarea_larga_duracion():
    print("Iniciando tarea de larga duración...")
    time.sleep(10)  # Simula una tarea que tarda 10 segundos
    print("Tarea de larga duración completada.")
    return "Resultado de la tarea"