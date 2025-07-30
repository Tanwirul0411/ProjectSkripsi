# model.py
import os
import fitz  # PyMuPDF
import re
import torch
import pandas as pd
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

class DivisionRecommendationSystem:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("indobenchmark/indobert-base-p1")
        self.model = BertModel.from_pretrained("indobenchmark/indobert-base-p1")
        self.divisions = self._load_keywords_from_file('keywords.csv')

    def _load_keywords_from_file(self, file_path):
        """Membaca keywords dari file CSV dan mengubahnya menjadi dictionary."""
        try:
            df = pd.read_csv(file_path)
            divisions_dict = {}
            for division in df['divisi'].unique():
                keywords = df[df['divisi'] == division]['keyword'].tolist()
                divisions_dict[division] = keywords
            return divisions_dict
        except FileNotFoundError:
            print(f"Error: File '{file_path}' tidak ditemukan.")
            return {}
        except KeyError:
            print(f"Error: File '{file_path}' tidak memiliki kolom 'divisi' atau 'keyword'.")
            return {}

    def extract_text(self, pdf_path):
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
        return text

    def clean_text(self, text):
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def get_cls_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        cls_token = outputs.last_hidden_state[:, 0, :]
        return cls_token.squeeze().cpu().numpy()

    def get_recommendations(self, cv_path, certificate_paths=None):
        # LANGKAH 1: Ekstrak dan hitung skor awal
        full_text = self.extract_text(cv_path)
        if certificate_paths:
            for path in certificate_paths:
                full_text += " " + self.extract_text(path)
        
        cleaned_full_text = self.clean_text(full_text)
        user_vector = self.get_cls_embedding(cleaned_full_text)

        results = []
        for div, keywords in self.divisions.items():
            nama_divisi = div.split('(')[0].strip()
            desc_text = f"Kandidat untuk divisi {nama_divisi} harus memiliki keahlian dalam bidang berikut: {', '.join(keywords)}."
            desc_vec = self.get_cls_embedding(self.clean_text(desc_text))
            similarity = cosine_similarity([user_vector], [desc_vec])[0][0]
            results.append({'divisi': div, 'skor': similarity})

        # LANGKAH 2: Tentukan divisi terkuat (jika ada)
        it_keywords = ['backend', 'frontend', 'full stack', 'devops', 'programmer', 'software engineer', 'network engineer', 'keamanan siber', 'jaringan komputer']
        mc_keywords = ['photoshop', 'illustrator', 'premiere', 'after effects', 'final cut', 'editing video', 'video editor', 'desain grafis', 'graphic design', 'design', 'fotografi', 'videografi', 'kameramen', 'animasi', 'blender', 'figma', 'multimedia', 'corel draw']
        admin_keywords = ['sekretaris', 'bendahara', 'administrasi', 'surat menyurat', 'pengarsipan', 'menyusun laporan', 'dokumentasi', 'pajak', 'akuntansi', 'akuntan', 'pembukuan', 'laporan keuangan', 'finansial', 'anggaran', 'audit', 'faktur']
        enp_keywords = ['guru', 'pengajar', 'dosen', 'instruktur', 'pendidik', 'jurnal', 'publikasi', 'silabus', 'pelatihan', 'mengajar', 'penulis', 'editor', 'karya tulis ilmiah', 'riset', 'peneliti']

        it_count = sum(1 for keyword in it_keywords if keyword in cleaned_full_text)
        mc_count = sum(1 for keyword in mc_keywords if keyword in cleaned_full_text)
        admin_count = sum(1 for keyword in admin_keywords if keyword in cleaned_full_text)
        enp_count = sum(1 for keyword in enp_keywords if keyword in cleaned_full_text)

        strong_division = None
        if mc_count >= 3:
            strong_division = 'Media Creation (MC)'
        elif admin_count >= 3:
            strong_division = 'Administration & Finance'
        elif it_count >= 3:
            strong_division = 'Information Technology (IT)'
        elif enp_count >= 3:
            strong_division = 'Education & Publishing (EnP)'

        # LANGKAH 3: Terapkan Bonus dan Penalti
        if strong_division:
            for res in results:
                if res['divisi'] == strong_division:
                    res['skor'] *= 1.10
                else:
                    res['skor'] *= 0.90
        
        # --- PERUBAHAN UTAMA DI SINI: Batasi Skor Maksimal ---
        final_results_processed = []
        for res in results:
            # Pastikan skor tidak melebihi 1.0 (atau 100%)
            final_score = min(res['skor'], 1.0)
            final_results_processed.append((res['divisi'], final_score))
        
        # LANGKAH 4: Urutkan hasil akhir
        final_results_processed.sort(key=lambda x: x[1], reverse=True)
        
        return final_results_processed