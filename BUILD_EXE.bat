pyinstaller --noconfirm --onedir --windowed --icon "NONE" ^
 --add-data "data;data" ^
 --add-data "config.json;." ^
 --add-data "credentials.json;." ^
 --add-data "security.py;." ^
 --add-data "templates_manager.py;." ^
 --add-data "wa_bot.py;." ^
 --add-data "calendar_manager.py;." ^
 --add-data "main.py;." ^
 --add-data "monitor.py;." ^
 --add-data "send_report.py;." ^
 --add-data "sync_calendar.py;." ^
 --hidden-import "babel.numbers" ^
 --name "WhatsAppAutoBot" ^
 app_gui.py
pause
