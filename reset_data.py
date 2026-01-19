import pandas as pd
import os

excel_path = os.path.join('data', 'contacts.xlsx')
if os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
    df['Estado'] = 'Pendiente'
    df.to_excel(excel_path, index=False)
    print(f"Status reset to 'Pendiente' in {excel_path}")
else:
    print("File not found.")
