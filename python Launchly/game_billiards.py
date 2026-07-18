import pygame
import math
import sys
import json

# Inițializare Pygame
pygame.init()

# Setări ecran
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Biliardul lui Newton - Simulator de Impuls")
clock = pygame.time.Clock()
FPS = 60

# Culori
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREEN = (34, 139, 34)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
GRAY = (150, 150, 150)

# Fonturi
font_small = pygame.font.SysFont("Arial", 14, bold=True)
font_medium = pygame.font.SysFont("Arial", 20)
font_large = pygame.font.SysFont("Arial", 28, bold=True)

global_friction = 0.99

class Ball:
    def __init__(self, x, y, radius, mass, color, is_cue=False):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.color = color
        self.vx = 0.0
        self.vy = 0.0
        self.is_cue = is_cue

    def draw(self, surface):
        # Desenează bila
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)

        # Afișează masa pe bilă
        mass_text = font_small.render(f"{self.mass:.1f}kg", True, BLACK)
        text_rect = mass_text.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(mass_text, text_rect)

    def move(self, dt):
        global global_friction
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Frecare ușoară pentru a opri bilele eventual
        self.vx *= global_friction
        self.vy *= global_friction

        if abs(self.vx) < 0.1: self.vx = 0
        if abs(self.vy) < 0.1: self.vy = 0

        # Coliziuni cu marginile
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -1

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1
        elif self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -1

def check_collision(b1, b2):
    dx = b1.x - b2.x
    dy = b1.y - b2.y
    distance = math.hypot(dx, dy)

    if distance < b1.radius + b2.radius:
        # Rezolvarea suprapunerii (pentru a nu se bloca una în alta)
        overlap = (b1.radius + b2.radius) - distance
        if distance == 0: distance = 1 # prevenire împărțire la zero
        nx = dx / distance
        ny = dy / distance

        total_mass = b1.mass + b2.mass
        b1.x += nx * overlap * (b2.mass / total_mass)
        b1.y += ny * overlap * (b2.mass / total_mass)
        b2.x -= nx * overlap * (b1.mass / total_mass)
        b2.y -= ny * overlap * (b1.mass / total_mass)

        # Ciocnire elastică 2D
        # Viteza relativă de-a lungul normalei
        dvx = b1.vx - b2.vx
        dvy = b1.vy - b2.vy
        vel_along_normal = dvx * nx + dvy * ny

        # Dacă se îndepărtează, nu face nimic
        if vel_along_normal > 0:
            return

        # Coeficient de restituire (1 = perfect elastic)
        e = 1.0

        # Impuls scalar
        j = -(1 + e) * vel_along_normal
        j /= (1 / b1.mass + 1 / b2.mass)

        # Aplicare impuls
        impulse_x = j * nx
        impulse_y = j * ny

        b1.vx += impulse_x / b1.mass
        b1.vy += impulse_y / b1.mass
        b2.vx -= impulse_x / b2.mass
        b2.vy -= impulse_y / b2.mass

def reset_level():
    # Creăm bilele: (x, y, rază, masă, culoare, is_cue)
    return [
        Ball(200, 300, 20, 1.0, WHITE, True), # Bila albă (Cue)
        Ball(700, 300, 30, 2.0, RED), # Bilă grea
        Ball(760, 270, 15, 0.5, BLUE), # Bilă ușoară
        Ball(760, 330, 20, 1.0, YELLOW) # Bilă medie
    ]

def draw_arrow(surface, color, start, end):
    pygame.draw.line(surface, color, start, end, 3)
    rotation = math.degrees(math.atan2(start[1]-end[1], end[0]-start[0]))+90
    pygame.draw.polygon(surface, color, (
        (end[0] + 5 * math.sin(math.radians(rotation)), end[1] + 5 * math.cos(math.radians(rotation))),
        (end[0] + 5 * math.sin(math.radians(rotation-120)), end[1] + 5 * math.cos(math.radians(rotation-120))),
        (end[0] + 5 * math.sin(math.radians(rotation+120)), end[1] + 5 * math.cos(math.radians(rotation+120)))
    ))

# Variabile de stare
balls = reset_level()
aiming = False
mouse_start_pos = (0, 0)
cue_ball = balls[0]

# Bucla principală
running = True
frame_count = 0
while running:
    dt = clock.tick(FPS) / 100.0 # Time step
    
    frame_count += 1
    if frame_count % 10 == 0:
        try:
            with open('sim_data.json', 'r') as f:
                sim_data = json.load(f)
                if "billiards" in sim_data:
                    balls[1].mass = sim_data["billiards"]["red_mass"]
                    balls[2].mass = sim_data["billiards"]["blue_mass"]
                    balls[3].mass = sim_data["billiards"]["yellow_mass"]
                    global_friction = sim_data["billiards"].get("friction", 0.99)
        except Exception as e:
            pass

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Verificăm dacă dăm click pe bila albă
            dist = math.hypot(mouse_pos[0] - cue_ball.x, mouse_pos[1] - cue_ball.y)
            if dist <= cue_ball.radius and cue_ball.vx == 0 and cue_ball.vy == 0:
                aiming = True
                mouse_start_pos = mouse_pos

        if event.type == pygame.MOUSEBUTTONUP:
            if aiming:
                mouse_pos = pygame.mouse.get_pos()
                # Calculăm viteza în funcție de cât a tras utilizatorul (stil praștie)
                dx = mouse_start_pos[0] - mouse_pos[0]
                dy = mouse_start_pos[1] - mouse_pos[1]
                cue_ball.vx = dx * 0.5
                cue_ball.vy = dy * 0.5
                aiming = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # R pentru Reset
                balls = reset_level()
                cue_ball = balls[0]

    # Fizica - Mișcare și Ciocniri
    moving = False
    for ball in balls:
        ball.move(dt)
        if abs(ball.vx) > 0 or abs(ball.vy) > 0:
            moving = True

    # Verifică ciocnirile între toate perechile de bile
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            check_collision(balls[i], balls[j])

    # Desenare
    screen.fill(DARK_GREEN) # Culoarea mesei de biliard

    # Desenează găurile / colțurile (pur estetic)
    for x in [0, WIDTH//2, WIDTH]:
        for y in [0, HEIGHT]:
            pygame.draw.circle(screen, BLACK, (x, y), 35)

    # Desenarea vectorilor în timpul țintirii
    if aiming:
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_start_pos[0] - mouse_pos[0]
        dy = mouse_start_pos[1] - mouse_pos[1]

        # Viteza proiectată (Vector v)
        end_x = cue_ball.x + dx
        end_y = cue_ball.y + dy
        draw_arrow(screen, WHITE, (cue_ball.x, cue_ball.y), (end_x, end_y))

        # Calcul viteză și impuls
        v_mag = math.hypot(dx, dy) * 0.5
        p_mag = cue_ball.mass * v_mag

        # UI afișare parametri înainte de lovitură
        info_text = font_medium.render(f"Viteză (v): {v_mag:.1f} m/s | Impuls (p=m*v): {p_mag:.1f} kg*m/s", True, WHITE)
        screen.blit(info_text, (20, HEIGHT - 40))

    # Desenează bilele
    for ball in balls:
        ball.draw(screen)

    # UI permanent
    title = font_large.render("Biliardul lui Newton", True, WHITE)
    screen.blit(title, (20, 20))

    instructions = [
        "Trage de bila albă (stil praștie) pentru a seta viteza și vectorul.",
        "Apasă 'R' pentru a reseta puzzle-ul.",
        "Observă cum bilele cu masă mare modifică transferul de impuls!"
    ]
    for i, inst in enumerate(instructions):
        txt = font_medium.render(inst, True, GRAY)
        screen.blit(txt, (20, 60 + i * 25))

    pygame.display.flip()

pygame.quit()
sys.exit()
