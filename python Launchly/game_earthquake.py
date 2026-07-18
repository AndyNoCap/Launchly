import pygame
import math
import sys
import random

# --- INIȚIALIZARE PYGAME ---
pygame.init()
pygame.font.init()

# Configurații Ecran
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Laborator Virtual: Fizica Cutremurelor și Rezonanța")

# Culori (RGB)
COLOR_BG = (20, 25, 30)         # Fundal întunecat (stil dark mode pt vizibilitate)
COLOR_GRID = (40, 45, 55)       # Caroiaj
COLOR_GROUND = (60, 50, 40)     # Pământ
COLOR_PANEL = (30, 35, 45)      # Panou UI
COLOR_TEXT_LIGHT = (230, 230, 240)
COLOR_TEXT_DARK = (15, 15, 20)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (120, 120, 130)
COLOR_RED = (255, 60, 60)
COLOR_GREEN = (40, 220, 100)
COLOR_BLUE = (60, 150, 255)
COLOR_YELLOW = (255, 200, 40)

# Culori Clădiri (Vibrante pentru contrast pe fundal închis)
COLOR_TALL = (100, 180, 255)    # Albastru deschis
COLOR_MEDIUM = (255, 150, 50)   # Portocaliu
COLOR_SHORT = (200, 100, 255)   # Violet

# Fonturi
font_small = pygame.font.SysFont("Segoe UI", 14)
font_medium = pygame.font.SysFont("Segoe UI", 18, bold=True)
font_large = pygame.font.SysFont("Segoe UI", 24, bold=True)
font_math = pygame.font.SysFont("Consolas", 15)

clock = pygame.time.Clock()
FPS = 60
DAMPING_RATIO = 0.10  # Coeficientul de amortizare (zeta)

# --- CLASE UI ---

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, start_val, label, unit=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.label = label
        self.unit = unit
        self.handle_rect = pygame.Rect(x, y, 16, h + 14)
        self.update_handle_pos()
        self.dragging = False

    def update_handle_pos(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.x + ratio * self.rect.width
        self.handle_rect.centery = self.rect.centery

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pos_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            ratio = (pos_x - self.rect.x) / self.rect.width
            self.val = self.min_val + ratio * (self.max_val - self.min_val)
            self.update_handle_pos()

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_GRAY, self.rect, border_radius=5)
        color_handle = COLOR_YELLOW if self.dragging else COLOR_WHITE
        pygame.draw.rect(surface, color_handle, self.handle_rect, border_radius=5)
        txt = f"{self.label}: {self.val:.1f} {self.unit}"
        surface.blit(font_medium.render(txt, True, COLOR_TEXT_LIGHT), (self.rect.x, self.rect.y - 25))

class Button:
    def __init__(self, x, y, w, h, text, color, hover_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return True
        return False

    def draw(self, surface):
        c = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, c, self.rect, border_radius=6)
        txt_surf = font_medium.render(self.text, True, COLOR_WHITE)
        surface.blit(txt_surf, txt_surf.get_rect(center=self.rect.center))

# --- FIZICĂ PARTICULE ---

class Debris:
    def __init__(self, x, y, w, h, vx, vy, color):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.vx, self.vy = vx, vy
        self.color = color
        self.angle = 0.0
        self.rot_speed = random.uniform(-200, 200)

    def update(self, dt, ground_y, ground_v):
        # Gravitație
        self.vy += 1500 * dt  
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle += self.rot_speed * dt

        # Coliziune cu solul mobil (Bouncing)
        if self.y + self.h > ground_y:
            self.y = ground_y - self.h
            if abs(self.vy) > 30: # Dacă cade suficient de tare, sare
                self.vy = -self.vy * 0.35 # Coeficient de restituire (pierde energie)
                self.vx *= 0.6  # Frecare la contact
                self.rot_speed *= 0.5
            else: # S-a oprit din sărit
                self.vy = 0
                self.vx = ground_v # Se mișcă stânga-dreapta cu solul
                self.rot_speed = 0

    def draw(self, surface):
        rect_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(rect_surf, self.color, (0, 0, self.w, self.h))
        pygame.draw.rect(rect_surf, (0, 0, 0), (0, 0, self.w, self.h), 1)
        rotated = pygame.transform.rotate(rect_surf, self.angle)
        surface.blit(rotated, rotated.get_rect(center=(self.x + self.w/2, self.y + self.h/2)).topleft)

# --- CLASA CLĂDIRE ---

class Building:
    def __init__(self, center_x, height, width, f_natural, name, color):
        self.center_x = center_x
        self.height = height
        self.width = width
        self.f_natural = f_natural
        self.name = name
        self.default_color = color
        self.color = color
        self.x_top = center_x
        self.v_top = 0.0
        self.collapsed = False
        self.debris = []

    def reset(self):
        self.x_top = self.center_x
        self.v_top = 0.0
        self.collapsed = False
        self.debris.clear()
        self.color = self.default_color

    def update(self, ground_x, ground_v, dt, ground_y):
        if self.collapsed:
            for d in self.debris:
                d.update(dt, ground_y, ground_v)
            return

        # Fizica ecuației oscilatorului forțat: m*x'' + c*x' + k*x = Forță_sol
        omega_n = 2 * math.pi * self.f_natural
        k = omega_n ** 2
        c = 2 * DAMPING_RATIO * omega_n 
        
        dx = self.x_top - (self.center_x + ground_x)
        dv = self.v_top - ground_v
        a_top = -k * dx - c * dv
        
        # Sub-stepping pentru precizie numerică
        sub_steps = 5
        for _ in range(sub_steps):
            self.v_top += a_top * (dt / sub_steps)
            self.x_top += self.v_top * (dt / sub_steps)

        # Verificare tensiune de rupere
        current_shear = abs(self.x_top - (self.center_x + ground_x))
        threshold = 40 if self.height > 150 else (30 if self.height > 100 else 18)
        
        if current_shear > threshold:
            self.collapsed = True
            # Spargere în blocuri
            num_blocks = int(self.height / 25)
            bh = self.height / num_blocks
            base_x = self.center_x + ground_x
            
            for i in range(num_blocks):
                ratio = i / num_blocks
                cy = ground_y - self.height + i * bh
                cx = self.x_top * (1 - ratio) + base_x * ratio
                # Atribuire impuls inițial (bucățile de sus zboară mai tare)
                vx = self.v_top * (1 - ratio) * 1.5 + random.uniform(-20, 20)
                vy = random.uniform(-100, 0)
                self.debris.append(Debris(cx - self.width/2, cy, self.width, bh+1, vx, vy, self.color))

    def draw(self, surface, ground_x, ground_y):
        if self.collapsed:
            for d in self.debris: d.draw(surface)
            lbl = font_medium.render("PRĂBUȘITĂ", True, COLOR_RED)
            surface.blit(lbl, (self.center_x + ground_x - lbl.get_width()//2, ground_y - 25))
            return

        base_x = self.center_x + ground_x
        top_y = ground_y - self.height
        p1, p2 = (base_x - self.width//2, ground_y), (base_x + self.width//2, ground_y)
        p3, p4 = (self.x_top + self.width//2, top_y), (self.x_top - self.width//2, top_y)
        
        # Desen Clădire
        pygame.draw.polygon(surface, self.color, [p1, p2, p3, p4])
        pygame.draw.polygon(surface, COLOR_TEXT_LIGHT, [p1, p2, p3, p4], 2)
        
        # Etaje/Ferestre dinamice
        for f in range(int(self.height / 25)):
            cy = ground_y - 12 - (f * 23)
            ratio = (ground_y - cy) / self.height
            cx = base_x + ratio * (self.x_top - base_x)
            pygame.draw.rect(surface, COLOR_BG, (cx - self.width//4 - 4, cy - 6, 8, 12))
            pygame.draw.rect(surface, COLOR_BG, (cx + self.width//4 - 4, cy - 6, 8, 12))
            
        lbl = font_medium.render(f"{self.name} ({self.f_natural} Hz)", True, self.color)
        surface.blit(lbl, (self.x_top - lbl.get_width() // 2, top_y - 25))

# --- FUNCȚIE GRAFIC REZONANȚĂ TEORETICĂ ---
def draw_resonance_graph(surface, x, y, w, h, buildings, current_f):
    pygame.draw.rect(surface, (20, 25, 30), (x, y, w, h), border_radius=8)
    pygame.draw.rect(surface, COLOR_GRAY, (x, y, w, h), 2, border_radius=8)
    
    # Axe
    pygame.draw.line(surface, COLOR_GRAY, (x+10, y+h-15), (x+w-10, y+h-15), 1) # Axa Frecvență (X)
    pygame.draw.line(surface, COLOR_GRAY, (x+10, y+10), (x+10, y+h-15), 1)     # Axa Amplitudine (Y)
    surface.blit(font_small.render("Amplitudine Răspuns (Teoretic)", True, COLOR_TEXT_LIGHT), (x+20, y+5))
    surface.blit(font_small.render("Frecvență (Hz) ->", True, COLOR_TEXT_LIGHT), (x+w-100, y+h-30))

    max_f = 4.5
    
    # Desenăm curbele pentru fiecare clădire
    for b in buildings:
        points = []
        for px in range(10, w-10):
            f = (px / (w-20)) * max_f
            if f == 0: continue
            
            # Formula Factorului de Amplificare Dinamică (Magnification Factor)
            r = f / b.f_natural
            denominator = math.sqrt((1 - r**2)**2 + (2 * DAMPING_RATIO * r)**2)
            M = 1.0 / denominator if denominator != 0 else 0
            
            py = y + h - 15 - (M * 12) # Scalare vizuală
            if py < y + 10: py = y + 10 # Cap
            points.append((x + px, py))
        
        if len(points) > 1:
            pygame.draw.lines(surface, b.color, False, points, 2)

    # Linia indicatorului curent
    cx = x + 10 + int((current_f / max_f) * (w - 20))
    pygame.draw.line(surface, COLOR_RED, (cx, y+10), (cx, y+h-15), 2)
    surface.blit(font_small.render(f"Undă: {current_f}Hz", True, COLOR_RED), (cx + 5, y + 25))


# --- FUNCȚIE PRINCIPALĂ ---
def main():
    buildings = [
        Building(300, 260, 60, 1.0, "Zgârie Nori", COLOR_TALL),
        Building(600, 150, 70, 2.2, "Bloc Locuințe", COLOR_MEDIUM),
        Building(900, 80, 80, 3.6, "Casă Cărămidă", COLOR_SHORT)
    ]
    
    # UI Control (Mutat mai jos, panou mai mare)
    panel_y = 550
    slider_amp = Slider(30, 600, 200, 12, 0.0, 40.0, 20.0, "AMPLITUDINE", "px")
    slider_freq = Slider(30, 680, 200, 12, 0.5, 4.5, 1.5, "FRECVENȚĂ", "Hz")
    
    btn_start = Button(260, 590, 160, 45, "START CUTREMUR", COLOR_GREEN, (80, 240, 120))
    btn_reset = Button(260, 660, 160, 45, "REPARĂ TOT", COLOR_GRAY, (160, 160, 170))
    
    graph_points = []
    ground_y = 520
    sim_time, ground_x, ground_v = 0.0, 0.0, 0.0
    active = False
    running = True

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            # --- ADD THIS BLOCK ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False 
            # ----------------------
            
            slider_amp.handle_event(event)
            slider_freq.handle_event(event)
            if btn_start.handle_event(event):
                active = not active
                btn_start.text, btn_start.color = ("OPREȘTE", COLOR_RED) if active else ("START CUTREMUR", COLOR_GREEN)
            if btn_reset.handle_event(event):
                active, sim_time, ground_x, ground_v = False, 0.0, 0.0, 0.0
                graph_points.clear()
                btn_start.text, btn_start.color = "START CUTREMUR", COLOR_GREEN
                for b in buildings: b.reset()

        f, A = slider_freq.val, slider_amp.val

        if active:
            sim_time += dt
            ground_x = A * math.sin(2 * math.pi * f * sim_time)
            ground_v = A * (2 * math.pi * f) * math.cos(2 * math.pi * f * sim_time)
        else:
            ground_x, ground_v = 0.0, 0.0

        for b in buildings: b.update(ground_x, ground_v, dt, ground_y)

        # RENDER MEDIU (Fundal Grid)
        screen.fill(COLOR_BG)
        for i in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, COLOR_GRID, (i, 0), (i, ground_y), 1)
        for i in range(0, ground_y, 50):
            pygame.draw.line(screen, COLOR_GRID, (0, i), (SCREEN_WIDTH, i), 1)

        # Sol
        pygame.draw.rect(screen, COLOR_GROUND, (0, ground_y, SCREEN_WIDTH, SCREEN_HEIGHT - ground_y))
        pygame.draw.line(screen, (100, 200, 100), (0, ground_y), (SCREEN_WIDTH, ground_y), 8)

        # Clădiri
        for b in buildings: b.draw(screen, ground_x, ground_y)

        # PANOU JOS
        pygame.draw.rect(screen, COLOR_PANEL, (0, panel_y, SCREEN_WIDTH, SCREEN_HEIGHT - panel_y))
        pygame.draw.line(screen, COLOR_WHITE, (0, panel_y), (SCREEN_WIDTH, panel_y), 3)
        
        slider_amp.draw(screen)
        slider_freq.draw(screen)
        btn_start.draw(screen)
        btn_reset.draw(screen)

        # SEISMOGRAF (Unda solului)
        sg_rect = pygame.Rect(450, 580, 280, 180)
        pygame.draw.rect(screen, (20, 25, 30), sg_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_GRAY, sg_rect, 2, border_radius=8)
        pygame.draw.line(screen, (60, 60, 70), (sg_rect.x, sg_rect.centery), (sg_rect.right, sg_rect.centery), 1)
        
        graph_points.append(ground_x)
        if len(graph_points) > 260: graph_points.pop(0)
        if len(graph_points) > 1:
            pts = [(sg_rect.right - (i * 1.05), sg_rect.centery + int(v * 1.5)) 
                   for i, v in enumerate(reversed(graph_points)) if sg_rect.right - (i * 1.05) > sg_rect.x]
            if len(pts) > 1: pygame.draw.lines(screen, COLOR_GREEN, False, pts, 2)
        screen.blit(font_small.render("Seismograf", True, COLOR_TEXT_LIGHT), (sg_rect.x + 10, sg_rect.y + 5))

        # GRAFIC REZONANȚĂ (Nou!)
        draw_resonance_graph(screen, 750, 580, 420, 180, buildings, f)

        # TEXT EDUCAȚIONAL LIVE (Sus)
        omega = 2 * math.pi * f
        a_max = (A * 0.01) * (omega ** 2)
        
        info_txt = f"Simulare Activă | Accelerația maximă a solului: {a_max:.2f} m/s²" if active else "Setați frecvența și apăsați START."
        color_txt = COLOR_WHITE
        
        if active:
            for b in buildings:
                if abs(f - b.f_natural) < 0.25:
                    info_txt = f"RESONANȚĂ DETECTATĂ ({b.f_natural} Hz) -> Distrugere iminentă a clădirii '{b.name}'!"
                    color_txt = COLOR_RED
                    break

        txt_surf = font_large.render(info_txt, True, color_txt)
        pygame.draw.rect(screen, (0,0,0, 150), (10, 10, txt_surf.get_width() + 20, 40), border_radius=5)
        screen.blit(txt_surf, (20, 15))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
