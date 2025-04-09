import vectorestore
import embedding
import textwrap
from openai import OpenAI
client = OpenAI()
gpt_model="gpt-4o"

def search_query(prompt):
    # Assuming `vector_store` and `embedding_function` are already defined
    search_results = vectorestore.vector_store.search(embedding_data=prompt, embedding_function=embedding.embedding_function)
    return search_results

user_prompt="What skills will I learn on an Animation and Illustration course?"
search_results = search_query(user_prompt)
#print(search_results)

def wrap_text(text, width=80):
    lines = []
    while len(text) > width:
        split_index = text.rfind(' ', 0, width)
        if split_index == -1:
            split_index = width
        lines.append(text[:split_index])
        text = text[split_index:].strip()
    lines.append(text)
    return '\n'.join(lines)


# Assuming the search results are ordered with the top result first
top_score = search_results['score'][0]
top_text = search_results['text'][0].strip()
top_metadata = search_results['metadata'][0]['source']

# Print the top search result
print("Top Search Result:")
print(f"Score: {top_score}")
print(f"Source: {top_metadata}")
print("Text:")
print(wrap_text(top_text))

augmented_input=user_prompt+" "+top_text

def call_gpt4_with_full_text(itext):
    # Join all lines to form a single string
    text_input = '\n'.join(itext)
    prompt = f"Please answer the question:\n{text_input}"

    try:
        response = client.chat.completions.create(
            model=gpt_model,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for students of the university of Bolton who wants to get quick information about the school."},
                {"role": "assistant", "content": "You can read the input and answer in detail."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1  # Fine-tune parameters as needed
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

gpt4_response = call_gpt4_with_full_text(augmented_input)
