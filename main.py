import pygame
import sys
import random
from settings import *
from player import Player
from enemy import Enemy
from bullet import Bullet
from item import Item
from map_generator import generate_map

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SHADOW STRIKE - Battle Royale 2D")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font("assets/fonts/agency_font.ttf", 36)
        self.big_font = pygame.font.Font("assets/fonts/agency_font.ttf", 72)
        
        # Load assets
        self.bg = pygame.image.load("assets/sprites/bg.jpg").convert()
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        
        # Inisialisasi
        self.player = Player(WIDTH//2, HEIGHT//2)
        self.enemies = []
        self.bullets = []
        self.items = []
        self.score = 0
        self.wave = 1
        self.game_over = False
        
        # Generate map & spawn awal
        self.map_obstacles = generate_map()
        self.spawn_wave()
        
    def spawn_wave(self):
        """Spawn musuh sesuai wave"""
        enemy_count = 3 + (self.wave * 2)
        for _ in range(enemy_count):
            x = random.randint(50, WIDTH-50)
            y = random.randint(50, HEIGHT-50)
            # Cegah spawn di atas player
            while abs(x - self.player.x) < 100 and abs(y - self.player.y) < 100:
                x = random.randint(50, WIDTH-50)
                y = random.randint(50, HEIGHT-50)
            self.enemies.append(Enemy(x, y, self.player))
        
        # Spawn item
        for _ in range(3 + self.wave):
            x = random.randint(50, WIDTH-50)
            y = random.randint(50, HEIGHT-50)
            self.items.append(Item(x, y, random.choice(['health', 'shield', 'ammo'])))
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Shooting
                    bullet = self.player.shoot()
                    if bullet:
                        self.bullets.append(bullet)
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        if self.game_over:
            return
            
        # Update player
        self.player.update()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.off_screen():
                self.bullets.remove(bullet)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            # Enemy mati kena tembak
            for bullet in self.bullets[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.health -= bullet.damage
                    self.bullets.remove(bullet)
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += 10
                        # Drop item random
                        if random.random() < 0.3:
                            self.items.append(Item(enemy.x, enemy.y, random.choice(['health', 'shield', 'ammo'])))
        
        # Update items
        for item in self.items[:]:
            if item.rect.colliderect(self.player.rect):
                item.apply(self.player)
                self.items.remove(item)
        
        # Collision player vs enemy
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect) and enemy.attack_cooldown <= 0:
                self.player.health -= 10
                enemy.attack_cooldown = 30
                if self.player.health <= 0:
                    self.game_over = True
        
        # Cek wave selesai
        if len(self.enemies) == 0:
            self.wave += 1
            self.spawn_wave()
            # Bonus health tiap wave
            self.player.health = min(self.player.health + 20, 100)
    
    def draw(self):
        # Background
        self.screen.blit(self.bg, (0, 0))
        
        # Draw map obstacles
        for obs in self.map_obstacles:
            pygame.draw.rect(self.screen, (50, 50, 50), obs)
        
        # Draw items
        for item in self.items:
            item.draw(self.screen)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # HUD
        health_text = self.font.render(f"HP: {self.player.health}", True, WHITE)
        self.screen.blit(health_text, (20, 20))
        
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 60))
        
        wave_text = self.font.render(f"Wave: {self.wave}", True, YELLOW)
        self.screen.blit(wave_text, (20, 100))
        
        ammo_text = self.font.render(f"Ammo: {self.player.ammo}", True, WHITE)
        self.screen.blit(ammo_text, (20, 140))
        
        # Game Over
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            go_text = self.big_font.render("GAME OVER", True, RED)
            self.screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 100))
            
            score_final = self.font.render(f"Final Score: {self.score}", True, WHITE)
            self.screen.blit(score_final, (WIDTH//2 - score_final.get_width()//2, HEIGHT//2))
            
            restart = self.font.render("Press R to Restart", True, YELLOW)
            self.screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 60))
        
        pygame.display.flip()
    
    def reset_game(self):
        """Reset semua state"""
        self.player = Player(WIDTH//2, HEIGHT//2)
        self.enemies.clear()
        self.bullets.clear()
        self.items.clear()
        self.score = 0
        self.wave = 1
        self.game_over = False
        self.spawn_wave()
    
    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
