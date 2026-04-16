import pandas as pd
import numpy as np
import random
from itertools import product

# ─── SEED ───
np.random.seed(42)
random.seed(42)

N = 500  # Jumlah siswa

# ═══════════════════════════════════════════════════════════════════════
# 1. IDENTITAS SISWA
# ═══════════════════════════════════════════════════════════════════════

nisn = [str(random.randint(10**9, 10**10 - 1)) for _ in range(N)]

# pool 48 x 30 = 1.440 kombinasi
nama_depan = [
    "Budi", "Siti", "Andi", "Rina", "Joko", "Ayu", "Fajar", "Dewi",
    "Rizky", "Putri", "Dian", "Hendra", "Mega", "Tono", "Yuli", "Wahyu",
    "Fitri", "Agus", "Lina", "Bagas", "Citra", "Doni", "Eka", "Gilang",
    "Indah", "Kurnia", "Maya", "Nanda", "Okta", "Rafi", "Salsa", "Tegar",
    "Yoga", "Wulan", "Rendra", "Tiara", "Haris", "Nisa", "Galih", "Reni",
    "Bayu", "Shinta", "Arif", "Novi", "Fandi", "Dimas", "Ratna", "Ilham",
]
nama_belakang = [
    "Santoso", "Wijaya", "Pratama", "Sari", "Kusuma", "Setiawan",
    "Lestari", "Hidayat", "Nugroho", "Rahayu", "Wibowo", "Suryadi",
    "Permata", "Saputra", "Andini", "Firmansyah", "Kurniawan", "Puspita",
    "Susanto", "Hartono", "Budiman", "Wahyudi", "Utomo", "Handoko",
    "Siregar", "Nasution", "Harahap", "Situmorang", "Sinaga", "Lubis",
]
pool_nama = [f"{d} {b}" for d, b in product(nama_depan, nama_belakang)]
nama_lengkap = random.sample(pool_nama, N)  # Dijamin tidak ada duplikat

jenis_kelamin = np.random.choice(["Laki-laki", "Perempuan"], N, p=[0.52, 0.48])

# Kelas 7–12 (SMP + SMA)
kelas = np.random.choice([7, 8, 9, 10, 11, 12], N)
usia_base = {7: 13, 8: 14, 9: 15, 10: 16, 11: 17, 12: 18}
usia = np.array([usia_base[k] + random.choice([-1, 0, 0, 1]) for k in kelas])

jurusan = [
    random.choice(["IPA", "IPS", "Kejuruan"]) if k >= 10 else "-"
    for k in kelas
]

# ═══════════════════════════════════════════════════════════════════════
# 2. DATA AKADEMIK
# ═══════════════════════════════════════════════════════════════════════

kehadiran = np.clip(np.random.normal(84, 11, N), 40, 100).astype(int)
rata_nilai = np.clip(np.random.normal(73, 13, N), 30, 100).astype(int)

# Remedial berkorelasi negatif dengan nilai
jumlah_remedial = np.clip(
    np.round((100 - rata_nilai) / 15 + np.random.normal(0, 1, N)), 0, 8
).astype(int)

# Peringkat kelas berkorelasi negatif dengan nilai
peringkat_kelas = np.clip(
    np.round(41 - (rata_nilai / 100 * 40) + np.random.normal(0, 5, N)), 1, 40
).astype(int)

# Pernah tinggal kelas — lebih mungkin jika nilai + kehadiran buruk
prob_tinggal = np.where(
    (rata_nilai < 60) & (kehadiran < 75), 0.55,
    np.where((rata_nilai < 70) | (kehadiran < 80), 0.20, 0.05)
)
pernah_tinggal_kelas = np.array(
    [np.random.choice([1, 0], p=[p, 1 - p]) for p in prob_tinggal]
)

# Surat peringatan — otomatis jika kehadiran < 75%
surat_peringatan = np.where(
    kehadiran < 75, np.random.choice([1, 2, 3], N), 0
)

ekskul = np.random.choice(["Aktif", "Tidak Aktif"], N, p=[0.45, 0.55])

# Siswa bekerja sambil sekolah
siswa_bekerja = np.random.choice([1, 0], N, p=[0.18, 0.82])

# ═══════════════════════════════════════════════════════════════════════
# 3. DATA KELUARGA
# ═══════════════════════════════════════════════════════════════════════

status_ortu = np.random.choice(
    ["Lengkap", "Cerai", "Yatim", "Piatu", "Yatim Piatu"],
    N, p=[0.65, 0.15, 0.09, 0.08, 0.03]
)

jumlah_saudara = np.clip(
    np.round(np.random.exponential(1.5, N)), 0, 7
).astype(int)

pendidikan_ortu = np.random.choice(
    ["Tidak Sekolah", "SD", "SMP", "SMA/SMK", "D3/S1", "S2/S3"],
    N, p=[0.05, 0.15, 0.20, 0.35, 0.22, 0.03]
)

pekerjaan_ayah = np.random.choice(
    ["Petani", "Buruh Harian", "Pedagang", "PNS/TNI/Polri",
     "Karyawan Swasta", "Wiraswasta", "Tidak Bekerja", "Meninggal"],
    N, p=[0.18, 0.20, 0.15, 0.08, 0.17, 0.12, 0.07, 0.03]
)

pekerjaan_ibu = np.random.choice(
    ["Ibu Rumah Tangga", "Petani", "Buruh Harian", "Pedagang",
     "Karyawan Swasta", "Wiraswasta", "PNS", "Meninggal"],
    N, p=[0.35, 0.12, 0.13, 0.12, 0.10, 0.09, 0.06, 0.03]
)

# ═══════════════════════════════════════════════════════════════════════
# 4. KONDISI SOSIAL-EKONOMI & RUMAH
# ═══════════════════════════════════════════════════════════════════════

# Penghasilan — distribusi lognormal agar realistis (skewed ke bawah)
gaji_ortu = np.clip(
    np.random.lognormal(mean=np.log(2200000), sigma=0.8, size=N),
    400000, 15000000
).astype(int)
gaji_ortu = (gaji_ortu // 100000) * 100000  # Bulatkan ke 100 ribuan

# Pengeluaran — bisa lebih besar dari penghasilan (defisit/utang)
pengeluaran = np.clip(
    gaji_ortu * np.random.uniform(0.7, 1.3, N),
    300000, 12000000
).astype(int)
pengeluaran = (pengeluaran // 50000) * 50000

kepemilikan_rumah = np.random.choice(
    ["Milik Sendiri", "Sewa/Kontrak", "Numpang Keluarga", "Dinas"],
    N, p=[0.55, 0.22, 0.20, 0.03]
)

kondisi_rumah = np.random.choice(
    ["Permanen", "Semi Permanen", "Tidak Layak Huni"],
    N, p=[0.48, 0.35, 0.17]
)

akses_listrik = np.random.choice(
    ["PLN Mandiri", "PLN Subsidi (450VA/900VA)", "Nebeng Tetangga", "Tidak Ada"],
    N, p=[0.40, 0.38, 0.17, 0.05]
)

sumber_air = np.random.choice(
    ["PAM/PDAM", "Sumur Pompa", "Sumur Gali", "Sungai/Tadah Hujan"],
    N, p=[0.30, 0.35, 0.25, 0.10]
)

jarak_sekolah_km = np.clip(
    np.random.lognormal(mean=np.log(3), sigma=0.9, size=N), 0.3, 25
).round(1)

moda_transportasi = np.random.choice(
    ["Jalan Kaki", "Sepeda", "Motor Pribadi", "Angkutan Umum", "Diantar Ortu"],
    N, p=[0.20, 0.12, 0.30, 0.22, 0.16]
)

akses_internet = np.random.choice(
    ["Wifi Rumah", "Paket Data", "Tidak Ada"],
    N, p=[0.25, 0.55, 0.20]
)

# ═══════════════════════════════════════════════════════════════════════
# 5. STATUS BANTUAN SOSIAL
# ═══════════════════════════════════════════════════════════════════════

# DTKS — lebih mungkin terdaftar jika penghasilan rendah
prob_dtks = np.where(gaji_ortu < 1000000, 0.80,
            np.where(gaji_ortu < 2000000, 0.45,
            np.where(gaji_ortu < 3500000, 0.15, 0.03)))
terdaftar_dtks = np.array(
    [np.random.choice([1, 0], p=[p, 1 - p]) for p in prob_dtks]
)

# KIP — prioritas penerima DTKS
penerima_kip = np.where(
    terdaftar_dtks == 1,
    np.random.choice([1, 0], N, p=[0.60, 0.40]),
    np.random.choice([1, 0], N, p=[0.05, 0.95])
)

# PKH — Program Keluarga Harapan
penerima_pkh = np.where(
    terdaftar_dtks == 1,
    np.random.choice([1, 0], N, p=[0.50, 0.50]),
    np.random.choice([1, 0], N, p=[0.03, 0.97])
)

status_bpjs = np.random.choice(
    ["PBI (Gratis)", "Mandiri Kelas 3", "Mandiri Kelas 2/1", "Tidak Punya"],
    N, p=[0.35, 0.20, 0.15, 0.30]
)

bantuan_lokal = np.random.choice([1, 0], N, p=[0.12, 0.88])

# ═══════════════════════════════════════════════════════════════════════
# 6. ENGINE SKOR RISIKO PUTUS SEKOLAH
# ═══════════════════════════════════════════════════════════════════════

skor_risiko = np.zeros(N, dtype=int)

# Dimensi Akademik
skor_risiko += np.where(kehadiran < 65, 4,
               np.where(kehadiran < 75, 2,
               np.where(kehadiran < 85, 1, 0)))
skor_risiko += np.where(rata_nilai < 55, 3,
               np.where(rata_nilai < 65, 2,
               np.where(rata_nilai < 70, 1, 0)))
skor_risiko += np.where(jumlah_remedial >= 5, 2,
               np.where(jumlah_remedial >= 3, 1, 0))
skor_risiko += pernah_tinggal_kelas * 2

# Dimensi Keluarga
skor_risiko += np.isin(status_ortu, ["Yatim Piatu", "Yatim", "Piatu"]).astype(int) * 2
skor_risiko += np.where(status_ortu == "Cerai", 1, 0)
skor_risiko += np.where(jumlah_saudara >= 5, 2,
               np.where(jumlah_saudara >= 3, 1, 0))
skor_risiko += np.isin(pendidikan_ortu, ["Tidak Sekolah", "SD"]).astype(int)
skor_risiko += siswa_bekerja * 2

# Dimensi Ekonomi
skor_risiko += np.where(gaji_ortu < 800000, 4,
               np.where(gaji_ortu < 1500000, 3,
               np.where(gaji_ortu < 2500000, 1, 0)))
skor_risiko += np.where(pengeluaran > gaji_ortu * 1.1, 1, 0)  # defisit

# Dimensi Kondisi
skor_risiko += np.where(kondisi_rumah == "Tidak Layak Huni", 2,
               np.where(kondisi_rumah == "Semi Permanen", 1, 0))
skor_risiko += np.where(jarak_sekolah_km > 10, 2,
               np.where(jarak_sekolah_km > 5, 1, 0))
skor_risiko += np.where(akses_internet == "Tidak Ada", 1, 0)

# Label Risiko
status_risiko = np.where(
    skor_risiko >= 10, "Tinggi",
    np.where(skor_risiko >= 5, "Sedang", "Rendah")
)

# ═══════════════════════════════════════════════════════════════════════
# 7. ENGINE KELAYAKAN BANTUAN SOSIAL
# ═══════════════════════════════════════════════════════════════════════

skor_bansos = np.zeros(N, dtype=int)
skor_bansos += np.where(gaji_ortu < 1000000, 5,
               np.where(gaji_ortu < 2000000, 3,
               np.where(gaji_ortu < 3500000, 1, 0)))
skor_bansos += np.where(kondisi_rumah == "Tidak Layak Huni", 3,
               np.where(kondisi_rumah == "Semi Permanen", 1, 0))
skor_bansos += np.isin(status_ortu, ["Yatim Piatu", "Yatim", "Piatu"]).astype(int) * 3
skor_bansos += np.where(penerima_kip == 0, 1, 0)   # belum dapat KIP
skor_bansos += np.where(terdaftar_dtks == 1, 2, 0)
skor_bansos += np.where(jumlah_saudara >= 4, 2, 0)

kelayakan_bansos = np.where(
    skor_bansos >= 8, "Sangat Layak",
    np.where(skor_bansos >= 5, "Layak",
    np.where(skor_bansos >= 2, "Perlu Ditinjau", "Tidak Layak"))
)

rekomendasi_bansos = np.where(
    (kelayakan_bansos == "Sangat Layak") & (penerima_kip == 0), "KIP Prioritas",
    np.where(
        (kelayakan_bansos == "Sangat Layak") & (penerima_pkh == 0), "PKH Prioritas",
        np.where(kelayakan_bansos == "Layak", "Bansos Daerah",
        np.where(kelayakan_bansos == "Perlu Ditinjau", "Verifikasi Lapangan", "—"))
    )
)

# ═══════════════════════════════════════════════════════════════════════
# 8. SUSUN DATAFRAME
# ═══════════════════════════════════════════════════════════════════════

df = pd.DataFrame({
    # ── Identitas ──
    "NISN"                      : nisn,
    "Nama_Lengkap"              : nama_lengkap,
    "Jenis_Kelamin"             : jenis_kelamin,
    "Usia"                      : usia,
    "Kelas"                     : kelas,
    "Jurusan"                   : jurusan,

    # ── Akademik ──
    "Kehadiran_Persen"          : kehadiran,
    "Rata_Nilai"                : rata_nilai,
    "Jumlah_Remedial"           : jumlah_remedial,
    "Peringkat_Kelas"           : peringkat_kelas,
    "Pernah_Tinggal_Kelas"      : pernah_tinggal_kelas,
    "Surat_Peringatan"          : surat_peringatan,
    "Status_Ekstrakurikuler"    : ekskul,
    "Siswa_Bekerja"             : siswa_bekerja,

    # ── Keluarga ──
    "Status_Ortu"               : status_ortu,
    "Jumlah_Saudara"            : jumlah_saudara,
    "Pendidikan_Tertinggi_Ortu" : pendidikan_ortu,
    "Pekerjaan_Ayah"            : pekerjaan_ayah,
    "Pekerjaan_Ibu"             : pekerjaan_ibu,

    # ── Sosial-Ekonomi ──
    "Penghasilan_Keluarga_Bulan": gaji_ortu,
    "Pengeluaran_Keluarga_Bulan": pengeluaran,
    "Kepemilikan_Rumah"         : kepemilikan_rumah,
    "Kondisi_Rumah"             : kondisi_rumah,
    "Akses_Listrik"             : akses_listrik,
    "Sumber_Air_Bersih"         : sumber_air,
    "Jarak_Ke_Sekolah_KM"       : jarak_sekolah_km,
    "Moda_Transportasi"         : moda_transportasi,
    "Akses_Internet"            : akses_internet,

    # ── Bantuan Sosial ──
    "Terdaftar_DTKS"            : terdaftar_dtks,
    "Penerima_KIP"              : penerima_kip,
    "Penerima_PKH"              : penerima_pkh,
    "Status_BPJS"               : status_bpjs,
    "Bantuan_Lokal_Daerah"      : bantuan_lokal,

    # ── Target / Label ──
    "Skor_Risiko"               : skor_risiko,
    "Status_Risiko"             : status_risiko,
    "Skor_Kelayakan_Bansos"     : skor_bansos,
    "Kelayakan_Bansos"          : kelayakan_bansos,
    "Rekomendasi_Bansos"        : rekomendasi_bansos,
})

# ─── Validasi keunikan ───────────────────────────────────────────────
assert df["Nama_Lengkap"].nunique() == N, "ERROR: Ada nama yang duplikat!"
assert df["NISN"].nunique() == N,         "ERROR: Ada NISN yang duplikat!"

# ═══════════════════════════════════════════════════════════════════════
# 9. SIMPAN & RINGKASAN
# ═══════════════════════════════════════════════════════════════════════

df.to_csv("data_dummy.csv", index=False)

print("=" * 60)
print("  RSI — Data Dummy Berhasil Dibuat")
print("=" * 60)
print(f"  Total Siswa  : {len(df)}")
print(f"  Total Kolom  : {len(df.columns)}")
print(f"  Nama Unik    : {df['Nama_Lengkap'].nunique()} ✅")
print(f"  NISN Unik    : {df['NISN'].nunique()} ✅")
print()
print("── Distribusi Status Risiko ──────────────────────────────")
print(df["Status_Risiko"].value_counts().to_string())
print()
print("── Distribusi Kelayakan Bansos ───────────────────────────")
print(df["Kelayakan_Bansos"].value_counts().to_string())
print()
print("── Statistik Penghasilan Keluarga ────────────────────────")
stats = df["Penghasilan_Keluarga_Bulan"].describe()
for label, val in stats.items():
    if label == "count":
        print(f"  {label:<10}: {int(val)}")
    else:
        print(f"  {label:<10}: Rp {val:>15,.0f}")
print()
print("✅ File 'data_dummy.csv' tersimpan.")