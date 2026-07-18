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
pygame.display.set_caption("Laborator Virtual: Cinematica Proiectilelor în Regim Live")

# Paletă de Culori Premium (Dark Tech Style)
COLOR_BG = (10, 11, 15)
COLOR_PANEL_BG = (18, 20, 28)
COLOR_PANEL_BORDER = (35, 42, 60)
COLOR_WHITE = (240, 240, 250)
COLOR_TEXT_MUTED = (110, 125, 150)
COLOR_CYAN = (0, 210, 255)
COLOR_GREEN = (140, 255, 100)
COLOR_ORANGE = (255, 135, 50)
COLOR_RED = (230, 75, 75)

font_title = pygame.font.SysFont("Segoe UI", 16, bold=True)
font_ui = pygame.font.SysFont("Segoe UI", 13, bold=True)
font_math = pygame.font.SysFont("Consolas", 14)

clock = pygame.time.Clock()
FPS = 60

# --- CLASA EFECT PARTICULE (FUM ȘI EXPLOZIE) ---
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
        radius = max(1, int((self.lifetime / self.max_life) * 6))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), radius)

# --- CLASA SLIDER COMPACT INTERACTIV ---
class CompactSlider:
    def __init__(self, x, y, w, min_val, max_val, start_val, label, unit="", color=COLOR_CYAN):
        self.rect = pygame.Rect(x, y, w, 6)
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.label = label
        self.unit = unit
        self.color = color
        self.handle_radius = 7
        self.handle_pos = [x, y + 3]
        self.update_handle()
        self.dragging = False

    def update_handle(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_pos[0] = self.rect.x + ratio * self.rect.width

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
        pygame.draw.circle(surface, COLOR_WHITE if self.dragging else self.color, (int(self.handle_pos[0]), int(self.handle_pos[1])), self.handle_radius)
        txt = font_ui.render(f"{self.label}: {self.val:.1f}{self.unit}", True, COLOR_WHITE)
        surface.blit(txt, (self.rect.x, self.rect.y - 20))

# --- STRUCTURĂ ZONE INTERFAȚĂ ---
view_simulation = pygame.Rect(30, 70, 1040, 400)
panel_data = pygame.Rect(30, 490, 500, 140)
panel_controls = pygame.Rect(550, 490, 520, 140)
panel_sliders = pygame.Rect(30, 650, 1040, 100)
panel_footer = pygame.Rect(30, 765, 1040, 40)

# REPOZIȚIONARE REZOLVATĂ: Coborâte de la Y=510 la Y=535 pentru a nu mai încăleca titlul
btn_fire = pygame.Rect(570, 535, 130, 32)
btn_preset_windy = pygame.Rect(715, 535, 155, 32)
btn_reset = pygame.Rect(885, 535, 115, 32)

# Inițializare Slidere
slider_angle = CompactSlider(50, 710, 210, 0.0, 90.0, 45.0, "Unghi Lansare (θ)", "°", COLOR_CYAN)
slider_velocity = CompactSlider(300, 710, 210, 10.0, 150.0, 70.0, "Viteză Inițială (v₀)", " m/s", COLOR_CYAN)
slider_gravity = CompactSlider(590, 710, 210, 1.0, 25.0, 9.8, "Gravitație (g)", " m/s²", COLOR_ORANGE)
slider_wind = CompactSlider(840, 710, 170, -20.0, 20.0, 5.0, "Vânt Orizontal (Wx)", " m/s", COLOR_GREEN)

class AdvancedArtillery:
    def __init__(self):
        self.particles = []
        self.reset_target()

    def reset_target(self):
        self.state = "AIMING"
        self.cannon_pos = (70, view_simulation.bottom - 40)
        self.projectile_pos = list(self.cannon_pos)
        self.trail = []
        self.t = 0.0
        
        tx = random.randint(550, view_simulation.right - 100)
        ty = random.randint(view_simulation.y + 150, view_simulation.bottom - 60)
        self.target_size = 50
        self.target_rect = pygame.Rect(tx, ty, self.target_size, 30)

    def trigger_explosion(self, px, py, color):
        for _ in range(40):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 7)
            self.particles.append(Particle(px, py, math.cos(angle) * speed, math.sin(angle) * speed, color, random.randint(20, 50)))

    def fire(self):
        if self.state != "IN_AIR":
            self.state = "IN_AIR"
            self.projectile_pos = list(self.cannon_pos)
            self.trail = []
            self.t = 0.0
            self.trigger_explosion(self.cannon_pos[0], self.cannon_pos[1], COLOR_ORANGE)

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)

        if self.state == "IN_AIR":
            dt_step = 0.08
            self.t += dt_step

            angle_rad = math.radians(slider_angle.val)
            vx = slider_velocity.val * math.cos(angle_rad)
            vy = slider_velocity.val * math.sin(angle_rad)

            # Fizică reală: Vântul adaugă o viteză constantă pe orizontală t, nu o accelerare exponențială
            px = self.cannon_pos[0] + (vx * self.t) + (slider_wind.val * self.t)
            py = self.cannon_pos[1] - (vy * self.t - 0.5 * slider_gravity.val * (self.t ** 2))

            self.projectile_pos = [px, py]
            self.trail.append((int(px), int(py)))

            if random.random() > 0.3:
                self.particles.append(Particle(px, py, random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), (100, 105, 120), 25))

            proj_rect = pygame.Rect(px - 4, py - 4, 8, 8)
            if self.target_rect.colliderect(proj_rect):
                self.state = "HIT"
                self.trigger_explosion(px, py, COLOR_GREEN)
            elif py > view_simulation.bottom - 20 or px > view_simulation.right or px < view_simulation.left:
                self.state = "MISS"
                self.trigger_explosion(px, py, COLOR_RED)

    def draw(self):
        pygame.draw.rect(screen, COLOR_PANEL_BG, view_simulation, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, view_simulation, 1, border_radius=6)

        for x in range(view_simulation.left, view_simulation.right, 80):
            pygame.draw.line(screen, (25, 28, 38), (x, view_simulation.y), (x, view_simulation.bottom), 1)
        for y in range(view_simulation.y, view_simulation.bottom, 60):
            pygame.draw.line(screen, (25, 28, 38), (view_simulation.left, y), (view_simulation.right, y), 1)

        pygame.draw.line(screen, (50, 58, 80), (view_simulation.left, view_simulation.bottom - 20), (view_simulation.right, view_simulation.bottom - 20), 2)
        pygame.draw.rect(screen, COLOR_RED, self.target_rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_WHITE, self.target_rect, 1, border_radius=4)

        pygame.draw.circle(screen, (80, 90, 110), self.cannon_pos, 16)
        pygame.draw.circle(screen, COLOR_PANEL_BORDER, self.cannon_pos, 16, 2)

        barrel_len = 36
        end_x = self.cannon_pos[0] + barrel_len * math.cos(math.radians(slider_angle.val))
        end_y = self.cannon_pos[1] - barrel_len * math.sin(math.radians(slider_angle.val))
        pygame.draw.line(screen, COLOR_WHITE, self.cannon_pos, (end_x, end_y), 6)

        # Traiectorie Predictivă Calibrată
        if self.state != "IN_AIR":
            ghost_t = 0.0
            angle_rad = math.radians(slider_angle.val)
            vx = slider_velocity.val * math.cos(angle_rad)
            vy = slider_velocity.val * math.sin(angle_rad)
            
            for _ in range(40):
                ghost_t += 0.22
                g_x = self.cannon_pos[0] + (vx * ghost_t) + (slider_wind.val * ghost_t)
                g_y = self.cannon_pos[1] - (vy * ghost_t - 0.5 * slider_gravity.val * (ghost_t ** 2))
                if view_simulation.collidepoint(g_x, g_y) and g_y < view_simulation.bottom - 20:
                    pygame.draw.circle(screen, (80, 110, 140), (int(g_x), int(g_y)), 2)

        if len(self.trail) > 1:
            pygame.draw.lines(screen, COLOR_TEXT_MUTED, False, self.trail, 1)

        for p in self.particles:
            p.draw(screen)

        if self.state == "IN_AIR":
            pygame.draw.circle(screen, COLOR_ORANGE, (int(self.projectile_pos[0]), int(self.projectile_pos[1])), 5)
            pygame.draw.circle(screen, COLOR_WHITE, (int(self.projectile_pos[0]), int(self.projectile_pos[1])), 5, 1)

        wind_indicator_center = (view_simulation.right - 60, view_simulation.y + 40)
        pygame.draw.circle(screen, COLOR_PANEL_BG, wind_indicator_center, 25)
        pygame.draw.circle(screen, COLOR_PANEL_BORDER, wind_indicator_center, 25, 1)
        pygame.draw.line(screen, COLOR_GREEN, wind_indicator_center, (wind_indicator_center[0] + slider_wind.val * 1.2, wind_indicator_center[1]), 2)
        screen.blit(font_ui.render(f"Vânt: {slider_wind.val:.1f} m/s", True, COLOR_GREEN), (wind_indicator_center[0] - 110, wind_indicator_center[1] - 8))


def main():
    game = AdvancedArtillery()
    running = True

    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(COLOR_BG)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # --- ADAUGĂ ACEST BLOC PENTRU IEȘIRE ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            # ---------------------------------------
            
            slider_angle.handle_event(event)
            slider_velocity.handle_event(event)
            slider_gravity.handle_event(event)
            slider_wind.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_fire.collidepoint(mouse_pos):
                    game.fire()
                elif btn_preset_windy.collidepoint(mouse_pos):
                    slider_angle.val = 50.0
                    slider_velocity.val = 85.0
                    slider_wind.val = -15.0
                    slider_gravity.val = 9.8
                    slider_angle.update_handle()
                    slider_velocity.update_handle()
                    slider_wind.update_handle()
                    slider_gravity.update_handle()
                elif btn_reset.collidepoint(mouse_pos):
                    game.reset_target()

        game.update()

        # --- RENDERING INTERFAȚĂ ---
        screen.blit(font_title.render("SIMULATOR ARTILERIE: KINETICĂ BALISTICĂ LIVE", True, COLOR_WHITE), (30, 25))

        # 1. Panou Date Analitice
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_data, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_data, 1, border_radius=6)
        screen.blit(font_ui.render("DATE TELEMETRICE PROIECTIL", True, COLOR_CYAN), (45, 505))

        rad = math.radians(slider_angle.val)
        v0x = slider_velocity.val * math.cos(rad)
        v0y = slider_velocity.val * math.sin(rad)

        lines_telemetry = [
            f"Viteză componentă v0_x: {v0x:.2f} m/s",
            f"Viteză componentă v0_y: {v0y:.2f} m/s",
            f"Timp de zbor cumulat:   {game.t:.2f} sec",
            f"Stare curentă sistem:   {game.state}"
        ]
        for idx, line in enumerate(lines_telemetry):
            color_text = COLOR_GREEN if "HIT" in line or game.state == "HIT" and idx == 3 else COLOR_WHITE
            if "MISS" in line or game.state == "MISS" and idx == 3: color_text = COLOR_RED
            screen.blit(font_math.render(line, True, color_text), (45, 535 + idx * 22))

        # 2. Panou Comenzi (FĂRĂ SUPRAPUNERI ACUM)
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_controls, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_controls, 1, border_radius=6)
        screen.blit(font_ui.render("PANOU DE COMANDĂ LIVE", True, COLOR_WHITE), (565, 505))

        col_fire = COLOR_RED if game.state == "IN_AIR" else COLOR_CYAN
        pygame.draw.rect(screen, col_fire, btn_fire, border_radius=4)
        txt_fire = font_ui.render("ÎN AER" if game.state == "IN_AIR" else "LANSATOR (FIRE)", True, COLOR_BG)
        screen.blit(txt_fire, (btn_fire.centerx - txt_fire.get_width() // 2, btn_fire.centery - 8))

        pygame.draw.rect(screen, (25, 45, 35), btn_preset_windy, border_radius=4)
        pygame.draw.rect(screen, COLOR_GREEN, btn_preset_windy, 1, border_radius=4)
        txt_pre = font_ui.render("Preset: Furtună", True, COLOR_GREEN)
        screen.blit(txt_pre, (btn_preset_windy.centerx - txt_pre.get_width() // 2, btn_preset_windy.centery - 8))

        pygame.draw.rect(screen, COLOR_PANEL_BORDER, btn_reset, border_radius=4)
        txt_res_btn = font_ui.render("REGENERARE", True, COLOR_WHITE)
        screen.blit(txt_res_btn, (btn_reset.centerx - txt_res_btn.get_width() // 2, btn_reset.centery - 8))

        screen.blit(font_math.render("• Setează parametrii din sliderele inferioare.", True, COLOR_TEXT_MUTED), (565, 582))
        screen.blit(font_math.render("• 'Regenerare' mută ținta aleatoriu pe ecran.", True, COLOR_TEXT_MUTED), (565, 602))

        # 3. Zona Slidere Dedicată
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_sliders, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_sliders, 1, border_radius=6)
        slider_angle.draw(screen)
        slider_velocity.draw(screen)
        slider_gravity.draw(screen)
        slider_wind.draw(screen)

        # 4. Footer
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_footer, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_footer, 1, border_radius=6)
        screen.blit(font_math.render("• EXPERIMENT: Observă cum vântul orizontal modifică simetria parabolei balistice în timpul zborului.", True, COLOR_TEXT_MUTED), (45, 776))

        game.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
