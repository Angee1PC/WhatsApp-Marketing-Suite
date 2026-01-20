import json
import time
import traceback
import sys
import io

# Force UTF-8 encoding for Windows consoles
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except:
    pass

from wa_bot import WhatsAppBot
from generate_report import ReportGenerator

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def send_report(wait_for_input=True):
    try:
        config = load_config()
        admin_number = config['admin_number']
        
        if admin_number == "YOUR_NUMBER_HERE":
            print("Error: Please set your 'admin_number' in config.json to receive the report.")
            return

        print("Generating report...")
        generator = ReportGenerator(config.get('excel_path', 'data/contacts.xlsx'), admin_number)
        report_text = generator.generate_summary()
        
        print("--- REPORT PREVIEW ---")
        print(report_text) # Keeping report_text as it's defined above
        
        # 4. Enviar
        bot = WhatsAppBot(config)
        bot.start_browser()

        try:
            if admin_number:
                print(f"Enviando a: {admin_number}")
                bot.send_message(admin_number, report_text) # Keeping report_text
                print("[OK] Reporte enviado correctamente.")
            else:
                print("[ERROR] No hay numero de admin configurado en config.json")
        
        except Exception as e:
            print(f"[ERROR] enviando reporte: {e}")

        # Optional: Ask to close
        # Optional: Ask to close
        if wait_for_input:
            input("Press Enter to close browser...")
        bot.close()
        return True

    except Exception as e:
        print(f"Error sending report: {e}")
        return False

if __name__ == "__main__":
    send_report()
