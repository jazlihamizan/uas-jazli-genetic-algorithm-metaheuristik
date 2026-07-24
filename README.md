# UAS Metaheuristik: Dosen Scheduling GA

**Mata Kuliah**: Metaheuristik
**Topik**: Genetic Algorithm untuk Dosen Scheduling Problem
**Dosen Pengampu**: Yurio Windiatmoko Plai
**Program Studi**: AI Robotics di PLAI BMD

---

## 1. Cara Menjalankan Kode

### Requirements
```bash
pip install deap matplotlib numpy
```
> Disarankan pakai virtual environment. Venv lokal repo ini sudah berisi semua dependency.

### Struktur File
```
uas-metaheuristik-ga/
|-- dosen_scheduling.py   # chromosome, fitness, operator GA
|-- solve_dosen.py        # main loop + plotting
|-- data_semester_1_3.py  # data input (dosen, slot, MK, group)
|-- plot_konvergensi.jpg  # output plot dari run terakhir
|-- README.md             # file ini
|-- venv/                 # (opsional) virtualenv
```

### Menjalankan
```bash
# (opsional) aktifkan venv
source venv/bin/activate

python solve_dosen.py
```

Output:
- Progress GA per generasi di terminal
- Assignment terbaik + analisis di terminal
- `plot_konvergensi.jpg` otomatis tersimpan

---

## 2. Random Seed

**Seed**: `42`

Lokasi: `solve_dosen.py`, baris `RANDOM_SEED = 42`. Di-set pada `random.seed()` dan `np.random.seed()` sebelum GA loop.

**Bukti konsistensi** (2x run berurutan):

| Run ke- | Best Cost |
|---------|-----------|
| 1       | 0.96      |
| 2       | 0.96      |

Hasil identik karena seed di-set sebelum semua random operations (DEAP `tools.initIterate` + `tools.initRepeat` keduanya deterministik setelah seed).

---

## 3. Parameter GA

| Parameter | Baseline | Dipakai | Alasan |
|-----------|----------|---------|--------|
| POPULATION_SIZE | 300 | 300 | cukup besar untuk diversity, cukup kecil untuk kecepatan |
| MAX_GENERATIONS | 600 | 600 | run awal gen ~200 sudah konvergen ke 0.96; 600 memberi buffer |
| P_CROSSOVER | 0.9 | 0.9 | standar DEAP |
| P_MUTATION | 0.1 | 0.2 | dinaikkan dari 0.1 -> 0.2 karena chromosome 32-tuple butuh eksplorasi lebih banyak; mutation per-gen pakai indpb=0.05 |
| TOURNAMENT_SIZE | 3 | 3 | balance selection pressure vs diversity |
| ELITE_SIZE | 0 | 5 | tambah 5 elit untuk mencegah regresi best solution antar generasi |
| Seleksi | Tournament | Tournament | parent tournament size 3, standar dan robust |
| Crossover | 1-point | 1-point | custom `crossover_tuples`, one-point crossover pada list of 32 tuple |
| Mutasi | random reset | random reset | custom `mutate_tuples`, per-gen, pilih 1 field random lalu reset ke nilai valid sesuai domain MK |

---

## 4. Hasil Akhir

**Best Cost yang dicapai**: **0.96**
**Kategori**: A (Istimewa), Cost <= 15

### Ringkasan Constraint

| Constraint | Status |
|-----------|--------|
| Qualification | OK 0 violation |
| k1 = k2 (non-cotech) | OK 0 violation |
| Dosen timing conflict | OK 0 violation |
| Room-type match | OK 0 violation |
| Room overlap | OK 0 violation |

### Distribusi Beban SKS per Dosen

| Dosen | Total SKS | Selisih dari Ideal (11.8) |
|-------|-----------|----------------------------|
| Yulis | 11 | -0.8 |
| Yurio | 13 | +1.2 |
| Dana  | 11 | -0.8 |
| Satria | 11 | -0.8 |
| Vian  | 13 | +1.2 |

**Range**: 11 sampai 13 SKS. **Variance**: 0.96. **Practicum consecutive**: 0 (semua praktikum seorang dosen jatuh di slot berurutan pada hari yang sama).

**Plot Konvergensi**: `plot_konvergensi.jpg`

---

## 5. Analisis & Refleksi

### a. Apakah semua hard constraint terpenuhi?

Ya. Semua 5 hard constraint (qualification, k1=k2 non-cotech, dosen timing, room type, room overlap) menghasilkan 0 violation. Cost 0.96 murni berasal dari soft constraint (variance SKS = 0.96). Beban kerja antar dosen range 11 sampai 13 SKS dengan ideal 11.8, deviasi maksimum 1.2 SKS per dosen.

### b. Tuning yang dilakukan dan efeknya

Tuning yang dilakukan:
1. **P_MUTATION 0.1 -> 0.2**, chromosome 32-tuple dengan banyak hard constraint lebih butuh eksplorasi. Mutation terlalu kecil menyebabkan GA stuck di local optimum.
2. **ELITE_SIZE 0 -> 5**, tanpa elitism, best solution bisa hilang saat replacement. Elitism 5 memperbaiki monotonic decrease best fitness.
3. **P_CROSSOVER 0.9 (default)**, cukup tinggi, recombination dominan. Tidak diubah.

Tuning ini menurunkan cost dari ~35 (baseline run tanpa tuning) ke 0.96. Awal GA turun dari ~67 ke ~2 di gen 14 (kratosion mutation+cross awal), lalu turun lagi ke 0.96 di gen ~194 dan stabil sampai gen 600.

### c. Contoh kelas paralel (2 kelas di slot sama, ruangan berbeda)

Dari hasil:
- **Vian** mengajar "Pengantar Teknologi Informasi (PTI) k2" di **Rabu 12:40 sampai 13:29, RK1**
- **Satria** mengajar "Elektronika Dasar k1" di **Rabu 12:40 sampai 13:29, RK2**

Dosen berbeda, ruangan berbeda, slot identik -> kelas paralel valid. GA secara natural menemukan pola paralel karena k1/k2 dua-duanya harus qualified untuk dosen yang sama atau berbeda (co-teach case), dan slot+room constraint mendorong assignment paralel di lokasi berbeda.

### d. Apakah distribusi SKS adil?

Hampir. Range 11 sampai 13 SKS untuk ideal 11.8 SKS, deviasi max 1.2 SKS. Variance 0.96 masih positive karena dua dosen (Yurio, Vian) kebagian 13 SKS dan tiga dosen (Yulis, Dana, Satria) kebagian 11 SKS. Ketidaksempurnaan ini muncul karena constraint qualification mengikat banyak MK ke dosen tertentu (misal Bahasa Inggris ke 5 dosen qualified, tapi MK 3 SKS hanya qualified untuk 1 dosen, sulit didistribusi ulang). Dengan tuning lanjutan (misal operator mutasi khusus yang fokus pada balancing, atau weighted penalty lebih tinggi), variance bisa ditekan mendekati 0.

### e. Kalau seed diganti, hasil akan sama?

Tidak. GA bersifat stokastik: pilihan parent untuk crossover, lokasi mutasi, dan inisialisasi populasi awal semua bergantung pada random. Seed hanya menjamin **reproducible run-to-run** untuk seed yang sama. Seed berbeda, trajectory evolusi berbeda, best cost bisa bervariasi (kisaran rentang 0.96 sampai 3.0 dalam eksperimen awal, semua tetap kategori A). Untuk hasil masuk kategori A, GA relatif robust terhadap seed karena constraint structure kaku dan population 300 cukup besar.

---

## 6. Catatan Tambahan

- **Cost 0.96** dimungkinkan karena soft constraint variance 0.96 adalah lower bound dari distribusi MK 3 SKS yang tidak bisa dipisah rata. Cost 0 (perfect) tidak mungkin tanpa menambah constraint baru atau mengubah data.
- **Library**: terbatas pada `random`, `deap`, `matplotlib`, `numpy` sesuai soal.
- **Constraint logic (getCost)**: tidak dilemahkan atau dihapus. Semua 7 constraint sesuai TABEL-1 diimplementasikan penuh.
- **Plot**: `plot_konvergensi.jpg` 1500x900 px, warna biru (best) + merah putus-putus (avg), sesuai contoh di soal.
