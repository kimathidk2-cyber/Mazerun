import pygame
import random
import sys
import os
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Phillips Exeter Academy - Dorm Dash")
clock = pygame.time.Clock()

# Polished color palette
WHITE = (248, 248, 248)           
LIGHT_GREY = (220, 220, 220)      
BLACK = (0, 0, 0)
CRIMSON = (140, 35, 52)          
RED = (185, 65, 65)              
GREEN = (90, 150, 90)            
YELLOW = (235, 205, 85)          
OAK_BROWN = (101, 67, 33)       
DARK_OAK = (75, 50, 25)        
GOLD = (255, 215, 0)           

EXETER_DORMS = [
    "Lamont", "Wheelwright", "Dunbar", "Amon", "Dutch House", 
    "Main Street", "Wentworth", "Webster", "Soule", "Abbot", 
    "Ewald, ew", "McConnell", "Langdell", "Front Street", "Dow House", 
    "Knight House", "New Hall", "Peabody", "Merrill
]


GRID_SIZE = 100
GRID_COLS = WIDTH // GRID_SIZE
GRID_ROWS = HEIGHT // GRID_SIZE

class Particle:
    def __init__(self, x, y, color, velocity, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 4)
    
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1
        
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color_with_alpha = (*self.color[:3], alpha)
            s = pygame.Surface((self.size * 2, self.size * 2))
            s.set_alpha(alpha)
            s.fill(self.color)
            screen.blit(s, (int(self.x), int(self.y)))

class Player:
    def __init__(self):
        self.rect = pygame.Rect(55, HEIGHT - 95, 40, 40)  # Adjusted for frame
        self.speed = 4
        self.color = CRIMSON
        self.border_color = DARK_OAK
    
    def move(self, keys, walls):
        dx = 0
        dy = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed
        
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                if dx < 0:
                    self.rect.left = wall.right
        
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                if dy < 0:
                    self.rect.top = wall.bottom
    
    def draw(self, screen):
      
        border_rect = pygame.Rect(self.rect.x - 2, self.rect.y - 2, 
                                 self.rect.width + 4, self.rect.height + 4)
        pygame.draw.rect(screen, self.border_color, border_rect)
        pygame.draw.rect(screen, self.color, self.rect)
    
    def reset_position(self):
        self.rect.topleft = (55, HEIGHT - 95)  # Adjusted for frame

class Enemy:
    def __init__(self, x, y, size, color):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        self.border_color = DARK_OAK
    
    def draw(self, screen):
      
        border_rect = pygame.Rect(self.rect.x - 1, self.rect.y - 1, 
                                 self.rect.width + 2, self.rect.height + 2)
        pygame.draw.rect(screen, self.border_color, border_rect)
        pygame.draw.rect(screen, self.color, self.rect)

class WanderingEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 35, RED)
        self.direction_x = random.choice([-2, -1, 1, 2])
        self.direction_y = random.choice([-2, -1, 1, 2])
        self.move_timer = 0
        self.speed_boost = random.choice([1.0, 1.2, 1.5])  # Some enemies are faster
        self.aggressiveness = random.choice([0.7, 1.0, 1.3])  # Some change direction more
    
    def update(self, walls):
      
        self.move_timer += 1
        direction_change_chance = int(120 / self.aggressiveness)
        
        if self.move_timer > random.randint(80, direction_change_chance):
            self.direction_x = random.choice([-2, -1, 1, 2])
            self.direction_y = random.choice([-2, -1, 1, 2])
            self.move_timer = 0
        
        old_x = self.rect.x
        old_y = self.rect.y
        
      
        move_x = int(self.direction_x * self.speed_boost)
        move_y = int(self.direction_y * self.speed_boost)
        
        self.rect.x += move_x
        self.rect.y += move_y
        
        hit_wall = False
        for wall in walls:
            if self.rect.colliderect(wall):
                hit_wall = True
                break
        
        if hit_wall or self.rect.left < 20 or self.rect.right > WIDTH - 20 or self.rect.top < 20 or self.rect.bottom > HEIGHT - 20:
            self.rect.x = old_x
            self.rect.y = old_y
            self.direction_x = -self.direction_x
            self.direction_y = -self.direction_y

class Token:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.color = YELLOW
        self.border_color = DARK_OAK
        self.pulse_timer = random.randint(0, 60)  # Random start for animation variety
    
    def update(self):
        self.pulse_timer += 1
    
    def draw(self, screen):
        
        pulse = abs(pygame.math.Vector2(0, 1).rotate(self.pulse_timer * 3).y)
        size_mod = int(2 * pulse)
        
        border_rect = pygame.Rect(self.rect.x - 1 - size_mod, self.rect.y - 1 - size_mod, 
                                 self.rect.width + 2 + size_mod * 2, self.rect.height + 2 + size_mod * 2)
        token_rect = pygame.Rect(self.rect.x - size_mod, self.rect.y - size_mod,
                               self.rect.width + size_mod * 2, self.rect.height + size_mod * 2)
        
        pygame.draw.rect(screen, self.border_color, border_rect)
        pygame.draw.rect(screen, self.color, token_rect)

class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.tokens = []
        self.walls = []
        self.particles = []  # Particle system for effects
        self.goal = pygame.Rect(WIDTH - 115, 55, 60, 60)  # Adjusted for frame
        self.tokens_collected = 0
        self.game_over = False
        self.won = False
        self.selected_dorm = random.choice(EXETER_DORMS)
        self.fade_timer = 0
        self.fade_duration = 60
        self.screen_shake = 0  # Screen shake effect
        
       
        self.level = 1
        self.max_level = 10  # Cap at level 10 (10 enemies, 7 tokens)
        self.base_enemies = 3
        self.base_tokens = 3
        self.max_enemies = 10
        self.max_tokens = 7
        
    
        try:
            self.title_font = pygame.font.SysFont("Georgia", 42, bold=True)
            self.font = pygame.font.SysFont("Georgia", 28)
            self.small_font = pygame.font.SysFont("Georgia", 20)
        except:
            self.title_font = pygame.font.SysFont(None, 42)
            self.font = pygame.font.SysFont(None, 28)
            self.small_font = pygame.font.SysFont(None, 20)
        
   
        self.exeter_seal = None
        try:
            self.exeter_seal = pygame.image.load("/mnt/user-data/uploads/Screenshot_2025-11-17_at_8_08_42_PM.png")
            self.exeter_seal = pygame.transform.scale(self.exeter_seal, (120, 120))
        except:
            pass
        
        self.setup_game()
    
    def get_current_enemy_count(self):
      
        return min(self.base_enemies + (self.level - 1), self.max_enemies)
    
    def get_current_token_count(self):
      
       
        token_bonus = (self.level - 1) // 2
        return min(self.base_tokens + token_bonus, self.max_tokens)
    
    def get_enemy_speed_multiplier(self):
       
        return min(1.0 + (self.level - 1) * 0.05, 1.5)
    
    def add_particles(self, x, y, color, count=5):
       
        for _ in range(count):
            velocity = (random.randint(-3, 3), random.randint(-3, 3))
            lifetime = random.randint(15, 30)
            self.particles.append(Particle(x, y, color, velocity, lifetime))
    
    def trigger_screen_shake(self, intensity=10):
    
        self.screen_shake = intensity
    
    def get_grid_sectors(self):
     
        for row in range(2, GRID_ROWS - 1):  
            for col in range(1, GRID_COLS - 2): 
                x = col * GRID_SIZE + random.randint(10, GRID_SIZE - 50)
                y = row * GRID_SIZE + random.randint(10, GRID_SIZE - 50)
                sectors.append((x, y))
        return sectors
    
    def spawn_enemies_in_grid(self, num_enemies):
       
        available_sectors = self.get_grid_sectors()
        random.shuffle(available_sectors)
        
        enemies_created = 0
        speed_multiplier = self.get_enemy_speed_multiplier()
        
        for sector_pos in available_sectors:
            if enemies_created >= num_enemies:
                break
            
            x, y = sector_pos
            enemy_rect = pygame.Rect(x, y, 35, 35)
            
            
            valid_spot = True
            for wall in self.walls:
                if enemy_rect.colliderect(wall):
                    valid_spot = False
                    break
            
         
            player_start_distance = ((x - 40)**2 + (y - (HEIGHT - 80))**2)**0.5
            if player_start_distance < 100:
                valid_spot = False
            
            if valid_spot:
              
                enemy = WanderingEnemy(x, y)
                enemy.speed_boost *= speed_multiplier  
                self.enemies.append(enemy)
                enemies_created += 1
    
    def generate_walls(self):
        frame_thickness = 15
        walls = [
            pygame.Rect(0, 0, WIDTH, frame_thickness),
            pygame.Rect(0, HEIGHT - frame_thickness, WIDTH, frame_thickness),
            pygame.Rect(0, 0, frame_thickness, HEIGHT),
            pygame.Rect(WIDTH - frame_thickness, 0, frame_thickness, HEIGHT),
        ]
        
        maze_choice = self.current_maze
        
        if maze_choice == 1:
          
            walls.extend([
                # Original horizontal blocks
                pygame.Rect(200, 150, 100, 20),    
                pygame.Rect(500, 150, 100, 20),    
                pygame.Rect(350, 300, 100, 20),    
                pygame.Rect(200, 450, 100, 20),   
                pygame.Rect(500, 450, 100, 20),   
                
                # Added vertical pillars to fill space
                pygame.Rect(120, 250, 20, 80),     
                pygame.Rect(660, 250, 20, 80),      
                pygame.Rect(280, 380, 20, 60),     
                pygame.Rect(520, 380, 20, 60),     
                pygame.Rect(400, 80, 20, 60),       
            ])
        else:  # maze_choice == 2
            # LAYOUT 2: Cross with additional vertical supports
            walls.extend([
                # Original cross
                pygame.Rect(300, 200, 200, 20),     
                pygame.Rect(390, 120, 20, 160),     
                pygame.Rect(390, 300, 20, 160),     
                
                # Additional vertical obstacles
                pygame.Rect(150, 120, 20, 100),     
                pygame.Rect(630, 120, 20, 100),    
                pygame.Rect(150, 380, 20, 100),    
                pygame.Rect(630, 380, 20, 100),    
                pygame.Rect(270, 350, 20, 80),     
                pygame.Rect(510, 350, 20, 80),      
            ])
        
        return walls
    
    def place_tokens_smartly(self, num_tokens):
        self.tokens = []
        maze_choice = self.current_maze
        
        if maze_choice == 1:
            good_spots = [
                (120, 200), (350, 120), (450, 120), (680, 200),
                (120, 350), (350, 380), (450, 380), (680, 350),
                (400, 250), (150, 500), (650, 500), (400, 80)
            ]
        else:  # maze_choice == 2
            good_spots = [
                (150, 150), (550, 150), (150, 450), (550, 450),
                (80, 300), (720, 300), (400, 80), (400, 520),
                (250, 300), (550, 300), (400, 160), (400, 380)
            ]
        
        random.shuffle(good_spots)
        
        placed_tokens = 0
        for spot in good_spots:
            if placed_tokens >= num_tokens:
                break
                
            x, y = spot
            x += random.randint(-30, 30)
            y += random.randint(-30, 30)
            x = max(40, min(WIDTH - 60, x))
            y = max(40, min(HEIGHT - 60, y))
            
            token_rect = pygame.Rect(x, y, 20, 20)
            
            valid_spot = True
            for wall in self.walls:
                if token_rect.colliderect(wall):
                    valid_spot = False
                    break
            
            for existing_token in self.tokens:
                distance = ((x - existing_token.rect.x)**2 + (y - existing_token.rect.y)**2)**0.5
                if distance < 80:
                    valid_spot = False
                    break
            
            if valid_spot:
                self.tokens.append(Token(x, y))
                placed_tokens += 1
        
        while len(self.tokens) < num_tokens:
            attempts = 0
            while attempts < 50:
                x = random.randint(60, WIDTH - 80)
                y = random.randint(60, HEIGHT - 80)
                token_rect = pygame.Rect(x, y, 20, 20)
                
                valid_spot = True
                for wall in self.walls:
                    if token_rect.colliderect(wall):
                        valid_spot = False
                        break
                
                for existing_token in self.tokens:
                    distance = ((x - existing_token.rect.x)**2 + (y - existing_token.rect.y)**2)**0.5
                    if distance < 80:
                        valid_spot = False
                        break
                
                if valid_spot:
                    self.tokens.append(Token(x, y))
                    break
                
                attempts += 1
    
    def setup_game(self):
        self.current_maze = random.randint(1, 2)
        self.walls = self.generate_walls()
        self.enemies = []
        self.tokens = []
        
 
        enemy_count = self.get_current_enemy_count()
        token_count = self.get_current_token_count()
        
       
        self.spawn_enemies_in_grid(enemy_count)
        
 
        self.place_tokens_smartly(token_count)
        
        self.tokens_collected = 0
        self.game_over = False
        self.won = False
    
    def update(self, keys):
        if not self.game_over:
            self.player.move(keys, self.walls)
            
            for enemy in self.enemies:
                enemy.update(self.walls)
            
    
            for token in self.tokens:
                token.update()
            
   
            self.particles = [p for p in self.particles if p.lifetime > 0]
            for particle in self.particles:
                particle.update()
            
            for enemy in self.enemies:
                if self.player.rect.colliderect(enemy.rect):
                    self.game_over = True
                    self.fade_timer = 0
                    self.trigger_screen_shake(15)  # Screen shake on getting caught
            
       
            for token in self.tokens[:]:
                if self.player.rect.colliderect(token.rect):
                    self.tokens.remove(token)
                    self.tokens_collected += 1
                    # Add golden particles when collecting tokens
                    self.add_particles(token.rect.centerx, token.rect.centery, GOLD, 8)
                    self.trigger_screen_shake(3)  # Subtle shake on collection
            
            if self.player.rect.colliderect(self.goal) and len(self.tokens) == 0:
                self.won = True
                self.game_over = True
                # Victory particle explosion
                self.add_particles(self.goal.centerx, self.goal.centery, CRIMSON, 15)
        else:
           
            if not self.won:
                self.fade_timer += 1
        
   
        if self.screen_shake > 0:
            self.screen_shake -= 1
        
        if self.game_over and keys[pygame.K_r]:
            if self.won:
         
                if self.level < self.max_level:
                    self.level += 1
            else:
            
                self.level = 1
            
            self.player.reset_position()
            self.selected_dorm = random.choice(EXETER_DORMS)
            self.fade_timer = 0
            self.particles.clear()  # Clear particles on restart
            self.screen_shake = 0
            self.setup_game()
    
    def draw1(self, screen):
        screen.fill(OAK_BROWN)
        

        for wall in self.walls:
          
            shadow_rect = pygame.Rect(wall.x + 2, wall.y + 2, wall.width, wall.height)
            pygame.draw.rect(screen, DARK_OAK, shadow_rect)
          
            pygame.draw.rect(screen, WHITE, wall)
        

        goal_border = pygame.Rect(self.goal.x - 3, self.goal.y - 3, 
                                 self.goal.width + 6, self.goal.height + 6)
        pygame.draw.rect(screen, DARK_OAK, goal_border)
        pygame.draw.rect(screen, GREEN, self.goal)
        

        for token in self.tokens:
            token.draw(screen)
        

        for enemy in self.enemies:
            enemy.draw(screen)
        

        self.player.draw(screen)
        
    def draw(self, screen):
        # Apply screen shake offset (ensure integers)
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        
        screen.fill(OAK_BROWN)
        
        # Draw walls with subtle depth effect
        for wall in self.walls:
    
            shadow_rect = pygame.Rect(wall.x + 2 + shake_x, wall.y + 2 + shake_y, wall.width, wall.height)
            pygame.draw.rect(screen, DARK_OAK, shadow_rect)

            wall_rect = pygame.Rect(wall.x + shake_x, wall.y + shake_y, wall.width, wall.height)
            pygame.draw.rect(screen, WHITE, wall_rect)

        goal_border = pygame.Rect(self.goal.x - 3 + shake_x, self.goal.y - 3 + shake_y, 
                                 self.goal.width + 6, self.goal.height + 6)
        pygame.draw.rect(screen, DARK_OAK, goal_border)
        goal_rect = pygame.Rect(self.goal.x + shake_x, self.goal.y + shake_y, self.goal.width, self.goal.height)
        pygame.draw.rect(screen, GREEN, goal_rect)
        
    
        for particle in self.particles:
            particle.draw(screen)
        

        for token in self.tokens:
            # Temporarily adjust token position for screen shake
            original_x, original_y = token.rect.x, token.rect.y
            token.rect.x += shake_x
            token.rect.y += shake_y
            token.draw(screen)
            token.rect.x, token.rect.y = original_x, original_y
        

        for enemy in self.enemies:
            original_x, original_y = enemy.rect.x, enemy.rect.y
            enemy.rect.x += shake_x
            enemy.rect.y += shake_y
            enemy.draw(screen)
            enemy.rect.x, enemy.rect.y = original_x, original_y
        
       
        original_x, original_y = self.player.rect.x, self.player.rect.y
        self.player.rect.x += shake_x
        self.player.rect.y += shake_y
        self.player.draw(screen)
        self.player.rect.x, self.player.rect.y = original_x, original_y
        
       
        frame_thickness = 15
       
        pygame.draw.rect(screen, LIGHT_GREY, (0, 0, WIDTH, frame_thickness))
      
        pygame.draw.rect(screen, LIGHT_GREY, (0, HEIGHT - frame_thickness, WIDTH, frame_thickness))
       
        pygame.draw.rect(screen, LIGHT_GREY, (0, 0, frame_thickness, HEIGHT))
       
        pygame.draw.rect(screen, LIGHT_GREY, (WIDTH - frame_thickness, 0, frame_thickness, HEIGHT))
        
     
        progress_text = self.font.render(f"Tokens: {self.tokens_collected}/{self.tokens_collected + len(self.tokens)}", True, WHITE)
        progress_shadow = self.font.render(f"Tokens: {self.tokens_collected}/{self.tokens_collected + len(self.tokens)}", True, DARK_OAK)
        text_x = WIDTH // 2 - progress_text.get_width() // 2
        screen.blit(progress_shadow, (text_x + 2, 12))
        screen.blit(progress_text, (text_x, 10))
        
        if self.game_over:
            if self.won:
                
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(128)
                overlay.fill(DARK_OAK)
                screen.blit(overlay, (0, 0))
                
              
                if self.exeter_seal:
                    seal_x = WIDTH // 2 - 60
                    seal_y = HEIGHT // 2 - 100
                    screen.blit(self.exeter_seal, (seal_x, seal_y))
                
                
                if self.level < self.max_level:
                    victory_text = self.title_font.render(f"Welcome to {self.selected_dorm}!", True, CRIMSON)
                    victory_shadow = self.title_font.render(f"Welcome to {self.selected_dorm}!", True, DARK_OAK)
                    text_x = WIDTH // 2 - victory_text.get_width() // 2
                    text_y = HEIGHT // 2 + 40
                    screen.blit(victory_shadow, (text_x + 2, text_y + 2))
                    screen.blit(victory_text, (text_x, text_y))
                    
                   
                    level_advance_text = self.font.render(f"Level {self.level} Complete! Advancing to Level {self.level + 1}", True, GOLD)
                    level_x = WIDTH // 2 - level_advance_text.get_width() // 2
                    screen.blit(level_advance_text, (level_x, text_y + 50))
                else:
                   
                    victory_text = self.title_font.render("You skipped so many assemblys you get stricts for life! Congrats!", True, GOLD)
                    victory_shadow = self.title_font.render("4 Life!", True, DARK_OAK)
                    text_x = WIDTH // 2 - victory_text.get_width() // 2
                    text_y = HEIGHT // 2 + 40
                    screen.blit(victory_shadow, (text_x + 2, text_y + 2))
                    screen.blit(victory_text, (text_x, text_y))
                    
                    
                    master_text = self.font.render(f"You conquered all 10 levels at {self.selected_dorm}!", True, WHITE)
                    master_x = WIDTH // 2 - master_text.get_width() // 2
                    screen.blit(master_text, (master_x, text_y + 50))
                
            else:
                
                if self.fade_timer < self.fade_duration:
                    # Fade to black effect
                    fade_alpha = min(255, (self.fade_timer * 255) // self.fade_duration)
                    fade_overlay = pygame.Surface((WIDTH, HEIGHT))
                    fade_overlay.set_alpha(fade_alpha)
                    fade_overlay.fill(BLACK)
                    screen.blit(fade_overlay, (0, 0))
                else:
                  
                    screen.fill(BLACK)
                    
                    fail_text = self.title_font.render("Caught by a Mx Elle!", True, RED)
                    text_x = WIDTH // 2 - fail_text.get_width() // 2
                    text_y = HEIGHT // 2 - 20
                    screen.blit(fail_text, (text_x, text_y))
                    

                    restart_text = self.font.render("Press R to restart or get stricts", True, WHITE)
                    restart_x = WIDTH // 2 - restart_text.get_width() // 2
                    restart_y = HEIGHT // 2 + 40
                    screen.blit(restart_text, (restart_x, restart_y))

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        game.update(keys)
        game.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
