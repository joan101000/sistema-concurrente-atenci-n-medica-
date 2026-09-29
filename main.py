import os
import statistics
import time

from multiprocessing import (
    Process,
    Queue,
    freeze_support,
)

from procesamiento import (
    procesar_pacientes_secuencial
)

from paralelo import (
    ejecutar_paralelo
)


def trabajador_secuencial(
    cantidad,
    cola_resultados,
):
    try:
        pid = os.getpid()

        inicio = time.time_ns()

        resultado = (
            procesar_pacientes_secuencial(
                cantidad
            )
        )

        fin = time.time_ns()

        cola_resultados.put(
            {
                "tipo": "resultado",
                "pid": pid,
                "inicio": inicio,
                "fin": fin,
                "resultado": resultado,
            }
        )

    except Exception as error:
        cola_resultados.put(
            {
                "tipo": "error",
                "mensaje": str(error),
            }
        )


def ejecutar_secuencial_aislado(
    cantidad
):
    if cantidad <= 0:
        raise ValueError(
            "La cantidad de pacientes "
            "debe ser mayor que cero."
        )

    cola_resultados = Queue()

    proceso = Process(
        target=trabajador_secuencial,
        args=(
            cantidad,
            cola_resultados,
        ),
        name="Proceso-Secuencial",
    )

    inicio_total = (
        time.perf_counter()
    )

    proceso.start()

    mensaje = (
        cola_resultados.get()
    )

    proceso.join()

    fin_total = (
        time.perf_counter()
    )

    if proceso.exitcode != 0:
        raise RuntimeError(
            "El proceso secuencial "
            "terminó con error."
        )

    if mensaje["tipo"] == "error":
        raise RuntimeError(
            "Error en la ejecución "
            "secuencial: "
            + mensaje["mensaje"]
        )

    datos = {
        "modo":
            "secuencial",

        "pid":
            mensaje["pid"],

        "inicio":
            mensaje["inicio"],

        "fin":
            mensaje["fin"],

        "duracion_interna":
            (
                mensaje["fin"]
                - mensaje["inicio"]
            ) / 1_000_000_000,

        "tiempo":
            fin_total - inicio_total,

        "resultado":
            mensaje["resultado"],

        "muestras":
            mensaje["resultado"].get(
                "muestras",
                [],
            ),
    }

    cola_resultados.close()
    cola_resultados.join_thread()

    return datos


def validar_resultados(
    resultado_secuencial,
    resultado_paralelo,
):
    claves = [
        "cantidad",
        "alta",
        "media",
        "normal",
        "suma_ids",
        "control",
    ]

    return all(
        resultado_secuencial[clave]
        ==
        resultado_paralelo[clave]
        for clave in claves
    )


def ejecutar_prueba_secuencial(
    cantidad,
    repeticiones=1,
):
    if cantidad <= 0:
        raise ValueError(
            "La cantidad de pacientes "
            "debe ser mayor que cero."
        )

    if repeticiones <= 0:
        raise ValueError(
            "Las repeticiones deben "
            "ser mayores que cero."
        )

    tiempos = []

    ultima_ejecucion = None

    for _ in range(
        repeticiones
    ):
        ultima_ejecucion = (
            ejecutar_secuencial_aislado(
                cantidad
            )
        )

        tiempos.append(
            ultima_ejecucion["tiempo"]
        )

    return {
        "modo":
            "secuencial",

        "cantidad":
            cantidad,

        "repeticiones":
            repeticiones,

        "tiempos":
            tiempos,

        "tiempo_promedio":
            statistics.mean(
                tiempos
            ),

        "pid":
            ultima_ejecucion["pid"],

        "inicio":
            ultima_ejecucion["inicio"],

        "fin":
            ultima_ejecucion["fin"],

        "resultado":
            ultima_ejecucion["resultado"],

        "muestras":
            ultima_ejecucion["muestras"],
    }


def ejecutar_prueba_paralela(
    cantidad,
    numero_medicos,
    repeticiones=1,
):
    if cantidad <= 0:
        raise ValueError(
            "La cantidad de pacientes "
            "debe ser mayor que cero."
        )

    if numero_medicos <= 0:
        raise ValueError(
            "La cantidad de médicos "
            "debe ser mayor que cero."
        )

    if repeticiones <= 0:
        raise ValueError(
            "Las repeticiones deben "
            "ser mayores que cero."
        )

    numero_medicos = min(
        numero_medicos,
        cantidad,
    )

    tiempos = []

    ultimo_resultado = None

    for _ in range(
        repeticiones
    ):
        inicio = (
            time.perf_counter()
        )

        ultimo_resultado = (
            ejecutar_paralelo(
                cantidad,
                numero_medicos,
            )
        )

        tiempos.append(
            time.perf_counter()
            - inicio
        )

    return {
        "modo":
            "paralelo",

        "cantidad":
            cantidad,

        "medicos":
            numero_medicos,

        "repeticiones":
            repeticiones,

        "tiempos":
            tiempos,

        "tiempo_promedio":
            statistics.mean(
                tiempos
            ),

        "resultado":
            ultimo_resultado,

        "procesos":
            ultimo_resultado[
                "procesos"
            ],

        "pids":
            ultimo_resultado[
                "pids_distintos"
            ],

        "paralelismo_detectado":
            ultimo_resultado[
                "paralelismo_detectado"
            ],

        "superposiciones":
            ultimo_resultado[
                "superposiciones"
            ],

        "muestras":
            ultimo_resultado[
                "muestras"
            ],

        "productor":
            ultimo_resultado[
                "productor"
            ],
    }


def comparar_ejecuciones(
    cantidad,
    numero_medicos,
    repeticiones=3,
):
    if cantidad <= 0:
        raise ValueError(
            "La cantidad de pacientes "
            "debe ser mayor que cero."
        )

    if numero_medicos <= 0:
        raise ValueError(
            "La cantidad de médicos "
            "debe ser mayor que cero."
        )

    if repeticiones <= 0:
        raise ValueError(
            "Las repeticiones deben "
            "ser mayores que cero."
        )

    numero_medicos = min(
        numero_medicos,
        cantidad,
    )

    prueba_secuencial = (
        ejecutar_prueba_secuencial(
            cantidad,
            repeticiones,
        )
    )

    prueba_paralela = (
        ejecutar_prueba_paralela(
            cantidad,
            numero_medicos,
            repeticiones,
        )
    )

    correcto = (
        validar_resultados(
            prueba_secuencial[
                "resultado"
            ],
            prueba_paralela[
                "resultado"
            ],
        )
    )

    if not correcto:
        raise RuntimeError(
            "Los resultados secuencial "
            "y paralelo no coinciden."
        )

    tiempo_secuencial = (
        prueba_secuencial[
            "tiempo_promedio"
        ]
    )

    tiempo_paralelo = (
        prueba_paralela[
            "tiempo_promedio"
        ]
    )

    speedup = (
        tiempo_secuencial
        / tiempo_paralelo
    )

    eficiencia = (
        speedup
        / numero_medicos
    ) * 100

    mejora = (
        (
            tiempo_secuencial
            - tiempo_paralelo
        )
        / tiempo_secuencial
    ) * 100

    return {
        "cantidad":
            cantidad,

        "medicos":
            numero_medicos,

        "repeticiones":
            repeticiones,

        "secuencial":
            prueba_secuencial,

        "paralelo":
            prueba_paralela,

        "tiempo_secuencial":
            tiempo_secuencial,

        "tiempo_paralelo":
            tiempo_paralelo,

        "speedup":
            speedup,

        "eficiencia":
            eficiencia,

        "mejora":
            mejora,

        "correcto":
            correcto,
    }


def analizar_escalabilidad(
    cantidad,
    repeticiones=3,
    configuraciones=None,
):
    """
    Prueba diferentes cantidades de procesos
    contra una referencia secuencial.
    """
    if cantidad <= 0:
        raise ValueError(
            "La cantidad de pacientes "
            "debe ser mayor que cero."
        )

    if repeticiones <= 0:
        raise ValueError(
            "Las repeticiones deben "
            "ser mayores que cero."
        )

    cpu_disponibles = (
        os.cpu_count() or 1
    )

    if configuraciones is None:
        configuraciones = [
            1,
            2,
            4,
            6,
            8,
            12,
        ]

    configuraciones_validas = sorted(
        {
            min(
                int(procesos),
                cantidad,
            )
            for procesos in configuraciones
            if (
                int(procesos) > 0
                and
                int(procesos)
                <= cpu_disponibles
            )
        }
    )

    if not configuraciones_validas:
        configuraciones_validas = [
            1
        ]

    secuencial = (
        ejecutar_prueba_secuencial(
            cantidad,
            repeticiones,
        )
    )

    tiempo_secuencial = (
        secuencial[
            "tiempo_promedio"
        ]
    )

    filas = []

    for procesos in (
        configuraciones_validas
    ):
        paralelo = (
            ejecutar_prueba_paralela(
                cantidad,
                procesos,
                repeticiones,
            )
        )

        correcto = (
            validar_resultados(
                secuencial[
                    "resultado"
                ],
                paralelo[
                    "resultado"
                ],
            )
        )

        if not correcto:
            raise RuntimeError(
                f"La configuración de "
                f"{procesos} proceso(s) "
                f"no coincide con el "
                f"resultado secuencial."
            )

        tiempo_paralelo = (
            paralelo[
                "tiempo_promedio"
            ]
        )

        speedup = (
            tiempo_secuencial
            / tiempo_paralelo
        )

        eficiencia = (
            speedup
            / procesos
        ) * 100

        mejora = (
            (
                tiempo_secuencial
                - tiempo_paralelo
            )
            / tiempo_secuencial
        ) * 100

        filas.append(
            {
                "procesos":
                    procesos,

                "tiempo":
                    tiempo_paralelo,

                "speedup":
                    speedup,

                "eficiencia":
                    eficiencia,

                "mejora":
                    mejora,

                "correcto":
                    correcto,

                "paralelismo_detectado":
                    paralelo[
                        "paralelismo_detectado"
                    ],

                "pids":
                    paralelo["pids"],
            }
        )

    mejor = min(
        filas,
        key=lambda fila:
        fila["tiempo"],
    )

    return {
        "cantidad":
            cantidad,

        "repeticiones":
            repeticiones,

        "cpu_disponibles":
            cpu_disponibles,

        "secuencial":
            secuencial,

        "tiempo_secuencial":
            tiempo_secuencial,

        "configuraciones":
            configuraciones_validas,

        "resultados":
            filas,

        "mejor":
            mejor,
    }


def pedir_entero(
    mensaje,
    valor_defecto,
):
    texto = input(
        f"{mensaje} "
        f"[{valor_defecto}]: "
    ).strip()

    if not texto:
        return valor_defecto

    valor = int(texto)

    if valor <= 0:
        raise ValueError(
            "El valor debe ser "
            "mayor que cero."
        )

    return valor


def main():
    print()

    print(
        "SISTEMA CONCURRENTE "
        "DE ATENCIÓN MÉDICA"
    )

    print(
        f"Procesadores lógicos disponibles: "
        f"{os.cpu_count() or 1}"
    )

    while True:
        print()
        print(
            "1. Ejecutar SECUENCIAL"
        )

        print(
            "2. Ejecutar PARALELO"
        )

        print(
            "3. COMPARAR ambos"
        )

        print(
            "4. ANALIZAR ESCALABILIDAD"
        )

        print(
            "5. Salir"
        )

        opcion = input(
            "Seleccione una opción: "
        ).strip()

        try:
            if opcion == "1":
                cantidad = pedir_entero(
                    "Pacientes a simular",
                    1000,
                )

                repeticiones = pedir_entero(
                    "Repeticiones",
                    1,
                )

                datos = (
                    ejecutar_prueba_secuencial(
                        cantidad,
                        repeticiones,
                    )
                )

                print(
                    f"Tiempo promedio: "
                    f"{datos['tiempo_promedio']:.4f} s"
                )

            elif opcion == "2":
                cantidad = pedir_entero(
                    "Pacientes a simular",
                    1000,
                )

                medicos = pedir_entero(
                    "Médicos / procesos",
                    min(
                        4,
                        os.cpu_count() or 1,
                    ),
                )

                repeticiones = pedir_entero(
                    "Repeticiones",
                    1,
                )

                datos = (
                    ejecutar_prueba_paralela(
                        cantidad,
                        medicos,
                        repeticiones,
                    )
                )

                print(
                    f"Tiempo promedio: "
                    f"{datos['tiempo_promedio']:.4f} s"
                )

                print(
                    f"PIDs: "
                    f"{datos['pids']}"
                )

            elif opcion == "3":
                cantidad = pedir_entero(
                    "Pacientes a simular",
                    1000,
                )

                medicos = pedir_entero(
                    "Médicos / procesos",
                    min(
                        4,
                        os.cpu_count() or 1,
                    ),
                )

                repeticiones = pedir_entero(
                    "Repeticiones",
                    3,
                )

                datos = (
                    comparar_ejecuciones(
                        cantidad,
                        medicos,
                        repeticiones,
                    )
                )

                print(
                    f"Secuencial: "
                    f"{datos['tiempo_secuencial']:.4f} s"
                )

                print(
                    f"Paralelo: "
                    f"{datos['tiempo_paralelo']:.4f} s"
                )

                print(
                    f"Speedup: "
                    f"{datos['speedup']:.2f}x"
                )

                print(
                    f"Eficiencia: "
                    f"{datos['eficiencia']:.2f}%"
                )

                print(
                    f"Mejora: "
                    f"{datos['mejora']:.2f}%"
                )

            elif opcion == "4":
                cantidad = pedir_entero(
                    "Pacientes a simular",
                    1000,
                )

                repeticiones = pedir_entero(
                    "Repeticiones",
                    3,
                )

                datos = (
                    analizar_escalabilidad(
                        cantidad,
                        repeticiones,
                    )
                )

                print(
                    f"Referencia secuencial: "
                    f"{datos['tiempo_secuencial']:.4f} s"
                )

                for fila in (
                    datos["resultados"]
                ):
                    print(
                        f"{fila['procesos']:>2} proc | "
                        f"{fila['tiempo']:.4f} s | "
                        f"speedup "
                        f"{fila['speedup']:.2f}x | "
                        f"eficiencia "
                        f"{fila['eficiencia']:.2f}% | "
                        f"mejora "
                        f"{fila['mejora']:.2f}%"
                    )

            elif opcion == "5":
                break

            else:
                print(
                    "Seleccione una opción "
                    "entre 1 y 5."
                )

        except (
            ValueError,
            RuntimeError,
        ) as error:
            print(
                f"Error: {error}"
            )


if __name__ == "__main__":
    freeze_support()
    main()