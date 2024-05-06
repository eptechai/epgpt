import os

import time
import pandas as pd
import streamlit as st


st.title("Sistema de Analisis  Financiero y Tecnico Interventoria Alumbrado Publico De Soledad")


RAWDATAPATH = "/app"

aire_dict = {}

def save_uploadedfile(uploadedfile):
    global RAWDATAPATH
    with open(os.path.join(RAWDATAPATH, uploadedfile.name), "wb") as f:

        f.write(uploadedfile.getbuffer())

        with st.spinner(text="Cargando . . ."):
            time.sleep(3)

    bala = os.path.join(RAWDATAPATH, uploadedfile.name)

    print(bala)

    return bala

tab1, tab2, tab3, tab4 = st.tabs(["Catastro", "Facturación", "Recaudo", "Resultado"])


if 'data' not in st.session_state:
    st.session_state.data = {}

with tab1:
    file_to_be_uploaded = st.file_uploader("Agregue el archivo para el catastro de Air-E", type=["CSV"])
    if st.button("Carga Catastro"):
        if file_to_be_uploaded is not None:

            input_files = save_uploadedfile(file_to_be_uploaded)
            st.write(f"File is uploaded in {input_files}")

            # Audio Files Listening
            df = pd.read_csv(input_files, sep="|", encoding = "ISO-8859-1")
            st.write(df.head())
            st.header('Usuarios De Air-E')
            st.write(df["DEUDA_CORRIENTE"].sum())
            summary_group_series = df.groupby(['COD_TARIFA', 'ESTADO_SUMINISTRO'])["ESTADO_SUMINISTRO"].count()
            summary_df = summary_group_series.unstack(level='COD_TARIFA')
            all_columns = list(summary_df)

            summary_df = summary_df[all_columns].fillna(0).astype(int)
            st.table(summary_df)

            st.session_state.data[1]  = df
            st.write(st.session_state.data)

with tab2:
    file_to_be_uploaded = st.file_uploader("Agregue el archivo para la facturacion de Air-E", type=["CSV"])

    if st.button("Carga Facturacion"):
        input_files = save_uploadedfile(file_to_be_uploaded)
        df = pd.read_csv(input_files, sep="|", encoding = "ISO-8859-1")
        st.write(df.head())
        st.write(df["IMPORTE"].sum())
        st.write(df["VALOR_RECIBO"].sum())
        st.session_state.data['2']  = df
        st.write(st.session_state.data)

with tab3:
    file_to_be_uploaded = st.file_uploader("Agregue el archivo para la Recaudo de Air-E", type=["CSV"])

    if st.button("Carga Recaudo"):
        input_files = save_uploadedfile(file_to_be_uploaded)
        df = pd.read_csv(input_files, sep="|", encoding = "ISO-8859-1")
        st.write(df.head())
        st.write(df["IMPORTE"].sum())
        st.write(df["VALOR_RECIBO"].sum())
        
        st.session_state.data['3']  = df
        st.write(st.session_state.data)

