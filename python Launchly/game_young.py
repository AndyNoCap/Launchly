import pygame
import math
import sys

# --- INIȚIALIZARE ---
pygame.init()
pygame.font.init()

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 740  
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Laborator Interactiv: Dispozitivul lui Young & Interferența Optică")

# Culori Interfață
COLOR_BG = (10, 11, 15)
COLOR_PANEL_BG = (18, 20, 28)
COLOR_PANEL_BORDER = (35, 42, 60)
COLOR_WHITE = (240, 240, 250)
COLOR_TEXT_MUTED = (90, 105, 130)
COLOR_SLIDER_BG = (35, 40, 55)
COLOR_BUTTON_BG = (28, 32, 45)
COLOR_BUTTON_HOVER = (45, 52, 75)

font_title = pygame.font.SysFont("Segoe UI", 15, bold=True)
font_ui = pygame.font.SysFont("Segoe UI", 12, bold=True)
font_math = pygame.font.SysFont("Consolas", 12)

clock = pygame.time.Clock()
FPS = 60


def sinc(x):
    return math.sin(x) / x if x != 0 else 1.0


def wavelength_to_rgb(nm):
    if 380 <= nm < 440:
        r, g, b = -(nm - 440) / (440 - 380), 0.0, 1.0
    elif 440 <= nm < 490:
        r, g, b = 0.0, (nm - 440) / (490 - 440), 1.0
    elif 490 <= nm < 510:
        r, g, b = 0.0, 1.0, -(nm - 510) / (510 - 490)
    elif 510 <= nm < 580:
        r, g, b = (nm - 510) / (580 - 510), 1.0, 0.0
    elif 580 <= nm < 645:
        r, g, b = 1.0, -(nm - 645) / (645 - 580), 0.0
    elif 645 <= nm <= 750:
        r, g, b = 1.0, 0.0, 0.0
    else:
        r, g, b = 0.0, 0.0, 0.0
    factor = 1.0
    if 380 <= nm < 420: factor = 0.3 + 0.7 * (nm - 380) / (420 - 380)
    elif 700 <= nm <= 750: factor = 0.3 + 0.7 * (750 - nm) / (750 - 700)
    return (int(r * 255 * factor), int(g * 255 * factor), int(b * 255 * factor))


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
        txt = font_ui.render(f"{self.label}: {self.val:.1f} {self.unit}", True, COLOR_WHITE)
        surface.blit(txt, (self.rect.x, self.rect.y - 18))


class PresetButton:
    def __init__(self, x, y, w, h, text, target_lambda, target_d, target_D):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.t_lambda = target_lambda
        self.t_d = target_d
        self.t_D = target_D

    def draw(self, surface, mouse_pos):
        is_hovered = self.rect.collidepoint(mouse_pos)
        bg_color = COLOR_BUTTON_HOVER if is_hovered else COLOR_BUTTON_BG
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.rect, 1, border_radius=4)
        
        txt_surface = font_ui.render(self.text, True, COLOR_WHITE)
        surface.blit(txt_surface, (self.rect.centerx - txt_surface.get_width()//2, self.rect.centery - txt_surface.get_height()//2))

    def check_click(self, mouse_pos, s_lam, s_d, s_D):
        if self.rect.collidepoint(mouse_pos):
            s_lam.val = self.t_lambda
            s_d.val = self.t_d
            s_D.val = self.t_D
            s_lam.update_handle()
            s_d.update_handle()
            s_D.update_handle()


wave_box = pygame.Rect(30, 80, 450, 200)
screen_box = pygame.Rect(540, 160, 450, 120) 
graph_box = pygame.Rect(540, 80, 450, 75)   


slider_lambda = CompactSlider(30, 310, 210, 400.0, 700.0, 650.0, "Lungime de undă (λ)", "nm")
slider_d_fante = CompactSlider(270, 310, 210, 10.0, 50.0, 22.0, "Distanța fante (d)", "μm", (150, 255, 100))
slider_D_ecran = CompactSlider(30, 360, 210, 1.0, 5.0, 3.0, "Distanța ecran (D)", "m", (255, 150, 50))


buttons = [
    PresetButton(540, 315, 140, 28, "Preset: Laser Roșu", 680.0, 25.0, 3.0),
    PresetButton(695, 315, 140, 28, "Preset: Laser Violet", 410.0, 25.0, 3.0),
    PresetButton(850, 315, 140, 28, "Preset: Fante Apropiate", 550.0, 12.0, 4.0)
]

def main():
    running = True
    sim_time = 0.0

    while running:
        clock.tick(FPS)
        sim_time += 0.08

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
                
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            
            slider_lambda.handle_event(event)
            slider_d_fante.handle_event(event)
            slider_D_ecran.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in buttons:
                    btn.check_click(event.pos, slider_lambda, slider_d_fante, slider_D_ecran)

        lam = slider_lambda.val       
        d_dist = slider_d_fante.val   
        D_dist = slider_D_ecran.val   

        laser_color = wavelength_to_rgb(lam)
        slider_lambda.color = laser_color  

        screen.fill(COLOR_BG)
        
        pygame.draw.line(screen, COLOR_PANEL_BORDER, (512, 0), (512, 740), 1)
        pygame.draw.line(screen, COLOR_PANEL_BORDER, (0, 410), (1024, 410), 1)

        
        screen.blit(font_title.render("1. PROPAGAREA ȘI SUPRAPUNEREA UNDELOR", True, laser_color), (30, 25))
        pygame.draw.rect(screen, COLOR_PANEL_BG, wave_box, border_radius=4)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, wave_box, 1, border_radius=4)

        fante_x = wave_box.x + 80
        fanta1_y = wave_box.centery - int(d_dist * 1.2)
        fanta2_y = wave_box.centery + int(d_dist * 1.2)

        pygame.draw.rect(screen, laser_color, (wave_box.x, wave_box.y, 80, wave_box.height), 1)
        for wx in range(wave_box.x + 10, fante_x, 15):
            alpha = int(125 + 125 * math.sin(wx * 0.2 - sim_time))
            c_surface = pygame.Surface((2, wave_box.height), pygame.SRCALPHA)
            c_surface.fill((*laser_color, alpha))
            screen.blit(c_surface, (wx, wave_box.y))

        pygame.draw.line(screen, COLOR_WHITE, (fante_x, wave_box.y), (fante_x, wave_box.height + wave_box.y), 4)
        pygame.draw.line(screen, COLOR_PANEL_BG, (fante_x, fanta1_y - 4), (fante_x, fanta1_y + 4), 5)
        pygame.draw.line(screen, COLOR_PANEL_BG, (fante_x, fanta2_y - 4), (fante_x, fanta2_y + 4), 5)

        wave_surface = pygame.Surface((wave_box.width, wave_box.height), pygame.SRCALPHA)
        k_opt = 1000 / lam 
        
        for r_arc in range(15, 350, 18):
            f1_alpha = int(100 * (1 - r_arc/350)) 
            if f1_alpha > 0:
                f1_alpha = int(f1_alpha * (0.5 + 0.5 * math.sin(r_arc * k_opt - sim_time)))
                pygame.draw.circle(wave_surface, (*laser_color, f1_alpha), (fante_x - wave_box.x, fanta1_y - wave_box.y), r_arc, 1)
            
            f2_alpha = int(100 * (1 - r_arc/350))
            if f2_alpha > 0:
                f2_alpha = int(f2_alpha * (0.5 + 0.5 * math.sin(r_arc * k_opt - sim_time)))
                pygame.draw.circle(wave_surface, (*laser_color, f2_alpha), (fante_x - wave_box.x, fanta2_y - wave_box.y), r_arc, 1)

        screen.blit(wave_surface, (wave_box.x, wave_box.y))
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, wave_box, 1, border_radius=4)


        
        screen.blit(font_title.render("2. GRAFICUL INTENSITĂȚII ȘI FRANJELE PE ECRAN", True, COLOR_WHITE), (540, 25))
        
        pygame.draw.rect(screen, COLOR_PANEL_BG, graph_box, border_radius=4)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, graph_box, 1, border_radius=4)
        pygame.draw.rect(screen, COLOR_PANEL_BG, screen_box, border_radius=4)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, screen_box, 1, border_radius=4)

        franja_px = (lam * 0.05 * D_dist) / (d_dist * 0.1)
        graph_points = []

        for px in range(screen_box.width):
            screen_x = screen_box.x + px
            dist_to_center = px - screen_box.width // 2
            
            faza_interferenta = math.pi * dist_to_center / (franja_px if franja_px > 0 else 1)
            intensitate = (math.cos(faza_interferenta)) ** 2
            
            atenuare_difractie = sinc(dist_to_center * 0.015) 
            factor_final = max(0, min(1, intensitate * (atenuare_difractie ** 2)))

            graph_y = graph_box.bottom - 5 - int(factor_final * (graph_box.height - 10))
            graph_points.append((screen_x, graph_y))

            pixel_color = (int(laser_color[0] * factor_final), 
                           int(laser_color[1] * factor_final), 
                           int(laser_color[2] * factor_final))
            pygame.draw.line(screen, pixel_color, (screen_x, screen_box.y + 5), (screen_x, screen_box.bottom - 5))

        
        if len(graph_points) > 1:
            pygame.draw.lines(screen, COLOR_WHITE, False, graph_points, 2)

        screen.blit(font_ui.render("Intensitate Lumină I(y)", True, COLOR_TEXT_MUTED), (graph_box.x + 10, graph_box.y + 5))


        
        calc_s = pygame.Rect(30, 440, 452, 260)
        pygame.draw.rect(screen, COLOR_PANEL_BG, calc_s, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, calc_s, 1, border_radius=6)
        
        interfranja_reala = (lam * 1e-9 * D_dist) / (d_dist * 1e-6) * 1000 

        lines_s = [
            "  DISPOZITIVUL YOUNG: FORMULE FINALE",
            "  Interfranja: i = (λ * D) / d",
            " ------------------------------------------------",
            f"  • Lungime undă (λ)   = {lam:.1f} nm",
            f"  • Distanța fante (d) = {d_dist:.1f} μm",
            f"  • Distanța ecran (D) = {D_dist:.2f} m",
            f"  • Lățime franjă (i)  = {interfranja_reala:.3f} mm",
            " ------------------------------------------------",
            "  * Maxim (Lumină): Când undele sosesc în fază.",
            "  * Minim (Întuneric): Când se anulează reciproc."
        ]
        for idx, line in enumerate(lines_s):
            c = laser_color if idx in [0,1] else (COLOR_TEXT_MUTED if idx >= 8 else COLOR_WHITE)
            screen.blit(font_math.render(line, True, c), (40, 455 + idx * 24))


        
        calc_g = pygame.Rect(540, 440, 450, 260)
        pygame.draw.rect(screen, COLOR_PANEL_BG, calc_g, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, calc_g, 1, border_radius=6)
        lines_g = [
            "  GHID DE ÎNȚELEGERE: OBSERVAȚI GRAFICUL ALB",
            " ------------------------------------------------",
            "  • Punctele Maxime ale liniei albe din grafic",
            "    reprezintă INTERFERENȚA CONSTRUCTIVĂ (Lumină).",
            "  • Punctele de Minim (baza graficului) înseamnă",
            "    INTERFERENȚĂ DISTRACTIVĂ (Unde în antifază).",
            " ------------------------------------------------",
            "  • EXPERIMENT: Apăsați pe butoanele Preset de mai",
            "    sus pentru a vedea cum lumina violetă (undă scurtă)",
            "    strânge franjele, iar fantele apropiate le dilată."
        ]
        for idx, line in enumerate(lines_g):
            c = COLOR_WHITE if idx in [2, 4, 7] else COLOR_TEXT_MUTED
            if idx == 0: c = COLOR_WHITE
            screen.blit(font_math.render(line, True, c), (550, 455 + idx * 24))

        
        slider_lambda.draw(screen)
        slider_d_fante.draw(screen)
        slider_D_ecran.draw(screen)
        for btn in buttons:
            btn.draw(screen, mouse_pos)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
