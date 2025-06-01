from multiprocessing import Process, Event, Value, current_process
import time
import random
import time
from typing import Any, List
import readProcesses

class EventProcess:
    def __init__(self, runEvent, dataRow):
        self.runEvent = runEvent
        self.dataRow = dataRow
        self.segundosTotaisAteFinalizacao = Value('d', 0.0)

    runEvent : Event # type: ignore
    process : Process
    dataRow : readProcesses.DataRow
    trocasContextoTotais = 0
    quantum = 2


def process(process : EventProcess, stopEvent : Event): # type: ignore
    tempoInicio = 0.0
    if not stopEvent.is_set():
        tempoInicio = time.time()
        print("Iniciando processo: " + current_process().name)

    i = 0
    while not stopEvent.is_set():
        while process.runEvent.is_set():
            # Bloqueio I/O
            if i >= process.dataRow.execucao and process.dataRow.hasBloqueio:
                process.dataRow.hasBloqueio = False
                process.runEvent.clear()
                time.sleep(process.dataRow.espera)
                break

            if i >= process.dataRow.execucao + process.dataRow.execucao2:
                print("Processo: " + current_process().name + " completo.")
                process.segundosTotaisAteFinalizacao.value = time.time() - tempoInicio
                return
            i += 1
            time.sleep(1)
        time.sleep(1)

def finish():
    threadStopEvent.set()
    stopEvent.set()

    completeProcesses.sort(key=lambda eventprocess: eventprocess.dataRow.id)
    data : List[List[Any]] = [["id", "segundos totais", "tempo executando", "tempo de espera", "trocas de contexto"]]
    for process in completeProcesses:
        tempoExecutando = process.dataRow.execucao + process.dataRow.execucao2
        data.append([
            process.dataRow.id,
            process.segundosTotaisAteFinalizacao.value,
            tempoExecutando,
            process.segundosTotaisAteFinalizacao.value - tempoExecutando,
            process.trocasContextoTotais
        ])
    
    for row in data:
        print("{:<5} {:<20} {:<20} {:<20}".format(*row))

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
    for processRunner in processRunners:
        processRunner.join()
    exit()

if __name__ == '__main__':
    beginTime = time.time()
    from multiprocessing import set_start_method
    set_start_method('spawn')

    stopEvent = Event()

    completeProcesses : List[EventProcess] = []

    cpuCore1Process : List[EventProcess] = []
    cpuCore2Process : List[EventProcess] = []
    cpuCore3Process : List[EventProcess] = []
    cpuCore4Process : List[EventProcess] = []

    processes : List[EventProcess] = []
    dataRows = readProcesses.read_file_to_objects("processes.txt")
    for data in dataRows:
        newProcess = EventProcess(Event(), data)
        newProcess.process = Process(target=process, args=(newProcess, stopEvent))
        processes.append(newProcess)
    
    import threading
    def processBuild(threadStopEvent : threading.Event, processes : List[EventProcess]):
        while not threadStopEvent.is_set():
            leastTime = 0
            if len(processes) == 0:
                return
            nowTime = time.time() - beginTime
            for process in processes:
                if process.dataRow.tempoChegada < nowTime:
                    if len(cpuCore1Process) == len(cpuCore2Process):
                        cpuCore1Process.append(process)
                    elif len(cpuCore2Process) == len(cpuCore3Process):
                        cpuCore2Process.append(process)
                    elif len(cpuCore3Process) == len(cpuCore4Process):
                        cpuCore3Process.append(process)
                    else:
                        cpuCore4Process.append(process)
                    process.process.start()
                elif process.dataRow.tempoChegada > leastTime:
                    leastTime = process.dataRow.tempoChegada - nowTime

            processes = [process for process in processes if process.dataRow.tempoChegada >= nowTime]
            time.sleep(leastTime)

    def processRunn(cpuProcesses : List[EventProcess], threadStopEvent : threading.Event, quantumOpcoes : str):
        def runCicle(processes : list[EventProcess]):
            if len(processes) != 0:
                if not processes[0].process.is_alive() and not (processes[0].process.exitcode is None):
                    processes[0].quantum -= 1
                    completeProcesses.append(processes[0])
                    processes.pop(0)
                    runCicle(processes)
                else:
                    if processes[0].runEvent.is_set():
                        processes[0].trocasContextoTotais += 1
                        processes[0].runEvent.clear()
                        process = processes[0]
                        processes.pop(0)
                        processes.append(process)
                    processes[0].runEvent.set()

        while not threadStopEvent.is_set(): 
            runCicle(cpuProcesses)

            if quantumOpcoes == 'f':
                time.sleep(2)
            else:
                time.sleep(cpuProcesses[0].quantum)

    threadStopEvent = threading.Event()

    print("Quantum fixo ou alternado? (f, a)")
    quantumOpcoes = ''
    while True:
        quantumOpcoes = input()
        if quantumOpcoes.lower() == 'f' or quantumOpcoes.lower() == 'a':
            break
        else:
            print("Opção inválida!")

    processBuilder = threading.Thread(target=processBuild, args=(threadStopEvent, processes))
    processBuilder.start()
    processRunners : List[threading.Thread] = [
        threading.Thread(target=processRunn, args=(cpuCore1Process, threadStopEvent, quantumOpcoes)),
        threading.Thread(target=processRunn, args=(cpuCore2Process, threadStopEvent, quantumOpcoes)),
        threading.Thread(target=processRunn, args=(cpuCore3Process, threadStopEvent, quantumOpcoes)),
        threading.Thread(target=processRunn, args=(cpuCore4Process, threadStopEvent, quantumOpcoes))
    ]
    for i in range(4):
        processRunners[i].start()

    try:
        while(processBuilder.is_alive() or len(cpuCore1Process) != 0 or len(cpuCore2Process) != 0 or len(cpuCore3Process) != 0 or len(cpuCore4Process) != 0):
            time.sleep(1)
    except KeyboardInterrupt:
        finish()

    finish()

    print("Finalizando...")
