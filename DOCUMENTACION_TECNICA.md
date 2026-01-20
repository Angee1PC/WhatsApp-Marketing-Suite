# Documentación Técnica Maestra: WhatsApp Automation Suite PRO 🚀

**Fecha de Última Actualización:** Enero 2026
**Autor:** by AngeeL / Desarrollador
**Versión:** 9.0 (Producción Final)

---

## 1. Visión General del Sistema
Este software es una herramienta de escritorio diseñada para automatizar la comunicación vía WhatsApp Web, integrar citas desde Google Calendar y generar reportes de gestión. Está construido en **Python** con una interfaz gráfica moderna (`customtkinter`) y utiliza **Selenium** para la automatización del navegador.

### Características Principales
*   **Envío Masivo Personalizado**: Lee contactos de Excel y envía mensajes con variables dinámicas (`{Nombre}`).
*   **Integración Google Calendar**: Sincroniza citas próximas y las carga listas para confirmar.
*   **Monitor de Respuestas**: Escucha respuestas entrantes y actualiza el estado (Interesado/No interesado) en Excel.
*   **Sistema de Licencias**: Protegido por ID de Hardware (MAC Address) y claves únicas.
*   **Reportes**: Genera resúmenes automáticos y los envía al administrador.

---

## 2. Arquitectura de Archivos (Estructura del Proyecto)

| Archivo | Función Principal |
| :--- | :--- |
| **`app_gui.py`** | **Núcleo de la App**. Contiene la interfaz gráfica, botones y lógica de procesos en hilos. |
| `wa_bot.py` | **Motor de Automatización**. Controla Chrome mediante Selenium (abrir chat, leer, enviar). |
| `calendar_manager.py`| **Conector Google**. Se autentica con la API de Calendar y extrae eventos. |
| `data_handler.py` | **Gestor de Excel**. Lee/Escribe en `contacts.xlsx`. Maneja estados de mensajes. |
| `security.py` | **Seguridad**. Genera el `Machine ID` y valida el `license.key`. |
| `main.py` | Script que ejecuta el **Envío Masivo**. |
| `monitor.py` | Script que ejecuta el **Monitor de Respuestas**. |
| `send_report.py` | Script que genera y envía el **Reporte de Resultados**. |
| `sync_calendar.py` | Script puente para ejecutar la sincronización de calendario. |
| `templates_manager.py`| Contiene las plantillas de texto para Ventas y Citas. |
| `config.json` | Archivo de configuración (rutas, mensajes, teléfono admin). |
| `credentials.json` | Llave de acceso a Google Cloud (INDISPENSABLE para Calendar). |

---

## 3. Flujo de Datos

### A. Sincronización de Citas
1.  **Usuario** crea evento en Google Calendar (con teléfono en título o descripción).
2.  **App** (`sync_calendar.py`) consulta la API de Google.
3.  Busca eventos desde "Hoy" hasta "3 días después".
4.  Si encuentra un teléfono (10 dígitos), lo formatea (`52` + número).
5.  Verifica si ya existe en `contacts.xlsx`. Si no, lo agrega con estado `Pendiente`.

### B. Envío de Mensajes
1.  **App** (`main.py`) lee `contacts.xlsx`.
2.  Filtra filas donde `Estado == "Pendiente"`.
3.  Abre WhatsApp Web.
4.  Para cada contacto:
    *   Busca el chat o crea enlace directo.
    *   Envía el mensaje templado.
    *   Actualiza el Excel: `Estado` -> `Enviado`.
    *   Espera un tiempo aleatorio (anti-bloqueo).

### C. Monitoreo
1.  **App** (`monitor.py`) escanea la lista de chats en busca del círculo verde (mensaje no leído).
2.  Entra al chat, lee el último mensaje.
3.  Busca al remitente en el Excel.
4.  Clasifica la respuesta (palabras clave "no gracias", "precio", "sí").
5.  Actualiza `contacts.xlsx` (Columna `Interes` y `Ultimo Mensaje`).

---

## 4. Guía de Mantenimiento y Desarrollo

### Requisitos Previos
*   Python 3.9+
*   Google Chrome instalado.
*   Librerías: `selenium`, `customtkinter`, `pandas`, `openpyxl`, `google-api-python-client`, `webdriver-manager`.

### Cómo Actualizar Credenciales de Google
Si el login de calendario falla (`Access Blocked` o error de credenciales):
1.  Ve a [Google Cloud Console](https://console.cloud.google.com/).
2.  Selecciona tu proyecto.
3.  Ve a **APIs & Services > Credentials**.
4.  Crea un nuevo **OAuth 2.0 Client ID** (Tipo: Desktop App).
5.  Descarga el JSON, renómbralo a `credentials.json` y reemplaza el archivo en la carpeta del proyecto.
6.  Borra el archivo `token.pickle` (si existe) para forzar un nuevo login.

### Cómo Modificar Plantillas
1.  Edita `templates_manager.py`.
2.  Asegúrate de mantener el formato de lista `[...]`.
3.  Usa `{Nombre}` tal cual para que el reemplazo automático funcione.

---

## 5. Sistema de Seguridad y Licencias

### Generar una Licencia para un Cliente
Tú (como vendedor) debes usar el script `security.py` para generar claves.

1.  Pídele al cliente su **ID de Dispositivo** (aparece al abrir la App sin licencia).
2.  Abre una terminal en tu PC y ejecuta Python:
    ```python
    from security import SecurityManager
    sm = SecurityManager()
    # Pega el ID del cliente aquí
    print(sm.generate_valid_key("ID_DEL_CLIENTE_AQUI"))
    ```
3.  Copia el código que te devuelve y envíaselo al cliente.

---

## 6. Cómo Generar el Ejecutable (.exe) para Venta

Para entregar el software al cliente sin que vea el código fuente, usa **PyInstaller**.

**Comando de Compilación (Ejecutar en Terminal):**

```bash
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
```

*Nota: Asegúrate de tener `credentials.json` presente antes de compilar.*

El resultado estará en la carpeta `dist/WhatsAppAutoBot`. Esa carpeta completa es la que entregas (puedes hacerle un ZIP o un instalador).

---

## 7. Solución de Problemas Comunes

*   **Error: "Chrome se cerró inesperadamente"**:
    *   Causa: Versión de Chrome incompatible con ChromeDriver.
    *   Solución: Ejecuta `pip install --upgrade webdriver-manager`. El bot lo arregla solo al iniciar.
*   **Error: "UnicodeEncodeError / charmap"**:
    *   Causa: Windows intentando imprimir emojis en consola.
    *   Solución: Ya está parcheado en el código forzando UTF-8, pero si persiste, asegúrate de no usar emojis en `print()` de scripts nuevos.
*   **Calendario no sincroniza**:
    *   Verifica que el evento sea para HOY o los próximos 3 días.
    *   Verifica que tenga un número de 10 dígitos en Descripción o Título.

---

## 8. Guía Rápida para el Usuario Final

*(Copia esto para enviárselo a tu cliente)*

**Pasos para usar tu Bot:**

1.  **Configuración Inicial**:
    *   Abre la App.
    *   Ve a la pestaña "Configuración".
    *   Elige el tipo de mensaje (Ventas o Citas) y personalízalo. Dale Guardar.
    *   (Opcional) Haz clic en "Importar Citas" y conecta tu cuenta de Google.

2.  **Operación Diaria**:
    *   **Paso 1**: Abre el Excel. Revisa que tus contactos tengan estado "Pendiente".
    *   **Paso 2**: Dale a "Iniciar Envío". Se abrirá Chrome, escanea el QR y deja que trabaje hasta terminar.
    *   **Paso 3**: Dale a "Iniciar Monitor". Deja esa ventana minimizada todo el día para que detecte respuestas.
    *   **Paso 4**: Al final del día, dale a "Enviar Reporte" para recibir el resumen en tu celular.

**Reglas de Oro:**
*   Nunca cierres la ventana negra de Chrome manualmente mientras trabaja.
*   Si importas de Google Calendar, pon el teléfono del cliente (10 dígitos) en la descripción del evento.

---
## 9. Historial de Cambios (Changelog)
### Versión V9 (Producción Final) - Enero 2026
*   **Distribución de Archivo Único (.exe)**: Se eliminó la necesidad de carpetas complejas. Ahora el software es un solo archivo "portable" (`WhatsApp_Production_Final_v9.exe`) que contiene todo lo necesario (credenciales, librerías, configuración).
*   **Creación Automática de Datos**: Al ejecutarse en una PC nueva, crea automáticamente la carpeta `data/` y un archivo `contacts.xlsx` de ejemplo si no existen. También genera la configuración por defecto.
*   **Filtro de Privacidad**: El Monitor de Respuestas ahora **ignora** cualquier mensaje que provenga de un número no registrado en el Excel. Esto evita leer mensajes personales del usuario.
*   **Identificación Inteligente**: El Bot ahora entra al perfil del contacto para extraer su número real. Esto permite identificar al cliente aunque el usuario lo tenga guardado con apodos (ej. "Juan Mecánico") en su celular.
*   **Protocolo de Cierre Limpio**: Se programó un cierre forzado de procesos (`chromedriver.exe`) al cerrar la ventana principal, evitando que queden procesos "zombies" consumiendo memoria.
*   **Corrección de Logs**: Se limpiaron los mensajes de error técnicos (Selenium stacktraces) para mostrar logs limpios y comprensibles al usuario.
*   **Formato de Teléfonos**: El sistema añade automáticamente el prefijo `52` si detecta un número de 10 dígitos, facilitando la entrada de datos.

---
**Fin del Documento.**
