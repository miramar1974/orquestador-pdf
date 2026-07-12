import os
import streamlit as st 
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough

from my_models import GEMINI_FLASH
from detalles_image import DetallesImagen

# CONFIGURACION DE LA PAGINA STREAMLIT
st.set_page_config(
    page_title="Orquestador de Documentos AI",
    page_icon="",
    layout="wide"
)

st.title("Orquestador Inteligente de Documentos PDF")
st.subheader("Análisis objetivo y resúmenes ejecutivos enfocados al público Mexicano.")

# CONFIGURACION DEL MODELO Y CADENA (LANGCHAIN)
# INSTANCIA LLM USANDO API KEY
llm = ChatGoogleGenerativeAI(
    api_key="AQ.Ab8RN6IKoWhiQzpsOoy7ugCWFKJDfLyNxAJHRitNOF5U7ezzeA",
    model=GEMINI_FLASH,
    temperature=0.2  # Flexibilidad para resúmenes redactados en forma natural
)

parser_json = JsonOutputParser(pydantic_object=DetallesImagen)

# PROMPT DEL ORQUESTADOR SIMPLIFICADO PARA WEB
template_orquestador = ChatPromptTemplate.from_messages([
    (
         "system",
         """
         Asume que eres un orquestador y analista de información experto.
         Tu tarea es procesar el texto extraído de un documento PDF y generar un resumen claro, objetivo y sencillo.
         Esta comunicación debe estar enfocada y priorizada para el público Mexicano, facilitando consultas posteriores.
         
         {formato_salida}
         """
    ),
    (
        "user",
        "Analiza el siguiente texto extraído del PDF y genera el reporte estructurado:\n\n{texto_entrada}"
    )
])

promt_parcial = template_orquestador.partial(
    formato_salida=parser_json.get_format_instructions()
)

# Definición de la cadena LCEL limpia
cadena_orquestador = promt_parcial | llm | parser_json

# LOGICA DE CARGA Y PROCESAMIENTO DE ARCHIVOS
archivo_subido = st.file_uploader("Selecciona o arrastra tu archivo PDF aquí", type=["pdf"])
if archivo_subido is not None:
    
    # Creamos un estado en streamlit para evitar que vuelva a procesar el pdf si el usuario interactúa con la UI
    if "resultado_analisis" not in st.session_state:
        
        with st.spinner("Procesando y analizando el contenido del PDF con Gemini Flash ..."):
            try:
                # 1. Guardar temporalmente el archivo en disco para que PyPDFLoader pueda leerlo
                temp_filename = f"temp_{archivo_subido.name}"
                with open(temp_filename, "wb") as f:
                    f.write(archivo_subido.read())
                    
                # 2. Extraer el texto de todas las páginas del PDF
                loader = PyPDFLoader(temp_filename)
                paginas = loader.load()
                texto_completo = "\n".join([pagina.page_content for pagina in paginas])
                                                
                # 3. Eliminar el archivo temporal por seguridad
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                
                # 4. Validar que el PDF tenga texto extraíble
                if not texto_completo.strip():
                    st.error("No se pudo extraer texto de este archivo. Asegúrate de que no sea un PDF escaneado sin OCR.")
                else:
                    # 5. Invocar la cadena del orquestador de texto
                    respuesta_json = cadena_orquestador.invoke({"texto_entrada": texto_completo})
                    st.session_state.resultado_analisis = respuesta_json
                    st.success("¡Análisis completado con éxito!")
        
            except Exception as e:
                st.error(f"Ocurrió un error al procesar el documento: {e}")
            
# INTERFAZ DE RESULTADOS VISUALES
if "resultado_analisis" in st.session_state:
    datos = st.session_state.resultado_analisis
    
    st.markdown("___")
    st.header("Resultados del Análisis")
    
    # Ajustamos el despliegue dinámicamente según las variables mapeadas en DetallesImagen
    descripcion = datos.get("Descripcion de la imagen") or datos.get("descripcion") or list(datos.values())[0]
    etiquetas = datos.get("Etiquetas") or datos.get("etiquetas") or []
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Resumen general")
        st.info(descripcion)
        
    with col2:
        st.subheader("Palabras Clave / Etiquetas")
        if isinstance(etiquetas, list):
            for tag in etiquetas:
                st.markdown(f" **{tag.strip()}**")
        elif isinstance(etiquetas, str):
            for tag in etiquetas.split(","):
                st.markdown(f" **{tag.strip()}**")
        else:
            st.write("No se generaron etiquetas.")
            
    # Pestaña técnica para desarrolladores
    with st.expander("Ver JSON completo (Salida de datos RAW)"):
        st.json(datos)
