import streamlit as st
import os
from model import DivisionRecommendationSystem
from db import init_db, save_user, save_document
import pandas as pd
import matplotlib.pyplot as plt
import io
import xlsxwriter

# Inisialisasi
init_db()
os.makedirs("CV_Mahasiswa", exist_ok=True)
os.makedirs("Sertif_Mahasiswa", exist_ok=True)
rekomendasi = DivisionRecommendationSystem()

st.title("IMPLEMENTASI PENDEKATAN BERT DAN COSINE SIMILARITY PADA OPTIMASI PENEMPATAN PEGAWAI (STUDI KASUS ITCC ITPLN)")
st.markdown("<br>", unsafe_allow_html=True)

with st.form("upload_form"):
    nama = st.text_input("Nama Mahasiswa")
    email = st.text_input("Email (opsional)")
    cv_file = st.file_uploader("Upload CV (PDF)", type="pdf")
    
    sertif_files = st.file_uploader(
        "Upload Sertifikat (opsional, maks. 3 file, PDF)",
        type="pdf",
        accept_multiple_files=True
    )

    if sertif_files and len(sertif_files) > 3:
        st.warning("⚠️ Maksimal hanya boleh mengunggah 3 sertifikat. Yang lainnya akan diabaikan.")
        sertif_files = sertif_files[:3]

    submitted = st.form_submit_button("Rekomendasikan")

if submitted and nama and cv_file:
    user_id = save_user(nama, email)

    cv_path = os.path.join("CV_Mahasiswa", cv_file.name)
    with open(cv_path, "wb") as f:
        f.write(cv_file.getbuffer())
    save_document(user_id, "CV", cv_file.name, cv_path)

    cert_paths = []
    for cert in sertif_files:
        cert_path = os.path.join("Sertif_Mahasiswa", cert.name)
        with open(cert_path, "wb") as f:
            f.write(cert.getbuffer())
        cert_paths.append(cert_path)
        save_document(user_id, "Sertifikat", cert.name, cert_path)

    st.success("File berhasil diupload. Memproses rekomendasi...")

    hasil = rekomendasi.get_recommendations(cv_path, cert_paths)
    hasil_persen = [(div, score * 100) for div, score in hasil]
    top_divisi, top_score = hasil_persen[0]
    st.markdown(f"### 🎯 Divisi yang disarankan: **{top_divisi}** ({top_score:.2f}%)")
    st.markdown("---")

    st.subheader("📋 Hasil Rekomendasi Divisi:")
    for div, score in hasil_persen:
        st.write(f"**{div}**: {score:.2f}%")

    # Visualisasi
    st.subheader("📊 Visualisasi Skor Rekomendasi")
    df = pd.DataFrame(hasil_persen, columns=["Divisi", "Skor (%)"])

    fig, ax = plt.subplots()
    bars = ax.barh(df["Divisi"], df["Skor (%)"], color='skyblue')

    # Tambahkan label persen pada bar
    for bar in bars:
        width = bar.get_width()
        ax.text(width -12,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.2f}%",
                color='white', fontweight='bold',
                va='center')

    ax.invert_yaxis()
    ax.set_xlabel("Skor (%)")
    ax.set_title("Visualisasi Kecocokan Divisi")

    st.pyplot(fig)

    # Simpan ke Excel dengan chart pada sheet terpisah
    df_hasil = pd.DataFrame(hasil_persen, columns=["Divisi", "Skor (%)"])
    max_score = df_hasil["Skor (%)"].max()
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: Rekomendasi
        df_hasil.to_excel(writer, index=False, sheet_name='Rekomendasi')
        workbook = writer.book
        worksheet_data = writer.sheets['Rekomendasi']

        # Header format
        header_format = workbook.add_format({'bold': True})
        worksheet_data.set_row(0, None, header_format)

        # Format persentase
        percent_format = workbook.add_format({'num_format': '0.00"%"', 'align': 'center'})
        worksheet_data.set_column(1, 1, 12, percent_format)

        # Highlight baris dengan skor tertinggi
        highlight_format_text = workbook.add_format({
            'bg_color': '#C6EFCE',
            'font_color': '#006100',
            'bold': True
        })

        highlight_format_percent = workbook.add_format({
            'bg_color': '#C6EFCE',
            'font_color': '#006100',
            'bold': True,
            'num_format': '#,##0.00"%"',
            'align': 'center'
        })

        # Sheet 2: Chart Rekomendasi
        for row_num, value in enumerate(df_hasil["Skor (%)"], start=1):
            if value == max_score:
                # Tulis ulang nama divisi (kolom 0)
                worksheet_data.write(row_num, 0, df_hasil["Divisi"][row_num - 1], highlight_format_text)
                # Tulis ulang skor (kolom 1) dengan format persen
                worksheet_data.write_number(row_num, 1, value, highlight_format_percent)

                # Buat chartsheet (bukan worksheet biasa)
                chartsheet = workbook.add_chartsheet('Chart Rekomendasi')

                # Buat chart seperti biasa
                chart = workbook.add_chart({'type': 'bar'})

                chart.add_series({
                    'name': 'Skor (%)',
                    'categories': ['Rekomendasi', 1, 0, len(df_hasil), 0],
                    'values':     ['Rekomendasi', 1, 1, len(df_hasil), 1],
                    'data_labels': {'value': True, 'num_format': '0.00"%"'},
                    'fill': {'color': '#5DADE2'},
                })

                chart.set_title({'name': 'Visualisasi Rekomendasi Divisi di ITCC'})
                chart.set_x_axis({'name': 'Skor (%)', 'num_format': '0.00"%"'})
                chart.set_y_axis({'name': 'Divisi'})
                chart.set_legend({'position': 'right'})
                chart.set_style(8)

                # Sisipkan chart ke chartsheet (langsung penuh layar)
                chartsheet.set_chart(chart)

    writer.close()
    output.seek(0)
    excel_data = output.getvalue()

    st.download_button(
        label="⬇️ Download Hasil Rekomendasi (.xlsx)",
        data=excel_data,
        file_name=f"Hasil_Rekomendasi_{nama.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Silakan lengkapi form dan upload minimal CV untuk mulai.")