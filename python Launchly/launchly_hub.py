import customtkinter as ctk
import subprocess
import os
import sys


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LaunchlyHub(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Launchly - Physics Game Hub")
        self.geometry("720x840") 
        self.resizable(False, False)

        
        self.title_label = ctk.CTkLabel(self, text="Launchly Physics Hub", font=ctk.CTkFont(size=32, weight="bold"))
        self.title_label.pack(pady=(25, 5))
        
        self.subtitle_label = ctk.CTkLabel(self, text="Selectați un laborator virtual pentru simulare", font=ctk.CTkFont(size=14), text_color="gray")
        self.subtitle_label.pack(pady=(0, 15))

        
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=5)

        
        self.btn_artillery = ctk.CTkButton(self.button_frame, text="Artilerie Balistică", width=230, height=50, 
                                          font=ctk.CTkFont(size=14), command=lambda: self.launch_standalone("game_artillery.py"))
        self.btn_artillery.grid(row=0, column=0, padx=15, pady=8)

        self.btn_orbit = ctk.CTkButton(self.button_frame, text="Slingshot Orbital", width=230, height=50, 
                                       font=ctk.CTkFont(size=14), command=lambda: self.launch_game("game_orbit.py"))
        self.btn_orbit.grid(row=0, column=1, padx=15, pady=8)

        
        self.btn_optics = ctk.CTkButton(self.button_frame, text="Oglinzi și Lasere", width=230, height=50, 
                                        font=ctk.CTkFont(size=14), command=lambda: self.launch_game("game_optics.py"))
        self.btn_optics.grid(row=1, column=0, padx=15, pady=8)

        self.btn_circuit = ctk.CTkButton(self.button_frame, text="Circuite Electrice", width=230, height=50, 
                                        font=ctk.CTkFont(size=14), command=lambda: self.launch_standalone("game_circuit.py"))
        self.btn_circuit.grid(row=1, column=1, padx=15, pady=8)

        
        self.btn_earthquake = ctk.CTkButton(self.button_frame, text="Rezonanță Seismică", width=230, height=50, 
                                        font=ctk.CTkFont(size=14), command=lambda: self.launch_standalone("game_earthquake.py"))
        self.btn_earthquake.grid(row=2, column=0, padx=15, pady=8)

        self.btn_waves = ctk.CTkButton(self.button_frame, text="Unde Seismice vs. Gravitaționale", width=230, height=50, 
                                        font=ctk.CTkFont(size=14), command=lambda: self.launch_standalone("game_waves.py"))
        self.btn_waves.grid(row=2, column=1, padx=15, pady=8)

        
        self.btn_young = ctk.CTkButton(self.button_frame, text="Dispozitivul lui Young", width=230, height=50, 
                                        font=ctk.CTkFont(size=14), command=lambda: self.launch_standalone("game_young.py"))
        self.btn_young.grid(row=3, column=0, padx=15, pady=8)

        self.btn_cradle = ctk.CTkButton(self.button_frame, text="Pendulul lui Newton", width=230, height=50, 
                                        font=ctk.CTkFont(size=14), command=lambda: self.launch_standalone("game_cradle.py"))
        self.btn_cradle.grid(row=3, column=1, padx=15, pady=8)

        
        self.btn_thermo = ctk.CTkButton(self.button_frame, text="Termodinamică", width=230, height=50, 
                                        font=ctk.CTkFont(size=14), command=lambda: self.launch_standalone("game_thermo.py"))
        self.btn_thermo.grid(row=4, column=0, padx=15, pady=8)

        self.btn_pulleys = ctk.CTkButton(self.button_frame, text="Scripeți și Randament", width=230, height=50, 
                                        font=ctk.CTkFont(size=14), command=lambda: self.launch_standalone("game_pulleys.py"))
        self.btn_pulleys.grid(row=4, column=1, padx=15, pady=8)

        
        self.btn_bungee = ctk.CTkButton(self.button_frame, text="Elasticitate Bungee", width=230, height=50, 
                                        font=ctk.CTkFont(size=14), command=lambda: self.launch_standalone("game_bungee.py"))
        self.btn_bungee.grid(row=5, column=0, padx=15, pady=8)

        self.btn_slope = ctk.CTkButton(self.button_frame, text="Plan Înclinat și Frecare", width=230, height=50, 
                                        font=ctk.CTkFont(size=14), command=lambda: self.launch_standalone("game_slope.py"))
        self.btn_slope.grid(row=5, column=1, padx=15, pady=8)

       
        self.btn_spacetime = ctk.CTkButton(self.button_frame, text="Relativitate și Spațiu-Timp", width=230, height=50, 
                                        font=ctk.CTkFont(size=14), command=lambda: self.launch_standalone("game_spacetime.py"))
        self.btn_spacetime.grid(row=6, column=0, padx=15, pady=8)

        self.btn_pascal = ctk.CTkButton(self.button_frame, text="Principiul lui Pascal", width=230, height=50, 
                                        font=ctk.CTkFont(size=14), command=lambda: self.launch_standalone("game_pascal.py"))
        self.btn_pascal.grid(row=6, column=1, padx=15, pady=8)

        
        self.status_label = ctk.CTkLabel(self, text="Sistem pregătit.", text_color="gray", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="bottom", pady=15)

    def launch_game(self, filename):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        controller_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sim_controller.py")
        
        if not os.path.exists(filepath):
            self.show_error(f"Error: {filename} not found in directory.")
            return

        self.status_label.configure(text=f"Launching {filename} & Controller...", text_color="green")
        
        try:
            
            subprocess.Popen([sys.executable, filepath])
            
            subprocess.Popen([sys.executable, controller_path])
        except Exception as e:
            self.show_error(f"Failed to launch {filename}: {str(e)}")

    def launch_standalone(self, filename):
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        
        if not os.path.exists(filepath):
            self.show_error(f"Error: {filename} not found in directory.")
            return

        self.status_label.configure(text=f"Launching Standalone Module: {filename}...", text_color="cyan")
        
        try:
           
            subprocess.Popen([sys.executable, filepath])
        except Exception as e:
            self.show_error(f"Failed to launch {filename}: {str(e)}")

    def show_error(self, message):
        self.status_label.configure(text=message, text_color="red")

if __name__ == "__main__":
    app = LaunchlyHub()
    app.mainloop()
