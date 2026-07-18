import pygame
import sys
import math
import random


pygame.init()
pygame.font.init()

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 850  
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Laborator Virtual: Termodinamică și Dinamică Moleculară")


COLOR_BG = (10, 11, 15)
COLOR_PANEL_BG = (18, 20, 28)
COLOR_PANEL_BORDER = (35, 42, 60)
COLOR_WHITE = (240, 240, 250)
COLOR_TEXT_MUTED = (110, 125, 150)
COLOR_CYAN = (0, 210, 255)
COLOR_GREEN = (140, 255, 100)
COLOR_ORANGE = (255, 135, 50)
COLOR_RED = (230, 75, 75)
COLOR_PISTON = (100, 115, 130)

font_title = pygame.font.SysFont("Segoe UI", 16, bold=True)
font_ui = pygame.font.SysFont("Segoe UI", 13, bold=True)
font_math = pygame.font.SysFont("Consolas", 13)

clock = pygame.time.Clock()
FPS = 60


class Molecule:
    def __init__(self, x_min, x_max, y_min, y_max):
        self.x = random.uniform(x_min, x_max)
        self.y = random.uniform(y_min, y_max)
        angle = random.uniform(0, 2 * math.pi)
        self.speed = 2.0
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

    def update(self, x_min, x_max, y_min, y_max, speed_factor):
        
        current_speed = self.speed * speed_factor
        
        
        v_len = math.hypot(self.vx, self.vy)
        if v_len > 0:
            self.vx = (self.vx / v_len) * current_speed
            self.vy = (self.vy / v_len) * current_speed

        self.x += self.vx
        self.y += self.vy

        
        if self.x <= x_min + 3: self.x = x_min + 3; self.vx *= -1
        if self.x >= x_max - 3: self.x = x_max - 3; self.vx *= -1
        if self.y <= y_min + 3: self.y = y_min + 3; self.vy *= -1
        if self.y >= y_max - 3: self.y = y_max - 3; self.vy *= -1

    def draw(self, surface, color):
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 3)


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


view_izobar = pygame.Rect(30, 70, 500, 390)
view_izocor = pygame.Rect(570, 70, 500, 390)

panel_data_izobar = pygame.Rect(30, 480, 500, 150)
panel_data_izocor = pygame.Rect(570, 480, 500, 150)


panel_sliders = pygame.Rect(30, 650, 1040, 100)
panel_footer = pygame.Rect(30, 765, 1040, 65)


btn_start_izobar = pygame.Rect(45, 115, 95, 26)
btn_start_izocor = pygame.Rect(585, 115, 95, 26)
btn_preset_izobar = pygame.Rect(150, 115, 180, 26)
btn_preset_izocor = pygame.Rect(690, 115, 180, 26)
btn_reset_global = pygame.Rect(960, 20, 100, 26)


slider_rate_izobar = CompactSlider(50, 710, 200, 0.0, 150.0, 30.0, "Debit Căldură (Q/s)", " J/s", COLOR_CYAN)
slider_n_izobar = CompactSlider(300, 710, 200, 0.1, 2.0, 1.0, "Cantitate gaz (n)", " moli", COLOR_CYAN)

slider_rate_izocor = CompactSlider(590, 710, 200, 0.0, 150.0, 30.0, "Debit Căldură (Q/s)", " J/s", COLOR_GREEN)
slider_n_izocor = CompactSlider(840, 710, 200, 0.1, 2.0, 1.0, "Cantitate gaz (n)", " moli", COLOR_GREEN)


R_CONSTANT = 8.314  
Cv = 1.5 * R_CONSTANT
Cp = 2.5 * R_CONSTANT
T0 = 300.0          
V0 = 1.0            
P0 = 2.0            

Q_total_izobar = 0.0; T_izobar = T0; V_izobar = V0; P_izobar = P0; play_izobar = False
Q_total_izocor = 0.0; T_izocor = T0; V_izocor = V0; P_izocor = P0; play_izocor = False


molecules_izobar = [Molecule(160, 280, 250, 350) for _ in range(30)]
molecules_izocor = [Molecule(700, 820, 250, 350) for _ in range(30)]

def main():
    global Q_total_izobar, T_izobar, V_izobar, P_izobar, play_izobar
    global Q_total_izocor, T_izocor, V_izocor, P_izocor, play_izocor

    while True:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(COLOR_BG)

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 
            
            
            slider_rate_izobar.handle_event(event)
            slider_n_izobar.handle_event(event)
            slider_rate_izocor.handle_event(event)
            slider_n_izocor.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_start_izobar.collidepoint(mouse_pos):
                    play_izobar = not play_izobar
                elif btn_start_izocor.collidepoint(mouse_pos):
                    play_izocor = not play_izocor
                
                elif btn_preset_izobar.collidepoint(mouse_pos):
                    slider_rate_izobar.val = 130.0
                    slider_n_izobar.val = 0.3
                    slider_rate_izobar.update_handle()
                    slider_n_izobar.update_handle()
                
                elif btn_preset_izocor.collidepoint(mouse_pos):
                    slider_rate_izocor.val = 130.0
                    slider_n_izocor.val = 0.3
                    slider_rate_izocor.update_handle()
                    slider_n_izocor.update_handle()

                elif btn_reset_global.collidepoint(mouse_pos):
                    play_izobar = False; play_izocor = False
                    Q_total_izobar = 0.0; T_izobar = T0; V_izobar = V0; P_izobar = P0
                    Q_total_izocor = 0.0; T_izocor = T0; V_izocor = V0; P_izocor = P0

       
        if play_izobar:
            dQ_izobar = slider_rate_izobar.val / FPS
            Q_total_izobar += dQ_izobar
            T_izobar += dQ_izobar / (slider_n_izobar.val * Cp)
            V_izobar = V0 * (T_izobar / T0)

        if play_izocor:
            dQ_izocor = slider_rate_izocor.val / FPS
            Q_total_izocor += dQ_izocor
            T_izocor += dQ_izocor / (slider_n_izocor.val * Cv)
            P_izocor = P0 * (T_izocor / T0)

        delta_U_izobar = slider_n_izobar.val * Cv * (T_izobar - T0)
        L_izobar = Q_total_izobar - delta_U_izobar

        delta_U_izocor = Q_total_izocor
        L_izocor = 0.0

        
        screen.blit(font_title.render("LABORATOR VIRTUAL: BILANȚ TERMODINAMIC ȘI DINAMICĂ MOLECULARĂ", True, COLOR_WHITE), (30, 25))
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, btn_reset_global, border_radius=4)
        txt_res = font_ui.render("RESET TOTAL", True, COLOR_WHITE)
        screen.blit(txt_res, (btn_reset_global.centerx - txt_res.get_width()//2, btn_reset_global.centery - 8))

        
        pygame.draw.rect(screen, COLOR_PANEL_BG, view_izobar, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, view_izobar, 1, border_radius=6)
        screen.blit(font_ui.render("TRANSFORMARE IZOBARĂ (P = Const.)", True, COLOR_CYAN), (45, 85))

        pygame.draw.rect(screen, COLOR_RED if play_izobar else COLOR_CYAN, btn_start_izobar, border_radius=4)
        screen.blit(font_ui.render("PAUZĂ" if play_izobar else "START LIVE", True, COLOR_BG), (btn_start_izobar.x + 12, btn_start_izobar.y + 4))
        
        pygame.draw.rect(screen, (25, 35, 60), btn_preset_izobar, border_radius=4)
        pygame.draw.rect(screen, COLOR_CYAN, btn_preset_izobar, 1, border_radius=4)
        screen.blit(font_ui.render("Preset: Expansiune Rapidă", True, COLOR_CYAN), (btn_preset_izobar.x + 15, btn_preset_izobar.y + 4))

        cil_x = view_izobar.centerx - 60
        cil_y_baza = view_izobar.y + 350
        cil_w = 120
        h_piston_izobar = min(210, 70 * V_izobar)
        y_piston_izobar = cil_y_baza - h_piston_izobar

        
        r_f = min(255, int(40 + (T_izobar - T0) * 0.4))
        b_f = max(40, int(180 - (T_izobar - T0) * 0.3))
        pygame.draw.rect(screen, (r_f, 50, b_f), (cil_x + 4, int(y_piston_izobar), cil_w - 8, int(h_piston_izobar)), border_radius=2)

        
        speed_factor_izobar = math.sqrt(T_izobar / T0)
        for m in molecules_izobar:
            m.update(cil_x + 4, cil_x + cil_w - 4, y_piston_izobar, cil_y_baza, speed_factor_izobar)
            m.draw(screen, COLOR_WHITE)

        
        pygame.draw.line(screen, COLOR_WHITE, (cil_x, view_izobar.y + 150), (cil_x, cil_y_baza), 3)
        pygame.draw.line(screen, COLOR_WHITE, (cil_x + cil_w, view_izobar.y + 150), (cil_x + cil_w, cil_y_baza), 3)
        pygame.draw.line(screen, COLOR_WHITE, (cil_x, cil_y_baza), (cil_x + cil_w, cil_y_baza), 3)
        pygame.draw.rect(screen, COLOR_PISTON, (cil_x + 2, int(y_piston_izobar), cil_w - 4, 14), border_radius=2)


        
        pygame.draw.rect(screen, COLOR_PANEL_BG, view_izocor, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, view_izocor, 1, border_radius=6)
        screen.blit(font_ui.render("TRANSFORMARE IZOCORĂ (V = Const.)", True, COLOR_GREEN), (585, 85))

        pygame.draw.rect(screen, COLOR_RED if play_izocor else COLOR_GREEN, btn_start_izocor, border_radius=4)
        screen.blit(font_ui.render("PAUZĂ" if play_izocor else "START LIVE", True, COLOR_BG), (btn_start_izocor.x + 12, btn_start_izocor.y + 4))

        pygame.draw.rect(screen, (25, 45, 35), btn_preset_izocor, border_radius=4)
        pygame.draw.rect(screen, COLOR_GREEN, btn_preset_izocor, 1, border_radius=4)
        screen.blit(font_ui.render("Preset: Suprapresiune Șoc", True, COLOR_GREEN), (btn_preset_izocor.x + 15, btn_preset_izocor.y + 4))

        cil_x_m = view_izocor.centerx - 60
        cil_y_baza_m = view_izocor.y + 350
        h_piston_izocor = 70 * V0
        y_piston_izocor = cil_y_baza_m - h_piston_izocor

        
        r_m = min(255, int(40 + (T_izocor - T0) * 0.6))
        b_m = max(40, int(180 - (T_izocor - T0) * 0.5))
        pygame.draw.rect(screen, (r_m, 40, b_m), (cil_x_m + 4, int(y_piston_izocor), cil_w - 8, int(h_piston_izocor)), border_radius=2)

        
        speed_factor_izocor = math.sqrt(T_izocor / T0)
        for m in molecules_izocor:
            m.update(cil_x_m + 4, cil_x_m + cil_w - 4, y_piston_izocor, cil_y_baza_m, speed_factor_izocor)
            m.draw(screen, COLOR_WHITE)

        
        pygame.draw.line(screen, COLOR_WHITE, (cil_x_m, view_izocor.y + 150), (cil_x_m, cil_y_baza_m), 3)
        pygame.draw.line(screen, COLOR_WHITE, (cil_x_m + cil_w, view_izocor.y + 150), (cil_x_m + cil_w, cil_y_baza_m), 3)
        pygame.draw.line(screen, COLOR_WHITE, (cil_x_m, cil_y_baza_m), (cil_x_m + cil_w, cil_y_baza_m), 3)
        pygame.draw.rect(screen, COLOR_PISTON, (cil_x_m + 2, int(y_piston_izocor), cil_w - 4, 14), border_radius=2)
        pygame.draw.circle(screen, COLOR_RED, (cil_x_m - 6, int(y_piston_izocor + 7)), 6)
        pygame.draw.circle(screen, COLOR_RED, (cil_x_m + cil_w + 6, int(y_piston_izocor + 7)), 6)


        
        
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_data_izobar, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_data_izobar, 1, border_radius=6)
        lines_f = [
            f"PRESIUNE (P):         {P_izobar:.2f} atm (CONSTANTĂ)",
            f"VOLUM (V):            {V_izobar:.2f} Litri",
            f"TEMPERATURĂ (T):      {T_izobar:.1f} K  | ΔT: +{(T_izobar - T0):.1f} K",
            f"BILANȚ ENERGETIC: Q({Q_total_izobar:.1f}J) = ΔU({delta_U_izobar:.1f}J) + L({L_izobar:.1f}J)"
        ]
        for idx, line in enumerate(lines_f):
            col = COLOR_CYAN if idx == 3 else COLOR_WHITE
            screen.blit(font_math.render(line, True, col), (45, panel_data_izobar.y + 20 + idx * 24))

       
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_data_izocor, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_data_izocor, 1, border_radius=6)
        lines_m = [
            f"PRESIUNE (P):         {P_izocor:.2f} atm (CREȘTE EXPONENȚIAL)",
            f"VOLUM (V):            {V_izocor:.2f} Litri (BLOCAT)",
            f"TEMPERATURĂ (T):      {T_izocor:.1f} K  | ΔT: +{(T_izocor - T0):.1f} K",
            f"BILANȚ ENERGETIC: Q({Q_total_izocor:.1f}J) = ΔU({delta_U_izocor:.1f}J) + L({L_izocor:.1f}J)"
        ]
        for idx, line in enumerate(lines_m):
            col = COLOR_GREEN if idx == 3 else COLOR_WHITE
            screen.blit(font_math.render(line, True, col), (585, panel_data_izocor.y + 20 + idx * 24))


        
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_sliders, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_sliders, 1, border_radius=6)
        slider_rate_izobar.draw(screen)
        slider_n_izobar.draw(screen)
        slider_rate_izocor.draw(screen)
        slider_n_izocor.draw(screen)

        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_footer, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_footer, 1, border_radius=6)
        notes = [
            "• REZOLVARE: Interfața a fost recalibrată, sliderele sunt izolate jos pentru a preveni orice formă de suprapunere textuală.",
            "• VIZUALIZARE MOLECULARĂ: Particulele albe simulează energia cinetică medie; în transformarea izocoră, agitația lor devine violentă!"
        ]
        for idx, note in enumerate(notes):
            screen.blit(font_math.render(note, True, COLOR_TEXT_MUTED), (45, panel_footer.y + 12 + idx * 22))

        pygame.display.flip()

if __name__ == "__main__":
    main()
