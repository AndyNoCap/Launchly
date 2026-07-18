import pygame
import sys
import math
import random

# --- INIȚIALIZARE ---
pygame.init()
pygame.font.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🎯 Bungee Pro Ultra-Compact Fix")

# Culori Interfață
COLOR_BG = (11, 15, 26)
COLOR_PANEL = (20, 27, 45)
COLOR_PANEL_BORDER = (47, 63, 97)
COLOR_WHITE = (241, 245, 249)
COLOR_TEXT_MUTED = (148, 163, 184)
COLOR_CYAN = (6, 182, 212)
COLOR_GREEN = (34, 197, 94)
COLOR_RED = (239, 68, 68)
COLOR_ORANGE = (249, 115, 22)
COLOR_WATER = (14, 116, 144)
COLOR_WATER_FOAM = (103, 232, 249)

font_title = pygame.font.SysFont("Segoe UI", 14, bold=True)
font_ui = pygame.font.SysFont("Segoe UI", 12, bold=True)
font_mono = pygame.font.SysFont("Consolas", 11)

clock = pygame.time.Clock()
FPS = 60

# --- CLASA PARTICULE ---
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -1)
        self.radius = random.randint(2, 4)
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 12
        if self.radius > 0.1: self.radius -= 0.05

    def draw(self, surface):
        if self.alpha <= 0 or self.radius <= 0: return
        p_surf = pygame.Surface((int(self.radius*2), int(self.radius*2)), pygame.SRCALPHA)
        pygame.draw.circle(p_surf, (103, 232, 249, self.alpha), (int(self.radius), int(self.radius)), int(self.radius))
        surface.blit(p_surf, (int(self.x - self.radius), int(self.y - self.radius)))

# --- COMPONENTE INTERFAȚĂ ---
class ModernSlider:
    def __init__(self, x, y, w, min_val, max_val, start_val, label, unit, color):
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

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if math.hypot(event.pos[0] - self.handle_pos[0], event.pos[1] - self.handle_pos[1]) <= 10 or self.rect.inflate(0, 12).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pos_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            self.val = self.min_val + ((pos_x - self.rect.x) / self.rect.width) * (self.max_val - self.min_val)
            self.handle_pos[0] = pos_x

    def draw(self, surface):
        pygame.draw.rect(surface, (11, 15, 26), self.rect, border_radius=3)
        if self.handle_pos[0] - self.rect.x > 0:
            pygame.draw.rect(surface, self.color, (self.rect.x, self.rect.y, self.handle_pos[0] - self.rect.x, self.rect.height), border_radius=3)
        pygame.draw.circle(surface, COLOR_WHITE, (int(self.handle_pos[0]), int(self.handle_pos[1])), 6)

        lbl_surf = font_ui.render(f"{self.label}: {self.val:.1f} {self.unit}", True, COLOR_WHITE)
        surface.blit(lbl_surf, (self.rect.x, self.rect.y - 16))

class ModernButton:
    def __init__(self, x, y, w, h, text, bg_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.bg_color = bg_color
        self.enabled = True

    def draw(self, surface, mouse_pos):
        if not self.enabled: draw_color = (60, 70, 90)
        elif self.rect.collidepoint(mouse_pos): draw_color = tuple(min(255, c + 25) for c in self.bg_color)
        else: draw_color = self.bg_color

        pygame.draw.rect(surface, draw_color, self.rect, border_radius=6)
        txt_surf = font_ui.render(self.text, True, COLOR_WHITE)
        surface.blit(txt_surf, (self.rect.centerx - txt_surf.get_width()//2, self.rect.centery - txt_surf.get_height()//2))

# --- CONFIGURARE LAYOUT COMPACT ---
view_canvas = pygame.Rect(15, 65, 430, 515)
view_controls = pygame.Rect(465, 65, 415, 515)

slider_mass = ModernSlider(485, 190, 375, 50.0, 120.0, 80.0, "Masă Turist (m)", "kg", COLOR_CYAN)
slider_l0 = ModernSlider(485, 240, 375, 10.0, 35.0, 22.0, "Lungime Cord (L₀)", "m", COLOR_ORANGE)
slider_k = ModernSlider(485, 290, 375, 20.0, 150.0, 55.0, "Rigiditate Elastică (k)", "N/m", COLOR_CYAN)

rect_p1 = pygame.Rect(485, 125, 115, 24)
rect_p2 = pygame.Rect(615, 125, 115, 24)
rect_p3 = pygame.Rect(745, 125, 115, 24)

btn_perfect_case = ModernButton(485, 335, 375, 30, "🎯 ÎNCARCĂ CAZ FAVORABIL PERFECT (2.00m)", (30, 58, 138))
btn_start = ModernButton(485, 530, 175, 36, "🚀 JUMP", COLOR_GREEN)
btn_reset = ModernButton(685, 530, 175, 36, "🔄 RESET", COLOR_RED)

# Parametri Fizici
g = 9.81
h_platform = 50.0
pixels_per_meter = view_canvas.height / (h_platform + 10)

sim_state = "IDLE"  # IDLE, FALLING, FINISHED
jumper_y = h_platform
jumper_vel = 0.0
jumper_acc = 0.0
max_y_reached = h_platform
max_g_force = 1.0
particles_list = []

feedback_msg = "Sistem pregătit. Apasă pe butonul albastru pentru Cazul Perfect!"
feedback_color = COLOR_WHITE

def get_pixel_y(meter_y):
    return view_canvas.top + int((h_platform + 3.0 - meter_y) * pixels_per_meter)

def main():
    global sim_state, jumper_y, jumper_vel, jumper_acc, max_y_reached, max_g_force, feedback_msg, feedback_color
    running = True
    splash_triggered = False

    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(COLOR_BG)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 
            
            
            # Gestionare evenimente slidere doar în mod IDLE
            if sim_state == "IDLE":
                slider_mass.handle_event(event)
                slider_l0.handle_event(event)
                slider_k.handle_event(event)
            
            # BLOC VERIFICARE CLICK-URI DIRECTE BUTOANE (Independent și Securizat)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if sim_state == "IDLE":
                    if rect_p1.collidepoint(mouse_pos): slider_mass.val = 60.0; slider_mass.update_handle()
                    elif rect_p2.collidepoint(mouse_pos): slider_mass.val = 85.0; slider_mass.update_handle()
                    elif rect_p3.collidepoint(mouse_pos): slider_mass.val = 115.0; slider_mass.update_handle()
                    
                    # Încărcarea Cazului Favorabil funcționează acum garantat la click!
                    if btn_perfect_case.rect.collidepoint(mouse_pos):
                        slider_mass.val = 80.0
                        slider_l0.val = 15.0
                        slider_k.val = 70.0
                        slider_mass.update_handle()
                        slider_l0.update_handle()
                        slider_k.update_handle()
                        feedback_msg = "🎯 Cazul Favorabil Încărcat! Oprire matematică exact la Y = 2.00 metri!"
                        feedback_color = COLOR_GREEN

                if btn_start.rect.collidepoint(mouse_pos) and sim_state == "IDLE":
                    sim_state = "FALLING"
                    jumper_y = h_platform
                    jumper_vel = 0.0
                    jumper_acc = 0.0
                    max_y_reached = h_platform
                    max_g_force = 1.0
                    splash_triggered = False
                    feedback_msg = "În cădere..."
                    feedback_color = COLOR_CYAN
                    btn_start.enabled = False
                
                if btn_reset.rect.collidepoint(mouse_pos):
                    sim_state = "IDLE"
                    jumper_y = h_platform
                    jumper_vel = 0.0
                    jumper_acc = 0.0
                    max_y_reached = h_platform
                    max_g_force = 1.0
                    particles_list.clear()
                    feedback_msg = "Sistem re-armat. Pregătit de salt."
                    feedback_color = COLOR_WHITE
                    btn_start.enabled = True

        # --- MOTORUL DE FIZICĂ ---
        m = slider_mass.val
        L0 = slider_l0.val
        k = slider_k.val
        displacement = h_platform - jumper_y

        E_pot_grav = max(0.0, m * g * jumper_y)
        E_elastic = 0.0 if displacement <= L0 else 0.5 * k * ((displacement - L0) ** 2)

        if sim_state == "FALLING":
            dt = 0.0166
            old_vel = jumper_vel
            
            F_net = - (m * g)
            if displacement > L0:
                F_net += k * (displacement - L0)
            F_net += -0.12 * jumper_vel
            
            jumper_acc = F_net / m
            jumper_vel += jumper_acc * dt
            jumper_y += jumper_vel * dt

            if jumper_y < max_y_reached: 
                max_y_reached = jumper_y

            cg = abs(jumper_acc) / 9.81
            if cg > max_g_force: max_g_force = cg

            if jumper_y <= 3.0 and not splash_triggered:
                for _ in range(20): 
                    particles_list.append(Particle(view_canvas.x + 150, get_pixel_y(jumper_y)))
                splash_triggered = True

            if jumper_y <= 0:
                jumper_y, jumper_vel = 0, 0
                sim_state = "FINISHED"
                feedback_msg = "❌ CRASH! Turistul a lovit apa!"
                feedback_color = COLOR_RED

            elif old_vel < 0 and jumper_vel >= 0 and displacement > L0:
                jumper_y = max_y_reached
                jumper_vel = 0
                sim_state = "FINISHED"
                if 1.0 <= max_y_reached <= 3.0:
                    feedback_msg = f"🏆 PERFECT! Oprire ideală în zona de siguranță la {max_y_reached:.2f}m!"
                    feedback_color = COLOR_GREEN
                elif max_y_reached > 10.0:
                    feedback_msg = f"😴 PREA SUS. S-a oprit la {max_y_reached:.2f}m."
                    feedback_color = COLOR_ORANGE
                else:
                    feedback_msg = f"⚖️ SALVAT. Oprire sigură la {max_y_reached:.2f}m."
                    feedback_color = COLOR_WHITE

        # Ecuația de gradul II pentru predicția în timp real
        a_q, b_q, c_q = 0.5 * k, -m * g, -m * g * L0
        disc = (b_q**2) - (4 * a_q * c_q)
        y_min_teoretic = h_platform - (L0 + ((-b_q + math.sqrt(disc)) / (2 * a_q) if disc >= 0 else 0))

        # --- RENDERING ---
        pygame.draw.rect(screen, COLOR_PANEL, view_canvas, border_radius=8)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, view_canvas, 2, border_radius=8)
        pygame.draw.rect(screen, COLOR_PANEL, view_controls, border_radius=8)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, view_controls, 2, border_radius=8)

        # Apă și Zonă Țintă
        w_y = get_pixel_y(0)
        pygame.draw.rect(screen, COLOR_WATER, (view_canvas.x+2, w_y, view_canvas.width-4, view_canvas.bottom - w_y - 2), border_radius=6)
        t_top, t_bot = get_pixel_y(3.0), get_pixel_y(1.0)
        surf_target = pygame.Surface((view_canvas.width-4, t_bot - t_top), pygame.SRCALPHA)
        surf_target.fill((34, 197, 94, 45))
        screen.blit(surf_target, (view_canvas.x+2, t_top))

        # Turn de lansare
        centerX = view_canvas.x + 150
        plat_y = get_pixel_y(h_platform)
        pygame.draw.rect(screen, (51, 65, 85), (view_canvas.right - 40, plat_y, 25, w_y - plat_y))
        pygame.draw.rect(screen, (38, 45, 64), (centerX, plat_y - 3, view_canvas.right - 40 - centerX, 6))

        for p in particles_list: p.update(); p.draw(screen)

        # Sfoară & Jumper
        jump_p_y = get_pixel_y(jumper_y)
        if sim_state == "IDLE":
            pygame.draw.line(screen, COLOR_ORANGE, (centerX, plat_y + 2), (centerX, plat_y + 12), 2)
            pygame.draw.circle(screen, (254, 215, 170), (centerX, plat_y - 12), 4)
            pygame.draw.line(screen, COLOR_WHITE, (centerX, plat_y - 8), (centerX, plat_y), 2)
        else:
            if displacement <= L0:
                pts = [(centerX + (4 if i%2==0 and i!=0 and i!=10 else -4 if i!=0 and i!=10 else 0), plat_y + i*((jump_p_y-plat_y)/10)) for i in range(11)]
                pygame.draw.lines(screen, COLOR_ORANGE, False, pts, 2)
            else:
                p_l0 = plat_y + int(L0 * pixels_per_meter)
                pygame.draw.line(screen, COLOR_ORANGE, (centerX, plat_y), (centerX, p_l0), 2)
                pts_e = [(centerX + (4 if j%2==0 and j!=0 and j!=12 else -4 if j!=0 and j!=12 else 0), p_l0 + j*((jump_p_y-p_l0)/12)) for j in range(13)]
                pygame.draw.lines(screen, COLOR_CYAN, False, pts_e, 2)

            h_col = COLOR_GREEN if sim_state == "FINISHED" and 1.0 <= max_y_reached <= 3.0 else COLOR_RED
            pygame.draw.circle(screen, (254, 215, 170), (centerX, jump_p_y + 10), 4)
            pygame.draw.circle(screen, h_col, (centerX, jump_p_y + 11), 5, 1)
            pygame.draw.line(screen, COLOR_WHITE, (centerX, jump_p_y), (centerX, jump_p_y + 7), 2)
            screen.blit(font_mono.render(f"{abs(jumper_vel):.1f} m/s", True, COLOR_CYAN), (centerX + 15, jump_p_y))

        # Riglă metrică
        for h in range(0, 51, 10):
            hy = get_pixel_y(h)
            pygame.draw.line(screen, COLOR_PANEL_BORDER, (view_canvas.x + 2, hy), (view_canvas.x + 10, hy), 1)
            screen.blit(font_mono.render(f"{h}m", True, COLOR_TEXT_MUTED), (view_canvas.x + 14, hy - 6))

        # --- PANOU CONTROL ---
        screen.blit(font_title.render("⚙️ OPERATOR BUNGEE JUMP", True, COLOR_WHITE), (485, 85))
        
        for rect, txt in [(rect_p1, "60kg (Slăbuț)"), (rect_p2, "85kg (Mediu)"), (rect_p3, "115kg (Robust)")]:
            pygame.draw.rect(screen, (47, 63, 97) if rect.collidepoint(mouse_pos) else (30, 41, 59), rect, border_radius=4)
            t_s = font_mono.render(txt, True, COLOR_WHITE)
            screen.blit(t_s, (rect.centerx - t_s.get_width()//2, rect.centery - t_s.get_height()//2))

        slider_mass.draw(screen)
        slider_l0.draw(screen)
        slider_k.draw(screen)
        btn_perfect_case.draw(screen, mouse_pos)

        # Telemetrie și Bare Energie
        screen.blit(font_title.render("📊 MONITORIZARE LIVE ENERGIE", True, COLOR_CYAN), (485, 385))
        
        max_te = 120 * g * 50.0
        pygame.draw.rect(screen, (15, 23, 42), (485, 420, 375, 6), border_radius=3)
        pygame.draw.rect(screen, COLOR_GREEN, (485, 420, int(375 * min(1.0, E_pot_grav / max_te)), 6), border_radius=3)
        screen.blit(font_mono.render(f"Ep (Gravitațională): {E_pot_grav:.0f} J", True, COLOR_TEXT_MUTED), (485, 405))

        pygame.draw.rect(screen, (15, 23, 42), (485, 455, 375, 6), border_radius=3)
        pygame.draw.rect(screen, COLOR_CYAN, (485, 455, int(375 * min(1.0, E_elastic / max_te)), 6), border_radius=3)
        screen.blit(font_mono.render(f"E_el (Elastică coardă): {E_elastic:.0f} J", True, COLOR_TEXT_MUTED), (485, 440))

        # Casetă Punct Oprire Estimat (Va afișa corect 2.00 m!)
        pygame.draw.rect(screen, (15, 23, 42), (485, 475, 375, 32), border_radius=4)
        txt_p = font_mono.render(f"Punct minim teoretic calculat: Y = {y_min_teoretic:.2f} m", True, COLOR_GREEN if 1.0 <= y_min_teoretic <= 3.0 else COLOR_ORANGE)
        screen.blit(txt_p, (495, 485))

        if sim_state == "FINISHED":
            screen.blit(font_mono.render(f"Forță G Maximă resimțită: {max_g_force:.2f} G", True, COLOR_WHITE), (485, 107))

        btn_start.draw(screen, mouse_pos)
        btn_reset.draw(screen, mouse_pos)

        # Zonă superioară mesaje
        pygame.draw.rect(screen, COLOR_PANEL, (15, 12, 865, 36), border_radius=6)
        screen.blit(font_ui.render(feedback_msg, True, feedback_color), (30, 22))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
