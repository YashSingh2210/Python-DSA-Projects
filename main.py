import pygame
import random
import numpy as np # pyright: ignore[reportMissingImports]

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Screen
WIDTH, HEIGHT = 600, 500
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge Block Pro with Power-up Indicators & Text")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 50)
CYAN = (50, 255, 255)
ORANGE = (255, 165, 0)

# Fonts
font = pygame.font.SysFont(None, 28)
large_font = pygame.font.SysFont(None, 50)

# Player
player_width, player_height = 50, 50
player_vel = 6

# Game variables
best_score = 0

# Stars for animated background
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1,3)] for _ in range(50)]

# Power-up class
class PowerUp:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind  # "speed" or "shield"
        self.size = 20
        self.color = YELLOW if kind=="speed" else CYAN
        self.speed = 3
    
    def move(self):
        self.y += self.speed
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))

# Sound generation using NumPy
def play_beep(frequency=440, duration=150, volume=0.3):
    sample_rate = 44100
    t = np.linspace(0, duration/1000, int(sample_rate*duration/1000), False)
    wave = np.sin(frequency * 2 * np.pi * t) * 32767
    wave = wave.astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))  # 2 channels
    sound = pygame.sndarray.make_sound(stereo_wave)
    sound.set_volume(volume)
    sound.play()

# Main game function
def main_game():
    global best_score
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - player_height - 10
    
    blocks = []
    powerups = []
    score = 0
    enemies_dodged = 0
    powerups_collected = 0
    shield = False
    speed_boost = False
    boost_timer = 0
    
    base_block_speed = 4
    run = True
    game_over = False
    pause = False
    clock = pygame.time.Clock()
    
    while run:
        clock.tick(60)
        win.fill(BLACK)
        
        # Update background stars
        for star in stars:
            star[1] += star[2]
            if star[1] > HEIGHT:
                star[0] = random.randint(0, WIDTH)
                star[1] = 0
                star[2] = random.randint(1,3)
            pygame.draw.circle(win, WHITE, (star[0], star[1]), star[2])
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and not game_over:
                    pause = not pause
                if event.key == pygame.K_SPACE and game_over:
                    return
        
        keys = pygame.key.get_pressed()
        if not game_over and not pause:
            # Move player
            current_vel = player_vel * 1.5 if speed_boost else player_vel
            if keys[pygame.K_LEFT] and player_x - current_vel > 0:
                player_x -= current_vel
            if keys[pygame.K_RIGHT] and player_x + player_width + current_vel < WIDTH:
                player_x += current_vel
            
            # Gradual difficulty
            difficulty_multiplier = 1 + (score // 500)
            
            # Spawn blocks
            if random.randint(1, 20) == 1:
                block_x = random.randint(0, WIDTH - 50)
                block_y = -50
                block_speed = base_block_speed + random.randint(0,3) + difficulty_multiplier
                color = random.choice([RED, BLUE, GREEN])
                size = random.randint(30, 60)
                blocks.append([block_x, block_y, block_speed, size, color])
            
            # Spawn power-ups occasionally
            if random.randint(1, 500) == 1:
                kind = random.choice(["speed","shield"])
                powerups.append(PowerUp(random.randint(20, WIDTH-20), -20, kind))
            
            # Move blocks
            for block in blocks:
                block[1] += block[2]
                pygame.draw.rect(win, block[4], (block[0], block[1], block[3], block[3]))
            
            # Move power-ups
            for pu in powerups:
                pu.move()
                pu.draw(win)
            
            # Collision detection with blocks
            for block in blocks:
                if (player_x < block[0] + block[3] and
                    player_x + player_width > block[0] and
                    player_y < block[1] + block[3] and
                    player_y + player_height > block[1]):
                    if shield:
                        shield = False
                    else:
                        game_over = True
                        play_beep(300,300)  # Game over beep
            
            # Collision with power-ups
            for pu in powerups[:]:
                if (player_x < pu.x + pu.size and
                    player_x + player_width > pu.x and
                    player_y < pu.y + pu.size and
                    player_y + player_height > pu.y):
                    if pu.kind == "speed":
                        speed_boost = True
                        boost_timer = pygame.time.get_ticks()
                    elif pu.kind == "shield":
                        shield = True
                    powerups_collected += 1
                    powerups.remove(pu)
                    play_beep(700,100)  # Power-up collected
            
            # Remove off-screen blocks
            new_blocks = []
            for block in blocks:
                if block[1] < HEIGHT:
                    new_blocks.append(block)
                else:
                    enemies_dodged += 1
                    play_beep(500,50)
            blocks = new_blocks
            
            # Remove off-screen powerups
            powerups = [pu for pu in powerups if pu.y < HEIGHT]
            
            # Update score
            score += 1
            if score // 10 > best_score:
                best_score = score // 10
            
            # Check speed boost timer
            if speed_boost and pygame.time.get_ticks() - boost_timer > 5000:
                speed_boost = False
        
        # Draw player with visual indicators
        if shield:
            color = CYAN
        else:
            color = BLUE
        
        pygame.draw.rect(win, color, (player_x, player_y, player_width, player_height))
        
        # Speed boost visual indicator (yellow border)
        if speed_boost:
            pygame.draw.rect(win, YELLOW, (player_x-3, player_y-3, player_width+6, player_height+6), 3)
        
        # Draw stats
        stats_text = font.render(f"Score: {score//10}  Best: {best_score}  Dodged: {enemies_dodged}  Power-ups: {powerups_collected}", True, WHITE)
        win.blit(stats_text, (10,10))
        
        # Draw power-up text indicators
        shield_text = "ON" if shield else "OFF"
        speed_text = "ON" if speed_boost else "OFF"
        powerup_status = font.render(f"Shield: {shield_text}  Speed Boost: {speed_text}", True, ORANGE)
        win.blit(powerup_status, (10, 35))
        
        if pause and not game_over:
            pause_text = large_font.render("PAUSED", True, YELLOW)
            win.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
        
        if game_over:
            over_text = large_font.render("GAME OVER!", True, RED)
            restart_text = font.render("Press SPACE to Restart", True, WHITE)
            win.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 50))
            win.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))
        
        pygame.display.update()

# Run game
while True:
    main_game()

pygame.quit()
