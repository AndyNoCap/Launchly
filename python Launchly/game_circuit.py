import pygame
import math
import sys
import random

# =====================================================================
# INIȚIALIZARE ȘI CONFIGURARE DE BAZĂ
# =====================================================================
pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1350, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("QuantumCircuit V2.2 PRO - Animație Optimizată")
clock = pygame.time.Clock()

# --- PALETĂ DE CULORI ---
COLOR_BG = (10, 12, 20)
COLOR_PANEL = (20, 24, 38)
COLOR_WIRE = (60, 70, 90)
COLOR_WIRE_OFF = (30, 35, 45)
COLOR_ELECTRON = (0, 255, 255)
COLOR_TEXT = (230, 235, 245)
COLOR_TEXT_MUTED = (130, 140, 160)
COLOR_TEXT_ACTIVE = (0, 255, 150)
COLOR_PRIMARY = (80, 110, 255)
COLOR_HOVER = (110, 140, 255)
COLOR_ACTIVE = (0, 255, 150)
COLOR_WARNING = (255, 80, 80)
COLOR_TOOLTIP = (15, 18, 28)

FONT_SM = pygame.font.Font(None, 18)
FONT_MD = pygame.font.Font(None, 22)
FONT_LG = pygame.font.Font(None, 28)
FONT_MATH = pygame.font.Font(None, 24)

# =====================================================================
# CLASE UI (Interfață)
# =====================================================================
class UISlider:
    def __init__(self, x, y, w, min_val, max_val, initial_val, label, unit):
        self.rect = pygame.Rect(x, y, w, 8)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.label = label
        self.unit = unit
        self.is_dragging = False

    def update(self, mouse_pos, mouse_pressed):
        handle_x = self.rect.x + int(((self.val - self.min_val) / (self.max_val - self.min_val)) * self.rect.width)
        handle_rect = pygame.Rect(handle_x - 10, self.rect.y - 10, 20, 20)
        
        if mouse_pressed[0]:
            if handle_rect.collidepoint(mouse_pos) or (self.rect.collidepoint(mouse_pos) and not self.is_dragging):
                self.is_dragging = True
            if self.is_dragging:
                rel_x = max(0, min(mouse_pos[0] - self.rect.x, self.rect.width))
                self.val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
        else:
            self.is_dragging = False

    def draw(self, surface):
        pygame.draw.rect(surface, (40, 48, 70), self.rect, border_radius=4)
        handle_x = self.rect.x + int(((self.val - self.min_val) / (self.max_val - self.min_val)) * self.rect.width)
        pygame.draw.rect(surface, COLOR_PRIMARY, (self.rect.x, self.rect.y, handle_x - self.rect.x, self.rect.height), border_radius=4)
        
        color = COLOR_ACTIVE if self.is_dragging else COLOR_TEXT
        pygame.draw.circle(surface, color, (handle_x, self.rect.y + 4), 8)
        
        txt = FONT_MD.render(f"{self.label}: {self.val:.2f} {self.unit}", True, COLOR_TEXT)
        surface.blit(txt, (self.rect.x, self.rect.y - 20))

class UIButton:
    def __init__(self, x, y, w, h, text, identity):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.identity = identity

    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click[0]

    def draw(self, surface, active_identity=None):
        is_active = (self.identity == active_identity)
        mouse_pos = pygame.mouse.get_pos()
        
        if is_active:
            bg_col, txt_col = COLOR_ACTIVE, COLOR_BG
        elif self.rect.collidepoint(mouse_pos):
            bg_col, txt_col = COLOR_HOVER, COLOR_TEXT
        else:
            bg_col, txt_col = COLOR_PRIMARY, COLOR_TEXT
            
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=6)
        txt = FONT_MD.render(self.text, True, txt_col)
        surface.blit(txt, (self.rect.x + (self.rect.width - txt.get_width()) // 2, self.rect.y + (self.rect.height - txt.get_height()) // 2))

class UIToggle:
    def __init__(self, x, y, text, initial_state=True):
        self.rect = pygame.Rect(x, y, 50, 24)
        self.text = text
        self.state = initial_state

    def is_clicked(self, mouse_pos, mouse_click):
        if self.rect.collidepoint(mouse_pos) and mouse_click[0]:
            self.state = not self.state
            return True
        return False

    def draw(self, surface):
        bg_col = COLOR_ACTIVE if self.state else (80, 80, 80)
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=12)
        circle_x = self.rect.x + 38 if self.state else self.rect.x + 12
        pygame.draw.circle(surface, COLOR_TEXT, (circle_x, self.rect.y + 12), 10)
        
        lbl = FONT_MD.render(self.text, True, COLOR_TEXT)
        surface.blit(lbl, (self.rect.x + 60, self.rect.y + 4))

# =====================================================================
# MOTORUL DE ANIMAȚIE (FLUIDĂ ȘI COERENTĂ)
# =====================================================================
def draw_electrons_on_path(surface, path, current, spacing=65, speed_factor=50.0):
    if current <= 0.005:
        return
        
    time_sec = pygame.time.get_ticks() / 1000.0
    total_offset = (time_sec * current * speed_factor) % spacing
    
    segments = []
    for i in range(len(path) - 1):
        p1, p2 = path[i], path[i+1]
        dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        segments.append((p1, p2, dist))
        
    total_length = sum(seg[2] for seg in segments)
    current_dist = total_offset
    
    while current_dist < total_length:
        accumulated = 0
        for p1, p2, dist in segments:
            if accumulated <= current_dist <= accumulated + dist:
                factor = (current_dist - accumulated) / dist
                ex = p1[0] + factor * (p2[0] - p1[0])
                ey = p1[1] + factor * (p2[1] - p1[1])
                pygame.draw.circle(surface, COLOR_ELECTRON, (int(ex), int(ey)), 3)
                break
            accumulated += dist
        current_dist += spacing

# =====================================================================
# RENDERING COMPONENTE FIZICE
# =====================================================================
def draw_battery(surface, x, y, vertical=True):
    color = COLOR_TEXT
    rect = pygame.Rect(x-20, y-25, 40, 50) if vertical else pygame.Rect(x-25, y-20, 50, 40)
    
    if vertical:
        pygame.draw.line(surface, color, (x - 18, y - 10), (x + 18, y - 10), 4)
        pygame.draw.line(surface, color, (x - 10, y - 2),  (x + 10, y - 2), 2)
        pygame.draw.line(surface, color, (x - 18, y + 6),  (x + 18, y + 6), 4)
        pygame.draw.line(surface, color, (x - 10, y + 14), (x + 10, y + 14), 2)
    else:
        pygame.draw.line(surface, color, (x - 10, y - 18), (x - 10, y + 18), 4)
        pygame.draw.line(surface, color, (x - 2,  y - 10), (x - 2,  y + 10), 2)
        pygame.draw.line(surface, color, (x + 6,  y - 18), (x + 6,  y + 18), 4)
        pygame.draw.line(surface, color, (x + 14, y - 10), (x + 14, y + 10), 2)
        
    return rect

def draw_resistor(surface, x, y, label, val, power, is_on, vertical=False):
    w, h = (24, 50) if vertical else (50, 24)
    rect = pygame.Rect(x - w//2, y - h//2, w, h)
    
    heat_factor = min(255, int((power / 300.0) * 255)) if is_on else 0
    glow_color = (max(25, heat_factor), max(25, 45 - heat_factor//4), 35)
    
    pygame.draw.rect(surface, glow_color, rect, border_radius=3)
    pygame.draw.rect(surface, COLOR_TEXT, rect, 2, border_radius=3)
    
    txt_lbl = FONT_SM.render(label, True, COLOR_TEXT_ACTIVE if is_on else COLOR_TEXT_MUTED)
    txt_val = FONT_SM.render(f"{val:.1f}Ω", True, COLOR_TEXT)
    
    if vertical:
        surface.blit(txt_lbl, (rect.x + 30, rect.y + 8))
        surface.blit(txt_val, (rect.x + 30, rect.y + 26))
    else:
        surface.blit(txt_lbl, (rect.x + 12, rect.y - 32))
        surface.blit(txt_val, (rect.x + 8, rect.y - 16))
        
    return rect

def draw_switch(surface, x, y, is_closed, vertical=False):
    if vertical:
        pygame.draw.circle(surface, COLOR_TEXT, (x, y - 15), 4)
        pygame.draw.circle(surface, COLOR_TEXT, (x, y + 15), 4)
        if is_closed:
            pygame.draw.line(surface, COLOR_ACTIVE, (x, y - 15), (x, y + 15), 3)
        else:
            pygame.draw.line(surface, COLOR_WARNING, (x, y + 15), (x + 15, y - 10), 3)
    else:
        pygame.draw.circle(surface, COLOR_TEXT, (x - 15, y), 4)
        pygame.draw.circle(surface, COLOR_TEXT, (x + 15, y), 4)
        if is_closed:
            pygame.draw.line(surface, COLOR_ACTIVE, (x - 15, y), (x + 15, y), 3)
        else:
            pygame.draw.line(surface, COLOR_WARNING, (x - 15, y), (x + 10, y - 15), 3)

def draw_tooltip(surface, x, y, lines):
    box_w = max([FONT_MD.size(l)[0] for l in lines]) + 20
    box_h = len(lines) * 22 + 12
    
    if x + box_w > WIDTH: x = WIDTH - box_w - 10
    if y + box_h > HEIGHT: y = HEIGHT - box_h - 10
        
    rect = pygame.Rect(x, y, box_w, box_h)
    pygame.draw.rect(surface, COLOR_TOOLTIP, rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_PRIMARY, rect, 1, border_radius=6)
    
    for idx, line in enumerate(lines):
        surface.blit(FONT_MD.render(line, True, COLOR_TEXT), (x + 10, y + 8 + idx * 22))

# =====================================================================
# ENGINE FIZIC
# =====================================================================
def calculate_physics(mode, E, r_int, r1, r2, r3, switch_closed):
    if not switch_closed:
        return 0.001, 0, (0,0,0), (0,0,0), (0,0,0), 0, E
        
    r1, r2, r3 = max(0.1, r1), max(0.1, r2), max(0.1, r3)
    
    if mode == "SERIE":
        R_eq = r1 + r2 + r3
        R_tot = R_eq + r_int
        I_tot = E / R_tot
        I1 = I2 = I3 = I_tot
        V1, V2, V3 = I1 * r1, I2 * r2, I3 * r3
    else:
        R_eq = 1.0 / ((1.0 / r1) + (1.0 / r2) + (1.0 / r3))
        R_tot = R_eq + r_int
        I_tot = E / R_tot
        V_borne = I_tot * R_eq
        V1 = V2 = V3 = V_borne
        I1, I2, I3 = V1 / r1, V2 / r2, V3 / r3

    V_borne = E - (I_tot * r_int)
    P1, P2, P3 = V1 * I1, V2 * I2, V3 * I3
    P_tot = V_borne * I_tot
    
    return R_eq, I_tot, (I1, I2, I3), (V1, V2, V3), (P1, P2, P3), P_tot, V_borne

# =====================================================================
# SISTEM QUIZ
# =====================================================================
class QuizSystem:
    def __init__(self):
        self.active_question = None
        self.correct_answer = 0.0
        self.unit = ""
        self.show_answer = False

    def generate_question(self, mode, E, r_int, r1, r2, r3, I_tot, currents, voltages, V_borne):
        self.show_answer = False
        q_type = random.choice(["Req", "Itot", "Vborne", "V1", "I2"])
        
        if q_type == "Req":
            self.active_question = "Care este rezistența echivalentă (Req) a circuitului extern?"
            self.correct_answer = r1+r2+r3 if mode == "SERIE" else 1/((1/r1)+(1/r2)+(1/r3))
            self.unit = "Ω"
        elif q_type == "Itot":
            self.active_question = "Ce curent total (Itot) debitează sursa în circuit?"
            self.correct_answer = I_tot
            self.unit = "A"
        elif q_type == "Vborne":
            self.active_question = "Care este tensiunea la bornele sursei (U)?"
            self.correct_answer = V_borne
            self.unit = "V"
        elif q_type == "V1":
            self.active_question = "Ce cădere de tensiune avem pe rezistorul R1?"
            self.correct_answer = voltages[0]
            self.unit = "V"
        elif q_type == "I2":
            self.active_question = "Ce curent (I2) traversează ramura rezistorului R2?"
            self.correct_answer = currents[1]
            self.unit = "A"

# =====================================================================
# MAIN APPLICATION LOOP
# =====================================================================
def main():
    sliders = [
        UISlider(40, 100, 240, 1.0, 100.0, 100.0, "T. Electromotoare (E)", "V"),
        UISlider(40, 170, 240, 0.0, 10.0, 0.0, "Rezistența Internă (r)", "Ω"),
        UISlider(40, 240, 240, 1.0, 100.0, 15.0, "Rezistență R1", "Ω"),
        UISlider(40, 310, 240, 1.0, 100.0, 10.0, "Rezistență R2", "Ω"),
        UISlider(40, 380, 240, 1.0, 100.0, 12.0, "Rezistență R3", "Ω")
    ]
    
    mode_buttons = [
        UIButton(40, 30, 115, 35, "SERIE", "SERIE"),
        UIButton(165, 30, 115, 35, "PARALEL", "PARALEL")
    ]
    
    tab_buttons = [
        UIButton(940, 20, 120, 32, "TELEMETRIE", "TAB_TEL"),
        UIButton(1070, 20, 145, 32, "PAȘI REZOLVARE", "TAB_STEPS"),
        UIButton(1225, 20, 100, 32, "MOD QUIZ", "TAB_QUIZ")
    ]
    
    switch_ui = UIToggle(40, 440, "Întrerupător General", True)
    quiz = QuizSystem()
    btn_new_quiz = UIButton(950, 180, 170, 38, "Generează Problemă", "GEN")
    btn_show_ans = UIButton(1140, 180, 140, 38, "Vezi Răspuns", "SHOW")

    current_mode = "PARALEL"
    active_tab = "TAB_TEL"
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        mouse_clicked = (False, False, False)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:         
                if event.key == pygame.K_ESCAPE:     
                    running = False                  
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = (True, False, False)

        for btn in mode_buttons:
            if btn.is_clicked(mouse_pos, mouse_clicked):
                current_mode = btn.identity
                
        for btn in tab_buttons:
            if btn.is_clicked(mouse_pos, mouse_clicked):
                active_tab = btn.identity
                
        for slider in sliders:
            slider.update(mouse_pos, mouse_pressed)
            
        switch_ui.is_clicked(mouse_pos, mouse_clicked)

        E = sliders[0].val
        r_int = sliders[1].val
        r1, r2, r3 = sliders[2].val, sliders[3].val, sliders[4].val
        is_on = switch_ui.state

        R_eq, I_tot, currents, voltages, powers, P_tot, V_borne = calculate_physics(
            current_mode, E, r_int, r1, r2, r3, is_on
        )

        screen.fill(COLOR_BG)
        
        pygame.draw.rect(screen, COLOR_PANEL, (0, 0, 320, HEIGHT))
        pygame.draw.rect(screen, COLOR_PANEL, (920, 0, 430, HEIGHT))

        for btn in mode_buttons: btn.draw(screen, current_mode)
        for btn in tab_buttons: btn.draw(screen, active_tab)
        for slider in sliders: slider.draw(screen)
        switch_ui.draw(screen)

        wire_color = COLOR_WIRE if is_on else COLOR_WIRE_OFF
        tooltips_to_draw = []

        # --- RENDERING CONFIGURAȚIE SERIE ---
        if current_mode == "SERIE":
            x_left, x_right, y_top, y_bottom = 450, 810, 250, 550
            pygame.draw.lines(screen, wire_color, True, [(x_left, y_top), (x_right, y_top), (x_right, y_bottom), (x_left, y_bottom)], 4)
            
            rect_bat = draw_battery(screen, x_left, 400, vertical=True)
            rect_r1 = draw_resistor(screen, 630, y_top, "R1", r1, powers[0], is_on, vertical=False)
            rect_r2 = draw_resistor(screen, x_right, 400, "R2", r2, powers[1], is_on, vertical=True)
            rect_r3 = draw_resistor(screen, 630, y_bottom, "R3", r3, powers[2], is_on, vertical=False)
            draw_switch(screen, 520, y_bottom, is_on, vertical=False)
            
            if is_on:
                serie_path = [(x_left, y_bottom), (x_left, 400), (x_left, y_top), (630, y_top), (x_right, y_top), (x_right, 400), (x_right, y_bottom), (520, y_bottom), (x_left, y_bottom)]
                draw_electrons_on_path(screen, serie_path, I_tot, spacing=65)

        # --- RENDERING CONFIGURAȚIE PARALEL (OPTIMIZATĂ COMPLET) ---
        else:
            x_bus_left, x_bus_right, y_top, y_bottom = 460, 820, 250, 550
            x_branches = [550, 685, 820]
            
            # Schițare mecanică a liniilor de circuit fizic
            pygame.draw.line(screen, wire_color, (380, y_top), (x_bus_right, y_top), 4)
            pygame.draw.line(screen, wire_color, (380, y_bottom), (x_bus_right, y_bottom), 4)
            pygame.draw.line(screen, wire_color, (380, y_top), (380, y_bottom), 4)
            
            rect_bat = draw_battery(screen, 380, 400, vertical=True)
            draw_switch(screen, 425, y_top, is_on, vertical=False)
            
            rect_r1 = draw_resistor(screen, x_branches[0], 400, "R1", r1, powers[0], is_on, vertical=True)
            rect_r2 = draw_resistor(screen, x_branches[1], 400, "R2", r2, powers[1], is_on, vertical=True)
            rect_r3 = draw_resistor(screen, x_branches[2], 400, "R3", r3, powers[2], is_on, vertical=True)
            
            for xb in x_branches:
                pygame.draw.line(screen, wire_color, (xb, y_top), (xb, 375), 4)
                pygame.draw.line(screen, wire_color, (xb, 425), (xb, y_bottom), 4)
                
            # EXECUȚIE ANIMAȚIE SEGMENTATĂ (Fără suprapuneri defectuoase!)
            if is_on:
                spacing_val = 65
                # Segment A: De la Sursă la primul Nod de Sus (Transportă Curentul Total)
                path_main_top = [(380, 400), (380, y_top), (425, y_top), (x_branches[0], y_top)]
                draw_electrons_on_path(screen, path_main_top, I_tot, spacing=spacing_val)
                
                # Segment B: Ramura verticală aferentă lui R1 (Curent local I1)
                path_r1_branch = [(x_branches[0], y_top), (x_branches[0], 400), (x_branches[0], y_bottom)]
                draw_electrons_on_path(screen, path_r1_branch, currents[0], spacing=spacing_val)
                
                # Segment C: Segmentul dintre R1 și R2 sus (Curent I2 + I3)
                path_top_mid = [(x_branches[0], y_top), (x_branches[1], y_top)]
                draw_electrons_on_path(screen, path_top_mid, currents[1] + currents[2], spacing=spacing_val)
                
                # Segment D: Ramura verticală aferentă lui R2 (Curent local I2)
                path_r2_branch = [(x_branches[1], y_top), (x_branches[1], 400), (x_branches[1], y_bottom)]
                draw_electrons_on_path(screen, path_r2_branch, currents[1], spacing=spacing_val)
                
                # Segment E: Segmentul dintre R2 și R3 sus (Curent local I3)
                path_top_right = [(x_branches[1], y_top), (x_branches[2], y_top)]
                draw_electrons_on_path(screen, path_top_right, currents[2], spacing=spacing_val)
                
                # Segment F: Ramura verticală aferentă lui R3 (Curent local I3)
                path_r3_branch = [(x_branches[2], y_top), (x_branches[2], 400), (x_branches[2], y_bottom)]
                draw_electrons_on_path(screen, path_r3_branch, currents[2], spacing=spacing_val)
                
                # Segment G: Segmentul dintre R3 și R2 jos (Curent local I3)
                path_bot_right = [(x_branches[2], y_bottom), (x_branches[1], y_bottom)]
                draw_electrons_on_path(screen, path_bot_right, currents[2], spacing=spacing_val)
                
                # Segment H: Segmentul dintre R2 și R1 jos (Curent I2 + I3)
                path_bot_mid = [(x_branches[1], y_bottom), (x_branches[0], y_bottom)]
                draw_electrons_on_path(screen, path_bot_mid, currents[1] + currents[2], spacing=spacing_val)
                
                # Segment I: De la primul Nod de Jos înapoi spre Sursă (Curentul Total Reîntregit)
                path_main_bot = [(x_branches[0], y_bottom), (380, y_bottom), (380, 400)]
                draw_electrons_on_path(screen, path_main_bot, I_tot, spacing=spacing_val)

        # Intersecție senzori virtuali (Hover Multimetru)
        if rect_bat.collidepoint(mouse_pos):
            tooltips_to_draw.append((mouse_pos[0], mouse_pos[1], [
                "SURSĂ DE ALIMENTARE",
                f"T. Electromotoare (E): {E:.2f} V",
                f"Tensiune la borne (U): {V_borne:.2f} V",
                f"Rezistență internă (r): {r_int:.2f} Ω"
            ]))
        
        res_mapping = [(rect_r1, 1), (rect_r2, 2), (rect_r3, 3)]
        for r_rect, num in res_mapping:
            if r_rect.collidepoint(mouse_pos):
                tooltips_to_draw.append((mouse_pos[0], mouse_pos[1], [
                    f"MULTIMETRU REZISTOR R{num}",
                    f"Tensiune (V{num}): {voltages[num-1]:.2f} V",
                    f"Intensitate (I{num}): {currents[num-1]:.2f} A",
                    f"Putere Disipată (P): {powers[num-1]:.2f} W"
                ]))

        # --- PANOU INFORMATIV DREAPTA ---
        dash_x = 940
        if active_tab == "TAB_TEL":
            screen.blit(FONT_LG.render("DATE BRUTE CIRCUIT", True, COLOR_ACTIVE), (dash_x, 80))
            screen.blit(FONT_MD.render(f"Stare Sistem: {'CONECTAT' if is_on else 'DECONECTAT'}", True, COLOR_ACTIVE if is_on else COLOR_WARNING), (dash_x, 120))
            screen.blit(FONT_MD.render(f"R_extern Echivalent: {R_eq:.2f} Ω", True, COLOR_TEXT), (dash_x, 150))
            screen.blit(FONT_MD.render(f"Curent Total (Itot): {I_tot:.2f} A", True, COLOR_ELECTRON), (dash_x, 180))
            screen.blit(FONT_MD.render(f"Cădere de Tensiune Internă (u): {(I_tot*r_int):.2f} V", True, COLOR_WARNING), (dash_x, 210))
            
            pygame.draw.line(screen, COLOR_WIRE, (dash_x, 245), (1310, 245), 1)
            screen.blit(FONT_LG.render("DISTRIBUȚIE ENERGIE", True, COLOR_PRIMARY), (dash_x, 260))
            
            curr_y = 300
            for i in range(3):
                screen.blit(FONT_MD.render(f"Element R{i+1}:  U={voltages[i]:.1f}V  |  I={currents[i]:.2f}A  |  P={powers[i]:.1f}W", True, COLOR_TEXT_MUTED), (dash_x, curr_y))
                curr_y += 35
                
        elif active_tab == "TAB_STEPS":
            screen.blit(FONT_LG.render("PAȘI DE REZOLVARE PEDAGOGICI", True, COLOR_PRIMARY), (dash_x, 80))
            if not is_on:
                screen.blit(FONT_MD.render("Închide circuitul din întrerupător pentru calcule.", True, COLOR_WARNING), (dash_x, 130))
            else:
                if current_mode == "SERIE":
                    f1, f2 = "Req = R1 + R2 + R3", f"Req = {r1:.1f} + {r2:.1f} + {r3:.1f} = {R_eq:.2f} Ω"
                else:
                    f1, f2 = "1/Req = 1/R1 + 1/R2 + 1/R3", f"Req = 1 / (1/{r1:.1f} + 1/{r2:.1f} + 1/{r3:.1f}) = {R_eq:.2f} Ω"
                
                steps = [
                    "Pas 1: Calcularea Rezistenței Echivalente Externe",
                    f"   Formulă: {f1}", f"   Rezultat: {f2}",
                    "Pas 2: Rezistența Totală a Circuitului (R_tot = Req + r)",
                    f"   R_tot = {R_eq:.2f} + {r_int:.1f} = {(R_eq+r_int):.2f} Ω",
                    "Pas 3: Aplicarea Legii lui Ohm pe întreg circuitul (Itot = E / R_tot)",
                    f"   Itot = {E:.1f}V / {(R_eq+r_int):.2f}Ω = {I_tot:.2f} A",
                    "Pas 4: Determinarea Tensiunii la Borne (U = E - Itot * r)",
                    f"   U = {E:.1f}V - ({I_tot:.2f}A * {r_int:.1f}Ω) = {V_borne:.2f} V"
                ]
                
                y_pos = 120
                for st in steps:
                    col = COLOR_ACTIVE if st.startswith("   ") else COLOR_TEXT
                    screen.blit(FONT_MATH.render(st, True, col), (dash_x, y_pos))
                    y_pos += 26

        elif active_tab == "TAB_QUIZ":
            screen.blit(FONT_LG.render("MOD EVALUARE / EXEMPLU ELEV", True, COLOR_HOVER), (dash_x, 80))
            screen.blit(FONT_SM.render("Modifică rezistențele din slidere, apoi generează testul.", True, COLOR_TEXT_MUTED), (dash_x, 110))
            
            btn_new_quiz.draw(screen)
            if btn_new_quiz.is_clicked(mouse_pos, mouse_clicked) and is_on:
                quiz.generate_question(current_mode, E, r_int, r1, r2, r3, I_tot, currents, voltages, V_borne)
                
            if quiz.active_question:
                screen.blit(FONT_MD.render("Problemă generată:", True, COLOR_TEXT), (dash_x, 240))
                
                words = quiz.active_question.split(' ')
                line1, line2 = "", ""
                for w in words:
                    if len(line1) < 35: line1 += w + " "
                    else: line2 += w + " "
                
                screen.blit(FONT_MATH.render(line1, True, COLOR_ACTIVE), (dash_x, 270))
                if line2: screen.blit(FONT_MATH.render(line2, True, COLOR_ACTIVE), (dash_x, 295))
                
                btn_show_ans.draw(screen)
                if btn_show_ans.is_clicked(mouse_pos, mouse_clicked):
                    quiz.show_answer = True
                    
                if quiz.show_answer:
                    screen.blit(FONT_LG.render(f"Răspuns Corect: {quiz.correct_answer:.2f} {quiz.unit}", True, COLOR_WARNING), (dash_x, 370))

        for tt_x, tt_y, lines in tooltips_to_draw:
            draw_tooltip(screen, tt_x, tt_y, lines)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
