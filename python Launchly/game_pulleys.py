import pygame
import sys
import math

# --- INIȚIALIZARE ---
pygame.init()
pygame.font.init()

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 820
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Laborator Fizică: Scripeți Independenți (Control prin Slidere)")

# Culori Premium (Sci-Fi Dashboard)
COLOR_BG = (10, 11, 15)
COLOR_PANEL_BG = (18, 20, 28)
COLOR_PANEL_BORDER = (35, 42, 60)
COLOR_WHITE = (240, 240, 250)
COLOR_TEXT_MUTED = (110, 125, 150)
COLOR_ROPE = (225, 175, 115)
COLOR_METAL = (140, 155, 175)
COLOR_WEIGHT = (210, 75, 75)
COLOR_CYAN = (0, 210, 255)
COLOR_GREEN = (140, 255, 100)

font_title = pygame.font.SysFont("Segoe UI", 16, bold=True)
font_ui = pygame.font.SysFont("Segoe UI", 13, bold=True)
font_math = pygame.font.SysFont("Consolas", 13)

clock = pygame.time.Clock()
FPS = 60

# --- CLASA SLIDER COMPACT ---
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

# --- ZONE DE RENDERING (Dimensiuni Corectate) ---
view_fix = pygame.Rect(30, 70, 500, 410)
view_mobil = pygame.Rect(570, 70, 500, 410)

# Panouri mai înalte pentru a încăpea perfect textul și sliderele
panel_data_fix = pygame.Rect(30, 495, 500, 205)
panel_data_mobil = pygame.Rect(570, 495, 500, 205)

# Footer-ul a fost coborât
panel_footer = pygame.Rect(30, 715, 1040, 80)

# --- REORGANIZARE COMPACTĂ SLIDERE (Fără Suprapunere) ---
slider_mass_fix = CompactSlider(50, 635, 200, 20.0, 200.0, 100.0, "Masă Sarcină (G)", " N", COLOR_CYAN)
slider_fric_fix = CompactSlider(300, 635, 200, 0.0, 40.0, 0.0, "Frecare Ax", " N", COLOR_CYAN)
slider_pull_fix = CompactSlider(50, 680, 450, 0.0, 100.0, 0.0, "Tracțiune Coardă (s)", " %", COLOR_CYAN)

slider_mass_mobil = CompactSlider(590, 635, 200, 20.0, 200.0, 100.0, "Masă Sarcină (G)", " N", COLOR_GREEN)
slider_fric_mobil = CompactSlider(840, 635, 200, 0.0, 40.0, 0.0, "Frecare Ax", " N", COLOR_GREEN)
slider_pull_mobil = CompactSlider(590, 680, 450, 0.0, 100.0, 0.0, "Tracțiune Coardă (s)", " %", COLOR_GREEN)

def main():
    R = 24  # Raza scripetelui
    
    while True:
        clock.tick(FPS)
        screen.fill(COLOR_BG)

        # --- GESTIONARE EVENIMENTE ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Rută de urgență ESC înapoi la Hub
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

            # Evenimente slidere stânga
            slider_mass_fix.handle_event(event)
            slider_fric_fix.handle_event(event)
            slider_pull_fix.handle_event(event)
            
            # Evenimente slidere dreapta
            slider_mass_mobil.handle_event(event)
            slider_fric_mobil.handle_event(event)
            slider_pull_mobil.handle_event(event)

        # Preluare dinamică a valorilor din noile slidere de pull
        pull_percent_fix = slider_pull_fix.val
        pull_percent_mobil = slider_pull_mobil.val

       
        screen.blit(font_title.render("SISTEM DE SIMULARE FIZICĂ: ANALIZA LUCRULUI MECANIC ȘI A RANDAMENTULUI REAL", True, COLOR_WHITE), (30, 25))

        # ================= 1. VIZUALIZARE: SCRIPETE FIX (STÂNGA) =================
        pygame.draw.rect(screen, COLOR_PANEL_BG, view_fix, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, view_fix, 1, border_radius=6)
        screen.blit(font_ui.render("SCRIPETE FIX (Controlați deplasarea din slider-ul de jos)", True, COLOR_CYAN), (45, 85))

        G_fix = slider_mass_fix.val
        Fricare_fix = slider_fric_fix.val  
        p_fix = pull_percent_fix / 100.0

        h_fix = p_fix * 1.5      
        s_fix = p_fix * 1.5      
        F_real_fix = G_fix + Fricare_fix  
        L_util_fix = G_fix * h_fix
        L_cons_fix = F_real_fix * s_fix
        eta_fix = (L_util_fix / L_cons_fix * 100) if L_cons_fix > 0 else 100.0

        tavan_fix_y = view_fix.y + 60
        center_fix = (view_fix.centerx, tavan_fix_y + 45)
        
        pygame.draw.line(screen, COLOR_WHITE, (view_fix.x + 60, tavan_fix_y), (view_fix.right - 60, tavan_fix_y), 3)
        pygame.draw.line(screen, COLOR_METAL, (center_fix[0], tavan_fix_y), (center_fix[0], center_fix[1]), 5)
        
        y_greutate_fix = (center_fix[1] + 210) - (p_fix * 180)
        y_maner_fix = (center_fix[1] + 30) + (p_fix * 180)

        pygame.draw.line(screen, COLOR_ROPE, (center_fix[0] - R, center_fix[1]), (center_fix[0] - R, y_greutate_fix), 2)
        pygame.draw.line(screen, COLOR_ROPE, (center_fix[0] + R, center_fix[1]), (center_fix[0] + R, y_maner_fix), 2)
        pygame.draw.arc(screen, COLOR_ROPE, (center_fix[0] - R, center_fix[1] - R, R*2, R*2), 0, math.pi, 2)
        
        pygame.draw.circle(screen, COLOR_METAL, center_fix, R)
        pygame.draw.circle(screen, COLOR_BG, center_fix, 6)

        rect_g_fix = pygame.Rect(center_fix[0] - R - 15, y_greutate_fix, 38, 34)
        pygame.draw.rect(screen, COLOR_WEIGHT, rect_g_fix, border_radius=4)
        screen.blit(font_ui.render("G", True, COLOR_WHITE), (rect_g_fix.centerx - 6, rect_g_fix.centery - 8))

        pygame.draw.circle(screen, COLOR_CYAN, (center_fix[0] + R, int(y_maner_fix)), 8)
        pygame.draw.circle(screen, COLOR_WHITE, (center_fix[0] + R, int(y_maner_fix)), 3)

        # ================= 2. VIZUALIZARE: SCRIPETE MOBIL (DREAPTA) =================
        pygame.draw.rect(screen, COLOR_PANEL_BG, view_mobil, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, view_mobil, 1, border_radius=6)
        screen.blit(font_ui.render("SCRIPETE MOBIL (Controlați deplasarea din slider-ul de jos)", True, COLOR_GREEN), (585, 85))

        G_mobil = slider_mass_mobil.val
        Fricare_mobil = slider_fric_mobil.val  
        p_mobil = pull_percent_mobil / 100.0

        s_mobil = p_mobil * 1.5
        h_mobil = s_mobil / 2.0  
        F_real_mobil = (G_mobil / 2.0) + Fricare_mobil  
        L_util_mobil = G_mobil * h_mobil
        L_cons_mobil = F_real_mobil * s_mobil
        eta_mobil = (L_util_mobil / L_cons_mobil * 100) if L_cons_mobil > 0 else 100.0

        tavan_mobil_y = view_mobil.y + 60
        pygame.draw.line(screen, COLOR_WHITE, (view_mobil.x + 60, tavan_mobil_y), (view_mobil.right - 60, tavan_mobil_y), 3)
        pygame.draw.circle(screen, COLOR_METAL, (view_mobil.x + 200 - R, tavan_mobil_y), 4)

        y_centru_scripete_mobil = (tavan_mobil_y + 230) - (h_mobil * 120 * 2)
        y_maner_mobil = (tavan_mobil_y + 230) - (s_mobil * 120 * 2)

        pygame.draw.line(screen, COLOR_ROPE, (view_mobil.x + 200 - R, tavan_mobil_y), (view_mobil.x + 200 - R, y_centru_scripete_mobil), 2)
        pygame.draw.line(screen, COLOR_ROPE, (view_mobil.x + 200 + R, y_centru_scripete_mobil), (view_mobil.x + 200 + R, y_maner_mobil), 2)
        pygame.draw.arc(screen, COLOR_ROPE, (view_mobil.x + 200 - R, y_centru_scripete_mobil - R, R*2, R*2), math.pi, 2*math.pi, 2)

        pygame.draw.circle(screen, COLOR_METAL, (view_mobil.x + 200, int(y_centru_scripete_mobil)), R)
        pygame.draw.circle(screen, COLOR_BG, (view_mobil.x + 200, int(y_centru_scripete_mobil)), 6)
        pygame.draw.line(screen, COLOR_METAL, (view_mobil.x + 200, y_centru_scripete_mobil), (view_mobil.x + 200, y_centru_scripete_mobil + R + 5), 4)

        rect_g_mobil = pygame.Rect(view_mobil.x + 200 - 19, y_centru_scripete_mobil + R + 5, 38, 34)
        pygame.draw.rect(screen, COLOR_WEIGHT, rect_g_mobil, border_radius=4)
        screen.blit(font_ui.render("G", True, COLOR_WHITE), (rect_g_mobil.centerx - 6, rect_g_mobil.centery - 8))

        pygame.draw.circle(screen, COLOR_GREEN, (view_mobil.x + 200 + R, int(y_maner_mobil)), 8)
        pygame.draw.circle(screen, COLOR_WHITE, (view_mobil.x + 200 + R, int(y_maner_mobil)), 3)

        # ================= 3. DASHBOARD DATE PANOURI =================
        
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_data_fix, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_data_fix, 1, border_radius=6)
        
        lines_f = [
            f"FORȚĂ REALĂ APLICATĂ: {F_real_fix:.1f} N",
            f"Distanța sfoară (s):  {s_fix:.2f} m   | Înălțime sarcină (h): {h_fix:.2f} m",
            f"Lucru Mecanic Util:   {L_util_fix:.1f} J   | Lucru Consumat:      {L_cons_fix:.1f} J",
            f"RANDAMENT SISTEM (η): {eta_fix:.1f} %"
        ]
        for idx, line in enumerate(lines_f):
            col = COLOR_CYAN if idx in [0, 3] else COLOR_WHITE
            screen.blit(font_math.render(line, True, col), (45, panel_data_fix.y + 15 + idx * 20))

        # Panou Dreapta: Date Scripete Mobil
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_data_mobil, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_data_mobil, 1, border_radius=6)
        
        lines_m = [
            f"FORȚĂ REALĂ APLICATĂ: {F_real_mobil:.1f} N  (G/2 + Frecare)",
            f"Distanța sfoară (s):  {s_mobil:.2f} m   | Înălțime sarcină (h): {h_mobil:.2f} m",
            f"Lucru Mecanic Util:   {L_util_mobil:.1f} J   | Lucru Consumat:      {L_cons_mobil:.1f} J",
            f"RANDAMENT SISTEM (η): {eta_mobil:.1f} %"
        ]
        for idx, line in enumerate(lines_m):
            col = COLOR_GREEN if idx in [0, 3] else COLOR_WHITE
            screen.blit(font_math.render(line, True, col), (585, panel_data_mobil.y + 15 + idx * 20))

        # Sub-sol
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_footer, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_footer, 1, border_radius=6)
        
        footer_notes = [
            "• OBSERVAȚIE PRACTICĂ: Când Frecarea = 0 N, ambele sisteme consumă EXACT același Lucru Mecanic (Randament 100%).",
            "• EFECTUL FRECĂRII REALE: Dacă mărești Frecarea Axului, Forța aplicată crește, iar Lucrul Consumat depășește Lucrul Util (Restul devine căldură)."
        ]
        for idx, note in enumerate(footer_notes):
            screen.blit(font_math.render(note, True, COLOR_TEXT_MUTED), (45, panel_footer.y + 16 + idx * 22))

        # Afișare Slidere Active
        slider_mass_fix.draw(screen)
        slider_fric_fix.draw(screen)
        slider_pull_fix.draw(screen)
        
        slider_mass_mobil.draw(screen)
        slider_fric_mobil.draw(screen)
        slider_pull_mobil.draw(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main()
