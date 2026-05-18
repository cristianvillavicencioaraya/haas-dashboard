# dashboard_haas_simulado.py
# Dashboard web simulado para tornos Haas
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
    page_title="Dashboard Haas CNC - Simulación",
    page_icon="⚙️",
    layout="wide"
)


# -----------------------------
# Configuración de máquinas
# -----------------------------
MAQUINAS = [
    "Torno Haas 1",
    "Torno Haas 2",
    "Torno Haas 3",
    "Torno Haas 4",
]

PROGRAMAS = ["O12345", "O20410", "O33001", "O45020", "O55100"]
ESTADOS = ["Produciendo", "Detenido", "Alarma", "Setup", "Sin material"]
OPERADORES = ["Juan", "Pedro", "Carlos", "Luis", "Miguel"]
CAUSAS_DETENCION = [
    "Cambio herramienta",
    "Falta material",
    "Setup",
    "Alarma CNC",
    "Espera operador",
    "Mantención",
    "Sin detención",
]


# -----------------------------
# Funciones de simulación
# -----------------------------
def simular_maquina(nombre: str) -> dict:
    estado = random.choices(
        ESTADOS,
        weights=[65, 12, 8, 10, 5],
        k=1
    )[0]

    ciclo_objetivo = random.randint(150, 420)  # segundos
    ciclo_real = max(60, int(ciclo_objetivo * random.uniform(0.85, 1.35)))

    piezas_turno = random.randint(20, 180) if estado != "Alarma" else random.randint(0, 40)
    piezas_buenas = int(piezas_turno * random.uniform(0.94, 1.00))
    piezas_malas = max(0, piezas_turno - piezas_buenas)

    uptime_horas = round(random.uniform(3.0, 7.8), 2) if estado == "Produciendo" else round(random.uniform(0.5, 5.0), 2)
    downtime_horas = round(8.0 - uptime_horas, 2)

    disponibilidad = min(100, max(0, uptime_horas / 8.0 * 100))
    rendimiento = min(100, max(0, ciclo_objetivo / ciclo_real * 100))
    calidad = min(100, max(0, piezas_buenas / piezas_turno * 100 if piezas_turno > 0 else 0))
    oee = round((disponibilidad / 100) * (rendimiento / 100) * (calidad / 100) * 100, 1)

    return {
        "Máquina": nombre,
        "Estado": estado,
        "Programa": random.choice(PROGRAMAS),
        "Operador": random.choice(OPERADORES),
        "Piezas turno": piezas_turno,
        "Piezas buenas": piezas_buenas,
        "Piezas malas": piezas_malas,
        "Tiempo ciclo objetivo (s)": ciclo_objetivo,
        "Tiempo ciclo real (s)": ciclo_real,
        "Uptime (h)": uptime_horas,
        "Downtime (h)": downtime_horas,
        "Disponibilidad (%)": round(disponibilidad, 1),
        "Rendimiento (%)": round(rendimiento, 1),
        "Calidad (%)": round(calidad, 1),
        "OEE (%)": oee,
        "Causa detención": random.choice(CAUSAS_DETENCION) if estado != "Produciendo" else "Sin detención",
        "Última actualización": datetime.now().strftime("%H:%M:%S"),
    }


def crear_historial(maquinas: list[str], horas: int = 8) -> pd.DataFrame:
    registros = []
    ahora = datetime.now()

    for maquina in maquinas:
        piezas_acumuladas = 0
        for i in range(horas * 6):  # cada 10 minutos
            t = ahora - timedelta(minutes=(horas * 60 - i * 10))
            estado = random.choices(ESTADOS, weights=[70, 10, 5, 10, 5], k=1)[0]
            piezas = random.randint(2, 8) if estado == "Produciendo" else 0
            piezas_acumuladas += piezas

            registros.append({
                "Hora": t,
                "Máquina": maquina,
                "Estado": estado,
                "Piezas acumuladas": piezas_acumuladas,
                "Piezas intervalo": piezas,
                "OEE (%)": random.randint(45, 92) if estado == "Produciendo" else random.randint(5, 50),
            })

    return pd.DataFrame(registros)


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("⚙️ Simulador Haas CNC")
st.sidebar.write("Dashboard demostrativo para cliente.")

auto_refresh = st.sidebar.checkbox("Actualizar automáticamente", value=False)
segundos = st.sidebar.slider("Cada cuántos segundos actualizar", 3, 30, 5)
turno = st.sidebar.selectbox("Turno", ["Turno A - 07:00 a 15:00", "Turno B - 15:00 a 23:00", "Turno C - 23:00 a 07:00"])

st.sidebar.markdown("---")
st.sidebar.write("Este dashboard simula datos que podrían venir desde Haas por RS-232, Ethernet o una Raspberry Pi.")


# -----------------------------
# Datos simulados
# -----------------------------
datos = pd.DataFrame([simular_maquina(m) for m in MAQUINAS])
historial = crear_historial(MAQUINAS, horas=8)


# -----------------------------
# Título
# -----------------------------
st.title("Dashboard Web - Monitoreo de Tornos Haas CNC")
st.caption(f"{turno} | Última actualización: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


# -----------------------------
# KPIs generales
# -----------------------------
total_piezas = int(datos["Piezas turno"].sum())
prom_oee = round(datos["OEE (%)"].mean(), 1)
maquinas_produciendo = int((datos["Estado"] == "Produciendo").sum())
alarmas = int((datos["Estado"] == "Alarma").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Piezas turno", total_piezas)
c2.metric("OEE promedio", f"{prom_oee}%")
c3.metric("Máquinas produciendo", f"{maquinas_produciendo}/{len(MAQUINAS)}")
c4.metric("Alarmas activas", alarmas)


# -----------------------------
# Estado por máquina
# -----------------------------
st.subheader("Estado actual de máquinas")

cols = st.columns(len(MAQUINAS))
for i, row in datos.iterrows():
    with cols[i]:
        st.markdown(f"### {row['Máquina']}")
        st.write(f"**Estado:** {row['Estado']}")
        st.write(f"**Programa:** {row['Programa']}")
        st.write(f"**Operador:** {row['Operador']}")
        st.write(f"**Piezas:** {row['Piezas turno']}")
        st.write(f"**Ciclo real:** {row['Tiempo ciclo real (s)']} s")
        st.write(f"**OEE:** {row['OEE (%)']}%")
        st.write(f"**Causa:** {row['Causa detención']}")


# -----------------------------
# Tabla principal
# -----------------------------
st.subheader("Tabla de producción actual")
st.dataframe(datos, use_container_width=True)


# -----------------------------
# Gráficos
# -----------------------------
g1, g2 = st.columns(2)

with g1:
    fig_oee = px.bar(
        datos,
        x="Máquina",
        y="OEE (%)",
        text="OEE (%)",
        title="OEE por máquina"
    )
    st.plotly_chart(fig_oee, use_container_width=True)

with g2:
    fig_piezas = px.bar(
        datos,
        x="Máquina",
        y=["Piezas buenas", "Piezas malas"],
        title="Piezas buenas vs piezas malas"
    )
    st.plotly_chart(fig_piezas, use_container_width=True)


g3, g4 = st.columns(2)

with g3:
    fig_uptime = px.bar(
        datos,
        x="Máquina",
        y=["Uptime (h)", "Downtime (h)"],
        title="Uptime vs Downtime por máquina"
    )
    st.plotly_chart(fig_uptime, use_container_width=True)

with g4:
    resumen_estados = datos["Estado"].value_counts().reset_index()
    resumen_estados.columns = ["Estado", "Cantidad"]
    fig_estado = px.pie(
        resumen_estados,
        names="Estado",
        values="Cantidad",
        title="Distribución de estados"
    )
    st.plotly_chart(fig_estado, use_container_width=True)


# -----------------------------
# Historial
# -----------------------------
st.subheader("Historial simulado del turno")

maquina_filtro = st.selectbox("Seleccionar máquina para historial", MAQUINAS)

hist_filtrado = historial[historial["Máquina"] == maquina_filtro]

fig_hist = px.line(
    hist_filtrado,
    x="Hora",
    y="Piezas acumuladas",
    title=f"Piezas acumuladas - {maquina_filtro}"
)
st.plotly_chart(fig_hist, use_container_width=True)

fig_oee_hist = px.line(
    hist_filtrado,
    x="Hora",
    y="OEE (%)",
    title=f"OEE histórico - {maquina_filtro}"
)
st.plotly_chart(fig_oee_hist, use_container_width=True)


# -----------------------------
# Alarmas
# -----------------------------
st.subheader("Alarmas y detenciones")

alarmas_df = datos[datos["Estado"].isin(["Alarma", "Detenido", "Sin material"])]

if alarmas_df.empty:
    st.success("No hay alarmas ni detenciones críticas activas.")
else:
    st.warning("Hay eventos que requieren revisión.")
    st.dataframe(
        alarmas_df[["Máquina", "Estado", "Causa detención", "Operador", "Última actualización"]],
        use_container_width=True
    )


# -----------------------------
# Nota técnica
# -----------------------------
with st.expander("Cómo se conectaría esto a un Haas real"):
    st.write("""
    En una máquina real, estos datos podrían venir desde el control Haas usando RS-232 o Ethernet.

    Ejemplos de comandos vistos en el manual:

    - Q100: número de serie
    - Q101: versión de software
    - Q102: modelo de máquina
    - Q104: modo actual
    - Q200: cambios de herramienta
    - Q201: herramienta en uso
    - Q300: tiempo encendido
    - Q301: tiempo de movimiento
    - Q303: último tiempo de ciclo
    - Q402 / Q403: contador de piezas
    - Q500: estado resumido
    - Q600: lectura de variables macro

    Una Raspberry Pi puede consultar esos datos, guardarlos en una base de datos y alimentar este dashboard.
    """)


# -----------------------------
# Auto refresh simple
# -----------------------------
if auto_refresh:
    time.sleep(segundos)
    st.rerun()
