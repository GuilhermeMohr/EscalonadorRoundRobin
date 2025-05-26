from multiprocessing import Process, Event, current_process
import time
import random
import datetime
import os

class EventProcess:
    def __init__(self, runEvent):
        self.runEvent = runEvent

    runEvent : Event
    process : Process


def process(runEvent : Event, stopEvent : Event):
    if not stopEvent.is_set():
        print("Iniciando processo: " + current_process().name)

    i = 0
    while not stopEvent.is_set():
        while runEvent.is_set():
            if i > 20:
                print("Processo: " + current_process().name + " completo.")
                return
            i += 1
            time.sleep(1)
        time.sleep(1)

if __name__ == '__main__':
    from multiprocessing import set_start_method
    set_start_method('spawn')

    cpuCore1Process = []
    cpuCore2Process = []
    cpuCore3Process = []
    cpuCore4Process = []

    stopEvent = Event()

    import threading
    def processBuild(threadStopEvent : threading.Event):
        while not threadStopEvent.is_set():
            
            newProcess = EventProcess(Event())
            newProcess.process = Process(target=process, args=(newProcess.runEvent, stopEvent))
            if len(cpuCore1Process) == len(cpuCore2Process):
                cpuCore1Process.append(newProcess)
            elif len(cpuCore2Process) == len(cpuCore3Process):
                cpuCore2Process.append(newProcess)
            elif len(cpuCore3Process) == len(cpuCore4Process):
                cpuCore3Process.append(newProcess)
            else:
                cpuCore4Process.append(newProcess)

            newProcess.process.start()

            time.sleep(random.randint(5,10))
    
    def processRunn(threadStopEvent : threading.Event, quantumOpcoes : str):
        def runCicle(processes : list):
            if len(processes) != 0:
                if processes[0].runEvent.is_set():
                    processes[0].runEvent.clear()
                    process = processes[0]
                    processes.remove(processes[0])
                    processes.append(process)
                processes[0].runEvent.set()

        while not threadStopEvent.is_set(): 
            runCicle(cpuCore1Process)
            runCicle(cpuCore2Process)
            runCicle(cpuCore3Process)
            runCicle(cpuCore4Process)

            if quantumOpcoes == 'f':
                time.sleep(2)
            else:
                time.sleep(random.randint(1,5))

    threadStopEvent = threading.Event()

    print("Quantum fixo ou alternado? (f, a)")
    quantumOpcoes = ''
    while True:
        quantumOpcoes = input()
        if quantumOpcoes.lower() == 'f' or quantumOpcoes.lower() == 'a':
            break
        else:
            print("Opção inválida!")

    print("Pressione enter no terminal para finalizar o programa.\n")

    processBuilder = threading.Thread(target=processBuild, args=(threadStopEvent,))
    processRunner = threading.Thread(target=processRunn, args=(threadStopEvent, quantumOpcoes))
    processBuilder.start()
    processRunner.start()

    input()
    print("Finalizando...")

    threadStopEvent.set()
    stopEvent.set()

    def endProcess(eventProcess):
        if not eventProcess.process.is_alive() and eventProcess.process.exitcode is None:
            eventProcess.process.start()
        else:
            eventProcess.runEvent.clear()
        eventProcess.process.join()

    for p in cpuCore1Process:
        endProcess(p)
    for p in cpuCore2Process:
        endProcess(p)
    for p in cpuCore3Process:
        endProcess(p)
    for p in cpuCore4Process:
        endProcess(p)

    processBuilder.join()
    processRunner.join()
    exit()