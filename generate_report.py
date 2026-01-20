import pandas as pd
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, excel_path, admin_number):
        self.excel_path = excel_path
        self.admin_number = admin_number
    
    def generate_summary(self):
        if not os.path.exists(self.excel_path):
            return "No hay datos para generar reporte."
            
        df = pd.read_excel(self.excel_path)
        
        # Filter responses
        interesados = df[df['Estado'] == 'Interesado']
        no_interesados = df[df['Estado'] == 'No Interesado']
        # 'Desconocido' or any other status that is not Pendiente/Enviado/Error
        otros = df[~df['Estado'].isin(['Interesado', 'No Interesado', 'Pendiente', 'Enviado', 'Error'])]
        
        # Build text report
        report = f"*📊 RESUMEN DEL DÍA ({datetime.now().strftime('%H:%M')})*\n\n"
        
        report += f"✅ *Interesados*: {len(interesados)}\n"
        for _, row in interesados.iterrows():
            resp = str(row['Respuesta']) if pd.notna(row['Respuesta']) else "..."
            report += f"- {row['Nombre']}: {resp[:40]}...\n"
            
        report += f"\n❌ *No Interesados*: {len(no_interesados)}\n"
        
        if not otros.empty:
            report += f"\n⚠️ *Por revisar/Desconocido*: {len(otros)}\n"
            for _, row in otros.iterrows():
                resp = str(row['Respuesta']) if pd.notna(row['Respuesta']) else "..."
                report += f"- {row['Nombre']}: {resp[:40]}...\n"
        
        # Count pending (Pendiente OR Enviado because Enviado means no response yet)
        pendientes = df[df['Estado'].isin(['Pendiente', 'Enviado'])]
        report += f"\n⏳ *Sin respuesta aún*: {len(pendientes)}\n"
        
        return report

if __name__ == "__main__":
    # Test
    gen = ReportGenerator("data/contacts.xlsx", "ADMIN")
    print(gen.generate_summary())
