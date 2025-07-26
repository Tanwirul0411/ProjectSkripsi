# model.py
import os
import fitz  # PyMuPDF
import re
import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

class DivisionRecommendationSystem:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("indobenchmark/indobert-base-p1")
        self.model = BertModel.from_pretrained("indobenchmark/indobert-base-p1")
        self.divisions = {
            'Information Technology (IT)': [
                'python', 'java', 'javascript', 'html', 'css', 'php', 'sql', 'mysql', 
                'postgresql', 'mongodb', 'react', 'angular', 'vue', 'nodejs', 'django',
                'flask', 'spring', 'laravel', 'codeigniter', 'bootstrap', 'jquery',
                'git', 'github', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
                'linux', 'ubuntu', 'centos', 'windows server', 'apache', 'nginx',
                'programming', 'developer', 'software engineer', 'seo', 'sem', 'google ads',
                'web developer', 'full stack', 'frontend', 'backend', 'database', 'api',
                'microservices', 'devops', 'cloud', 'cybersecurity', 'network', 'rest api',
                'artificial intelligence', 'machine learning', 'data science',
                'big data', 'analytics', 'tensorflow', 'pytorch', 'scikit-learn',
                'system administrator', 'it support', 'technical support',
                'cisco', 'comptia', 'microsoft certified', 'oracle certified',
                'red hat', 'vmware', 'citrix', 'networking', 'firewall', 'router',
                'pemrograman', 'pengembang', 'programmer', 'developer', 'sistem informasi',
                'teknologi informasi', 'basis data', 'database', 'jaringan komputer',
                'keamanan siber', 'administrator sistem', 'dukungan teknis', 'support teknis',
                'pengembangan web', 'aplikasi mobile', 'software', 'perangkat lunak',
                'sistem operasi', 'server', 'cloud computing', 'komputasi awan',
                'data mining', 'analisis data', 'kecerdasan buatan', 'ai', 'ml',
                'machine learning', 'deep learning', 'big data', 'data scientist',
                'web design', 'ui/ux', 'front end', 'back end', 'full stack',
                'mobile developer', 'android', 'ios', 'flutter', 'react native'
            ],
            
            'Media Creation (MC)': [
                'photoshop', 'illustrator', 'indesign', 'after effects', 'premiere pro',
                'final cut', 'davinci resolve', 'lightroom', 'figma', 'sketch',
                'adobe creative', 'corel draw', 'canva', 'blender', '3ds max', 'maya',
                'cinema 4d', 'unity', 'unreal engine', 'video editing', 'motion graphics',
                'animation', '2d animation', '3d animation', 'graphic design', 'ui design',
                'ux design', 'web design', 'logo design', 'branding', 'typography',
                'photography', 'videography', 'cinematography', 'content creator',
                'social media', 'digital marketing', 'creative director', 'art director',
                'multimedia', 'visual effects', 'sound design', 'audio editing',
                'pro tools', 'audacity', 'logic pro', 'ableton', 'creative writing',
                'copywriting', 'storytelling', 'scriptwriting', 'content writing',
                'youtube', 'instagram', 'tiktok', 'facebook', 'twitter', 'linkedin',
                'marketing digital', 'facebook ads', 'powerpoint',
                'desain grafis', 'desainer grafis', 'editing video', 'editor video',
                'fotografi', 'fotografer', 'videografi', 'videographer', 'animator',
                'animasi', 'motion graphic', 'konten kreator', 'pembuat konten',
                'media sosial', 'sosial media', 'pemasaran digital', 'digital marketing',
                'branding', 'logo', 'identitas visual', 'kreatif', 'seni', 'video editing',
                'multimedia', 'audio visual', 'sinematografi', 'produksi video',
                'editing audio', 'sound engineer', 'musik', 'suara', 'podcast',
                'copywriter', 'penulis konten', 'content writer', 'storytelling',
                'influencer', 'youtuber', 'blogger', 'vlogger', 'streamer',
                'marketing', 'promosi', 'iklan', 'advertising', 'kampanye',
                'ui designer', 'ux designer', 'web designer', 'tipografi',
                'desain', 'editing', 'editor', 'poster', 'kameramen', 'product design',
                'manajer desain', 'desain produk', 'kreativitas', 'visual', 'konten visual'
            ],
            
            'Education & Publishing (EnP)': [
                'teacher', 'educator', 'instructor', 'lecturer', 'professor', 'tutor',
                'curriculum', 'pedagogy', 'educational', 'teaching', 'training',
                'learning management', 'e-learning', 'online learning', 'moodle',
                'blackboard', 'canvas', 'google classroom', 'zoom', 'microsoft teams',
                'educational technology', 'instructional design', 'assessment',
                'academic', 'research', 'thesis', 'dissertation', 'publication',
                'journal', 'editorial', 'proofreading', 'copyediting', 'publishing',
                'content development', 'textbook', 'course material', 'syllabus',
                'lesson plan', 'educational content', 'training material',
                'workshop', 'seminar', 'conference', 'presentation', 'public speaking',
                'microsoft office', 'google docs', 'penulisan', 'shortcut'
                'latex', 'mendeley', 'zotero', 'endnote', 'citation', 'bibliography',
                'academic writing', 'technical writing', 'documentation',
                'knowledge management', 'library science', 'information science',
                'guru', 'pengajar', 'dosen', 'instruktur', 'pendidik', 'tutor',
                'pendidikan', 'pembelajaran', 'mengajar', 'pelatihan', 'training',
                'kurikulum', 'silabus', 'rencana pembelajaran', 'bahan ajar',
                'materi pembelajaran', 'modul', 'buku teks', 'e-learning',
                'pembelajaran online', 'kelas online', 'zoom', 'google classroom',
                'teknologi pendidikan', 'edtech', 'lms', 'assessment', 'evaluasi',
                'penelitian', 'riset', 'thesis', 'tesis', 'skripsi', 'disertasi',
                'jurnal', 'publikasi', 'penerbit', 'penerbitan', 'editor',
                'proofreader', 'copyeditor', 'penulis', 'author', 'konten edukatif',
                'workshop', 'seminar', 'pelatihan', 'presentasi', 'public speaking',
                'perpustakaan', 'librarian', 'pustakawan', 'manajemen pengetahuan',
                'dokumentasi', 'technical writer', 'content developer',
                'akademik', 'scholar', 'ilmiah', 'scientific', 'konferensi'
            ],
            
            'Administration & Finance': [
                'accounting', 'bookkeeping', 'financial', 'finance', 'budget',
                'auditing', 'tax', 'payroll', 'invoice', 'receipt', 'expenses',
                'revenue', 'profit', 'loss', 'balance sheet', 'income statement',
                'cash flow', 'financial analysis', 'financial planning', 'investment',
                'banking', 'insurance', 'loan', 'credit', 'debit', 'accounts payable',
                'accounts receivable', 'general ledger', 'trial balance',
                'quickbooks', 'sage', 'xero', 'tally', 'myob', 'accurate',
                'administration', 'administrative', 'office manager', 'secretary',
                'receptionist', 'data entry', 'filing', 'documentation', 'records',
                'human resources', 'hr', 'recruitment', 'payroll', 'benefits',
                'employee relations', 'performance management', 'compliance',
                'policy', 'procedure', 'governance', 'risk management',
                'project management', 'operations', 'logistics', 'supply chain',
                'procurement', 'vendor management', 'contract', 'negotiation',
                'customer service', 'client relations', 'communication',
                'microsoft excel', 'spreadsheet', 'pivot table', 'vlookup',
                'financial modeling', 'forecasting', 'reporting', 'dashboard',
                'akuntansi', 'akuntan', 'keuangan', 'finansial', 'anggaran', 'budget',
                'audit', 'auditor', 'pajak', 'tax', 'gaji', 'payroll', 'invoice',
                'faktur', 'kwitansi', 'pengeluaran', 'pendapatan', 'keuntungan',
                'kerugian', 'neraca', 'laporan keuangan', 'arus kas', 'cash flow',
                'analisis keuangan', 'perencanaan keuangan', 'investasi', 'perbankan',
                'asuransi', 'kredit', 'pinjaman', 'hutang', 'piutang', 'buku besar',
                'administrasi', 'administratif', 'manajer kantor', 'sekretaris',
                'resepsionis', 'entry data', 'filing', 'dokumentasi', 'arsip',
                'sumber daya manusia', 'sdm', 'hr', 'rekrutmen', 'recruitment',
                'tunjangan', 'benefit', 'hubungan karyawan', 'manajemen kinerja',
                'kepatuhan', 'compliance', 'kebijakan', 'prosedur', 'governance',
                'manajemen risiko', 'risk management', 'manajemen proyek',
                'operasional', 'logistik', 'supply chain', 'pengadaan', 'procurement',
                'vendor', 'kontrak', 'negosiasi', 'customer service', 'layanan pelanggan',
                'komunikasi', 'excel', 'spreadsheet', 'pivot table', 'laporan',
                'dashboard', 'forecasting', 'peramalan', 'modeling keuangan',
                'analis keuangan', 'pasar modal', 'saham', 'obligasi', 'reksadana',
                'manajemen aset', 'aset', 'liabilitas', 'ekuitas', 'laporan laba rugi',
                'neraca saldo', 'teller', 'simpanan', 'giro', 'tabungan', 'deposito',
                'pembukuan', 'jurnal', 'akuntan publik', 'pajak penghasilan', 'pph', 'ppn'
            ]
        }

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
        
        # --- PENDORONG UNTUK IT ---
        it_trigger_keywords = [
            'backend', 'frontend', 'full stack', 'devops', 'programmer',
            'software engineer', 'network engineer', 'keamanan siber', 'jaringan komputer'
        ]
        it_trigger_count = 0
        for keyword in it_trigger_keywords:
            if keyword in cleaned_full_text:
                it_trigger_count += 1
        
        if it_trigger_count >= 2: # Cukup 2 untuk IT karena istilahnya sangat spesifik
            for res in results:
                if res['divisi'] == 'Information Technology (IT)':
                    res['skor'] *= 1.10
                    break

        # --- PENDORONG UNTUK MEDIA CREATION ---
        mc_trigger_keywords = [
            'photoshop', 'illustrator', 'premiere', 'after effects', 'final cut',
            'editing video', 'desain grafis', 'fotografi', 'videografi',
            'kameramen', 'animasi', 'blender', 'figma', 'multimedia'
        ]
        mc_trigger_count = 0
        for keyword in mc_trigger_keywords:
            if keyword in cleaned_full_text:
                mc_trigger_count += 1
        
        if mc_trigger_count >= 3:
            for res in results:
                if res['divisi'] == 'Media Creation (MC)':
                    res['skor'] *= 1.10
                    break
        
        # --- PENDORONG UNTUK ADMINISTRATION & FINANCE ---
        admfin_trigger_keywords = [
            'sekretaris', 'bendahara', 'administrasi', 'surat menyurat', 'pengarsipan',
            'menyusun laporan', 'dokumentasi', 'pajak', 'akuntansi', 'akuntan', 
            'pembukuan', 'laporan keuangan', 'finansial', 'anggaran', 'audit', 'faktur'
        ]
        admin_trigger_count = 0
        for keyword in admfin_trigger_keywords:
            if keyword in cleaned_full_text:
                admin_trigger_count += 1

        if admin_trigger_count >= 3:
            for res in results:
                if res['divisi'] == 'Administration & Finance':
                    res['skor'] *= 1.10
                    break
        
        # --- PENDORONG UNTUK EDUCATION & PUBLISHING ---
        enp_trigger_keywords = [
            'guru', 'pengajar', 'dosen', 'instruktur', 'pendidik', 'jurnal',
            'publikasi', 'silabus', 'pelatihan', 'mengajar', 'penulis', 'editor'
        ]
        enp_trigger_count = 0
        for keyword in enp_trigger_keywords:
            if keyword in cleaned_full_text:
                enp_trigger_count += 1

        if enp_trigger_count >= 3:
            for res in results:
                if res['divisi'] == 'Education & Publishing (EnP)':
                    res['skor'] *= 1.10
                    break

        # --- LANGKAH 4: URUTKAN HASIL AKHIR ---
        final_results = [(res['divisi'], res['skor']) for res in results]
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        return final_results