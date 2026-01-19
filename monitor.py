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
        handler = DataHandler(config['excel_path'])
        print("Config/Data loaded. Starting monitor...")
        
        bot = WhatsAppBot(config)
        bot.start_browser()
        
        print("Monitoring for new messages... (Ctrl+C to stop)")
        
        try:
            while True:
                # Check every 10 seconds for testing
                unread_list = bot.get_unread_messages()
                
                for chat in unread_list:
                    name = chat['sender']
                    msg = chat['message']
                    print(f"New interaction from {name}: {msg}")
                    
                    found, classification = handler.log_response(name, msg)
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
