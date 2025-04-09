import streamlit as st
import uuid
import re
from generator import search_bot as ask_question
import sendMail

st.set_page_config(page_title="UOGM")
st.title("UOGM Chatbot")
st.markdown("Welcome to the University of Bolton Chatbot")
st.markdown("This chatbot is designed to help you with any questions you may have about the University of Bolton")
st.video("https://youtu.be/WIh15eEd5N8")


def get_last_assistant_message():
    for message in reversed(st.session_state.messages):
        if message["role"] == "assistant":
            return message["content"]
    return ""

def draft_email(prompt, email_address):
    email_prompt = f"Draft an email to {email_address} based on the following request: {prompt}. Please also provide a suitable subject line."
    email_response = ask_question(email_prompt)
    email_text = email_response

    subject_match = re.search(r"Subject: (.+)\n", email_text)
    if subject_match:
        subject = subject_match.group(1)
        body = email_text.replace(subject_match.group(0), "").strip()
    else:
        subject = "No Subject Provided"
        body = email_text

    return subject, body

def process_email_request(prompt):
    last_response = get_last_assistant_message()
    email_matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", last_response)
    if not email_matches:
        return "No email address found in the last response."
    elif len(email_matches) == 1:
        subject, body = draft_email(prompt, email_matches[0])
        return sendMail.send_email(subject, body, email_matches[0])
    else:
        st.session_state.multiple_emails = email_matches
        st.session_state.email_prompt_for_context = prompt
        email_choices = "\n".join([f"{i + 1}. {email}" for i, email in enumerate(email_matches)])
        st.session_state.awaiting_email_choice = True
        return f"Multiple email addresses found:\n{email_choices}\nPlease type the number of the address you'd like to use."

def handle_email_choice(choice_input):
    try:
        idx = int(choice_input.strip()) - 1
        email_address = st.session_state.multiple_emails[idx]
        prompt = st.session_state.email_prompt_for_context
        subject, body = draft_email(prompt, email_address)
        return sendMail.send_email(subject, body, email_address)
    except (ValueError, IndexError):
        return "Invalid selection. Please enter a valid number."

def show_ui(prompt_to_user="How may I help you?"):
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": prompt_to_user}]
    if "fbk" not in st.session_state:
        st.session_state.fbk = str(uuid.uuid4())

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input():
        if st.session_state.get("awaiting_email_choice"):
            with st.chat_message("user"):
                st.write(prompt)
            with st.chat_message("assistant"):
                response = handle_email_choice(prompt)
                st.write(response)
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.awaiting_email_choice = False
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            if "send an email to" in prompt.lower():
                with st.chat_message("assistant"):
                    with st.spinner("Drafting and sending email..."):
                        email_result = process_email_request(prompt)
                        st.markdown(email_result)
                st.session_state.messages.append({"role": "assistant", "content": email_result})
            else:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = ask_question(prompt)
                        if response is None:
                            st.error("The assistant returned no response. Please try again or check your vectorstore.")
                        else:
                            st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

    if len(st.session_state.messages) > 1 and st.session_state.messages[-1]["role"] == "assistant":
        from streamlit_feedback import streamlit_feedback
        def save_feedback(response):
            st.session_state.messages[-1]["feedback"] = response
            st.session_state.fbk = str(uuid.uuid4())

        streamlit_feedback(
            feedback_type="thumbs",
            optional_text_label="Optional",
            align="flex-start",
            key=st.session_state.fbk,
            on_submit=save_feedback
        )

# Launch the chat
show_ui()

