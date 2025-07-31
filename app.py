# app.py
import streamlit as st
import os
from model import DivisionRecommendationSystem
from db import init_db, save_user, save_document, get_user_info_by_id
import pandas as pd
import matplotlib.pyplot as plt
import io
import time
from excel_generator import create_excel_report

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Sistem Rekomendasi Divisi",
    page_icon="img/itcc_icon.png"
)

# --- Inisialisasi ---
@st.cache_resource
def initialize_system():
    init_db()
    os.makedirs("CV_Mahasiswa", exist_ok=True)
    os.makedirs("Sertif_Mahasiswa", exist_ok=True)
    rekomendasi = DivisionRecommendationSystem()
    return rekomendasi

rekomendasi = initialize_system()

# --- Tampilan Antarmuka (UI) ---
st.image("img/logo_itcc.png", width=300)
st.title("Sistem Rekomendasi Penempatan Pegawai")
st.markdown("Studi Kasus: **ITCC ITPLN**")
st.markdown("---")

# --- Formulir Input ---
st.header("Informasi Kandidat")
with st.form("upload_form"):
    nama = st.text_input("Nama Kandidat", placeholder="Masukkan nama kandidat")
    email = st.text_input("Email (Opsional)", placeholder="contoh@email.com")
    cv_file = st.file_uploader("Unggah CV (Wajib, format PDF)", type="pdf")
    
    sertif_files = st.file_uploader(
        "Unggah Sertifikat (Opsional, format PDF)",
        type="pdf",
        accept_multiple_files=True
    )
    
    submitted = st.form_submit_button("🚀 Rekomendasikan")

st.markdown("---")

# --- Logika Pemrosesan dan Tampilan Hasil ---
if submitted:
    if not nama or not cv_file:
        st.error("⚠️ **Peringatan:** Mohon isi Nama Kandidat dan unggah file CV terlebih dahulu.")
    else:
        if len(sertif_files) > 3:
            st.warning(f"⚠️ **Peringatan:** Anda mengunggah {len(sertif_files)} file sertifikat. Hanya 3 file pertama yang akan diproses.")
            sertif_files = sertif_files[:3]

        with st.spinner('Harap Tunggu, Sedang menganalisis profil kandidat...'):
            # Simpan data user ke DB
            user_id = save_user(nama, email)

            # Simpan file-file yang diunggah
            cv_path = os.path.join("CV_Mahasiswa", cv_file.name)
            with open(cv_path, "wb") as f: f.write(cv_file.getbuffer())
            save_document(user_id, "CV", cv_file.name, cv_path)

            cert_paths = []
            for cert in sertif_files:
                cert_path = os.path.join("Sertif_Mahasiswa", cert.name)
                with open(cert_path, "wb") as f: f.write(cert.getbuffer())
                cert_paths.append(cert_path)
                save_document(user_id, "Sertifikat", cert.name, cert_path)

            # Dapatkan hasil dari model NLP
            hasil = rekomendasi.get_recommendations(cv_path, cert_paths)
            hasil_persen = [(div, score * 100) for div, score in hasil]
            top_divisi, top_score = hasil_persen[0]

            # Ambil info lengkap dari DB untuk laporan
            user_info = get_user_info_by_id(user_id)
            if user_info:
                nama_db, email_db, tanggal_db = user_info
            else:
                nama_db, email_db, tanggal_db = nama, email, "N/A"

        st.success(f"✅ Analisis untuk **{nama_db}** selesai!")
        
        st.header("🎯 Hasil Rekomendasi")
        st.subheader(f"Rekomendasi Utama: **{top_divisi}**")
        progress_value = min(int(top_score), 100)
        st.progress(progress_value)
        st.markdown(f"Tingkat kecocokan mencapai **{top_score:.2f}%**.")
        
        with st.expander("📊 Lihat Rincian Skor dan Grafik"):
            # Expander Untuk Menampilkan Rincian
            st.subheader("📋 Rincian Skor")
            for div, score in hasil_persen:
                st.write(f"**{div}**: {score:.2f}%")
            # ===============================================

            st.subheader("Visualisasi")
            df = pd.DataFrame(hasil_persen, columns=["Divisi", "Skor (%)"])
            fig, ax = plt.subplots() 
            bars = ax.barh(df["Divisi"], df["Skor (%)"], color='skyblue')
            ax.invert_yaxis()
            ax.set_xlabel("Skor (%)")
            ax.set_title("Grafik Kecocokan Divisi")
            for bar in bars:
                width = bar.get_width()
                label_x_pos = width - (width * 0.20)
                ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.2f}%', 
                        va='center', ha='left', color='white', fontweight='bold')
            st.pyplot(fig)

        # Panggil fungsi untuk membuat Excel dengan data dari DB
        excel_data = create_excel_report(
            nama_kandidat=nama_db,
            email_kandidat=email_db,
            tanggal_rekomendasi=tanggal_db,
            data_hasil=hasil_persen
        )

        st.download_button(
            label="⬇️ Unduh Laporan Hasil (.xlsx)",
            data=excel_data,
            file_name=f"Hasil_Rekomendasi_{nama_db.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Silakan isi form di atas dan klik tombol 'Rekomendasikan' untuk memulai.")