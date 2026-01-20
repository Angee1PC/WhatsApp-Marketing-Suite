import pandas as pd
import os

class DataHandler:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.df = None
        self.load_data()

    def load_data(self):
        if os.path.exists(self.excel_path):
            self.df = pd.read_excel(self.excel_path, dtype={'Telefono': str})
        else:
            # Create default structure if missing
            self.df = pd.DataFrame(columns=["Nombre", "Telefono", "Estado", "Mensaje", "Respuesta", "Interes"])
            # Create directory if needed
            os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
            self.save_data()

    def get_pending_contacts(self):
        # Filter where State is 'Pendiente'
        return self.df[self.df['Estado'] == 'Pendiente']

    def update_status(self, index, status):
        self.df.at[index, 'Estado'] = status
        self.save_data()

    def save_data(self):
        self.df.to_excel(self.excel_path, index=False)

    def log_response(self, name, message, phone_context=""):
        """
        Saves the response to the Excel file matching by Name or Phone.
        """
        # Simple classification
        classification = "Desconocido"
        msg_lower = message.lower()
        if any(x in msg_lower for x in ['si', 'sì', 'sí', 'interesa', 'quiero', 'comprar', 'rentar']):
            classification = "Interesado"
        elif any(x in msg_lower for x in ['no', 'gracias', 'baja', 'stop']):
            classification = "No Interesado"
            
        # Advanced Matching Logic
        wa_id = name.lower().strip()
        
        # Extract digits from the context gathered by Bot
        context_digits = "".join(filter(str.isdigit, phone_context)) if phone_context else ""
        
        # 1. Try to clean up name as phone number (remove +, spaces, dashes)
        wa_name_digits = "".join(filter(str.isdigit, wa_id))
        
        match_idx = None
        
        for idx, row in self.df.iterrows():
            # Excel Data
            excel_name = str(row['Nombre']).lower().strip()
            excel_phone = str(row['Telefono'])
            excel_phone_digits = "".join(filter(str.isdigit, excel_phone))
            
            # Match 1: Context Phone Match (Bot found Real Number in Profile)
            if len(context_digits) > 6 and len(excel_phone_digits) > 6:
                if excel_phone_digits in context_digits or context_digits in excel_phone_digits:
                     match_idx = idx
                     break

            # Match 2: Name appears to be a phone number
            if len(wa_name_digits) > 7 and len(excel_phone_digits) > 7:
                if excel_phone_digits in wa_name_digits or wa_name_digits in excel_phone_digits:
                    match_idx = idx
                    break
            
            # Match 3: Flexible Name Match
            if excel_name in wa_id or wa_id in excel_name:
                match_idx = idx
                break
        
        if match_idx is not None:
            # We found the user in the Excel!
            # We can now use the 'Nombre' from Excel to refer to them in future logic if needed
            matched_name = self.df.at[match_idx, 'Nombre']
            print(f" -> Identificado en Excel como: {matched_name}")
            
            self.df.at[match_idx, 'Respuesta'] = message
            self.df.at[match_idx, 'Estado'] = classification
            self.save_data()
            return True, classification
            
        return False, None

    def get_whitelist(self):
        """
        Returns a list of all names and phones in the database to filter incoming messages.
        """
        whitelist = []
        if self.df is not None:
            # 1. Names
            whitelist.extend(self.df['Nombre'].astype(str).tolist())
            # 2. Phones
            phones = self.df['Telefono'].astype(str).tolist()
            # Clean phones
            cleaned_phones = ["".join(filter(str.isdigit, p))[-10:] for p in phones]
            whitelist.extend(cleaned_phones)
            
        # Lowercase for loose matching
        return [str(x).lower().strip() for x in whitelist if len(str(x)) > 1]
