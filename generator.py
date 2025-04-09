
import os
from dotenv import load_dotenv
import openai
import embedding
from openai import OpenAI
from vectorestore import load_or_create_vectorstore
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


client = OpenAI()
gptmodel = "gpt-4o"

def extract_schedule_from_natural_language(prompt):
    """
    Uses GPT to extract structured schedule data from a natural language prompt.
    Returns a list of dictionaries: [{"day": ..., "time": ..., "title": ...}]
    """
    system_message = (
        "You are a helpful assistant. A user will describe a calendar reminder or class schedule in plain English. "
        "Extract and return a list of JSON objects with 'day', 'time', and 'title' fields.\n\n"
        "Example:\n"
        "Input: 'Set a reminder for Friday's Math class at 10am'\n"
        "Output: [{\"day\": \"Friday\", \"time\": \"10:00-11:00\", \"title\": \"Math class\"}]\n"
        "Use 1-hour default durations if not specified. Use 24-hour format. "
    )

    try:
        response = client.chat.completions.create(
            model=gptmodel,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content
        # Attempt to extract JSON block from response
        import json, re
        json_match = re.search(r'\[.*\]', result, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        return []
    except Exception as e:
        print("Error extracting schedule:", e)
        return []


def call_llm_with_full_text(itext):
    text_input = '\n'.join(itext)
    prompt = f"Please elaborate on the following content:\n{text_input}"

    try:
        response = client.chat.completions.create(
            model=gptmodel,
            messages=[
                {"role": "system", "content": """You are a helpful AI assistant for students of the university of Bolton who wants to get quick information about the school.
    you also assist the students to draft emails if you are asked to do so.
    Always check the vector store for the most relevant documents to the question.
    When asked a follow up question, always refer to the previous question and answer.
    If you don't know the answer, just say that you don't know. 
    keep your answer brief and to the point.
    If the users question reqires providing email addresses, do hesitate to give them.
    Alwyas asks the user if they are satisfied with the response you gave"""
    },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return str(e)

def search_bot(user_prompt, top_k=3):
    try:
        vector_store = load_or_create_vectorstore()
        docs = vector_store.similarity_search(user_prompt, k=top_k)
        if not docs:
            return "No relevant documents found in the index."
        top_chunks = "\n\n".join([doc.page_content for doc in docs])
        augmented_input = user_prompt + "\n\n" + top_chunks
        return call_llm_with_full_text([augmented_input])
    except Exception as e:
        return f"Search failed: {e}"

# def call_llm_with_full_text(itext):
#     text_input = '\n'.join(itext)
#     prompt = f"Please elaborate on the following content:\n{text_input}"

#     try:
#         response = client.chat.completions.create(
#             model=gptmodel,
#             messages=[
#                 {"role": "system", "content": "You are a helpful AI assistant for students of the university of Bolton who wants to get quick information about the school."},
#                 {"role": "assistant", "content": "You can read the input and answer in detail."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.1
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return str(e)

# def search_bot(user_prompt, top_k=3):
    
#     try:
#         vector_store = load_or_create_vectorstore()
#         results = vector_store.search(
#             embedding_data=user_prompt, 
#             k=top_k,
#             embedding_function=embedding.embedding_function  # Add this line
#             )
        
#         top_chunks = "\n\n".join([r['text'] for r in results['matches']])
#         augmented_input = user_prompt + "\n\n" + top_chunks
#         return call_llm_with_full_text([augmented_input])
#     except Exception as e:
#         return f"Search failed: {e}"


# def call_llm_with_full_text(itext):
#     # Join all lines to form a single string
#     text_input = '\n'.join(itext)
#     prompt = f"Please elaborate on the following content:\n{text_input}"

#     try:
#       response = client.chat.completions.create(
#          model=gptmodel,
#          messages=[
#             {"role": "system", "content": "You are an expert Natural Language Processing exercise expert."},
#             {"role": "assistant", "content": "1.You can explain read the input and answer in detail"},
#             {"role": "user", "content": prompt}
#          ],
#          temperature=0.1  # Add the temperature parameter here and other parameters you need
#         )
#       return response.choices[0].message.content.strip()
#     except Exception as e:
#         return str(e)