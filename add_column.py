import pandas as pd
import os

excel_path = os.path.join('data', 'contacts.xlsx')

if os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
    
    # Add new column 'Interes' if it doesn't exist
    # Alternating values for variety
    intereses = ['Casas', 'Departamentos', 'Terrenos']
    df['Interes'] = [intereses[i % len(intereses)] for i in range(len(df))]
    
    # Reset status to Pendiente
    df['Estado'] = 'Pendiente'
    
    # Save
    df.to_excel(excel_path, index=False)
    print(f"Updated {excel_path}: Added 'Interes' column and reset status.")
    print(df[['Nombre', 'Interes', 'Estado']])
else:
    print("Excel file not found.")
