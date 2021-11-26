import pygame
import os
import random
from pygame import mixer
from Sprite_sheet import SpriteSheet
from Enemy import Enemy

mixer.init()
pygame.init()

window_width = 400
window_height = 600

window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Jumpy")
icon = pygame.image.load(os.path.join("Assets/jump.png"))
pygame.display.set_icon(icon)

pygame.mixer.music.load(os.path.join("Assets/music.mp3"))
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1, 0.0)
jump_sound = pygame.mixer.Sound(os.path.join("Assets/jump.mp3"))
jump_sound.set_volume(0.5)
death_sound = pygame.mixer.Sound(os.path.join("Assets/death.mp3"))
death_sound.set_volume(0.5)

scroll_thresh = 200
gravity = 1
max_platforms = 20
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

if (os.path.exists("score.txt")):
    with (open("score.txt", "r")) as file:
        high_score = int(file.read())
else:
    high_score = 0

font_small = pygame.font.SysFont("Lucida Sans", 20)
font_big = pygame.font.SysFont("Lucida Sans", 30)

jumpy_img = pygame.image.load(os.path.join("Assets/jump.png"))
bg_img = pygame.image.load(os.path.join("Assets/bg.png"))
platform_img = pygame.image.load(os.path.join("Assets/wood.png"))
bird_image = pygame.image.load(os.path.join("Assets/bird.png"))

bird_sheet = SpriteSheet(bird_image)

def draw_text(text, font, text_colour, x, y):
    img = font.render(text, True, text_colour)
    window.blit(img, (x, y))

def draw_panel():
    pygame.draw.rect(window, (153, 217, 234), (0, 0, window_width, 30))
    pygame.draw.line(window, (255, 255, 255), (0, 30), (window_width, 30), 2)
    draw_text("SCORE: " + str(score), font_small, (255, 255, 255), 0, 0)

def draw_bg(bg_scroll):
    window.blit(bg_img, (0, 0 + bg_scroll))
    window.blit(bg_img, (0, -600 + bg_scroll))

class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(jumpy_img, (45, 45))
        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False
    
    def move(self):
        scroll = 0
        dx = 0
        dy = 0

        key = pygame.key.get_pressed()
        if (key[pygame.K_a]):
            dx = -10
            self.flip = True
        if (key[pygame.K_d]):
            dx = 10
            self.flip = False

        self.vel_y += gravity
        dy += self.vel_y

        if (self.rect.left + dx < 0):
            dx = -self.rect.left
        if (self.rect.right + dx > window_width):
            dx = window_width - self.rect.right

        for platform_ in platform_group:
            if (platform_.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height)):
                if (self.rect.bottom < platform_.rect.centery):
                    if (self.vel_y > 0):
                        self.rect.bottom = platform_.rect.top
                        dy = 0
                        self.vel_y = -20
                        jump_sound.play()

        if (self.rect.top <= scroll_thresh):
            if (self.vel_y < 0):
                scroll = -dy

        self.rect.x += dx
        self.rect.y += dy + scroll

        return scroll

    def draw(self):
        window.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5))

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_img, (width, 10))
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        if (self.moving):
            self.move_counter += 1
            self.rect.x += self.direction * self.speed

        if (self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > window_height):
            self.direction *= -1
            self.move_counter = 0

        self.rect.y += scroll

        if (self.rect.top > window_height):
            self.kill()

jumpy = Player(window_width // 2, window_height - 150)

platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

platform = Platform(window_width // 2 - 50, window_height - 50, 100, False)
platform_group.add(platform)

clock = pygame.time.Clock()
fps = 60

run = True
while run:
    clock.tick(fps)

    if (game_over == False):
        scroll = jumpy.move()

        bg_scroll += scroll
        if (bg_scroll >= 600):
            bg_scroll = 0
        draw_bg(bg_scroll)

        if (len(platform_group) < max_platforms):
            p_w = random.randint(40, 60)
            p_x = random.randint(0, window_width - p_w)
            p_y = platform.rect.y - random.randint(80, 120)
            p_type = random.randint(1, 2)
            if (p_type == 1 and score > 500):
                p_moving = True
            else:
                p_moving = False
            platform = Platform(p_x, p_y, p_w, p_moving)
            platform_group.add(platform)

        platform_group.draw(window)
        enemy_group.draw(window)

        platform_group.update(scroll)
        enemy_group.update(scroll, window_width)

        if (len(enemy_group) == 0 and score > 1500):
            enemy = Enemy(window_width, 100, bird_sheet, 1.5)
            enemy_group.add(enemy)

        if (scroll > 0):
            score += scroll

        pygame.draw.line(window, (255, 255, 255), (0, score - high_score + scroll_thresh), (window_width, score - high_score + scroll_thresh), 3)
        draw_text("HIGH SCORE: " + str(high_score), font_small, (255, 255, 255), window_width - 125, score - high_score + scroll_thresh)

        jumpy.draw()

        draw_panel()

        if (jumpy.rect.top > window_height):
            game_over = True
            death_sound.play()

        if (pygame.sprite.spritecollide(jumpy, enemy_group, False)):
            if pygame.sprite.spritecollide(jumpy, enemy_group, False, pygame.sprite.collide_mask):
                game_over = True
                death_sound.play()
    else:
        if (fade_counter < window_width):
            fade_counter += 5
            for i in range(0, 6, 2):
                pygame.draw.rect(window, (0, 0, 0), (0, i * 100, fade_counter, 100))
                pygame.draw.rect(window, (0, 0, 0), (window_width - fade_counter, (i + 1) * 100, window_width, 100))
        else:
            draw_text("GAME OVER!", font_big, (255, 255, 255), 135, 200)
            draw_text("SCORE: " + str(score), font_big, (255, 255, 255), 135, 250)
            draw_text("PRESS SPACE TO PLAY AGAIN!", font_big, (255, 255, 255), 50, 300)
            if (score > high_score):
                high_score = score
                with (open("score.txt", "w")) as file:
                    file.write(str(high_score))
            key = pygame.key.get_pressed()
            if (key[pygame.K_SPACE]):
                game_over = False
                score = 0
                scroll = 0
                fade_counter = 0
                jumpy.rect.center = (window_width // 2, window_height - 150)
                enemy_group.empty()
                platform_group.empty()
                platform = Platform(window_width // 2 - 50, window_height - 50, 100, False)
                platform_group.add(platform)

    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            if (score > high_score):
                high_score = score
                with (open("score.txt", "w")) as file:
                    file.write(str(high_score))
            run = False
    
    pygame.display.update()
pygame.quit()