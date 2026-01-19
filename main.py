import json
from wa_bot import WhatsAppBot
from data_handler import DataHandler
import sys

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    try:
        config = load_config()
        print("Config loaded.")
        
        handler = DataHandler(config['excel_path'])
        print(f"Data loaded from {config['excel_path']}")
        
        pending_contacts = handler.get_pending_contacts()
        
        if pending_contacts.empty:
            print("No pending contacts found.")
            return

        print(f"Found {len(pending_contacts)} pending messages.")
        
        bot = WhatsAppBot(config)
        bot.start_browser()
        
        for index, row in pending_contacts.iterrows():
            name = row['Nombre']
            phone = row['Telefono']
            
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
        input("Press Enter to close browser...") # Keep open to see result
        bot.close()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
