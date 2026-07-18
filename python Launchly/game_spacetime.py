import pygame
import sys
import math
import numpy as np

# --- INIȚIALIZARE ---
pygame.init()
pygame.font.init()

# Rezoluție și mai compactă (1024x700)
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pânza Spațiu-Timp - Laborator Fizică")

# Culori Interfață (Interstellar Cyberpunk Theme)
COLOR_BG = (10, 12, 18)
COLOR_PANEL = (20, 24, 35)
COLOR_PANEL_BORDER = (45, 55, 72)
COLOR_GRID = (38, 45, 62)
COLOR_WHITE = (241, 245, 249)
COLOR_TEXT_MUTED = (148, 163, 184)
COLOR_YELLOW = (250, 204, 21)
COLOR_BLACK_HOLE = (5, 5, 10)
COLOR_HORIZON = (255, 255, 255)
COLOR_CYAN = (34, 211, 238)
COLOR_RED = (239, 68, 68)
COLOR_GREEN = (34, 197, 94)

font_title = pygame.font.SysFont("Segoe UI", 14, bold=True)
font_subtitle = pygame.font.SysFont("Segoe UI", 12, bold=True)
font_ui = pygame.font.SysFont("Segoe UI", 11, bold=True)
font_mono = pygame.font.SysFont("Consolas", 11)

clock = pygame.time.Clock()
FPS = 60

# --- CONSTANTE FIZICE ---
G = 0.1  
SPEED_OF_LIGHT = 15.0  

# Dimensiuni zone (Canvas stânga, Control dreapta)
canvas_rect = pygame.Rect(15, 15, 710, 670)
panel_rect = pygame.Rect(740, 15, 270, 670)

class CelestialBody:
    def __init__(self, x, y, mass, body_type):
        self.x = float(x)
        self.y = float(y)
        self.type = body_type
        
        if body_type == 'star':
            self.mass = mass
            self.radius = max(14, int(mass * 0.004 + 8))
            self.color = COLOR_YELLOW
        else:
            self.mass = mass * 100  
            self.radius = max(8, int(mass * 0.001 + 5))
            self.color = COLOR_BLACK_HOLE

    def is_clicked(self, mx, my):
        return math.hypot(mx - self.x, my - self.y) <= max(self.radius, 15)

    def draw(self, surface):
        if self.type == 'star':
            glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (250, 204, 21, 25), (self.radius * 2, self.radius * 2), self.radius * 2)
            surface.blit(glow, (int(self.x - self.radius * 2), int(self.y - self.radius * 2)))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        else:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, COLOR_HORIZON, (int(self.x), int(self.y)), self.radius, 1)

class LightRay:
    def __init__(self, start_y):
        self.x = float(canvas_rect.left)
        self.y = float(start_y)
        self.initial_y = float(start_y)
        self.vx = SPEED_OF_LIGHT
        self.vy = 0.0
        self.history = [(self.x, self.y)]
        self.active = True
        self.status_msg = ""
        self.dev_angle = 0.0  

    def update(self, bodies):
        if not self.active: return

        ax, ay = 0.0, 0.0
        dt = 1.0

        for body in bodies:
            dx = body.x - self.x
            dy = body.y - self.y
            r_sq = dx*dx + dy*dy
            r = math.sqrt(r_sq)

            if r < 2: continue

            mag = (2.0 * G * body.mass) / (r_sq * r)
            ax += mag * dx
            ay += mag * dy

            if r <= body.radius:
                self.active = False
                self.status_msg = "Rază capturată!"
                return

        self.vx += ax * dt
        self.vy += ay * dt

        v_mag = math.hypot(self.vx, self.vy)
        if v_mag > 0:
            self.vx = (self.vx / v_mag) * SPEED_OF_LIGHT
            self.vy = (self.vy / v_mag) * SPEED_OF_LIGHT

        self.x += self.vx
        self.y += self.vy
        self.history.append((self.x, self.y))
        self.dev_angle = abs(math.degrees(math.atan2(self.vy, self.vx)))

        if not canvas_rect.inflate(30, 30).collidepoint(self.x, self.y):
            self.active = False

    def draw(self, surface):
        if len(self.history) < 2: return
        points = [(px, py) for px, py in self.history if canvas_rect.collidepoint(px, py)]
        if len(points) >= 2:
            pygame.draw.lines(surface, COLOR_CYAN, False, points, 2)

class ModernSlider:
    def __init__(self, x, y, w, min_val, max_val, start_val, label):
        self.rect = pygame.Rect(x, y, w, 6)
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.label = label
        self.handle_pos = [x, y + 3]
        self.update_handle()
        self.dragging = False

    def update_handle(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_pos[0] = self.rect.x + ratio * self.rect.width

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if math.hypot(event.pos[0] - self.handle_pos[0], event.pos[1] - self.handle_pos[1]) <= 10 or self.rect.inflate(0, 16).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pos_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            self.val = self.min_val + ((pos_x - self.rect.x) / self.rect.width) * (self.max_val - self.min_val)
            self.handle_pos[0] = pos_x

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_BG, self.rect, border_radius=3)
        if self.handle_pos[0] - self.rect.x > 0:
            pygame.draw.rect(surface, COLOR_CYAN, (self.rect.x, self.rect.y, self.handle_pos[0] - self.rect.x, self.rect.height), border_radius=3)
        pygame.draw.circle(surface, COLOR_WHITE, (int(self.handle_pos[0]), int(self.handle_pos[1])), 6)
        lbl_surf = font_ui.render(f"{self.label}: {int(self.val)}", True, COLOR_WHITE)
        surface.blit(lbl_surf, (self.rect.x, self.rect.y - 16))

class ModernButton:
    def __init__(self, x, y, w, h, text, base_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.base_color = base_color
        self.is_active = False

    def draw(self, surface, mouse_pos):
        if self.is_active: draw_color = tuple(min(255, c + 40) for c in self.base_color)
        elif self.rect.collidepoint(mouse_pos): draw_color = tuple(min(255, c + 20) for c in self.base_color)
        else: draw_color = self.base_color

        pygame.draw.rect(surface, draw_color, self.rect, border_radius=5)
        if self.is_active:
            pygame.draw.rect(surface, COLOR_CYAN, self.rect, 1, border_radius=5)

        txt_surf = font_ui.render(self.text, True, COLOR_WHITE)
        surface.blit(txt_surf, (self.rect.centerx - txt_surf.get_width() // 2, self.rect.centery - txt_surf.get_height() // 2))

def generate_distorted_grid(bodies):
    grid_spacing = 25
    xs = np.arange(canvas_rect.left, canvas_rect.right + 1, grid_spacing)
    ys = np.arange(canvas_rect.top, canvas_rect.bottom + 1, grid_spacing)
    X, Y = np.meshgrid(xs, ys)
    X_def, Y_def = X.astype(float), Y.astype(float)

    for body in bodies:
        dx = body.x - X
        dy = body.y - Y
        r_sq = dx*dx + dy*dy
        r = np.sqrt(r_sq)
        np.clip(r, 1.0, None, out=r)
        
        displacement_mag = (body.mass * 0.4) / (r_sq + 400)
        np.clip(displacement_mag, 0, r * 0.8, out=displacement_mag)
        
        X_def += (dx / r) * displacement_mag
        Y_def += (dy / r) * displacement_mag

    return xs, ys, X_def, Y_def

def main():
    selected_mode = 'star'
    bodies = []
    light_rays = []
    flash_message = ""
    flash_timer = 0
    
    # Stocăm ce tip de raze urmează să fie lansate la apăsarea START
    pending_ray_type = None 

    # UI Controls setup - Compactat
    btn_star = ModernButton(panel_rect.x + 15, 95, 115, 28, "Adaugă Stea", (30, 41, 59))
    btn_star.is_active = True
    btn_bh = ModernButton(panel_rect.x + 140, 95, 115, 28, "Gaură Neagră", (30, 41, 59))
    
    slider_mass = ModernSlider(panel_rect.x + 15, 160, 240, 100, 10000, 3000, "Masă Sursă")
    
    btn_launch = ModernButton(panel_rect.x + 15, 205, 240, 36, "🚀 LANSEAZĂ FASCICUL (START)", (16, 185, 129))
    btn_clear = ModernButton(panel_rect.x + 15, 250, 240, 28, "🗑️ Resetează Tot", (239, 68, 68))

    # Layout Presets Buttons - Compactat
    btn_p1 = ModernButton(panel_rect.x + 15, 315, 240, 26, "Preset 1: Lentilă Gravitațională", (47, 63, 97))
    btn_p2 = ModernButton(panel_rect.x + 15, 345, 240, 26, "Preset 2: Captură Orizont", (47, 63, 97))
    btn_p3 = ModernButton(panel_rect.x + 15, 375, 240, 26, "Preset 3: Sistem Binar Stele", (47, 63, 97))

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(COLOR_BG)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # --- ADAUGĂ ACEST BLOC ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 
            # -------------------------

            slider_mass.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if canvas_rect.collidepoint(mx, my):
                    if event.button == 1:
                        bodies = [b for b in bodies if not b.is_clicked(mx, my)]
                        bodies.append(CelestialBody(mx, my, slider_mass.val, selected_mode))
                        light_rays.clear()
                        pending_ray_type = "manual"
                    elif event.button == 3:
                        bodies = [b for b in bodies if not b.is_clicked(mx, my)]
                        light_rays.clear()
                
                elif panel_rect.collidepoint(mx, my) and event.button == 1:
                    if btn_star.rect.collidepoint(mx, my):
                        selected_mode = 'star'; btn_star.is_active = True; btn_bh.is_active = False
                    elif btn_bh.rect.collidepoint(mx, my):
                        selected_mode = 'blackhole'; btn_star.is_active = False; btn_bh.is_active = True
                    
                    elif btn_launch.rect.collidepoint(mx, my):
                        # Executarea lansării efective la apăsarea START
                        light_rays.clear()
                        if pending_ray_type == "p1":
                            for o in [-80, -40, -15, 15, 40, 80]: light_rays.append(LightRay(canvas_rect.centery + o))
                        elif pending_ray_type == "p2":
                            light_rays.append(LightRay(canvas_rect.centery - 10))
                            light_rays.append(LightRay(canvas_rect.centery + 45))
                        elif pending_ray_type == "p3":
                            for o in range(-100, 101, 25): light_rays.append(LightRay(canvas_rect.centery + o))
                        else: 
                            for offset in [-60, -30, 0, 30, 60]: light_rays.append(LightRay(canvas_rect.centery + offset))
                    
                    elif btn_clear.rect.collidepoint(mx, my):
                        bodies.clear(); light_rays.clear(); flash_message = ""; pending_ray_type = None
                    
                    
                    elif btn_p1.rect.collidepoint(mx, my):
                        bodies.clear(); light_rays.clear()
                        bodies.append(CelestialBody(canvas_rect.centerx, canvas_rect.centery, 4000, 'blackhole'))
                        pending_ray_type = "p1"
                        flash_message = "Layout 1 Încărcat! Apasă butonul verde pentru START."; flash_timer = 120
                    elif btn_p2.rect.collidepoint(mx, my):
                        bodies.clear(); light_rays.clear()
                        bodies.append(CelestialBody(canvas_rect.centerx, canvas_rect.centery, 6000, 'blackhole'))
                        pending_ray_type = "p2"
                        flash_message = "Layout 2 Încărcat! Apasă butonul verde pentru START."; flash_timer = 120
                    elif btn_p3.rect.collidepoint(mx, my):
                        bodies.clear(); light_rays.clear()
                        bodies.append(CelestialBody(canvas_rect.centerx - 80, canvas_rect.centery - 30, 3000, 'star'))
                        bodies.append(CelestialBody(canvas_rect.centerx + 80, canvas_rect.centery + 40, 2000, 'star'))
                        pending_ray_type = "p3"
                        flash_message = "Layout 3 Încărcat! Apasă butonul verde pentru START."; flash_timer = 120

        # --- UPDATE FIZICĂ ---
        for ray in light_rays:
            if ray.active:
                ray.update(bodies)
                if ray.status_msg:
                    flash_message = ray.status_msg; flash_timer = 90

        # --- RENDERING ---
        xs, ys, X_def, Y_def = generate_distorted_grid(bodies)
        for i in range(len(ys)):
            pygame.draw.lines(screen, COLOR_GRID, False, [(X_def[i, j], Y_def[i, j]) for j in range(len(xs))], 1)
        for j in range(len(xs)):
            pygame.draw.lines(screen, COLOR_GRID, False, [(X_def[i, j], Y_def[i, j]) for i in range(len(ys))], 1)

        # Măști decupare margini canvas
        pygame.draw.rect(screen, COLOR_BG, (0, 0, SCREEN_WIDTH, canvas_rect.top))
        pygame.draw.rect(screen, COLOR_BG, (0, canvas_rect.bottom, SCREEN_WIDTH, SCREEN_HEIGHT - canvas_rect.bottom))
        pygame.draw.rect(screen, COLOR_BG, (0, 0, canvas_rect.left, SCREEN_HEIGHT))

        for ray in light_rays: ray.draw(screen)
        for body in bodies: body.draw(screen)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, canvas_rect, 2, border_radius=4)

        
        if light_rays and len(bodies) == 1:
            main_ray = light_rays[0]
            body = bodies[0]
            param_b = abs(main_ray.initial_y - body.y)
            c_sq = SPEED_OF_LIGHT ** 2
            teoretici_deg = min(90.0, math.degrees((4.0 * G * body.mass) / (c_sq * param_b))) if param_b > 0 else 0.0

            stats_box = pygame.Rect(canvas_rect.left + 15, canvas_rect.top + 15, 280, 95)
            pygame.draw.rect(screen, (15, 23, 42, 230), stats_box, border_radius=6)
            pygame.draw.rect(screen, COLOR_CYAN, stats_box, 1, border_radius=6)
            
            screen.blit(font_title.render("📊 TELEMETRIE MATEMATICĂ", True, COLOR_CYAN), (stats_box.x + 10, stats_box.y + 8))
            screen.blit(font_mono.render(f"Parametru Impact (b): {param_b:.1f} px", True, COLOR_WHITE), (stats_box.x + 10, stats_box.y + 32))
            screen.blit(font_mono.render(f"Deviație Teoretică: {teoretici_deg:.2f}°", True, COLOR_YELLOW), (stats_box.x + 10, stats_box.y + 50))
            screen.blit(font_mono.render(f"Deviație Reală Sim: {main_ray.dev_angle:.2f}°", True, COLOR_GREEN), (stats_box.x + 10, stats_box.y + 68))

        
        pygame.draw.rect(screen, COLOR_PANEL, panel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_rect, 2, border_radius=6)

        screen.blit(font_title.render("Pânza Spațiu-Timp", True, COLOR_WHITE), (panel_rect.x + 15, panel_rect.y + 15))
        screen.blit(font_mono.render("Relativitatea Generală", True, COLOR_CYAN), (panel_rect.x + 15, panel_rect.y + 32))
        pygame.draw.line(screen, COLOR_PANEL_BORDER, (panel_rect.x + 15, panel_rect.y + 50), (panel_rect.right - 15, panel_rect.y + 50), 1)
        
        screen.blit(font_subtitle.render("1. Instrumente Editor", True, COLOR_WHITE), (panel_rect.x + 15, panel_rect.y + 60))
        btn_star.draw(screen, mouse_pos); btn_bh.draw(screen, mouse_pos)
        slider_mass.draw(screen); btn_launch.draw(screen, mouse_pos); btn_clear.draw(screen, mouse_pos)

        # Secțiune Presets
        pygame.draw.line(screen, COLOR_PANEL_BORDER, (panel_rect.x + 15, panel_rect.y + 292), (panel_rect.right - 15, panel_rect.y + 292), 1)
        screen.blit(font_subtitle.render("2. Structuri / Presets", True, COLOR_WHITE), (panel_rect.x + 15, panel_rect.y + 300))
        btn_p1.draw(screen, mouse_pos); btn_p2.draw(screen, mouse_pos); btn_p3.draw(screen, mouse_pos)

        
        guide_y = panel_rect.y + 415
        pygame.draw.line(screen, COLOR_PANEL_BORDER, (panel_rect.x + 15, guide_y), (panel_rect.right - 15, guide_y), 1)
        screen.blit(font_subtitle.render("📖 Ghid de Utilizare Rapid:", True, COLOR_WHITE), (panel_rect.x + 15, guide_y + 8))
        
        tips = [
            "• Pas 1: Apasă pe oricare dintre cele 3",
            "  butoane albastre de 'Preset'.",
            "• Pas 2: Analizează cum se deformează",
            "  pânza în funcție de masele adăugate.",
            "• Pas 3: Apasă pe butonul verde mare",
            "  'LANSEAZĂ FASCICUL' pentru a porni",
            "  simularea traiectoriei luminii.",
            "• Pas 4: Modifică glisorul de Masă,",
            "  fă click stânga pe ecran și pornește",
            "  propriile tale probleme experimentale."
        ]
        for i, tip in enumerate(tips):
            screen.blit(font_mono.render(tip, True, COLOR_TEXT_MUTED), (panel_rect.x + 12, guide_y + 28 + i*15))

        # Alertă text pe ecran (Notificări status)
        if flash_timer > 0 and flash_message:
            flash_bg = pygame.Rect(canvas_rect.left + 20, canvas_rect.bottom - 45, 410, 30)
            pygame.draw.rect(screen, (35, 15, 20), flash_bg, border_radius=4)
            pygame.draw.rect(screen, COLOR_RED if "capturată" in flash_message else COLOR_CYAN, flash_bg, 1, border_radius=4)
            screen.blit(font_ui.render(flash_message, True, COLOR_WHITE), (flash_bg.x + 12, flash_bg.y + 7))
            flash_timer -= 1

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
