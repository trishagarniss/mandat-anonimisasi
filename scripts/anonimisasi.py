import pandas as pd
import numpy as np
import hashlib
from cryptography.fernet import Fernet

np.random.seed(42)

# ═══════════════════════════════════════════════════════════════════════
# 0. LOAD DATA
# ═══════════════════════════════════════════════════════════════════════

df = pd.read_csv("data_dummy.csv")

print("=" * 65)
print("  DATA ASLI (sebelum anonimisasi)")
print("=" * 65)
print(df[["NISN", "Nama_Lengkap", "Rata_Nilai", "Kehadiran_Persen",
          "Penghasilan_Keluarga_Bulan", "Usia"]].head(3).to_string())
print("-" * 65)

# ═══════════════════════════════════════════════════════════════════════
# DATA MASKING
# ═══════════════════════════════════════════════════════════════════════
# Teknik  : Menyembunyikan sebagian karakter dengan simbol bintang (*)
# Target  : Nama_Lengkap
# Tujuan  : Mencegah identifikasi langsung tanpa kehilangan format nama
# Contoh  : "Rizky Pratama" → "Riz**********"
# -----------------------------------------------------------------------

def masking_nama(nama: str) -> str:
    """Pertahankan 3 huruf pertama, bintangi sisanya per kata."""
    kata = nama.split()
    hasil = []
    for i, k in enumerate(kata):
        if i == 0:
            # Kata pertama: tampilkan 3 huruf awal
            hasil.append(k[:3] + "*" * max(0, len(k) - 3))
        else:
            # Kata berikutnya: sembunyikan semua kecuali huruf kapital awal
            hasil.append(k[0] + "*" * (len(k) - 1))
    return " ".join(hasil)

df["Nama_Masking"] = df["Nama_Lengkap"].apply(masking_nama)

print("\n[Anggota 1] DATA MASKING — Nama_Lengkap")
print(df[["Nama_Lengkap", "Nama_Masking"]].head(4).to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
# PSEUDONYMIZATION (Hashing Searah)
# ═══════════════════════════════════════════════════════════════════════
# Teknik  : Mengganti identifier asli dengan token acak yang konsisten
# Target  : NISN
# Tujuan  : NISN tidak bisa dibaca langsung, tapi satu siswa tetap
#           punya satu ID unik (konsisten lintas tabel/join)
# Contoh  : "3746317213" → "a3f9c12b84e7"
# -----------------------------------------------------------------------

def hash_nisn(nisn: str) -> str:
    """SHA-256, ambil 16 karakter pertama sebagai pseudo-ID."""
    return hashlib.sha256(nisn.encode()).hexdigest()[:16]

df["NISN_Hash"] = df["NISN"].astype(str).apply(hash_nisn)

print("\n[Anggota 2] PSEUDONYMIZATION — NISN")
print(df[["NISN", "NISN_Hash"]].head(4).to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
# GENERALIZATION (Pengelompokan ke Rentang/Kategori)
# ═══════════════════════════════════════════════════════════════════════
# Teknik  : Mengganti nilai presisi tinggi dengan label rentang umum
# Target  : Penghasilan_Keluarga_Bulan, Usia, Jarak_Ke_Sekolah_KM
# Tujuan  : Mengurangi granularitas data sensitif (angka pasti → bracket)
# Contoh  : Rp 2.100.000 → "1.5 Juta - 4 Juta"
# -----------------------------------------------------------------------

# Generalisasi penghasilan keluarga
batas_gaji   = [0, 1_000_000, 2_500_000, 5_000_000, float("inf")]
label_gaji   = ["< 1 Juta", "1 - 2.5 Juta", "2.5 - 5 Juta", "> 5 Juta"]
df["Penghasilan_Generalisasi"] = pd.cut(
    df["Penghasilan_Keluarga_Bulan"], bins=batas_gaji, labels=label_gaji
)

# Generalisasi usia → kelompok umur
batas_usia   = [0, 13, 15, 18, float("inf")]
label_usia   = ["≤ 13 th", "14–15 th", "16–18 th", "> 18 th"]
df["Usia_Generalisasi"] = pd.cut(
    df["Usia"], bins=batas_usia, labels=label_usia
)

# Generalisasi jarak ke sekolah
batas_jarak  = [0, 2, 5, 10, float("inf")]
label_jarak  = ["Dekat (≤2 km)", "Sedang (2–5 km)", "Jauh (5–10 km)", "Sangat Jauh (>10 km)"]
df["Jarak_Generalisasi"] = pd.cut(
    df["Jarak_Ke_Sekolah_KM"], bins=batas_jarak, labels=label_jarak
)

print("\n[Anggota 3] GENERALIZATION — Penghasilan, Usia, Jarak")
print(df[["Penghasilan_Keluarga_Bulan", "Penghasilan_Generalisasi",
          "Usia", "Usia_Generalisasi",
          "Jarak_Ke_Sekolah_KM", "Jarak_Generalisasi"]].head(4).to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
# NOISE ADDITION (Penambahan Gangguan Acak)
# ═══════════════════════════════════════════════════════════════════════
# Teknik  : Menambahkan nilai desimal acak (distribusi normal) ke data numerik
# Target  : Rata_Nilai, Kehadiran_Persen
# Tujuan  : Nilai tidak lagi presisi 100%, tapi distribusi statistiknya
#           (mean, std) masih cukup akurat untuk keperluan analitik
# Contoh  : Nilai 75 → 74.3 (noise ±2), Kehadiran 88 → 89.1 (noise ±1.5)
# -----------------------------------------------------------------------

# Noise pada nilai akademik — standar deviasi 2 poin
noise_nilai      = np.random.normal(loc=0, scale=2.0, size=len(df))
df["Nilai_Noise"] = np.clip(
    np.round(df["Rata_Nilai"] + noise_nilai, 1), 0, 100
)

# Noise pada kehadiran — standar deviasi 1.5 poin
noise_kehadiran      = np.random.normal(loc=0, scale=1.5, size=len(df))
df["Kehadiran_Noise"] = np.clip(
    np.round(df["Kehadiran_Persen"] + noise_kehadiran, 1), 0, 100
)

print("\n[Anggota 4] NOISE ADDITION — Rata_Nilai & Kehadiran_Persen")
print(df[["Rata_Nilai", "Nilai_Noise",
          "Kehadiran_Persen", "Kehadiran_Noise"]].head(4).to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
# ENCRYPTION (Enkripsi Simetris Dua Arah)
# ═══════════════════════════════════════════════════════════════════════
# Teknik  : Mengenkripsi data sensitif dengan kunci rahasia (Fernet/AES)
# Target  : Nama_Lengkap
# Tujuan  : Data bisa dibuka kembali (decrypt) oleh Super Admin yang
#           memegang kunci — berbeda dengan hash yang satu arah
# Catatan : Kunci HARUS disimpan terpisah dan aman (tidak boleh ikut CSV)
# -----------------------------------------------------------------------

kunci_rahasia = Fernet.generate_key()
cipher        = Fernet(kunci_rahasia)

df["Nama_Enkripsi"] = df["Nama_Lengkap"].apply(
    lambda x: cipher.encrypt(x.encode()).decode()
)

# Verifikasi: decrypt balik untuk membuktikan reversible
nama_terdekripsi = cipher.decrypt(df["Nama_Enkripsi"].iloc[0].encode()).decode()

print("\n[Anggota 5] ENCRYPTION — Nama_Lengkap")
print(f"  Asli       : {df['Nama_Lengkap'].iloc[0]}")
print(f"  Terenkripsi: {df['Nama_Enkripsi'].iloc[0][:50]}...")
print(f"  Terdekripsi: {nama_terdekripsi}  ✅ (reversible dengan kunci)")
print(f"\n  ⚠️  Kunci Rahasia (simpan terpisah, JANGAN disertakan di CSV):")
print(f"  {kunci_rahasia.decode()}")

# ═══════════════════════════════════════════════════════════════════════
# DATA SHUFFLING (Pengacakan Vertikal)
# ═══════════════════════════════════════════════════════════════════════
# Teknik  : Mengacak urutan nilai dalam satu kolom sehingga tidak lagi
#           cocok dengan baris/individu yang seharusnya
# Target  : Pekerjaan_Ayah
# Tujuan  : Profil pekerjaan tidak bisa dikaitkan langsung ke siswa
#           tertentu, tapi distribusi pekerjaan secara keseluruhan tetap
#           sama (cocok untuk analisis agregat)
# -----------------------------------------------------------------------

df["Pekerjaan_Ayah_Shuffled"] = (
    df["Pekerjaan_Ayah"]
    .sample(frac=1, random_state=99)
    .reset_index(drop=True)
)

print("\n[Anggota 6] DATA SHUFFLING — Pekerjaan_Ayah")
print(df[["Nama_Lengkap", "Pekerjaan_Ayah", "Pekerjaan_Ayah_Shuffled"]].head(6).to_string(index=False))
print("\n  Distribusi sebelum vs sesudah (harus sama):")
dist_before = df["Pekerjaan_Ayah"].value_counts()
dist_after  = df["Pekerjaan_Ayah_Shuffled"].value_counts()
cmp = pd.DataFrame({"Sebelum": dist_before, "Sesudah": dist_after})
print(cmp.to_string())

# ═══════════════════════════════════════════════════════════════════════
# FINISHING — GABUNGKAN JADI TABEL AKHIR SIAP ML
# ═══════════════════════════════════════════════════════════════════════
# Hanya kolom yang sudah anonim yang masuk ke dataset final.
# Kolom identitas asli (NISN, Nama_Lengkap) TIDAK ikut disimpan.
# -----------------------------------------------------------------------

df_aman = pd.DataFrame({
    # Identitas anonim
    "ID_Siswa"              : df["NISN_Hash"],                 
    "Nama_Siswa"            : df["Nama_Masking"],               

    # Demografis — generalisasi
    "Kelompok_Usia"         : df["Usia_Generalisasi"],        
    "Kelas"                 : df["Kelas"],
    "Jenis_Kelamin"         : df["Jenis_Kelamin"],
    "Jurusan"               : df["Jurusan"],

    # Akademik — dengan noise
    "Nilai_Akhir"           : df["Nilai_Noise"],               
    "Kehadiran_Persen"      : df["Kehadiran_Noise"],            
    "Jumlah_Remedial"       : df["Jumlah_Remedial"],
    "Pernah_Tinggal_Kelas"  : df["Pernah_Tinggal_Kelas"],
    "Siswa_Bekerja"         : df["Siswa_Bekerja"],

    # Keluarga
    "Status_Ortu"           : df["Status_Ortu"],
    "Jumlah_Saudara"        : df["Jumlah_Saudara"],
    "Pendidikan_Ortu"       : df["Pendidikan_Tertinggi_Ortu"],
    "Pekerjaan_Ayah"        : df["Pekerjaan_Ayah_Shuffled"],    

    # Ekonomi — generalisasi
    "Ekonomi_Keluarga"      : df["Penghasilan_Generalisasi"],  
    "Jarak_Ke_Sekolah"      : df["Jarak_Generalisasi"],         
    "Kondisi_Rumah"         : df["Kondisi_Rumah"],
    "Akses_Internet"        : df["Akses_Internet"],

    # Bantuan sosial
    "Penerima_KIP"          : df["Penerima_KIP"],
    "Penerima_PKH"          : df["Penerima_PKH"],
    "Terdaftar_DTKS"        : df["Terdaftar_DTKS"],

    # Target label ML
    "Status_Risiko"         : df["Status_Risiko"],
    "Kelayakan_Bansos"      : df["Kelayakan_Bansos"],
})

df_aman.to_csv("data_siswa_siap_ml.csv", index=False)

print("\n" + "=" * 65)
print("  DATASET FINAL ")
print("=" * 65)
print(f"  Baris    : {len(df_aman)}")
print(f"  Kolom    : {len(df_aman.columns)}")
print(f"\n  Kolom yang DIHAPUS dari dataset final:")
print(f"    ✗ NISN (asli)         → diganti NISN_Hash")
print(f"    ✗ Nama_Lengkap (asli) → diganti Nama_Masking")
print(f"    ✗ Penghasilan (angka) → diganti bracket kategori")
print(f"    ✗ Usia (angka pasti)  → diganti kelompok umur")
print(f"    ✗ Jarak (angka pasti) → diganti kategori jarak")
print(f"\nPreview dataset akhir:")
print(df_aman.head(3).T.to_string())
print("\n✅ File 'data_siswa_siap.csv' berhasil disimpan!")