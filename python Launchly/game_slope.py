import pygame
import sys
import math
import random

# --- INIȚIALIZARE ---
pygame.init()
pygame.font.init()

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 820
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Laborator Virtual: Panta Alunecoasă (Frecarea pe Plan Înclinat)")

# Culori Interfață Tech Premium
COLOR_BG = (10, 11, 15)
COLOR_PANEL_BG = (18, 20, 28)
COLOR_PANEL_BORDER = (35, 42, 60)
COLOR_WHITE = (240, 240, 250)
COLOR_TEXT_MUTED = (110, 125, 150)
COLOR_CYAN = (0, 210, 255)
COLOR_GREEN = (140, 255, 100)
COLOR_RED = (255, 75, 75)
COLOR_YELLOW = (255, 200, 50)
COLOR_BLUE = (50, 150, 255)

font_title = pygame.font.SysFont("Segoe UI", 16, bold=True)
font_ui = pygame.font.SysFont("Segoe UI", 13, bold=True)
font_math = pygame.font.SysFont("Consolas", 14)

clock = pygame.time.Clock()
FPS = 60

# --- CLASE PARTICULE ---
class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_life = lifetime

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, surface):
        radius = max(1, int((self.lifetime / self.max_life) * 4))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)

particles = []

# --- CLASE UI ---
class CompactSlider:
    def __init__(self, x, y, w, min_val, max_val, start_val, label, unit="", color=COLOR_CYAN):
        self.rect = pygame.Rect(x, y, w, 6)
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.label = label
        self.unit = unit
        self.color = color
        self.handle_pos = [x, y + 3]
        self.update_handle()
        self.dragging = False

    def update_handle(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_pos[0] = self.rect.x + ratio * self.rect.width

    def set_value(self, new_val):
        self.val = max(self.min_val, min(self.max_val, new_val))
        self.update_handle()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if math.hypot(event.pos[0] - self.handle_pos[0], event.pos[1] - self.handle_pos[1]) <= 12 or self.rect.inflate(0, 12).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pos_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            self.val = self.min_val + ((pos_x - self.rect.x) / self.rect.width) * (self.max_val - self.min_val)
            self.handle_pos[0] = pos_x

    def draw(self, surface):
        pygame.draw.rect(surface, (35, 40, 55), self.rect, border_radius=3)
        if self.handle_pos[0] - self.rect.x > 0:
            pygame.draw.rect(surface, self.color, (self.rect.x, self.rect.y, self.handle_pos[0] - self.rect.x, self.rect.height), border_radius=3)
        pygame.draw.circle(surface, COLOR_WHITE if self.dragging else self.color, (int(self.handle_pos[0]), int(self.handle_pos[1])), 7)
        txt = font_ui.render(f"{self.label}: {self.val:.1f}{self.unit}", True, COLOR_WHITE)
        surface.blit(txt, (self.rect.x, self.rect.y - 20))

class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.active = False

    def draw(self, surface):
        bg_col = self.color if self.active else COLOR_PANEL_BG
        text_col = COLOR_BG if self.active else self.color
        border_col = self.color
        
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=4)
        pygame.draw.rect(surface, border_col, self.rect, 2, border_radius=4)
        
        txt_surf = font_ui.render(self.text, True, text_col)
        surface.blit(txt_surf, (self.rect.centerx - txt_surf.get_width()//2, self.rect.centery - txt_surf.get_height()//2))

# --- FUNCȚII DESENARE VECTORI ---
def draw_vector(surface, start_pos, end_pos, color, scale=1.0):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    length = math.hypot(dx, dy)
    if length < 2: return
    pygame.draw.line(surface, color, start_pos, end_pos, 3)
    angle = math.atan2(dy, dx)
    arrow_len = 10
    p1 = (end_pos[0] - arrow_len * math.cos(angle - math.pi/6), end_pos[1] - arrow_len * math.sin(angle - math.pi/6))
    p2 = (end_pos[0] - arrow_len * math.cos(angle + math.pi/6), end_pos[1] - arrow_len * math.sin(angle + math.pi/6))
    pygame.draw.polygon(surface, color, [end_pos, p1, p2])

# --- LOGICA ȘI STAREA JOCULUI ---
view_sim = pygame.Rect(30, 70, 680, 500)
panel_data = pygame.Rect(30, 590, 680, 200)
panel_controls = pygame.Rect(730, 70, 340, 720)

# Slidere
slider_angle = CompactSlider(760, 230, 280, 0.0, 60.0, 20.0, "Unghi Pantă (θ)", "°", COLOR_CYAN)
slider_mass = CompactSlider(760, 290, 280, 5.0, 50.0, 20.0, "Masă Cutie (m)", " kg", COLOR_YELLOW)
slider_v0 = CompactSlider(760, 350, 280, 1.0, 35.0, 12.0, "Impuls Inițial (v₀)", " m/s", COLOR_GREEN)

# Materiale manuale
btn_mat_ice = Button(760, 130, 90, 30, "GHEAȚĂ", COLOR_CYAN)
btn_mat_wood = Button(860, 130, 90, 30, "LEMN", COLOR_YELLOW)
btn_mat_rubber = Button(960, 130, 90, 30, "CAUCIUC", COLOR_RED)
btn_mat_wood.active = True

# --- BUTOANE SCENARII (3 FAVORABILE / 3 NEFAVORABILE) ---
btn_fav_ice = Button(745, 465, 145, 30, "✔ FAV: Gheață", COLOR_GREEN)
btn_fav_wood = Button(745, 505, 145, 30, "✔ FAV: Lemn", COLOR_GREEN)
btn_fav_rubber = Button(745, 545, 145, 30, "✔ FAV: Cauciuc", COLOR_GREEN)

btn_unfav_ice = Button(910, 465, 145, 30, "❌ NEFAV: Gheață", COLOR_RED)
btn_unfav_wood = Button(910, 505, 145, 30, "❌ NEFAV: Lemn", COLOR_RED)
btn_unfav_rubber = Button(910, 545, 145, 30, "❌ NEFAV: Cauciuc", COLOR_RED)

btn_start = Button(760, 680, 130, 40, "START SIM", COLOR_GREEN)
btn_reset = Button(910, 680, 130, 40, "RESETARE", COLOR_RED)

materials = {
    "GHEAȚĂ": {"mu_s": 0.1, "mu_k": 0.05, "part_color": (200, 240, 255)},
    "LEMN": {"mu_s": 0.4, "mu_k": 0.3, "part_color": (160, 110, 60)},
    "CAUCIUC": {"mu_s": 0.8, "mu_k": 0.6, "part_color": (90, 90, 100)}
}
current_material = "LEMN"

# Constante Fizice
g = 9.81
ramp_length_m = 10.0
pixels_per_m = 45.0
origin_x = view_sim.left + 50
origin_y = view_sim.bottom - 60

state = "IDLE"
pos_s = 0.0
vel = 0.0
message = "Selectează un scenariu stabilizat din cele 6 butoane."
msg_color = COLOR_WHITE

def reset_sim():
    global state, pos_s, vel, message, msg_color, particles
    state = "IDLE"
    pos_s = 0.0
    vel = 0.0
    particles.clear()
    message = "Sistem pregătit. Alege un scenariu sau modifică parametrii."
    msg_color = COLOR_WHITE

def apply_scenario(mat, angle, speed, is_favorable, custom_msg):
    global current_material, state, pos_s, vel, message, msg_color, particles
    current_material = mat
    btn_mat_ice.active = (mat == "GHEAȚĂ")
    btn_mat_wood.active = (mat == "LEMN")
    btn_mat_rubber.active = (mat == "CAUCIUC")
    
    slider_angle.set_value(angle)
    slider_v0.set_value(speed)
    
    pos_s = 0.0
    vel = speed
    state = "UP"
    particles.clear()
    message = custom_msg
    msg_color = COLOR_GREEN if is_favorable else COLOR_RED

def main():
    global current_material, state, pos_s, vel, message, msg_color, particles
    running = True

    while running:
        clock.tick(FPS)
        fixed_dt = 0.0166  # Timp fix determinist
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(COLOR_BG)

        # --- EVENIMENTE ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 
            
            
            if state in ["IDLE", "STOPPED", "WIN", "CRASH", "LOSS_SLIDE"]:
                slider_angle.handle_event(event)
                slider_mass.handle_event(event)
                slider_v0.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state in ["IDLE", "STOPPED", "WIN", "CRASH", "LOSS_SLIDE"]:
                    if btn_mat_ice.rect.collidepoint(mouse_pos): current_material = "GHEAȚĂ"; btn_mat_ice.active = True; btn_mat_wood.active = False; btn_mat_rubber.active = False
                    elif btn_mat_wood.rect.collidepoint(mouse_pos): current_material = "LEMN"; btn_mat_ice.active = False; btn_mat_wood.active = True; btn_mat_rubber.active = False
                    elif btn_mat_rubber.rect.collidepoint(mouse_pos): current_material = "CAUCIUC"; btn_mat_ice.active = False; btn_mat_wood.active = False; btn_mat_rubber.active = True

                    
                    if btn_fav_ice.rect.collidepoint(mouse_pos):
                        apply_scenario("GHEAȚĂ", 15.0, 7.8, True, "✔ CAZ FAVORABIL GHEAȚĂ: Frecare redusă, ajunge sigur în camion!")
                    elif btn_unfav_ice.rect.collidepoint(mouse_pos):
                        apply_scenario("GHEAȚĂ", 15.0, 3.0, False, "❌ CAZ NEFAVORABIL GHEAȚĂ: Impuls prea mic, alunecă înapoi la bază.")

                    elif btn_fav_wood.rect.collidepoint(mouse_pos):
                        apply_scenario("LEMN", 20.0, 11.2, True, "✔ CAZ FAVORABIL LEMN: Viteza învinge frecarea medie.")
                    elif btn_unfav_wood.rect.collidepoint(mouse_pos):
                        apply_scenario("LEMN", 12.0, 4.5, False, "❌ CAZ NEFAVORABIL LEMN: Cutia se oprește și încremenește pe pantă.")

                    elif btn_fav_rubber.rect.collidepoint(mouse_pos):
                        
                        apply_scenario("CAUCIUC", 25.0, 14, True, "✔ CAZ FAVORABIL CAUCIUC: Impuls masiv calculat pentru a penetra aderența!")
                    elif btn_unfav_rubber.rect.collidepoint(mouse_pos):
                        apply_scenario("CAUCIUC", 40.0, 8.0, False, "❌ CAZ NEFAVORABIL CAUCIUC: Panta abruptă + Aderența maximă opresc cutia imediat.")

                if btn_start.rect.collidepoint(mouse_pos) and state in ["IDLE", "STOPPED", "WIN", "CRASH", "LOSS_SLIDE"]:
                    reset_sim()
                    vel = slider_v0.val
                    state = "UP"
                    message = "Simulare manuală pornită..."
                    msg_color = COLOR_CYAN
                
                if btn_reset.rect.collidepoint(mouse_pos):
                    reset_sim()

        # --- LOGICA FIZICĂ (SIGURĂ LA CADRU) ---
        theta_rad = math.radians(slider_angle.val)
        m = slider_mass.val
        mu_s = materials[current_material]["mu_s"]
        mu_k = materials[current_material]["mu_k"]

        G = m * g
        Gx = G * math.sin(theta_rad)
        Gy = G * math.cos(theta_rad)
        N = Gy
        Ff_max = mu_s * N
        Ffk = mu_k * N

        sim_speed = 1.3
        eff_dt = fixed_dt * sim_speed

        if state in ["UP", "DOWN"]:
            b_bot_x = origin_x + pos_s * pixels_per_m * math.cos(theta_rad)
            b_bot_y = origin_y - pos_s * pixels_per_m * math.sin(theta_rad)
            if random.random() < 0.5:
                particles.append(Particle(b_bot_x, b_bot_y, random.uniform(-1, 1), random.uniform(-2, 0), materials[current_material]["part_color"], random.randint(15, 30)))

        if state == "UP":
            a_up = -g * (math.sin(theta_rad) + mu_k * math.cos(theta_rad))
            
            # Actualizăm poziția în avans
            next_pos = pos_s + vel * eff_dt
            
            # VERIFICARE SOSIRE ÎNAINTE DE VERIFICAREA VITEZEI ZERO
            if next_pos >= ramp_length_m:
                pos_s = ramp_length_m
                if vel <= 4.5: 
                    state = "WIN"
                    message = f"SUCCES! Încărcare reușită la destinație! (Viteză finală: {vel:.2f} m/s)"
                    msg_color = COLOR_GREEN
                else:
                    state = "CRASH"
                    message = f"CRASH! Cutia a izbit violent platforma camionului ({vel:.2f} m/s)!"
                    msg_color = COLOR_RED
            else:
                pos_s = next_pos
                vel += a_up * eff_dt
                
                if vel <= 0:
                    vel = 0
                    if Gx > Ff_max:
                        state = "DOWN"
                        message = "Viteza s-a epuizat. Greutatea (Gx) trage cutia înapoi jos!"
                        msg_color = COLOR_YELLOW
                    else:
                        state = "STOPPED"
                        message = "Frecare Statică Ridicată: Cutia s-a oprit definitiv pe rampă."
                        msg_color = COLOR_CYAN

        elif state == "DOWN":
            a_down = -g * (math.sin(theta_rad) - mu_k * math.cos(theta_rad))
            vel += a_down * eff_dt
            pos_s += vel * eff_dt

            if pos_s <= 0:
                pos_s = 0
                vel = 0
                state = "LOSS_SLIDE"
                message = "EȘEC: Cutia s-a prăbușit înapoi la baza planului înclinat."
                msg_color = COLOR_RED

        # --- REZOLVARE PARTICULE ---
        for p in particles[:]:
            p.update()
            if p.lifetime <= 0: particles.remove(p)

        # --- RANDARE GRAFICĂ ---
        pygame.draw.rect(screen, COLOR_PANEL_BG, view_sim, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, view_sim, 1, border_radius=6)
        screen.blit(font_title.render("ZONA EXPERIMENTALA (PLAN ÎNCLINAT)", True, COLOR_WHITE), (45, 85))

        # Panta
        ramp_end_x = origin_x + ramp_length_m * pixels_per_m * math.cos(theta_rad)
        ramp_end_y = origin_y - ramp_length_m * pixels_per_m * math.sin(theta_rad)
        pygame.draw.polygon(screen, (32, 38, 52), [(origin_x, origin_y), (ramp_end_x, origin_y), (ramp_end_x, ramp_end_y)])
        pygame.draw.line(screen, COLOR_WHITE, (origin_x, origin_y), (ramp_end_x, ramp_end_y), 4)

        # Camion
        truck_col = COLOR_GREEN if state == "WIN" else COLOR_CYAN
        pygame.draw.rect(screen, truck_col, (ramp_end_x, ramp_end_y - 12, 110, 12), border_radius=2)
        pygame.draw.rect(screen, truck_col, (ramp_end_x + 80, ramp_end_y - 45, 40, 45), border_radius=4)
        pygame.draw.rect(screen, COLOR_PANEL_BG, (ramp_end_x + 90, ramp_end_y - 40, 25, 20))
        pygame.draw.circle(screen, (50, 50, 50), (int(ramp_end_x + 20), int(ramp_end_y + 10)), 12)
        pygame.draw.circle(screen, (50, 50, 50), (int(ramp_end_x + 90), int(ramp_end_y + 10)), 12)
        
        for p in particles: p.draw(screen)

        # Cutie
        box_size = 40
        b_bot_x = origin_x + pos_s * pixels_per_m * math.cos(theta_rad)
        b_bot_y = origin_y - pos_s * pixels_per_m * math.sin(theta_rad)
        cx = b_bot_x - (box_size/2) * math.sin(theta_rad)
        cy = b_bot_y - (box_size/2) * math.cos(theta_rad)

        corners = [(-20, -20), (20, -20), (20, 20), (-20, 20)]
        rotated_corners = []
        for x, y in corners:
            rx = x * math.cos(-theta_rad) - y * math.sin(-theta_rad)
            ry = x * math.sin(-theta_rad) + y * math.cos(-theta_rad)
            rotated_corners.append((cx + rx, cy + ry))
        
        box_color = (170, 130, 80) if current_material == "LEMN" else (190, 220, 245) if current_material == "GHEAȚĂ" else (60, 60, 65)
        pygame.draw.polygon(screen, box_color, rotated_corners)
        pygame.draw.polygon(screen, COLOR_WHITE, rotated_corners, 2)

        # Vectori Forțe
        scale_f = min(100.0 / G, 1.4) if G > 0 else 1.0 
        draw_vector(screen, (cx, cy), (cx, cy + G * scale_f), COLOR_GREEN)
        draw_vector(screen, (cx, cy), (cx - N * scale_f * math.sin(theta_rad), cy - N * scale_f * math.cos(theta_rad)), COLOR_BLUE)

        f_vec = Ffk if state in ["UP", "DOWN"] else min(Gx, Ff_max)
        if state == "UP":
            draw_vector(screen, (cx, cy), (cx - f_vec * scale_f * math.cos(theta_rad), cy + f_vec * scale_f * math.sin(theta_rad)), COLOR_RED)
        else:
            draw_vector(screen, (cx, cy), (cx + f_vec * scale_f * math.cos(theta_rad), cy - f_vec * scale_f * math.sin(theta_rad)), COLOR_RED)

        # --- PANOU INFORMATIV ---
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_data, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_data, 1, border_radius=6)
        screen.blit(font_title.render("TELEMETRIE SENSORI REALA", True, COLOR_CYAN), (45, 605))

        lines = [
            f"Greutate (G) = {G:.1f} N  | Gx (paralel) = {Gx:.1f} N  | Gy (normal) = {Gy:.1f} N",
            f"Ff_max (Statica) = {Ff_max:.1f} N  | Ffk (Cinetica Activa) = {Ffk:.1f} N",
            f"-----------------------------------------------------------------------------",
            f"Pozitie cutie: {pos_s:.2f} m / {ramp_length_m} m  | Viteza instantanee: {vel:.2f} m/s"
        ]
        for idx, line in enumerate(lines):
            screen.blit(font_math.render(line, True, COLOR_WHITE), (45, 640 + idx * 22))

        # Alerte Globale Superior
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, (30, 20, 1040, 40), border_radius=4)
        screen.blit(font_ui.render(message, True, msg_color), (45, 31))

        # --- PANOU CONTROALE (DREAPTA) ---
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_controls, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_controls, 1, border_radius=6)
        
        screen.blit(font_title.render("PANOU DE CONTROL INTERACTIV", True, COLOR_WHITE), (760, 80))
        screen.blit(font_ui.render("1. Selectie Material Manual:", True, COLOR_TEXT_MUTED), (760, 105))
        btn_mat_ice.draw(screen); btn_mat_wood.draw(screen); btn_mat_rubber.draw(screen)
        
        screen.blit(font_ui.render("2. Ajustare Parametri:", True, COLOR_TEXT_MUTED), (760, 200))
        slider_angle.draw(screen)
        slider_mass.draw(screen)
        slider_v0.draw(screen)

        screen.blit(font_ui.render("3. Scenarii de Laborator Fixate:", True, COLOR_TEXT_MUTED), (750, 435))
        btn_fav_ice.draw(screen); btn_unfav_ice.draw(screen)
        btn_fav_wood.draw(screen); btn_unfav_wood.draw(screen)
        btn_fav_rubber.draw(screen); btn_unfav_rubber.draw(screen)
        
        pygame.draw.line(screen, COLOR_PANEL_BORDER, (760, 650), (1040, 650), 1)
        btn_start.draw(screen)
        btn_reset.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
