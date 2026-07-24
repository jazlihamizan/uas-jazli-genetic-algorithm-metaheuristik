"""
Data Input untuk Dosen Scheduling Problem
Semester 1 (2 kelas) + Semester 3 (1 kelas)

Ini adalah DATA berdasarkan informasi jadwal kurikulum.
"""

# ===== 1. DOSEN DATA =====
dosen_data = {
    0: {"name": "Yulis", "id": 0},
    1: {"name": "Yurio", "id": 1},
    2: {"name": "Dana", "id": 2},
    3: {"name": "Satria", "id": 3},
    4: {"name": "Vian", "id": 4},
}


# ===== 2. TIME SLOTS =====
# SAMA dengan Semester 2 schedule!
# 40 time slots / minggu (5 hari × 8 slots/hari)
# Ruangan: RK1, RK2 (Ruang Kuliah) dan LAB (Lab Robotik)

time_slots = [
    # ===== SENIN =====
    {"id": 0, "hari": "Senin", "jam": "07:30-08:19", "room": "RK1"},
    {"id": 1, "hari": "Senin", "jam": "08:20-09:09", "room": "LAB"},
    {"id": 2, "hari": "Senin", "jam": "09:10-09:59", "room": "LAB"},
    {"id": 3, "hari": "Senin", "jam": "10:00-10:49", "room": "RK1"},
    {"id": 4, "hari": "Senin", "jam": "10:50-11:39", "room": "RK2"},
    {"id": 5, "hari": "Senin", "jam": "12:40-13:29", "room": "LAB"},  # Istirahat 11:40-12:39
    {"id": 6, "hari": "Senin", "jam": "13:30-14:19", "room": "RK1"},
    {"id": 7, "hari": "Senin", "jam": "14:20-15:09", "room": "RK2"},
    
    # ===== SELASA =====
    {"id": 8, "hari": "Selasa", "jam": "07:30-08:19", "room": "RK1"},
    {"id": 9, "hari": "Selasa", "jam": "08:20-09:09", "room": "RK2"},
    {"id": 10, "hari": "Selasa", "jam": "09:10-09:59", "room": "RK1"},
    {"id": 11, "hari": "Selasa", "jam": "10:00-10:49", "room": "RK2"},
    {"id": 12, "hari": "Selasa", "jam": "10:50-11:39", "room": "RK1"},
    {"id": 13, "hari": "Selasa", "jam": "12:40-13:29", "room": "RK2"},  # Istirahat
    {"id": 14, "hari": "Selasa", "jam": "14:20-15:09", "room": "RK1"},  # Jam 13:30 skip, mulai 14:20
    {"id": 15, "hari": "Selasa", "jam": "15:10-15:59", "room": "RK2"},  # After istirahat
    
    # ===== RABU =====
    {"id": 16, "hari": "Rabu", "jam": "07:30-08:19", "room": "RK1"},
    {"id": 17, "hari": "Rabu", "jam": "08:20-09:09", "room": "LAB"},
    {"id": 18, "hari": "Rabu", "jam": "09:10-09:59", "room": "LAB"},
    {"id": 19, "hari": "Rabu", "jam": "10:00-10:49", "room": "LAB"},
    {"id": 20, "hari": "Rabu", "jam": "10:50-11:39", "room": "LAB"},
    {"id": 21, "hari": "Rabu", "jam": "12:40-13:29", "room": "LAB"},  # Istirahat
    {"id": 22, "hari": "Rabu", "jam": "13:30-14:19", "room": "LAB"},
    {"id": 23, "hari": "Rabu", "jam": "14:20-15:09", "room": "RK1"},
    
    # ===== KAMIS =====
    {"id": 24, "hari": "Kamis", "jam": "07:30-08:19", "room": "RK1"},
    {"id": 25, "hari": "Kamis", "jam": "08:20-09:09", "room": "LAB"},
    {"id": 26, "hari": "Kamis", "jam": "09:10-09:59", "room": "LAB"},
    {"id": 27, "hari": "Kamis", "jam": "10:00-10:49", "room": "LAB"},
    {"id": 28, "hari": "Kamis", "jam": "10:50-11:39", "room": "LAB"},
    {"id": 29, "hari": "Kamis", "jam": "12:40-13:29", "room": "LAB"},  # Istirahat
    {"id": 30, "hari": "Kamis", "jam": "13:30-14:19", "room": "RK1"},
    {"id": 31, "hari": "Kamis", "jam": "14:20-15:09", "room": "RK2"},
    
    # ===== JUMAT =====
    {"id": 32, "hari": "Jumat", "jam": "07:30-08:19", "room": "RK1"},
    {"id": 33, "hari": "Jumat", "jam": "08:20-09:09", "room": "LAB"},
    {"id": 34, "hari": "Jumat", "jam": "09:10-09:59", "room": "LAB"},
    {"id": 35, "hari": "Jumat", "jam": "10:00-10:49", "room": "LAB"},
    {"id": 36, "hari": "Jumat", "jam": "10:50-11:39", "room": "LAB"},
    {"id": 37, "hari": "Jumat", "jam": "12:40-13:29", "room": "LAB"},  # Istirahat
    {"id": 38, "hari": "Jumat", "jam": "13:30-14:19", "room": "LAB"},
    {"id": 39, "hari": "Jumat", "jam": "14:20-15:09", "room": "RK2"},
    # Note: Slot 15:10-15:39 adalah istirahat kedua, skip dari schedule
]


# ===== 3. MK INSTANCES =====
# Total: 20 (Sem1, 2 kelas) + 12 (Sem3, 1 kelas) = 32

mk_instances = [
    # ===== SEMESTER 1 (20 instances) =====
    # Kelas 1
    {"id": 0, "name": "Pengantar Kecerdasan Buatan", "kelas": "k1", "semester": 1, 
     "type": "teori", "dosen_qualified": ["Yulis"], "is_co_teach": False, "sks": 2},
    {"id": 1, "name": "Aljabar Linear & Matriks", "kelas": "k1", "semester": 1,
     "type": "teori", "dosen_qualified": ["Yurio"], "is_co_teach": False, "sks": 3},
    {"id": 2, "name": "Logika dan algoritma", "kelas": "k1", "semester": 1,
     "type": "teori", "dosen_qualified": ["Dana"], "is_co_teach": False, "sks": 2},
    {"id": 3, "name": "Praktikum Pemrograman C++", "kelas": "k1", "semester": 1,
     "type": "praktek", "dosen_qualified": ["Dana"], "is_co_teach": False, "sks": 1},
    {"id": 4, "name": "Design thinking, Produk, Manajemen", "kelas": "k1", "semester": 1,
     "type": "teori", "dosen_qualified": ["Dana", "Yurio"], "is_co_teach": True, "sks": 2},
    {"id": 5, "name": "Pengantar Teknologi Informasi (PTI)", "kelas": "k1", "semester": 1,
     "type": "teori", "dosen_qualified": ["Satria", "Vian"], "is_co_teach": True, "sks": 2},
    {"id": 6, "name": "Praktikum Gambar Teknik", "kelas": "k1", "semester": 1,
     "type": "praktek", "dosen_qualified": ["Yulis"], "is_co_teach": False, "sks": 2},
    {"id": 7, "name": "Elektronika Dasar", "kelas": "k1", "semester": 1,
     "type": "teori", "dosen_qualified": ["Satria"], "is_co_teach": False, "sks": 2},
    {"id": 8, "name": "Praktikum Elektronika Dasar", "kelas": "k1", "semester": 1,
     "type": "praktek", "dosen_qualified": ["Satria"], "is_co_teach": False, "sks": 1},
    {"id": 9, "name": "Fisika Terapan", "kelas": "k1", "semester": 1,
     "type": "teori", "dosen_qualified": ["Vian"], "is_co_teach": False, "sks": 3},
    
    # Kelas 2
    {"id": 10, "name": "Pengantar Kecerdasan Buatan", "kelas": "k2", "semester": 1, 
     "type": "teori", "dosen_qualified": ["Yulis"], "is_co_teach": False, "sks": 2},
    {"id": 11, "name": "Aljabar Linear & Matriks", "kelas": "k2", "semester": 1,
     "type": "teori", "dosen_qualified": ["Yurio"], "is_co_teach": False, "sks": 3},
    {"id": 12, "name": "Logika dan algoritma", "kelas": "k2", "semester": 1,
     "type": "teori", "dosen_qualified": ["Dana"], "is_co_teach": False, "sks": 2},
    {"id": 13, "name": "Praktikum Pemrograman C++", "kelas": "k2", "semester": 1,
     "type": "praktek", "dosen_qualified": ["Dana"], "is_co_teach": False, "sks": 1},
    {"id": 14, "name": "Design thinking, Produk, Manajemen", "kelas": "k2", "semester": 1,
     "type": "teori", "dosen_qualified": ["Dana", "Yurio"], "is_co_teach": True, "sks": 2},
    {"id": 15, "name": "Pengantar Teknologi Informasi (PTI)", "kelas": "k2", "semester": 1,
     "type": "teori", "dosen_qualified": ["Satria", "Vian"], "is_co_teach": True, "sks": 2},
    {"id": 16, "name": "Praktikum Gambar Teknik", "kelas": "k2", "semester": 1,
     "type": "praktek", "dosen_qualified": ["Yulis"], "is_co_teach": False, "sks": 2},
    {"id": 17, "name": "Elektronika Dasar", "kelas": "k2", "semester": 1,
     "type": "teori", "dosen_qualified": ["Satria"], "is_co_teach": False, "sks": 2},
    {"id": 18, "name": "Praktikum Elektronika Dasar", "kelas": "k2", "semester": 1,
     "type": "praktek", "dosen_qualified": ["Satria"], "is_co_teach": False, "sks": 1},
    {"id": 19, "name": "Fisika Terapan", "kelas": "k2", "semester": 1,
     "type": "teori", "dosen_qualified": ["Vian"], "is_co_teach": False, "sks": 3},
    
    # ===== SEMESTER 3 (12 instances) =====
    {"id": 20, "name": "Statistika & Machine learning", "kelas": "k1", "semester": 3,
     "type": "teori", "dosen_qualified": ["Yurio"], "is_co_teach": False, "sks": 2},
    {"id": 21, "name": "Pratikum Statistika & Machine Learning", "kelas": "k1", "semester": 3,
     "type": "praktek", "dosen_qualified": ["Yurio"], "is_co_teach": False, "sks": 1},
    {"id": 22, "name": "Praktikum IoT", "kelas": "k1", "semester": 3,
     "type": "praktek", "dosen_qualified": ["Vian", "Yulis"], "is_co_teach": True, "sks": 2},
    {"id": 23, "name": "Pengembangan Apk berbasis web", "kelas": "k1", "semester": 3,
     "type": "teori", "dosen_qualified": ["Dana"], "is_co_teach": False, "sks": 2},
    {"id": 24, "name": "Praktikum Pengembangan Apk berbasis web", "kelas": "k1", "semester": 3,
     "type": "praktek", "dosen_qualified": ["Dana"], "is_co_teach": False, "sks": 1},
    {"id": 25, "name": "Bahasa Inggris", "kelas": "k1", "semester": 3,
     "type": "teori", "dosen_qualified": ["Yulis", "Yurio", "Dana", "Satria", "Vian"], "is_co_teach": False, "sks": 2},
    {"id": 26, "name": "Perancangan Sistem Elektronika", "kelas": "k1", "semester": 3,
     "type": "teori", "dosen_qualified": ["Vian"], "is_co_teach": False, "sks": 2},
    {"id": 27, "name": "Praktikum Perancangan Sistem Elektronika", "kelas": "k1", "semester": 3,
     "type": "praktek", "dosen_qualified": ["Vian"], "is_co_teach": False, "sks": 1},
    {"id": 28, "name": "Antarmuka & Akuisisi Data", "kelas": "k1", "semester": 3,
     "type": "teori", "dosen_qualified": ["Satria"], "is_co_teach": False, "sks": 2},
    {"id": 29, "name": "Praktikum Antarmuka & Akuisisi Data", "kelas": "k1", "semester": 3,
     "type": "praktek", "dosen_qualified": ["Satria"], "is_co_teach": False, "sks": 1},
    {"id": 30, "name": "Computer Vision", "kelas": "k1", "semester": 3,
     "type": "teori", "dosen_qualified": ["Yulis"], "is_co_teach": False, "sks": 2},
    {"id": 31, "name": "Praktikum Computer Vision", "kelas": "k1", "semester": 3,
     "type": "praktek", "dosen_qualified": ["Yulis"], "is_co_teach": False, "sks": 1},
]


# ===== 4. MK GROUPS (untuk track k1 & k2 yang harus same dosen) =====
mk_groups = [
    # Semester 1 - Non Co-teaching
    {"mk_name": "Pengantar Kecerdasan Buatan", "instances": [0, 10], "is_co_teach": False},
    {"mk_name": "Aljabar Linear & Matriks", "instances": [1, 11], "is_co_teach": False},
    {"mk_name": "Logika dan algoritma", "instances": [2, 12], "is_co_teach": False},
    {"mk_name": "Praktikum Pemrograman C++", "instances": [3, 13], "is_co_teach": False},
    {"mk_name": "Elektronika Dasar", "instances": [7, 17], "is_co_teach": False},
    {"mk_name": "Praktikum Elektronika Dasar", "instances": [8, 18], "is_co_teach": False},
    {"mk_name": "Fisika Terapan", "instances": [9, 19], "is_co_teach": False},
    {"mk_name": "Praktikum Gambar Teknik", "instances": [6, 16], "is_co_teach": False},
    
    # Semester 1 - Co-teaching (flexible assign, bisa beda dosen)
    {"mk_name": "Design thinking, Produk, Manajemen", "instances": [4, 14], "is_co_teach": True},
    {"mk_name": "Pengantar Teknologi Informasi (PTI)", "instances": [5, 15], "is_co_teach": True},
]


# ===== SUMMARY =====
if __name__ == "__main__":
    print("="*70)
    print("DOSEN SCHEDULING - DATA SUMMARY")
    print("="*70)
    print(f"\nDosen: {len(dosen_data)}")
    for did, ddata in dosen_data.items():
        print(f"  {did}: {ddata['name']}")
    
    print(f"\nTime Slots: {len(time_slots)}")
    lab_slots = len([s for s in time_slots if s["room"] == "LAB"])
    rk_slots = len([s for s in time_slots if s["room"] in ["RK1", "RK2"]])
    print(f"  - LAB: {lab_slots} slots")
    print(f"  - Ruang Kuliah (RK1/RK2): {rk_slots} slots")
    
    print(f"\nMK Instances: {len(mk_instances)}")
    sem1_count = len([m for m in mk_instances if m["semester"] == 1])
    sem3_count = len([m for m in mk_instances if m["semester"] == 3])
    print(f"  - Semester 1: {sem1_count} instances")
    print(f"  - Semester 3: {sem3_count} instances")
    
    print(f"\nMK Groups (for k1=k2 constraint): {len(mk_groups)}")
    cotech = len([g for g in mk_groups if g["is_co_teach"]])
    non_cotech = len([g for g in mk_groups if not g["is_co_teach"]])
    print(f"  - Non Co-teaching: {non_cotech} groups")
    print(f"  - Co-teaching (flexible): {cotech} groups")
    
    print("\n" + "="*70)
