import os
import threading
import customtkinter as ctk

from multiprocessing import freeze_support
from queue import Queue as ThreadQueue, Empty
from tkinter import messagebox

from main import (
    ejecutar_prueba_secuencial,
    ejecutar_prueba_paralela,
    comparar_ejecuciones,
    analizar_escalabilidad,
)

from procesamiento import (
    ordenar_solicitudes_por_prioridad,
    NOMBRES_PRIORIDAD,
)


ctk.set_appearance_mode("dark")


FONDO = "#0F172A"
PANEL = "#111827"
PANEL_2 = "#1E293B"
PANEL_3 = "#0B1220"
BORDE = "#334155"

TEXTO = "#F8FAFC"
TEXTO_SECUNDARIO = "#94A3B8"

AZUL = "#2563EB"
AZUL_HOVER = "#1D4ED8"
AZUL_CLARO = "#60A5FA"
AZUL_FONDO = "#172554"

VERDE = "#16A34A"
VERDE_HOVER = "#15803D"
VERDE_CLARO = "#4ADE80"
VERDE_OSCURO = "#14532D"

TURQUESA = "#0D9488"
TURQUESA_HOVER = "#0F766E"
TURQUESA_CLARO = "#2DD4BF"

MORADO = "#7C3AED"
MORADO_CLARO = "#A78BFA"

NARANJA_CLARO = "#FB923C"

ROJO_CLARO = "#FCA5A5"
ROJO_FONDO = "#7F1D1D"

GRIS = "#475569"
GRIS_HOVER = "#334155"

AMARILLO_TEXTO = "#FCD34D"


class InterfazAtencionMedica(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(
            "Sistema Concurrente de Atención Médica"
        )

        self.geometry(
            "1280x860"
        )

        self.minsize(
            1100,
            740,
        )

        self.configure(
            fg_color=FONDO
        )

        self.cpu_disponibles = (
            os.cpu_count() or 1
        )

        self.cola_interfaz = ThreadQueue()

        self.ejecutando = False

        self.crear_interfaz()

        self.after(
            100,
            self.revisar_cola_interfaz,
        )

    def crear_interfaz(self):
        self.crear_encabezado()
        self.crear_configuracion()
        self.crear_botones()
        self.crear_estado()
        self.crear_tarjetas_principales()
        self.crear_pestanas()

    def crear_encabezado(self):
        encabezado = ctk.CTkFrame(
            self,
            fg_color=AZUL_FONDO,
            corner_radius=20,
            border_width=1,
            border_color=AZUL,
        )

        encabezado.pack(
            fill="x",
            padx=22,
            pady=(10, 6),
        )

        encabezado.grid_columnconfigure(
            0,
            weight=1,
        )

        bloque_titulo = ctk.CTkFrame(
            encabezado,
            fg_color="transparent",
        )

        bloque_titulo.grid(
            row=0,
            column=0,
            padx=22,
            pady=10,
            sticky="w",
        )

        ctk.CTkLabel(
            bloque_titulo,
            text=(
                "SISTEMA CONCURRENTE "
                "DE ATENCIÓN MÉDICA"
            ),
            font=(
                "Segoe UI",
                22,
                "bold",
            ),
            text_color=TEXTO,
        ).pack(
            anchor="w"
        )

        ctk.CTkLabel(
            bloque_titulo,
            text=(
                "Asignación de pacientes, "
                "sala de espera, prioridades "
                "y procesamiento paralelo"
            ),
            font=(
                "Segoe UI",
                13,
            ),
            text_color="#BFDBFE",
        ).pack(
            anchor="w",
            pady=(5, 0),
        )

        bloque_cpu = ctk.CTkFrame(
            encabezado,
            fg_color="#1E3A8A",
            corner_radius=14,
        )

        bloque_cpu.grid(
            row=0,
            column=1,
            padx=22,
            pady=9,
        )

        ctk.CTkLabel(
            bloque_cpu,
            text="PROCESADORES LÓGICOS",
            font=(
                "Segoe UI",
                10,
                "bold",
            ),
            text_color="#BFDBFE",
        ).pack(
            padx=18,
            pady=(8, 0),
        )

        ctk.CTkLabel(
            bloque_cpu,
            text=str(
                self.cpu_disponibles
            ),
            font=(
                "Segoe UI",
                23,
                "bold",
            ),
            text_color=TEXTO,
        ).pack(
            padx=18,
            pady=(0, 8),
        )

    def crear_configuracion(self):
        configuracion = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=18,
            border_width=1,
            border_color=BORDE,
        )

        configuracion.pack(
            fill="x",
            padx=22,
            pady=5,
        )

        ctk.CTkLabel(
            configuracion,
            text="CONFIGURACIÓN DE LA PRUEBA",
            font=(
                "Segoe UI",
                16,
                "bold",
            ),
            text_color=AZUL_CLARO,
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            pady=(9, 10),
        )

        ctk.CTkLabel(
            configuracion,
            text="Cantidad de pacientes",
            text_color=TEXTO_SECUNDARIO,
        ).grid(
            row=1,
            column=0,
            pady=(0, 5),
        )

        self.entry_cantidad = ctk.CTkEntry(
            configuracion,
            width=225,
            height=34,
            justify="center",
            fg_color=PANEL_2,
            border_color=AZUL,
            text_color=TEXTO,
        )

        self.entry_cantidad.insert(
            0,
            "1000",
        )

        self.entry_cantidad.grid(
            row=2,
            column=0,
            padx=20,
            pady=(0, 10),
        )

        ctk.CTkLabel(
            configuracion,
            text="Médicos / procesos",
            text_color=TEXTO_SECUNDARIO,
        ).grid(
            row=1,
            column=1,
            pady=(0, 5),
        )

        opciones_medicos = [
            str(numero)
            for numero in range(
                1,
                self.cpu_disponibles + 1,
            )
        ]

        self.combo_medicos = ctk.CTkComboBox(
            configuracion,
            values=opciones_medicos,
            width=225,
            height=34,
            state="readonly",
            fg_color=PANEL_2,
            border_color=TURQUESA,
            button_color=TURQUESA,
            button_hover_color=TURQUESA_HOVER,
            text_color=TEXTO,
        )

        self.combo_medicos.set(
            "4"
            if self.cpu_disponibles >= 4
            else str(
                self.cpu_disponibles
            )
        )

        self.combo_medicos.grid(
            row=2,
            column=1,
            padx=20,
            pady=(0, 10),
        )

        ctk.CTkLabel(
            configuracion,
            text="Repeticiones",
            text_color=TEXTO_SECUNDARIO,
        ).grid(
            row=1,
            column=2,
            pady=(0, 5),
        )

        self.combo_repeticiones = ctk.CTkComboBox(
            configuracion,
            values=[
                "1",
                "2",
                "3",
                "5",
                "10",
            ],
            width=225,
            height=34,
            state="readonly",
            fg_color=PANEL_2,
            border_color=MORADO,
            button_color=MORADO,
            button_hover_color="#6D28D9",
            text_color=TEXTO,
        )

        self.combo_repeticiones.set(
            "3"
        )

        self.combo_repeticiones.grid(
            row=2,
            column=2,
            padx=20,
            pady=(0, 10),
        )

        for columna in range(3):
            configuracion.grid_columnconfigure(
                columna,
                weight=1,
            )

    def crear_botones(self):
        frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        frame.pack(
            pady=(5, 2)
        )

        self.boton_secuencial = ctk.CTkButton(
            frame,
            text="EJECUTAR SECUENCIAL",
            width=190,
            height=38,
            corner_radius=11,
            font=(
                "Segoe UI",
                12,
                "bold",
            ),
            fg_color=AZUL,
            hover_color=AZUL_HOVER,
            command=self.iniciar_secuencial,
        )

        self.boton_secuencial.grid(
            row=0,
            column=0,
            padx=5,
        )

        self.boton_paralelo = ctk.CTkButton(
            frame,
            text="EJECUTAR PARALELO",
            width=190,
            height=38,
            corner_radius=11,
            font=(
                "Segoe UI",
                12,
                "bold",
            ),
            fg_color=TURQUESA,
            hover_color=TURQUESA_HOVER,
            command=self.iniciar_paralelo,
        )

        self.boton_paralelo.grid(
            row=0,
            column=1,
            padx=5,
        )

        self.boton_comparar = ctk.CTkButton(
            frame,
            text="COMPARAR AMBOS",
            width=180,
            height=38,
            corner_radius=11,
            font=(
                "Segoe UI",
                12,
                "bold",
            ),
            fg_color=VERDE,
            hover_color=VERDE_HOVER,
            command=self.iniciar_comparacion,
        )

        self.boton_comparar.grid(
            row=0,
            column=2,
            padx=5,
        )

        self.boton_escalabilidad = ctk.CTkButton(
            frame,
            text="ANALIZAR ESCALABILIDAD",
            width=210,
            height=38,
            corner_radius=11,
            font=(
                "Segoe UI",
                12,
                "bold",
            ),
            fg_color=MORADO,
            hover_color="#6D28D9",
            command=self.iniciar_escalabilidad,
        )

        self.boton_escalabilidad.grid(
            row=0,
            column=3,
            padx=5,
        )

        self.boton_limpiar = ctk.CTkButton(
            frame,
            text="LIMPIAR",
            width=110,
            height=38,
            corner_radius=11,
            font=(
                "Segoe UI",
                12,
                "bold",
            ),
            fg_color=GRIS,
            hover_color=GRIS_HOVER,
            command=self.limpiar,
        )

        self.boton_limpiar.grid(
            row=0,
            column=4,
            padx=5,
        )

    def crear_estado(self):
        self.frame_estado = ctk.CTkFrame(
            self,
            fg_color=AZUL_FONDO,
            corner_radius=18,
        )

        self.frame_estado.pack(
            pady=(5, 4)
        )

        self.label_estado = ctk.CTkLabel(
            self.frame_estado,
            text="●  Listo para iniciar",
            font=(
                "Segoe UI",
                12,
                "bold",
            ),
            text_color=AZUL_CLARO,
        )

        self.label_estado.pack(
            padx=18,
            pady=4,
        )

        frame_progreso = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        frame_progreso.pack(
            pady=(0, 6)
        )

        self.barra_progreso = ctk.CTkProgressBar(
            frame_progreso,
            width=540,
            height=12,
            corner_radius=10,
            fg_color=BORDE,
            progress_color=AZUL,
        )

        self.barra_progreso.set(
            0
        )

        self.barra_progreso.grid(
            row=0,
            column=0,
            padx=(0, 12),
        )

        self.label_porcentaje = ctk.CTkLabel(
            frame_progreso,
            text="0%",
            width=45,
            font=(
                "Segoe UI",
                12,
                "bold",
            ),
            text_color=AZUL_CLARO,
        )

        self.label_porcentaje.grid(
            row=0,
            column=1,
        )

    def crear_tarjetas_principales(self):
        frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        frame.pack(
            fill="x",
            padx=22,
            pady=2,
        )

        self.tarjeta_pacientes = self.crear_tarjeta(
            frame,
            "PACIENTES ATENDIDOS",
            "0",
            VERDE_CLARO,
        )

        self.tarjeta_prioridad = self.crear_tarjeta(
            frame,
            "PRIORIDAD ALTA",
            "0",
            TURQUESA_CLARO,
        )

        self.tarjeta_speedup = self.crear_tarjeta(
            frame,
            "SPEEDUP",
            "0.00x",
            MORADO_CLARO,
        )

        self.tarjeta_eficiencia = self.crear_tarjeta(
            frame,
            "EFICIENCIA",
            "0.00%",
            NARANJA_CLARO,
        )

        tarjetas = (
            self.tarjeta_pacientes,
            self.tarjeta_prioridad,
            self.tarjeta_speedup,
            self.tarjeta_eficiencia,
        )

        for indice, tarjeta in enumerate(
            tarjetas
        ):
            tarjeta.grid(
                row=0,
                column=indice,
                padx=5,
                sticky="ew",
            )

            frame.grid_columnconfigure(
                indice,
                weight=1,
            )

    def crear_tarjeta(
        self,
        padre,
        titulo,
        valor,
        color,
    ):
        tarjeta = ctk.CTkFrame(
            padre,
            height=90,
            fg_color=PANEL,
            corner_radius=15,
            border_width=1,
            border_color=BORDE,
        )

        tarjeta.grid_propagate(
            False
        )

        tarjeta.grid_columnconfigure(
            1,
            weight=1,
        )

        tarjeta.grid_rowconfigure(
            0,
            weight=1,
        )

        acento = ctk.CTkFrame(
            tarjeta,
            width=6,
            fg_color=color,
            corner_radius=6,
        )

        acento.grid(
            row=0,
            column=0,
            padx=(11, 12),
            pady=8,
            sticky="ns",
        )

        contenido = ctk.CTkFrame(
            tarjeta,
            fg_color="transparent",
        )

        contenido.grid(
            row=0,
            column=1,
            padx=(0, 12),
            pady=8,
            sticky="nsew",
        )

        ctk.CTkLabel(
            contenido,
            text=titulo,
            font=(
                "Segoe UI",
                10,
                "bold",
            ),
            text_color=TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(
            fill="x",
            anchor="w",
            pady=(4, 0),
        )

        label_valor = ctk.CTkLabel(
            contenido,
            text=valor,
            font=(
                "Segoe UI",
                20,
                "bold",
            ),
            text_color=color,
            anchor="w",
        )

        label_valor.pack(
            fill="x",
            anchor="w",
            pady=(2, 4),
        )

        tarjeta.label_valor = (
            label_valor
        )

        return tarjeta

    def crear_tarjeta_resultado(
        self,
        padre,
        titulo,
        valor,
        color,
    ):
        tarjeta = ctk.CTkFrame(
            padre,
            height=64,
            fg_color=PANEL_3,
            corner_radius=13,
            border_width=1,
            border_color=BORDE,
        )

        tarjeta.pack_propagate(
            False
        )

        ctk.CTkLabel(
            tarjeta,
            text=titulo,
            font=(
                "Segoe UI",
                10,
                "bold",
            ),
            text_color=TEXTO_SECUNDARIO,
        ).pack(
            pady=(7, 1),
            padx=12,
        )

        label_valor = ctk.CTkLabel(
            tarjeta,
            text=valor,
            font=(
                "Segoe UI",
                15,
                "bold",
            ),
            text_color=color,
        )

        label_valor.pack(
            pady=(0, 7),
            padx=12,
        )

        tarjeta.label_valor = (
            label_valor
        )

        return tarjeta

    def crear_pestanas(self):
        self.pestanas = ctk.CTkTabview(
            self,
            fg_color=PANEL,
            corner_radius=17,
            border_width=1,
            border_color=BORDE,
            segmented_button_selected_color=AZUL,
            segmented_button_selected_hover_color=AZUL_HOVER,
            segmented_button_unselected_color=PANEL_2,
            segmented_button_unselected_hover_color=GRIS,
        )

        self.pestanas.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=(5, 10),
        )

        for nombre in (
            "Secuencial",
            "Paralelo / Sala de espera",
            "Comparación",
            "Escalabilidad",
        ):
            self.pestanas.add(
                nombre
            )

        self.crear_pestana_secuencial()
        self.crear_pestana_paralelo()
        self.crear_pestana_comparacion()
        self.crear_pestana_escalabilidad()

    def crear_pestana_secuencial(self):
        tab = self.pestanas.tab(
            "Secuencial"
        )

        frame = ctk.CTkFrame(
            tab,
            fg_color="transparent",
        )

        frame.pack(
            fill="x",
            padx=10,
            pady=(7, 5),
        )

        self.sec_procesos = self.crear_tarjeta_resultado(
            frame,
            "PROCESOS",
            "1",
            AZUL_CLARO,
        )

        self.sec_pid = self.crear_tarjeta_resultado(
            frame,
            "PID DEL PROCESO",
            "Pendiente",
            TURQUESA_CLARO,
        )

        self.sec_tiempo = self.crear_tarjeta_resultado(
            frame,
            "TIEMPO PROMEDIO",
            "Pendiente",
            VERDE_CLARO,
        )

        for indice, tarjeta in enumerate(
            (
                self.sec_procesos,
                self.sec_pid,
                self.sec_tiempo,
            )
        ):
            tarjeta.grid(
                row=0,
                column=indice,
                padx=5,
                sticky="ew",
            )

            frame.grid_columnconfigure(
                indice,
                weight=1,
            )

        self.tabla_secuencial = ctk.CTkFrame(
            tab,
            fg_color=PANEL_3,
            corner_radius=13,
        )

        self.tabla_secuencial.pack(
            fill="x",
            padx=15,
            pady=(4, 15),
        )

        self.mostrar_secuencial_vacio()

    def crear_pestana_paralelo(self):
        tab = self.pestanas.tab(
            "Paralelo / Sala de espera"
        )

        frame = ctk.CTkFrame(
            tab,
            fg_color="transparent",
        )

        frame.pack(
            fill="x",
            padx=10,
            pady=(7, 5),
        )

        self.par_pid_recepcion = self.crear_tarjeta_resultado(
            frame,
            "PID RECEPCIÓN",
            "Pendiente",
            AZUL_CLARO,
        )

        self.par_procesos = self.crear_tarjeta_resultado(
            frame,
            "PROCESOS MÉDICOS",
            "0",
            TURQUESA_CLARO,
        )

        self.par_simultaneo = self.crear_tarjeta_resultado(
            frame,
            "TRABAJO SIMULTÁNEO",
            "Pendiente",
            VERDE_CLARO,
        )

        self.par_coincidencias = self.crear_tarjeta_resultado(
            frame,
            "COINCIDENCIAS",
            "0",
            MORADO_CLARO,
        )

        for indice, tarjeta in enumerate(
            (
                self.par_pid_recepcion,
                self.par_procesos,
                self.par_simultaneo,
                self.par_coincidencias,
            )
        ):
            tarjeta.grid(
                row=0,
                column=indice,
                padx=5,
                sticky="ew",
            )

            frame.grid_columnconfigure(
                indice,
                weight=1,
            )

        self.contenido_paralelo = ctk.CTkScrollableFrame(
            tab,
            fg_color=PANEL_3,
            corner_radius=13,
            height=280,
        )

        self.contenido_paralelo.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(4, 12),
        )

        self.contenido_paralelo.grid_columnconfigure(
            0,
            weight=1,
        )

        self.contenido_paralelo.grid_columnconfigure(
            1,
            weight=1,
        )

        self.mostrar_paralelo_vacio()

    def crear_pestana_comparacion(self):
        tab = self.pestanas.tab(
            "Comparación"
        )

        frame_tiempos = ctk.CTkFrame(
            tab,
            fg_color="transparent",
        )

        frame_tiempos.pack(
            fill="x",
            padx=10,
            pady=(7, 5),
        )

        self.comp_tiempo_sec = self.crear_tarjeta_resultado(
            frame_tiempos,
            "TIEMPO SECUENCIAL",
            "Pendiente",
            AZUL_CLARO,
        )

        self.comp_tiempo_par = self.crear_tarjeta_resultado(
            frame_tiempos,
            "TIEMPO PARALELO",
            "Pendiente",
            TURQUESA_CLARO,
        )

        self.comp_mejora = self.crear_tarjeta_resultado(
            frame_tiempos,
            "MEJORA DE TIEMPO",
            "Pendiente",
            VERDE_CLARO,
        )

        for indice, tarjeta in enumerate(
            (
                self.comp_tiempo_sec,
                self.comp_tiempo_par,
                self.comp_mejora,
            )
        ):
            tarjeta.grid(
                row=0,
                column=indice,
                padx=5,
                sticky="ew",
            )

            frame_tiempos.grid_columnconfigure(
                indice,
                weight=1,
            )

        comparacion = ctk.CTkFrame(
            tab,
            fg_color=PANEL_3,
            corner_radius=14,
            border_width=1,
            border_color=BORDE,
        )

        comparacion.pack(
            fill="x",
            padx=15,
            pady=(5, 8),
        )

        encabezados = (
            "MODO",
            "PROCESOS",
            "TIEMPO",
            "PACIENTES",
        )

        for columna, titulo in enumerate(
            encabezados
        ):
            comparacion.grid_columnconfigure(
                columna,
                weight=1,
            )

            ctk.CTkLabel(
                comparacion,
                text=titulo,
                font=(
                    "Segoe UI",
                    11,
                    "bold",
                ),
                text_color=AZUL_CLARO,
                fg_color=PANEL_2,
                corner_radius=7,
            ).grid(
                row=0,
                column=columna,
                padx=4,
                pady=4,
                sticky="ew",
                ipady=7,
            )

        self.comp_fila_sec = []
        self.comp_fila_par = []

        for fila, lista in (
            (
                1,
                self.comp_fila_sec,
            ),
            (
                2,
                self.comp_fila_par,
            ),
        ):
            for columna in range(4):
                label = ctk.CTkLabel(
                    comparacion,
                    text="Pendiente",
                    font=(
                        "Segoe UI",
                        12,
                    ),
                    text_color=TEXTO,
                    fg_color=PANEL,
                    corner_radius=7,
                )

                label.grid(
                    row=fila,
                    column=columna,
                    padx=4,
                    pady=4,
                    sticky="ew",
                    ipady=8,
                )

                lista.append(
                    label
                )

        frame_metricas = ctk.CTkFrame(
            tab,
            fg_color="transparent",
        )

        frame_metricas.pack(
            fill="x",
            padx=10,
            pady=(4, 15),
        )

        self.comp_speedup = self.crear_tarjeta_resultado(
            frame_metricas,
            "SPEEDUP",
            "0.00x",
            MORADO_CLARO,
        )

        self.comp_eficiencia = self.crear_tarjeta_resultado(
            frame_metricas,
            "EFICIENCIA",
            "0.00%",
            NARANJA_CLARO,
        )

        self.comp_validacion = self.crear_tarjeta_resultado(
            frame_metricas,
            "MISMO RESULTADO",
            "Pendiente",
            VERDE_CLARO,
        )

        self.comp_simultaneo = self.crear_tarjeta_resultado(
            frame_metricas,
            "TRABAJO SIMULTÁNEO",
            "Pendiente",
            TURQUESA_CLARO,
        )

        for indice, tarjeta in enumerate(
            (
                self.comp_speedup,
                self.comp_eficiencia,
                self.comp_validacion,
                self.comp_simultaneo,
            )
        ):
            tarjeta.grid(
                row=0,
                column=indice,
                padx=5,
                sticky="ew",
            )

            frame_metricas.grid_columnconfigure(
                indice,
                weight=1,
            )

    def crear_pestana_escalabilidad(self):
        tab = self.pestanas.tab(
            "Escalabilidad"
        )

        ctk.CTkLabel(
            tab,
            text="ANÁLISIS DE ESCALABILIDAD",
            font=(
                "Segoe UI",
                16,
                "bold",
            ),
            text_color=MORADO_CLARO,
        ).pack(
            pady=(8, 2)
        )

        ctk.CTkLabel(
            tab,
            text=(
                "Prueba automáticamente "
                "1, 2, 4, 6, 8 y 12 procesos, "
                "según los procesadores disponibles."
            ),
            font=(
                "Segoe UI",
                11,
            ),
            text_color=TEXTO_SECUNDARIO,
        ).pack(
            pady=(0, 7)
        )

        frame = ctk.CTkFrame(
            tab,
            fg_color="transparent",
        )

        frame.pack(
            fill="x",
            padx=10,
            pady=(2, 7),
        )

        self.esc_referencia = self.crear_tarjeta_resultado(
            frame,
            "REFERENCIA SECUENCIAL",
            "Pendiente",
            AZUL_CLARO,
        )

        self.esc_mejor_procesos = self.crear_tarjeta_resultado(
            frame,
            "MEJOR CONFIG. PROBADA",
            "Pendiente",
            VERDE_CLARO,
        )

        self.esc_mejor_tiempo = self.crear_tarjeta_resultado(
            frame,
            "MEJOR TIEMPO",
            "Pendiente",
            TURQUESA_CLARO,
        )

        self.esc_mejor_speedup = self.crear_tarjeta_resultado(
            frame,
            "SPEEDUP",
            "Pendiente",
            MORADO_CLARO,
        )

        for indice, tarjeta in enumerate(
            (
                self.esc_referencia,
                self.esc_mejor_procesos,
                self.esc_mejor_tiempo,
                self.esc_mejor_speedup,
            )
        ):
            tarjeta.grid(
                row=0,
                column=indice,
                padx=5,
                sticky="ew",
            )

            frame.grid_columnconfigure(
                indice,
                weight=1,
            )

        tabla = ctk.CTkFrame(
            tab,
            fg_color=PANEL_3,
            corner_radius=14,
            border_width=1,
            border_color=BORDE,
        )

        tabla.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(4, 15),
        )

        cabecera = ctk.CTkFrame(
            tabla,
            fg_color="transparent",
        )

        cabecera.pack(
            fill="x",
            padx=(4, 18),
            pady=(4, 0),
        )

        encabezados = (
            "PROCESOS",
            "TIEMPO",
            "SPEEDUP",
            "EFICIENCIA",
            "MEJORA",
            "VALIDACIÓN",
        )

        for columna, titulo in enumerate(
            encabezados
        ):
            cabecera.grid_columnconfigure(
                columna,
                weight=1,
                uniform="esc",
            )

            ctk.CTkLabel(
                cabecera,
                text=titulo,
                font=(
                    "Segoe UI",
                    10,
                    "bold",
                ),
                text_color=MORADO_CLARO,
                fg_color=PANEL_2,
                corner_radius=7,
            ).grid(
                row=0,
                column=columna,
                padx=3,
                pady=3,
                sticky="ew",
                ipady=7,
            )

        self.tabla_escalabilidad = ctk.CTkScrollableFrame(
            tabla,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=GRIS,
            scrollbar_button_hover_color=GRIS_HOVER,
        )

        self.tabla_escalabilidad.pack(
            fill="both",
            expand=True,
            padx=4,
            pady=(0, 4),
        )

        for columna in range(6):
            self.tabla_escalabilidad.grid_columnconfigure(
                columna,
                weight=1,
                uniform="esc",
            )

        self.mostrar_escalabilidad_vacia()

    def leer_datos(self):
        try:
            cantidad = int(
                self.entry_cantidad.get()
            )

            medicos = int(
                self.combo_medicos.get()
            )

            repeticiones = int(
                self.combo_repeticiones.get()
            )

        except ValueError:
            raise ValueError(
                "Los valores deben ser números enteros."
            )

        if cantidad <= 0:
            raise ValueError(
                "La cantidad de pacientes debe ser mayor que cero."
            )

        if cantidad > 500000:
            raise ValueError(
                "La cantidad máxima para esta prueba "
                "es 500.000 pacientes."
            )

        if medicos <= 0:
            raise ValueError(
                "Debe seleccionar al menos un médico/proceso."
            )

        if repeticiones <= 0:
            raise ValueError(
                "Las repeticiones deben ser mayores que cero."
            )

        return (
            cantidad,
            medicos,
            repeticiones,
        )

    def iniciar_secuencial(self):
        if self.ejecutando:
            return

        try:
            (
                cantidad,
                _,
                repeticiones,
            ) = self.leer_datos()

        except ValueError as error:
            messagebox.showerror(
                "Datos incorrectos",
                str(error),
            )
            return

        self.preparar_ejecucion(
            "Ejecutando modo secuencial...",
            AZUL_CLARO,
            AZUL_FONDO,
        )

        self.pestanas.set(
            "Secuencial"
        )

        threading.Thread(
            target=self.trabajo_secuencial,
            args=(
                cantidad,
                repeticiones,
            ),
            daemon=True,
        ).start()

    def trabajo_secuencial(
        self,
        cantidad,
        repeticiones,
    ):
        try:
            datos = ejecutar_prueba_secuencial(
                cantidad,
                repeticiones,
            )

            self.cola_interfaz.put(
                (
                    "secuencial",
                    datos,
                )
            )

        except Exception as error:
            self.cola_interfaz.put(
                (
                    "error",
                    str(error),
                )
            )

    def iniciar_paralelo(self):
        if self.ejecutando:
            return

        try:
            (
                cantidad,
                medicos,
                repeticiones,
            ) = self.leer_datos()

        except ValueError as error:
            messagebox.showerror(
                "Datos incorrectos",
                str(error),
            )
            return

        self.preparar_ejecucion(
            "Ejecutando modo paralelo...",
            TURQUESA_CLARO,
            "#134E4A",
        )

        self.pestanas.set(
            "Paralelo / Sala de espera"
        )

        threading.Thread(
            target=self.trabajo_paralelo,
            args=(
                cantidad,
                medicos,
                repeticiones,
            ),
            daemon=True,
        ).start()

    def trabajo_paralelo(
        self,
        cantidad,
        medicos,
        repeticiones,
    ):
        try:
            datos = ejecutar_prueba_paralela(
                cantidad,
                medicos,
                repeticiones,
            )

            self.cola_interfaz.put(
                (
                    "paralelo",
                    datos,
                )
            )

        except Exception as error:
            self.cola_interfaz.put(
                (
                    "error",
                    str(error),
                )
            )

    def iniciar_comparacion(self):
        if self.ejecutando:
            return

        try:
            (
                cantidad,
                medicos,
                repeticiones,
            ) = self.leer_datos()

        except ValueError as error:
            messagebox.showerror(
                "Datos incorrectos",
                str(error),
            )
            return

        self.preparar_ejecucion(
            "Comparando secuencial y paralelo...",
            VERDE_CLARO,
            VERDE_OSCURO,
        )

        self.pestanas.set(
            "Comparación"
        )

        threading.Thread(
            target=self.trabajo_comparacion,
            args=(
                cantidad,
                medicos,
                repeticiones,
            ),
            daemon=True,
        ).start()

    def trabajo_comparacion(
        self,
        cantidad,
        medicos,
        repeticiones,
    ):
        try:
            datos = comparar_ejecuciones(
                cantidad,
                medicos,
                repeticiones,
            )

            self.cola_interfaz.put(
                (
                    "comparacion",
                    datos,
                )
            )

        except Exception as error:
            self.cola_interfaz.put(
                (
                    "error",
                    str(error),
                )
            )

    def iniciar_escalabilidad(self):
        if self.ejecutando:
            return

        try:
            (
                cantidad,
                _,
                repeticiones,
            ) = self.leer_datos()

        except ValueError as error:
            messagebox.showerror(
                "Datos incorrectos",
                str(error),
            )
            return

        configuraciones = [
            valor
            for valor in (
                1,
                2,
                4,
                6,
                8,
                12,
            )
            if valor <= self.cpu_disponibles
        ]

        if not configuraciones:
            configuraciones = [1]

        texto = (
            "Analizando escalabilidad: "
            + ", ".join(
                str(valor)
                for valor in configuraciones
            )
            + " procesos..."
        )

        self.preparar_ejecucion(
            texto,
            MORADO_CLARO,
            "#3B0764",
        )

        self.pestanas.set(
            "Escalabilidad"
        )

        threading.Thread(
            target=self.trabajo_escalabilidad,
            args=(
                cantidad,
                repeticiones,
                configuraciones,
            ),
            daemon=True,
        ).start()

    def trabajo_escalabilidad(
        self,
        cantidad,
        repeticiones,
        configuraciones,
    ):
        try:
            datos = analizar_escalabilidad(
                cantidad,
                repeticiones,
                configuraciones,
            )

            self.cola_interfaz.put(
                (
                    "escalabilidad",
                    datos,
                )
            )

        except Exception as error:
            self.cola_interfaz.put(
                (
                    "error",
                    str(error),
                )
            )

    def revisar_cola_interfaz(self):
        try:
            while True:
                tipo, contenido = (
                    self.cola_interfaz.get_nowait()
                )

                if tipo == "secuencial":
                    self.mostrar_resultado_secuencial(
                        contenido
                    )

                elif tipo == "paralelo":
                    self.mostrar_resultado_paralelo(
                        contenido
                    )

                elif tipo == "comparacion":
                    self.mostrar_resultado_comparacion(
                        contenido
                    )

                elif tipo == "escalabilidad":
                    self.mostrar_resultado_escalabilidad(
                        contenido
                    )

                elif tipo == "error":
                    self.mostrar_error(
                        contenido
                    )

        except Empty:
            pass

        self.after(
            100,
            self.revisar_cola_interfaz,
        )

    def mostrar_resultado_secuencial(
        self,
        datos,
    ):
        resultado = datos[
            "resultado"
        ]

        self.sec_procesos.label_valor.configure(
            text="1"
        )

        self.sec_pid.label_valor.configure(
            text=str(
                datos["pid"]
            )
        )

        self.sec_tiempo.label_valor.configure(
            text=(
                f"{datos['tiempo_promedio']:.4f} s"
            )
        )

        self.limpiar_frame(
            self.tabla_secuencial
        )

        encabezados = (
            "ORDEN",
            "PACIENTE",
            "LLEGADA",
            "PRIORIDAD",
        )

        for columna, titulo in enumerate(
            encabezados
        ):
            self.tabla_secuencial.grid_columnconfigure(
                columna,
                weight=1,
            )

            ctk.CTkLabel(
                self.tabla_secuencial,
                text=titulo,
                font=(
                    "Segoe UI",
                    11,
                    "bold",
                ),
                text_color=AZUL_CLARO,
                fg_color=PANEL_2,
                corner_radius=7,
            ).grid(
                row=0,
                column=columna,
                padx=4,
                pady=4,
                sticky="ew",
                ipady=6,
            )

        muestras = (
            datos.get(
                "muestras",
                [],
            )[:5]
        )

        if not muestras:
            solicitudes = ordenar_solicitudes_por_prioridad(
                datos["cantidad"]
            )

            muestras = [
                {
                    "orden_atencion": posicion,
                    "paciente": solicitud["paciente"],
                    "turno_llegada": solicitud["turno_llegada"],
                    "nombre_prioridad": NOMBRES_PRIORIDAD[
                        solicitud["prioridad"]
                    ],
                }
                for posicion, solicitud in enumerate(
                    solicitudes[:5],
                    start=1,
                )
            ]

        for fila, muestra in enumerate(
            muestras,
            start=1,
        ):
            valores = [
                str(
                    muestra["orden_atencion"]
                ),
                f"P{muestra['paciente']:04d}",
                str(
                    muestra["turno_llegada"]
                ),
                muestra["nombre_prioridad"],
            ]

            for columna, valor in enumerate(
                valores
            ):
                color = (
                    self.color_prioridad(
                        valor
                    )
                    if columna == 3
                    else TEXTO
                )

                ctk.CTkLabel(
                    self.tabla_secuencial,
                    text=valor,
                    font=(
                        "Segoe UI",
                        12,
                    ),
                    text_color=color,
                    fg_color=(
                        PANEL
                        if fila % 2
                        else PANEL_2
                    ),
                    corner_radius=7,
                ).grid(
                    row=fila,
                    column=columna,
                    padx=4,
                    pady=3,
                    sticky="ew",
                    ipady=7,
                )

        self.actualizar_tarjetas_principales(
            resultado,
            None,
            None,
        )

        self.finalizar_resultado(
            "Ejecución secuencial finalizada",
            "Secuencial",
        )

    def mostrar_resultado_paralelo(
        self,
        datos,
    ):
        resultado = datos[
            "resultado"
        ]

        productor = datos[
            "productor"
        ]

        self.par_pid_recepcion.label_valor.configure(
            text=str(
                productor["pid"]
            )
        )

        self.par_procesos.label_valor.configure(
            text=str(
                datos["medicos"]
            )
        )

        self.par_simultaneo.label_valor.configure(
            text=(
                "SÍ"
                if datos[
                    "paralelismo_detectado"
                ]
                else "NO"
            )
        )

        self.par_coincidencias.label_valor.configure(
            text=str(
                len(
                    datos[
                        "superposiciones"
                    ]
                )
            )
        )

        self.limpiar_frame(
            self.contenido_paralelo
        )

        fila = 0

        for indice, proceso in enumerate(
            datos["procesos"]
        ):
            columna = indice % 2

            if indice > 0 and columna == 0:
                fila += 1

            tarjeta = ctk.CTkFrame(
                self.contenido_paralelo,
                fg_color=PANEL,
                corner_radius=13,
                border_width=1,
                border_color=BORDE,
            )

            tarjeta.grid(
                row=fila,
                column=columna,
                padx=6,
                pady=6,
                sticky="nsew",
            )

            ctk.CTkLabel(
                tarjeta,
                text=(
                    f"MÉDICO "
                    f"{proceso['medico']}"
                ),
                font=(
                    "Segoe UI",
                    14,
                    "bold",
                ),
                text_color=TURQUESA_CLARO,
            ).pack(
                anchor="w",
                padx=14,
                pady=(12, 3),
            )

            ctk.CTkLabel(
                tarjeta,
                text=(
                    f"PID: "
                    f"{proceso['pid']}"
                ),
                font=(
                    "Segoe UI",
                    12,
                    "bold",
                ),
                text_color=AZUL_CLARO,
            ).pack(
                anchor="w",
                padx=14,
            )

            ctk.CTkLabel(
                tarjeta,
                text=(
                    f"Pacientes: "
                    f"{proceso['cantidad']}    "
                    f"Alta: "
                    f"{proceso['alta']}    "
                    f"Media: "
                    f"{proceso['media']}    "
                    f"Normal: "
                    f"{proceso['normal']}"
                ),
                font=(
                    "Segoe UI",
                    11,
                ),
                text_color=TEXTO,
            ).pack(
                anchor="w",
                padx=14,
                pady=(5, 2),
            )

            ctk.CTkLabel(
                tarjeta,
                text=(
                    f"Tiempo activo: "
                    f"{proceso['duracion']:.4f} s"
                ),
                font=(
                    "Segoe UI",
                    11,
                ),
                text_color=TEXTO_SECUNDARIO,
            ).pack(
                anchor="w",
                padx=14,
                pady=(0, 8),
            )

        fila += 1

        ctk.CTkLabel(
            self.contenido_paralelo,
            text="PRIMERAS ASIGNACIONES",
            font=(
                "Segoe UI",
                14,
                "bold",
            ),
            text_color=AZUL_CLARO,
        ).grid(
            row=fila,
            column=0,
            columnspan=2,
            pady=(14, 6),
        )

        fila += 1

        tabla = ctk.CTkFrame(
            self.contenido_paralelo,
            fg_color="transparent",
        )

        tabla.grid(
            row=fila,
            column=0,
            columnspan=2,
            padx=6,
            pady=(0, 8),
            sticky="ew",
        )

        for columna in range(4):
            tabla.grid_columnconfigure(
                columna,
                weight=1,
            )

        encabezados = (
            "ORDEN",
            "PACIENTE",
            "PRIORIDAD",
            "MÉDICO",
        )

        for columna, titulo in enumerate(
            encabezados
        ):
            ctk.CTkLabel(
                tabla,
                text=titulo,
                font=(
                    "Segoe UI",
                    11,
                    "bold",
                ),
                text_color=AZUL_CLARO,
                fg_color=PANEL_2,
                corner_radius=6,
            ).grid(
                row=0,
                column=columna,
                padx=3,
                pady=2,
                sticky="ew",
                ipady=6,
            )

        for indice, muestra in enumerate(
            datos["muestras"][:12],
            start=1,
        ):
            valores = [
                str(
                    muestra["solicitud"]
                ),
                f"P{muestra['paciente']:04d}",
                muestra["nombre_prioridad"],
                f"Médico {muestra['medico']}",
            ]

            for columna, valor in enumerate(
                valores
            ):
                color = (
                    self.color_prioridad(
                        valor
                    )
                    if columna == 2
                    else TEXTO
                )

                ctk.CTkLabel(
                    tabla,
                    text=valor,
                    font=(
                        "Segoe UI",
                        11,
                    ),
                    text_color=color,
                    fg_color=(
                        PANEL
                        if indice % 2
                        else PANEL_2
                    ),
                    corner_radius=6,
                ).grid(
                    row=indice,
                    column=columna,
                    padx=3,
                    pady=2,
                    sticky="ew",
                    ipady=6,
                )

        self.actualizar_tarjetas_principales(
            resultado,
            None,
            None,
        )

        self.finalizar_resultado(
            "Ejecución paralela finalizada",
            "Paralelo / Sala de espera",
        )

    def mostrar_resultado_comparacion(
        self,
        datos,
    ):
        secuencial = datos[
            "secuencial"
        ]

        paralelo = datos[
            "paralelo"
        ]

        resultado = secuencial[
            "resultado"
        ]

        self.comp_tiempo_sec.label_valor.configure(
            text=(
                f"{datos['tiempo_secuencial']:.4f} s"
            )
        )

        self.comp_tiempo_par.label_valor.configure(
            text=(
                f"{datos['tiempo_paralelo']:.4f} s"
            )
        )

        self.comp_mejora.label_valor.configure(
            text=(
                f"{datos['mejora']:.2f}%"
            )
        )

        self.comp_speedup.label_valor.configure(
            text=(
                f"{datos['speedup']:.2f}x"
            )
        )

        self.comp_eficiencia.label_valor.configure(
            text=(
                f"{datos['eficiencia']:.2f}%"
            )
        )

        self.comp_validacion.label_valor.configure(
            text=(
                "CORRECTO"
                if datos["correcto"]
                else "REVISAR"
            )
        )

        self.comp_simultaneo.label_valor.configure(
            text=(
                "SÍ"
                if paralelo[
                    "paralelismo_detectado"
                ]
                else "NO"
            )
        )

        valores_sec = [
            "Secuencial",
            "1",
            f"{datos['tiempo_secuencial']:.4f} s",
            f"{resultado['cantidad']:,}",
        ]

        valores_par = [
            "Paralelo",
            str(
                datos["medicos"]
            ),
            f"{datos['tiempo_paralelo']:.4f} s",
            f"{paralelo['resultado']['cantidad']:,}",
        ]

        for columna, valor in enumerate(
            valores_sec
        ):
            self.comp_fila_sec[
                columna
            ].configure(
                text=valor
            )

        for columna, valor in enumerate(
            valores_par
        ):
            self.comp_fila_par[
                columna
            ].configure(
                text=valor
            )

        self.actualizar_tarjetas_principales(
            resultado,
            datos["speedup"],
            datos["eficiencia"],
        )

        self.finalizar_resultado(
            "Comparación finalizada",
            "Comparación",
        )

    def mostrar_resultado_escalabilidad(
        self,
        datos,
    ):
        mejor = datos[
            "mejor"
        ]

        resultado_secuencial = datos[
            "secuencial"
        ][
            "resultado"
        ]

        self.esc_referencia.label_valor.configure(
            text=(
                f"{datos['tiempo_secuencial']:.4f} s"
            )
        )

        self.esc_mejor_procesos.label_valor.configure(
            text=(
                f"{mejor['procesos']} "
                f"proceso(s)"
            )
        )

        self.esc_mejor_tiempo.label_valor.configure(
            text=(
                f"{mejor['tiempo']:.4f} s"
            )
        )

        self.esc_mejor_speedup.label_valor.configure(
            text=(
                f"{mejor['speedup']:.2f}x"
            )
        )

        self.limpiar_frame(
            self.tabla_escalabilidad
        )

        for columna in range(6):
            self.tabla_escalabilidad.grid_columnconfigure(
                columna,
                weight=1,
                uniform="esc",
            )

        for fila, resultado in enumerate(
            datos["resultados"]
        ):
            valores = [
                str(
                    resultado["procesos"]
                ),

                f"{resultado['tiempo']:.4f} s",

                f"{resultado['speedup']:.2f}x",

                f"{resultado['eficiencia']:.2f}%",

                f"{resultado['mejora']:.2f}%",

                (
                    "CORRECTO"
                    if resultado[
                        "correcto"
                    ]
                    else "REVISAR"
                ),
            ]

            es_mejor = (
                resultado is mejor
            )

            for columna, valor in enumerate(
                valores
            ):
                color = TEXTO

                if (
                    columna == 5
                    and valor == "CORRECTO"
                ):
                    color = VERDE_CLARO

                if (
                    es_mejor
                    and columna != 5
                ):
                    color = MORADO_CLARO

                ctk.CTkLabel(
                    self.tabla_escalabilidad,
                    text=valor,
                    font=(
                        "Segoe UI",
                        11,
                        (
                            "bold"
                            if es_mejor
                            else "normal"
                        ),
                    ),
                    text_color=color,
                    fg_color=(
                        PANEL_2
                        if es_mejor
                        else (
                            PANEL
                            if fila % 2 == 0
                            else PANEL_3
                        )
                    ),
                    corner_radius=6,
                ).grid(
                    row=fila,
                    column=columna,
                    padx=4,
                    pady=3,
                    sticky="ew",
                    ipady=7,
                )

        self.actualizar_tarjetas_principales(
            resultado_secuencial,
            mejor["speedup"],
            mejor["eficiencia"],
        )

        self.finalizar_resultado(
            "Análisis de escalabilidad finalizado",
            "Escalabilidad",
        )

    def preparar_ejecucion(
        self,
        texto,
        color_texto,
        color_fondo,
    ):
        self.ejecutando = True

        self.cambiar_botones(
            "disabled"
        )

        self.barra_progreso.set(
            0.15
        )

        self.label_porcentaje.configure(
            text="15%"
        )

        self.cambiar_estado(
            texto,
            color_texto,
            color_fondo,
        )

    def finalizar_resultado(
        self,
        mensaje,
        pestana,
    ):
        self.barra_progreso.set(
            1
        )

        self.label_porcentaje.configure(
            text="100%"
        )

        self.cambiar_estado(
            mensaje,
            VERDE_CLARO,
            VERDE_OSCURO,
        )

        self.pestanas.set(
            pestana
        )

        self.finalizar_procesamiento()

    def cambiar_estado(
        self,
        texto,
        color_texto,
        color_fondo,
    ):
        self.frame_estado.configure(
            fg_color=color_fondo
        )

        self.label_estado.configure(
            text=f"●  {texto}",
            text_color=color_texto,
        )

    def cambiar_botones(
        self,
        estado,
    ):
        for boton in (
            self.boton_secuencial,
            self.boton_paralelo,
            self.boton_comparar,
            self.boton_escalabilidad,
            self.boton_limpiar,
        ):
            boton.configure(
                state=estado
            )

    def finalizar_procesamiento(self):
        self.ejecutando = False

        self.cambiar_botones(
            "normal"
        )

    def mostrar_error(
        self,
        mensaje,
    ):
        self.barra_progreso.set(
            0
        )

        self.label_porcentaje.configure(
            text="0%"
        )

        self.cambiar_estado(
            "La ejecución terminó con error",
            ROJO_CLARO,
            ROJO_FONDO,
        )

        self.finalizar_procesamiento()

        messagebox.showerror(
            "Error de ejecución",
            mensaje,
        )

    def actualizar_tarjetas_principales(
        self,
        resultado,
        speedup,
        eficiencia,
    ):
        self.tarjeta_pacientes.label_valor.configure(
            text=(
                f"{resultado['cantidad']:,}"
            )
        )

        self.tarjeta_prioridad.label_valor.configure(
            text=(
                f"{resultado['alta']:,}"
            )
        )

        self.tarjeta_speedup.label_valor.configure(
            text=(
                "--"
                if speedup is None
                else f"{speedup:.2f}x"
            )
        )

        self.tarjeta_eficiencia.label_valor.configure(
            text=(
                "--"
                if eficiencia is None
                else f"{eficiencia:.2f}%"
            )
        )

    def color_prioridad(
        self,
        prioridad,
    ):
        if prioridad == "Alta":
            return ROJO_CLARO

        if prioridad == "Media":
            return AMARILLO_TEXTO

        return VERDE_CLARO

    def limpiar_frame(
        self,
        frame,
    ):
        for widget in (
            frame.winfo_children()
        ):
            widget.destroy()

    def mostrar_secuencial_vacio(self):
        self.limpiar_frame(
            self.tabla_secuencial
        )

        ctk.CTkLabel(
            self.tabla_secuencial,
            text=(
                "Ejecuta SECUENCIAL para ver "
                "el orden de atención."
            ),
            font=(
                "Segoe UI",
                14,
            ),
            text_color=TEXTO_SECUNDARIO,
        ).grid(
            row=0,
            column=0,
            padx=20,
            pady=45,
        )

    def mostrar_paralelo_vacio(self):
        self.limpiar_frame(
            self.contenido_paralelo
        )

        ctk.CTkLabel(
            self.contenido_paralelo,
            text=(
                "Ejecuta PARALELO para ver "
                "los médicos y la sala de espera."
            ),
            font=(
                "Segoe UI",
                14,
            ),
            text_color=TEXTO_SECUNDARIO,
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            padx=20,
            pady=55,
        )

    def mostrar_escalabilidad_vacia(self):
        self.limpiar_frame(
            self.tabla_escalabilidad
        )

        ctk.CTkLabel(
            self.tabla_escalabilidad,
            text=(
                "Pulsa ANALIZAR ESCALABILIDAD "
                "para ejecutar las configuraciones disponibles."
            ),
            font=(
                "Segoe UI",
                13,
            ),
            text_color=TEXTO_SECUNDARIO,
        ).grid(
            row=0,
            column=0,
            columnspan=6,
            padx=20,
            pady=45,
        )

    def limpiar(self):
        if self.ejecutando:
            return

        self.tarjeta_pacientes.label_valor.configure(
            text="0"
        )

        self.tarjeta_prioridad.label_valor.configure(
            text="0"
        )

        self.tarjeta_speedup.label_valor.configure(
            text="0.00x"
        )

        self.tarjeta_eficiencia.label_valor.configure(
            text="0.00%"
        )

        self.sec_procesos.label_valor.configure(
            text="1"
        )

        self.sec_pid.label_valor.configure(
            text="Pendiente"
        )

        self.sec_tiempo.label_valor.configure(
            text="Pendiente"
        )

        self.par_pid_recepcion.label_valor.configure(
            text="Pendiente"
        )

        self.par_procesos.label_valor.configure(
            text="0"
        )

        self.par_simultaneo.label_valor.configure(
            text="Pendiente"
        )

        self.par_coincidencias.label_valor.configure(
            text="0"
        )

        self.comp_tiempo_sec.label_valor.configure(
            text="Pendiente"
        )

        self.comp_tiempo_par.label_valor.configure(
            text="Pendiente"
        )

        self.comp_mejora.label_valor.configure(
            text="Pendiente"
        )

        self.comp_speedup.label_valor.configure(
            text="0.00x"
        )

        self.comp_eficiencia.label_valor.configure(
            text="0.00%"
        )

        self.comp_validacion.label_valor.configure(
            text="Pendiente"
        )

        self.comp_simultaneo.label_valor.configure(
            text="Pendiente"
        )

        for label in (
            self.comp_fila_sec
            + self.comp_fila_par
        ):
            label.configure(
                text="Pendiente"
            )

        self.esc_referencia.label_valor.configure(
            text="Pendiente"
        )

        self.esc_mejor_procesos.label_valor.configure(
            text="Pendiente"
        )

        self.esc_mejor_tiempo.label_valor.configure(
            text="Pendiente"
        )

        self.esc_mejor_speedup.label_valor.configure(
            text="Pendiente"
        )

        self.mostrar_secuencial_vacio()
        self.mostrar_paralelo_vacio()
        self.mostrar_escalabilidad_vacia()

        self.barra_progreso.set(
            0
        )

        self.label_porcentaje.configure(
            text="0%"
        )

        self.pestanas.set(
            "Secuencial"
        )

        self.cambiar_estado(
            "Listo para iniciar",
            AZUL_CLARO,
            AZUL_FONDO,
        )


if __name__ == "__main__":
    freeze_support()

    app = InterfazAtencionMedica()

    app.mainloop()