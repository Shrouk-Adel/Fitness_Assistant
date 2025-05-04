from langchain_community.document_loaders import CSVLoader
# embedding 
from langchain.embeddings import OllamaEmbeddings
# vector db 
from langchain_community.vectorstores import Chroma
 

def load_data(data_path='../Data/data.csv'):
 
    loader =CSVLoader(data_path)
    fit_docs =loader.load()
    
    return fit_docs

def retriever():
    # embedding text
    embeddings =OllamaEmbeddings(model ='plutonioumguy/bge-m3')

    # loading chromadb from disk later
    vectore_store = Chroma(
        embedding_function=embeddings,
        persist_directory='../notebooks/chromadb'
    )

    # retrieve
    retriever =vectore_store.as_retriever(search_kwargs={'k':5})
    return retriever
