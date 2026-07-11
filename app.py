import streamlit as st
import time
import random
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
import requests
from io import BytesIO
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv
import os

# ============================================================
# CARGA DE VARIABLES DE ENTORNO
# ============================================================

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# ============================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================

class Config:
    """Configuración de la aplicación"""
    PAGE_TITLE = "Asistente de Reembolsos"
    PAGE_ICON = "💬"
    LAYOUT = "centered"
    TYPING_DELAY_MIN = 0.5
    TYPING_DELAY_MAX = 1.0
    
    # Mensajes del sistema
    WELCOME_MESSAGE = "¡Hola! Pregunta sobre políticas, plazos y procesos de reembolso"
    DEFAULT_RESPONSE = "No tengo información específica sobre eso. Contacta con atención al cliente."
    DEFAULT_SOURCE = "Atención al Cliente"
    
    # Configuración RAG
    PDF_URL = "https://cdn1.gnarususercontent.com.br/documents/6/internal/b9abdeaf-ffcb-46c4-8e1b-16935a594875.pdf"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    SCORE_THRESHOLD = 0.3
    K_RETRIEVAL = 4

# ============================================================
# MODELO DE DATOS
# ============================================================

class KnowledgeEntry:
    """Entrada de conocimiento con respuesta y fuentes"""
    
    def __init__(self, respuesta: str, fuentes: List[str]):
        self.respuesta = respuesta
        self.fuentes = fuentes
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización"""
        return {
            "respuesta": self.respuesta,
            "fuentes": self.fuentes
        }

class Message:
    """Modelo de mensaje del chat"""
    
    def __init__(self, rol: str, contenido: str, fuentes: Optional[List[str]] = None):
        self.rol = rol
        self.contenido = contenido
        self.fuentes = fuentes or []
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para almacenar en session_state"""
        return {
            "rol": self.rol,
            "contenido": self.contenido,
            "fuentes": self.fuentes
        }

# ============================================================
# SISTEMA RAG (REEMPLAZA AL REPOSITORIO ESTÁTICO)
# ============================================================

class RAGSystem:
    """Sistema de RAG con Cohere para respuestas inteligentes"""
    
    def __init__(self):
        self.vectorstore = None
        self.retriever = None
        self.document_chain = None
        self._initialize_rag()
    
    def _initialize_rag(self):
        """Inicializa el sistema RAG cargando el PDF y creando el vectorstore"""
        try:
            # Cargar y procesar PDF
            docs = self._load_pdf()
            
            if docs:
                # Crear chunks
                chunks = self._create_chunks(docs)
                
                # Crear embeddings y vectorstore
                self._create_vectorstore(chunks)
                
                # Configurar retriever
                self._configure_retriever()
                
                # Configurar chain de documentos
                self._configure_document_chain()
                
                print(f"✅ Sistema RAG inicializado correctamente")
                print(f"📄 Total de chunks: {len(chunks)}")
            else:
                print("❌ No se pudo cargar el PDF, usando modo fallback")
                
        except Exception as e:
            print(f"❌ Error inicializando RAG: {e}")
            self.vectorstore = None
    
    def _load_pdf(self) -> List:
        """Carga el PDF desde la URL"""
        try:
            response = requests.get(Config.PDF_URL)
            response.raise_for_status()
            
            with NamedTemporaryFile(delete=True, suffix='.pdf') as temp_file:
                temp_file.write(response.content)
                temp_file.flush()
                
                loader = PyMuPDFLoader(temp_file.name)
                docs = loader.load()
                
            print(f"✅ PDF procesado: {len(docs)} páginas")
            return docs
            
        except Exception as e:
            print(f"❌ Error cargando PDF: {e}")
            return []
    
    def _create_chunks(self, docs) -> List:
        """Divide los documentos en chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(docs)
        print(f"✂️ Total de chunks: {len(chunks)}")
        return chunks
    
    def _create_vectorstore(self, chunks):
        """Crea el vectorstore con embeddings de Cohere"""
        embeddings = CohereEmbeddings(
            model="embed-multilingual-v3.0",
            cohere_api_key=COHERE_API_KEY
        )
        
        self.vectorstore = FAISS.from_documents(chunks, embeddings)
        print("✅ Vectorstore creado")
    
    def _configure_retriever(self):
        """Configura el retriever con umbral de similitud"""
        if self.vectorstore:
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={
                    "score_threshold": Config.SCORE_THRESHOLD,
                    "k": Config.K_RETRIEVAL
                }
            )
            print("✅ Retriever configurado")
    
    def _configure_document_chain(self):
        """Configura la cadena de documentos con el prompt RAG"""
        prompt_rag = ChatPromptTemplate([
            ("system",
                """Eres el especialista en Políticas de atención al cliente, cambios y devoluciones de la empresa Mercado Central de las 24H.
                Responde siempre utilizando los conocimientos de las bases de datos pasadas a ti.
                Si no hay información sobre la pregunta en los datos, responde solo 'No lo sé'.
                """
            ),
            ("human", "Contexto: {context}\nPregunta del empleado: {input}")
        ])
        
        llm = ChatCohere(
            model="command-a-03-2025",
            cohere_api_key=COHERE_API_KEY,
            temperature=0.7
        )
        
        self.document_chain = create_stuff_documents_chain(llm, prompt_rag)
        print("✅ Document chain configurada")
    
    def query(self, pregunta: str) -> Dict:
        """Realiza una consulta al sistema RAG"""
        if not self.retriever or not self.document_chain:
            return {
                "respuesta": Config.DEFAULT_RESPONSE,
                "citaciones": [],
                "documentos_encontrados": False,
                "fuentes": [Config.DEFAULT_SOURCE]
            }
        
        try:
            # Buscar documentos relevantes
            documentos_relacionados = self.retriever.invoke(pregunta)
            
            if not documentos_relacionados:
                return {
                    "respuesta": "No lo sé",
                    "citaciones": [],
                    "documentos_encontrados": False,
                    "fuentes": ["No se encontraron documentos relevantes"]
                }
            
            # Generar respuesta
            answer = self.document_chain.invoke({
                "input": pregunta,
                "context": documentos_relacionados
            })
            
            # Verificar si la respuesta es "No lo sé"
            if answer.rstrip(".!?") == "No lo sé":
                return {
                    "respuesta": "No lo sé",
                    "citaciones": [],
                    "documentos_encontrados": False,
                    "fuentes": ["No se encontró información relevante en los documentos"]
                }
            
            # Extraer fuentes de los documentos
            fuentes = []
            for doc in documentos_relacionados[:3]:  # Limitar a 3 fuentes
                source = doc.metadata.get('source', 'Documento')
                page = doc.metadata.get('page', '')
                if page:
                    fuentes.append(f"{source} - Página {page}")
                else:
                    fuentes.append(source)
            
            return {
                "respuesta": answer,
                "citaciones": documentos_relacionados,
                "documentos_encontrados": True,
                "fuentes": fuentes if fuentes else ["Política de Reembolsos - Documento oficial"]
            }
            
        except Exception as e:
            print(f"❌ Error en consulta RAG: {e}")
            return {
                "respuesta": "Ocurrió un error al procesar tu pregunta. Por favor, intenta de nuevo.",
                "citaciones": [],
                "documentos_encontrados": False,
                "fuentes": ["Error en el sistema"]
            }

# ============================================================
# SERVICIOS
# ============================================================

class ChatService:
    """Servicio principal del chat usando RAG"""
    
    def __init__(self, rag_system: RAGSystem):
        self.rag_system = rag_system
    
    def process_question(self, question: str) -> KnowledgeEntry:
        """Procesa una pregunta usando el sistema RAG"""
        # Simular tiempo de procesamiento
        self._simulate_processing()
        
        # Consultar al sistema RAG
        result = self.rag_system.query(question)
        
        # Crear entrada de conocimiento con la respuesta y fuentes
        return KnowledgeEntry(
            respuesta=result["respuesta"],
            fuentes=result.get("fuentes", [Config.DEFAULT_SOURCE])
        )
    
    @staticmethod
    def _simulate_processing():
        """Simula el tiempo de procesamiento de la respuesta"""
        time.sleep(random.uniform(Config.TYPING_DELAY_MIN, Config.TYPING_DELAY_MAX))

class SessionManager:
    """Gestiona el estado de la sesión en Streamlit"""
    
    @staticmethod
    def initialize():
        """Inicializa el estado de la sesión si no existe"""
        if "mensajes" not in st.session_state:
            st.session_state.mensajes = []
        if "rag_system" not in st.session_state:
            st.session_state.rag_system = RAGSystem()
    
    @staticmethod
    def add_message(message: Message):
        """Agrega un mensaje al historial de la sesión"""
        st.session_state.mensajes.append(message.to_dict())
    
    @staticmethod
    def get_messages() -> List[Dict]:
        """Obtiene todos los mensajes del historial"""
        return st.session_state.mensajes
    
    @staticmethod
    def clear():
        """Limpia el historial de mensajes"""
        st.session_state.mensajes = []
    
    @staticmethod
    def get_rag_system() -> RAGSystem:
        """Obtiene el sistema RAG"""
        return st.session_state.rag_system

# ============================================================
# COMPONENTES DE UI
# ============================================================

class ChatUI:
    """Componentes de la interfaz de usuario"""
    
    def __init__(self, chat_service: ChatService, session_manager: SessionManager):
        self.chat_service = chat_service
        self.session_manager = session_manager
        
        # Preguntas rápidas predefinidas
        self.quick_questions = [
            ("⏰ Plazos", "¿Cuál es el plazo máximo para solicitar un reembolso?"),
            ("📝 Proceso", "¿Cómo solicito un reembolso?"),
            ("⏳ Tiempo", "¿Cuánto tiempo tarda en procesarse un reembolso?"),
            ("✅ Elegible", "¿Qué productos son elegibles para reembolso?"),
            ("❌ Cancelar", "¿Puedo cancelar un reembolso ya solicitado?"),
            ("📄 Docs", "¿Qué documentos necesito para el reembolso?")
        ]
    
    def render_header(self):
        """Renderiza el encabezado de la aplicación"""
        st.title(f"{Config.PAGE_ICON} {Config.PAGE_TITLE}")
        st.caption(Config.WELCOME_MESSAGE)
        
        # Mostrar estado del sistema RAG
        with st.expander("ℹ️ Estado del sistema"):
            rag = self.session_manager.get_rag_system()
            if rag.vectorstore:
                st.success("✅ Sistema RAG activo - Utilizando inteligencia artificial para respuestas")
                st.info("📚 El asistente usa el documento oficial de políticas de reembolso")
            else:
                st.warning("⚠️ Sistema en modo básico - Usando respuestas predefinidas")
    
    def render_messages(self):
        """Renderiza todos los mensajes del historial"""
        messages = self.session_manager.get_messages()
        
        for msg in messages:
            with st.chat_message(msg["rol"]):
                st.markdown(msg["contenido"])
                self._render_sources(msg.get("fuentes", []))
    
    def render_quick_questions(self):
        """Renderiza los botones de preguntas rápidas"""
        st.markdown("---")
        st.caption("⚡ Preguntas rápidas:")
        
        # Organizar en columnas (2 filas x 3 columnas)
        cols = st.columns(3)
        for idx, (label, question) in enumerate(self.quick_questions):
            col = cols[idx % 3]
            with col:
                if st.button(label, key=f"quick_{idx}", use_container_width=True):
                    self._handle_question(question)
    
    def render_chat_input(self):
        """Renderiza el input de chat"""
        question = st.chat_input("Escribe tu pregunta sobre reembolsos...")
        if question:
            self._handle_question(question)
    
    def render_clear_button(self):
        """Renderiza el botón para limpiar el chat"""
        st.divider()
        if st.button("🗑️ Limpiar conversación", use_container_width=True):
            self.session_manager.clear()
            st.rerun()
    
    def _handle_question(self, question: str):
        """Maneja una pregunta del usuario"""
        # Agregar mensaje del usuario
        user_message = Message(rol="user", contenido=question)
        self.session_manager.add_message(user_message)
        
        # Procesar y obtener respuesta
        with st.spinner("🤔 Analizando documentos..."):
            entry = self.chat_service.process_question(question)
        
        # Agregar respuesta del asistente
        assistant_message = Message(
            rol="assistant",
            contenido=entry.respuesta,
            fuentes=entry.fuentes
        )
        self.session_manager.add_message(assistant_message)
        
        # Recargar la UI
        st.rerun()
    
    @staticmethod
    def _render_sources(fuentes: List[str]):
        """Renderiza las fuentes de información"""
        if fuentes and fuentes != [Config.DEFAULT_SOURCE]:
            with st.expander("📚 Ver fuentes de información"):
                for fuente in fuentes:
                    st.write(f"• {fuente}")
        elif fuentes and fuentes != ["No se encontraron documentos relevantes"]:
            with st.expander("📚 Ver fuentes de información"):
                for fuente in fuentes:
                    st.write(f"• {fuente}")

# ============================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================

def configure_app():
    """Configura la aplicación Streamlit"""
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        page_icon=Config.PAGE_ICON,
        layout=Config.LAYOUT
    )

# ============================================================
# INICIALIZACIÓN DE DEPENDENCIAS (Inyección de dependencias)
# ============================================================

def initialize_dependencies() -> Tuple[ChatService, SessionManager, ChatUI]:
    """Inicializa todas las dependencias de la aplicación"""
    # Inicializar sesión y RAG
    session_manager = SessionManager()
    session_manager.initialize()
    
    # Obtener sistema RAG
    rag_system = session_manager.get_rag_system()
    
    # Crear servicios
    chat_service = ChatService(rag_system)
    
    # Crear UI
    chat_ui = ChatUI(chat_service, session_manager)
    
    return chat_service, session_manager, chat_ui

# ============================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================

def main():
    """Función principal de la aplicación"""
    # Configuración
    configure_app()
    
    # Inicializar dependencias
    _, _, chat_ui = initialize_dependencies()
    
    # Renderizar UI
    chat_ui.render_header()
    chat_ui.render_messages()
    chat_ui.render_quick_questions()
    chat_ui.render_chat_input()
    chat_ui.render_clear_button()

# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()