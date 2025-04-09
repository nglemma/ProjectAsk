import streamlit as st
from generator import search_bot
from vectorestore import load_or_create_vectorstore

st.set_page_config(page_title="UOGM Bot", layout="wide")
st.title("ASK UOGM")

# Session state to hold the vectorstore
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = load_or_create_vectorstore()

# Reload button
if st.button("Reload Dataset and Re-Embed"):
    with st.spinner("Reloading and embedding dataset..."):
        st.session_state.vector_store = load_or_create_vectorstore(force_reload=True)
    st.success("Dataset reloaded and embedded!")

# Input box for user query
user_query = st.text_area("Enter your question:", height=150)

if st.button("Send"):
    if user_query.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = search_bot(user_query)
                st.markdown("Response:")
                st.write(response)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
