import json
import time
from wa_bot import WhatsAppBot
from data_handler import DataHandler

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def run_monitor():
    try:
        config = load_config()
        handler = DataHandler(config.get('excel_path', 'data/contacts.xlsx'))
        print("Config/Data loaded. Starting monitor...")
        
        bot = WhatsAppBot(config)
        bot.start_browser()
        
        print("Monitoring for new messages... (Ctrl+C to stop)")
        
        try:
            while True:
                # Check every 10 seconds for testing
                # Get current expected contacts
                whitelist = handler.get_whitelist()
                unread_list = bot.get_unread_messages(whitelist=whitelist)
                
                for chat in unread_list:
                    name = chat.get('sender', 'Unknown')
                    phone = chat.get('phone', '')
                    msg = chat.get('message', '')
                    print(f"New interaction from {name}: {msg}")
                    
                    found, classification = handler.log_response(name, msg, phone_context=phone)
                    if found:
                         print(f" -> Saved to Excel. Classification: {classification}")
                    else:
                         print(" -> Name not found in Excel database.")
                
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("Stopping monitor...")
        finally:
            bot.close()
            
    except Exception as e:
        print(f"Monitor error: {e}")

if __name__ == "__main__":
    run_monitor()
