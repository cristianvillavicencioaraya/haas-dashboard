
# dashboard_haas_simulado.py
# Panel de control simulado para tornos de la empresa Forymec
# Ejecutar con:
#   pip install streamlit pandas plotly
#   streamlit run dashboard_haas_simulado.py

import time
import random
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Panel de Control Forymec - Tornos",
    page_icon="⚙️",
    layout="wide"
)


MAQUINAS = [
    "Torno Forymec 1",
    "Torno Forymec 2",
    "Torno Forymec 3",
    "Torno Forymec 4",
    "Torno Forymec 5",
    "Torno Forymec 6",
    "Torno Forymec 7",
    "Torno Forymec 8",
]

PROGRAMAS = ["P-1001", "P-1002", "P-2001", "P-3005", "P-4100", "P-5100"]
ESTADOS = ["Produciendo", "Detenido", "Alarma", "Preparación", "Sin material"]
OPERADORES = ["Operador 1", "Operador 2", "Operador 3", "Operador 4", "Operador 5"]

CAUSAS_DETENCION = [
    "Cambio de herramienta",
    "Falta de material",
    "Preparación de máquina",
    "Alarma de máquina",
    "Espera de operador",
    "Mantención",
    "Sin detención",
]


def simular_maquina(nombre: str) -> dict:
    estado = random.choices(ESTADOS, weights=[65, 12, 8, 10, 5], k=1)[0]

    tiempo_objetivo = random.randint(150, 420)
    tiempo_real = max(60, int(tiempo_objetivo * random.uniform(0.85, 1.35)))

    piezas_turno = random.randint(20, 180) if estado != "Alarma" else random.randint(0, 40)
    piezas_buenas = int(piezas_turno * random.uniform(0.94, 1.00))
    piezas_rechazadas = max(0, piezas_turno - piezas_buenas)

    horas_produciendo = (
        round(random.uniform(3.0, 7.8), 2)
        if estado == "Produciendo"
        else round(random.uniform(0.5, 5.0), 2)
    )
    horas_detenido = round(8.0 - horas_produciendo, 2)

    disponibilidad = min(100, max(0, horas_produciendo / 8.0 * 100))
    rendimiento = min(100, max(0, tiempo_objetivo / tiempo_real * 100))
    calidad = min(100, max(0, piezas_buenas / piezas_turno * 100 if piezas_turno > 0 else 0))

    eficiencia_general = round(
        (disponibilidad / 100) * (rendimiento / 100) * (calidad / 100) * 100,
        1
    )

    return {
        "Máquina": nombre,
        "Estado": estado,
        "Programa": random.choice(PROGRAMAS),
        "Operador": random.choice(OPERADORES),
        "Piezas del turno": piezas_turno,
        "Piezas buenas": piezas_buenas,
        "Piezas rechazadas": piezas_rechazadas,
        "Tiempo objetivo por pieza (s)": tiempo_objetivo,
        "Tiempo real por pieza (s)": tiempo_real,
        "Horas produciendo": horas_produciendo,
        "Horas detenido": horas_detenido,
        "Disponibilidad (%)": round(disponibilidad, 1),
        "Rendimiento (%)": round(rendimiento, 1),
        "Calidad (%)": round(calidad, 1),
        "Eficiencia general de producción (%)": eficiencia_general,
        "Causa de detención": random.choice(CAUSAS_DETENCION) if estado != "Produciendo" else "Sin detención",
        "Última actualización": datetime.now().strftime("%H:%M:%S"),
    }


def crear_historial(maquinas: list[str], horas: int = 8) -> pd.DataFrame:
    registros = []
    ahora = datetime.now()

    for maquina in maquinas:
        piezas_acumuladas = 0
        for i in range(horas * 6):
            t = ahora - timedelta(minutes=(horas * 60 - i * 10))
            estado = random.choices(ESTADOS, weights=[70, 10, 5, 10, 5], k=1)[0]
            piezas = random.randint(2, 8) if estado == "Produciendo" else 0
            piezas_acumuladas += piezas

            registros.append({
                "Hora": t,
                "Máquina": maquina,
                "Estado": estado,
                "Piezas acumuladas": piezas_acumuladas,
                "Piezas por intervalo": piezas,
                "Eficiencia general de producción (%)": random.randint(45, 92) if estado == "Produciendo" else random.randint(5, 50),
            })

    return pd.DataFrame(registros)


st.sidebar.title("⚙️ Panel Forymec")
st.sidebar.write("Panel de control demostrativo para monitoreo de tornos.")

actualizacion_automatica = st.sidebar.checkbox("Actualizar automáticamente", value=False)

minutos = st.sidebar.slider(
    "Tiempo de actualización automática",
    min_value=1,
    max_value=60,
    value=5,
    step=1
)

turno = st.sidebar.selectbox(
    "Turno",
    [
        "Turno A - 07:00 a 15:00",
        "Turno B - 15:00 a 23:00",
        "Turno C - 23:00 a 07:00",
    ]
)

st.sidebar.markdown("---")
st.sidebar.write("La información mostrada es simulada para presentación comercial.")


datos = pd.DataFrame([simular_maquina(m) for m in MAQUINAS])
historial = crear_historial(MAQUINAS, horas=8)


st.title("Panel de Control de Producción - Tornos Forymec")
st.caption(f"{turno} | Última actualización: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


total_piezas = int(datos["Piezas del turno"].sum())
promedio_eficiencia = round(datos["Eficiencia general de producción (%)"].mean(), 1)
maquinas_produciendo = int((datos["Estado"] == "Produciendo").sum())
alarmas = int((datos["Estado"] == "Alarma").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Piezas del turno", total_piezas)
c2.metric("Eficiencia general promedio", f"{promedio_eficiencia}%")
c3.metric("Máquinas produciendo", f"{maquinas_produciendo}/{len(MAQUINAS)}")
c4.metric("Alarmas activas", alarmas)


with st.expander("¿Qué significa la eficiencia general de producción?"):
    st.write("""
    La eficiencia general de producción permite medir qué tan bien se está utilizando cada torno durante el turno.

    Se calcula considerando tres factores:

    - Disponibilidad: cuánto tiempo la máquina estuvo disponible y produciendo.
    - Rendimiento: qué tan cerca está el tiempo real de fabricación respecto al tiempo esperado.
    - Calidad: cuántas piezas buenas se fabricaron respecto al total de piezas producidas.

    Una eficiencia alta indica que la máquina produjo durante más tiempo, con buenos tiempos de fabricación y con baja cantidad de piezas rechazadas.
    """)


st.subheader("Estado actual de los tornos")

for grupo_inicio in range(0, len(MAQUINAS), 4):
    columnas = st.columns(4)
    for posicion, (_, row) in enumerate(datos.iloc[grupo_inicio:grupo_inicio + 4].iterrows()):
        with columnas[posicion]:
            st.markdown(f"### {row['Máquina']}")
            st.write(f"**Estado:** {row['Estado']}")
            st.write(f"**Programa:** {row['Programa']}")
            st.write(f"**Operador:** {row['Operador']}")
            st.write(f"**Piezas del turno:** {row['Piezas del turno']}")
            st.write(f"**Tiempo real por pieza:** {row['Tiempo real por pieza (s)']} s")
            st.write(f"**Eficiencia:** {row['Eficiencia general de producción (%)']}%")
            st.write(f"**Causa:** {row['Causa de detención']}")


st.subheader("Tabla de producción actual")
st.dataframe(datos, use_container_width=True)


g1, g2 = st.columns(2)

with g1:
    fig_eficiencia = px.bar(
        datos,
        x="Máquina",
        y="Eficiencia general de producción (%)",
        text="Eficiencia general de producción (%)",
        title="Eficiencia general por máquina"
    )
    st.plotly_chart(fig_eficiencia, use_container_width=True)

with g2:
    fig_piezas = px.bar(
        datos,
        x="Máquina",
        y=["Piezas buenas", "Piezas rechazadas"],
        title="Piezas buenas y piezas rechazadas"
    )
    st.plotly_chart(fig_piezas, use_container_width=True)


g3, g4 = st.columns(2)

with g3:
    fig_tiempo = px.bar(
        datos,
        x="Máquina",
        y=["Horas produciendo", "Horas detenido"],
        title="Horas produciendo y horas detenido por máquina"
    )
    st.plotly_chart(fig_tiempo, use_container_width=True)

with g4:
    resumen_estados = datos["Estado"].value_counts().reset_index()
    resumen_estados.columns = ["Estado", "Cantidad"]
    fig_estado = px.pie(
        resumen_estados,
        names="Estado",
        values="Cantidad",
        title="Distribución de estados de los tornos"
    )
    st.plotly_chart(fig_estado, use_container_width=True)


st.subheader("Historial simulado del turno")

maquina_filtro = st.selectbox("Seleccionar máquina para revisar historial", MAQUINAS)
hist_filtrado = historial[historial["Máquina"] == maquina_filtro]

fig_hist = px.line(
    hist_filtrado,
    x="Hora",
    y="Piezas acumuladas",
    title=f"Piezas acumuladas - {maquina_filtro}"
)
st.plotly_chart(fig_hist, use_container_width=True)

fig_eficiencia_hist = px.line(
    hist_filtrado,
    x="Hora",
    y="Eficiencia general de producción (%)",
    title=f"Eficiencia histórica - {maquina_filtro}"
)
st.plotly_chart(fig_eficiencia_hist, use_container_width=True)


st.subheader("Alarmas y detenciones")

eventos_df = datos[datos["Estado"].isin(["Alarma", "Detenido", "Sin material"])]

if eventos_df.empty:
    st.success("No hay alarmas ni detenciones críticas activas.")
else:
    st.warning("Hay eventos que requieren revisión.")
    st.dataframe(
        eventos_df[["Máquina", "Estado", "Causa de detención", "Operador", "Última actualización"]],
        use_container_width=True
    )


if actualizacion_automatica:
    time.sleep(minutos * 60)
    st.rerun()
