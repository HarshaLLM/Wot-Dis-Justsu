from langchain import hub
import bs4
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaLLM
import ollama


class Phi3Embeddings:
    """
    Custom class for using Phi-3.5-mini-instruct embeddings for indexing.
    """
    def __init__(self, model_name):
        self.model_name = model_name
    
    def embed_documents(self, texts):
        return [ollama.embeddings(model=self.model_name, prompt=text)["embedding"] for text in texts]

    def embed_query(self, text):
        return ollama.embeddings(model=self.model_name, prompt=text)["embedding"]
        
class RAGAgent:
    """
    Phi-3.5-mini-Instruct as an RAG-agent for document-based QA.
    by Harsha Vardhan Khurdula.
    """
    def __init__(self, model_name="Phi-3.5-mini", chunk_size=1000, chunk_overlap=200):
        self.model_name = model_name
        self.strainer = bs4.SoupStrainer(['article', 'main', 'div', 'section'])
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embedding_model = Phi3Embeddings(model_name)
        self.prompt = hub.pull("rlm/rag-prompt")
        self.llm = OllamaLLM(model=model_name)
        self.vectorstore = None
        self.retriever = None
        self.rag_chain = None

    def load_and_index(self, url):
        """
        Load and index:
        1. Scrape the contents of the blog.
        2. Create chunks for the documents.
        3. Index the contents of the blog using vectorstore.
        4. Create a RagChain for querying.
        """
        self.clear_collection()  
        loader = WebBaseLoader(web_paths=(url,))
        docs = loader.load()

        splits = self.text_splitter.split_documents(docs)

        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embedding_model
        )

        self.retriever = self.vectorstore.as_retriever(search_type="mmr", search_kwargs={'k': 4, 'fetch_k': 20})

        self.rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def answer_query(self, query):
        """
        Answer a query using the RAG chain.
        """
        if self.rag_chain is None:
            raise ValueError("No documents loaded. Please load and index a webpage first.")
        
        response = self.rag_chain.invoke(query)
        return response

    def clear_collection(self):
        """
        Reset the collections and clear the vectorstore.
        """
        if self.vectorstore is not None:
            try:
                self.vectorstore.delete_collection()
                self.vectorstore = None  
                self.retriever = None  
                self.rag_chain = None  
            except Exception as e:
                print(f"[ERR] The following error occurred while trying to clear the context: {e}")
        else:
            self.retriever = None
            self.rag_chain = None
