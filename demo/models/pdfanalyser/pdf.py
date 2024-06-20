import os
import cv2
import numpy as np
import joblib
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from llama_parse import LlamaParse
from langchain_groq import ChatGroq
from langchain_community.vectorstores.chroma import Chroma

# Load variables from .env file
# load_dotenv('.env')

llamaparse_api_key="llx-KZm8M1tyCNWv1WQfcp9QyDAcbJSh8CcHVfCNvN2MB3UZy7Pq"
groq_api_key="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"

# llamaparse_api_key = os.getenv('LLAMA_API_KEY')
# groq_api_key = os.getenv("GROQ_API_KEY")

 
def load_or_parse_data(path):
    data_file = "media/pdfs/parsed_data.pkl"

    if os.path.exists(data_file):
        # Load the parsed data from the file
        parsed_data = joblib.load(data_file)
    else:
        # Perform the parsing step and store the result in llama_parse_documents
        parsingInstruction = """ It contains tables.
        Try to be precise while generating the questions and answers. """
        parser = LlamaParse(api_key=llamaparse_api_key,
                            result_type="markdown",
                            parsing_instruction=parsingInstruction,
                            max_timeout=10000,)
        llama_parse_documents = parser.load_data(path)


        # Save the parsed data to a file
        print("Saving the parse results in .pkl format ..........")
        joblib.dump(llama_parse_documents, data_file)
        # Set the parsed data to the variable
        parsed_data = llama_parse_documents


    print(parsed_data)
    return parsed_data

# pd=load_or_parse_data()

 # Create vector database
def create_vector_database(fpath):
    """
    Creates a vector database using document loaders and embeddings.

    This function loads urls,
    splits the loaded documents into chunks, transforms them into embeddings using OllamaEmbeddings,
    and finally persists the embeddings into a Chroma vector database.

    """
    # Call the function to either load or parse the data
    llama_parse_documents = load_or_parse_data(path=fpath)
    #print(llama_parse_documents[0].text[:300])

    with open('media/pdfs/output.md', 'a') as f:  # Open the file in append mode ('a')
        for doc in llama_parse_documents:
            f.write(doc.text + '\n')

    markdown_path = "media/pdfs/output.md"
    loader = UnstructuredMarkdownLoader(markdown_path)

   #loader = DirectoryLoader('data/', glob="**/*.md", show_progress=True)
    documents = loader.load()
    # Split loaded documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    #len(docs)
    print(f"length of documents loaded: {len(documents)}")
    print(f"total number of document chunks generated :{len(docs)}")
    #docs[0]

    # Initialize Embeddings
    embed_model = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")

    # Create and persist a Chroma vector database from the chunked documents
    vs = Chroma.from_documents(
        documents=docs,
        embedding=embed_model,
        persist_directory="chroma_db_llamaparse1",  # Local mode with in-memory storage only
        collection_name="rag"
    )


    print('Vector DB created successfully !')
    return vs,embed_model