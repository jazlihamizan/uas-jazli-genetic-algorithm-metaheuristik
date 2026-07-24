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
|-- dosen_scheduling.py   # fitness function (class DosenSchedulingProblem, reference v2 dari dosen)
|-- solve_dosen.py        # main loop GA + plotting
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

**Bukti konsistensi** (3x run berurutan):

| Run ke- | Best Cost |
|---------|-----------|
| 1       | 5.80      |
| 2       | 5.80      |
| 3       | 5.80      |

Hasil identik karena seed di-set sebelum semua random operations (DEAP `tools.initIterate` + `tools.initRepeat` keduanya deterministik setelah seed).

---

## 3. Parameter GA

| Parameter | Baseline | Dipakai | Alasan |
|-----------|----------|---------|--------|
| POPULATION_SIZE | 300 | 300 | cukup besar untuk diversity, cukup kecil untuk kecepatan |
| MAX_GENERATIONS | 600 | 600 | run awal gen ~200 sudah konvergen ke 5.80; 600 memberi buffer |
| P_CROSSOVER | 0.9 | 0.9 | standar DEAP |
| P_MUTATION | 0.1 | 0.2 | dinaikkan dari 0.1 -> 0.2 karena chromosome 32-tuple butuh eksplorasi lebih banyak; mutation per-gen pakai indpb=0.05 |
| TOURNAMENT_SIZE | 3 | 3 | balance selection pressure vs diversity |
| ELITE_SIZE | 0 | 5 | tambah 5 elit untuk mencegah regresi best solution antar generasi |
| Seleksi | Tournament | Tournament | parent tournament size 3, standar dan robust |
| Crossover | 1-point | 1-point | custom `crossover_tuples`, one-point crossover pada list of 32 tuple |
| Mutasi | random reset | random reset | custom `mutate_tuples`, per-gen, pilih 1 field random lalu reset ke nilai valid sesuai domain MK |
| Fitness function | DosenSchedulingProblem.getCost | DosenSchedulingProblem.getCost | mengikuti referensi dosen_scheduling_v2.py |

---

## 4. Hasil Akhir

**Best Cost yang dicapai**: **5.80**
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

**Range**: 11 sampai 13 SKS. **Variance (sum of squared deviations)**: 4.80. **Practicum kolejalah**: 2 kejadian non-consecutive (penalty 1.0).

**Plot Konvergensi**: `plot_konvergensi.jpg`

---

## 5. Analisis & Refleksi

### a. Apakah semua hard constraint terpenuhi?

Ya. Semua 5 hard constraint (qualification, k1=k2 non-cotech, dosen timing, room type, room overlap) menghasilkan 0 violation. Cost 5.80 berasal dari soft constraint: variance SKS = 4.80 (sum of squared deviations) + prac consecutive penalty 1.0. Beban kerja antar dosen range 11 sampai 13 SKS dengan ideal 11.8, deviasi maksimum 1.2 SKS per dosen.

### b. Tuning yang dilakukan dan efeknya

Tuning yang dilakukan:
1. **P_MUTATION 0.1 -> 0.2**, chromosome 32-tuple dengan banyak hard constraint lebih butuh eksplorasi. Mutation terlalu kecil menyebabkan GA stuck di local optimum.
2. **ELITE_SIZE 0 -> 5**, tanpa elitism, best solution bisa hilang saat replacement. Elitism 5 memperbaiki monotonic decrease best fitness.
3. **P_CROSSOVER 0.9 (default)**, cukup tinggi, recombination dominan. Tidak diubah.
4. **Fitness function reference v2 (dari dosen)**: menggunakan class `DosenSchedulingProblem` dari `dosen_scheduling_v2.py` yang dikirim dosen via Classroom. Ini memastikan cost calculation match referensi dosen.

Tuning ini menurunkan cost converge ke 5.80 yang stabil sejak gen ~194 sampai gen 600.

### c. Contoh kelas paralel (2 kelas di slot sama, ruangan berbeda)

Dari hasil best solution:
- **Vian** mengajar "Pengantar Teknologi Informasi (PTI) k2" di **Selasa 07:30 sampai 08:19, RK1**
- **Satria** mengajar "Praktikum Elektronika Dasar k1" di **Selasa 07:30 sampai 08:19, LAB**

Dosen berbeda, ruangan berbeda, slot identik -> kelas paralel valid. GA secara natural menemukan pola paralel karena k1/k2 duaduanya harus qualified untuk dosen yang sama atau berbeda (co-teach case), dan slot+room constraint mendorong assignment paralel di lokasi berbeda.

### d. Apakah distribusi SKS sudah adil?

Hampir. Range 11 sampai 13 SKS untuk ideal 11.8 SKS, deviasi max 1.2 SKS. Variance (sum of squared deviations) 4.80 masih positive karena dua dosen (Yurio, Vian) kebagian 13 SKS dan tiga dosen (Yulis, Dana, Satria) kebagian 11 SKS. Ketidaksempurnaan ini muncul karena constraint qualification mengikat banyak MK ke dosen tertentu (misal Bahasa Inggris ke 5 dosen qualified, tapi MK 3 SKS hanya qualified untuk 1 dosen, sulit didistribusi ulang). Untuk variance 0, semua dosen harus kebagian 11.8 SKS (tidak mungkin dengan SKS integer).

### e. Kalau seed diganti, hasil akan sama?

Tidak. GA bersifat stokastik: pilihan parent untuk crossover, lokasi mutasi, dan inisialisasi populasi awal semua bergantung pada random. Seed hanya menjamin **reproducible run-to-run** untuk seed yang sama. Seed berbeda, trajectory evolusi berbeda, best cost bisa bervariasi (kisaran rentang 5.80 sampai 10 dalam eksperimen awal, semua tetap kategori A). Untuk hasil masuk kategori A, GA relatif robust terhadap seed karena constraint structure kaku dan population 300 cukup besar.

---

## 6. Catatan Tambahan

- **Cost 5.80** masuk kategori A (Istimewa). Semua hard constraint 0 violation, variance SKS dalam range acceptable, prac consecutive penalty kecil.
- **Library**: terbatas pada `random`, `deap`, `matplotlib`, `numpy` sesuai soal.
- **Fitness function**: menggunakan class `DosenSchedulingProblem` dari `dosen_scheduling_v2.py` (referensi dosen). Tidak ada constraint yang dilemahkan.
- **Data**: tidak ada perubahan pada `data_semester_1_3.py` (original dari dosen).
- **Plot**: `plot_konvergensi.jpg` 1500x900 px, warna biru (best) + merah putus-putus (avg), sesuai contoh di soal.
