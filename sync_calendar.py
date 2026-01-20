from calendar_manager import CalendarManager
import sys
import io
import tkinter.messagebox as messagebox

# Force UTF-8 (Fix for Windows Emoji Crash)
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except:
    pass

def main():
    print("--- INICIANDO SINCRONIZACIÓN DE CALENDARIO ---")
    print("Nota: Si es la primera vez, se abrirá el navegador para login.")
    
    try:
        cm = CalendarManager()
        # Authenticate first
        print("Autenticando con Google...")
        cm.authenticate()
        
        # Sync
        print("Buscando eventos para MAÑANA...")
        added = cm.sync_to_excel()
        
        msg = f"[OK] Sincronización Exitosa.\nSe encontraron y agregaron {added} citas nuevas al Excel.\n\nAhora puedes ir al paso 2: Enviar Mensajes."
        print(msg)
        return True
        
    except FileNotFoundError as e:
        print(f"[ERROR] ARCHIVO NO ENCONTRADO: {e}")
        print("Por favor coloca el archivo 'credentials.json' de Google Cloud en la carpeta del proyecto.")
    except Exception as e:
        print(f"[ERROR] INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
