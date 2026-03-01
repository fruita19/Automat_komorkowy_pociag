import pygame
import math
from typing import List, Dict, Optional


class Cell:
    def __init__(self, cid, cell_type, next_cells, train_id, signal):
        self.cid = cid
        self.cell_type = cell_type
        self.next_cells = next_cells
        self.train_id = train_id
        self.signal = signal
        self.selected_route = 0


class Train:
    def __init__(self, tid, cells, dwell_remaining, waiting_ticks):
        self.tid = tid
        self.cells = list(cells)
        self.dwell_remaining = dwell_remaining
        self.waiting_ticks = waiting_ticks


class World:
    def __init__(self, cells, trains, params, tick=0):
        self.cells = cells
        self.trains = trains
        self.params = params
        self.tick = tick

    @staticmethod
    def build_world():
        cells = []
        trains = []

        params = {"dwell_time": 10}
        params["station_platform"] = {}
        params["station_entry_cell"] = {}
        params["station_nodes"] = {}
        params["station_entry_index"] = {}
        params["rings"] = {}
        params["transfer_switches"] = set()

        RING_N = 24

        def make_ring(n):
            ring = []
            for _ in range(n):
                cid = len(cells)
                cells.append(Cell(cid, "TRACK", [], None, True))
                ring.append(cid)
            for i in range(n):
                cells[ring[i]].next_cells = [ring[(i + 1) % n]]
            return ring

        rings = {
            "BLACK": make_ring(RING_N),
            "ORANGE": make_ring(RING_N),
            "GREEN": make_ring(RING_N),
        }
        params["rings"] = rings

        order = ["BLACK", "ORANGE", "GREEN"]
        for i, name in enumerate(order):
            if i == len(order) - 1: break 
            nxt = order[i + 1]
            conn = rings[name][0] 
            stay = rings[name][1]
            go = rings[nxt][RING_N // 2] 
            cells[conn].cell_type = "SWITCH"
            cells[conn].next_cells = [stay, go]
            params["transfer_switches"].add(conn)

        def add_station(name, entry_index):
            ring = rings[name]
            entry = ring[entry_index]
            dalej = cells[entry].next_cells[0]

            sw = len(cells)
            cells.append(Cell(sw, "SWITCH", [], None, True))
            spur = len(cells)
            cells.append(Cell(spur, "TRACK", [], None, True))
            platform = len(cells)
            cells.append(Cell(platform, "PLATFORM", [], None, True))

            cells[entry].next_cells = [sw]
            cells[sw].next_cells = [dalej, spur]
            cells[spur].next_cells = [platform]
            cells[platform].next_cells = [dalej]

            params["station_platform"][name] = platform
            params["station_entry_cell"][name] = entry
            params["station_nodes"][name] = {
                "entry": entry, "sw": sw, "spur": spur, "platform": platform
            }
            params["station_entry_index"][name] = entry_index

        add_station("BLACK", 6)
        add_station("ORANGE", 6)
        add_station("GREEN", 6)
        def place_train(tid, ring_name, head_index):
            ring = rings[ring_name]
            ids = [
                ring[head_index % RING_N],
                ring[(head_index - 1) % RING_N],
                ring[(head_index - 2) % RING_N],
            ]
            t = Train(tid, ids, 0, 0)
            trains.append(t)
            for cid in ids:
                cells[cid].train_id = tid

        place_train(1, "BLACK", 3)
        place_train(3, "GREEN", 15)

        return World(cells, trains, params)

def get_station_by_entry(world, head_id):
    for name, entry in world.params["station_entry_cell"].items():
        if head_id == entry:
            return name
    return None


def choose_next_cell(world, head_id):
    C = world.cells[head_id]

    if C.cell_type == "SIGNAL" and not C.signal:
        return None

    station = get_station_by_entry(world, head_id)
    if station is not None:
        platform = world.params["station_platform"][station]
        sw = C.next_cells[0]
        world.cells[sw].selected_route = (
            1 if world.cells[platform].train_id is None else 0
        )
        return sw

    if C.cell_type == "SWITCH" and head_id in world.params["transfer_switches"]:
        go = C.next_cells[1]
        if world.cells[go].train_id is None:
            C.selected_route = 1
            return go
        C.selected_route = 0
        return C.next_cells[0]

    if C.cell_type == "SWITCH":
        return C.next_cells[min(C.selected_route, len(C.next_cells) - 1)]

    return C.next_cells[0] if C.next_cells else None


def resolve_conflicts(world, intents):
    claims = {}
    for tid, tgt in intents.items():
        if tgt is not None:
            claims.setdefault(tgt, []).append(tid)

    waits = {t.tid: t.waiting_ticks for t in world.trains}

    for tgt, tids in claims.items():
        if len(tids) > 1:
            winner = max(tids, key=lambda t: waits[t])
            for t in tids:
                if t != winner:
                    intents[t] = None


def move_train(world, train, nxt):
    tail = train.cells[-1]
    world.cells[tail].train_id = None
    train.cells = [nxt] + train.cells[:-1]
    world.cells[nxt].train_id = train.tid
    if world.cells[nxt].cell_type == "PLATFORM":
        train.dwell_remaining = world.params["dwell_time"]


def update_signals(world):
    for c in world.cells:
        if c.cell_type == "SIGNAL" and c.next_cells:
            nxt = world.cells[c.next_cells[0]]
            c.signal = nxt.train_id is None


def step(world):
    intents = {}
    for t in world.trains:
        if t.dwell_remaining > 0:
            t.dwell_remaining -= 1
            intents[t.tid] = None
            t.waiting_ticks += 1
            continue
        intents[t.tid] = choose_next_cell(world, t.cells[0])

    resolve_conflicts(world, intents)

    for t in world.trains:
        if intents[t.tid] is not None:
            move_train(world, t, intents[t.tid])
            t.waiting_ticks = 0

    update_signals(world)
    world.tick += 1


CELL_RADIUS = 10

class Button:
    def __init__(self, name, pos, size):
        self.name = name
        self.pos = pos
        self.size = size

    def hit(self, mx, my):
        x, y = self.pos
        return x <= mx <= x + self.size and y <= my <= y + 30


def layout_positions(world):
    W, H = 1200, 700
    positions = {}
    centers = {"BLACK": (250, 350), "ORANGE": (600, 350), "GREEN": (950, 350)}
    R = 150

    for name, ring in world.params["rings"].items():
        cx, cy = centers[name]
        n = len(ring)
        for i, cid in enumerate(ring):
            ang = 2 * math.pi * (i / n)
            positions[cid] = (
                round(cx + R * math.cos(ang)),
                round(cy + R * math.sin(ang)),
            )

    for name, nodes in world.params["station_nodes"].items():
        idx = world.params["station_entry_index"][name]
        ring = world.params["rings"][name]
        ang = 2 * math.pi * (idx / len(ring))
        ex, ey = positions[nodes["entry"]]

        def out(d):
            return round(ex + d * math.cos(ang)), round(ey + d * math.sin(ang))

        positions[nodes["sw"]] = out(35)
        positions[nodes["spur"]] = out(75)
        positions[nodes["platform"]] = out(120)

    return positions, (W, H)


def cell_color(c):
    if c.cell_type == "TRACK": return (150,150,150)
    if c.cell_type == "PLATFORM": return (80,150,255)
    if c.cell_type == "SWITCH": return (255,170,60)
    return (180,180,180)

def draw_ring_edges(screen, world, positions):
    color = (80, 80, 80)
    transfer_color = (0,0,0)
    thickness = 2
    for ring in world.params["rings"].values():
        n = len(ring)
        for i in range(n):
            a = ring[i]
            b = ring[(i + 1) % n]
            pygame.draw.line(screen, color, positions[a], positions[b], thickness)
    for conn_id in world.params["transfer_switches"]:
        c = world.cells[conn_id]
        if len(c.next_cells) > 1:
            go_id = c.next_cells[1] 
            pygame.draw.line(screen, transfer_color, positions[conn_id], positions[go_id], 5)
    for name, nodes in world.params["station_nodes"].items():
        p1, p2, p3, p4 = nodes["entry"], nodes["sw"], nodes["spur"], nodes["platform"]
        pygame.draw.line(screen, color, positions[p1], positions[p2], thickness)
        pygame.draw.line(screen, color, positions[p2], positions[p3], thickness)
        pygame.draw.line(screen, color, positions[p3], positions[p4], thickness)

def draw_world(screen, font, world, positions, buttons):
    screen.fill((180,180,180))
    draw_ring_edges(screen, world, positions)
    for c in world.cells:
        if c.cid in positions:
            pygame.draw.circle(screen, cell_color(c), positions[c.cid], CELL_RADIUS)

    for t in world.trains:
        for cid in t.cells:
            pygame.draw.circle(screen, (255,255,0), positions[cid], CELL_RADIUS-4)

    txt = font.render(f"tick={world.tick}", True, (0,0,0))
    screen.blit(txt, (10,10))

    for b in buttons:
        x, y = b.pos
        pygame.draw.rect(screen, (80,80,90), (x,y,b.size,30))
        pygame.draw.rect(screen, (200,200,200), (x,y,b.size,30), 2)
        t = font.render(b.name, True, (255,255,255))
        screen.blit(t, (x+5,y+5))

pygame.init()
world = World.build_world()
positions, (W, H) = layout_positions(world)
screen = pygame.display.set_mode((W, H))
font = pygame.font.SysFont("Arial", 18)
clock = pygame.time.Clock()

buttons = [
    Button("Start/Pause", (50, 650), 120),
    Button("Step", (200, 650), 60),
    Button("Reset", (300, 650), 70),
]

paused = True
running = True

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for b in buttons:
                if b.hit(mx, my):
                    if b.name == "Start/Pause":
                        paused = not paused
                    elif b.name == "Step":
                        step(world)
                    elif b.name == "Reset":
                        world = World.build_world()
                        positions, _ = layout_positions(world)

    if not paused:
        step(world)

    draw_world(screen, font, world, positions, buttons)
    pygame.display.flip()
    clock.tick(4)