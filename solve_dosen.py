"""
Dosen Scheduling - GA Solver
============================

Run: python solve_dosen.py

Library: random, numpy, deap, matplotlib (sesuai soal)
Fitness: DosenSchedulingProblem.getCost dari dosen_scheduling.py (reference v2)

Output:
  - Progress per generasi
  - Best solution + analisis
  - plot_konvergensi.jpg
"""

import random
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from deap import base, creator, tools

from data_semester_1_3 import (
    dosen_data,
    time_slots,
    mk_instances,
    mk_groups,
)
from dosen_scheduling import (
    DosenSchedulingProblem,
    analyze_solution,
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
MUTATION_INDPB = 0.05
TOURNAMENT_SIZE = 3
ELITE_SIZE = 5


# ===== Init problem =====
problem = DosenSchedulingProblem(
    mk_instances, dosen_data, time_slots, mk_groups,
    hard_constraint_penalty=10,
    soft_constraint_penalty=1,
)
NUM_MK = len(mk_instances)
NUM_DOSEN = len(dosen_data)
NUM_SLOTS = len(time_slots)

# Slot -> room id mapping (for valid room assignment)
SLOT_ROOM_ID = {}
for s in time_slots:
    room_name = s["room"]
    room_id = problem.ROOM_ID.get(room_name, 0)
    SLOT_ROOM_ID[s["id"]] = room_id

# Slot -> hari
SLOT_HARI = {s["id"]: s["hari"] for s in time_slots}


# ===== Random builder =====
def random_gene(mk):
    """Satu gen = (dosen_id, slot_id, room_id) untuk satu MK."""
    qualified_names = mk["dosen_qualified"]
    qualified_ids = [did for did, d in dosen_data.items() if d["name"] in qualified_names]
    dosen_id = random.choice(qualified_ids)
    slot_id = random.randrange(NUM_SLOTS)
    if mk["type"] == "praktek":
        room_id = 2  # LAB
    else:
        # teori: pilih RK1 atau RK2 (room_id 0 atau 1)
        room_id = random.choice([0, 1])
    return (dosen_id, slot_id, room_id)


def random_individual():
    """Satu individu = list of 32 gen."""
    return [random_gene(mk) for mk in mk_instances]


# ===== Custom genetic operators =====
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
    """
    for i in range(len(individual)):
        if random.random() < indpb:
            mk = mk_instances[i]
            field = random.randrange(3)
            d, s, r = individual[i]
            if field == 0:
                qualified_names = mk["dosen_qualified"]
                qualified_ids = [did for did, din in dosen_data.items() if din["name"] in qualified_names]
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


# ===== DEAP setup =====
if not hasattr(creator, "FitMin"):
    creator.create("FitMin", base.Fitness, weights=(-1.0,))
if not hasattr(creator, "Individual"):
    creator.create("Individual", list, fitness=creator.FitMin)

toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, random_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def evaluate(ind):
    """Wrap DosenSchedulingProblem.getCost untuk DEAP (returns tuple)."""
    cost = problem.getCost(ind)
    return (cost,)


toolbox.register("evaluate", evaluate)
toolbox.register("select", tools.selTournament, tournsize=TOURNAMENT_SIZE)
toolbox.register("mate", crossover_tuples)
toolbox.register("mutate", mutate_tuples, indpb=MUTATION_INDPB)


def run_ga():
    """Main GA loop."""
    pop = toolbox.population(n=POPULATION_SIZE)

    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("avg", lambda fits: float(np.mean(fits)))
    stats.register("std", lambda fits: float(np.std(fits)))
    stats.register("min", lambda fits: float(np.min(fits)))
    stats.register("max", lambda fits: float(np.max(fits)))

    logbook = tools.Logbook()
    logbook.header = ["gen", "nevals", "avg", "std", "min", "max"]

    record = stats.compile(pop)
    logbook.record(gen=0, nevals=len(pop), **record)
    print(logbook.stream)

    best = tools.selBest(pop, k=1)[0]

    for gen in range(1, MAX_GENERATIONS + 1):
        elites = tools.selBest(pop, k=ELITE_SIZE)
        elites = [toolbox.clone(e) for e in elites]

        offspring = toolbox.select(pop, len(pop) - ELITE_SIZE)
        offspring = [toolbox.clone(o) for o in offspring]

        for c1, c2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < P_CROSSOVER:
                toolbox.mate(c1, c2)
                del c1.fitness.values
                del c2.fitness.values

        for m in offspring:
            if random.random() < P_MUTATION:
                toolbox.mutate(m)
                del m.fitness.values

        invalid = [i for i in offspring if not i.fitness.valid]
        fitnesses = list(map(toolbox.evaluate, invalid))
        for ind, fit in zip(invalid, fitnesses):
            ind.fitness.values = fit

        pop = elites + offspring

        best = tools.selBest(pop, k=1)[0]

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
    plt.title("Konvergensi GA - Dosen Scheduling")
    plt.legend(loc="upper right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150, format="jpg")
    plt.close()
    print(f"\nPlot saved to: {path}")


def main():
    print("=" * 80)
    print("DOSEN SCHEDULING - GENETIC ALGORITHM")
    print("=" * 80)
    print(f"\nProblem Size:")
    print(f"  - MK Instances: {NUM_MK}")
    print(f"  - Dosen: {NUM_DOSEN}")
    print(f"  - Time Slots: {NUM_SLOTS}")
    print(f"  - Population Size: {POPULATION_SIZE}")
    print(f"  - Generations: {MAX_GENERATIONS}")
    print(f"  - Random Seed: {RANDOM_SEED}")
    print("\nRunning GA...\n" + "-" * 80)

    t0 = time.time()
    logbook, best = run_ga()
    elapsed = time.time() - t0

    print("-" * 80)
    print(f"\nGA Finished in {elapsed:.1f}s")
    print(f"Best Cost Found: {problem.getCost(best):.2f}")

    analyze_solution(best, mk_instances, dosen_data, time_slots, mk_groups)
    plot_convergence(logbook)

    print(f"\n===== FINAL COST: {problem.getCost(best):.2f} =====")
    print("=" * 80)


if __name__ == "__main__":
    main()
