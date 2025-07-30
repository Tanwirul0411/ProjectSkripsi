# excel_generator.py
import pandas as pd
import io
import xlsxwriter
from datetime import datetime

def create_excel_report(nama_kandidat, email_kandidat, tanggal_rekomendasi, data_hasil):

    df_hasil = pd.DataFrame(data_hasil, columns=["Divisi", "Skor (%)"])
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        sheet_name_data = 'Rekomendasi'
        sheet_name_chart = 'Visualisasi Chart'

        # --- Sheet 1: Menulis Tabel Data ---
        df_hasil.to_excel(writer, index=False, sheet_name=sheet_name_data, startrow=5) 
        worksheet_data = writer.sheets[sheet_name_data]
        
        # --- Memisahkan Tanggal dan Waktu ---
        format_header = workbook.add_format({'bold': True, 'font_size': 11})
        format_tanggal = workbook.add_format({'num_format': 'dd mmmm yyyy', 'font_size': 11})

        try:
            # Mengubah string timestamp dari DB menjadi objek datetime
            timestamp_obj = datetime.strptime(tanggal_rekomendasi, '%Y-%m-%d %H:%M:%S')
            tanggal_saja = timestamp_obj.date()
            waktu_saja = timestamp_obj.strftime('%H:%M:%S')
        except (ValueError, TypeError):
            # Fallback jika format tidak sesuai
            timestamp_obj = datetime.now()
            tanggal_saja = timestamp_obj.date()
            waktu_saja = timestamp_obj.strftime('%H:%M:%S')

        worksheet_data.write('A1', 'Tanggal Rekomendasi:', format_header)
        worksheet_data.write_datetime('B1', tanggal_saja, format_tanggal)
        
        worksheet_data.write('A2', 'Waktu Rekomendasi:', format_header)
        worksheet_data.write('B2', waktu_saja)

        worksheet_data.write('A3', 'Nama Kandidat:', format_header)
        worksheet_data.write('B3', nama_kandidat)
        
        worksheet_data.write('A4', 'Email Kandidat:', format_header)
        worksheet_data.write('B4', email_kandidat if email_kandidat else 'Tidak diisi')
        
        worksheet_data.set_column('A:A', 25)
        worksheet_data.set_column('B:B', 20)

        # --- Sheet 2: Chart Full Screen ---
        chartsheet = workbook.add_chartsheet(sheet_name_chart)
        chart = workbook.add_chart({'type': 'bar'})

        num_rows = len(df_hasil)
        chart.add_series({
            # Referensi disesuaikan karena tabel bergeser
            'name':       f"='{sheet_name_data}'!$B$6",
            'categories': f"='{sheet_name_data}'!$A$7:$A${num_rows + 6}",
            'values':     f"='{sheet_name_data}'!$B$7:$B${num_rows + 6}",

            'data_labels': {
                'value': True, 
                'position': 'inside_end',
                'num_format': '0.00"%"', 
                'font': {'color': 'white', 'bold': True} 
            }
        })

        chart.set_title({'name': f'Hasil Rekomendasi untuk {nama_kandidat}'})
        chart.set_x_axis({'name': 'Skor (%)'})
        chart.set_y_axis({'name': 'Divisi', 'reverse': True})
        chart.set_legend({'position': 'none'})

        chartsheet.set_chart(chart)

    return output.getvalue()