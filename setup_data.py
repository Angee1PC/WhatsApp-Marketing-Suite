import pandas as pd
import os

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Sample data
data = {
    'Nombre': ['Juan', 'Maria', 'Carlos'],
    'Telefono': ['1234567890', '0987654321', '1122334455'],
    'Estado': ['Pendiente', 'Pendiente', 'Pendiente'],
    'Respuesta': ['', '', '']
}

df = pd.DataFrame(data)

# Save to Excel
excel_path = os.path.join('data', 'contacts.xlsx')
df.to_excel(excel_path, index=False)

print(f"Sample data created at {excel_path}")
