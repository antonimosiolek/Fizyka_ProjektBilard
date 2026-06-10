import pygame
import math
import sys

# ─────────────────────────────────────────────
#  Inicjalizacja
# ─────────────────────────────────────────────
pygame.init()

WIDTH, HEIGHT = 1220, 680
TABLE_L = 55
TABLE_R = 870
TABLE_T = 70
TABLE_B = 620

PANEL_X = TABLE_R + 25
PANEL_W = 310

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Symulacja Bilardu – Efekt Motyla | Schemat Eulera")
CLOCK = pygame.time.Clock()

# ─────────────────────────────────────────────
#  Stałe fizyczne
#   Jednostki "wewnętrzne": piksele i sekundy
#   SCALE = 200 px / 1 m  ->  G·SCALE = przyspieszenie tarcia [px/s²]
# ─────────────────────────────────────────────
G      = 9.81   # m/s²
MU     = 0.1   # współczynnik tarcia kinetycznego (bezwymiarowy)
SCALE  = 200    # px / m
DT     = 0.005  # krok czasowy schematu Eulera [s]
STOP_V = 1.5    # próg zatrzymania [px/s]  – mały, żeby nie trzaskać

FRICTION_ACC = MU * G * SCALE   # Z drugiego równania Newtona przyspieszenie (opóźnienie)
MAX_TRAJ     = 600              # max punktów trajektorii (pamięć)

# ─────────────────────────────────────────────
#  Paleta kolorów
# ─────────────────────────────────────────────
BG          = (12, 14, 18)
TABLE_FELT  = (30, 125, 50)
TABLE_FELT2 = (27, 112, 44)
TABLE_RAIL  = (90, 55, 20)
POCKET_C    = (8, 8, 8)
LINE_FELT   = (34, 138, 56)

PANEL_BG    = (18, 20, 30)
PANEL_LINE  = (55, 60, 85)

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
YELLOW = (255, 215, 0)
GRAY   = (120, 120, 140)

RED        = (220,  60,  60)
LIGHT_RED  = (255, 130, 130)
BLUE       = ( 60, 110, 230)
LIGHT_BLUE = (120, 170, 255)



# rysowanie zaokrąglonego prostokąta
def draw_rounded_rect(surf, color, rect, r=8, width=0):
    pygame.draw.rect(surf, color, rect, width, border_radius=r)


# ─────────────────────────────────────────────
#  Klasa Bila
# ─────────────────────────────────────────────
class Ball:
    def __init__(self, x, y, vx, vy, radius=14, color=WHITE):
        self.x  = float(x)
        self.y  = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.r  = radius
        self.color = color
        self.traj: list[tuple[float, float]] = []
        self.moving = (vx != 0 or vy != 0)

    # ── Schemat Eulera (semi-niejawny) ───────
    def update(self, dt: float):
        speed = math.hypot(self.vx, self.vy)

        if speed > STOP_V:
            # Tarcie: a = −µg · v̂   (kierunek przeciwny do v)
            # WAŻNE: sprawdzamy, czy deceleration nie "przewróci" prędkości
            decel = FRICTION_ACC * dt
            if decel >= speed:
                # Zatrzymanie dokładnie w tym kroku (Euler mógłby odwrócić v)
                self.vx = 0.0
                self.vy = 0.0
                self.moving = False
            else:
                inv = 1.0 / speed
                self.vx -= FRICTION_ACC * self.vx * inv * dt   # Euler: v ← v + a·Δt
                self.vy -= FRICTION_ACC * self.vy * inv * dt
                self.moving = True
        else:
            self.vx = 0.0
            self.vy = 0.0
            self.moving = False

        # Pozycja: x ← x + v·Δt  (używamy zaktualizowanego v → semi-implicit)
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Zapis trajektorii
        if self.moving:
            if (not self.traj or
                    math.hypot(self.x - self.traj[-1][0],
                               self.y - self.traj[-1][1]) > 3):
                self.traj.append((self.x, self.y))
                if len(self.traj) > MAX_TRAJ:
                    self.traj.pop(0)

    def clear_traj(self):
        self.traj.clear()

    # ── Rysowanie ────────────────────────────
    def draw(self, surf, ghost=False):
        # Trajektoria z zanikaniem
        n = len(self.traj)
        if n > 1:
            for i in range(1, n):
                t = i / n
                c = tuple(int(ch * t * 0.75) for ch in self.color)
                pygame.draw.line(surf, c,
                                 (int(self.traj[i-1][0]), int(self.traj[i-1][1])),
                                 (int(self.traj[i][0]),   int(self.traj[i][1])), 2)

        cx, cy = int(self.x), int(self.y)
        if ghost:
            pygame.draw.circle(surf, self.color, (cx, cy), self.r, 3)
            pygame.draw.circle(surf, WHITE, (cx - 4, cy - 4), 3)
        else:
            pygame.draw.circle(surf, self.color, (cx, cy), self.r)
            lighter = tuple(min(255, ch + 90) for ch in self.color)
            pygame.draw.circle(surf, lighter, (cx - 4, cy - 4), 5)


# ─────────────────────────────────────────────
#  Klasa System Bilardowy
# ─────────────────────────────────────────────
class BilliardSystem:
    BALL_R = 14

    def __init__(self, angle_offset: float, label: str):
        self.label         = label
        self.angle_offset  = angle_offset
        self.time_elapsed  = 0.0
        self.balls: list[Ball] = []
        self._init()

    def _init(self):
        self.balls.clear()
        self.time_elapsed = 0.0

        cue_x  = TABLE_L + 165
        cue_y  = (TABLE_T + TABLE_B) // 2
        tgt_x  = TABLE_L + int((TABLE_R - TABLE_L) * 0.65)
        tgt_y  = (TABLE_T + TABLE_B) // 2

        speed  = 540                           # [px/s]
        angle  = self.angle_offset             # [rad]
        vx     = speed * math.cos(angle)
        vy     = speed * math.sin(angle)

        cc = RED       if self.label == "A" else BLUE
        tc = LIGHT_RED if self.label == "A" else LIGHT_BLUE
        r  = self.BALL_R

        self.cue = Ball(cue_x, cue_y, vx, vy, radius=r, color=cc)
        self.balls.append(self.cue)

        # Trójkąt 3 bil docelowych
        gap = 1
        self.balls.append(Ball(tgt_x,           tgt_y,           0, 0, r, tc))
        self.balls.append(Ball(tgt_x + 2*r+gap, tgt_y - r - gap, 0, 0, r, tc))
        self.balls.append(Ball(tgt_x + 2*r+gap, tgt_y + r + gap, 0, 0, r, tc))

    def reset(self):
        self._init()

    def all_stopped(self) -> bool:
        return all(not b.moving for b in self.balls)

    def clear_trajs(self):
        for b in self.balls:
            b.clear_traj()

    # ── Aktualizacja fizyki ───────────────────
    def update(self):
        self.time_elapsed += DT

        for b in self.balls:
            b.update(DT)

        # Kolizje ze ścianami (abs() chroni przed wielokrotnym odbiciem w tej samej klatce)
        for b in self.balls:
            if b.x - b.r < TABLE_L:
                b.x  = TABLE_L + b.r
                b.vx = abs(b.vx)
                b.moving = True
            elif b.x + b.r > TABLE_R:
                b.x  = TABLE_R - b.r
                b.vx = -abs(b.vx)
                b.moving = True
            if b.y - b.r < TABLE_T:
                b.y  = TABLE_T + b.r
                b.vy = abs(b.vy)
                b.moving = True
            elif b.y + b.r > TABLE_B:
                b.y  = TABLE_B - b.r
                b.vy = -abs(b.vy)
                b.moving = True

        # Zderzenia bil: sprężyste (równe masy)
        # Dla równych mas: wymiana składowych prędkości wzdłuż normalnej
        n = len(self.balls)
        for i in range(n):
            for j in range(i + 1, n):
                b1, b2  = self.balls[i], self.balls[j]
                dx      = b2.x - b1.x
                dy      = b2.y - b1.y
                dist    = math.hypot(dx, dy)
                min_d   = b1.r + b2.r

                if 0 < dist < min_d:
                    # Normalna zderzenia
                    nx, ny  = dx / dist, dy / dist

                    # Korekcja pozycji (zapobiega przenikaniu)
                    overlap = min_d - dist
                    b1.x -= nx * overlap * 0.5
                    b1.y -= ny * overlap * 0.5
                    b2.x += nx * overlap * 0.5
                    b2.y += ny * overlap * 0.5




    def draw(self, surf, ghost=False):
        for b in self.balls:
            b.draw(surf, ghost=ghost)


# ─────────────────────────────────────────────
#  Rysowanie stołu bilardowego
# ─────────────────────────────────────────────
def draw_table(surf):
    # Bandy (rail)
    rail_rect = (TABLE_L - 18, TABLE_T - 18,
                 TABLE_R - TABLE_L + 36, TABLE_B - TABLE_T + 36)
    draw_rounded_rect(surf, TABLE_RAIL, rail_rect, r=12)

    # Filc stołu – szachownica (subtelna tekstura)
    for row in range(int((TABLE_B - TABLE_T) / 30) + 1):
        for col in range(int((TABLE_R - TABLE_L) / 30) + 1):
            rx = TABLE_L + col * 30
            ry = TABLE_T + row * 30
            rw = min(30, TABLE_R - rx)
            rh = min(30, TABLE_B - ry)
            c  = TABLE_FELT if (row + col) % 2 == 0 else TABLE_FELT2
            pygame.draw.rect(surf, c, (rx, ry, rw, rh))

    # Linia środkowa
    cx = (TABLE_L + TABLE_R) // 2
    my = (TABLE_T + TABLE_B) // 2
    pygame.draw.line(surf, LINE_FELT, (cx, TABLE_T), (cx, TABLE_B), 1)
    pygame.draw.circle(surf, LINE_FELT, (cx, my), 45, 1)

    # Łuzy (kieszenie)
    pockets = [
        (TABLE_L, TABLE_T), (TABLE_R, TABLE_T),
        (TABLE_L, TABLE_B), (TABLE_R, TABLE_B),
        (cx,      TABLE_T), (cx,      TABLE_B),
    ]
    for px, py in pockets:
        pygame.draw.circle(surf, POCKET_C, (px, py), 14)
        pygame.draw.circle(surf, (4, 4, 4),  (px, py), 11)


# ─────────────────────────────────────────────
#  Panel informacyjny
# ─────────────────────────────────────────────
def draw_panel(surf, sA: BilliardSystem, sB: BilliardSystem,
               angle_deg: float, paused: bool):
    pr = pygame.Rect(PANEL_X - 8, TABLE_T - 18, PANEL_W, TABLE_B - TABLE_T + 36)
    draw_rounded_rect(surf, PANEL_BG,   pr, r=10)
    draw_rounded_rect(surf, PANEL_LINE, pr, r=10, width=2)

    f_big  = pygame.font.SysFont("Arial", 16, bold=True)
    f_med  = pygame.font.SysFont("Arial", 14)
    f_sml  = pygame.font.SysFont("Arial", 12)

    x0 = PANEL_X + 5
    y  = TABLE_T - 5

    def row(text, color, font=None, indent=0):
        nonlocal y
        s = (font or f_med).render(text, True, color)
        surf.blit(s, (x0 + indent, y))
        y += s.get_height() + 3

    def sep():
        nonlocal y
        y += 4
        pygame.draw.line(surf, PANEL_LINE,
                         (PANEL_X, y), (PANEL_X + PANEL_W - 16, y))
        y += 8

    # ── Nagłówek ──
    row("EFEKT MOTYLA", YELLOW,        font=f_big)
    row("Chaos w bilardzie",  GRAY,    font=f_sml)
    sep()

    # ── Układ A ──
    row("▶  Układ A  (czerwony)", RED, font=f_big)
    spA = math.hypot(sA.cue.vx, sA.cue.vy)
    row(f"Kąt uderzenia:  {math.degrees(sA.angle_offset):.4f}°",  LIGHT_RED, indent=8)
    row(f"Prędkość bili:  {spA:.1f} px/s",                        LIGHT_RED, indent=8)
    row(f"Czas symulacji: {sA.time_elapsed:.2f} s",               LIGHT_RED, indent=8)
    row(f"Status: {'✔ STOP' if sA.all_stopped() else '● Ruch'}",  LIGHT_RED, indent=8)
    sep()

    # ── Układ B ──
    row("▷  Układ B  (niebieski)", BLUE, font=f_big)
    spB = math.hypot(sB.cue.vx, sB.cue.vy)
    row(f"Kąt uderzenia:  {math.degrees(sB.angle_offset):.4f}°",  LIGHT_BLUE, indent=8)
    row(f"Prędkość bili:  {spB:.1f} px/s",                        LIGHT_BLUE, indent=8)
    row(f"Czas symulacji: {sB.time_elapsed:.2f} s",               LIGHT_BLUE, indent=8)
    row(f"Status: {'✔ STOP' if sB.all_stopped() else '● Ruch'}",  LIGHT_BLUE, indent=8)
    sep()

    # ── Rozbieżność ──
    row("Rozbieżność układów", YELLOW, font=f_big)
    dist = math.hypot(sA.cue.x - sB.cue.x, sA.cue.y - sB.cue.y)
    row(f"Δr bili białej:  {dist:.2f} px", WHITE, indent=8)
    row(f"Δθ (odchył):     {angle_deg:.4f}°",  WHITE, indent=8)

    # Pasek rozbieżności
    y += 4
    bw = PANEL_W - 30
    bf = min(1.0, dist / 250.0)
    pygame.draw.rect(surf, (50, 50, 60), (x0, y, bw, 12), border_radius=4)
    if bf > 0:
        fc = (int(255 * bf), int(220 * (1 - bf)), 40)
        pygame.draw.rect(surf, fc, (x0, y, int(bw * bf), 12), border_radius=4)
    y += 20
    sep()

    # ── Sterowanie ──
    row("Sterowanie", (200, 200, 200), font=f_big)
    controls = [
        ("SPACJA",  "Restart symulacji"),
        ("P",       "Pauza / Wznów"),
        ("↑ / ↓",  "Zmień odchył Δθ"),
        ("T",       "Wyczyść trajektorie"),
        ("ESC",     "Wyjście"),
    ]
    for key, desc in controls:
        ks = f_sml.render(f"[{key}]", True, YELLOW)
        ds = f_sml.render(desc,       True, GRAY)
        surf.blit(ks, (x0,      y))
        surf.blit(ds, (x0 + 75, y))
        y += ks.get_height() + 4

    if paused:
        sep()
        row("⏸  PAUZA", YELLOW, font=f_big)


# ─────────────────────────────────────────────
#  Górny pasek statusu
# ─────────────────────────────────────────────
def draw_topbar(surf, angle_deg: float):
    f = pygame.font.SysFont("Arial", 13)
    parts = [
        ("Symulacja Bilardu",       WHITE),
        ("  |  ",                   GRAY),
        ("Schemat Eulera",          YELLOW),
        ("  |  ",                   GRAY),
        ("Zderzenia sprężyste",     LIGHT_RED),
        ("  |  ",                   GRAY),
        (f"Tarcie kinetyczne µ= {MU} ",LIGHT_BLUE),
        ("  |  ",                   GRAY),
        (f"Δθ = {angle_deg:.4f}°",  YELLOW),
    ]
    x = TABLE_L
    for text, color in parts:
        s = f.render(text, True, color)
        surf.blit(s, (x, 20))
        x += s.get_width()


# ─────────────────────────────────────────────
#  Główna pętla
# ─────────────────────────────────────────────
angle_offset = 0.001   # [rad]  ≈ 0.057°  (efekt motyla)

sA = BilliardSystem(angle_offset=0.0,          label="A")
sB = BilliardSystem(angle_offset=angle_offset,  label="B")

paused  = False
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_SPACE:
                sA = BilliardSystem(0.0,          "A")
                sB = BilliardSystem(angle_offset,  "B")

            elif event.key == pygame.K_p:
                paused = not paused

            elif event.key == pygame.K_t:
                sA.clear_trajs()
                sB.clear_trajs()

            elif event.key == pygame.K_UP:
                angle_offset = min(math.radians(10), angle_offset + math.radians(0.05))
                sA = BilliardSystem(0.0,          "A")
                sB = BilliardSystem(angle_offset,  "B")

            elif event.key == pygame.K_DOWN:
                angle_offset = max(math.radians(0.01), angle_offset - math.radians(0.05))
                sA = BilliardSystem(0.0,          "A")
                sB = BilliardSystem(angle_offset,  "B")


    if not paused:
        sA.update()
        sB.update()

    # ── Rysowanie ──
    SCREEN.fill(BG)
    draw_topbar(SCREEN, math.degrees(angle_offset))
    draw_table(SCREEN)

    sA.draw(SCREEN, ghost=False)   # Układ A: pełne koła
    sB.draw(SCREEN, ghost=True)    # Układ B: okręgi (duch)

    draw_panel(SCREEN, sA, sB, math.degrees(angle_offset), paused)

    pygame.display.flip()
    CLOCK.tick(60)

pygame.quit()
sys.exit()