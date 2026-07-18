import pygame
import sys
import math
import json
import random
import subprocess

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
MAX_BOUNCES = 10
SHOW_ANGLES = True
ADD_MIRROR_TRIGGER = 0
ANIMATE_LASER_TRIGGER = 0
ANIM_SPEED = 0.5
ANIM_TRAIL = 3

# Colors
BG_COLOR = (20, 20, 20)
TEXT_COLOR = (200, 200, 200)
EMITTER_COLOR = (150, 150, 150)
TARGET_COLOR = (50, 200, 50)
MIRROR_COLOR = (100, 200, 255)
MIRROR_HOVER = (200, 255, 255)
LASER_COLOR = (255, 50, 50)
LASER_WIN_COLOR = (50, 255, 50)
NORMAL_COLOR = (150, 150, 150)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laser Mirrors")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

def cross2d(v, w):
    return v[0] * w[1] - v[1] * w[0]

def line_intersection(p, r, q, s):
    rxs = cross2d(r, s)
    q_p = (q[0] - p[0], q[1] - p[1])
    
    if abs(rxs) < 1e-6:
        return None, None
        
    t = cross2d(q_p, s) / rxs
    u = cross2d(q_p, r) / rxs
    
    if t >= 0 and 0 <= u <= 1:
        return t, (p[0] + t * r[0], p[1] + t * r[1])
    return None, None

class Mirror:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.length = 100.0
        self.hovered = False
        self.curvature = 0

    def get_segments(self):
        # If the mirror is flat, just draw one fast straight line
        if abs(self.curvature) < 1:
            rad = math.radians(self.angle)
            dx = math.cos(rad) * (self.length / 2)
            dy = math.sin(rad) * (self.length / 2)
            return [((self.x - dx, self.y - dy), (self.x + dx, self.y + dy))]

        segments = []
        RESOLUTION = 12 # 12 segments creates a buttery smooth curve
        
        # Calculate how deep the curve is based on the slider (-45 to 45)
        bend_factor = self.curvature / 45.0 
        max_depth = self.length / 4 
        
        points = []
        for i in range(RESOLUTION + 1):
            # t goes from -0.5 (left edge) to 0.5 (right edge)
            t = (i / RESOLUTION) - 0.5 
            
            # Local coordinates (building a parabola flat on the X axis)
            local_x = t * self.length
            # Parabola equation: vertex is at (0,0) so the center of the mirror stays on the mouse
            local_y = bend_factor * max_depth * ((2 * t)**2) 

            # Rotate the points to match the mirror's actual angle
            rad = math.radians(self.angle)
            rot_x = local_x * math.cos(rad) - local_y * math.sin(rad)
            rot_y = local_x * math.sin(rad) + local_y * math.cos(rad)
            
            points.append((self.x + rot_x, self.y + rot_y))

        # Connect the dots into line segments for the laser to bounce off of
        for i in range(len(points) - 1):
            segments.append((points[i], points[i+1]))
            
        return segments

    def get_normal(self, incoming_dir, segment_pts):
        p1, p2 = segment_pts
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length == 0: return (0, 0)
        dx /= length
        dy /= length
        
        n1 = (-dy, dx)
        n2 = (dy, -dx)
        
        dot1 = incoming_dir[0] * n1[0] + incoming_dir[1] * n1[1]
        if dot1 < 0:
            return n1
        return n2

    def check_hover(self, mx, my):
        self.hovered = False
        for p1, p2 in self.get_segments():
            l2 = (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2
            if l2 == 0: continue
            t = max(0, min(1, ((mx - p1[0]) * (p2[0] - p1[0]) + (my - p1[1]) * (p2[1] - p1[1])) / l2))
            proj = (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
            dist = math.sqrt((mx - proj[0])**2 + (my - proj[1])**2)
            if dist < 10:
                self.hovered = True
                break
        return self.hovered

class OpticsGame:
    def __init__(self):
        self.emitter_rect = pygame.Rect(20, HEIGHT // 2 - 20, 40, 40)
        self.target_rect = pygame.Rect(WIDTH - 60, HEIGHT // 2 - 60, 40, 120)
        self.mirrors = [
            Mirror(300, 200, 45)
        ]
        self.dragging_mirror = None
        self.win = False
        self.current_mirror_trigger = 0
        self.local_anim_trigger = 0
        self.animating = False
        self.anim_progress = 1.0 # Tracks how many nodes of the path to draw

    def get_laser_path(self):
        path = []
        bounces = []
        start_pt = (self.emitter_rect.right, self.emitter_rect.centery)
        direction = (1.0, 0.0)
        path.append(start_pt)
        
        self.win = False
        
        global MAX_BOUNCES
        for _ in range(MAX_BOUNCES): # Max bounces
            closest_t = float('inf')
            closest_intersect = None
            closest_mirror = None
            closest_segment = None
            
            # Check mirror intersections
            for mirror in self.mirrors:
                for seg in mirror.get_segments():
                    p1, p2 = seg
                    q = p1
                    s = (p2[0] - p1[0], p2[1] - p1[1])
                    
                    t, pt = line_intersection(start_pt, direction, q, s)
                    if t is not None and 1e-4 < t < closest_t:
                        closest_t = t
                        closest_intersect = pt
                        closest_mirror = mirror
                        closest_segment = seg
            
            # Check target intersection
            q_target = (self.target_rect.left, self.target_rect.top)
            s_target = (0, self.target_rect.height)
            t_target, pt_target = line_intersection(start_pt, direction, q_target, s_target)
            
            if t_target is not None and 1e-4 < t_target < closest_t:
                path.append(pt_target)
                self.win = True
                break
                
            # Walls
            walls = [
                ((0, 0), (WIDTH, 0)), ((WIDTH, 0), (0, HEIGHT)),
                ((WIDTH, HEIGHT), (-WIDTH, 0)), ((0, HEIGHT), (0, -HEIGHT))
            ]
            for w_q, w_s in walls:
                t_w, pt_w = line_intersection(start_pt, direction, w_q, w_s)
                if t_w is not None and 1e-4 < t_w < closest_t:
                    closest_t = t_w
                    closest_intersect = pt_w
                    closest_mirror = None
            
            if closest_intersect:
                path.append(closest_intersect)
                if closest_mirror:
                    normal = closest_mirror.get_normal(direction, closest_segment)
                    dot = direction[0] * normal[0] + direction[1] * normal[1]
                    ref_x = direction[0] - 2 * dot * normal[0]
                    ref_y = direction[1] - 2 * dot * normal[1]
                    
                    dot_clamped = min(1.0, abs(dot))
                    inc_angle = math.degrees(math.acos(dot_clamped))
                    bounces.append((closest_intersect, normal, inc_angle))
                    
                    direction = (ref_x, ref_y)
                    start_pt = closest_intersect
                else:
                    break
            else:
                path.append((start_pt[0] + direction[0]*2000, start_pt[1] + direction[1]*2000))
                break
                
        return path, bounces

    def draw(self):
        screen.fill(BG_COLOR)
        
        pygame.draw.rect(screen, EMITTER_COLOR, self.emitter_rect)
        pygame.draw.rect(screen, TARGET_COLOR if not self.win else LASER_WIN_COLOR, self.target_rect)
        
        path, bounces = self.get_laser_path()
        
        # --- ANIMATION LOGIC (Comet Effect) ---
        if self.animating:
            self.anim_progress += ANIM_SPEED 
            head_index = int(self.anim_progress)
            
            
            tail_index = max(0, head_index - ANIM_TRAIL)
            
            
            if tail_index >= len(path):
                self.animating = False 
            else:
                
                path = path[tail_index:head_index + 1]
                
                
                bounce_tail = max(0, tail_index - 1)
                bounce_head = max(0, head_index)
                bounces = bounces[bounce_tail:bounce_head]
        
        
        laser_color = LASER_WIN_COLOR if self.win else LASER_COLOR
        
        if len(path) > 1:
            pygame.draw.lines(screen, laser_color, False, path, 3)
            
        for mirror in self.mirrors:
            color = MIRROR_HOVER if mirror.hovered else MIRROR_COLOR
            for p1, p2 in mirror.get_segments():
                pygame.draw.line(screen, color, p1, p2, 6)
            
        for pt, normal, angle in bounces:
            n_end = (pt[0] + normal[0] * 30, pt[1] + normal[1] * 30)
            pygame.draw.line(screen, NORMAL_COLOR, pt, n_end, 1)
            
            # ONLY draw the text if the checkbox is ticked!
            if SHOW_ANGLES:
                text = f"θ = {angle:.1f}°"
                text_surf = font.render(text, True, TEXT_COLOR)
                screen.blit(text_surf, (pt[0] + 10, pt[1] - 20))
            
        instructions = "Drag to move | Q/E or Mouse Wheel to rotate | ESC: Quit"
        inst_surf = pygame.font.Font(None, 24).render(instructions, True, (150, 150, 150))
        screen.blit(inst_surf, (20, HEIGHT - 30))

def main():
    game = OpticsGame()
    running = True
    frame_count = 0
    global MAX_BOUNCES, ADD_MIRROR_TRIGGER
    
    while running:
        frame_count += 1
        if frame_count % 10 == 0:
            try:
                with open('sim_data.json', 'r') as f:
                    sim_data = json.load(f)
                    MAX_BOUNCES = sim_data["optics"]["max_bounces"]
                    ADD_MIRROR_TRIGGER = sim_data["optics"]["add_mirror_trigger"]
                    global SHOW_ANGLES, ANIMATE_LASER_TRIGGER, ANIM_SPEED, ANIM_TRAIL
                    SHOW_ANGLES = sim_data["optics"].get("show_angles", True)
                    ANIMATE_LASER_TRIGGER = sim_data["optics"].get("animate_laser_trigger", 0)
                    ANIM_SPEED = sim_data["optics"].get("anim_speed", 0.5)
                    ANIM_TRAIL = sim_data["optics"].get("anim_trail", 3)
                    configs = sim_data["optics"].get("mirrors_config", {})
            except Exception as e:
                pass
                
            # Catch the Animation Trigger
            if ANIMATE_LASER_TRIGGER > game.local_anim_trigger:
                game.animating = True
                game.anim_progress = 1.0 # Reset animation to the start
                game.local_anim_trigger = ANIMATE_LASER_TRIGGER

            # Add new mirrors if button was clicked
            if ADD_MIRROR_TRIGGER > game.current_mirror_trigger:
                diff = ADD_MIRROR_TRIGGER - game.current_mirror_trigger
                for _ in range(diff):
                    nx = 400 + random.randint(-100, 100)
                    ny = 300 + random.randint(-100, 100)
                    game.mirrors.append(Mirror(nx, ny, 0))
                game.current_mirror_trigger = ADD_MIRROR_TRIGGER
                
            # Apply individual lengths and curves!
            for i, mirror in enumerate(game.mirrors):
                # Match the names generated by the controller
                key = "Mirror 1 (Default)" if i == 0 else f"Mirror {i+1}"
                if key in configs:
                    mirror.length = configs[key]["length"]
                    mirror.curvature = configs[key]["curve"]
                
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    subprocess.Popen([sys.executable, "sim_controller.py"])
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for mirror in game.mirrors:
                        if mirror.hovered:
                            game.dragging_mirror = mirror
                            break
                elif event.button == 4:
                    for mirror in game.mirrors:
                        if mirror.hovered:
                            mirror.angle += 5
                elif event.button == 5:
                    for mirror in game.mirrors:
                        if mirror.hovered:
                            mirror.angle -= 5
                            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    game.dragging_mirror = None
                    
            if event.type == pygame.MOUSEMOTION:
                if game.dragging_mirror:
                    game.dragging_mirror.x = mx
                    game.dragging_mirror.y = my
                else:
                    for mirror in game.mirrors:
                        mirror.check_hover(mx, my)
                        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            for mirror in game.mirrors:
                if mirror.hovered:
                    mirror.angle -= 2
        if keys[pygame.K_e]:
            for mirror in game.mirrors:
                if mirror.hovered:
                    mirror.angle += 2
                    
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
