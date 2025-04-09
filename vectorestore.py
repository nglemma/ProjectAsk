
import os
import dataprocessing
import embedding
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pickle

faiss_index_path = "faiss_index"

# Helper wrapper to plug in your existing embedding function
class OpenAIEmbeddingsWrapper(Embeddings):
    def embed_documents(self, texts):
        embeddings = []
        batch_size = 100  # stay well under OpenAI token limits

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = embedding.embedding_function(batch)
            embeddings.extend(batch_embeddings)

        return embeddings

    def embed_query(self, text):
        return embedding.embedding_function(text)[0]

def load_or_create_vectorstore(force_reload=False):
    if os.path.exists(faiss_index_path) and not force_reload:
        with open(os.path.join(faiss_index_path, "index.pkl"), "rb") as f:
            return pickle.load(f)
    
    # Load and chunk data
    with open(dataprocessing.ouput_dir, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = [Document(page_content=chunk) for chunk in splitter.split_text(raw_text)]

    # Embed and create vectorstore
    vectorstore = FAISS.from_documents(docs, OpenAIEmbeddingsWrapper())
    
    # Save to disk
    os.makedirs(faiss_index_path, exist_ok=True)
    with open(os.path.join(faiss_index_path, "index.pkl"), "wb") as f:
        pickle.dump(vectorstore, f)

    return vectorstore



# from deeplake.core.vectorstore import VectorStore

# import deeplake.util
# import dataprocessing
# import embedding
# vector_store_path = "hub://ngeleemmanuel/UOGMBOT"
# source_text = dataprocessing.ouput_dir  # Path to the text file
# #add_to_vector_store = True


# def load_or_create_vectorstore(force_reload=False):
#     try:
#         if not force_reload:
#             vector_store = VectorStore(path=vector_store_path)
#             print("Vector store loaded.")
#             return vector_store
#         else:
#             raise FileNotFoundError  # Skip to creation
#     except FileNotFoundError:
#         print(" Vector store not found or reloading requested. Creating a new one...")

#         with open(source_text, 'r') as f:
#             text = f.read()

#         CHUNK_SIZE = 1000
#         chunked_text = [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]

#         vector_store = VectorStore(path=vector_store_path)
#         vector_store.add(
#             text=chunked_text,
#             embedding_function=embedding.embedding_function,
#             embedding_data=chunked_text,
#             metadata=[{"source": source_text}]*len(chunked_text)
#         )

#         print(" Vector store created.")
#         return vector_store

# try:
#     # Attempt to load the vector store
#     vector_store = VectorStore(path=vector_store_path)
#     print("Vector store exists")
# except FileNotFoundError:
#     print("Vector store does not exist. You can create it.")
#     # Code to create the vector store goes here
#     create_vector_store=True

# if add_to_vector_store == True:
#     with open(source_text, 'r') as f:
#         text = f.read()
#         CHUNK_SIZE = 1000
#         chunked_text = [text[i:i+1000] for i in range(0, len(text), CHUNK_SIZE)]

# vector_store.add(text = chunked_text,
#               embedding_function = embedding.embedding_function,
#               embedding_data = chunked_text,
#               metadata = [{"source": source_text}]*len(chunked_text))

