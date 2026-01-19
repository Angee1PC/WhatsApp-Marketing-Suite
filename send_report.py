import json
from wa_bot import WhatsAppBot
from generate_report import ReportGenerator

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def send_report():
    try:
        config = load_config()
        admin_number = config['admin_number']
        
        if admin_number == "YOUR_NUMBER_HERE":
            print("Error: Please set your 'admin_number' in config.json to receive the report.")
            return

        print("Generating report...")
        generator = ReportGenerator(config['excel_path'], admin_number)
        report_text = generator.generate_summary()
        
        print("\n--- REPORT PREVIEW ---")
        print(report_text)
        print("----------------------\n")
        
        bot = WhatsAppBot(config)
        bot.start_browser()
        
        print(f"Sending report to Admin ({admin_number})...")
        bot.send_message(admin_number, report_text)
        
        print("Report sent successfully.")
        
        # Optional: Ask to close
        input("Press Enter to close browser...")
        bot.close()

    except Exception as e:
        print(f"Error sending report: {e}")

if __name__ == "__main__":
    send_report()
