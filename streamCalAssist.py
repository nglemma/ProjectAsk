import streamlit as st
import uuid
import re
from generator import search_bot as ask_question
import sendMail
from openai import OpenAI
from Calendar1 import create_calendar_event
from generator import extract_schedule_from_natural_language

client = OpenAI()

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

def match_reminder_request(prompt, schedule_blocks):
    schedule_text = "\n".join([f"{i+1}. {b['day']} {b['time']}: {b['title']}" for i, b in enumerate(schedule_blocks)])
    full_prompt = f"""
From the following schedule:
{schedule_text}

User says: "{prompt}"

Which numbered item best matches the user's intent? Just return the number (1-based).
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": full_prompt}
        ],
        temperature=0
    )
    answer = response.choices[0].message.content.strip()
    try:
        idx = int(answer) - 1
        return schedule_blocks[idx]
    except:
        return None

def process_reminder_request(prompt):
    last_response = get_last_assistant_message()
    blocks = extract_schedule_from_natural_language(last_response)
    if not blocks:
        return "No valid schedule found in the previous message."
    match = match_reminder_request(prompt, blocks)
    if not match:
        return "Could not understand which class to set a reminder for. Please be more specific."

    if "reminders" not in st.session_state:
        st.session_state.reminders = []

    st.session_state.reminders.append(match)

    # Automatically export to Google Calendar
    try:
        calendar_result = create_calendar_event(match['title'], match['day'], match['time'])
        return f"Reminder set: {match['day']} {match['time']} – {match['title']}\n{calendar_result}"
    except Exception as e:
        return f"Reminder set locally but failed to export to Google Calendar: {e}"

def confirm_and_edit_email():
    prompt = st.session_state.email_prompt_for_context
    email_address = st.session_state.selected_email
    subject, body = draft_email(prompt, email_address)
    st.session_state.draft_subject = subject
    st.session_state.draft_body = body
    st.session_state.awaiting_email_confirmation = True
    return f"Here is the drafted email to {email_address}: Subject: {subject}\n\n{body}\n\nPlease review and confirm or edit before sending."

def finalize_email():
    subject = st.session_state.draft_subject
    body = st.session_state.draft_body
    email_address = st.session_state.selected_email
    return sendMail.send_email(subject, body, email_address)

def handle_email_choice(choice_input):
    try:
        idx = int(choice_input.strip()) - 1
        st.session_state.selected_email = st.session_state.multiple_emails[idx]
        return confirm_and_edit_email()
    except (ValueError, IndexError):
        return "Invalid selection. Please enter a valid number."

def process_email_request(prompt):
    last_response = get_last_assistant_message()
    email_matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", last_response)
    if not email_matches:
        return "No email address found in the last response."
    elif len(email_matches) == 1:
        st.session_state.selected_email = email_matches[0]
        st.session_state.email_prompt_for_context = prompt
        return confirm_and_edit_email()
    else:
        st.session_state.multiple_emails = email_matches
        st.session_state.email_prompt_for_context = prompt
        email_choices = "\n".join([f"{i + 1}. {email}" for i, email in enumerate(email_matches)])
        st.session_state.awaiting_email_choice = True
        return f"Multiple email addresses found:\n{email_choices}\nPlease type the number of the address you'd like to use."

def show_ui(prompt_to_user="How may I help you?"):
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": prompt_to_user}]
    if "fbk" not in st.session_state:
        st.session_state.fbk = str(uuid.uuid4())

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.session_state.get("awaiting_email_confirmation"):
        st.markdown("### ✉️ Review your email before sending:")
        st.session_state.draft_subject = st.text_input("Subject", value=st.session_state.draft_subject)
        st.session_state.draft_body = st.text_area("Body", value=st.session_state.draft_body, height=200)
        if st.button("Send Email"):
            with st.chat_message("assistant"):
                with st.spinner("Sending email..."):
                    result = finalize_email()
                    st.write(result)
            st.session_state.messages.append({"role": "assistant", "content": result})
            st.session_state.awaiting_email_confirmation = False
            st.experimental_rerun()
        return

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
                    with st.spinner("Drafting and preparing email..."):
                        email_result = process_email_request(prompt)
                        st.markdown(email_result)
                st.session_state.messages.append({"role": "assistant", "content": email_result})

            elif "reminder" in prompt.lower() or "set a reminder" in prompt.lower():
                with st.chat_message("assistant"):
                    with st.spinner("Checking your schedule and setting a reminder..."):
                        reminder_result = process_reminder_request(prompt)
                        st.markdown(reminder_result)
                st.session_state.messages.append({"role": "assistant", "content": reminder_result})

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
