import pandas as pd
import streamlit as st
import io

# Configuración de la interfaz
st.set_page_config(
    page_title="Procesador de Conexiones",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Procesador de Conexiones por Agente")
st.write("Sube tu archivo de Excel para generar el layout automáticamente. **El archivo no se guarda en el servidor**, la carga es 100% temporal.")

# 1. Componente para subir el archivo (Carga temporal en memoria)
uploaded_file = st.file_uploader("Elige tu archivo Excel (ej. conexiones.xlsx)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # 2. Cargar datos del archivo subido en memoria
        df = pd.read_excel(uploaded_file, sheet_name=0)
        
        columnas_requeridas = ['Agente', 'Fecha Desde', 'Fecha Hasta']
        if not all(col in df.columns for col in columnas_requeridas):
            st.error(f"El archivo debe contener las columnas: {', '.join(columnas_requeridas)}")
        else:
            # 3. Procesar datos (Mínimo entrada, Máximo salida)
            df['Fecha_Dia'] = pd.to_datetime(df['Fecha Desde']).dt.date

            layout = df.groupby(['Agente', 'Fecha_Dia']).agg(
                Fecha_Hora_Entrada=('Fecha Desde', 'min'),
                Fecha_Hora_Salida=('Fecha Hasta', 'max')
            ).reset_index()

            st.success("¡Archivo procesado con éxito!")
            
            # Vista previa en la app
            st.subheader("Vista previa del Layout:")
            st.dataframe(layout.head(15), use_container_width=True)
            
            # 4. Generar el Excel de descarga en memoria RAM (sin guardar archivos en disco)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                layout.to_excel(writer, index=False)
            buffer.seek(0)
            
            # 5. Botón de descarga
            st.download_button(
                label="📥 Descargar Layout Procesado",
                data=buffer,
                file_name="layout_conexiones_procesado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")