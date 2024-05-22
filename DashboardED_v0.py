import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
from PIL import Image
import plotly.graph_objects as go
import os
import warnings
import sys
import platform
import sqlite3
warnings.filterwarnings('ignore')

st.set_page_config(page_title="ElectroDunas", page_icon=":bar_chart:",layout="wide")

#st.title(" :bar_chart: ElectroDunas")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

con = sqlite3.connect('Clientes.db')
df = pd.read_sql_query ('SELECT * FROM ClientesF;', con)
#print(df)

## Logo Tittle
image = Image.open('ElectroDunasLogo.jpg')
col1, col2 = st.columns((2))
with col1:
    st.image(image, width=600) 
with col2:
    st.title("")

## create new column fecha_ymd
df['fecha_ymd'] = df.iloc[:, 1].str[:10]

col1, col2 = st.columns((2))
df["fecha_ymd"] = pd.to_datetime(df["fecha_ymd"])

# Getting the min and max fecha_ymd 
startDate = pd.to_datetime(df["fecha_ymd"]).min()
endDate = pd.to_datetime(df["fecha_ymd"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Fecha Inicio", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("Fecha Fin", endDate))

df = df[(df["fecha_ymd"] >= date1) & (df["fecha_ymd"] <= date2)].copy()

# Filters
st.sidebar.header("Escoge tu filtro: ")
# Choose for Sector
sector = st.sidebar.multiselect("Escoge el Sector", df["SectorD"].unique())
if not sector:
    df2 = df.copy()
else:
    df2 = df[df["SectorD"].isin(sector)]

# Choose for Cliente
cliente = st.sidebar.multiselect("Escoge el Cliente", df2["ClientesD"].unique())
if not cliente:
    df3 = df2.copy()
else:
    df3 = df2[df2["ClientesD"].isin(cliente)]

# Filter the data based on sector and cliente
if not sector and not cliente:
    filtered_df = df
elif sector and not cliente:
    filtered_df = df[df["SectorD"].isin(sector)]
elif not sector and cliente:
    filtered_df = df[df["ClientesD"].isin(cliente)]
else:
    filtered_df = df3[df["SectorD"].isin(sector) & df3["ClientesD"].isin(cliente)]

cluster_df = filtered_df.groupby(by = ["Cluster"], as_index = False)["Active_energy"].sum()

# ClusterHistogram - SectorDonut -- Graphics
with col1:
    st.subheader("Detalles de Clusters")
    fig = px.bar(cluster_df, x = "Cluster", y = "Active_energy", text = ['${:,.2f}'.format(x) for x in cluster_df["Active_energy"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Detalles de Sectores")
    fig = px.pie(filtered_df, values = "Active_energy", names = "SectorD", hole = 0.5)
    fig.update_traces(text = filtered_df["SectorD"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns((2))

# ClusterHistogram - SectorDonut -- DataGrids
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Datos de Clusters"):
        st.write(cluster_df.style.background_gradient(cmap="Blues"))
        csv = cluster_df.to_csv(index = False).encode('utf-8')
        st.download_button("Descargar Datos", data = csv, file_name = "Cluster.csv", mime = "text/csv",
                            help = 'Click para descargar datos en formato CSV')

with cl2:
    with st.expander("Datos de Sectores"):
        sector = filtered_df.groupby(by = "SectorD", as_index = False)["Active_energy"].sum()
        st.write(sector.style.background_gradient(cmap="Oranges"))
        csv = sector.to_csv(index = False).encode('utf-8')
        st.download_button("Descargar Datos", data = csv, file_name = "Sector.csv", mime = "text/csv",
                        help = 'Click para descargar datos en formato CSV')

# TimeSeries        
filtered_df["month_year"] = filtered_df["fecha_ymd"].dt.to_period("M")
st.subheader('Análisis de Consumos')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Active_energy"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Active_energy", labels = {"Active_energy": "kWh"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("Datos de Consumos:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Descargar Datos', data = csv, file_name = "Consumos.csv", mime ='text/csv') 
       
# Treem based on Sector, Cluster, and Cliente
st.subheader("Detalle Sector - Cluster - Cliente")
fig3 = px.treemap(filtered_df, path = ["SectorD","Cluster","ClientesD"], values = "Active_energy",hover_data = ["Active_energy"],
                  color = "ClientesD")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

# Pie for Sector, and Cliente
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Detalles de Sectores")
    fig = px.bar(filtered_df, x = "Active_energy", y = "SectorD", orientation='h', 
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with chart2:
    st.subheader("Detalles de Clientes")
    fig = px.bar(filtered_df, x = "Active_energy", y = "ClientesD", orientation='h', 
                 template = "seaborn")
    st.write(fig)
    #st.plotly_chart(fig,use_container_width=True, height = 200)

