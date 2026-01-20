import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
import threading
import time

# Module Imports
import main as main_script
import monitor as monitor_script
import send_report as report_script
import sync_calendar as calendar_script
from templates_manager import TemplateManager
from security import SecurityManager

# --- Global Logger Setup ---
# Captures all print statements to activity.log
if not hasattr(sys, "original_stdout"):
    sys.original_stdout = sys.stdout

class AppLogger:
    def __init__(self, file_path):
        self.file_path = file_path
        
    def write(self, message):
        try:
            # Write to file - safe with utf-8
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(message)
        except:
            pass
            
        # Write to original stdout - unsafe on Windows
        if sys.original_stdout:
            try: 
                sys.original_stdout.write(message)
            except UnicodeEncodeError:
                # Fallback for console: strip non-ascii to prevent crash
                try:
                    sys.original_stdout.write(message.encode('ascii', 'ignore').decode('ascii'))
                except:
                    pass
            except Exception:
                pass

    def flush(self):
        if sys.original_stdout:
            try: sys.original_stdout.flush() 
            except: pass

# Redirect Sys Output globally
logger = AppLogger("activity.log")
sys.stdout = logger
sys.stderr = logger

# Configuration for Modern UI
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class LoginDialog(ctk.CTkToplevel):
    def __init__(self, parent, security_mgr):
        super().__init__(parent)
        self.security = security_mgr
        self.title("Licencia Requerida 🔒")
        self.geometry("400x350")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.device_id = self.security.get_device_id()
        self.authenticated = False
        
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
        
        # Ensure 'data' directory exists
        if not os.path.exists("data"):
            os.makedirs("data")
            
        self.security = SecurityManager()
        saved_key = self.security.load_license()
        
        if not saved_key or not self.security.validate_key(saved_key):
            self.withdraw() # Hide until login
            login = LoginDialog(self, self.security)
            self.wait_window(login)
            
            if not login.authenticated:
                sys.exit()
            
            self.deiconify()
            
        self.title("WhatsApp Automation Suite PRO 🚀")
        self.geometry("800x700")
        self.minsize(600, 600)
        
        self.config = self.load_config()
        
        # Ensure default excel path exists in config
        if 'excel_path' not in self.config:
            self.config['excel_path'] = os.path.join(os.getcwd(), 'data', 'contacts.xlsx')
            try:
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4)
            except:
                pass
                
        if 'session_path' not in self.config:
            self.config['session_path'] = 'session_data'
            try:
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=4)
            except:
                pass

        # Defaults for timeouts
        if 'scan_timeout' not in self.config:
            self.config['scan_timeout'] = 60
        if 'wait_between_messages' not in self.config:
            self.config['wait_between_messages'] = [5, 10]
            
        # Save updated config
        try:
             with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except:
            pass
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Layout (Tabs) - Removed fixed size to adapt to window
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.tab_config = self.tab_view.add("⚙️ Configuración")
        self.tab_actions = self.tab_view.add("🚀 Panel de Control")
        
        self.setup_config_tab()
        self.setup_actions_tab()
        
        # Clean exit protocol
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        # Force kill leftover processes to ensure clean exit
        try:
             import subprocess
             if os.name == 'nt':
                 subprocess.run("taskkill /f /im chromedriver.exe", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        except:
            pass
        self.destroy()
        sys.exit(0)

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
            print("Configuración guardada")
            tk.messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def setup_config_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_config)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Configuración General", font=("Roboto", 20, "bold")).pack(pady=10)
        
        ctk.CTkLabel(frame, text="Número Admin (Tu WhatsApp):").pack(anchor="w", padx=20)
        self.entry_admin = ctk.CTkEntry(frame, placeholder_text="Ej: 521...")
        self.entry_admin.insert(0, self.config.get('admin_number', ''))
        self.entry_admin.pack(anchor="w", padx=20, pady=(0, 10), fill="x")
        
        ctk.CTkLabel(frame, text="Objetivo del Mensaje (Sugerencias):", font=("Roboto", 14, "bold")).pack(anchor="w", padx=20, pady=(5, 5))
        
        self.combo_type = ctk.CTkComboBox(frame, 
                                          values=["Ventas (Producto/Inmueble)", "Citas (Reservar/Confirmar)"], 
                                          command=self.update_suggestions_event)
        self.combo_type.pack(anchor="w", padx=20, pady=5, fill="x")
        
        ctk.CTkLabel(frame, text="Click en una sugerencia para usarla:").pack(anchor="w", padx=20, pady=5)
        self.scroll_suggestions = ctk.CTkFrame(frame)
        self.scroll_suggestions.pack(padx=20, pady=5, fill="x")
        
        ctk.CTkLabel(frame, text="Mensaje Final (Editable):", font=("Roboto", 14, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        # Textbox: fill="x" only (not expand=True) to avoid layout issues in ScrollableFrame
        self.text_template = ctk.CTkTextbox(frame, height=150)
        self.text_template.insert("0.0", self.config.get('message_template', ''))
        self.text_template.pack(padx=20, pady=5, fill="x")
        
        ctk.CTkButton(frame, text="💾 Guardar Configuración", command=self.save_settings, height=40, font=("Roboto", 14, "bold")).pack(pady=15, fill="x", padx=20)

    def update_suggestions_event(self, choice):
        for widget in self.scroll_suggestions.winfo_children():
            widget.destroy()
            
        suggestions = TemplateManager.get_suggestions(choice)
        
        for i, text in enumerate(suggestions):
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
        
        ctk.CTkLabel(frame, text="Opcional: Importar desde Google", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(10,0))
        btn_sync = ctk.CTkButton(frame, text="📅 Importar Citas (Hoy/Mañana) al Excel", 
                                  command=lambda: self.run_task_thread("Sincronizar", calendar_script.main),
                                  height=40,
                                  font=("Roboto", 14),
                                  fg_color="#3498DB", hover_color="#2980B9")
        btn_sync.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(frame, text="Paso 1: Configura tus datos", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(15,0))
        btn_excel = ctk.CTkButton(frame, text="📂 1. Abrir Lista Excel (Contactos)", 
                                  command=self.open_excel,
                                  height=40,
                                  font=("Roboto", 16),
                                  fg_color="#E0AA3E", hover_color="#C4922F")
        btn_excel.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(frame, text="⚠️ IMPORTANTE: Asegúrate que la columna 'Estado' diga 'Pendiente'\npara los contactos a los que quieres enviar mensaje.", 
                     font=("Roboto", 12), text_color="#E74C3C").pack(padx=40, pady=5)
        
        ctk.CTkLabel(frame, text="Paso 2: Ejecuta el envío", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(15,0))
        btn_send = ctk.CTkButton(frame, text="📤 2. Iniciar Envío Masivo", 
                                 command=lambda: self.run_task_thread("Envío Masivo", main_script.main, wait_for_input=False),
                                 height=40,
                                 font=("Roboto", 16))
        btn_send.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(frame, text="Paso 3: Espera respuestas", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(15,0))
        # Monitor button (uses Start Monitor logic, not run_task_thread)
        btn_monitor = ctk.CTkButton(frame, text="👂 3. Iniciar Monitor (Recibir Respuestas)", 
                                    command=self.start_monitor,
                                    height=40,
                                    font=("Roboto", 16),
                                    fg_color="#2CC069", hover_color="#249E56")
        btn_monitor.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(frame, text="💡 Las respuestas se guardarán automáticamente en el Excel.", font=("Roboto", 11), text_color="gray").pack(padx=40)
        
        ctk.CTkLabel(frame, text="Paso 4: Resultados", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(15,0))
        btn_report = ctk.CTkButton(frame, text="📊 4. Enviar Reporte al Admin", 
                                   command=lambda: self.run_task_thread("Reporte", report_script.send_report, wait_for_input=False),
                                   height=40,
                                   font=("Roboto", 16),
                                   fg_color="#8E44AD", hover_color="#732D91")
        btn_report.pack(fill="x", padx=40, pady=5)
        
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
        # Ensure data folder exists
        data_dir = os.path.join(os.getcwd(), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        excel_path = os.path.abspath(self.config.get('excel_path', os.path.join(data_dir, 'contacts.xlsx')))
        
        # Check if file exists, if not, create a dummy one or warn
        if not os.path.exists(excel_path):
            try:
                with open(excel_path.replace('.xlsx', '.csv'), 'w') as f:
                    f.write("Nombre,Telefono,Estado,Fecha de Cita,Servicio\nEjemplo,525500000000,Pendiente,10/10/2024,Corte")
                tk.messagebox.showwarning("Archivo Nuevo", "Se ha creado un archivo de ejemplo en 'data/contacts.csv'.\nPor favor ábrelo y guárdalo como Excel (.xlsx).")
                excel_path = excel_path.replace('.xlsx', '.csv')
            except Exception as e:
                print(f"Failed to create dummy file: {e}")

        try:
            os.startfile(excel_path)
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo abrir Excel: {e}")

    def start_monitor(self):
        # Start monitor thread without blocking or waiting for return
        self.configure(cursor="watch")
        threading.Thread(target=monitor_script.run_monitor, daemon=True).start()
        
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] MONITOR INICIADO EN PREGUNTO PLANO...")
        tk.messagebox.showinfo("Monitor Iniciado", "El monitor se está ejecutando en segundo plano.\nRevisará mensajes cada 10 segundos.\n\nPuedes ver la actividad en 'Ver Logs'.")
        self.configure(cursor="")

    def run_task_thread(self, task_name, func, **kwargs):
        """Runs a python function in a separate thread."""
        self.configure(cursor="watch")
        threading.Thread(target=self._execute_task, args=(task_name, func), kwargs=kwargs, daemon=True).start()

    def _execute_task(self, task_name, func, **kwargs):
        log_file = "activity.log"
        start_pos = 0
        
        # Get current log size to read only new output later
        try:
            if os.path.exists(log_file):
                start_pos = os.path.getsize(log_file)
        except:
            pass

        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] STARTING TASK: {task_name}")
        
        success = False
        try:
            # Execute the function
            result = func(**kwargs)
            
            # If function returns boolean, use it as success
            if isinstance(result, bool):
                success = result
            else:
                success = True
                
        except Exception as e:
            print(f"\nCRITICAL ERROR in {task_name}: {e}")
            import traceback
            traceback.print_exc()
            success = False
        
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] TASK FINISHED: {task_name}")
        
        # Read new output from file
        output_txt = ""
        try:
             if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    f.seek(start_pos)
                    output_txt = f.read()
        except Exception as e:
            output_txt = f"Could not read logs: {e}"

        # Update GUI
        self.after(0, lambda: self._show_feedback(task_name, success, output_txt))

    def _show_feedback(self, task_name, success, output):
        self.configure(cursor="")
        
        display_text = output[-1000:] if len(output) > 1000 else output
        
        if success:
            tk.messagebox.showinfo(f"{task_name} Finalizado", f"✅ Proceso completado.\n\nDetalles recientes:\n{display_text}")
        else:
            tk.messagebox.showerror(f"Error en {task_name}", f"❌ Ocurrió un error.\n\nDetalles:\n{display_text}")

    def request_support(self):
        device_id = SecurityManager().get_device_id()
        admin_number = "5212205511054"
        
        log_content = ""
        try:
            if os.path.exists("activity.log"):
                with open("activity.log", "r") as f:
                    lines = f.readlines()
                    log_content = "".join(lines[-10:])
        except:
            log_content = "No logs available."
            
        msg = f"Hola Soporte Técnico! 🆘\nNecesito ayuda con el software.\n\n🆔 ID: {device_id}\n\n📝 Últimos registros:\n{log_content}"
        
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
# Configuration for Modern UI
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class LoginDialog(ctk.CTkToplevel):
    def __init__(self, parent, security_mgr):
        super().__init__(parent)
        self.security = security_mgr
        self.title("Licencia Requerida 🔒")
        self.geometry("400x350")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.device_id = self.security.get_device_id()
        self.authenticated = False
        
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
        
        # Ensure 'data' directory exists
        if not os.path.exists("data"):
            os.makedirs("data")
            
        self.security = SecurityManager()
        saved_key = self.security.load_license()
        
        if not saved_key or not self.security.validate_key(saved_key):
            self.withdraw()
            login = LoginDialog(self, self.security)
            self.wait_window(login)
            
            if not login.authenticated:
                sys.exit()
            
            self.deiconify()
            
        self.title("WhatsApp Automation Suite PRO 🚀")
        self.geometry("800x700")
        self.minsize(600, 600)
        
        self.config = self.load_config()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

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
            print("Configuración guardada")
            tk.messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def setup_config_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_config)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Configuración General", font=("Roboto", 20, "bold")).pack(pady=10)
        
        ctk.CTkLabel(frame, text="Número Admin (Tu WhatsApp):").pack(anchor="w", padx=20)
        self.entry_admin = ctk.CTkEntry(frame, placeholder_text="Ej: 521...")
        self.entry_admin.insert(0, self.config.get('admin_number', ''))
        self.entry_admin.pack(anchor="w", padx=20, pady=(0, 10), fill="x")
        
        ctk.CTkLabel(frame, text="Objetivo del Mensaje (Sugerencias):", font=("Roboto", 14, "bold")).pack(anchor="w", padx=20, pady=(5, 5))
        
        self.combo_type = ctk.CTkComboBox(frame, 
                                          values=["Ventas (Producto/Inmueble)", "Citas (Reservar/Confirmar)"], 
                                          command=self.update_suggestions_event)
        self.combo_type.pack(anchor="w", padx=20, pady=5, fill="x")
        
        ctk.CTkLabel(frame, text="Click en una sugerencia para usarla:").pack(anchor="w", padx=20, pady=5)
        self.scroll_suggestions = ctk.CTkScrollableFrame(frame, height=120, label_text="Sugerencias")
        self.scroll_suggestions.pack(padx=20, pady=5, fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="Mensaje Final (Editable):", font=("Roboto", 14, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        self.text_template = ctk.CTkTextbox(frame, height=100)
        self.text_template.insert("0.0", self.config.get('message_template', ''))
        self.text_template.pack(padx=20, pady=5, fill="both", expand=True)
        
        ctk.CTkButton(frame, text="💾 Guardar Configuración", command=self.save_settings, height=40, font=("Roboto", 14, "bold")).pack(pady=15, fill="x", padx=20)

    def update_suggestions_event(self, choice):
        for widget in self.scroll_suggestions.winfo_children():
            widget.destroy()
            
        suggestions = TemplateManager.get_suggestions(choice)
        
        for i, text in enumerate(suggestions):
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
        
        ctk.CTkLabel(frame, text="Opcional: Importar desde Google", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(10,0))
        btn_sync = ctk.CTkButton(frame, text="📅 Importar Citas (Hoy/Mañana) al Excel", 
                                  command=lambda: self.run_task_thread("Sincronizar", calendar_script.main),
                                  height=40,
                                  font=("Roboto", 14),
                                  fg_color="#3498DB", hover_color="#2980B9")
        btn_sync.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(frame, text="Paso 1: Configura tus datos", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(15,0))
        btn_excel = ctk.CTkButton(frame, text="📂 1. Abrir Lista Excel (Contactos)", 
                                  command=self.open_excel,
                                  height=40,
                                  font=("Roboto", 16),
                                  fg_color="#E0AA3E", hover_color="#C4922F")
        btn_excel.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(frame, text="⚠️ IMPORTANTE: Asegúrate que la columna 'Estado' diga 'Pendiente'\npara los contactos a los que quieres enviar mensaje.", 
                     font=("Roboto", 12), text_color="#E74C3C").pack(padx=40, pady=5)
        
        ctk.CTkLabel(frame, text="Paso 2: Ejecuta el envío", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(15,0))
        btn_send = ctk.CTkButton(frame, text="📤 2. Iniciar Envío Masivo", 
                                 command=lambda: self.run_task_thread("Envío Masivo", main_script.main, wait_for_input=False),
                                 height=40,
                                 font=("Roboto", 16))
        btn_send.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(frame, text="Paso 3: Espera respuestas", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(15,0))
        btn_monitor = ctk.CTkButton(frame, text="👂 3. Iniciar Monitor (Recibir Respuestas)", 
                                    command=lambda: self.run_task_thread("Monitor (20s check)", monitor_script.run_monitor),
                                    height=40,
                                    font=("Roboto", 16),
                                    fg_color="#2CC069", hover_color="#249E56")
        btn_monitor.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(frame, text="💡 Las respuestas se guardarán automáticamente en el Excel.", font=("Roboto", 11), text_color="gray").pack(padx=40)
        
        ctk.CTkLabel(frame, text="Paso 4: Resultados", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(15,0))
        btn_report = ctk.CTkButton(frame, text="📊 4. Enviar Reporte al Admin", 
                                   command=lambda: self.run_task_thread("Reporte", report_script.send_report, wait_for_input=False),
                                   height=40,
                                   font=("Roboto", 16),
                                   fg_color="#8E44AD", hover_color="#732D91")
        btn_report.pack(fill="x", padx=40, pady=5)
        
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
        # Ensure data folder exists
        data_dir = os.path.join(os.getcwd(), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        excel_path = os.path.abspath(self.config.get('excel_path', os.path.join(data_dir, 'contacts.xlsx')))
        
        # Check if file exists, if not, create a dummy one or warn
        if not os.path.exists(excel_path):
            with open(excel_path.replace('.xlsx', '.csv'), 'w') as f:
                f.write("Nombre,Telefono,Estado,Fecha de Cita,Servicio\nEjemplo,525500000000,Pendiente,10/10/2024,Corte")
            tk.messagebox.showwarning("Archivo Nuevo", "Se ha creado un archivo de ejemplo en 'data/contacts.csv'.\nPor favor ábrelo y guárdalo como Excel (.xlsx).")
            excel_path = excel_path.replace('.xlsx', '.csv')

        try:
            os.startfile(excel_path)
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo abrir Excel: {e}")

    def run_task_thread(self, task_name, func, **kwargs):
        """Runs a python function in a separate thread and captures output."""
        self.configure(cursor="watch")
        threading.Thread(target=self._execute_task, args=(task_name, func), kwargs=kwargs, daemon=True).start()

    def _execute_task(self, task_name, func, **kwargs):
        log_file = "activity.log"
        output_buffer = io.StringIO()
        success = False
        
        # Capture stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = output_buffer
        sys.stderr = output_buffer
        
        try:
            print(f"--- STARTING: {task_name} ---")
            # Execute the function
            # Check if function accepts arguments
            result = func(**kwargs)
            
            # If function returns boolean, use it as success
            if isinstance(result, bool):
                success = result
            else:
                success = True # Assume success if no error raised
                
        except Exception as e:
            print(f"\nCRITICAL ERROR in {task_name}: {e}")
            import traceback
            traceback.print_exc()
            success = False
        finally:
            # Restore stdout
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        output_txt = output_buffer.getvalue()
        
        # Write to log file
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] EXEC {task_name}\n")
                f.write(output_txt)
                f.write("-" * 30 + "\n")
        except:
            pass # Failing to log shouldn't crash app
            
        # Update GUI
        self.after(0, lambda: self._show_feedback(task_name, success, output_txt))

    def _show_feedback(self, task_name, success, output):
        self.configure(cursor="")
        
        display_text = output[-800:] if len(output) > 800 else output
        
        if success:
            tk.messagebox.showinfo(f"{task_name} Finalizado", f"✅ Proceso completado.\n\nÚltimos detalles:\n{display_text}")
        else:
            tk.messagebox.showerror(f"Error en {task_name}", f"❌ Ocurrió un error.\n\nDetalles:\n{display_text}")

    def request_support(self):
        device_id = SecurityManager().get_device_id()
        admin_number = "5212205511054"
        
        log_content = ""
        try:
            if os.path.exists("activity.log"):
                with open("activity.log", "r") as f:
                    lines = f.readlines()
                    log_content = "".join(lines[-10:])
        except:
            log_content = "No logs available."
            
        msg = f"Hola Soporte Técnico! 🆘\nNecesito ayuda con el software.\n\n🆔 ID: {device_id}\n\n📝 Últimos registros:\n{log_content}"
        
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
        
        # Action Buttons Layout - LOGICAL FLOW
        
        # Action Buttons Layout - LOGICAL FLOW
        
        # Optional: Calendar Sync
        ctk.CTkLabel(frame, text="Opcional: Importar desde Google", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(10,0))
        btn_sync = ctk.CTkButton(frame, text="📅 Importar Citas (Hoy/Mañana) al Excel", 
                                  command=lambda: self.run_script_with_feedback("sync_calendar.py"),
                                  height=40,
                                  font=("Roboto", 14),
                                  fg_color="#3498DB", hover_color="#2980B9") # Blue
        btn_sync.pack(fill="x", padx=40, pady=5)
        
        # 1. Edit Excel
        ctk.CTkLabel(frame, text="Paso 1: Configura tus datos", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(15,0))
        btn_excel = ctk.CTkButton(frame, text="📂 1. Abrir Lista Excel (Contactos)", 
                                  command=self.open_excel,
                                  height=40,
                                  font=("Roboto", 16),
                                  fg_color="#E0AA3E", hover_color="#C4922F") # Yellowish for file
        btn_excel.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(frame, text="⚠️ IMPORTANTE: Asegúrate que la columna 'Estado' diga 'Pendiente'\npara los contactos a los que quieres enviar mensaje.", 
                     font=("Roboto", 12), text_color="#E74C3C").pack(padx=40, pady=5)
        
        # 2. Send Messages
        ctk.CTkLabel(frame, text="Paso 2: Ejecuta el envío", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(15,0))
        btn_send = ctk.CTkButton(frame, text="📤 2. Iniciar Envío Masivo", 
                                 command=lambda: self.run_script("main.py"),
                                 height=40,
                                 font=("Roboto", 16))
        btn_send.pack(fill="x", padx=40, pady=5)
        
        # 3. Monitor
        ctk.CTkLabel(frame, text="Paso 3: Espera respuestas", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(15,0))
        btn_monitor = ctk.CTkButton(frame, text="👂 3. Iniciar Monitor (Recibir Respuestas)", 
                                    command=lambda: self.run_script("monitor.py"),
                                    height=40,
                                    font=("Roboto", 16),
                                    fg_color="#2CC069", hover_color="#249E56") # WhatsApp Green
        btn_monitor.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(frame, text="💡 Las respuestas se guardarán automáticamente en el Excel.", font=("Roboto", 11), text_color="gray").pack(padx=40)
        
        # 4. Report
        ctk.CTkLabel(frame, text="Paso 4: Resultados", font=("Roboto", 14, "bold"), text_color="gray").pack(anchor="w", padx=40, pady=(15,0))
        btn_report = ctk.CTkButton(frame, text="📊 4. Enviar Reporte al Admin", 
                                   command=lambda: self.run_script_with_feedback("send_report.py"),
                                   height=40,
                                   font=("Roboto", 16),
                                   fg_color="#8E44AD", hover_color="#732D91") # Purple for stats
        btn_report.pack(fill="x", padx=40, pady=5)
        
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
            
    def run_script_with_feedback(self, script_name):
        # Disable interactions or show loading
        self.configure(cursor="watch")
        
        # Run in thread to not freeze GUI
        import threading
        threading.Thread(target=self._execute_thread, args=(script_name,), daemon=True).start()

    def _execute_thread(self, script_name):
        log_file = "activity.log"
        output_txt = ""
        success = False
        
        try:
            startupinfo = None
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Force UTF-8 environment to support Emojis in logs (Fixes Windows charmap errors)
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            result = subprocess.run(
                ['python', script_name],
                capture_output=True,
                encoding='utf-8',     # Read output as UTF-8
                errors='replace',     # Replace unreadable chars instead of crashing
                startupinfo=startupinfo,
                env=env,              # Apply env var
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0
            )  
            
            output_txt = result.stdout + "\n" + result.stderr
            success = (result.returncode == 0)
            
            # Log it
            with open(log_file, "a") as f:
                f.write(f"\n--- EXEC {script_name} ---\n{output_txt}\n")

        except Exception as e:
            output_txt = str(e)
            success = False
            
        # Callback to main thread for popup
        self.after(0, lambda: self._show_feedback(script_name, success, output_txt))

    def _show_feedback(self, script_name, success, output):
        self.configure(cursor="")
        
        # Display max 500 chars of result
        display_text = output[-500:] if len(output) > 500 else output
        
        if success:
            tk.messagebox.showinfo("Proceso Terminado", f"✅ {script_name} finalizó correctamente.\n\nResultado:\n{display_text}")
        else:
            tk.messagebox.showerror("Error", f"❌ {script_name} falló.\n\nDetalles:\n{display_text}")

if __name__ == "__main__":
    app = WhatsAppAutoApp()
    app.mainloop()
