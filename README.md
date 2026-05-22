# Proyecto final: Mortalidad en Colombia 2019

## Introducción

En este proyecto se realizó un análisis de los registros de mortalidad no fetal en Colombia durante el año 2019. Para el desarrollo del tablero se utilizaron herramientas computacionales que permitieron organizar, procesar y visualizar la información por departamento, municipio, sexo, grupo de edad y causa de muerte.

##Objetivo

Analizar e interpretar los datos de mortalidad no fetal en Colombia correspondientes al año 2019 mediante el uso de Python y herramientas de visualización de datos.

## Estructura del proyecto

Proyecto_Final

main.py
requirements.txt
README.md
datos/
-NoFetal2019.xlsx
-CodigosDeMuerte.xlsx
-Divipola.xlsx


## Requisitos

python -m pip install -r requirements.txt

## Ejecución local

python -m streamlit run main.py

# Visualizaciones incluidas

• Mapa de distribución territorial de muertes.
• Gráfico de líneas con el total de muertes por mes.
• Gráfico de barras de las ciudades con mayor número de homicidios asociados al código X95.
• Gráfico circular de ciudades con menor mortalidad registrada.
• Tabla de las principales causas de muerte.
• Comparación de muertes por sexo en los departamentos con mayor registro.
• Distribución de muertes por grupo de edad.

# Proceso realizado

Para el desarrollo del proyecto se trabajó con tres archivos principales: la base de mortalidad no fetal, los códigos CIE-10 y la información de Divipola. Posteriormente se realizó la integración de los datos mediante el código DANE y se organizaron las variables necesarias para la construcción de los gráficos y tablas.

# Herramientas utilizadas

• Python
• Streamlit
• Pandas
• Plotly
• OpenPyXL
• Visual Studio Code

# Interpretación general

El tablero permite observar el comportamiento de la mortalidad no fetal en Colombia durante el año 2019 desde diferentes perspectivas. A través de las visualizaciones se pueden identificar diferencias territoriales, variaciones mensuales, principales causas de muerte y distribución de registros según sexo y grupo de edad.

