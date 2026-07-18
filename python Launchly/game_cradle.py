import pygame
import math
import sys

# --- INIȚIALIZARE ---
pygame.init()
pygame.font.init()

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Laborator de Fizică Avansat: Ciocniri Multiple de Penduli")

# Culori Premium
COLOR_BG = (10, 11, 15)
COLOR_PANEL_BG = (18, 20, 28)
COLOR_PANEL_BORDER = (35, 42, 60)
COLOR_WHITE = (240, 240, 250)
COLOR_TEXT_MUTED = (90, 105, 130)
COLOR_SLIDER_BG = (35, 40, 55)
COLOR_BUTTON_BG = (28, 32, 45)
COLOR_BUTTON_HOVER = (45, 52, 75)

font_title = pygame.font.SysFont("Segoe UI", 16, bold=True)
font_ui = pygame.font.SysFont("Segoe UI", 12, bold=True)
font_math = pygame.font.SysFont("Consolas", 13)

clock = pygame.time.Clock()
FPS = 60

# --- SLIDER COMPACT ---
class CompactSlider:
    def __init__(self, x, y, w, min_val, max_val, start_val, label, unit="", color=(0, 210, 255)):
        self.rect = pygame.Rect(x, y, w, 5)
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.label = label
        self.unit = unit
        self.color = color
        self.handle_radius = 6
        self.handle_pos = [x, y + 2]
        self.update_handle()
        self.dragging = False

    def update_handle(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_pos[0] = self.rect.x + ratio * self.rect.width

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if math.hypot(event.pos[0] - self.handle_pos[0], event.pos[1] - self.handle_pos[1]) <= 10 or self.rect.inflate(0, 10).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pos_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            self.val = self.min_val + ((pos_x - self.rect.x) / self.rect.width) * (self.max_val - self.min_val)
            self.handle_pos[0] = pos_x

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_SLIDER_BG, self.rect, border_radius=2)
        if self.handle_pos[0] - self.rect.x > 0:
            pygame.draw.rect(surface, self.color, (self.rect.x, self.rect.y, self.handle_pos[0] - self.rect.x, self.rect.height), border_radius=2)
        pygame.draw.circle(surface, COLOR_WHITE if self.dragging else self.color, (int(self.handle_pos[0]), int(self.handle_pos[1])), self.handle_radius)
        txt = font_ui.render(f"{self.label}: {self.val:.2f} {self.unit}", True, COLOR_WHITE)
        surface.blit(txt, (self.rect.x, self.rect.y - 18))

# --- CONFIGURAȚIE CASETE ---
sim_box = pygame.Rect(30, 80, 964, 380)

slider_balls = CompactSlider(30, 495, 200, 3.0, 8.0, 5.0, "Număr de Bile", "")
slider_gravity = CompactSlider(260, 495, 200, 5.0, 25.0, 9.81, "Gravitație (g)", "m/s²", (150, 255, 100))
slider_elasticity = CompactSlider(490, 495, 200, 0.85, 1.0, 0.99, "Coeficient Restituire (e)", "", (255, 150, 50))

btn_reset = pygame.Rect(720, 483, 110, 30)
btn_pull2 = pygame.Rect(845, 483, 150, 30)

# --- CLASA NEWTON BALL ---
class NewtonBall:
    def __init__(self, anchor_x, anchor_y, length, radius, id_index):
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.length = length
        self.radius = radius
        self.id = id_index
        
        self.angle = 0.0      
        self.vel = 0.0        
        self.x = anchor_x
        self.y = anchor_y + length
        self.is_dragged = False

    def update_position(self):
        self.x = self.anchor_x + self.length * math.sin(self.angle)
        self.y = self.anchor_y + self.length * math.cos(self.angle)

    def update_physics(self, dt, g):
        if self.is_dragged:
            self.vel = 0.0
            return
        acc = -(g / self.length) * math.sin(self.angle)
        self.vel += acc * dt
        self.angle += self.vel * dt
        self.update_position()

balls = []
BALL_RADIUS = 24

def reset_simulation():
    global balls
    balls = []
    num_balls = int(slider_balls.val)
    
    total_w = (num_balls - 1) * (BALL_RADIUS * 2)
    start_x = sim_box.centerx - total_w // 2
    anchor_y = sim_box.y + 40
    length = 220
    
    for i in range(num_balls):
        ax = start_x + i * (BALL_RADIUS * 2)
        ball = NewtonBall(ax, anchor_y, length, BALL_RADIUS, i)
        ball.update_position()
        balls.append(ball)

reset_simulation()

def main():
    global balls
    running = True
    dragged_group = []  # Reține indicii bilesor care sunt trase simultan
    drag_side = None    # "left" sau "right" pentru a ști cum grupăm restul bilelor

    while running:
        real_dt = min(clock.tick(FPS) / 1000.0, 0.02)
        mouse_pos = pygame.mouse.get_pos()
        num_balls_old = int(slider_balls.val)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # --- ADAUGĂ ACEST BLOC ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            # -------------------------
            
            slider_balls.handle_event(event)
            slider_gravity.handle_event(event)
            slider_elasticity.handle_event(event)

            if int(slider_balls.val) != num_balls_old:
                reset_simulation()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if btn_reset.collidepoint(event.pos):
                        reset_simulation()
                    elif btn_pull2.collidepoint(event.pos):
                        reset_simulation()
                        # Lansare automată cu DOUĂ bile deodată
                        balls[0].angle = math.radians(-45)
                        balls[1].angle = math.radians(-45)
                        balls[0].update_position()
                        balls[1].update_position()
                    else:
                        # Verificăm ce bilă a fost selectată cu mouse-ul
                        for idx, b in enumerate(balls):
                            if math.hypot(event.pos[0] - b.x, event.pos[1] - b.y) <= b.radius:
                                mid = len(balls) / 2
                                # Determinăm dacă tragem din grupul din stânga sau dreapta
                                if idx < mid:
                                    drag_side = "left"
                                    dragged_group = list(range(0, idx + 1)) # Ia bila curentă și tot ce e la stânga ei
                                else:
                                    drag_side = "right"
                                    dragged_group = list(range(idx, len(balls))) # Ia bila curentă și tot ce e la dreapta ei
                                
                                for g_idx in dragged_group:
                                    balls[g_idx].is_dragged = True
                                break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragged_group:
                    for g_idx in dragged_group:
                        balls[g_idx].is_dragged = False
                    dragged_group = []
                    drag_side = None

        # --- MODIFICARE UNGHI PENTRU TOATĂ GRUPA ---
        if dragged_group:
            # Luăm ca referință de unghi poziția mouse-ului față de ancora bilei pe care s-a dat efectiv click
            ref_ball = balls[dragged_group[-1]] if drag_side == "left" else balls[dragged_group[0]]
            dx = mouse_pos[0] - ref_ball.anchor_x
            dy = mouse_pos[1] - ref_ball.anchor_y
            target_angle = max(-math.pi/2.5, min(math.pi/2.5, math.atan2(dx, dy)))
            
            # Toate bilele din grup se vor mișca sincronizat la același unghi
            for g_idx in dragged_group:
                balls[g_idx].angle = target_angle
                balls[g_idx].update_position()

        # --- MOTOR FIZIC (SUB-STEPPING) ---
        sub_steps = 6
        dt = (real_dt / sub_steps) * 2.2  
        g_val = slider_gravity.val
        e_coef = slider_elasticity.val

        for _ in range(sub_steps):
            for b in balls:
                b.update_physics(dt, g_val)

            # Rezolvare coliziuni și transfer de impuls de la stânga la dreapta
            for i in range(len(balls) - 1):
                b1 = balls[i]
                b2 = balls[i+1]
                
                dist = math.hypot(b2.x - b1.x, b2.y - b1.y)
                min_dist = b1.radius + b2.radius
                
                if dist < min_dist:
                    v1 = b1.vel * b1.length
                    v2 = b2.vel * b2.length
                    
                    v_relative = v1 - v2
                    if v_relative > 0:
                        # Ecuațiile conservării impulsului pentru mase egale
                        v1_new = (v1 * (1 - e_coef) + v2 * (1 + e_coef)) / 2
                        v2_new = (v1 * (1 + e_coef) + v2 * (1 - e_coef)) / 2
                        
                        b1.vel = v1_new / b1.length
                        b2.vel = v2_new / b2.length
                    
                    # Corecție geometrică anti-suprapunere
                    overlap = min_dist - dist
                    if not b1.is_dragged:
                        b1.angle -= (overlap * 0.5) / b1.length
                        b1.update_position()
                    if not b2.is_dragged:
                        b2.angle += (overlap * 0.5) / b2.length
                        b2.update_position()

        # --- RENDERING ---
        screen.fill(COLOR_BG)
        
        screen.blit(font_title.render("SISTEM AVANSAT: TRAGERE ȘI PROPAGARE DE GRUPURI MULTIPLE", True, (0, 210, 255)), (30, 25))
        pygame.draw.rect(screen, COLOR_PANEL_BG, sim_box, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, sim_box, 1, border_radius=6)

        if len(balls) > 0:
            pygame.draw.line(screen, (70, 80, 95), (balls[0].anchor_x - 40, balls[0].anchor_y), (balls[-1].anchor_x + 40, balls[-1].anchor_y), 6)

        for b in balls:
            pygame.draw.line(screen, (80, 90, 110), (b.anchor_x, b.anchor_y), (int(b.x), int(b.y)), 1)
            # Dacă bila este selectată / trasă în acel moment, o luminăm ușor în cyan
            color_base = (0, 190, 230) if b.is_dragged else (160, 170, 185)
            pygame.draw.circle(screen, color_base, (int(b.x), int(b.y)), b.radius)
            pygame.draw.circle(screen, (100, 110, 125), (int(b.x), int(b.y)), b.radius, 2)
            pygame.draw.circle(screen, (245, 245, 255), (int(b.x) - 6, int(b.y) - 6), 4)

        pygame.draw.line(screen, COLOR_PANEL_BORDER, (0, 455), (1024, 455), 1)
        slider_balls.draw(screen)
        slider_gravity.draw(screen)
        slider_elasticity.draw(screen)

        # Buton Reset
        m_hover1 = btn_reset.collidepoint(mouse_pos)
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if m_hover1 else COLOR_BUTTON_BG, btn_reset, border_radius=4)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, btn_reset, 1, border_radius=4)
        screen.blit(font_ui.render("RESETĂ", True, COLOR_WHITE), (btn_reset.centerx - 22, btn_reset.centery - 8))

        # Buton Lansare Automată (2 Bile)
        m_hover2 = btn_pull2.collidepoint(mouse_pos)
        pygame.draw.rect(screen, COLOR_BUTTON_HOVER if m_hover2 else COLOR_BUTTON_BG, btn_pull2, border_radius=4)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, btn_pull2, 1, border_radius=4)
        screen.blit(font_ui.render("LANSARE (2 BILE)", True, (0, 210, 255)), (btn_pull2.centerx - 52, btn_pull2.centery - 8))

        # Panou Informative Live
        info_rect = pygame.Rect(30, 560, 964, 120)
        pygame.draw.rect(screen, COLOR_PANEL_BG, info_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, info_rect, 1, border_radius=6)

        text_lines = [
            "  [CONTROL NOU] Dă click pe A DOUA sau A TREIA bilă dintr-un capăt: codul va ridica automat tot blocul exterior.",
            "  [FĂ EXPERIMENTUL]: Trage de 2 bile din stânga și dă-le drumul. Vei vedea cum exact 2 bile vor pleca din extrema dreaptă!",
            "  [INDICAȚIE]: Acest fenomen demonstrează că sistemul își 'amintește' nu doar energia, ci și distribuția masei în mișcare.",
            "  * Algoritmul împarte dinamic indicii (0 -> selectat) sau (selectat -> capăt) în funcție de zona de ecran atinsă."
        ]
        for idx, line in enumerate(text_lines):
            c = (0, 210, 255) if idx == 1 else (COLOR_WHITE if idx == 0 else COLOR_TEXT_MUTED)
            screen.blit(font_math.render(line, True, c), (45, 575 + idx * 24))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
