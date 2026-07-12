# AGENTE DE POLÍTICA DE ATENCIÓN AL CLIENTE, CAMBIOS Y DEVOLUCIONES MERCADO CENTRAL 24H (challenge Agente RAG)

---

### [Visita el agente RAG](https://challenge-agenterag-2346.streamlit.app/)

<p align="center">
<img src="/imgGif/animacion.gif">
</p>

<p align="center">
<img src="/imgGif/imagencel.gif" width="100%" height="auto">
</p>
---

## Asistente de Reembolsos MERCADO CENTRAL 24H - Chatbot Inteligente

### 📋 Descripción del Proyecto

Asistente de Reembolsos es un chatbot inteligente basado en **RAG (Retrieval-Augmented Generation)** que utiliza **Streamlit** y **Cohere** para proporcionar respuestas precisas sobre políticas de atención al cliente, cambios y devoluciones de Mercado Central 24h. El sistema está desplegado en **Streamlit Cloud**.

#### 🎯 Objetivo Principal
Proporcionar un asistente virtual que pueda responder preguntas sobre políticas de reembolso, plazos, procesos y documentación necesaria, extrayendo información directamente del [documento oficial de políticas de la empresa](https://cdn1.gnarususercontent.com.br/documents/6/internal/b9abdeaf-ffcb-46c4-8e1b-16935a594875.pdf).

**Documento referente implementado:**
[Mercado center documento pdf](https://cdn1.gnarususercontent.com.br/documents/6/internal/b9abdeaf-ffcb-46c4-8e1b-16935a594875.pdf)

### 🚀 Características Principales

- ✅ **Respuestas Inteligentes**: Utiliza RAG con Cohere para respuestas contextuales basadas en el documento oficial
- ✅ **Preguntas Rápidas**: Botones predefinidos para consultas frecuentes
- ✅ **Fuentes Citadas**: Muestra las fuentes de información utilizadas en cada respuesta
- ✅ **Historial de Conversación**: Mantiene el contexto de la conversación durante la sesión
- ✅ **Interfaz Amigable**: Diseño limpio y centrado en la experiencia del usuario
- ✅ **Carga Automática de Documentos**: Obtiene el PDF desde una URL pública

### 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Streamlit** | 1.59.1 | Framework de interfaz web |
| **LangChain** | 1.3.9 | Framework para aplicaciones LLM |
| **LangChain-Cohere** | 0.6.0 | Integración con Cohere |
| **LangChain-Community** | 0.4.2 | Componentes comunitarios de LangChain |
| **LangChain-Classic** | 1.0.8 | Componentes clásicos de LangChain |
| **PyMuPDF** | 1.28.0 | Procesamiento de PDFs |
| **FAISS-CPU** | 1.14.3 | Vectorstore para búsqueda de similitud |
| **Requests** | 2.33.1 | Cliente HTTP para descarga de PDFs |
| **Python-Dotenv** | 1.2.2 | Gestión de variables de entorno |

### 📦 Estructura del Proyecto

```
asistente-reembolsos/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias del proyecto
└── README.md             # Documentación
```

#### Arquitectura del Código


- **Configuración Centralizada**: Clase `Config` para todas las constantes
- **Modelos de Datos**: Clases `KnowledgeEntry` y `Message` para estructurar la información
- **Sistema RAG**: Clase `RAGSystem` que maneja la carga, procesamiento y consulta del PDF
- **Servicios**: Clase `ChatService` para la lógica de negocio
- **Gestión de Estado**: Clase `SessionManager` para manejar la sesión de Streamlit
- **Componentes UI**: Clase `ChatUI` para renderizar la interfaz
- **Inyección de Dependencias**: Inicialización centralizada en `initialize_dependencies()`

## ⚙️ Configuración e Instalación

### Prerrequisitos

1. **Cuenta de Cohere**: Obtén una API Key en [Cohere Dashboard](https://dashboard.cohere.ai/)
2. **Python 3.11+**: Asegúrate de tener Python instalado
3. **Git**: Para clonar el repositorio
   
#### Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/asistente-reembolsos.git
cd asistente-reembolsos

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
echo "COHERE_API_KEY=tu_api_key_aqui" > .env

# Ejecutar la aplicación
streamlit run app.py
```

### Despliegue en Streamlit Cloud

1. **Sube el código a GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Conecta con Streamlit Cloud**
   - Ve a [share.streamlit.io](https://share.streamlit.io)
   - Inicia sesión con tu cuenta de GitHub
   - Haz clic en "New app"
   - Selecciona el repositorio y la rama `main`
   - Especifica `app.py` como archivo principal

3. **Configura los Secretos**
   - En el dashboard de Streamlit Cloud, ve a "Settings" → "Secrets"
   - Agrega la variable secreta:
   ```
   COHERE_API_KEY = "tu_api_key_aqui"
   ```

4. **Despliega**
   - Haz clic en "Deploy"
   - La aplicación estará disponible en `https://tu-usuario-asistente-reembolsos.streamlit.app`

## 🎨 Interfaz de Usuario

### Funcionalidades

1. **Chat Principal**: Área central donde se muestra la conversación
2. **Preguntas Rápidas**: Botones con consultas predefinidas
   - ⏰ Plazos
   - 📝 Proceso
   - ⏳ Tiempo
   - ✅ Elegible
   - ❌ Cancelar
   - 📄 Docs
3. **Entrada de Chat**: Campo de texto para preguntas libres
4. **Fuentes de Información**: Expansión que muestra los documentos utilizados
5. **Estado del Sistema**: Indicador del modo de operación (RAG activo/básico)
6. **Limpiar Conversación**: Botón para reiniciar el chat

## 🔧 Configuración Técnica

### Variables de Entorno

| Variable | Descripción | Obligatoria |
|----------|-------------|-------------|
| `COHERE_API_KEY` | API Key de Cohere para embeddings y generación | Sí |

### Parámetros Configurables (Clase Config)

```python
class Config:
    PAGE_TITLE = "Asistente de Reembolsos"
    PDF_URL = "https://cdn1.gnarususercontent.com.br/documents/6/internal/b9abdeaf-ffcb-46c4-8e1b-16935a594875.pdf"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    SCORE_THRESHOLD = 0.3
    K_RETRIEVAL = 4
```

## 📚 Flujo de Trabajo

1. **Inicialización**:
   - Carga de variables de entorno
   - Configuración de la página Streamlit
   - Inicialización del sistema RAG

2. **Procesamiento del PDF**:
   - Descarga del PDF desde la URL
   - División en chunks
   - Generación de embeddings con Cohere
   - Creación del vectorstore FAISS

3. **Consulta**:
   - El usuario hace una pregunta
   - Búsqueda de documentos relevantes
   - Generación de respuesta con contexto
   - Presentación de fuentes citadas

4. **Visualización**:
   - Renderizado de mensajes
   - Mostrar fuentes en expander
   - Actualización del historial

## 🧪 Pruebas y Validación

### Modos de Operación

1. **Modo RAG (Recomendado)**:
   - El sistema carga el PDF correctamente
   - Responde con información contextual del documento
   - Muestra fuentes específicas

2. **Modo Fallback**:
   - El sistema no puede cargar el PDF
   - Responde con mensajes predefinidos
   - Muestra fuentes genéricas

### Verificación del Sistema

```python
# Verificar estado del RAG
if rag_system.vectorstore:
    st.success("✅ Sistema RAG activo")
else:
    st.warning("⚠️ Modo básico activo")
```

## 🚨 Manejo de Errores

El sistema implementa manejo robusto de errores en todos los niveles:

- **Carga de PDF**: Fallback a modo básico si falla la descarga
- **Consultas RAG**: Respuesta por defecto si hay error
- **API Cohere**: Captura de excepciones en la generación
- **Estado de Sesión**: Inicialización segura de variables

## 🔒 Seguridad y Buenas Prácticas

1. **Variables de Entorno**: API Keys no están hardcodeadas
2. **Manejo de Excepciones**: Try/except en operaciones críticas
3. **Validación de Entrada**: Sanitización de preguntas del usuario
4. **Documentación**: Código comentado y documentado
5. **Arquitectura Limpia**: Separación de responsabilidades

## 📊 Métricas y Monitoreo

El sistema incluye logs informativos en consola:

```python
print(f"✅ Sistema RAG inicializado correctamente")
print(f"📄 Total de chunks: {len(chunks)}")
print(f"❌ Error inicializando RAG: {e}")
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Notas Adicionales

### Limitaciones Conocidas

- El tiempo de respuesta puede variar según la carga de la API

### Mejoras Futuras

- [ ] Cache de respuestas frecuentes
- [ ] Soporte para múltiples documentos
- [ ] Exportación de conversación
- [ ] Análisis de sentimiento en preguntas
- [ ] Dashboard de métricas de uso

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autor

- Juan David Morales Fonnegra

## 🙏 Agradecimientos

- Kevin Torre Giraldo
- Alura (ONE: IMERSIÓN AGENTE IA)

---
**Desarrollado para Mercado Central 24h**

---

## Ejemplo de Preguntas que Responde

1. "¿Cuál es el plazo máximo para solicitar un reembolso?"
2. "¿Cómo solicito un reembolso?"
3. "¿Cuánto tiempo tarda en procesarse un reembolso?"
4. "¿Qué productos son elegibles para reembolso?"
5. "¿Puedo cancelar un reembolso ya solicitado?"
6. "¿Qué documentos necesito para el reembolso?"

---
**Nota**: Asegúrate de tener una API Key válida de Cohere para que el sistema funcione correctamente.
