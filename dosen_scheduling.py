"""
Dosen Scheduling Problem v2 - FULL SCHEDULING (dosen + slot + room)
Assign 32 MK instances ke (dosen, slot, ruangan) tuples

INDIVIDUAL REPRESENTATION (NEW!):
  individual[i] = (dosen_id, slot_id, room_id) for MK instance i
  
  Length: 32 tuples
  dosen_id: 0-4 (5 dosen)
  slot_id: 0-39 (40 time slots)
  room_id: 0=RK1, 1=RK2, 2=LAB
  
EXAMPLE:
  individual[0] = (0, 5, 0)  → MK 0 (Intro AI k1): Yulis, Slot 5, RK1
  individual[10] = (0, 8, 1) → MK 10 (Intro AI k2): Yulis, Slot 8, RK2
                                (PARALLEL! Same slot, different room)

CONSTRAINTS:
  HARD (penalty=10):
  1. Qualification: dosen must be qualified for MK type
  2. k1=k2 sama dosen: non-cotech only
  3. Dosen timing: dosen can't teach 2 classes same slot
  4. Room-type match: teori→RK1/RK2, praktek→LAB
  5. Room overlap: no 2 classes same (slot, room)
  
  SOFT (penalty=1):
  1. Workload balance: SKS variance minimize
  2. Praktikum consecutive: prefer consecutive slots for 100-min classes
"""

class DosenSchedulingProblem:
    
    ROOM_ID = {"RK1": 0, "RK2": 1, "LAB": 2}
    ROOM_NAME = {0: "RK1", 1: "RK2", 2: "LAB"}
    
    def __init__(self, mk_instances, dosen_data, time_slots, mk_groups,
                 hard_constraint_penalty=10, soft_constraint_penalty=1):
        """
        Args:
            mk_instances: list of MK dicts
            dosen_data: dict {dosen_id: {name, id}}
            time_slots: list of slot dicts {id, hari, jam, room}
            mk_groups: list of MK groups for k1=k2 tracking
            hard_constraint_penalty: penalty per hard violation
            soft_constraint_penalty: penalty per soft violation unit
        """
        self.mk_instances = mk_instances
        self.dosen_data = dosen_data
        self.time_slots = time_slots
        self.mk_groups = mk_groups
        self.hard_constraint_penalty = hard_constraint_penalty
        self.soft_constraint_penalty = soft_constraint_penalty
        
        # Reverse mapping
        self.dosen_name_to_id = {v["name"]: v["id"] for k, v in dosen_data.items()}
        
        # Build room slots mapping
        self.room_slots = {0: [], 1: [], 2: []}  # room_id → list of slot_ids
        for slot in time_slots:
            room_id = self.ROOM_ID.get(slot["room"], 0)
            self.room_slots[room_id].append(slot["id"])
    
    def __len__(self):
        """Return jumlah MK instances"""
        return len(self.mk_instances)
    
    def getCost(self, individual):
        """
        Evaluate individual = list of (dosen_id, slot_id, room_id) tuples
        
        Args:
            individual: list of 32 tuples, one per MK instance
            
        Returns:
            cost (int): total hard + soft violations
        """
        hard_violations = 0
        soft_violations = 0
        
        # Unpack individual for easier access
        assignments = individual  # [(dosen_id, slot_id, room_id), ...]
        
        # ===== HARD CONSTRAINT 1: Qualification =====
        for mk_id, (dosen_id, slot_id, room_id) in enumerate(assignments):
            mk = self.mk_instances[mk_id]
            
            if dosen_id not in self.dosen_data:
                hard_violations += 1
                continue
            
            dosen_name = self.dosen_data[dosen_id]["name"]
            
            # Check qualification
            if dosen_name not in mk["dosen_qualified"]:
                hard_violations += 1
        
        # ===== HARD CONSTRAINT 2: k1 & k2 sama dosen (non-cotech) =====
        for group in self.mk_groups:
            if not group["is_co_teach"]:
                inst_ids = group["instances"]
                dosen_ids = [assignments[idx][0] for idx in inst_ids]
                
                if len(set(dosen_ids)) > 1:
                    hard_violations += 2
        
        # ===== HARD CONSTRAINT 3: Dosen timing conflict =====
        # Dosen tidak boleh teach 2 classes same slot (regardless of room)
        dosen_slot_count = {}  # (dosen_id, slot_id) → count
        for mk_id, (dosen_id, slot_id, room_id) in enumerate(assignments):
            key = (dosen_id, slot_id)
            dosen_slot_count[key] = dosen_slot_count.get(key, 0) + 1
            
            if dosen_slot_count[key] > 1:
                hard_violations += 2  # Dosen conflict!
        
        # ===== HARD CONSTRAINT 4: Room-type match =====
        # Teori → RK1/RK2 only, Praktek → LAB only
        for mk_id, (dosen_id, slot_id, room_id) in enumerate(assignments):
            mk = self.mk_instances[mk_id]
            
            if mk["type"] == "teori":
                # Teori must be in RK1 or RK2
                if room_id == 2:  # LAB
                    hard_violations += 2
            else:  # praktek
                # Praktek must be in LAB
                if room_id != 2:
                    hard_violations += 2
        
        # ===== HARD CONSTRAINT 5: Room overlap =====
        # No 2 classes same (slot, room)
        room_slot_assignment = {}  # (slot_id, room_id) → mk_ids
        for mk_id, (dosen_id, slot_id, room_id) in enumerate(assignments):
            key = (slot_id, room_id)
            
            if key not in room_slot_assignment:
                room_slot_assignment[key] = []
            
            if len(room_slot_assignment[key]) > 0:
                hard_violations += 2  # Room conflict!
            
            room_slot_assignment[key].append(mk_id)
        
        # ===== SOFT CONSTRAINT 1: Workload balance =====
        dosen_workload = {}
        for mk_id, (dosen_id, slot_id, room_id) in enumerate(assignments):
            mk = self.mk_instances[mk_id]
            if dosen_id not in dosen_workload:
                dosen_workload[dosen_id] = 0
            dosen_workload[dosen_id] += mk["sks"]
        
        if dosen_workload and len(self.dosen_data) > 0:
            total_sks = sum(dosen_workload.values())
            avg_sks = total_sks / len(self.dosen_data)
            workload_variance = sum((w - avg_sks) ** 2 for w in dosen_workload.values())
            soft_violations += workload_variance
        
        # ===== SOFT CONSTRAINT 2: Praktikum consecutive slots =====
        # For praktek MK using slot i, prefer slot i+1 also used
        # (only if there's another praktek assigned to i+1)
        praktek_slots = {}  # slot_id → list of mk_ids (praktek only)
        for mk_id, (dosen_id, slot_id, room_id) in enumerate(assignments):
            mk = self.mk_instances[mk_id]
            if mk["type"] == "praktek":
                if slot_id not in praktek_slots:
                    praktek_slots[slot_id] = []
                praktek_slots[slot_id].append(mk_id)
        
        # Check for non-consecutive praktek (soft penalty)
        non_consecutive_count = 0
        for slot_id, mk_list in praktek_slots.items():
            # If there's praktek at slot i, check if another at i+1
            if slot_id + 1 < len(self.time_slots):
                if slot_id + 1 not in praktek_slots or \
                   any(assignments[mk][2] != assignments[mk_id][2] for mk in mk_list for mk_id in praktek_slots.get(slot_id + 1, [])):
                    # Different dosen/room, not consecutive practical pair
                    non_consecutive_count += 1
        
        soft_violations += non_consecutive_count * 0.5  # Small penalty
        
        # ===== TOTAL COST =====
        cost = (self.hard_constraint_penalty * hard_violations + 
                self.soft_constraint_penalty * soft_violations)
        
        return cost


# ===== HELPER FUNCTIONS =====

def analyze_solution(individual, mk_instances, dosen_data, time_slots, mk_groups):
    """
    Print detailed analysis of solution
    
    Args:
        individual: list of (dosen_id, slot_id, room_id) tuples
        mk_instances: list of MK data
        dosen_data: dict of dosen
        time_slots: list of time slots
        mk_groups: list of MK groups
    """
    ROOM_NAME = {0: "RK1", 1: "RK2", 2: "LAB"}
    
    print("\n" + "="*90)
    print("SOLUTION ANALYSIS - DOSEN SCHEDULING (Full Slot Assignment)")
    print("="*90)
    
    # Parse assignments
    assignments = individual
    
    # 1. Assignment summary per dosen
    print("\n1. ASSIGNMENT PER DOSEN:")
    dosen_mk_map = {i: [] for i in range(len(dosen_data))}
    
    for mk_id, (dosen_id, slot_id, room_id) in enumerate(assignments):
        mk = mk_instances[mk_id]
        slot = time_slots[slot_id] if slot_id < len(time_slots) else None
        room_name = ROOM_NAME.get(room_id, "?")
        
        dosen_mk_map[dosen_id].append({
            "mk_name": mk["name"],
            "kelas": mk["kelas"],
            "sks": mk["sks"],
            "type": mk["type"],
            "slot": f"{slot['hari']} {slot['jam']}" if slot else "?",
            "room": room_name
        })
    
    for dosen_id in range(len(dosen_data)):
        mk_list = dosen_mk_map[dosen_id]
        if not mk_list:
            continue
        
        dosen_name = dosen_data[dosen_id]["name"]
        total_sks = sum(mk["sks"] for mk in mk_list)
        
        print(f"\n  [{dosen_id}] {dosen_name}: {len(mk_list)} MK, {total_sks} SKS")
        for mk in mk_list:
            print(f"      {mk['mk_name']:40} ({mk['kelas']:2}) | "
                  f"{mk['slot']:25} | {mk['room']:3} | {mk['sks']} SKS")
    
    # 2. Ruangan utilization
    print("\n2. RUANGAN UTILIZATION:")
    room_slot_usage = {}  # (slot_id, room_id) → count
    for mk_id, (dosen_id, slot_id, room_id) in enumerate(assignments):
        key = (slot_id, room_id)
        room_slot_usage[key] = room_slot_usage.get(key, 0) + 1
    
    conflicts = 0
    for (slot_id, room_id), count in room_slot_usage.items():
        if count > 1:
            conflicts += 1
            room_name = ROOM_NAME.get(room_id, "?")
            slot = time_slots[slot_id] if slot_id < len(time_slots) else None
            print(f"  ⚠️ CONFLICT: {room_name} @ {slot['hari']} {slot['jam']} has {count} classes")
    
    if conflicts == 0:
        print(f"  ✅ No room conflicts (each slot+room has ≤1 class)")
    
    # 3. Workload summary
    print("\n3. WORKLOAD SUMMARY:")
    workloads = []
    for dosen_id in range(len(dosen_data)):
        sks = sum(mk["sks"] for mk in dosen_mk_map[dosen_id])
        workloads.append(sks)
    
    total_sks = sum(workloads)
    avg_sks = total_sks / len(dosen_data) if dosen_data else 0
    variance = sum((w - avg_sks) ** 2 for w in workloads) if workloads else 0
    
    print(f"  Total SKS: {total_sks}")
    print(f"  Ideal per dosen: {avg_sks:.1f}")
    print(f"  Actual range: {min(workloads)}-{max(workloads)} SKS")
    print(f"  Workload variance: {variance:.2f}")
    
    # 4. Parallel classes (same slot, different room)
    print("\n4. PARALLEL CLASSES (same slot, different room):")
    parallel_count = 0
    slot_assignments = {}  # slot_id → [(mk_name, room, dosen), ...]
    
    for mk_id, (dosen_id, slot_id, room_id) in enumerate(assignments):
        mk = mk_instances[mk_id]
        room_name = ROOM_NAME.get(room_id, "?")
        dosen_name = dosen_data[dosen_id]["name"]
        
        if slot_id not in slot_assignments:
            slot_assignments[slot_id] = []
        slot_assignments[slot_id].append((mk["name"], room_name, dosen_name))
    
    for slot_id, items in sorted(slot_assignments.items()):
        if len(items) > 1:
            parallel_count += 1
            slot = time_slots[slot_id]
            print(f"  Slot {slot['hari']:5} {slot['jam']:15}:")
            for mk_name, room, dosen in items:
                print(f"    - {mk_name:40} @ {room} ({dosen})")
    
    if parallel_count == 0:
        print(f"  (No parallel classes)")
    else:
        print(f"  Total: {parallel_count} slots with parallel classes ✅ Running efficiently!")
    
    # 5. Constraint violations
    print("\n5. CONSTRAINT VIOLATIONS:")
    
    # Qualification
    qual_violations = 0
    for mk_id, (dosen_id, slot_id, room_id) in enumerate(assignments):
        mk = mk_instances[mk_id]
        dosen_name = dosen_data[dosen_id]["name"]
        if dosen_name not in mk["dosen_qualified"]:
            qual_violations += 1
            print(f"  ❌ Qualification: {mk['name']} ({mk['kelas']}) → {dosen_name} NOT qualified")
    
    if qual_violations == 0:
        print(f"  ✅ Qualification: OK")
    
    # k1 & k2
    k12_violations = 0
    for group in mk_groups:
        if not group["is_co_teach"]:
            inst_ids = group["instances"]
            dosen_ids = [assignments[idx][0] for idx in inst_ids]
            if len(set(dosen_ids)) > 1:
                k12_violations += 1
                print(f"  ❌ k1=k2: {group['mk_name']} → different dosen")
    
    if k12_violations == 0:
        print(f"  ✅ k1=k2 (non-cotech): OK")
    
    print("\n" + "="*90)
