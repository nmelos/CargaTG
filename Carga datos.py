import sqlite3
import streamlit as st
import pandas as pd
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlalchemy as sa
import plotly.express as px
import pandas as pd
import os
import warnings
import sys
import platform
warnings.filterwarnings('ignore')

st.set_page_config(page_title="ElectroDunas", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Sample ElectroDunas")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

os.chdir('C:/Nelson/ANDES/Bimestre 8/Proyecto aplicado en analítica de datos/Semana 8/Prueba')
conn = sqlite3.connect('Clientes2.db')
query = conn.execute("SELECT * FROM ClientesF;")
cols = [column[0] for column in query.description]

results_df= pd.DataFrame.from_records(
    data = query.fetchall(),
    columns = cols
)

st.dataframe(results_df)