import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Mortalidad Colombia 2019", page_icon="📊", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1rem; max-width: 1450px; }

[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e5e7eb;
}

.panel-title {
    font-size: 22px;
    font-weight: 800;
    color: #1f2937;
}

.panel-subtitle {
    color: #6b7280;
    font-size: 13px;
    margin-bottom: 18px;
}

.top-line {
    height: 6px;
    border-radius: 20px;
    background: linear-gradient(90deg, #005EB8 0%, #C40058 55%, #7A1F5C 100%);
    margin-bottom: 18px;
}

.main-title {
    font-size: 42px;
    font-weight: 850;
    color: #1f2937;
}

.main-subtitle {
    font-size: 16px;
    color: #667085;
    margin-bottom: 20px;
}

.kpi-card {
    background: linear-gradient(90deg, #C40058 0%, #C40058 2.5%, #ffffff 2.5%, #ffffff 100%);
    border: 1px solid #e6e9ef;
    border-radius: 18px;
    padding: 18px 20px 18px 24px;
    min-height: 118px;
    box-shadow: 0px 8px 22px rgba(31, 41, 55, 0.08);
}

.kpi-label {
    font-size: 13px;
    color: #667085;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 29px;
    color: #005EB8;
    font-weight: 850;
}

.kpi-note {
    font-size: 12px;
    color: #7b8190;
    margin-top: 8px;
}

.resultado {
    background: #ffffff;
    border: 1px solid #e6e9ef;
    border-left: 5px solid #005EB8;
    border-radius: 14px;
    padding: 15px 18px;
    color: #344054;
    line-height: 1.55;
    box-shadow: 0px 6px 16px rgba(31, 41, 55, 0.05);
    margin: 14px 0px 20px 0px;
}

#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def numero(valor):
    return f"{int(valor):,}".replace(",", ".")


def clasificar_edad(codigo):
    try:
        codigo = int(codigo)
    except:
        return "Edad desconocida"

    if 0 <= codigo <= 4:
        return "Mortalidad neonatal"
    if 5 <= codigo <= 6:
        return "Mortalidad infantil"
    if 7 <= codigo <= 8:
        return "Primera infancia"
    if 9 <= codigo <= 10:
        return "Niñez"
    if codigo == 11:
        return "Adolescencia"
    if 12 <= codigo <= 13:
        return "Juventud"
    if 14 <= codigo <= 16:
        return "Adultez temprana"
    if 17 <= codigo <= 19:
        return "Adultez intermedia"
    if 20 <= codigo <= 24:
        return "Vejez"
    if 25 <= codigo <= 28:
        return "Longevidad / Centenarios"
    return "Edad desconocida"


@st.cache_data
def cargar_datos():
    mortalidad = pd.read_excel("datos/NoFetal2019.xlsx", sheet_name="No_Fetales_2019", engine="openpyxl")
    divipola = pd.read_excel("datos/Divipola.xlsx", sheet_name="Hoja1", engine="openpyxl")
    codigos = pd.read_excel("datos/CodigosDeMuerte.xlsx", sheet_name="Final", header=8, engine="openpyxl")
    coordenadas = pd.read_excel("datos/Divipola.xlsx", sheet_name="Hoja3", header=[0, 1], engine="openpyxl")

    coordenadas.columns = ["COD_DEPTO", "DEPTO_COORD", "COD_MPIO", "MPIO_COORD", "TIPO", "LONGITUD", "LATITUD"]
    coordenadas = coordenadas.iloc[1:].copy()
    coordenadas["COD_DANE"] = pd.to_numeric(coordenadas["COD_MPIO"], errors="coerce")
    coordenadas["LONGITUD"] = coordenadas["LONGITUD"].astype(str).str.replace(",", ".", regex=False)
    coordenadas["LATITUD"] = coordenadas["LATITUD"].astype(str).str.replace(",", ".", regex=False)
    coordenadas["LONGITUD"] = pd.to_numeric(coordenadas["LONGITUD"], errors="coerce")
    coordenadas["LATITUD"] = pd.to_numeric(coordenadas["LATITUD"], errors="coerce")
    coordenadas = coordenadas[["COD_DANE", "LONGITUD", "LATITUD"]].dropna()

    mortalidad["COD_DANE"] = pd.to_numeric(mortalidad["COD_DANE"], errors="coerce")
    divipola["COD_DANE"] = pd.to_numeric(divipola["COD_DANE"], errors="coerce")

    mortalidad["COD_MUERTE"] = mortalidad["COD_MUERTE"].astype(str).str.strip().str.upper()
    mortalidad["COD_CIE3"] = mortalidad["COD_MUERTE"].str[:3]
    mortalidad["COD_CIE4"] = mortalidad["COD_MUERTE"].str[:4]

    codigos = codigos.rename(columns={
        "Nombre capítulo": "CAPITULO",
        "Código de la CIE-10 tres caracteres": "COD_CIE3",
        "Descripción  de códigos mortalidad a tres caracteres": "CAUSA_3",
        "Código de la CIE-10 cuatro caracteres": "COD_CIE4",
        "Descripcion  de códigos mortalidad a cuatro caracteres": "CAUSA_4"
    })

    codigos["COD_CIE3"] = codigos["COD_CIE3"].astype(str).str.strip().str.upper()
    codigos["COD_CIE4"] = codigos["COD_CIE4"].astype(str).str.strip().str.upper()
    codigos = codigos[["CAPITULO", "COD_CIE3", "CAUSA_3", "COD_CIE4", "CAUSA_4"]].drop_duplicates()

    datos = mortalidad.merge(
        divipola[["COD_DANE", "COD_DEPARTAMENTO", "DEPARTAMENTO", "COD_MUNICIPIO", "MUNICIPIO"]],
        on="COD_DANE",
        how="left"
    )

    datos = datos.merge(codigos, on=["COD_CIE3", "COD_CIE4"], how="left")
    datos = datos.merge(coordenadas, on="COD_DANE", how="left")

    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    datos["DEPARTAMENTO"] = datos["DEPARTAMENTO"].fillna("No identificado")
    datos["MUNICIPIO"] = datos["MUNICIPIO"].fillna("No identificado")
    datos["MES_NOMBRE"] = datos["MES"].map(meses)
    datos["MES_ORDEN"] = pd.to_numeric(datos["MES"], errors="coerce")
    datos["SEXO_TEXTO"] = datos["SEXO"].map({1: "Masculino", 2: "Femenino", 3: "Indeterminado"}).fillna("No informado")
    datos["CAUSA_FINAL"] = datos["CAUSA_4"].fillna(datos["CAUSA_3"]).fillna("Causa no identificada")
    datos["CAPITULO"] = datos["CAPITULO"].fillna("Capítulo no identificado")
    datos["GRUPO_EDAD_ANALISIS"] = datos["GRUPO_EDAD1"].apply(clasificar_edad)

    return datos


def kpi(titulo, valor, nota):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{titulo}</div>
        <div class="kpi-value">{valor}</div>
        <div class="kpi-note">{nota}</div>
    </div>
    """, unsafe_allow_html=True)


def lectura(texto):
    st.markdown(f'<div class="resultado">{texto}</div>', unsafe_allow_html=True)


def titulo_pagina(titulo, subtitulo):
    st.markdown('<div class="top-line"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-title">{titulo}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="main-subtitle">{subtitulo}</div>', unsafe_allow_html=True)


datos = cargar_datos()

st.sidebar.markdown('<div class="panel-title">Panel de selección</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="panel-subtitle">Navegue por las secciones del análisis.</div>', unsafe_allow_html=True)

pagina = st.sidebar.radio(
    "Menú principal",
    [
        "Resumen general",
        "Mapa territorial",
        "Muertes por mes",
        "Causas de muerte",
        "Violencia X95",
        "Sexo y edad",
        "Conclusiones"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Proyecto final**")
st.sidebar.write("Análisis estadístico de mortalidad no fetal en Colombia durante el año 2019.")


titulo_pagina(
    "Mortalidad en Colombia · 2019",
    "Análisis descriptivo de registros oficiales por territorio, mes, causa, sexo y grupo de edad."
)


if pagina == "Resumen general":
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi("Registros analizados", numero(len(datos)), "Muertes no fetales")
    with col2:
        kpi("Departamentos", numero(datos["DEPARTAMENTO"].nunique()), "Cobertura nacional")
    with col3:
        kpi("Municipios", numero(datos["MUNICIPIO"].nunique()), "Con registros")
    with col4:
        kpi("Causas CIE-10", numero(datos["COD_MUERTE"].nunique()), "Códigos identificados")

    st.markdown("### Datos integrados")
    st.dataframe(
        datos[["DEPARTAMENTO", "MUNICIPIO", "MES_NOMBRE", "SEXO_TEXTO", "GRUPO_EDAD_ANALISIS", "COD_MUERTE", "CAUSA_FINAL"]].head(20),
        use_container_width=True,
        hide_index=True
    )

    causa_principal = datos.groupby("CAUSA_FINAL").size().sort_values(ascending=False).index[0]
    depto_principal = datos.groupby("DEPARTAMENTO").size().sort_values(ascending=False).index[0]

    lectura(
        f"La base consolidada permite interpretar la mortalidad desde varias dimensiones. "
        f"En el total nacional, el departamento con mayor concentración es <b>{depto_principal}</b>, "
        f"y la causa más frecuente corresponde a <b>{causa_principal}</b>."
    )


elif pagina == "Mapa territorial":
    st.markdown("### Distribución territorial de muertes")

    mapa = datos.dropna(subset=["LATITUD", "LONGITUD"]).groupby(
        ["DEPARTAMENTO", "MUNICIPIO", "LATITUD", "LONGITUD"], as_index=False
    ).size().rename(columns={"size": "TOTAL"})

    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
        lat=mapa["LATITUD"],
        lon=mapa["LONGITUD"],
        mode="markers",
        marker=dict(
            size=(mapa["TOTAL"] / mapa["TOTAL"].max()) * 35 + 5,
            color=mapa["TOTAL"],
            colorscale=[[0, "#eef5fb"], [0.5, "#005EB8"], [1, "#C40058"]],
            showscale=True,
            colorbar=dict(title="Total")
        ),
        text=mapa["MUNICIPIO"] + "<br>" + mapa["DEPARTAMENTO"] + "<br>Total: " + mapa["TOTAL"].astype(str),
        hoverinfo="text"
    ))

    fig.update_layout(
        title="Distribución total de muertes por municipio",
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=4.5709, lon=-74.2973),
            zoom=4.8
        ),
        height=620,
        margin=dict(l=0, r=0, t=45, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

    deptos = datos.groupby("DEPARTAMENTO", as_index=False).size().rename(columns={"size": "TOTAL"}).sort_values("TOTAL", ascending=False)
    deptos_top = deptos.head(12).sort_values("TOTAL")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=deptos_top["TOTAL"],
        y=deptos_top["DEPARTAMENTO"],
        orientation="h",
        text=deptos_top["TOTAL"],
        marker=dict(color=deptos_top["TOTAL"], colorscale=[[0, "#eef5fb"], [0.5, "#005EB8"], [1, "#C40058"]])
    ))

    fig2.update_layout(
        title="Departamentos con mayor número de muertes registradas",
        xaxis_title="Total de muertes",
        yaxis_title="Departamento",
        template="plotly_white",
        height=500,
        showlegend=False
    )

    st.plotly_chart(fig2, use_container_width=True)

    principal = deptos.iloc[0]
    lectura(
        f"El departamento con mayor número de registros es <b>{principal['DEPARTAMENTO']}</b>, "
        f"con <b>{numero(principal['TOTAL'])}</b> muertes."
    )


elif pagina == "Muertes por mes":
    st.markdown("### Comportamiento mensual")

    mensual = datos.groupby(["MES_ORDEN", "MES_NOMBRE"], as_index=False).size().rename(columns={"size": "TOTAL"}).sort_values("MES_ORDEN")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mensual["MES_NOMBRE"],
        y=mensual["TOTAL"],
        mode="lines+markers",
        line=dict(color="#005EB8", width=3),
        marker=dict(color="#C40058", size=9),
        text=mensual["TOTAL"],
        hovertemplate="Mes: %{x}<br>Total: %{y}<extra></extra>"
    ))

    fig.update_layout(
        title="Total de muertes por mes en Colombia, 2019",
        xaxis_title="Mes",
        yaxis_title="Total de muertes",
        template="plotly_white",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    maximo = mensual.loc[mensual["TOTAL"].idxmax()]
    minimo = mensual.loc[mensual["TOTAL"].idxmin()]

    lectura(
        f"El mes con mayor número de registros es <b>{maximo['MES_NOMBRE']}</b>, "
        f"con <b>{numero(maximo['TOTAL'])}</b> casos. El menor registro se observa en "
        f"<b>{minimo['MES_NOMBRE']}</b>, con <b>{numero(minimo['TOTAL'])}</b> casos."
    )


elif pagina == "Causas de muerte":
    st.markdown("### Principales causas de muerte")

    causas = datos.groupby(["COD_MUERTE", "CAUSA_FINAL"], as_index=False).size().rename(columns={"size": "TOTAL"}).sort_values("TOTAL", ascending=False).head(10)

    st.dataframe(causas, use_container_width=True, hide_index=True)

    causas_grafico = causas.sort_values("TOTAL")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=causas_grafico["TOTAL"],
        y=causas_grafico["CAUSA_FINAL"],
        orientation="h",
        text=causas_grafico["TOTAL"],
        marker=dict(color=causas_grafico["TOTAL"], colorscale=[[0, "#eef5fb"], [0.5, "#005EB8"], [1, "#C40058"]])
    ))

    fig.update_layout(
        title="Diez principales causas de muerte",
        xaxis_title="Total de casos",
        yaxis_title="Causa de muerte",
        template="plotly_white",
        height=590,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    principal = causas.iloc[0]
    lectura(
        f"La causa con mayor frecuencia es <b>{principal['CAUSA_FINAL']}</b>, "
        f"código <b>{principal['COD_MUERTE']}</b>, con <b>{numero(principal['TOTAL'])}</b> registros."
    )


elif pagina == "Violencia X95":
    st.markdown("### Ciudades con mayor registro de homicidios X95")

    homicidios = datos[datos["COD_CIE3"] == "X95"].copy()

    top = homicidios.groupby(["MUNICIPIO", "DEPARTAMENTO"], as_index=False).size().rename(columns={"size": "TOTAL"}).sort_values("TOTAL", ascending=False).head(5)
    top["CIUDAD"] = top["MUNICIPIO"] + " - " + top["DEPARTAMENTO"]

    top_grafico = top.sort_values("TOTAL")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_grafico["TOTAL"],
        y=top_grafico["CIUDAD"],
        orientation="h",
        text=top_grafico["TOTAL"],
        marker=dict(color=top_grafico["TOTAL"], colorscale=[[0, "#eef5fb"], [0.5, "#005EB8"], [1, "#C40058"]])
    ))

    fig.update_layout(
        title="Top 5 ciudades con homicidios asociados al código X95",
        xaxis_title="Total de homicidios",
        yaxis_title="Ciudad",
        template="plotly_white",
        height=450,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Ciudades con menor mortalidad registrada")

    menores = datos[datos["MUNICIPIO"] != "No identificado"].groupby(
        ["MUNICIPIO", "DEPARTAMENTO"], as_index=False
    ).size().rename(columns={"size": "TOTAL"}).sort_values("TOTAL", ascending=True).head(10)

    menores["CIUDAD"] = menores["MUNICIPIO"] + " - " + menores["DEPARTAMENTO"]

    fig2 = go.Figure()
    fig2.add_trace(go.Pie(
        labels=menores["CIUDAD"],
        values=menores["TOTAL"],
        hole=0.42
    ))

    fig2.update_layout(
        title="Diez ciudades con menor número de muertes registradas",
        template="plotly_white",
        height=500
    )

    st.plotly_chart(fig2, use_container_width=True)

    if len(top) > 0:
        principal = top.iloc[0]
        lectura(
            f"Para el código X95, la ciudad con mayor registro es <b>{principal['MUNICIPIO']}</b> "
            f"en <b>{principal['DEPARTAMENTO']}</b>, con <b>{numero(principal['TOTAL'])}</b> casos."
        )


elif pagina == "Sexo y edad":
    st.markdown("### Comparación por sexo en departamentos con mayor registro")

    top_deptos = datos.groupby("DEPARTAMENTO").size().sort_values(ascending=False).head(15).index

    sexo = datos[datos["DEPARTAMENTO"].isin(top_deptos)].groupby(
        ["DEPARTAMENTO", "SEXO_TEXTO"], as_index=False
    ).size().rename(columns={"size": "TOTAL"})

    fig = go.Figure()

    for nombre_sexo, color in zip(["Masculino", "Femenino", "Indeterminado"], ["#005EB8", "#C40058", "#6B7280"]):
        base = sexo[sexo["SEXO_TEXTO"] == nombre_sexo]
        fig.add_trace(go.Bar(
            x=base["DEPARTAMENTO"],
            y=base["TOTAL"],
            name=nombre_sexo,
            marker_color=color
        ))

    fig.update_layout(
        title="Total de muertes por sexo y departamento",
        xaxis_title="Departamento",
        yaxis_title="Total de muertes",
        barmode="stack",
        template="plotly_white",
        height=520,
        xaxis_tickangle=-35
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Distribución por grupo de edad")

    orden_edad = [
        "Mortalidad neonatal", "Mortalidad infantil", "Primera infancia", "Niñez",
        "Adolescencia", "Juventud", "Adultez temprana", "Adultez intermedia",
        "Vejez", "Longevidad / Centenarios", "Edad desconocida"
    ]

    edad = datos.groupby("GRUPO_EDAD_ANALISIS", as_index=False).size().rename(columns={"size": "TOTAL"})
    edad["GRUPO_EDAD_ANALISIS"] = pd.Categorical(edad["GRUPO_EDAD_ANALISIS"], categories=orden_edad, ordered=True)
    edad = edad.sort_values("GRUPO_EDAD_ANALISIS")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=edad["GRUPO_EDAD_ANALISIS"],
        y=edad["TOTAL"],
        text=edad["TOTAL"],
        marker=dict(color=edad["TOTAL"], colorscale=[[0, "#eef5fb"], [0.5, "#005EB8"], [1, "#C40058"]])
    ))

    fig2.update_layout(
        title="Distribución de muertes por grupo de edad",
        xaxis_title="Grupo de edad",
        yaxis_title="Total de muertes",
        template="plotly_white",
        height=530,
        xaxis_tickangle=-35,
        showlegend=False
    )

    st.plotly_chart(fig2, use_container_width=True)

    principal = edad.loc[edad["TOTAL"].idxmax()]
    lectura(
        f"El grupo con mayor número de registros es <b>{principal['GRUPO_EDAD_ANALISIS']}</b>, "
        f"con <b>{numero(principal['TOTAL'])}</b> casos."
    )


elif pagina == "Conclusiones":
    depto = datos.groupby("DEPARTAMENTO").size().sort_values(ascending=False).index[0]
    causa = datos.groupby("CAUSA_FINAL").size().sort_values(ascending=False).index[0]
    edad = datos.groupby("GRUPO_EDAD_ANALISIS").size().sort_values(ascending=False).index[0]

    st.markdown("### Análisis")

    st.write(
        f"El análisis de mortalidad no fetal en Colombia durante 2019 evidencia que el departamento con mayor número "
        f"de registros es {depto}. La causa más frecuente corresponde a {causa}, y el grupo de edad con mayor concentración "
        f"es {edad}."
    )

    st.write(
        "Los resultados permiten observar que la mortalidad debe analizarse desde varias dimensiones. El componente territorial "
        "muestra concentración geográfica, la tendencia mensual permite revisar variaciones durante el año, las causas CIE-10 "
        "ordenan los eventos más frecuentes y la comparación por sexo y edad aporta una lectura demográfica."
    )

    st.write(
        "El proyecto transforma bases de datos oficiales en resultados visuales e interpretables, aplicando herramientas "
        "computacionales para la exploración de información estadística."
    )