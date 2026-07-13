import os
from dotenv import load_dotenv
import streamlit as st  
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser # <-- Quitamos la parte de JsonOutputParser para simplificar la salida
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, AIMessage #<-- Vamos a manejar tuplas de texto directas
#from langchain_text_splitters import RecursiveCharacterTextSplitter <-- Esto es para dividir textos largos
#from langchain_community.vectorstores import Chroma <-- Almacena, indexa y busca informacion
#from langchain_core.runnables import RunnablePassthrough <-- Pasa datos directamente a trves de una cadena 

from my_models import GEMINI_FLASH
# from detalles_image import DetallesImagen <-- esto era para analizar la imagen

# CARGAR LAS VARIABLES DEL ARCHIVO .ENV 
load_dotenv()

#LEER LA API KEY DESDE EL ENTORNO
gcp_api_key = os.getenv("GCP_API_KEY")

# CONFIGURACION DE LA INTERFAZ STREAMLIT
st.set_page_config(
    page_title="Asistente Virtual  -  SaludPlus",
    page_icon="",
    layout="centered" # <-- Estaba con la opcion wide, pero lo centre para mejor vista
)

st.title("Clinica Integral SaludPlus")
st.subheader("Asistente Virtual de Atencion al Paciente")
st.caption("Preguntame sobre nuestros servicios medicos")

#NOMBRE DEL ARCHIVO MAESTRO DEL HOSPITAL (CORREGIDO LE QUITE EL ACENTO)

PDF_INSTITUCIONAL = os.path.join(os.path.dirname(__file__), "Clinica Integral SaludPlus.pdf") # <-- Corregido para evitar el error de archivo no encontrado 

# 3. FUNCION PARA CARGAR EL PDF UNA SOLA VEZ (Cacheada para optimizar la velocidad)

@st.cache_data
def cargar_informacion_hospital():
    if not os.path.exists(PDF_INSTITUCIONAL):
        
        #Si el archivo no existe, creamos un aviso.
        return f"Error: No se encontro el archivo maestro en la ruta: {PDF_INSTITUCIONAL}"
    
    try:
        loader = PyPDFLoader(PDF_INSTITUCIONAL)
        paginas = loader.load()
        texto_completo = "\n".join(pagina.page_content for pagina in paginas)
        return texto_completo
    except Exception as e:
        return f"Error al procesar el documento maestro:{e}"
        
# Cargar el texto del hospital en memoria activa

informacion_hospital = cargar_informacion_hospital()

#Validar que el PDF se leyo correctamente antes de iniciar el chat

if "Error" in informacion_hospital: 
    st.error(informacion_hospital)
    st.info(f"Por favor, asegúrate de colocar el archivo PDF en la misma carpeta que este codigo de Python.")
    st.stop()  # Detener la ejecución si hay un error en la carga del PDF
    
# 4. CONFIGURACION DE GEMINI Y PROMPT CON MEMORIA CONVERSACIONAL
    
# CONFIGURACION DEL MODELO Y CADENA (LANGCHAIN)

# INSTANCIA LLM USANDO API KEY

llm = ChatGoogleGenerativeAI(
    api_key=gcp_api_key,
    model = "gemini-2.5-flash",
    temperature=0.3  # Temperatura baja para evitar que invente servicios
)

#Prompt del sistema adaptado al entorno medico institucional de Mexico

template_hospital = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""
         Eres el asistente virtual oficial de la Clinica Integral SaludPlus.
         Tu objetivo es atender de manera amable, empatica, clara y profesional a los pacientes y clientes. 
         
         Debes responder las dudas del usuario basandote EXCLUSIVAMENTE en la siguiente informacion oficial del Hospital:
         
         --------------------------
         {informacion_hospital}
         --------------------------
         REGLAS IMPORTANTES:
         
         1. Utiliza modismos y un tono adecuado para el publico Mexicano(ej. hablar de "citas", "consultorios", uso de "Usted" o "Tu" respetuoso)."f-string"
         2. Si la informacion solicitada (un horario especifico, costo,, una politica o un servicio, etc) No se encuentra explicitamente en el texto provisto, responde amablemente indicando que no tienes ese dato disponible en ese momento y sugiereles comunicarse directamente al telefono o ventanilla de la clinica. ¡NO inventes datos medicos, servicios ni horarios!
         3. Manten un tono servicil y compasivo, propio de un entorno de salud."f-string"                                                
        """
        
    ),
    # Espacio dinamico donde LangChain inyectara el historial de la conversacion actual (formato estructurado de tuplas nativas)
    MessagesPlaceholder(variable_name="historial"),
    ("user", "{pregunta_paciente}")
])

#Cadena LCEL limpia que procesa la entrada y devuelve texto directo
cadena_atencion = template_hospital | llm | StrOutputParser()
 
 # 4.1 MENU DE LA BARRA LATERAL (BOTON REINICIAR CHAT)
with st.sidebar:
     st.image("https://flaticon.com", width=100) # <-- Icono institucional decorativo
     st.header("Opciones de Sesion")
     st.write("Si deseas borrar la conversacion actual para iniciar una nueva consulta, presiona el siguiente boton:")
     
     # Boton que limpia la memoria de forma inmediata
     if st.button("Reiniciar Chat", use_container_width=True):
         if "mensajes_ui" in st.session_state: 
             del st.session_state.mensajes_ui
         if "historial_langchain" in st.session_state: 
             del st.session_state.historial_langchain
         st.success("¡Chat reiniciado con exito!")
         st.rerun()
         
 
 #5. ADMINISTRACION DEL HISTORIAL DE CHAT EN STREAMLIT
if "mensajes_ui" not in st.session_state:
     st.session_state.mensajes_ui = [] # <-- Para mostrar visualmente en Streamlit
if "historial_langchain" not in st.session_state:
    st.session_state.historial_langchain = [] # <-- Formato nativo de objetos LangChain para el modelo
    
# Mostrar un mensaje de bienvenida automatizado del hospital si el chat esta vacio
if len(st.session_state.mensajes_ui) == 0:
    bienvenida = "¡Hola! Bienvenido a la Clinica Integral SaludPlus. Soy tu asistente virtual y estoy aquí para ayudarte con tus consultas sobre nuestros servicios médicos. ¿En qué puedo ayudarte hoy?"
    st.session_state.mensajes_ui.append({"role": "assistant", "content": bienvenida})
    
#Renderizar el historial en pantalla
for msg in st.session_state.mensajes_ui:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
#6. CAJA DE TEXTO PARA PREGUNTAS DEL CLIENTE / PACIENTE

if pregunta := st.chat_input("Escribe tu pregunta aquí y presiona Enter..."):
    
    #Mostrar la pregunta del paciente en la UI
    with st.chat_message("user"):
        st.markdown(pregunta)
    st.session_state.mensajes_ui.append({"role": "user", "content": pregunta})
    
#Generar la respuesta medica institucional

with st.chat_message("assistant"):
    with st.spinner("Consultando la informacion interna de SaludPlus..."):
        
        try:
             #Invocar la cadena pasando el historial dinamico acumulado y la nueva pregunta
            respuesta_ai = cadena_atencion.invoke({
                "historial": st.session_state.historial_langchain,
                "pregunta_paciente": pregunta
           })
   
            #Desplegar la respuesta en la pantalla
            st.markdown(respuesta_ai)
        
            #Actualizar la UI
            st.session_state.mensajes_ui.append({"role": "assistant", "content": respuesta_ai})
        
            #Actualizar la memoria con el formato de tuplas nativo("user"/"assistant")compatible con pydantic v2
        
            st.session_state.historial_langchain.append(("user",pregunta)) # <-- Aqui quitamos HumanMessage(content=pregunta)
            st.session_state.historial_langchain.append(("assistant", respuesta_ai)) # <-- Aqui quitamos (AIMessage(content=respuesta_ai))
        
        except Exception as e:
            st.error(f"Tuvimos un problema al conectar con el sistea de atencion: {e}")
                                            
# NUEVA ESTRUCTURA DE TEXTO
#class Reportedocumento(BaseModel):
    #resumen_general: str = Field(description="Resumen general del documento")
    
#parser_json = JsonOutputParser(pydantic_object=DetallesImagen)

# PROMPT DEL ORQUESTADOR SIMPLIFICADO PARA WEB
#template_orquestador = ChatPromptTemplate.from_messages([
    #(
         #"system",
         #"""
         #Asume que eres un orquestador y analista de información experto.
         #Tu tarea es procesar el texto extraído de un documento PDF y generar un resumen claro, objetivo y sencillo.
         #Esta comunicación debe estar enfocada y priorizada para el público Mexicano, facilitando consultas posteriores.
         
         #{formato_salida}
         #"""
    #),
    #(
        #"user",
        #"Analiza el siguiente texto extraído del PDF y genera el reporte estructurado:\n\n{texto_entrada}"
    #)
#])

#promt_parcial = template_orquestador.partial(
    #formato_salida=parser_json.get_format_instructions()
#)

# Definición de la cadena LCEL limpia
#cadena_orquestador = promt_parcial | llm | parser_json

# LOGICA DE CARGA Y PROCESAMIENTO DE ARCHIVOS
#archivo_subido = st.file_uploader("Selecciona o arrastra tu archivo PDF aquí", type=["pdf"])
#if archivo_subido is not None:
    
    # Creamos un estado en streamlit para evitar que vuelva a procesar el pdf si el usuario interactúa con la UI
    #if "resultado_analisis" not in st.session_state:
        
        #with st.spinner("Procesando y analizando el contenido del PDF con Gemini Flash ..."):
            #try:
                # 1. Guardar temporalmente el archivo en disco para que PyPDFLoader pueda leerlo
                #temp_filename = f"temp_{archivo_subido.name}"
                #with open(temp_filename, "wb") as f:
                    #f.write(archivo_subido.read())
                    
                # 2. Extraer el texto de todas las páginas del PDF
                #loader = PyPDFLoader(temp_filename)
                #paginas = loader.load()
                #texto_completo = "\n".join([pagina.page_content for pagina in paginas])
                                                
                # 3. Eliminar el archivo temporal por seguridad
                #if os.path.exists(temp_filename):
                    #os.remove(temp_filename)
                
                # 4. Validar que el PDF tenga texto extraíble
                #if not texto_completo.strip():
                    #st.error("No se pudo extraer texto de este archivo. Asegúrate de que no sea un PDF escaneado sin OCR.")
                #else:
                    # 5. Invocar la cadena del orquestador de texto
                    #respuesta_json = cadena_orquestador.invoke({"texto_entrada": texto_completo})
                    #st.session_state.resultado_analisis = respuesta_json
                    #st.success("¡Análisis completado con éxito!")
        
            #except Exception as e:
                #st.error(f"Ocurrió un error al procesar el documento: {e}")
            
# INTERFAZ DE RESULTADOS VISUALES
#if "resultado_analisis" in st.session_state:
    #datos = st.session_state.resultado_analisis
    
    #st.markdown("___")
    #st.header("Resultados del Análisis")
    
    # Ajustamos el despliegue dinámicamente según las variables mapeadas en DetallesImagen
    #descripcion = datos.get("Descripcion de la imagen") or datos.get("descripcion") or list(datos.values())[0]
    #etiquetas = datos.get("Etiquetas") or datos.get("etiquetas") or []
    
    #col1, col2 = st.columns([2, 1])
    
    #with col1:
        #st.subheader("Resumen general")
        #st.info(descripcion)
        
    #with col2:
        #st.subheader("Palabras Clave / Etiquetas")
        #if isinstance(etiquetas, list):
            #for tag in etiquetas:
                #st.markdown(f" **{tag.strip()}**")
        #elif isinstance(etiquetas, str):
            #for tag in etiquetas.split(","):
                #st.markdown(f" **{tag.strip()}**")
        #else:
            #st.write("No se generaron etiquetas.")
            
    # Pestaña técnica para desarrolladores
    #with st.expander("Ver JSON completo (Salida de datos RAW)"):
        #st.json(datos)
