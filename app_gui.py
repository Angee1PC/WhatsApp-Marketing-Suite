import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
import subprocess
from templates_manager import TemplateManager

# Configuration for Modern UI
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

from security import SecurityManager

class LoginDialog(ctk.CTkToplevel):
    def __init__(self, parent, security_mgr):
        super().__init__(parent)
        self.security = security_mgr
        self.title("Licencia Requerida 🔒")
        self.geometry("400x350")
        self.resizable(False, False)
        
        # Center window
        self.transient(parent)
        self.grab_set()
        
        self.device_id = self.security.get_device_id()
        self.authenticated = False
        
        # UI Elements
        ctk.CTkLabel(self, text="🔒 Activación de Producto", font=("Roboto", 20, "bold")).pack(pady=20)
        
        ctk.CTkLabel(self, text="Tu ID de Dispositivo:").pack()
        self.entry_id = ctk.CTkEntry(self, width=250, justify="center")
        self.entry_id.insert(0, self.device_id)
        self.entry_id.configure(state="readonly")
        self.entry_id.pack(pady=5)
        
        ctk.CTkLabel(self, text="Copia este ID y envíalo al vendedor\npara obtener tu clave.", text_color="gray").pack(pady=5)
        
        ctk.CTkLabel(self, text="Ingresa tu Clave de Licencia:").pack(pady=(20, 5))
        self.entry_key = ctk.CTkEntry(self, width=250, placeholder_text="XXXX-XXXX-XXXX")
        self.entry_key.pack(pady=5)
        
        ctk.CTkButton(self, text="Activar Software", command=self.check_key, fg_color="#E0AA3E", hover_color="#C4922F").pack(pady=20)
        
        self.lbl_status = ctk.CTkLabel(self, text="", text_color="red")
        self.lbl_status.pack()

    def check_key(self):
        key = self.entry_key.get()
        if self.security.validate_key(key):
            self.security.save_license(key)
            self.authenticated = True
            tk.messagebox.showinfo("Bienvenido", "¡Licencia activada correctamente! 🚀")
            self.destroy()
        else:
            self.lbl_status.configure(text="❌ Clave inválida. Intenta de nuevo.")

class WhatsAppAutoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Security Check Loop
        self.security = SecurityManager()
        saved_key = self.security.load_license()
        
        # If no valid saved key, enforce login
        if not saved_key or not self.security.validate_key(saved_key):
            self.withdraw() # Hide main window
            login = LoginDialog(self, self.security)
            self.wait_window(login) # Wait for dialog to close
            
            if not login.authenticated:
                sys.exit() # Exit if closed without auth
            
            self.deiconify() # Show main window if passed
            
        # Window Setup
        self.title("WhatsApp Automation Suite PRO 🚀")
        self.geometry("800x700") # Slightly wider, manageable height
        self.minsize(600, 600)
        
        # Load Config
        self.config = self.load_config()
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Layout (Tabs)
        self.tab_view = ctk.CTkTabview(self, width=650, height=750)
        self.tab_view.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.tab_config = self.tab_view.add("⚙️ Configuración")
        self.tab_actions = self.tab_view.add("🚀 Panel de Control")
        
        self.setup_config_tab()
        self.setup_actions_tab()

    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def save_config(self):
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            # Custom msg box not included in CTK, using standard or print
            print("Configuración guardada")
            tk.messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def setup_config_tab(self):
        # Frame - Using ScrollableFrame to ensure Button is always reachable on small screens
        frame = ctk.CTkScrollableFrame(self.tab_config)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Make frame content stretchable
        # Title
        ctk.CTkLabel(frame, text="Configuración General", font=("Roboto", 20, "bold")).pack(pady=10)
        
        # Admin Number
        ctk.CTkLabel(frame, text="Número Admin (Tu WhatsApp):").pack(anchor="w", padx=20)
        self.entry_admin = ctk.CTkEntry(frame, placeholder_text="Ej: 521...")
        self.entry_admin.insert(0, self.config.get('admin_number', ''))
        self.entry_admin.pack(anchor="w", padx=20, pady=(0, 10), fill="x")
        
        # Template Section
        ctk.CTkLabel(frame, text="Objetivo del Mensaje (Sugerencias):", font=("Roboto", 14, "bold")).pack(anchor="w", padx=20, pady=(5, 5))
        
        self.combo_type = ctk.CTkComboBox(frame, 
                                          values=["Ventas (Producto/Inmueble)", "Citas (Reservar/Confirmar)"], 
                                          command=self.update_suggestions_event)
        self.combo_type.pack(anchor="w", padx=20, pady=5, fill="x")
        
        # Suggestions List (Using scrollable frame of buttons for modern look)
        ctk.CTkLabel(frame, text="Click en una sugerencia para usarla:").pack(anchor="w", padx=20, pady=5)
        self.scroll_suggestions = ctk.CTkScrollableFrame(frame, height=120, label_text="Sugerencias")
        self.scroll_suggestions.pack(padx=20, pady=5, fill="both", expand=True) # THIS EXPANDS
        
        # Text Area for Editing
        ctk.CTkLabel(frame, text="Mensaje Final (Editable):", font=("Roboto", 14, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        self.text_template = ctk.CTkTextbox(frame, height=100)
        self.text_template.insert("0.0", self.config.get('message_template', ''))
        self.text_template.pack(padx=20, pady=5, fill="both", expand=True) # THIS EXPANDS
        
        # Save Button
        ctk.CTkButton(frame, text="💾 Guardar Configuración", command=self.save_settings, height=40, font=("Roboto", 14, "bold")).pack(pady=15, fill="x", padx=20)

    def update_suggestions_event(self, choice):
        # Clear previous widgets in scrollable frame
        for widget in self.scroll_suggestions.winfo_children():
            widget.destroy()
            
        suggestions = TemplateManager.get_suggestions(choice)
        
        for i, text in enumerate(suggestions):
            # Create a button for each suggestion
            btn = ctk.CTkButton(self.scroll_suggestions, text=text[:60] + "...", anchor="w", fg_color="transparent", border_width=1, border_color="#3B8ED0", text_color=("gray10", "gray90"))
            btn.configure(command=lambda t=text: self.set_template_text(t))
            btn.pack(fill="x", pady=2)

    def set_template_text(self, text):
        self.text_template.delete("0.0", "end")
        self.text_template.insert("0.0", text)

    def save_settings(self):
        self.config['admin_number'] = self.entry_admin.get()
        self.config['message_template'] = self.text_template.get("0.0", "end").strip()
        self.save_config()

    def setup_actions_tab(self):
        frame = ctk.CTkFrame(self.tab_actions)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Panel de Control", font=("Roboto", 24, "bold")).pack(pady=20)
        
        # Action Buttons Layout
        # 1. Edit Excel
        btn_excel = ctk.CTkButton(frame, text="📂 1. Abrir Lista de Excel (Contactos)", 
                                  command=self.open_excel,
                                  height=50,
                                  font=("Roboto", 16),
                                  fg_color="#E0AA3E", hover_color="#C4922F") # Yellowish for file
        btn_excel.pack(fill="x", padx=40, pady=10)
        
        # 2. Send Messages
        btn_send = ctk.CTkButton(frame, text="📤 2. Iniciar Envío Masivo", 
                                 command=lambda: self.run_script("main.py"),
                                 height=50,
                                 font=("Roboto", 16))
        btn_send.pack(fill="x", padx=40, pady=10)
        
        # 3. Monitor
        btn_monitor = ctk.CTkButton(frame, text="👂 3. Iniciar Monitor de Respuestas", 
                                    command=lambda: self.run_script("monitor.py"),
                                    height=50,
                                    font=("Roboto", 16),
                                    fg_color="#2CC069", hover_color="#249E56") # WhatsApp Green
        btn_monitor.pack(fill="x", padx=40, pady=10)
        
        # 4. Report
        btn_report = ctk.CTkButton(frame, text="📊 4. Enviar Reporte al Admin", 
                                   command=lambda: self.run_script("send_report.py"),
                                   height=50,
                                   font=("Roboto", 16),
                                   fg_color="#8E44AD", hover_color="#732D91") # Purple for stats
        btn_report.pack(fill="x", padx=40, pady=10)
        
        # 5. Logs & Support
        frame_support = ctk.CTkFrame(frame, fg_color="transparent")
        frame_support.pack(fill="x", pady=20)
        
        ctk.CTkButton(frame_support, text="🛠️ Ver Logs", 
                                   command=self.open_logs,
                                   width=150,
                                   fg_color="transparent", border_width=1, border_color="gray").pack(side="left", padx=20)
                                   
        ctk.CTkButton(frame_support, text="🆘 Solicitar Soporte Técnico", 
                                   command=self.request_support,
                                   width=200,
                                   fg_color="#E74C3C", hover_color="#C0392B").pack(side="right", padx=20)
        
        ctk.CTkLabel(frame, text="⚠️ Recuerda cerrar las ventanas del bot antes de cambiar de acción.", text_color="gray").pack(pady=5)

    def open_excel(self):
        excel_path = os.path.abspath(self.config.get('excel_path', 'data/contacts.xlsx'))
        try:
            os.startfile(excel_path)
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo abrir Excel: {e}")

    def run_script(self, script_name):
        # Professional Execution: No black windows, log to file
        log_file = "activity.log"
        
        try:
            # Prepare startup info to hide window (Windows specific)
            startupinfo = None
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Open log file for appending
            with open(log_file, "a") as f:
                f.write(f"\n--- INICIANDO {script_name} ---\n")
                
                # Execute in background, directing output to file
                subprocess.Popen(
                    ['python', script_name],
                    stdout=f, 
                    stderr=f,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0
                )
            
            # Show friendly notification
            tk.messagebox.showinfo("Iniciado", f"El proceso {script_name} ha comenzado en segundo plano.\nPuedes seguir usando tu PC.")
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error ejecutando {script_name}: {e}")

    def request_support(self):
        # 1. Get Device ID
        device_id = SecurityManager().get_device_id()
        admin_number = "5212205511054"  # Support Number configured
        
        # 2. Get Last Errors from Log
        log_content = ""
        try:
            if os.path.exists("activity.log"):
                with open("activity.log", "r") as f:
                    lines = f.readlines()
                    # Take last 10 lines
                    log_content = "".join(lines[-10:])
        except:
            log_content = "No logs available."
            
        # 3. Construct Message
        msg = f"Hola Soporte Técnico! 🆘\nNecesito ayuda con el software.\n\n🆔 ID: {device_id}\n\n📝 Últimos registros:\n{log_content}"
        
        # 4. Open WhatsApp Web to send it
        import urllib.parse
        import webbrowser
        
        encoded = urllib.parse.quote(msg)
        webbrowser.open(f"https://web.whatsapp.com/send?phone={admin_number}&text={encoded}")

    def open_logs(self):
        try:
            if os.path.exists("activity.log"):
                os.startfile("activity.log")
            else:
                tk.messagebox.showinfo("Info", "Aún no hay registros de actividad.")
        except:
            pass

if __name__ == "__main__":
    app = WhatsAppAutoApp()
    app.mainloop()
