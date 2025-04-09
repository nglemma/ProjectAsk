import os
import openai
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def embedding_function(texts, model="text-embedding-3-small"):
   if isinstance(texts, str):
       texts = [texts]
   texts = [t.replace("\n", " ") for t in texts]
   return [data.embedding for data in openai.embeddings.create(input = texts, model=model).data]
     