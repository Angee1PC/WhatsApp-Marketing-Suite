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
            raise FileNotFoundError(f"File not found: {self.excel_path}")

    def get_pending_contacts(self):
        # Filter where State is 'Pendiente'
        return self.df[self.df['Estado'] == 'Pendiente']

    def update_status(self, index, status):
        self.df.at[index, 'Estado'] = status
        self.save_data()

    def save_data(self):
        self.df.to_excel(self.excel_path, index=False)

    def log_response(self, name, message):
        """
        Saves the response to the Excel file matching by Name.
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
        
        # 1. Try to clean up as phone number (remove +, spaces, dashes)
        wa_phone_digits = "".join(filter(str.isdigit, wa_id))
        
        match_idx = None
        
        for idx, row in self.df.iterrows():
            # Excel Data
            excel_name = str(row['Nombre']).lower().strip()
            excel_phone = str(row['Telefono'])
            excel_phone_digits = "".join(filter(str.isdigit, excel_phone))
            
            # Match Attempt 1: Exact Phone Match (Best for unsaved contacts)
            # If we extracted at least 7 digits to be safe
            if len(wa_phone_digits) > 7 and len(excel_phone_digits) > 7:
                if excel_phone_digits in wa_phone_digits or wa_phone_digits in excel_phone_digits:
                    match_idx = idx
                    break
            
            # Match Attempt 2: Flexible Name Match
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
