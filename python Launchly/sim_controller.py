import customtkinter as ctk
import json
import socket
import sys


try:
    singleton_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    singleton_socket.bind(('127.0.0.1', 54321))
except socket.error:
    # Port is taken, which means a controller is already open. Kill this duplicate silently!
    sys.exit()


ctk.set_appearance_mode("Dark")

ctk.set_default_color_theme("dark-blue") 

class MasterController(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Launchly | Telemetry Control")
        self.geometry("400x650") 
        self.attributes('-topmost', True)
        self.resizable(False, False)

        
        self.header = ctk.CTkLabel(self, text="SIMULATION TELEMETRY", font=ctk.CTkFont(family="Arial", size=22, weight="bold"), text_color="#00A8E8")
        self.header.pack(pady=(20, 5))
        self.sub_header = ctk.CTkLabel(self, text="Live Variable Injection Active", font=ctk.CTkFont(size=12), text_color="gray50")
        self.sub_header.pack(pady=(0, 15))

       
        self.tabview = ctk.CTkTabview(self, width=360, height=520, segmented_button_selected_color="#005C8A")
        self.tabview.pack(padx=20, pady=5)

        self.tabview.add("Orbit")
        self.tabview.add("Optics")

        self.setup_orbit_tab()
        self.setup_optics_tab()
        
        self.update_json()

   
    def setup_orbit_tab(self):
        tab = self.tabview.tab("Orbit")
        
        
        preset_frame = ctk.CTkFrame(tab, fg_color="gray12", border_width=1, border_color="gray25", corner_radius=8)
        preset_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(preset_frame, text="BODY PRESETS", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray60").pack(anchor="w", padx=10, pady=(5,0))
        
        self.preset_menu = ctk.CTkOptionMenu(preset_frame, values=["Earth (Default)", "Moon", "Jupiter", "Black Hole"], command=self.apply_orbit_preset)
        self.preset_menu.pack(pady=10, padx=20, fill="x")

       
        ed_frame = ctk.CTkFrame(tab, fg_color="gray12", border_width=1, border_color="gray25", corner_radius=8)
        ed_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(ed_frame, text="MANUAL TUNING", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray60").pack(anchor="w", padx=10, pady=(5,0))

        self.mass_lbl = ctk.CTkLabel(ed_frame, text="Mass Pull: 5000")
        self.mass_lbl.pack()
        self.mass_sld = ctk.CTkSlider(ed_frame, from_=500, to=20000, command=self.update_json)
        self.mass_sld.set(5000)
        self.mass_sld.pack(pady=(0,10))

        self.rad_lbl = ctk.CTkLabel(ed_frame, text="Radius: 40 px")
        self.rad_lbl.pack()
        self.rad_sld = ctk.CTkSlider(ed_frame, from_=5, to=150, command=self.update_json)
        self.rad_sld.set(40)
        self.rad_sld.pack(pady=(0,10))

       
        self.cam_var = ctk.BooleanVar(value=False)
        self.cam_check = ctk.CTkCheckBox(tab, text="Dynamic Camera Auto-Pan", variable=self.cam_var, command=self.update_json)
        self.cam_check.pack(pady=15)

    def apply_orbit_preset(self, choice):
        if choice == "Earth (Default)":
            self.mass_sld.set(5000)
            self.rad_sld.set(40)
        elif choice == "Moon":
            self.mass_sld.set(1000)
            self.rad_sld.set(15)
        elif choice == "Jupiter":
            self.mass_sld.set(15000)
            self.rad_sld.set(100)
        elif choice == "Black Hole":
            self.mass_sld.set(20000)
            self.rad_sld.set(5) 
        self.update_json()

   
    def setup_optics_tab(self):
        tab = self.tabview.tab("Optics")
        self.mirror_trigger_count = 0
        self.mirrors_data = {"Mirror 1 (Default)": {"length": 100, "curve": 0}}
        
       
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
       
        gl_frame = ctk.CTkFrame(scroll_frame, fg_color="gray12", border_width=1, border_color="gray25", corner_radius=8)
        gl_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(gl_frame, text="LASER PROPERTIES", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray60").pack(anchor="w", padx=10, pady=(5,0))

        self.bounce_lbl = ctk.CTkLabel(gl_frame, text="Max Bounces: 10")
        self.bounce_lbl.pack()
        self.bounce_sld = ctk.CTkSlider(gl_frame, from_=1, to=50, number_of_steps=49, command=self.update_json)
        self.bounce_sld.set(10)
        self.bounce_sld.pack(pady=(0,10))

        self.show_angles_var = ctk.BooleanVar(value=True)
        self.show_angles_check = ctk.CTkCheckBox(gl_frame, text="Show Impact Angles (θ)", variable=self.show_angles_var, command=self.update_json)
        self.show_angles_check.pack(pady=(0, 10))

  
        self.anim_trigger_count = 0
        self.anim_btn = ctk.CTkButton(gl_frame, text="▶ Play Laser Path", fg_color="#B33939", hover_color="#8C2B2B", command=self.trigger_animation)
        self.anim_btn.pack(pady=(10, 5))

        self.speed_lbl = ctk.CTkLabel(gl_frame, text="Animation Speed: 0.5x")
        self.speed_lbl.pack()
        self.speed_sld = ctk.CTkSlider(gl_frame, from_=0.1, to=2.0, command=self.update_json)
        self.speed_sld.set(0.5)
        self.speed_sld.pack(pady=(0,5))

        self.trail_lbl = ctk.CTkLabel(gl_frame, text="Trail Length (Bounces): 3")
        self.trail_lbl.pack()
        self.trail_sld = ctk.CTkSlider(gl_frame, from_=1, to=15, number_of_steps=14, command=self.update_json)
        self.trail_sld.set(3)
        self.trail_sld.pack(pady=(0,10))

        
        arr_frame = ctk.CTkFrame(scroll_frame, fg_color="gray12", border_width=1, border_color="gray25", corner_radius=8)
        arr_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(arr_frame, text="MIRROR ARRAY", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray60").pack(anchor="w", padx=10, pady=(5,0))

        self.add_mir_btn = ctk.CTkButton(arr_frame, text="+ Inject New Mirror", fg_color="#007A5E", hover_color="#005C46", command=self.trigger_new_mirror)
        self.add_mir_btn.pack(pady=10)

        ctk.CTkLabel(arr_frame, text="Edit Active Mirror:", font=ctk.CTkFont(size=11)).pack()
        self.active_mir_menu = ctk.CTkOptionMenu(arr_frame, values=["Mirror 1 (Default)"], command=self.load_mirror_data)
        self.active_mir_menu.pack(pady=(0,10))

        self.mir_lbl = ctk.CTkLabel(arr_frame, text="Length: 100 px")
        self.mir_lbl.pack()
        self.mir_sld = ctk.CTkSlider(arr_frame, from_=20, to=300, command=self.update_json)
        self.mir_sld.set(100)
        self.mir_sld.pack(pady=(0,10))

        self.curve_lbl = ctk.CTkLabel(arr_frame, text="Curvature: 0° (Flat)")
        self.curve_lbl.pack()
        self.curve_sld = ctk.CTkSlider(arr_frame, from_=-45, to=45, command=self.update_json)
        self.curve_sld.set(0)
        self.curve_sld.pack(pady=(0,20)) 

    def trigger_new_mirror(self):
        self.mirror_trigger_count += 1
        current_mirrors = self.active_mir_menu.cget("values")
        new_mirror_name = f"Mirror {len(current_mirrors) + 1}"
        
        
        self.mirrors_data[new_mirror_name] = {"length": 100, "curve": 0}
        
        current_mirrors.append(new_mirror_name)
        self.active_mir_menu.configure(values=current_mirrors)
        self.active_mir_menu.set(new_mirror_name) 
        self.load_mirror_data(new_mirror_name)

    def trigger_animation(self):
        self.anim_trigger_count += 1
        self.update_json()

    def load_mirror_data(self, choice):
        
        data = self.mirrors_data.get(choice, {"length": 100, "curve": 0})
        self.mir_sld.set(data["length"])
        self.curve_sld.set(data["curve"])
        self.update_json()

   
    def update_json(self, _=None):
        
        self.mass_lbl.configure(text=f"Mass Pull: {int(self.mass_sld.get())}")
        self.rad_lbl.configure(text=f"Radius: {int(self.rad_sld.get())} px")
        
        self.bounce_lbl.configure(text=f"Max Bounces: {int(self.bounce_sld.get())}")
        self.mir_lbl.configure(text=f"Length: {int(self.mir_sld.get())} px")
        
        curve_val = int(self.curve_sld.get())
        curve_text = f"Curvature: {abs(curve_val)}° "
        curve_text += "(Concave)" if curve_val > 0 else "(Convex)" if curve_val < 0 else "(Flat)"
        self.curve_lbl.configure(text=curve_text)

        self.speed_lbl.configure(text=f"Animation Speed: {self.speed_sld.get():.1f}x")
        self.trail_lbl.configure(text=f"Trail Length (Bounces): {int(self.trail_sld.get())}")

        active_mirror = self.active_mir_menu.get()
        self.mirrors_data[active_mirror] = {
            "length": int(self.mir_sld.get()),
            "curve": int(self.curve_sld.get())
        }

        
        data = {
            "orbit": {
                "planet_mass": float(self.mass_sld.get()),
                "planet_radius": int(self.rad_sld.get()),
                "camera_pan": self.cam_var.get()
            },
            "optics": {
                "max_bounces": int(self.bounce_sld.get()),
                "add_mirror_trigger": self.mirror_trigger_count,
                "show_angles": self.show_angles_var.get(),
                "animate_laser_trigger": self.anim_trigger_count,
                "anim_speed": float(self.speed_sld.get()),      
                "anim_trail": int(self.trail_sld.get()),        
                "mirrors_config": self.mirrors_data
            }
        }
        
        try:
            with open('sim_data.json', 'w') as f:
                json.dump(data, f)
        except Exception:
            pass 

if __name__ == "__main__":
    app = MasterController()
    app.mainloop()
