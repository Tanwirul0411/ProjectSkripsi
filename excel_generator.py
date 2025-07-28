# excel_generator.py
import pandas as pd
import io
import xlsxwriter
from datetime import date

def create_excel_report(nama_kandidat, email_kandidat, tanggal_rekomendasi, data_hasil):
    """
    Membuat laporan hasil rekomendasi dalam format Excel dengan dua sheet terpisah:
    1. Sheet 'Rekomendasi' untuk tabel data.
    2. Sheet 'Visualisasi Chart' untuk grafik bar (mode full screen).

    Args:
        nama_kandidat (str): Nama kandidat.
        email_kandidat (str): Email kandidat.
        tanggal_rekomendasi (str): Tanggal proses rekomendasi.
        data_hasil (list): Daftar tuple berisi (divisi, skor).

    Returns:
        bytes: Data file Excel dalam bentuk bytes.
    """
    df_hasil = pd.DataFrame(data_hasil, columns=["Divisi", "Skor (%)"])
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        sheet_name_data = 'Rekomendasi'
        sheet_name_chart = 'Chart Rekomendasi'

        # --- Sheet 1: Menulis Tabel Data ---
        df_hasil.to_excel(writer, index=False, sheet_name=sheet_name_data, startrow=4)
        worksheet_data = writer.sheets[sheet_name_data]
        
        format_header = workbook.add_format({'bold': True, 'font_size': 11})
        worksheet_data.write('A1', 'Tanggal Rekomendasi:', format_header)
        worksheet_data.write('B1', tanggal_rekomendasi)
        worksheet_data.write('A2', 'Nama Kandidat:', format_header)
        worksheet_data.write('B2', nama_kandidat)
        worksheet_data.write('A3', 'Email Kandidat:', format_header)
        worksheet_data.write('B3', email_kandidat if email_kandidat else 'Tidak diisi')
        
        worksheet_data.set_column('A:A', 25)
        worksheet_data.set_column('B:B', 15)

        # 1. Buat chartsheet baru (sheet khusus untuk chart)
        chartsheet = workbook.add_chartsheet(sheet_name_chart)

        # 2. Buat objek chart
        chart = workbook.add_chart({'type': 'bar'})

        # 3. Konfigurasi data series, pastikan referensi menuju ke sheet data ('Rekomendasi')
        num_rows = len(df_hasil)
        chart.add_series({
            'name':       f"='{sheet_name_data}'!$B$5",
            'categories': f"='{sheet_name_data}'!$A$6:$A${num_rows + 5}",
            'values':     f"='{sheet_name_data}'!$B$6:$B${num_rows + 5}",
        })

        # 4. Konfigurasi tampilan chart
        chart.set_title({'name': f'Hasil Rekomendasi untuk {nama_kandidat}'})
        chart.set_x_axis({'name': 'Skor (%)'})
        chart.set_y_axis({'name': 'Divisi', 'reverse': True})
        chart.set_legend({'position': 'none'})

        # 5. Tempatkan chart ke dalam chartsheet
        chartsheet.set_chart(chart)

    return output.getvalue()