import streamlit as st
import os
from model import DivisionRecommendationSystem
from db import init_db, save_user, save_document
import pandas as pd
import matplotlib.pyplot as plt
import io
import time
from excel_generator import create_excel_report # <-- 1. Import fungsi baru

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

# --- Garis pemisah untuk hasil ---
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
            time.sleep(2)
            
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

            hasil = rekomendasi.get_recommendations(cv_path, cert_paths)
            hasil_persen = [(div, score * 100) for div, score in hasil]
            top_divisi, top_score = hasil_persen[0]

        st.success(f"✅ Analisis untuk **{nama}** selesai!")
        
        st.header("🎯 Hasil Rekomendasi")
        st.subheader(f"Rekomendasi Utama: **{top_divisi}**")
        st.progress(int(top_score))
        st.markdown(f"Tingkat kecocokan mencapai **{top_score:.2f}%**.")
        
        with st.expander("📊 Lihat Rincian Skor dan Grafik"):
            st.subheader("📋 Rincian Skor")
            for div, score in hasil_persen:
                st.write(f"**{div}**: {score:.2f}%")

            st.subheader("Visualisasi")
            df = pd.DataFrame(hasil_persen, columns=["Divisi", "Skor (%)"])
            fig, ax = plt.subplots()
            bars = ax.barh(df["Divisi"], df["Skor (%)"], color='skyblue')
            ax.invert_yaxis()
            ax.set_xlabel("Skor (%)")
            ax.set_title("Grafik Kecocokan Divisi")
            st.pyplot(fig)

        # --- 2. Panggil fungsi untuk membuat Excel ---
        excel_data = create_excel_report(nama, hasil_persen)

        st.download_button(
            label="⬇️ Unduh Laporan Hasil (.xlsx)",
            data=excel_data,
            file_name=f"Hasil_Rekomendasi_{nama.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Silakan isi form di atas dan klik tombol 'Rekomendasikan' untuk memulai.")