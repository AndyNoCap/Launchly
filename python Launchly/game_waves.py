import pygame
import math
import sys


pygame.init()
pygame.font.init()


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Unde Seismice vs. Unde Gravitaționale (Compact)")


COLOR_BG = (10, 11, 15)
COLOR_PANEL_BG = (18, 20, 28)
COLOR_PANEL_BORDER = (35, 42, 60)
COLOR_GRID_LINE = (25, 30, 45)
COLOR_WHITE = (230, 230, 240)
COLOR_YELLOW = (255, 198, 41)
COLOR_CYAN = (0, 210, 255)
COLOR_MAGENTA = (255, 50, 100)
COLOR_TEXT_MUTED = (90, 105, 130)

font_title = pygame.font.SysFont("Segoe UI", 16, bold=True)
font_ui = pygame.font.SysFont("Segoe UI", 12, bold=True)
font_math = pygame.font.SysFont("Consolas", 12)

clock = pygame.time.Clock()
FPS = 60


class CompactSlider:
    def __init__(self, x, y, w, min_val, max_val, start_val, label, unit="", color=COLOR_CYAN):
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
        pygame.draw.rect(surface, (35, 40, 55), self.rect, border_radius=2)
        if self.handle_pos[0] - self.rect.x > 0:
            pygame.draw.rect(surface, self.color, (self.rect.x, self.rect.y, self.handle_pos[0] - self.rect.x, self.rect.height), border_radius=2)
        pygame.draw.circle(surface, COLOR_WHITE if self.dragging else self.color, (int(self.handle_pos[0]), int(self.handle_pos[1])), self.handle_radius)
        
        txt = font_ui.render(f"{self.label}: {self.val:.1f} {self.unit}", True, COLOR_WHITE)
        surface.blit(txt, (self.rect.x, self.rect.y - 18))


seismic_box = pygame.Rect(30, 80, 450, 200)
seismic_particles = []
cols, rows = 32, 10
s_spacing_x = seismic_box.width / (cols - 1)
s_spacing_y = seismic_box.height / (rows - 1)

for r in range(rows):
    for c in range(cols):
        px = seismic_box.x + c * s_spacing_x
        py = seismic_box.y + r * s_spacing_y
        seismic_particles.append({'orig_x': px, 'orig_y': py, 'x': px, 'y': py})


slider_s_amp = CompactSlider(30, 310, 210, 0.0, 30.0, 12.0, "Amp Seism", "px", COLOR_CYAN)
slider_s_freq = CompactSlider(270, 310, 210, 0.5, 5.0, 2.0, "Freq Seism", "Hz", COLOR_CYAN)
slider_s_type = CompactSlider(30, 360, 210, 0.0, 1.0, 0.0, "Tip Undă (0=P, 1=S)", "")

slider_g_amp = CompactSlider(540, 310, 210, 0.0, 40.0, 20.0, "Amp GW (Strain)", "x10⁻²", COLOR_MAGENTA)
slider_g_freq = CompactSlider(780, 310, 210, 0.5, 5.0, 1.5, "Freq Orbitală", "Hz", COLOR_MAGENTA)


gw_center = (760, 180)
gw_grid_size = 130
gw_spacing = 13

def main():
    running = True
    sim_time = 0.0

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)
        sim_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False 
            
            
            slider_s_amp.handle_event(event)
            slider_s_freq.handle_event(event)
            slider_s_type.handle_event(event)
            slider_g_amp.handle_event(event)
            slider_g_freq.handle_event(event)

        s_A, s_f = slider_s_amp.val, slider_s_freq.val
        g_A, g_f = slider_g_amp.val, slider_g_freq.val
        s_omega, g_omega = 2 * math.pi * s_f, 2 * math.pi * g_f
        k_seismic = 0.07

        
        is_s_wave = slider_s_type.val >= 0.5
        for p in seismic_particles:
            phase = (s_omega * sim_time) - (k_seismic * p['orig_x'])
            disp = s_A * math.sin(phase)
            p['x'] = p['orig_x'] + (0 if is_s_wave else disp)
            p['y'] = p['orig_y'] + (disp if is_s_wave else 0)

       
        screen.fill(COLOR_BG)
        
        
        pygame.draw.line(screen, COLOR_PANEL_BORDER, (512, 0), (512, 720), 1)
        pygame.draw.line(screen, COLOR_PANEL_BORDER, (0, 410), (1024, 410), 1)

        
        screen.blit(font_title.render("1. UNDE SEISMICE (Mediu Elastic)", True, COLOR_CYAN), (30, 25))
        pygame.draw.rect(screen, COLOR_PANEL_BG, seismic_box, border_radius=4)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, seismic_box, 1, border_radius=4)
        
        for p in seismic_particles:
            offset = math.hypot(p['x'] - p['orig_x'], p['y'] - p['orig_y'])
            ratio = min(offset / (s_A if s_A > 0 else 1), 1.0)
            p_color = (int(50 + ratio*205), int(180 - ratio*100), 255) if not is_s_wave else (255, int(130 + ratio*125), 50)
            pygame.draw.circle(screen, p_color, (int(p['x']), int(p['y'])), 3)

        
        calc_s = pygame.Rect(30, 440, 452, 250)
        pygame.draw.rect(screen, COLOR_PANEL_BG, calc_s, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, calc_s, 1, border_radius=6)
        lines_s = [
            "  Unda Mecanică: u(x,t) = A * cos(ωt - kx)",
            f"  • Pulsație (ω): {s_omega:.2f} rad/s",
            f"  • Viteza de fază (v): {s_omega/k_seismic:.1f} px/s",
            f"  • Mod: {'Transversal (S)' if is_s_wave else 'Longitudinal (P)'}",
            " ------------------------------------------------",
            "  * Undele P (Primare) comprimă solul (înainte-înapoi).",
            "  * Undele S (Secundare) distorsionează solul în plan",
            "    perpendicular și nu pot trece prin lichide."
        ]
        for idx, line in enumerate(lines_s):
            c = COLOR_CYAN if idx == 0 else (COLOR_TEXT_MUTED if idx >= 5 else COLOR_WHITE)
            screen.blit(font_math.render(line, True, c), (40, 455 + idx * 24))

        
        screen.blit(font_title.render("2. UNDE GRAVITAȚIONALE (Curbura Einstein)", True, COLOR_MAGENTA), (540, 25))
        grav_box = pygame.Rect(540, 80, 450, 200)
        pygame.draw.rect(screen, COLOR_PANEL_BG, grav_box, border_radius=4)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, grav_box, 1, border_radius=4)

        
        h_strain = (g_A / 40.0) * 0.35
        
        gw_points = {}
        for gx in range(-gw_grid_size, gw_grid_size + gw_spacing, gw_spacing):
            for gy in range(-gw_grid_size, gw_grid_size + gw_spacing, gw_spacing):
                r_dist = math.hypot(gx, gy)
                
                
                falloff = math.exp(-(r_dist / 90.0) ** 2)
                
                
                wave_ripple = math.sin(g_omega * sim_time - (0.05 * r_dist))
                h_dynamic = h_strain * wave_ripple * falloff
                
                
                new_x = gx * (1.0 + h_dynamic)
                new_y = gy * (1.0 - h_dynamic)
                
                gw_points[(gx, gy)] = (gw_center[0] + new_x, gw_center[1] + new_y)

        
        for gx in range(-gw_grid_size, gw_grid_size + gw_spacing, gw_spacing):
            for gy in range(-gw_grid_size, gw_grid_size + gw_spacing, gw_spacing):
                p_curr = gw_points[(gx, gy)]
                if (gx + gw_spacing, gy) in gw_points:
                    pygame.draw.line(screen, COLOR_GRID_LINE, p_curr, gw_points[(gx + gw_spacing, gy)], 1)
                if (gx, gy + gw_spacing) in gw_points:
                    pygame.draw.line(screen, COLOR_GRID_LINE, p_curr, gw_points[(gx, gy + gw_spacing)], 1)

        
        rot_r = 18
        orb_angle = sim_time * g_omega
        bh1 = (int(gw_center[0] + rot_r * math.cos(orb_angle)), int(gw_center[1] + rot_r * math.sin(orb_angle)))
        bh2 = (int(gw_center[0] - rot_r * math.cos(orb_angle)), int(gw_center[1] - rot_r * math.sin(orb_angle)))
        pygame.draw.circle(screen, (0, 0, 0), bh1, 7)
        pygame.draw.circle(screen, COLOR_MAGENTA, bh1, 7, 2)
        pygame.draw.circle(screen, (0, 0, 0), bh2, 5)
        pygame.draw.circle(screen, COLOR_WHITE, bh2, 5, 1)

        
        calc_g = pygame.Rect(540, 440, 450, 250)
        pygame.draw.rect(screen, COLOR_PANEL_BG, calc_g, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, calc_g, 1, border_radius=6)
        lines_g = [
            "  Perturbația metrică: g_μν = η_μν + h_μν",
            f"  • Deformare max locală (h): {h_strain:.3f}",
            f"  • Frecvență undă GW: {g_f * 2:.2f} Hz (Dublu f_orb)",
            "  • Atenuare spațială: Gaussiană exp(-r²)",
            " ------------------------------------------------",
            "  * Spațiul se dilată pe o axă în timp ce se",
            "    contractă pe cealaltă (Polarizare '+').",
            "  * NU există suport material; este o undă de geometrie",
            "    pură care se propagă cu viteza luminii (c)."
        ]
        for idx, line in enumerate(lines_g):
            c = COLOR_MAGENTA if idx == 0 else (COLOR_TEXT_MUTED if idx >= 5 else COLOR_WHITE)
            screen.blit(font_math.render(line, True, c), (550, 455 + idx * 24))

       
        slider_s_amp.draw(screen)
        slider_s_freq.draw(screen)
        slider_s_type.draw(screen)
        slider_g_amp.draw(screen)
        slider_g_freq.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
