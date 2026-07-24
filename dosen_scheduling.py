"""
Dosen Scheduling: Chromosome, Fitness, Genetic Operators
=========================================================

Problem: jadwalkan 32 mata kuliah (20 Sem1 + 12 Sem3) ke
5 dosen, 40 time slots, 3 ruangan (RK1, RK2, LAB).

Chromosome: list of 32 tuples:
    [(dosen_id, slot_id, room_id), ...]
    index ke-i  -> mk_instances[i]

Room_id dikodekan: 0 = RK1, 1 = RK2, 2 = LAB
(dipetakan kembali saat display).

Hard constraints (penalty 10 per violation):
  1. Dosen qualified untuk MK
  2. k1 == k2 untuk non-co-teach pair
  3. Dosen tidak mengajar 2 kelas di slot sama
  4. Room type match (teori -> RK1/RK2; praktek -> LAB)
  5. Tidak ada 2 kelas di (slot, room) sama

Soft constraints:
  6. SKS variance antar dosen (weight 1)
  7. Practicum consecutive slot (weight 0.5 per occurrence)

Library: random, numpy, deap (untuk GA framework).
"""

import random
from collections import defaultdict

from data_semester_1_3 import (
    dosen_data,
    time_slots,
    mk_instances,
    mk_groups,
)


# ===== Konstanta =====
ROOM_ID_MAP = {0: "RK1", 1: "RK2", 2: "LAB"}
ROOM_TYPE_OK = {
    "teori": {0, 1},        # RK1 atau RK2
    "praktek": {2},         # LAB
}
NUM_MK = len(mk_instances)              # 32
NUM_DOSEN = len(dosen_data)             # 5
NUM_SLOTS = len(time_slots)             # 40
NUM_ROOMS = 3

DOSEN_NAME = {d["id"]: d["name"] for d in dosen_data.values()}
NAME_TO_ID = {d["name"]: d["id"] for d in dosen_data.values()}


# ===== Indeks bantu =====
# Map nama MK -> [mk_instance_ids] (untuk constraint k1=k2)
MK_PAIR_INDEX = {}
for g in mk_groups:
    MK_PAIR_INDEX[g["mk_name"]] = (g["instances"], g["is_co_teach"])

# Map mk_id -> mk dict
MK_BY_ID = {m["id"]: m for m in mk_instances}

# Slot -> hari
SLOT_HARI = {s["id"]: s["hari"] for s in time_slots}


# ===== Random builder (init) =====
def random_gene(mk):
    """Satu gen = (dosen_id, slot_id, room_id) untuk satu MK."""
    qualified_ids = [NAME_TO_ID[n] for n in mk["dosen_qualified"]]
    dosen_id = random.choice(qualified_ids)
    slot_id = random.randrange(NUM_SLOTS)
    if mk["type"] == "praktek":
        room_id = 2  # LAB
    else:
        room_id = random.choice([0, 1])  # RK1 / RK2
    return (dosen_id, slot_id, room_id)


def random_individual():
    """Satu individu = list of 32 gen."""
    return [random_gene(mk) for mk in mk_instances]


# ===== Custom genetic operators (tuple-safe) =====
def crossover_tuples(ind1, ind2):
    """One-point crossover pada list of 32 tuple."""
    size = len(ind1)
    cxpoint = random.randrange(1, size)
    ind1[cxpoint:], ind2[cxpoint:] = ind2[cxpoint:], ind1[cxpoint:]
    return ind1, ind2


def mutate_tuples(individual, indpb=0.05):
    """
    Mutasi per-gen: kalau random < indpb, replace satu field
    secara acak (field yang dipilih juga random).

    Hanya ganti field yang legal:
      - dosen_id: dari qualified list MK tsb
      - slot_id: 0..39
      - room_id: sesuai type (praktek -> 2; teori -> 0/1)
    """
    for i in range(len(individual)):
        if random.random() < indpb:
            mk = MK_BY_ID[i]
            field = random.randrange(3)
            d, s, r = individual[i]
            if field == 0:
                qualified_ids = [NAME_TO_ID[n] for n in mk["dosen_qualified"]]
                d = random.choice(qualified_ids)
            elif field == 1:
                s = random.randrange(NUM_SLOTS)
            else:
                if mk["type"] == "praktek":
                    r = 2
                else:
                    r = random.choice([0, 1])
            individual[i] = (d, s, r)
    return individual,


# ===== Fitness =====
def getCost(individual):
    """
    Hitung total cost. Lebih kecil = lebih baik.
    Hard: +10 per violation.
    Soft: +1 * variance_sks; +0.5 per prac non-consecutive.
    """
    cost = 0.0

    # ----- Hard 1: qualification -----
    for i, (d, s, r) in enumerate(individual):
        mk = MK_BY_ID[i]
        if DOSEN_NAME[d] not in mk["dosen_qualified"]:
            cost += 10

    # ----- Hard 2: k1 == k2 (non-co-teach) -----
    for mk_name, (ids, is_cotech) in MK_PAIR_INDEX.items():
        if is_cotech:
            continue
        if len(ids) < 2:
            continue
        # ambil dosen untuk tiap instance di group
        dosens = {individual[i][0] for i in ids}
        if len(dosens) > 1:
            cost += 10

    # ----- Hard 3: dosen tidak boleh 2 kelas di slot sama -----
    dosen_slot = defaultdict(set)
    for i, (d, s, r) in enumerate(individual):
        dosen_slot[d].add(s)
    for d, slots in dosen_slot.items():
        # set sudah unik, tapi kalau dosen muncul > 1 di slot identik
        # sebenarnya gak mungkin karena set; pelanggaran di sini
        # hanya kalau satu MK punya 2 entries = tidak terjadi.
        # Kita count MK yang dosennya bentrok:
        pass
    # Implementasi yang benar: ukur berapa (dosen, slot) muncul >1
    pair_count = defaultdict(int)
    for i, (d, s, r) in enumerate(individual):
        pair_count[(d, s)] += 1
    for c in pair_count.values():
        if c > 1:
            cost += 10 * (c - 1)

    # ----- Hard 4: room type match -----
    for i, (d, s, r) in enumerate(individual):
        mk = MK_BY_ID[i]
        if r not in ROOM_TYPE_OK[mk["type"]]:
            cost += 10

    # ----- Hard 5: tidak ada 2 kelas di (slot, room) sama -----
    slot_room_count = defaultdict(int)
    for i, (d, s, r) in enumerate(individual):
        slot_room_count[(s, r)] += 1
    for c in slot_room_count.values():
        if c > 1:
            cost += 10 * (c - 1)

    # ----- Soft 6: SKS variance -----
    sks_per_dosen = [0] * NUM_DOSEN
    for i, (d, s, r) in enumerate(individual):
        sks_per_dosen[d] += MK_BY_ID[i]["sks"]
    mean_sks = sum(sks_per_dosen) / NUM_DOSEN
    variance = sum((x - mean_sks) ** 2 for x in sks_per_dosen) / NUM_DOSEN
    cost += 1.0 * variance

    # ----- Soft 7: practicum consecutive (hari sama, slot adjacent) -----
    # Kumpulkan slot prac per dosen, diurutkan
    prac_slots = defaultdict(list)
    for i, (d, s, r) in enumerate(individual):
        mk = MK_BY_ID[i]
        if mk["type"] == "praktek":
            prac_slots[d].append(s)
    non_consecutive = 0
    for d, slots in prac_slots.items():
        if len(slots) < 2:
            continue
        slots_sorted = sorted(slots)
        for a, b in zip(slots_sorted, slots_sorted[1:]):
            # consecutive kalau hari sama DAN slot_id b = a + 1
            if not (SLOT_HARI[a] == SLOT_HARI[b] and b == a + 1):
                non_consecutive += 1
    cost += 0.5 * non_consecutive

    return (cost,)


# ===== Utility: parsing balik ke text =====
def decode_individual(individual):
    """Convert chromosome ke list of dict siap print."""
    out = []
    for i, (d, s, r) in enumerate(individual):
        mk = MK_BY_ID[i]
        slot = time_slots[s]
        out.append({
            "mk_id": i,
            "mk_name": mk["name"],
            "kelas": mk["kelas"],
            "semester": mk["semester"],
            "type": mk["type"],
            "sks": mk["sks"],
            "dosen_id": d,
            "dosen_name": DOSEN_NAME[d],
            "slot_id": s,
            "hari": slot["hari"],
            "jam": slot["jam"],
            "room": ROOM_ID_MAP[r],
        })
    return out


# ===== Sanity check =====
if __name__ == "__main__":
    random.seed(0)
    ind = random_individual()
    print("Individual (first 4):", ind[:4])
    print("Cost:", getCost(ind))
