import pygame
import sys
import math

# --- INIȚIALIZARE ---
pygame.init()
pygame.font.init()

# Rezoluție extinsă (1100x720) - elimină complet orice suprapunere în UI
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Prezentare Fizică: Principiul lui Pascal & Presa Hidraulică")

# --- PALETĂ CULORI CONTRASTANTE ---
COLOR_BG = (10, 15, 26)
COLOR_PANEL = (20, 27, 45)
COLOR_BORDER = (51, 65, 85)
COLOR_FLUID = (14, 165, 233)
COLOR_FLUID_BG = (8, 38, 61)
COLOR_PISTON = (148, 163, 184)
COLOR_CEILING = (71, 85, 105)
COLOR_WHITE = (248, 250, 252)
COLOR_TEXT_MUTED = (100, 116, 139)
COLOR_CYAN = (6, 182, 212)
COLOR_GREEN = (34, 197, 94)
COLOR_RED = (239, 68, 68)
COLOR_YELLOW = (234, 179, 8)

font_title = pygame.font.SysFont("Segoe UI", 15, bold=True)
font_subtitle = pygame.font.SysFont("Segoe UI", 12, bold=True)
font_ui = pygame.font.SysFont("Segoe UI", 11, bold=True)
font_mono = pygame.font.SysFont("Consolas", 10, bold=True)

clock = pygame.time.Clock()
FPS = 60

canvas_rect = pygame.Rect(20, 20, 720, 680)
panel_rect = pygame.Rect(760, 20, 315, 680)

class ModernSlider:
    def __init__(self, x, y, w, min_val, max_val, start_val, label, unit):
        self.rect = pygame.Rect(x, y, w, 6)
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.label = label
        self.unit = unit
        self.handle_pos = [x, y + 3]
        self.update_handle()
        self.dragging = False

    def update_handle(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_pos[0] = self.rect.x + ratio * self.rect.width

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if math.hypot(event.pos[0] - self.handle_pos[0], event.pos[1] - self.handle_pos[1]) <= 10 or self.rect.inflate(0, 14).collidepoint(event.pos):
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
        lbl_surf = font_ui.render(f"{self.label}: {self.val:.1f} {self.unit}", True, COLOR_WHITE)
        surface.blit(lbl_surf, (self.rect.x, self.rect.y - 18))

class ModernButton:
    def __init__(self, x, y, w, h, text, base_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.base_color = base_color
        self.is_selected = False

    def draw(self, surface, mouse_pos):
        if self.is_selected:
            draw_color = COLOR_CYAN
        elif self.rect.collidepoint(mouse_pos):
            draw_color = tuple(min(255, c + 25) for c in self.base_color)
        else:
            draw_color = self.base_color

        pygame.draw.rect(surface, draw_color, self.rect, border_radius=5)
        txt_color = COLOR_BG if self.is_selected else COLOR_WHITE
        txt_surf = font_ui.render(self.text, True, txt_color)
        surface.blit(txt_surf, (self.rect.centerx - txt_surf.get_width() // 2, self.rect.centery - txt_surf.get_height() // 2))

class TargetObject:
    def __init__(self, name, resistance, color):
        self.name = name
        self.resistance = resistance
        self.color = color

    def draw(self, surface, cx, cy, is_crushed):
        if self.name == "Minge fotbal":
            r = 22
            if is_crushed:
                pygame.draw.ellipse(surface, self.color, (cx - r - 10, cy - 6, (r + 10) * 2, 12))
            else:
                pygame.draw.circle(surface, self.color, (cx, cy - r), r)
                pygame.draw.circle(surface, COLOR_BG, (cx, cy - r), r, 2)
        elif self.name == "Mașină veche":
            w, h = 76, 28
            if is_crushed:
                pygame.draw.polygon(surface, self.color, [(cx - w//2 - 5, cy), (cx - w//4, cy - 5), (cx + w//4, cy - 4), (cx + w//2 + 5, cy)])
            else:
                pygame.draw.rect(surface, self.color, (cx - w//2, cy - h, w, h//2), border_radius=3)
                pygame.draw.rect(surface, self.color, (cx - w//4, cy - h - h//2, w//2, h//2), border_radius=2)
                pygame.draw.circle(surface, COLOR_BG, (cx - w//4, cy), 6)
                pygame.draw.circle(surface, COLOR_BG, (cx + w//4, cy), 6)
        elif self.name == "Diamant":
            w, h = 30, 30
            if is_crushed:
                for o in [-12, -4, 4, 12]:
                    pygame.draw.polygon(surface, self.color, [(cx+o, cy), (cx+o+3, cy-5), (cx+o+5, cy)])
            else:
                pts = [(cx, cy - h), (cx + w//2, cy - h//3 * 2), (cx + w//2, cy - h//3), (cx, cy), (cx - w//2, cy - h//3), (cx - w//2, cy - h//3 * 2)]
                pygame.draw.polygon(surface, self.color, pts)
                pygame.draw.polygon(surface, COLOR_WHITE, pts, 1)

def main():
    objects = [
        TargetObject("Minge fotbal", 200, (241, 245, 249)),
        TargetObject("Mașină veche", 5000, COLOR_RED),
        TargetObject("Diamant", 35000, COLOR_CYAN) # Ajustat pentru echilibru cu noul scenariu 3
    ]
    active_obj_idx = 1

    # Slidere spațiate perfect
    slider_f1 = ModernSlider(panel_rect.x + 20, 120, 275, 10, 1000, 350, "Forță Sursă F1", "N")
    slider_d1 = ModernSlider(panel_rect.x + 20, 175, 275, 2.0, 10.0, 4.5, "Diametru d1", "cm")
    slider_d2 = ModernSlider(panel_rect.x + 20, 230, 275, 15.0, 60.0, 32.0, "Diametru d2", "cm")

    btn_press = ModernButton(panel_rect.x + 20, 270, 275, 35, "💥 LANSEAZĂ PRESA (START)", COLOR_GREEN)
    btn_reset = ModernButton(panel_rect.x + 20, 312, 275, 26, "🔄 Resetare Sistem", (140, 45, 45))

    # Butoane Scenarii Favorabile - Reconfigurate complet pentru a fi funcționale și sigure
    btn_scen1 = ModernButton(panel_rect.x + 20, 390, 275, 25, "Cazul 1: Minge (Raport Mic)", (40, 55, 85))
    btn_scen2 = ModernButton(panel_rect.x + 20, 422, 275, 25, "Cazul 2: Mașină (Echilibrat)", (40, 55, 85))
    btn_scen3 = ModernButton(panel_rect.x + 20, 454, 275, 25, "Cazul 3: Diamant (Raport Optim)", (40, 55, 85))
    
    btn_scen2.is_selected = True

    sim_state = "IDLE"
    fluid_zero_y = 420  # Poziția de start a pistoanelor
    fluid_bottom_limit = 550  # Fundul conductei (cursă maximă)
    ceiling_y = 260  # Plafonul fix unde se strivesc obiectele

    h1_offset = 0.0
    h2_offset = 0.0

    feedback_msg = "Sistem hidraulic pregătit. Selectați un caz din listă și apăsați START."
    feedback_color = COLOR_WHITE

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
                    return # Iese din buclă și închide scriptul elegant
            # -------------------------

            if sim_state == "IDLE":
                slider_f1.handle_event(event)
                slider_d1.handle_event(event)
                slider_d2.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                
                if btn_press.rect.collidepoint(mx, my) and sim_state == "IDLE":
                    sim_state = "ANIMATING"
                    feedback_msg = "Presa funcționează. Presiunea P se transmite integral conform Principiului Pascal."
                    feedback_color = COLOR_YELLOW

                if btn_reset.rect.collidepoint(mx, my):
                    sim_state = "IDLE"
                    h1_offset = 0.0; h2_offset = 0.0
                    feedback_msg = "Presa a fost resetată în starea inițială."
                    feedback_color = COLOR_WHITE

                # LOGICĂ FIXATĂ PENTRU CAZURI FAVORABILE
                if btn_scen1.rect.collidepoint(mx, my) and sim_state == "IDLE":
                    h1_offset = 0.0; h2_offset = 0.0; active_obj_idx = 0
                    btn_scen1.is_selected = True; btn_scen2.is_selected = False; btn_scen3.is_selected = False
                    slider_f1.val, slider_d1.val, slider_d2.val = 400.0, 6.0, 18.0
                    slider_f1.update_handle(); slider_d1.update_handle(); slider_d2.update_handle()
                    feedback_msg = "Cazul 1 Încărcat! Ideal pentru a vedea o cursă rapidă a pistonului 2."
                    feedback_color = COLOR_CYAN

                if btn_scen2.rect.collidepoint(mx, my) and sim_state == "IDLE":
                    h1_offset = 0.0; h2_offset = 0.0; active_obj_idx = 1
                    btn_scen1.is_selected = False; btn_scen2.is_selected = True; btn_scen3.is_selected = False
                    slider_f1.val, slider_d1.val, slider_d2.val = 350.0, 4.5, 32.0
                    slider_f1.update_handle(); slider_d1.update_handle(); slider_d2.update_handle()
                    feedback_msg = "Cazul 2 Încărcat! Raport echilibrat. Pistonul 1 coboară mult, 2 urcă lent."
                    feedback_color = COLOR_CYAN

                if btn_scen3.rect.collidepoint(mx, my) and sim_state == "IDLE":
                    h1_offset = 0.0; h2_offset = 0.0; active_obj_idx = 2
                    btn_scen1.is_selected = False; btn_scen2.is_selected = False; btn_scen3.is_selected = True
                    # Soluție raport: d1=3.5, d2=38.0 oferă destulă cursă ca să atingă tavanul fără să lovească fundul!
                    slider_f1.val, slider_d1.val, slider_d2.val = 450.0, 3.5, 38.0
                    slider_f1.update_handle(); slider_d1.update_handle(); slider_d2.update_handle()
                    feedback_msg = "Cazul 3 Încărcat! Forță masivă multiplicată, optimizată geometric pentru Diamant."
                    feedback_color = COLOR_CYAN

        # --- DINAMICA ȘI FIZICA PRESEI ---
        F1 = slider_f1.val
        d1 = slider_d1.val
        d2 = slider_d2.val

        A1 = math.pi * ((d1 / 2.0) ** 2)
        A2 = math.pi * ((d2 / 2.0) ** 2)
        P_system = F1 / A1
        F2 = P_system * A2
        current_target = objects[active_obj_idx]

        if sim_state == "ANIMATING":
            step_h1 = 1.5
            step_h2 = step_h1 * (A1 / A2)  # Conservarea volumului ($A_1 \cdot h_1 = A_2 \cdot h_2$)

            # Verificare dacă pistonul sorsă a atins fundul conductei
            if (fluid_zero_y + h1_offset + step_h1) >= fluid_bottom_limit:
                sim_state = "LOCKED_FAILURE"
                feedback_msg = "❌ BLOCAJ: Pistonul 1 a atins limita de cursă de jos. Schimbați diametrele!"
                feedback_color = COLOR_RED
            else:
                piston2_y_next = fluid_zero_y - h2_offset - step_h2
                object_height = 28
                
                # Verificare coliziune cu plafonul de strivire
                if (piston2_y_next - object_height) <= ceiling_y:
                    h2_offset = fluid_zero_y - (ceiling_y + object_height)
                    if F2 >= current_target.resistance:
                        sim_state = "SUCCESS_CRUSH"
                        feedback_msg = f"🏆 SUCCES! F2 ({F2:.1f} N) a depășit rezistența de {current_target.resistance} N. Corp Strivit!"
                        feedback_color = COLOR_GREEN
                    else:
                        sim_state = "LOCKED_FAILURE"
                        feedback_msg = "❌ EȘEC: Presa s-a oprit la tavan. Forța rezultată F2 este prea mică."
                        feedback_color = COLOR_RED
                else:
                    h1_offset += step_h1
                    h2_offset += step_h2

        # --- RENDERING GRAFIC CANVASES ---
        pygame.draw.rect(screen, COLOR_PANEL, canvas_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BORDER, canvas_rect, 2, border_radius=6)
        pygame.draw.rect(screen, COLOR_PANEL, panel_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_BORDER, panel_rect, 2, border_radius=6)

        # Axele geometrice ale conductelor
        cx1 = canvas_rect.x + 140
        cx2 = canvas_rect.x + 470
        w1_px = max(16, int(d1 * 9.0))
        w2_px = max(65, int(d2 * 3.8))

        p1_current_y = fluid_zero_y + h1_offset
        p2_current_y = fluid_zero_y - h2_offset

        # Desenare Camere Lichid (Fundal gol + Fluid Activ)
        pygame.draw.rect(screen, COLOR_FLUID_BG, (cx1 - w1_px//2, 180, w1_px, 370))
        pygame.draw.rect(screen, COLOR_FLUID_BG, (cx2 - w2_px//2, 180, w2_px, 370))
        pygame.draw.rect(screen, COLOR_FLUID_BG, (cx1 - w1_px//2, fluid_bottom_limit, (cx2 + w2_px//2) - (cx1 - w1_px//2), 40))

        pygame.draw.rect(screen, COLOR_FLUID, (cx1 - w1_px//2, p1_current_y, w1_px, fluid_bottom_limit - p1_current_y))
        pygame.draw.rect(screen, COLOR_FLUID, (cx2 - w2_px//2, p2_current_y, w2_px, fluid_bottom_limit - p2_current_y))
        pygame.draw.rect(screen, COLOR_FLUID, (cx1 - w1_px//2, fluid_bottom_limit, (cx2 + w2_px//2) - (cx1 - w1_px//2), 40))

        # Contururi Instalație Hidraulică
        pygame.draw.line(screen, COLOR_BORDER, (cx1 - w1_px//2, 180), (cx1 - w1_px//2, fluid_bottom_limit + 40), 3)
        pygame.draw.line(screen, COLOR_BORDER, (cx1 + w1_px//2, 180), (cx1 + w1_px//2, fluid_bottom_limit), 3)
        pygame.draw.line(screen, COLOR_BORDER, (cx1 + w1_px//2, fluid_bottom_limit), (cx2 - w2_px//2, fluid_bottom_limit), 3)
        pygame.draw.line(screen, COLOR_BORDER, (cx2 - w2_px//2, 180), (cx2 - w2_px//2, fluid_bottom_limit), 3)
        pygame.draw.line(screen, COLOR_BORDER, (cx2 + w2_px//2, 180), (cx2 + w2_px//2, fluid_bottom_limit + 40), 3)
        pygame.draw.line(screen, COLOR_BORDER, (cx1 - w1_px//2, fluid_bottom_limit + 40), (cx2 + w2_px//2, fluid_bottom_limit + 40), 3)

        # Componente Mecanice (Pistoane și Plafon de sprijin)
        pygame.draw.rect(screen, COLOR_PISTON, (cx1 - w1_px//2 + 1, p1_current_y, w1_px - 2, 12), border_radius=2)
        pygame.draw.rect(screen, COLOR_PISTON, (cx2 - w2_px//2 + 1, p2_current_y, w2_px - 2, 12), border_radius=2)
        pygame.draw.rect(screen, COLOR_CEILING, (cx2 - 85, ceiling_y - 10, 170, 10), border_radius=2)

        # Randare obiect interactiv
        is_crushed = (sim_state == "SUCCESS_CRUSH")
        current_target.draw(screen, cx2, p2_current_y, is_crushed)

        # Vectori forțe vizuali
        pygame.draw.line(screen, COLOR_YELLOW, (cx1, p1_current_y - 35), (cx1, p1_current_y - 3), 2)
        pygame.draw.polygon(screen, COLOR_YELLOW, [(cx1 - 4, p1_current_y - 8), (cx1, p1_current_y - 2), (cx1 + 4, p1_current_y - 8)])
        screen.blit(font_ui.render(f"F1: {F1:.0f}N", True, COLOR_YELLOW), (cx1 + 8, p1_current_y - 25))

        if sim_state in ["ANIMATING", "SUCCESS_CRUSH", "LOCKED_FAILURE"]:
            pygame.draw.line(screen, COLOR_GREEN, (cx2, p2_current_y + 16), (cx2, p2_current_y + 40), 2)
            screen.blit(font_ui.render(f"F2: {F2:.1f}N", True, COLOR_GREEN), (cx2 + 10, p2_current_y + 18))

        # --- PANOU LATERAL TITLU ȘI CONTROALE ---
        screen.blit(font_title.render("⚙️ PARAMETRII PREZENTARE", True, COLOR_WHITE), (panel_rect.x + 20, panel_rect.y + 15))
        pygame.draw.line(screen, COLOR_BORDER, (panel_rect.x + 20, panel_rect.y + 40), (panel_rect.right - 20, panel_rect.y + 40), 1)

        slider_f1.draw(screen); slider_d1.draw(screen); slider_d2.draw(screen)
        btn_press.draw(screen, mouse_pos); btn_reset.draw(screen, mouse_pos)

        # Panou separat pentru cazuri preconfigurate (Fără intersecții)
        pygame.draw.line(screen, COLOR_BORDER, (panel_rect.x + 20, panel_rect.y + 355), (panel_rect.right - 20, panel_rect.y + 355), 1)
        screen.blit(font_subtitle.render("📋 Demo: Cazuri Preconfigurate", True, COLOR_CYAN), (panel_rect.x + 20, panel_rect.y + 365))
        btn_scen1.draw(screen, mouse_pos); btn_scen2.draw(screen, mouse_pos); btn_scen3.draw(screen, mouse_pos)

        # --- DETALII TEHNICE LIVE INFERIOARE (ALINIERE PERFECTĂ PE COLOANE COORDONATE FIXE) ---
        tech_box = pygame.Rect(canvas_rect.x + 15, canvas_rect.bottom - 110, 690, 95)
        pygame.draw.rect(screen, COLOR_BG, tech_box, border_radius=6)
        pygame.draw.rect(screen, COLOR_BORDER, tech_box, 1, border_radius=6)
        
        screen.blit(font_subtitle.render("📊 RAPORT DE TELEMETRIE ÎN TIMP REAL (PASAL CALCULUS)", True, COLOR_CYAN), (tech_box.x + 12, tech_box.y + 8))
        
        col1_x = tech_box.x + 12
        col2_x = tech_box.x + 240
        col3_x = tech_box.x + 475

        c1_data = [f"• Secțiune S1: {A1:.2f} cm²", f"• Secțiune S2: {A2:.2f} cm²", f"• Presiune P: {P_system:.2f} N/cm²"]
        c2_data = [f"• Cursă Δh1: {h1_offset*0.1:.1f} cm", f"• Cursă Δh2: {h2_offset*0.1:.1f} cm", f"• Multiplicare: X {A2/A1:.1f} ori"]
        c3_data = [f"• Forță Reală F2: {F2:.1f} N", f"• Limită Corp: {current_target.resistance} N", f"• Obiect: {current_target.name}"]

        for idx, text in enumerate(c1_data): screen.blit(font_mono.render(text, True, COLOR_WHITE), (col1_x, tech_box.y + 32 + idx*18))
        for idx, text in enumerate(c2_data): screen.blit(font_mono.render(text, True, COLOR_YELLOW), (col2_x, tech_box.y + 32 + idx*18))
        for idx, text in enumerate(c3_data): screen.blit(font_mono.render(text, True, COLOR_GREEN if "F2" in text or "Reală" in text else COLOR_WHITE), (col3_x, tech_box.y + 32 + idx*18))

        # Alertă Status Superioară (Notificări live)
        info_bar = pygame.Rect(canvas_rect.x + 15, canvas_rect.y + 15, 690, 32)
        pygame.draw.rect(screen, (15, 23, 42, 240), info_bar, border_radius=5)
        pygame.draw.rect(screen, COLOR_BORDER, info_bar, 1, border_radius=5)
        screen.blit(font_ui.render(feedback_msg, True, feedback_color), (info_bar.x + 12, info_bar.y + 8))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
