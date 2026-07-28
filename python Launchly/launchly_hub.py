import customtkinter as ctk
import subprocess
import os
import sys

# Set Orbital Precision Dark Theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


COLOR_BG = "#0A0D14"            # Deep obsidian space background
COLOR_SURFACE = "#121620"       # Glassmorphism dark surface container
COLOR_SURFACE_HOVER = "#1B2232" # Card hover fill
COLOR_BORDER = "#1F283B"        # Subtle card border
COLOR_ACCENT = "#3B82F6"        # Electric Blue primary CTA
COLOR_ACCENT_HOVER = "#2563EB"  # Darker electric blue hover
COLOR_CYAN = "#4CD7F6"          # Telemetry cyan glow
COLOR_TEXT_MAIN = "#E1E2EC"     # High-contrast white header text
COLOR_TEXT_MUTED = "#8C909F"    # Monospace telemetry & subtitle gray
COLOR_GREEN = "#10B981"         # Ready status green

LABS_DATA = [
    {
        "id": "game_artillery.py",
        "title": "Artilerie Balistică",
        "category": "Mecanică",
        "tag": "🚀 MECANICĂ",
        "desc": "Simulare a mișcării pe parabolă și a traiectoriei proiectilelor.",
        "has_controller": False,
        "status": "READY"
    },
    {
        "id": "game_orbit.py",
        "title": "Slingshot Orbital",
        "category": "Mecanică",
        "tag": "🌌 GRAVITAȚIE",
        "desc": "Mecanică orbitală, atracție universală și asistență gravitațională.",
        "has_controller": True,
        "status": "LIVE SYNC"
    },
    {
        "id": "game_billiards.py",
        "title": "Ciocniri Elastice",
        "category": "Mecanică",
        "tag": "🎱 MECANICĂ",
        "desc": "Biliardul lui Newton: conservarea impulsului și a energiei cinetice.",
        "has_controller": False,
        "status": "READY"
    },
    {
        "id": "game_cradle.py",
        "title": "Pendulul lui Newton",
        "category": "Mecanică",
        "tag": "⚖️ MECANICĂ",
        "desc": "Demonstrație a conservării energiei și masei în ciocniri multiple.",
        "has_controller": False,
        "status": "READY"
    },
    {
        "id": "game_pulleys.py",
        "title": "Scripeți și Randament",
        "category": "Mecanică",
        "tag": "⚙️ MECANICĂ",
        "desc": "Avantajul mecanic al scripeților fixi/mobili și frecarea.",
        "has_controller": False,
        "status": "READY"
    },
    {
        "id": "game_bungee.py",
        "title": "Elasticitate Bungee",
        "category": "Mecanică",
        "tag": "🪢 MECANICĂ",
        "desc": "Oscilații, forță elastică (Hooke) și conversia energiei potențiale.",
        "has_controller": False,
        "status": "READY"
    },
    {
        "id": "game_slope.py",
        "title": "Plan Înclinat și Frecare",
        "category": "Mecanică",
        "tag": "📐 MECANICĂ",
        "desc": "Descompunerea forțelor pe plan înclinat și coeficientul de frecare.",
        "has_controller": False,
        "status": "READY"
    },
    {
        "id": "game_pascal.py",
        "title": "Principiul lui Pascal",
        "category": "Mecanică",
        "tag": "💧 HIDRODINAMICĂ",
        "desc": "Presa hidraulică, multiplicarea forței și transmiterea presiunii.",
        "has_controller": False,
        "status": "READY"
    },
    {
        "id": "game_optics.py",
        "title": "Oglinzi și Lasere",
        "category": "Optică & Unde",
        "tag": "🔦 OPTICĂ",
        "desc": "Optică geometrică, reflexie, unghiuri și rețea de oglinzi curbate.",
        "has_controller": True,
        "status": "LIVE SYNC"
    },
    {
        "id": "game_young.py",
        "title": "Dispozitivul lui Young",
        "category": "Optică & Unde",
        "tag": "🌈 OPTICĂ",
        "desc": "Interferență luminoasă pe dublă fantă și conversie spectru RGB.",
        "has_controller": False,
        "status": "READY"
    },
    {
        "id": "game_earthquake.py",
        "title": "Rezonanță Seismică",
        "category": "Optică & Unde",
        "tag": "🌋 SEISMOLOGIE",
        "desc": "Propagarea undelor P/S, funcționarea seismografului și rezonanța.",
        "has_controller": False,
        "status": "READY"
    },
    {
        "id": "game_waves.py",
        "title": "Unde Seismice vs Gravitaționale",
        "category": "Optică & Unde",
        "tag": "🌊 UNDE",
        "desc": "Comparație între interferența undelor mecanice și cele spațiu-timp.",
        "has_controller": False,
        "status": "READY"
    },
    {
        "id": "game_circuit.py",
        "title": "Circuite Electrice",
        "category": "Electromagnetism",
        "tag": "⚡ ELECTROMAGNETISM",
        "desc": "Legile lui Kirchhoff, rezistență echivalentă și Mod Quiz Evaluare.",
        "has_controller": False,
        "status": "QUIZ MODE"
    },
    {
        "id": "game_spacetime.py",
        "title": "Relativitate Spațiu-Timp",
        "category": "Fizică Modernă",
        "tag": "⚛️ FIZICĂ MODERNĂ",
        "desc": "Curbura spațiu-timp, dilatarea timpului și deformarea gravitațională.",
        "has_controller": False,
        "status": "READY"
    },
    {
        "id": "game_thermo.py",
        "title": "Termodinamică",
        "category": "Fizică Modernă",
        "tag": "🔥 TERMODINAMICĂ",
        "desc": "Gaz ideal, presiune, temperatură și mișcare browniană a moleculelor.",
        "has_controller": False,
        "status": "READY"
    }
]

class LaunchlyHub(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Launchly - Physics Game Hub [Orbital Precision UI]")
        self.geometry("1150x820")
        self.minsize(980, 700)
        self.configure(fg_color=COLOR_BG)

        self.current_category = "Toate"
        self.search_query = ""

        self.build_ui()

    def build_ui(self):
        # Header Bar
        self.header_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, corner_radius=0, height=75)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        # Title & Branding
        self.logo_label = ctk.CTkLabel(
            self.header_frame,
            text="⚡ LAUNCHLY",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color=COLOR_ACCENT
        )
        self.logo_label.pack(side="left", padx=(25, 10), pady=18)

        self.sub_logo = ctk.CTkLabel(
            self.header_frame,
            text="PHYSICS LAB HUB",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        )
        self.sub_logo.pack(side="left", padx=0, pady=22)

        # Live Badge
        self.live_chip = ctk.CTkLabel(
            self.header_frame,
            text=" ● 15 LABS ACTIVE ",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            fg_color="#0F2D24",
            text_color=COLOR_CYAN,
            corner_radius=12
        )
        self.live_chip.pack(side="left", padx=15, pady=22)

        # Search Bar
        self.search_entry = ctk.CTkEntry(
            self.header_frame,
            placeholder_text="🔍 Căutare laborator fizică...",
            width=260,
            height=36,
            fg_color=COLOR_BG,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_MAIN,
            placeholder_text_color=COLOR_TEXT_MUTED
        )
        self.search_entry.pack(side="right", padx=(10, 25), pady=18)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # Main Layout Container (Sidebar + Main Content)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=15)

        # --- LEFT SIDEBAR PANEL ---
        self.sidebar_frame = ctk.CTkFrame(self.main_container, fg_color=COLOR_SURFACE, width=240, corner_radius=12, border_width=1, border_color=COLOR_BORDER)
        self.sidebar_frame.pack(side="left", fill="y", padx=(0, 15), pady=0)
        self.sidebar_frame.pack_propagate(False)

        sidebar_title = ctk.CTkLabel(self.sidebar_frame, text="PANOU CONTROL", font=ctk.CTkFont(family="Inter", size=14, weight="bold"), text_color=COLOR_TEXT_MAIN)
        sidebar_title.pack(anchor="w", padx=15, pady=(15, 5))

        sidebar_sub = ctk.CTkLabel(self.sidebar_frame, text="Telemetrie & Sesiuni", font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_MUTED)
        sidebar_sub.pack(anchor="w", padx=15, pady=(0, 15))

        # Launch Master Telemetry Controller Button
        self.btn_telemetry = ctk.CTkButton(
            self.sidebar_frame,
            text="🎛️ Master Telemetrie",
            height=40,
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#0F2A4A",
            border_color=COLOR_ACCENT,
            border_width=1,
            hover_color="#1E3A5F",
            text_color=COLOR_CYAN,
            command=self.launch_master_controller
        )
        self.btn_telemetry.pack(fill="x", padx=12, pady=(0, 15))

        # Info Box inside Sidebar
        info_box = ctk.CTkFrame(self.sidebar_frame, fg_color=COLOR_BG, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        info_box.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(info_box, text="ℹ️ InfoEducație", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_ACCENT).pack(anchor="w", padx=10, pady=(8, 2))
        info_text = "Platformă software educațional completă cu 15 simulări fizice interactive, de la mecanică la fizică cuantică."
        ctk.CTkLabel(info_box, text=info_text, font=ctk.CTkFont(size=10), text_color=COLOR_TEXT_MUTED, wraplength=190, justify="left").pack(anchor="w", padx=10, pady=(0, 8))

        # Stats summary inside Sidebar
        stats_box = ctk.CTkFrame(self.sidebar_frame, fg_color=COLOR_BG, corner_radius=8, border_width=1, border_color=COLOR_BORDER)
        stats_box.pack(fill="x", padx=12, pady=10)
        ctk.CTkLabel(stats_box, text="📊 STATISTICI HUB", font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=10, pady=(8, 4))
        ctk.CTkLabel(stats_box, text="• 15 Laboratoare Virtuale", font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(stats_box, text="• 2 Module Live Controller", font=ctk.CTkFont(size=11), text_color=COLOR_CYAN).pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(stats_box, text="• 1 Mod Evaluare Quiz", font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_MAIN).pack(anchor="w", padx=10, pady=(2, 8))

        # --- RIGHT MAIN AREA ---
        self.right_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_area.pack(side="right", fill="both", expand=True)

        # Filter Chips Bar
        self.categories = ["Toate", "Mecanică", "Optică & Unde", "Electromagnetism", "Fizică Modernă"]
        self.filter_frame = ctk.CTkFrame(self.right_area, fg_color="transparent")
        self.filter_frame.pack(fill="x", pady=(0, 12))

        self.filter_buttons = {}
        for cat in self.categories:
            btn = ctk.CTkButton(
                self.filter_frame,
                text=cat,
                height=32,
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                fg_color=COLOR_ACCENT if cat == "Toate" else COLOR_SURFACE,
                hover_color=COLOR_ACCENT_HOVER if cat == "Toate" else COLOR_SURFACE_HOVER,
                text_color=COLOR_TEXT_MAIN,
                corner_radius=16,
                command=lambda c=cat: self.filter_category(c)
            )
            btn.pack(side="left", padx=(0, 8))
            self.filter_buttons[cat] = btn

        # Scrollable Grid for Cards
        self.cards_scroll = ctk.CTkScrollableFrame(self.right_area, fg_color="transparent")
        self.cards_scroll.pack(fill="both", expand=True)
        self.cards_scroll.grid_columnconfigure((0, 1, 2), weight=1, uniform="card_col")

        # Bottom Status Bar
        self.status_bar = ctk.CTkFrame(self, fg_color=COLOR_SURFACE, height=32, corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom")

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Sistem pregătit. Selectați un laborator pentru a începe.",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=COLOR_TEXT_MUTED
        )
        self.status_label.pack(side="left", padx=20, pady=4)

        # Render initial cards
        self.render_cards()

    def filter_category(self, cat):
        self.current_category = cat
        for c, btn in self.filter_buttons.items():
            if c == cat:
                btn.configure(fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER)
            else:
                btn.configure(fg_color=COLOR_SURFACE, hover_color=COLOR_SURFACE_HOVER)
        self.render_cards()

    def on_search(self, event=None):
        self.search_query = self.search_entry.get().strip().lower()
        self.render_cards()

    def render_cards(self):
        # Clear existing cards
        for widget in self.cards_scroll.winfo_children():
            widget.destroy()

        filtered = []
        for lab in LABS_DATA:
            cat_match = (self.current_category == "Toate") or (lab["category"] == self.current_category)
            search_match = (not self.search_query) or (self.search_query in lab["title"].lower() or self.search_query in lab["desc"].lower())
            if cat_match and search_match:
                filtered.append(lab)

        if not filtered:
            empty_lbl = ctk.CTkLabel(self.cards_scroll, text="Niciun laborator găsit.", font=ctk.CTkFont(size=14), text_color=COLOR_TEXT_MUTED)
            empty_lbl.pack(pady=40)
            return

        row, col = 0, 0
        for lab in filtered:
            card = ctk.CTkFrame(
                self.cards_scroll,
                fg_color=COLOR_SURFACE,
                border_width=1,
                border_color=COLOR_BORDER,
                corner_radius=10
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            # Tag / Category Header
            tag_lbl = ctk.CTkLabel(
                card,
                text=lab["tag"],
                font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                text_color=COLOR_CYAN
            )
            tag_lbl.pack(anchor="w", padx=12, pady=(12, 2))

            # Lab Title
            title_lbl = ctk.CTkLabel(
                card,
                text=lab["title"],
                font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                text_color=COLOR_TEXT_MAIN
            )
            title_lbl.pack(anchor="w", padx=12, pady=(0, 4))

            # Lab Description
            desc_lbl = ctk.CTkLabel(
                card,
                text=lab["desc"],
                font=ctk.CTkFont(size=11),
                text_color=COLOR_TEXT_MUTED,
                wraplength=220,
                justify="left"
            )
            desc_lbl.pack(anchor="w", padx=12, pady=(0, 10))

            # Status Chip & Launch Button Frame
            bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
            bottom_frame.pack(fill="x", padx=12, pady=(5, 12), side="bottom")

            status_col = COLOR_CYAN if lab["status"] == "LIVE SYNC" else COLOR_GREEN
            status_chip = ctk.CTkLabel(
                bottom_frame,
                text=f"● {lab['status']}",
                font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                text_color=status_col
            )
            status_chip.pack(side="left")

            btn_text = "Lansează" if not lab["has_controller"] else "Lansează + Sync"
            launch_btn = ctk.CTkButton(
                bottom_frame,
                text=btn_text,
                width=100,
                height=28,
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                fg_color=COLOR_ACCENT,
                hover_color=COLOR_ACCENT_HOVER,
                command=lambda f=lab["id"], c=lab["has_controller"]: self.launch_lab(f, c)
            )
            launch_btn.pack(side="right")

            col += 1
            if col >= 3:
                col = 0
                row += 1

    def launch_lab(self, filename, has_controller):
        if has_controller:
            self.launch_game(filename)
        else:
            self.launch_standalone(filename)

    def launch_master_controller(self):
        controller_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sim_controller.py")
        if not os.path.exists(controller_path):
            self.show_error("Error: sim_controller.py strictly missing.")
            return
        self.status_label.configure(text="Lansare Master Controller Telemetrie...", text_color=COLOR_CYAN)
        try:
            subprocess.Popen([sys.executable, controller_path])
        except Exception as e:
            self.show_error(f"Eroare lansare controller: {str(e)}")

    def launch_game(self, filename):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        controller_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sim_controller.py")

        if not os.path.exists(filepath):
            self.show_error(f"Eroare: {filename} nu exista.")
            return

        self.status_label.configure(text=f"Lansare {filename} & Telemetry Controller...", text_color=COLOR_GREEN)

        try:
            subprocess.Popen([sys.executable, filepath])
            subprocess.Popen([sys.executable, controller_path])
        except Exception as e:
            self.show_error(f"Eroare la lansarea {filename}: {str(e)}")

    def launch_standalone(self, filename):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

        if not os.path.exists(filepath):
            self.show_error(f"Eroare: {filename} nu exista.")
            return

        self.status_label.configure(text=f"Lansare Modul Standalone: {filename}...", text_color=COLOR_CYAN)

        try:
            subprocess.Popen([sys.executable, filepath])
        except Exception as e:
            self.show_error(f"Eroare la lansarea {filename}: {str(e)}")

    def show_error(self, message):
        self.status_label.configure(text=message, text_color="#EF4444")

if __name__ == "__main__":
    app = LaunchlyHub()
    app.mainloop()
