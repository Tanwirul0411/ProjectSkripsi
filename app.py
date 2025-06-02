# app.py
import streamlit as st
import os
from model import DivisionRecommendationSystem
from db import init_db, save_user, save_document

# Inisialisasi
init_db()
os.makedirs("CV_Mahasiswa", exist_ok=True)
os.makedirs("Sertif_Mahasiswa", exist_ok=True)
rekomendasi = DivisionRecommendationSystem()

st.title("Sistem Rekomendasi Divisi ITCC")

with st.form("upload_form"):
    nama = st.text_input("Nama Mahasiswa")
    email = st.text_input("Email (opsional)")
    cv_file = st.file_uploader("Upload CV (PDF)", type="pdf")
    sertif_files = st.file_uploader("Upload Sertifikat (PDF)", type="pdf", accept_multiple_files=True)
    submitted = st.form_submit_button("Proses Rekomendasi")

if submitted and nama and cv_file:
    user_id = save_user(nama, email)

    # Simpan file CV
    cv_path = os.path.join("CV_Mahasiswa", cv_file.name)
    with open(cv_path, "wb") as f:
        f.write(cv_file.getbuffer())
    save_document(user_id, "CV", cv_file.name, cv_path)

    # Simpan semua sertifikat
    cert_paths = []
    for cert in sertif_files:
        cert_path = os.path.join("Sertif_Mahasiswa", cert.name)
        with open(cert_path, "wb") as f:
            f.write(cert.getbuffer())
        cert_paths.append(cert_path)
        save_document(user_id, "Sertifikat", cert.name, cert_path)

    st.success("File berhasil diupload. Memproses rekomendasi...")

    # Jalankan rekomendasi
    hasil = rekomendasi.get_recommendations(cv_path, cert_paths)

    st.subheader("📋 Hasil Rekomendasi Divisi:")
    for div, score in hasil:
        st.write(f"**{div}**: {score:.4f}")
else:
    st.info("Silakan lengkapi form dan upload minimal CV untuk mulai.")
