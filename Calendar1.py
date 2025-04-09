import datetime
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the token.pickle file
SCOPES = ["https://www.googleapis.com/auth/calendar"]

CREDENTIALS_FILE = "/Users/mac/Documents/NewCAFormat/client_secret_223591589717-0plchjkrib5uldbtpu35f6pc3uu977vj.apps.googleusercontent.com.json"
TOKEN_FILE = "token.pickle"

def authenticate_google():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)

def create_calendar_event(summary, day_str, time_range):
    service = authenticate_google()

    # Example input: day_str="Friday", time_range="14:00-16:00"
    day_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }

    today = datetime.date.today()
    target_day = day_map[day_str.lower()]
    days_ahead = (target_day - today.weekday() + 7) % 7
    if days_ahead == 0:
        days_ahead = 7

    class_date = today + datetime.timedelta(days=days_ahead)
    start_time, end_time = time_range.split("-")

    start_datetime = datetime.datetime.strptime(f"{class_date} {start_time}", "%Y-%m-%d %H:%M")
    end_datetime = datetime.datetime.strptime(f"{class_date} {end_time}", "%Y-%m-%d %H:%M")

    event = {
        "summary": summary,
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Europe/London",
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Europe/London",
        },
    }

    event = service.events().insert(calendarId="primary", body=event).execute()
    return f"Google Calendar event created: {event.get('htmlLink')}"

# Example usage for dev/testing:
# print(create_calendar_event("AI Class - Module 1", "Friday", "14:00-16:00"))
