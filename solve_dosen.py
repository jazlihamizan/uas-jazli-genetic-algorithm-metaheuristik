"""
Dosen Scheduling: GA Solver
============================

Run: python solve_dosen.py

Output:
  - Progress per generasi
  - Best solution + analisis
  - plot_konvergensi.jpg
"""

import random
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")  # no display
import matplotlib.pyplot as plt

from deap import base, creator, tools

from data_semester_1_3 import (
    dosen_data,
    time_slots,
    mk_instances,
)
from dosen_scheduling import (
    random_individual,
    crossover_tuples,
    mutate_tuples,
    getCost,
    decode_individual,
    NUM_MK,
    NUM_DOSEN,
    DOSEN_NAME,
    MK_BY_ID,
    ROOM_ID_MAP,
    ROOM_TYPE_OK,
    SLOT_HARI,
)


# ===== Seed (REPRODUCIBLE) =====
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ===== GA Parameters =====
POPULATION_SIZE = 300
MAX_GENERATIONS = 600
P_CROSSOVER = 0.9
P_MUTATION = 0.2
MUTATION_INDPB = 0.05     # per-gen indpb (di dalam mutate_tuples)
TOURNAMENT_SIZE = 3
ELITE_SIZE = 5


# ===== DEAP setup =====
# We minimize cost, so weight = -1.0
if not hasattr(creator, "FitMin"):
    creator.create("FitMin", base.Fitness, weights=(-1.0,))
if not hasattr(creator, "Individual"):
    creator.create("Individual", list, fitness=creator.FitMin)

toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, random_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", getCost)
toolbox.register("select", tools.selTournament, tournsize=TOURNAMENT_SIZE)
toolbox.register("mate", crossover_tuples)
toolbox.register("mutate", mutate_tuples, indpb=MUTATION_INDPB)


def run_ga():
    """Main GA loop. Returns logbook + best individual."""
    pop = toolbox.population(n=POPULATION_SIZE)

    # Evaluate initial population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    # Stats
    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("avg", lambda fits: float(np.mean(fits)))
    stats.register("std", lambda fits: float(np.std(fits)))
    stats.register("min", lambda fits: float(np.min(fits)))
    stats.register("max", lambda fits: float(np.max(fits)))

    logbook = tools.Logbook()
    logbook.header = ["gen", "nevals", "avg", "std", "min", "max"]

    # Initial record
    record = stats.compile(pop)
    logbook.record(gen=0, nevals=len(pop), **record)
    print(logbook.stream)

    best = tools.selBest(pop, k=1)[0]

    for gen in range(1, MAX_GENERATIONS + 1):
        # Elitism: keep top ELITE_SIZE unchanged
        elites = tools.selBest(pop, k=ELITE_SIZE)
        elites = [toolbox.clone(e) for e in elites]

        # Select next gen (excluding elites, we'll add them back)
        offspring = toolbox.select(pop, len(pop) - ELITE_SIZE)
        offspring = [toolbox.clone(o) for o in offspring]

        # Crossover
        for c1, c2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < P_CROSSOVER:
                toolbox.mate(c1, c2)
                del c1.fitness.values
                del c2.fitness.values

        # Mutation
        for m in offspring:
            if random.random() < P_MUTATION:
                toolbox.mutate(m)
                del m.fitness.values

        # Evaluate invalid offspring
        invalid = [i for i in offspring if not i.fitness.valid]
        fitnesses = list(map(toolbox.evaluate, invalid))
        for ind, fit in zip(invalid, fitnesses):
            ind.fitness.values = fit

        # Reassemble: elites + offspring
        pop = elites + offspring

        # Update best
        best = tools.selBest(pop, k=1)[0]

        # Log
        record = stats.compile(pop)
        logbook.record(gen=gen, nevals=len(invalid), **record)
        print(logbook.stream)

    return logbook, best


def plot_convergence(logbook, path="plot_konvergensi.jpg"):
    """Best (min) + average fitness per generation."""
    gen = logbook.select("gen")
    mn = logbook.select("min")
    avg = logbook.select("avg")

    plt.figure(figsize=(10, 6))
    plt.plot(gen, mn, "b-", linewidth=2, label="Best Fitness")
    plt.plot(gen, avg, "r--", linewidth=1.5, label="Average Fitness")
    plt.xlabel("Generation")
    plt.ylabel("Cost")
    plt.title("Konvergensi GA: Dosen Scheduling")
    plt.legend(loc="upper right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150, format="jpg")
    plt.close()
    print(f"\nPlot saved to: {path}")


def analyze(best):
    """Print structured analysis of best solution."""
    decoded = decode_individual(best)
    cost = best.fitness.values[0]
    print("\n" + "=" * 80)
    print("SOLUTION ANALYSIS - DOSEN SCHEDULING")
    print("=" * 80)

    # Group by dosen
    by_dosen = {}
    for entry in decoded:
        by_dosen.setdefault(entry["dosen_name"], []).append(entry)

    print("\n1. ASSIGNMENT PER DOSEN:")
    for did in range(NUM_DOSEN):
        name = DOSEN_NAME[did]
        entries = sorted(by_dosen.get(name, []), key=lambda e: (e["hari"], e["slot_id"]))
        total_sks = sum(e["sks"] for e in entries)
        print(f"\n  [{did}] {name}: {len(entries)} MK, {total_sks} SKS")
        for e in entries:
            print(f"      {e['mk_name']} ({e['kelas']}) | {e['hari']} {e['jam']} | "
                  f"{e['room']} | {e['sks']} SKS")

    # Room utilization
    print("\n2. RUANGAN UTILIZATION:")
    sr_count = {}
    for e in decoded:
        sr_count[(e["slot_id"], e["room"])] = sr_count.get((e["slot_id"], e["room"]), 0) + 1
    max_overlap = max(sr_count.values())
    if max_overlap <= 1:
        print("  OK No room conflicts (each slot+room has <=1 class)")
    else:
        conflicts = [k for k, v in sr_count.items() if v > 1]
        print(f"  X {len(conflicts)} conflict(s):")
        for k in conflicts[:5]:
            print(f"      {k}: {sr_count[k]} classes")

    # Workload
    sks_per_dosen = [0] * NUM_DOSEN
    for e in decoded:
        sks_per_dosen[e["dosen_id"]] += e["sks"]
    total = sum(sks_per_dosen)
    ideal = total / NUM_DOSEN
    print("\n3. WORKLOAD SUMMARY:")
    print(f"  Total SKS: {total}")
    print(f"  Ideal per dosen: {ideal:.1f}")
    print(f"  Actual range: {min(sks_per_dosen)}-{max(sks_per_dosen)} SKS")
    mean = sum(sks_per_dosen) / NUM_DOSEN
    variance = sum((x - mean) ** 2 for x in sks_per_dosen) / NUM_DOSEN
    print(f"  Workload variance: {variance:.2f}")

    # Hard constraint violations
    print("\n4. CONSTRAINT VIOLATIONS:")
    # 1. qualification
    qual_viol = 0
    for e in decoded:
        if e["dosen_name"] not in MK_BY_ID[e["mk_id"]]["dosen_qualified"]:
            qual_viol += 1
    print(f"  {'OK' if qual_viol == 0 else 'X'} Qualification: {qual_viol} violation(s)")

    # 2. k1=k2 non-cotech
    from data_semester_1_3 import mk_groups
    k1k2_viol = 0
    for g in mk_groups:
        if g["is_co_teach"]:
            continue
        names = set()
        for i in g["instances"]:
            names.add(decoded[i]["dosen_name"])
        if len(names) > 1:
            k1k2_viol += 1
    print(f"  {'OK' if k1k2_viol == 0 else 'X'} k1=k2 (non-cotech): {k1k2_viol} violation(s)")

    # 3. dosen conflict
    pair_count = {}
    for e in decoded:
        key = (e["dosen_name"], e["slot_id"])
        pair_count[key] = pair_count.get(key, 0) + 1
    dosen_viol = sum(c - 1 for c in pair_count.values() if c > 1)
    print(f"  {'OK' if dosen_viol == 0 else 'X'} Dosen timing conflict: {dosen_viol} violation(s)")

    # 4. room type
    rt_viol = 0
    for e in decoded:
        mk = MK_BY_ID[e["mk_id"]]
        room_id = {"RK1": 0, "RK2": 1, "LAB": 2}[e["room"]]
        if room_id not in ROOM_TYPE_OK[mk["type"]]:
            rt_viol += 1
    print(f"  {'OK' if rt_viol == 0 else 'X'} Room-type match: {rt_viol} violation(s)")

    # 5. room overlap
    ro_viol = max(0, max_overlap - 1) if max_overlap > 1 else 0
    print(f"  {'OK' if ro_viol == 0 else 'X'} Room overlap: {ro_viol} violation(s)")

    print("\n" + "=" * 80)
    print(f"FINAL COST: {cost:.2f}")
    print("=" * 80)


def main():
    print("=" * 80)
    print("DOSEN SCHEDULING - GENETIC ALGORITHM")
    print("=" * 80)
    print(f"\nProblem Size:")
    print(f"  - MK Instances: {NUM_MK}")
    print(f"  - Dosen: {NUM_DOSEN}")
    print(f"  - Time Slots: {len(time_slots)}")
    print(f"  - Population Size: {POPULATION_SIZE}")
    print(f"  - Generations: {MAX_GENERATIONS}")
    print(f"  - Random Seed: {RANDOM_SEED}")
    print("\nRunning GA...\n" + "-" * 80)

    t0 = time.time()
    logbook, best = run_ga()
    elapsed = time.time() - t0

    print("-" * 80)
    print(f"\nGA Finished in {elapsed:.1f}s")
    print(f"Best Cost Found: {best.fitness.values[0]:.2f}")

    analyze(best)
    plot_convergence(logbook)


if __name__ == "__main__":
    main()
