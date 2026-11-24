"""Teks bahasa awam: deskripsi indikator, istilah, dan daftar uji beserta kegunaannya."""

# indikator -> (nama awam, penjelasan, arah)
INDIKATOR_AWAM = {
    "CPR": ("Pemakai KB modern", "Dari 100 pasangan usia subur, berapa yang memakai KB modern.", "Makin tinggi makin baik"),
    "MKJP": ("KB jangka panjang", "Porsi pengguna KB yang memakai metode jangka panjang (IUD, implan, steril).", "Makin tinggi makin baik"),
    "UnmetNeed": ("Butuh KB tapi belum terlayani", "Pasangan yang ingin menunda atau membatasi anak tetapi belum memakai KB.", "Makin rendah makin baik"),
    "DCR": ("Berhenti memakai KB", "Pengguna KB yang berhenti memakai alat/obat tanpa beralih ke metode lain.", "Makin rendah makin baik"),
    "TFR": ("Rata-rata jumlah anak", "Rata-rata jumlah anak yang dilahirkan seorang perempuan selama hidupnya.", "Makin rendah dianggap makin baik (asumsi)"),
}

# Uji statistik -> judul yang menjelaskan KEGUNAAN (bukan nama ujinya)
UJI = {
    "bentuk": "Seberapa merata sebaran angka antar daerah?",
    "acuan": "Apakah daerah-daerah umumnya di atas atau di bawah angka acuan?",
    "kota": "Apakah kota dan kabupaten punya capaian berbeda?",
    "kawasan": "Apakah capaian berbeda antar kawasan budaya (Mataraman, Arek, Tapal Kuda, Madura)?",
    "kualitas": "Apakah KB berjalan seiring dengan kualitas hidup (iBangga dan lama sekolah)?",
    "tertinggal": "Apakah ada indikator yang lebih sering tertinggal dibanding yang lain?",
    "jenis": "Apakah tingkat capaian terkait dengan jenis wilayah (kota atau kabupaten)?",
    "waktu": "Apakah pemakaian KB aktif berubah dari 2023 ke 2025?",
}

# Nama uji untuk yang ingin tahu (disembunyikan dalam kotak "Untuk yang ingin tahu istilahnya")
NAMA_UJI = {
    "bentuk": "Shapiro-Wilk", "acuan": "Wilcoxon (satu sampel)", "kota": "Mann-Whitney U",
    "kawasan": "Kruskal-Wallis dengan uji lanjut Dunn", "kualitas": "Korelasi Spearman",
    "tertinggal": "Cochran's Q", "jenis": "Chi-square dan Fisher exact", "waktu": "Wilcoxon signed-rank (berpasangan)",
}

GLOSARIUM = [
    ("Alokon", "Alat dan obat kontrasepsi: IUD, implan, suntik, pil, kondom, dan sterilisasi."),
    ("PUS", "Pasangan Usia Subur, yaitu pasangan yang istrinya berusia 15–49 tahun."),
    ("PKB", "Penyuluh Keluarga Berencana, petugas lapangan yang memberi penyuluhan KB."),
    ("CPR modern", "Persentase pasangan usia subur yang memakai KB modern."),
    ("MKJP", "Metode Kontrasepsi Jangka Panjang: IUD, implan, dan sterilisasi."),
    ("Unmet need", "Kebutuhan KB yang belum terpenuhi: ingin menunda/membatasi anak tetapi tidak memakai KB."),
    ("DCR", "Discontinuation rate: pengguna yang berhenti memakai KB."),
    ("TFR", "Total Fertility Rate: rata-rata jumlah anak per perempuan."),
    ("iBangga", "Indeks Pembangunan Keluarga: ukuran kualitas keluarga (0–100)."),
    ("RLS", "Rata-rata lama sekolah penduduk dewasa (tahun)."),
    ("Indeks capaian", "Skor gabungan lima indikator KB. Nol berarti sama dengan rata-rata 38 daerah; plus lebih baik; minus lebih rendah."),
    ("Skor z", "Cara menyamakan skala angka: seberapa jauh nilai daerah dari rata-rata semua daerah."),
    ("Klaster", "Kelompok daerah dengan pola capaian yang mirip."),
    ("Median", "Nilai tengah: separuh daerah di atasnya, separuh di bawahnya."),
    ("p (nilai p)", "Ukuran seberapa mungkin perbedaan terjadi kebetulan. Di bawah 0,05 dianggap perbedaan nyata."),
    ("Stok kritis", "Stok gudang alokon kurang dari satu bulan kebutuhan (asumsi penelitian)."),
    ("Autokorelasi spasial", "Kecenderungan daerah bertetangga mempunyai nilai yang mirip."),
    ("Tipologi", "Pengelompokan daerah menurut kombinasi capaian (rendah/tinggi) dan dukungan layanan (rendah/cukup)."),
    ("Tema pertanyaan", "Pokok yang ditanyakan warganet, dikelompokkan dengan kata kunci."),
    ("Nada komentar", "Apakah komentar bernada negatif (mengeluh/khawatir), netral, atau positif; dinilai komputer."),
]
