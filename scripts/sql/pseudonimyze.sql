CREATE TABLE data_siswa_mentah (
    NISN VARCHAR(15) PRIMARY KEY,
    Nama_Lengkap VARCHAR(100),
    Jenis_Kelamin VARCHAR(20),
    Usia INT,
    Kelas INT,
    Jurusan VARCHAR(50),
    Kehadiran_Persen INT,
    Rata_Nilai INT,
    Jumlah_Remedial INT,
    Peringkat_Kelas INT,
    Pernah_Tinggal_Kelas INT,
    Surat_Peringatan INT,
    Status_Ekstrakurikuler VARCHAR(50),
    Siswa_Bekerja INT,
    Status_Ortu VARCHAR(50),
    Jumlah_Saudara INT,
    Pendidikan_Tertinggi_Ortu VARCHAR(50),
    Pekerjaan_Ayah VARCHAR(50),
    Pekerjaan_Ibu VARCHAR(50),
    Penghasilan_Keluarga_Bulan BIGINT,
    Pengeluaran_Keluarga_Bulan BIGINT,
    Kepemilikan_Rumah VARCHAR(50),
    Kondisi_Rumah VARCHAR(50),
    Akses_Listrik VARCHAR(50),
    Sumber_Air_Bersih VARCHAR(50),
    Jarak_Ke_Sekolah_KM FLOAT,
    Moda_Transportasi VARCHAR(50),
    Akses_Internet VARCHAR(50),
    Terdaftar_DTKS INT,
    Penerima_KIP INT,
    Penerima_PKH INT,
    Status_BPJS VARCHAR(50),
    Bantuan_Lokal_Daerah INT,
    Skor_Risiko INT,
    Status_Risiko VARCHAR(50),
    Skor_Kelayakan_Bansos INT,
    Kelayakan_Bansos VARCHAR(50),
    Rekomendasi_Bansos VARCHAR(50)
);

-- 1. Buat Tabel Tujuan (Tanpa Nama & NISN diganti Pseudo_ID)
CREATE TABLE IF NOT EXISTS data_siswa_anonim (
    Pseudo_ID TEXT PRIMARY KEY,
    Usia INT,
    Kelas INT,
    Kehadiran_Persen INT,
    Rata_Nilai INT,
    Penghasilan_Keluarga_Bulan BIGINT,
    Skor_Risiko INT,
    Status_Risiko VARCHAR(50),
    Rekomendasi_Bansos VARCHAR(50)
);

-- 2. Buat Procedure Pseudonymization
CREATE OR REPLACE PROCEDURE pr_pseudonymize_data()
LANGUAGE plpgsql AS $$
BEGIN
    -- Kosongkan tabel riset setiap kali procedure dijalankan agar bersih
    TRUNCATE TABLE data_siswa_anonim;

    -- Proses pemindahan data + Hashing (Pseudonymization)
    INSERT INTO data_siswa_anonim (
        Pseudo_ID, 
        Usia, 
        Kelas, 
        Kehadiran_Persen, 
        Rata_Nilai, 
        Penghasilan_Keluarga_Bulan, 
        Skor_Risiko, 
        Status_Risiko, 
        Rekomendasi_Bansos
    )
    SELECT 
        MD5(NISN::TEXT || 'rahasia2024'), -- Mengubah NISN jadi kode rahasia
        Usia,
        Kelas,
        Kehadiran_Persen,
        Rata_Nilai,
        Penghasilan_Keluarga_Bulan,
        Skor_Risiko,
        Status_Risiko,
        Rekomendasi_Bansos
    FROM data_siswa_mentah;
    
    RAISE NOTICE 'Proses selesai! Data telah dipindah ke tabel riset.';
END;
$$;

CALL pr_pseudonymize_data();

SELECT * FROM data_siswa_anonim LIMIT 10;

SELECT * FROM data_siswa_mentah LIMIT 10;
