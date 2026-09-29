PRIORIDAD_ALTA = 1
PRIORIDAD_MEDIA = 2
PRIORIDAD_NORMAL = 3

NOMBRES_PRIORIDAD = {
    PRIORIDAD_ALTA: "Alta",
    PRIORIDAD_MEDIA: "Media",
    PRIORIDAD_NORMAL: "Normal",
}


def obtener_prioridad(id_paciente):
    """Asigna una prioridad simulada y reproducible a cada paciente."""
    marca = (id_paciente * 37 + 11) % 100

    if marca < 15:
        return PRIORIDAD_ALTA

    if marca < 45:
        return PRIORIDAD_MEDIA

    return PRIORIDAD_NORMAL


def generar_solicitudes(cantidad):
    """Genera solicitudes respetando el orden de llegada."""
    if cantidad <= 0:
        raise ValueError(
            "La cantidad de pacientes debe ser mayor que cero."
        )

    return [
        {
            "paciente": id_paciente,
            "turno_llegada": id_paciente,
            "prioridad": obtener_prioridad(id_paciente),
        }
        for id_paciente in range(1, cantidad + 1)
    ]


def ordenar_solicitudes_por_prioridad(cantidad):
    """
    Ordena Alta, Media y Normal.
    Mantiene FIFO dentro de cada prioridad.
    """
    solicitudes = generar_solicitudes(cantidad)

    grupos = {
        PRIORIDAD_ALTA: [],
        PRIORIDAD_MEDIA: [],
        PRIORIDAD_NORMAL: [],
    }

    for solicitud in solicitudes:
        grupos[solicitud["prioridad"]].append(solicitud)

    ordenadas = []

    for prioridad in (
        PRIORIDAD_ALTA,
        PRIORIDAD_MEDIA,
        PRIORIDAD_NORMAL,
    ):
        ordenadas.extend(grupos[prioridad])

    return ordenadas


def carga_validacion_medica(id_paciente, prioridad):
    """
    Simula carga de CPU para comparar
    ejecución secuencial y paralela.
    """
    iteraciones = 5500 + ((4 - prioridad) * 250)

    valor = (
        id_paciente * 97
        + prioridad * 31
    ) & 0xFFFFFFFF

    for i in range(1, iteraciones + 1):
        valor = (
            valor * 1664525
            + 1013904223
            + ((id_paciente + i) ^ (prioridad * 131))
        ) & 0xFFFFFFFF

        valor ^= valor >> 13

    return valor


def resultado_vacio():
    return {
        "cantidad": 0,
        "alta": 0,
        "media": 0,
        "normal": 0,
        "suma_ids": 0,
        "control": 0,
    }


def acumular_paciente(
    resultado,
    id_paciente,
    prioridad,
    control,
):
    resultado["cantidad"] += 1
    resultado["suma_ids"] += id_paciente

    resultado["control"] = (
        resultado["control"] + control
    ) & 0xFFFFFFFFFFFFFFFF

    if prioridad == PRIORIDAD_ALTA:
        resultado["alta"] += 1

    elif prioridad == PRIORIDAD_MEDIA:
        resultado["media"] += 1

    else:
        resultado["normal"] += 1


def procesar_pacientes_secuencial(
    cantidad,
    limite_muestras=25,
):
    """Procesa todos los pacientes en un único flujo."""
    solicitudes = ordenar_solicitudes_por_prioridad(
        cantidad
    )

    resultado = resultado_vacio()
    muestras = []

    for posicion, solicitud in enumerate(
        solicitudes,
        start=1,
    ):
        id_paciente = solicitud["paciente"]
        prioridad = solicitud["prioridad"]

        control = carga_validacion_medica(
            id_paciente,
            prioridad,
        )

        acumular_paciente(
            resultado,
            id_paciente,
            prioridad,
            control,
        )

        if len(muestras) < limite_muestras:
            muestras.append(
                {
                    "orden_atencion": posicion,
                    "paciente": id_paciente,
                    "turno_llegada":
                        solicitud["turno_llegada"],
                    "prioridad": prioridad,
                    "nombre_prioridad":
                        NOMBRES_PRIORIDAD[prioridad],
                }
            )

    resultado["muestras"] = muestras

    return resultado