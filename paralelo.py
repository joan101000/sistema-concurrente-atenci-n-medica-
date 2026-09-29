import os
import time

from multiprocessing import (
    Process,
    Queue,
    JoinableQueue,
    Value,
    Lock,
)

from procesamiento import (
    PRIORIDAD_ALTA,
    PRIORIDAD_MEDIA,
    PRIORIDAD_NORMAL,
    NOMBRES_PRIORIDAD,
    ordenar_solicitudes_por_prioridad,
    carga_validacion_medica,
    resultado_vacio,
    acumular_paciente,
)


def productor(
    cantidad,
    cola_tareas,
    numero_consumidores,
    cola_productor,
):
    """
    Representa la recepción.

    Genera y deposita las solicitudes
    en la sala de espera.
    """
    try:
        solicitudes = ordenar_solicitudes_por_prioridad(
            cantidad
        )

        conteo = {
            PRIORIDAD_ALTA: 0,
            PRIORIDAD_MEDIA: 0,
            PRIORIDAD_NORMAL: 0,
        }

        for numero_solicitud, solicitud in enumerate(
            solicitudes,
            start=1,
        ):
            prioridad = solicitud["prioridad"]

            conteo[prioridad] += 1

            cola_tareas.put(
                {
                    "numero_solicitud":
                        numero_solicitud,
                    "paciente":
                        solicitud["paciente"],
                    "turno_llegada":
                        solicitud["turno_llegada"],
                    "prioridad":
                        prioridad,
                }
            )

        cola_productor.put(
            {
                "tipo": "resultado",
                "pid": os.getpid(),
                "generados": cantidad,
                "alta":
                    conteo[PRIORIDAD_ALTA],
                "media":
                    conteo[PRIORIDAD_MEDIA],
                "normal":
                    conteo[PRIORIDAD_NORMAL],
            }
        )

    except Exception as error:
        cola_productor.put(
            {
                "tipo": "error",
                "mensaje": str(error),
            }
        )

    finally:
        for _ in range(numero_consumidores):
            cola_tareas.put(None)


def consumidor(
    identificador,
    cola_tareas,
    cola_resultados,
    progreso,
    lock_progreso,
):
    """
    Representa un médico consumidor.
    """
    pid = os.getpid()

    resultado_local = resultado_vacio()

    muestras = []

    inicio_proceso = None
    fin_proceso = None

    error_detectado = None

    progreso_pendiente = 0

    while True:
        tarea = cola_tareas.get()

        try:
            if tarea is None:
                break

            id_paciente = tarea["paciente"]
            prioridad = tarea["prioridad"]

            inicio_atencion = time.time_ns()

            if inicio_proceso is None:
                inicio_proceso = inicio_atencion

            try:
                control = carga_validacion_medica(
                    id_paciente,
                    prioridad,
                )

                acumular_paciente(
                    resultado_local,
                    id_paciente,
                    prioridad,
                    control,
                )

                fin_atencion = time.time_ns()
                fin_proceso = fin_atencion

                if len(muestras) < 15:
                    muestras.append(
                        {
                            "solicitud":
                                tarea["numero_solicitud"],
                            "paciente":
                                id_paciente,
                            "turno_llegada":
                                tarea["turno_llegada"],
                            "prioridad":
                                prioridad,
                            "nombre_prioridad":
                                NOMBRES_PRIORIDAD[
                                    prioridad
                                ],
                            "inicio":
                                inicio_atencion,
                            "fin":
                                fin_atencion,
                        }
                    )

                progreso_pendiente += 1

                if progreso_pendiente >= 20:
                    with lock_progreso:
                        progreso.value += (
                            progreso_pendiente
                        )

                    progreso_pendiente = 0

            except Exception as error:
                error_detectado = str(error)

        finally:
            cola_tareas.task_done()

    if progreso_pendiente:
        with lock_progreso:
            progreso.value += progreso_pendiente

    if inicio_proceso is None:
        instante = time.time_ns()

        inicio_proceso = instante
        fin_proceso = instante

    cola_resultados.put(
        {
            "tipo":
                "error"
                if error_detectado
                else "resultado",

            "medico":
                identificador,

            "pid":
                pid,

            "cantidad":
                resultado_local["cantidad"],

            "alta":
                resultado_local["alta"],

            "media":
                resultado_local["media"],

            "normal":
                resultado_local["normal"],

            "suma_ids":
                resultado_local["suma_ids"],

            "control":
                resultado_local["control"],

            "inicio":
                inicio_proceso,

            "fin":
                fin_proceso,

            "muestras":
                muestras,

            "mensaje":
                error_detectado,
        }
    )


def combinar_resultados(resultados):
    resultado_final = resultado_vacio()

    for resultado in resultados:
        resultado_final["cantidad"] += (
            resultado["cantidad"]
        )

        resultado_final["alta"] += (
            resultado["alta"]
        )

        resultado_final["media"] += (
            resultado["media"]
        )

        resultado_final["normal"] += (
            resultado["normal"]
        )

        resultado_final["suma_ids"] += (
            resultado["suma_ids"]
        )

        resultado_final["control"] = (
            resultado_final["control"]
            + resultado["control"]
        ) & 0xFFFFFFFFFFFFFFFF

    return resultado_final


def resumir_consumidores(resultados):
    procesos = []

    for resultado in resultados:
        duracion = (
            resultado["fin"]
            - resultado["inicio"]
        ) / 1_000_000_000

        procesos.append(
            {
                "medico":
                    resultado["medico"],

                "pid":
                    resultado["pid"],

                "cantidad":
                    resultado["cantidad"],

                "alta":
                    resultado["alta"],

                "media":
                    resultado["media"],

                "normal":
                    resultado["normal"],

                "inicio":
                    resultado["inicio"],

                "fin":
                    resultado["fin"],

                "duracion":
                    duracion,

                "muestras":
                    resultado["muestras"],
            }
        )

    procesos.sort(
        key=lambda proceso:
        proceso["medico"]
    )

    return procesos


def detectar_superposiciones(procesos):
    superposiciones = []

    for indice_a in range(
        len(procesos)
    ):
        proceso_a = procesos[indice_a]

        if proceso_a["cantidad"] == 0:
            continue

        for indice_b in range(
            indice_a + 1,
            len(procesos),
        ):
            proceso_b = procesos[indice_b]

            if proceso_b["cantidad"] == 0:
                continue

            inicio_comun = max(
                proceso_a["inicio"],
                proceso_b["inicio"],
            )

            fin_comun = min(
                proceso_a["fin"],
                proceso_b["fin"],
            )

            if inicio_comun < fin_comun:
                superposiciones.append(
                    {
                        "medico_1":
                            proceso_a["medico"],

                        "pid_1":
                            proceso_a["pid"],

                        "medico_2":
                            proceso_b["medico"],

                        "pid_2":
                            proceso_b["pid"],

                        "duracion_ms":
                            (
                                fin_comun
                                - inicio_comun
                            ) / 1_000_000,
                    }
                )

    return superposiciones


def obtener_muestras_globales(
    procesos,
    limite=30,
):
    muestras = []

    for proceso in procesos:
        for muestra in proceso["muestras"]:
            datos = dict(muestra)

            datos["medico"] = (
                proceso["medico"]
            )

            datos["pid"] = (
                proceso["pid"]
            )

            muestras.append(datos)

    muestras.sort(
        key=lambda muestra:
        muestra["inicio"]
    )

    return muestras[:limite]


def ejecutar_paralelo(
    cantidad,
    numero_procesos,
):
    if cantidad <= 0:
        raise ValueError(
            "La cantidad de pacientes "
            "debe ser mayor que cero."
        )

    if numero_procesos <= 0:
        raise ValueError(
            "La cantidad de médicos "
            "debe ser mayor que cero."
        )

    numero_consumidores = min(
        numero_procesos,
        cantidad,
    )

    cola_tareas = JoinableQueue(
        maxsize=max(
            40,
            numero_consumidores * 20,
        )
    )

    cola_resultados = Queue()
    cola_productor = Queue()

    progreso = Value(
        "q",
        0,
        lock=False,
    )

    lock_progreso = Lock()

    consumidores = []

    for identificador in range(
        1,
        numero_consumidores + 1,
    ):
        proceso = Process(
            target=consumidor,
            args=(
                identificador,
                cola_tareas,
                cola_resultados,
                progreso,
                lock_progreso,
            ),
            name=f"Medico-{identificador}",
        )

        consumidores.append(
            proceso
        )

        proceso.start()

    proceso_productor = Process(
        target=productor,
        args=(
            cantidad,
            cola_tareas,
            numero_consumidores,
            cola_productor,
        ),
        name="Recepcion-Productor",
    )

    proceso_productor.start()
    proceso_productor.join()

    if proceso_productor.exitcode != 0:
        raise RuntimeError(
            "El proceso de recepción "
            "terminó con error."
        )

    informacion_productor = (
        cola_productor.get()
    )

    if informacion_productor["tipo"] == "error":
        raise RuntimeError(
            "Error en recepción: "
            + informacion_productor["mensaje"]
        )

    cola_tareas.join()

    resultados = []
    errores = []

    for _ in range(
        numero_consumidores
    ):
        mensaje = (
            cola_resultados.get()
        )

        resultados.append(
            mensaje
        )

        if mensaje["tipo"] == "error":
            errores.append(
                mensaje
            )

    for proceso in consumidores:
        proceso.join()

    for proceso in consumidores:
        if proceso.exitcode != 0:
            raise RuntimeError(
                f"{proceso.name} terminó "
                f"con código "
                f"{proceso.exitcode}."
            )

    if errores:
        primer_error = errores[0]

        raise RuntimeError(
            f"Se produjo un error en "
            f"el médico "
            f"{primer_error['medico']}: "
            f"{primer_error['mensaje']}"
        )

    resultados.sort(
        key=lambda resultado:
        resultado["medico"]
    )

    resultado_final = (
        combinar_resultados(
            resultados
        )
    )

    procesos = (
        resumir_consumidores(
            resultados
        )
    )

    superposiciones = (
        detectar_superposiciones(
            procesos
        )
    )

    pids_distintos = sorted(
        {
            proceso["pid"]
            for proceso in procesos
        }
    )

    resultado_final.update(
        {
            "progreso":
                progreso.value,

            "consumidores":
                numero_consumidores,

            "procesos":
                procesos,

            "pids":
                [
                    proceso["pid"]
                    for proceso in procesos
                ],

            "pids_distintos":
                pids_distintos,

            "superposiciones":
                superposiciones,

            "paralelismo_detectado":
                (
                    len(pids_distintos) > 1
                    and bool(
                        superposiciones
                    )
                ),

            "muestras":
                obtener_muestras_globales(
                    procesos
                ),

            "productor":
                informacion_productor,

            "orden_prioridades":
                [
                    "Alta",
                    "Media",
                    "Normal",
                ],
        }
    )

    cola_tareas.close()
    cola_tareas.join_thread()

    cola_resultados.close()
    cola_resultados.join_thread()

    cola_productor.close()
    cola_productor.join_thread()

    return resultado_final