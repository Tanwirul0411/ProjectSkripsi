# model.py
import os
import fitz
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
                # Bahasa Programming & Framework
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
                # Bahasa Indonesia - IT
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
                # Software & Tools
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
                'marketing digital', 'facebook ads',
                # Bahasa Indonesia - Media Creation
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
                'ui designer', 'ux designer', 'web designer', 'tipografi'
            ],
            
            'Education & Publishing (EnP)': [
                # Education & Academic
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
                'microsoft office', 'word', 'powerpoint', 'excel', 'google docs',
                'latex', 'mendeley', 'zotero', 'endnote', 'citation', 'bibliography',
                'academic writing', 'technical writing', 'documentation',
                'knowledge management', 'library science', 'information science',
                # Bahasa Indonesia - Education & Publishing
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
                # Finance & Accounting
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
                # Bahasa Indonesia - Administration & Finance
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
                'dashboard', 'forecasting', 'peramalan', 'modeling keuangan'
            ]
        }

    def extract_text(self, pdf_path):
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        return text

    def clean_text(self, text):
        if not isinstance(text, str):  # Hindari error jika bukan string
            return ""
        text = text.lower()
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def get_cls_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        cls_token = outputs.last_hidden_state[:, 0, :]  # [CLS] token vector
        return cls_token.squeeze().cpu().numpy()

    def get_recommendations(self, cv_path, certificate_paths=None):
        full_text = self.extract_text(cv_path)
        if certificate_paths:
            for path in certificate_paths:
                full_text += " " + self.extract_text(path)
        cleaned_text = self.clean_text(full_text)
        user_vector = self.get_cls_embedding(cleaned_text)

        results = []
        for div, desc in self.divisions.items():
            desc_text = " ".join(desc)  # 
            desc_vec = self.get_cls_embedding(self.clean_text(desc_text))
            similarity = cosine_similarity([user_vector], [desc_vec])[0][0]
            results.append((div, similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results