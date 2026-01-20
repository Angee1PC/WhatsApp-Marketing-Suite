import os.path
import datetime
import re
import pickle
import sys
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd

# Scope: Read-only access to calendar is enough
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class CalendarManager:
    def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
        self.creds_file = credentials_file
        self.token_file = token_file
        self.service = None
        
        # Check bundled credentials if frozen
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundled_creds = os.path.join(sys._MEIPASS, credentials_file)
            if os.path.exists(bundled_creds):
                self.creds_file = bundled_creds

    def authenticate(self):
        """Authenticates the user with Google Calendar API."""
        creds = None
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                try:
                    creds = pickle.load(token)
                except:
                    pass
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.creds_file):
                    raise FileNotFoundError(f"No se encontró {self.creds_file}. Descárgalo de Google Cloud Console (OAuth Client ID).")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)
        return True

    def get_tomorrow_events(self):
        """Fetches events for Today and Upcoming week (Broad Search)."""
        if not self.service:
            self.authenticate()

        # Define 'Upcoming' range (Now to +3 days)
        # We start 24h ago just to be safe with timezones and catch today's earlier events
        now = datetime.datetime.utcnow()
        start_time = (now - datetime.timedelta(hours=24)).isoformat() + 'Z'
        end_time = (now + datetime.timedelta(days=3)).isoformat() + 'Z'

        print(f"Buscando eventos recientes y próximos...")
        
        events_result = self.service.events().list(
            calendarId='primary', 
            timeMin=start_time, 
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])

    def extract_phone_and_name(self, event):
        """
        Attempts to find a phone number in the event description or title.
        Returns: (Name, Phone, TimeStr)
        """
        summary = event.get('summary', 'Sin Titulo')
        description = event.get('description', '')
        start = event['start'].get('dateTime', event['start'].get('date'))
        
        # Parse time nicely (e.g., "10:30")
        try:
            dt_obj = datetime.datetime.fromisoformat(start)
            time_str = dt_obj.strftime("%H:%M")
        except:
            time_str = "Todo el día"

        # Combine text to search
        full_text = f"{summary} {description}"
        
        # Regex for phone numbers (10 digits, allowing spaces/dashes)
        # Matches: 5512345678, 55-1234-5678, 55 1234 5678
        phone_match = re.search(r'[\d\-\s]{10,15}', full_text)
        
        phone = None
        if phone_match:
            # Clean digits
            raw_phone = "".join(filter(str.isdigit, phone_match.group()))
            if len(raw_phone) >= 10:
                phone = raw_phone[-10:] # Take last 10 digits
                
                # Add Mexico Country Code if missing (Standard 52)
                # User specifically requested adding 52 prefix
                if len(phone) == 10:
                    phone = "52" + phone
        
        # Name: Assume the Title is the Name if it doesn't look like "Cita con..."
        # Heuristic: Remove "Cita", "Consulta" from summary
        name = summary.replace("Cita con", "").replace("Cita", "").replace("Consulta", "").strip()
        
        return name, phone, time_str

    def sync_to_excel(self, excel_path="data/contacts.xlsx"):
        """Reads calendar and appends to Excel."""
        events = self.get_tomorrow_events()
        new_contacts = []
        
        for event in events:
            # DEBUG: Print raw event info
            summary_raw = event.get('summary', 'No Title')
            start_raw = event['start'].get('dateTime', event['start'].get('date'))
            print(f"[DEBUG] Analizando evento: {summary_raw} ({start_raw})")
            
            name, phone, time_str = self.extract_phone_and_name(event)
            
            if phone:
                print(f"[OK] Telefono detectado: {phone}")
                # Create the confirmation message
                msg = f"Hola {name}, confirmamos tu cita para mañana a las {time_str}. 🗓️ ¿Podrías confirmar con un 'SÍ'?"
                
                new_contacts.append({
                    "Nombre": name,
                    "Telefono": phone,
                    "Mensaje": msg,
                    "Estado": "Pendiente",
                    "Interes": "Cita Agendada" # Tag
                })
            else:
                print(f"Evento sin teléfono detectado: {name}")

        if not new_contacts:
            return 0

        # DataFrame Logic using pandas
        try:
            df = pd.read_excel(excel_path, dtype=str)
        except:
            df = pd.DataFrame(columns=["Nombre", "Telefono", "Mensaje", "Estado", "Interes"])
        
        # Check for duplicates (don't add if phone already exists)
        existing_phones = df['Telefono'].astype(str).tolist() if 'Telefono' in df.columns else []
        
        added_count = 0
        for contact in new_contacts:
            if contact['Telefono'] not in existing_phones:
                row_df = pd.DataFrame([contact])
                df = pd.concat([df, row_df], ignore_index=True)
                added_count += 1
        
        if added_count > 0:
            df.to_excel(excel_path, index=False)
            print("Excel actualizado.")
            
        return added_count

if __name__ == "__main__":
    # Test
    try:
        cm = CalendarManager()
        count = cm.sync_to_excel()
        print(f"Se agregaron {count} citas nuevas al Excel.")
    except Exception as e:
        print(f"Error: {e}")
