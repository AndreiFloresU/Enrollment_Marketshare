import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Cargar los datos
df = pd.read_excel("./files/base_universidades2.xlsx")

# Título de la aplicación
st.title("MARKETSHARE")

# Filtros en la barra lateral
st.sidebar.header("Filtros")

# Filtro de Año
anio = st.sidebar.multiselect(
    "Año:",
    options=sorted(df["AÑO"].unique()),
    default=sorted(df["AÑO"].unique()),
    help="Selecciona uno o más años",
)

filtered_df = df.copy()

if anio:
    filtered_df = filtered_df[filtered_df["AÑO"].isin(anio)]

# Filtro de Región
region = st.sidebar.multiselect(
    "Región:",
    options=df["REGION"].unique(),
    default=None,
    help="Selecciona una o más regiones",
)

if region:
    filtered_df = filtered_df[filtered_df["REGION"].isin(region)]

# Filtro de Financiamiento
financiamiento = st.sidebar.multiselect(
    "Financiamiento:",
    options=filtered_df["FINANCIAMIENTO"].unique(),
    default=None,
    help="Selecciona uno o más tipos de financiamiento",
)

if financiamiento:
    filtered_df = filtered_df[filtered_df["FINANCIAMIENTO"].isin(financiamiento)]

# Filtro de Nivel
nivel = st.sidebar.multiselect(
    "Nivel:",
    options=filtered_df["NIVEL"].unique(),
    default=None,
    help="Selecciona uno o más niveles",
)

if nivel:
    filtered_df = filtered_df[filtered_df["NIVEL"].isin(nivel)]

# Filtro de Facultad
facultad = st.sidebar.selectbox(
    "Facultad:",
    options=[None] + filtered_df["FACULTAD"].unique().tolist(),
    index=0,
    help="Selecciona una facultad",
)

if facultad:
    filtered_df = filtered_df[filtered_df["FACULTAD"] == facultad]

# Filtro de Carrera
carrera = st.sidebar.multiselect(
    "Carrera:",
    options=filtered_df["CARRERA"].unique(),
    default=None,
    help="Selecciona una o más carreras",
)

if carrera:
    filtered_df = filtered_df[filtered_df["CARRERA"].isin(carrera)]

# Agrupar por universidad y año
df_agrupado = (
    filtered_df.groupby(["AÑO", "UNIVERSIDAD"])
    .agg({"MATRICULADOS": "sum"})
    .reset_index()
)

# Verificar que haya datos
if df_agrupado.empty:
    st.write("No hay datos con los filtros seleccionados.")
    st.stop()

# Calcular la participación
df_agrupado["PARTICIPACION"] = df_agrupado.groupby("AÑO")["MATRICULADOS"].transform(
    lambda x: x / x.sum()
)

# Función para mapear participación a escala de grises
def map_to_grayscale(value, min_val, max_val):
    if max_val == min_val:
        gray_level = 150  # Valor por defecto si no hay variación
    else:
        # Normalizar el valor entre 0 y 1
        norm = (value - min_val) / (max_val - min_val)
        # Invertir para que mayor participación sea más oscuro
        gray_level = int(255 * (1 - norm) * 0.7)  # Multiplicamos por 0.7 para evitar colores muy claros
    return f"rgb({gray_level}, {gray_level}, {gray_level})"

# Crear la figura
fig = go.Figure()

# Obtener los años únicos
años = df_agrupado["AÑO"].unique()

# Dibujar barras para cada año
for i, año in enumerate(años):
    df_year = df_agrupado[df_agrupado["AÑO"] == año]

    # Ordenar de menor a mayor participación
    df_year = df_year.sort_values(by="PARTICIPACION")

    # Obtener valores mínimos y máximos de participación para este año
    min_p = df_year["PARTICIPACION"].min()
    max_p = df_year["PARTICIPACION"].max()

    # Definir colores
    colors = [
        "#8d002e" if universidad == "UNIVERSIDAD DE LAS AMERICAS" else map_to_grayscale(p, min_p, max_p)
        for universidad, p in zip(df_year["UNIVERSIDAD"], df_year["PARTICIPACION"])
    ]

    fig.add_trace(
        go.Bar(
            x=df_year["PARTICIPACION"],
            y=df_year["UNIVERSIDAD"],
            marker_color=colors,
            orientation="h",
            name=f"Año {año}",
            text=df_year["PARTICIPACION"].apply(lambda x: f"{x:.2%}"),
            textposition="auto",
            textfont=dict(color="white"),
        )
    )

# Configurar el diseño del gráfico
fig.update_layout(
    barmode="group",
    title="Participación por Universidad y Año",
    xaxis_title="Participación",
    yaxis_title="Universidades",
    template="plotly_white",
    height=700,
)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig)
