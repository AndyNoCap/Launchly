import pygame
import sys
import math
import json
import subprocess

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
MASSIVE_PULL = 5000.0  # Simplified gravity constant * planet mass
PLANET_RADIUS = 40
CAMERA_PAN = False

# Colors
BG_COLOR = (15, 15, 25)
TEXT_COLOR = (200, 200, 200)
PLANET_COLOR = (50, 100, 200)
SAT_COLOR = (255, 255, 255)
DRAG_COLOR = (200, 50, 50)
TRAIL_COLOR = (100, 100, 100)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Orbital Slingshot")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class OrbitGame:
    def __init__(self):
        self.planet_pos = (WIDTH // 2, HEIGHT // 2)
        self.reset()

    def reset(self):
        self.state = "START" # START, DRAGGING, ORBITING, CRASHED, LOST
        self.sat_pos = [0.0, 0.0]
        self.sat_vel = [0.0, 0.0]
        self.drag_start = (0, 0)
        self.drag_current = (0, 0)
        self.trail = []
        self.orbit_frames = 0
        self.distance = 0.0

    def update(self):
        if self.state == "ORBITING":
            self.orbit_frames += 1
            
            rx = self.planet_pos[0] - self.sat_pos[0]
            ry = self.planet_pos[1] - self.sat_pos[1]
            self.distance = math.sqrt(rx**2 + ry**2)
            
            if self.distance <= PLANET_RADIUS + 5:
                self.state = "CRASHED"
                return
            elif self.distance > WIDTH * 2:
                self.state = "LOST IN SPACE"
                return
            
            accel = MASSIVE_PULL / (self.distance**2)
            ax = accel * (rx / self.distance)
            ay = accel * (ry / self.distance)
            
            self.sat_vel[0] += ax
            self.sat_vel[1] += ay
            
            self.sat_pos[0] += self.sat_vel[0]
            self.sat_pos[1] += self.sat_vel[1]
            
            if self.orbit_frames % 2 == 0:
                self.trail.append((self.sat_pos[0], self.sat_pos[1]))
                if len(self.trail) > 200:
                    self.trail.pop(0)

    def draw(self):
        screen.fill(BG_COLOR)
        
        global CAMERA_PAN
        camera_scale = 1.0
        if CAMERA_PAN and self.state in ["ORBITING", "CRASHED", "LOST IN SPACE"]:
            if self.distance > WIDTH // 2:
                camera_scale = (WIDTH // 2) / self.distance
                
        def scale_pos(p):
            cx, cy = WIDTH // 2, HEIGHT // 2
            return (cx + (p[0] - cx) * camera_scale, cy + (p[1] - cy) * camera_scale)
        
        # Draw Planet
        pygame.draw.circle(screen, PLANET_COLOR, self.planet_pos, int(PLANET_RADIUS * camera_scale))
        
        # Draw Trail
        if len(self.trail) > 1:
            scaled_trail = [scale_pos(p) for p in self.trail]
            pygame.draw.lines(screen, TRAIL_COLOR, False, scaled_trail, 2)
            
        if self.state == "DRAGGING":
            pygame.draw.circle(screen, SAT_COLOR, self.drag_start, 5)
            pygame.draw.line(screen, DRAG_COLOR, self.drag_start, self.drag_current, 2)
        elif self.state in ["ORBITING", "CRASHED", "LOST IN SPACE"]:
            sp = scale_pos(self.sat_pos)
            pygame.draw.circle(screen, SAT_COLOR, (int(sp[0]), int(sp[1])), max(1, int(5 * camera_scale)))
            
        # Draw UI
        vel_mag = math.sqrt(self.sat_vel[0]**2 + self.sat_vel[1]**2)
        time_sec = self.orbit_frames / FPS
        
        ui_text = f"Velocity: {vel_mag:.1f} m/s | Distance: {self.distance:.1f} km | Time: {time_sec:.1f}s | Status: {self.state}"
        text_surf = font.render(ui_text, True, TEXT_COLOR)
        screen.blit(text_surf, (20, 20))
        
        instructions = "Drag to launch satellite | R: Reset | ESC: Quit"
        inst_surf = pygame.font.Font(None, 24).render(instructions, True, (150, 150, 150))
        screen.blit(inst_surf, (20, HEIGHT - 30))

def main():
    game = OrbitGame()
    running = True
    frame_count = 0
    global MASSIVE_PULL, PLANET_RADIUS
    
    while running:
        frame_count += 1
        if frame_count % 10 == 0:
            try:
                with open('sim_data.json', 'r') as f:
                    sim_data = json.load(f)
                    MASSIVE_PULL = sim_data["orbit"]["planet_mass"]
                    PLANET_RADIUS = sim_data["orbit"]["planet_radius"]
                    global CAMERA_PAN
                    CAMERA_PAN = sim_data["orbit"]["camera_pan"]
            except Exception as e:
                pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
                elif event.key == pygame.K_c:
                    subprocess.Popen([sys.executable, "sim_controller.py"])
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    game.reset()
                    game.state = "DRAGGING"
                    game.drag_start = event.pos
                    game.drag_current = event.pos
            if event.type == pygame.MOUSEMOTION:
                if game.state == "DRAGGING":
                    game.drag_current = event.pos
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and game.state == "DRAGGING":
                    game.state = "ORBITING"
                    game.sat_pos = list(game.drag_start)
                    # "Angry birds" style: pull back to launch forward
                    dx = game.drag_start[0] - game.drag_current[0]
                    dy = game.drag_start[1] - game.drag_current[1]
                    # Scale down the vector for reasonable velocities
                    game.sat_vel = [dx * 0.05, dy * 0.05]
                    
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
