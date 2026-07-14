# Clínica Integral SaludPlus 🏥

Este proyecto implementa un sistema **RAG (Retrieval-Augmented Generation)** diseñado para responder preguntas utilizando exclusivamente la documentación interna (Manual de Operaciones, Políticas y Guías Integrales) de la empresa ficticia **Clínica Integral SaludPlus**.

El aplicativo resuelve dudas sobre políticas de privacidad, derechos ARCO, consultas y turnos, entrega de resultados, políticas de cancelación, devoluciones, convenios, alertas de seguridad, directorio de sedes regionales, catálogo de medicamentos exclusivos, costos de servicios, horarios, facturación electrónica, traslados en ambulancia, descuentos especiales y guía de admisión.

---

## 🎯 Objetivo

Desarrollar e implementar un asistente virtual inteligente capaz de:
*   **Consultar** minuciosamente la documentación interna de la clínica.
*   **Analizar** el documento para extraer la respuesta correcta de forma exacta.
*   **Generar** respuestas fundamentadas y validadas únicamente en dicho archivo.
*   **Evitar alucinaciones** o respuestas inventadas si la información no está contenida en el documento.

---

## 📈 Estado del Proyecto

🚀 **Finalizado, desplegado y en producción.**

---

## ✨ Características

*   **Procesamiento Inteligente:** Lectura automatizada de archivos PDF (Manual de Operaciones, Políticas y Guías).
*   **Generación Avanzada:** Respuestas creadas utilizando modelos de **Google Gemini**.
*   **Control de Información:** Respuestas limitadas estrictamente al contexto del PDF indexado.
*   **Interfaz Gráfica:** Frontend web moderno, rápido y amigable desarrollado con **Streamlit**.

---

## 🏗️ Arquitectura del Sistema

El proyecto se basa en una arquitectura **RAG (Retrieval-Augmented Generation)**. El flujo operativo sigue este orden:

1. El usuario realiza una consulta desde la interfaz web.
2. El módulo *Retriever* busca la respuesta en el documento PDF.
3. Si el tema no está en el PDF, se invita al usuario a reformular su pregunta.
4. Si la información existe, **Google Gemini** procesa el contexto y genera la respuesta.
5. La respuesta estructurada se muestra directamente en la pantalla.

### Diagrama de Flujo

```text
       [ Inicio ]
           │
           ▼
        Usuario
           │
           ▼
   Interfaz Streamlit
           │
           ▼
       Retriever
           │
           ▼
     ¿Información 
     en el PDF? ──( No )──► [ Invitación a reformular ]
           │                         │
        ( Sí )                       ▼
           │                Interfaz Streamlit
           ▼
     Google Gemini
           │
           ▼
   Respuesta en Pantalla
           │
           ▼
        [ Fin ]
```

---

## 🛠️ Tecnologías Utilizadas

*   **Lenguaje:** Python 3.14.6
*   **Framework Web:** Streamlit
*   **Orquestación LLM:** LangChain
*   **Modelo de Lenguaje:** Google Gemini
*   **Gestión de Entorno:** Python-dotenv

---

## ⚙️ Instalación y Configuración

Sigue estos pasos para clonar el proyecto y configurar tu entorno local:

### 1. Clonar el repositorio
```bash
git clone https://github.com/miramar1974/orquestador-pdf
cd orquestador-pdf
```

### 2. Crear un entorno virtual
```bash
python -m venv .venv
```

*Activa el entorno virtual según tu sistema operativo:*
*   **Windows:** `.venv\Scripts\activate`
*   **macOS/Linux:** `source .venv/bin/activate`

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo llamado `.env` en la raíz del proyecto y añade tu clave de API de Gemini:
```env
GEMINI_API_KEY=tu_clave_api_key_aquí
```

---

## 🚀 Ejecución

Una vez instaladas las dependencias y configurada tu API Key, inicializa la aplicación web con el siguiente comando:

```bash
streamlit run app_web.py
```

Inmediatamente se abrirá tu explorador web con la interfaz gráfica. Desde allí podrás interactuar con el sistema y realizar preguntas acerca de los servicios de la **Clínica Integral SaludPlus**.

---

## 💡 Ejemplos de Consultas

Puedes probar el asistente con preguntas como las siguientes:
*   *¿Costo de consultas?*
*   *¿Reembolsos?*
*   *¿Agendar consultas?*
*   *¿Traslados en ambulancia?*
*   *¿Política de privacidad del paciente?*
*   *¿Entrega de resultados?*
*   *¿Política de cancelaciones?*
*   *¿Devoluciones?*
*   *¿Guía de convenios?*
*   *¿Sedes alternas?*
*   *¿Costo de imagenología avanzada?*
*   *¿Facturación electrónica?*
*   *¿Política de descuentos?*
*   *¿Guía de admisión?*
*   *¿Protocolos de alta médica?*

---

## 📸 Capturas de Pantalla

*(Coloca aquí las imágenes de tu aplicación una vez que las subas a tu repositorio)*

---

## 📸 Capturas de Pantalla

| Interfaz Principal | Consulta con Contexto | Respuesta del Sistema |
| :---: | :---: | :---: |
| ![Interfaz Principal](assets/screenshot_principal.png) | ![Consulta con Contexto](assets/screenshot_contexto.png) | ![Respuesta del Sistema](assets/screenshot_respuesta.png) |

---

## 👤 Autor

Desarrollado con ❤️ por **Miguel Ibarra Miramar**
