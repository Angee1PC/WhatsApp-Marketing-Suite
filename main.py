import json
from wa_bot import WhatsAppBot
from data_handler import DataHandler
import sys

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def main(wait_for_input=True):
    try:
        config = load_config()
        print("Config loaded.")
        
        excel_path = config.get('excel_path', 'data/contacts.xlsx')
        handler = DataHandler(excel_path)
        print(f"Data loaded from {excel_path}")
        
        pending_contacts = handler.get_pending_contacts()
        
        if pending_contacts.empty:
            print("No pending contacts found.")
            return

        print(f"Found {len(pending_contacts)} pending messages.")
        
        bot = WhatsAppBot(config)
        bot.start_browser()
        
        for index, row in pending_contacts.iterrows():
            name = row['Nombre']
            raw_phone = str(row['Telefono'])
            
            # Auto-format Phone: Remove non-digits
            phone = "".join(filter(str.isdigit, raw_phone))
            
            # If 10 digits (Mexico Standard), Add 52 automatically
            if len(phone) == 10:
                phone = "52" + phone
            
            # Dynamic template replacement
            message = config['message_template']
            for col in row.index:
                # Replace {ColumnName} with the value in that column
                placeholder = "{" + str(col) + "}" 
                if placeholder in message:
                    message = message.replace(placeholder, str(row[col]))
            
            print(f"Sending to {name} ({phone})...")
            success = bot.send_message(phone, message)
            
            if success:
                handler.update_status(index, 'Enviado')
            else:
                handler.update_status(index, 'Error')
                
        print("Batch processing complete.")
        if wait_for_input:
            input("Press Enter to close browser...")
        else:
            print("Closing browser automatically.")
        
        bot.close()
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
        if wait_for_input:
            input("Press Enter to exit...")
        return False

if __name__ == "__main__":
    main()
