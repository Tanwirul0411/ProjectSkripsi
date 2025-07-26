# model.py
import os
import fitz  # PyMuPDF
import re
import torch
import pandas as pd  # Import library pandas
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

class DivisionRecommendationSystem:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("indobenchmark/indobert-base-p1")
        self.model = BertModel.from_pretrained("indobenchmark/indobert-base-p1")
        
        # Membaca daftar keywords dari file eksternal
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
            print(f"Error: File '{file_path}' tidak ditemukan. Pastikan file tersebut ada di folder yang sama.")
            return {}
        except KeyError:
            print(f"Error: File '{file_path}' tidak memiliki kolom 'divisi' atau 'keyword'. Pastikan header file CSV sudah benar.")
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
        # --- LANGKAH 1: EKSTRAK SEMUA TEKS ---
        full_text = self.extract_text(cv_path)
        if certificate_paths:
            for path in certificate_paths:
                full_text += " " + self.extract_text(path)

        cleaned_full_text = self.clean_text(full_text)
        user_vector = self.get_cls_embedding(cleaned_full_text)

        # --- LANGKAH 2: HITUNG SKOR AWAL ---
        results = []
        for div, keywords in self.divisions.items():
            nama_divisi = div.split('(')[0].strip()
            desc_text = f"Kandidat untuk divisi {nama_divisi} harus memiliki keahlian dalam bidang berikut: {', '.join(keywords)}."
            
            desc_vec = self.get_cls_embedding(self.clean_text(desc_text))
            similarity = cosine_similarity([user_vector], [desc_vec])[0][0]
            results.append({'divisi': div, 'skor': similarity})

        # --- LANGKAH 3: LOGIKA PENDORONG SKOR UNTUK SEMUA DIVISI ---
        
        # Cek Pemicu IT
        it_trigger_keywords = [
            'backend', 'frontend', 'full stack', 'devops', 'programmer',
            'software engineer', 'network engineer', 'keamanan siber', 'jaringan komputer'
        ]
        it_trigger_count = sum(1 for keyword in it_trigger_keywords if keyword in cleaned_full_text)
        
        # Cek Pemicu Media Creation
        mc_trigger_keywords = [
            'photoshop', 'illustrator', 'premiere', 'after effects', 'final cut', 'editing',
            'editing video', 'video editor', 'desain grafis', 'graphic design', 'design',
            'fotografi', 'videografi', 'kameramen', 'animasi', 'blender', 'figma', 'multimedia', 'corel draw'
        ]
        mc_trigger_count = sum(1 for keyword in mc_trigger_keywords if keyword in cleaned_full_text)

        # Cek Pemicu Administrasi & Keuangan
        admin_trigger_keywords = [
            'sekretaris', 'bendahara', 'administrasi', 'surat menyurat', 'pengarsipan',
            'menyusun laporan', 'dokumentasi', 'pajak', 'akuntansi', 'akuntan', 
            'pembukuan', 'laporan keuangan', 'finansial', 'anggaran', 'audit', 'faktur'
        ]
        admin_trigger_count = sum(1 for keyword in admin_trigger_keywords if keyword in cleaned_full_text)

        # Cek Pemicu Education & Publishing
        enp_trigger_keywords = [
            'guru', 'pengajar', 'dosen', 'instruktur', 'pendidik', 'jurnal',
            'publikasi', 'silabus', 'pelatihan', 'mengajar', 'penulis', 'editor',
            'karya tulis ilmiah', 'riset', 'peneliti'
        ]
        enp_trigger_count = sum(1 for keyword in enp_trigger_keywords if keyword in cleaned_full_text)

        # Terapkan Bonus dan Penalti berdasarkan divisi terkuat
        strong_candidate_division = None
        if mc_trigger_count >= 3:
            strong_candidate_division = 'Media Creation (MC)'
        elif admin_trigger_count >= 3:
            strong_candidate_division = 'Administration & Finance'
        elif it_trigger_count >= 3:
            strong_candidate_division = 'Information Technology (IT)'
        elif enp_trigger_count >= 3:
            strong_candidate_division = 'Education & Publishing (EnP)'

        if strong_candidate_division:
            for res in results:
                if res['divisi'] == strong_candidate_division:
                    res['skor'] *= 1.10
                else:
                    res['skor'] *= 0.90

        # --- LANGKAH 4: URUTKAN HASIL AKHIR ---
        final_results = [(res['divisi'], res['skor']) for res in results]
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        return final_results