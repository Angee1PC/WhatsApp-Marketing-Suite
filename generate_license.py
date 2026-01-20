import sys
from security import SecurityManager

def main():
    print("=== Generador de Licencias para WhatsApp Auto ===")
    print("-" * 50)
    
    try:
        # Instanciar el gestor de seguridad
        sm = SecurityManager()
        
        # Pedir el ID del dispositivo
        device_id = input("Por favor, ingresa el ID del CLIENTE (ej. F9797146): ").strip()
        
        if not device_id:
            print("Error: No ingresaste ningún ID.")
        else:
            # Generar la clave
            license_key = sm.generate_valid_key(device_id)
            
            print("\n" + "="*30)
            print(f"ID Cliente: {device_id}")
            print(f"LICENCIA GENERADA: {license_key}")
            print("="*30)
            print("\nCopia esta licencia y envíala al cliente.")
            
    except Exception as e:
        print(f"\nOcurrió un error: {e}")
    
    print("-" * 50)
    input("Presiona ENTER para salir...")

if __name__ == "__main__":
    main()
