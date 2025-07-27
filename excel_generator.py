# excel_generator.py
import pandas as pd
import io
import xlsxwriter

def create_excel_report(nama_kandidat, data_hasil):
    """
    Membuat laporan hasil rekomendasi dalam format Excel dengan dua sheet.

    Args:
        nama_kandidat (str): Nama kandidat untuk judul chart.
        data_hasil (list): Daftar tuple berisi (divisi, skor).

    Returns:
        bytes: Data file Excel dalam bentuk bytes.
    """
    df_hasil = pd.DataFrame(data_hasil, columns=["Divisi", "Skor (%)"])
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: Menulis data rekomendasi
        df_hasil.to_excel(writer, index=False, sheet_name='Rekomendasi')

        # Dapatkan workbook
        workbook = writer.book
        
        # Tambahkan sheet baru untuk chart (sebagai chartsheet)
        chartsheet = workbook.add_chartsheet('Diagram Batang')

        # Buat objek chart baru
        chart = workbook.add_chart({'type': 'bar'})

        # Konfigurasi data series untuk chart dari sheet 'Rekomendasi'
        num_rows = len(df_hasil)
        chart.add_series({
            'name':       ['Rekomendasi', 0, 1],  # Nama dari header kolom Skor
            'categories': ['Rekomendasi', 1, 0, num_rows, 0],  # Label Divisi
            'values':     ['Rekomendasi', 1, 1, num_rows, 1],  # Nilai Skor
        })

        # Konfigurasi tampilan chart
        chart.set_title({'name': f'Hasil Rekomendasi untuk {nama_kandidat}'})
        chart.set_x_axis({'name': 'Skor (%)'})
        chart.set_y_axis({'name': 'Divisi', 'reverse': True})
        chart.set_legend({'position': 'none'})

        # Sisipkan chart ke dalam chartsheet
        chartsheet.set_chart(chart)

    return output.getvalue()