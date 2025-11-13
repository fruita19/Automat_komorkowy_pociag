import pygame
import math
from typing import List, Dict, Tuple,Optional
class World:
    def __init__(self, cells : List["Cell"], trains : List["Train"], params, tick = 0):
        self.cells = cells
        self.trains = trains
        self.params = params
        self.tick = tick
    def get_cells(self):
        return self.cells
    def get_trains(self):
        return self.trains
    def get_params(self):
        return self.params
    def get_tick(self):
        return self.tick
    def set_cells(self,cells):
        self.cells=cells
    def set_trains(self,trains):
        self.trains=trains
    def set_params(self,params):
        self.params=params
    def set_tick(self,tick):
        self.tick=tick
    def build_world():
        cells: List[Cell]=[]
        trains: List[Train]=[]
        params: dict={"dwell_time":10}
        N= 40 
        for i in range(N):
            cells.append(Cell(cid=i, cell_type="TRACK", next_cells=[], train_id=None, signal=True))
        for i in range(N):
            cells[i].next_cells= [ (i+1) % N ]
        branch_id=len(cells)
        cells.append(Cell(branch_id, "BRANCH", [], None, True))
        cells[10].next_cells = [branch_id]
        PIN1 = len(cells); 
        cells.append(Cell(PIN1, "SWITCH",  [], None, True))
        PIN2 = len(cells); 
        cells.append(Cell(PIN2, "SWITCH",  [], None, True))
        PIN3 = len(cells); 
        cells.append(Cell(PIN3, "SWITCH",  [], None, True))
        P1 = len(cells)
        cells.append(Cell(P1, "PLATFORM", [], None, True))
        P2 = len(cells)
        cells.append(Cell(P2, "PLATFORM", [], None, True))
        P3 = len(cells)
        cells.append(Cell(P3, "PLATFORM", [], None, True))
        cells[branch_id].next_cells=[PIN1,PIN2]
        cells[PIN1].next_cells=[P1]
        cells[PIN2].next_cells=[P2,PIN3]
        cells[PIN3].next_cells=[P3]
        OUT_A=len(cells)
        cells.append(Cell(OUT_A, "TRACK",  [], None, True))
        SIG=len(cells)
        cells.append(Cell(SIG, "SIGNAL",  [], None, True))
        OUT_B=len(cells)
        cells.append(Cell(OUT_B, "TRACK",  [], None, True))
        MERGE=len(cells)
        cells.append(Cell(MERGE, "MERGE",  [], None, True))
        cells[P1].next_cells = [OUT_A]
        cells[P2].next_cells = [OUT_A]
        cells[P3].next_cells = [OUT_A]
        cells[OUT_A].next_cells = [SIG]
        cells[SIG].next_cells = [OUT_B]
        cells[OUT_B].next_cells = [MERGE]
        cells[MERGE].next_cells = [20]      
        T1_cells = [0, 39, 38]
        T2_cells = [22, 21, 20]
        trains.append(Train(1, T1_cells, 0, 0))
        trains.append(Train(3, T2_cells, 0, 0))
        for train in trains:
            for cid in train.cells:
                if 0<=cid<len(cells):
                    cells[cid].train_id=train.tid
        return World(cells, trains, params, 0)
class Train:
    def __init__(self, tid, cells , dwell_remaining , waiting_ticks  ):
        self.tid=tid
        self.cells=cells
        self.dwell_remaining=dwell_remaining
        self.waiting_ticks=waiting_ticks
    def get_tid(self):
        return self.tid
    def get_cells(self):
        return self.cells
    def get_dwell_remaining(self):
        return self.dwell_remaining
    def get_waiting_ticks(self):
        return self.waiting_ticks
    def set_tid(self,tid ):
        if isinstance(tid,int):
            self.tid=tid
        else:
            raise TypeError(" Type should be INT ")
    def set_cells(self,cells):
        self.cells=cells
    def set_dwell_remaining(self,dwell_remaining):
        if isinstance(dwell_remaining,int):
            self.dwell_remaining=dwell_remaining
        else:
            raise TypeError(" Type should be INT ")
    def set_waiting_ticks(self,waiting_ticks):
        if isinstance(waiting_ticks,int):
            self.waiting_ticks=waiting_ticks
        else:
            raise TypeError(" Type should be INT ")
class Cell:
    def __init__(self, cid, cell_type, next_cells, train_id, signal, state ="free" ):
        self.cid=cid 
        self.cell_type=cell_type
        self.next_cells=next_cells
        self.train_id=train_id
        self.state=state
        self.signal=signal
        self.selected_route = 0
    def get_cid(self):
        return self.cid
    def get_cell_type(self):
        return self.cell_type
    def get_next_cells(self):
        return self.next_cells
    def get_state(self):
        return self.state
    def get_train_id(self):
        return self.train_id
    def get_signal(self):
        return self.signal
    def set_cid(self,cid):
        self.cid=cid
    def set_cell_type(self,cell_type):
        self.cell_type=cell_type
    def set_next_cells(self,next_cells):
        self.next_cells=next_cells
    def set_state(self,state):
        self.state=state
    def set_train_id(self,train_id):
        self.train_id=train_id
    def set_signal(self,signal):
        self.signal=signal
    def set_switch_route(self, index):
        if self.cell_type == "SWITCH" and index < len(self.next_cells):
            self.selected_route = index
    def get_next_cell_id(self):
        if self.cell_type == "SWITCH":
            return self.next_cells[self.selected_route]
        return self.next_cells[0]
    def is_available(self):
        return self.signal == True
class Button:
    def __init__(self, name , positions , size ):
        self.name=name
        self.positions=positions
        self.size=size
    def get_name(self):
        return self.name
    def get_positions(self):
        return self.positions
    def get_size(self):
        return self.size
    def set_name(self,name):
        self.name=name
    def set_size(self,size):
        self.size=size
    def set_positions(self,positions):
        self.positions=positions
    def button_move(self, dx, dy):
        x, y = self.positions
        self.positions = (x + dx, y + dy)
def choose_next_cell(world,head_id):
        C = world.cells[head_id]
        if C.cell_type == "SIGNAL" and C.signal == False:
            return None
        if C.cell_type == "BRANCH":
            for  entry_id in C.next_cells:
                if not world.cells[entry_id].next_cells:
                    continue
                plat_id = world.cells[entry_id].next_cells[0]
                if world.cells[plat_id].train_id is  None:
                    return entry_id
            return None
        if C.cell_type == "SWITCH":
            return C.next_cells[C.selected_route] 
        if not C.next_cells :
            return None
        return C.next_cells[0]
def resolve_conflicts(world, intents):
        claims = {}
        for tid, target in intents.items():
            if target is not None:
                claims.setdefault(target, []).append(tid)
        waiting_map: Dict[int, int] = {t.tid: t.waiting_ticks for t in world.trains}
        for target, tids in claims.items():
            if len(tids) <= 1:
                continue
            winner = None
            best_wait = -1
            for tid in tids:
                w = waiting_map.get(tid, 0)
                if w > best_wait:
                    best_wait = w
                    winner = tid
            for tid in tids:
                if tid != winner:
                    intents[tid] = None
def move_train(world,train,nxt):
    tail=train.cells[-1]
    world.cells[tail].train_id = None
    train.cells=[nxt]+train.cells[:-1]
    train.tid =world.cells[nxt].train_id 
    if  world.cells[nxt].cell_type == "PLATFORM":
        train.dwell_remaining = world.params["dwell_time"]
def update_signals(world):
    for C in world.cells:
        if C.cell_type  == "SIGNAL":
            if not C.next_cells:
                continue
            next_id = C.next_cells[0]
            next_cell = world.cells[next_id]
            C.signal = (next_cell.train_id == None) 
def step(world, intents = {}):
    for t in world.trains:
        if t.dwell_remaining > 0:
            t.dwell_remaining = t.dwell_remaining - 1
            intents[t.tid] = None
            t.waiting_ticks = t.waiting_ticks + 1
            continue
        head = t.cells[0]
        target = choose_next_cell(world, head)
        if target != None:
            TGT=world.cells[target]
            allowed=(TGT.train_id == None) and  (TGT.cell_type != "SIGNAL" or  TGT.signal == True)
            intents[t.tid] = target   if  allowed  else  None
        else: 
            intents[t.tid]=None
        if intents[t.tid] == None:
          t.waiting_ticks = t.waiting_ticks + 1
    resolve_conflicts(world, intents)
    for t in world.trains:
        target = intents[t.tid]
        if target != None:
            move_train(world, t, target)
            t.waiting_ticks = 0
    update_signals(world)
    world.tick = world.tick + 1
if __name__ == "__main__":
    world = World.build_world()
    for i in range(1,5):
        step(world)
    heads = [t.cells[0] for t in world.trains]
def layout_positions(world):
    W=1000
    H=700
    cx=W/2
    cy=H/2
    R=250
    n=len(world.cells)
    positions={}
    for i,C in enumerate(world.cells):
        ang=2*math.pi*(i/max(1,n))
        x=cx+R*math.cos(ang)
        y=cy+R*math.sin(ang)
        positions[C.cid]=(round(x),round(y))
    return positions, (W,H)
def handle_click_switch(world, positions, mx, my):
    for c in world.cells:
        if c.cell_type != "SWITCH":
            continue
        (x,y)=positions[c.cid]
        dyst2=(mx-x)**2+(my-y)**2
        SWITCH_HIT_RADIUS=15
        if dyst2<=SWITCH_HIT_RADIUS**2:
            if c.next_cells and len(c.next_cells)>1:
                c.selected_route = (c.selected_route + 1) % len(c.next_cells)
            return True
    return False
color= (60, 60, 80)
EDGE_THICKNESS_DEFAULT = 1
EDGE_THICKNESS_ACTIVE = 3
def draw_edges(screen: pygame.Surface, world, positions: Dict[int, Tuple[int, int]]):
    for c in world.cells:
        try:
            px, py = positions[c.cid]
            x = px + 2 * 15  
            y = py + 15 // 2
        except KeyError:
            continue
        next_cells_list = c.next_cells if c.next_cells is not None else []
        for nxt_cid in next_cells_list:
            try:
                npx, npy = positions[nxt_cid]
                nx = npx
                ny = npy + 15 // 2   
            except KeyError:
                continue
            thickness = EDGE_THICKNESS_DEFAULT
            if c.cell_type == "SWITCH":
                route_index = c.selected_route % len(c.next_cells)
                if c.next_cells[route_index] == nxt_cid:
                    thickness = EDGE_THICKNESS_ACTIVE 
            pygame.draw.line(screen, color, (x, y), (nx, ny), thickness)
def cell_base_color(c):
    if  c.cell_type == "TRACK":   
        return (150,150,150) # szary 
    if c.cell_type == "BRANCH":  
        return (180,120,255)   # fiolet 
    if c.cell_type == "MERGE" :
        return   (120,80,200)   #ciemny fiolet 
    if c.cell_type == "PLATFORM":
        return (80,150,255) #niebieski
    if c.cell_type == "SWITCH":  
        return (255,170,60)  #pomarańczowy
    if c.cell_type == "SIGNAL":
        if c.signal == True: 
            return  (80,200,120)  # zielony
        elif c.signal == False: 
            return (220,60,60)  # czerwony 
    else: 
        return (180,180,180) # domyślny_szary 
CELL_RADIUS= 10
def  draw_switch_indicator(screen, c, positions):
    if  c.cell_type != "SWITCH" or not  c.next_cells:
        return None
    (x, y) = positions[c.cid]          
    r = CELL_RADIUS + 5                
    idx = min(c.selected_route, len(c.next_cells) - 1)
    tgt = c.next_cells[idx]            
    (nx, ny) = positions[tgt]
    ang = math.atan2(ny - y, nx - x)        
    px = x + r * math.cos(ang)              
    py = y + r * math.sin(ang)
    pygame.draw.circle(screen,(255,220,120), (px,py), 2)
def darken(color, o):
    R, G, B = color
    R2 = max(0, R - o)
    G2 = max(0, G - o)
    B2 = max(0, B - o)
    return (R2, G2, B2)
def  draw_cells(screen, world, positions):
    for  c in  world.cells:
        (x, y) = positions[c.cid]
        color  = cell_base_color(c)   
        if c.train_id != None:
            fill=darken(color, o=60)           
        elif  c.train_id == None:
            fill = color
        pygame.draw.circle(screen, fill, (x, y), CELL_RADIUS)  
        pygame.draw.circle(screen, (20,20,25),(x,y), CELL_RADIUS,2)
        draw_switch_indicator(screen, c, positions)
def draw_trains(screen, world, positions):
    for  t in world.trains:
        for cid in t.cells :
            (x, y) = positions[cid]
            pygame.draw.circle(screen, (255, 255, 0) , (x,y),CELL_RADIUS-4) # zolty 
        (hx, hy) = positions[t.cells[0]]
        pygame.draw.circle(screen, (0, 0, 0), (hx,hy), CELL_RADIUS-2) # czarne 
def draw_hud(screen, font, world):
    tekst= "tick=" + str(world.tick) +"   dwell_time=" + str(world.params["dwell_time" ]) +"   [SPACE]=start/pause  N=step  R=reset  ESC=exit"
    bitmapa = font.render(tekst, True,(230,230,230))
    screen.blit(bitmapa, (12,12))
def draw_buttons(screen,list_buttons,font):
    for b in list_buttons:
        (x, y) =b.positions
        w = b.size
        h = 30
        pygame.draw.rect(screen, (80, 80, 90), (x, y, w, h))
        pygame.draw.rect(screen, (200, 200, 200), (x, y, w, h), 2)
        text = font.render(b.name, True, (255, 255, 255)) 
        screen.blit(text, (x + 5, y + 5))
def draw_world(screen, font, world, positions):
    screen.fill( (180,180,180)) # domyślny_szary
    draw_edges(screen, world, positions)              
    draw_cells(screen, world, positions)              
    draw_trains(screen, world, positions)            
    draw_hud(screen, font, world) 
if __name__ == "__main__":
    pygame.init()
    world = World.build_world()
    positions, (W, H) = layout_positions(world)
    screen = pygame.display.set_mode((W, H))
    font = pygame.font.SysFont("Arial", 20)
    clock = pygame.time.Clock()
    buttons = [
        Button("Start/Pause", (50, 640), 100),
        Button("Step", (200, 640), 60),
        Button("Reset", (300, 640), 70)
    ]
    running = True
    paused=True  
    while running:
        for event in pygame.event.get():
            if  event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                handle_click_switch(world, positions, mx, my)
                for b in buttons:
                    bx, by = b.positions
                    if bx <= mx <= bx + b.size and by <= my <= by + 30:
                        if b.name == "Step":
                            step(world)
                        elif b.name == "Reset":
                            world = World.build_world()
                            positions, _ = layout_positions(world)
                        elif b.name == "Start/Pause":
                            paused = not paused
        if not paused:
            step(world)                   
        draw_world(screen, font, world, positions)
        draw_buttons(screen, buttons,font)
        pygame.display.flip()
        clock.tick(4) 
