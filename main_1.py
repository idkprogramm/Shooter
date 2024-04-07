from pygame import *
from random import randint

from time import time as timer


class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, size_x, size_y, speed):
        super().__init__()
        
        self.image = transform.scale(image.load(img), (size_x, size_y))
        self.speed = speed
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        global num_shots, reload_time, last_time
        
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.right < win_width:
            self.rect.x += self.speed
        if keys[K_SPACE]:
            if num_shots > 0 and not reload_time:
                self.fire()
                num_shots -= 1
            if num_shots <= 0 and not reload_time:
                reload_time = True
                last_time = timer()
    
    def fire(self):
        fire_sound.play()
        bullets.add(
            Bullet(
                "bullet.png", 
                self.rect.centerx, self.rect.top,
                15, 20,
                15)
        )
        
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        
        if self.rect.y > win_height:
            self.rect.y = -50
            self.rect.x = randint(0, win_width - 80)
            self.speed = randint(1, 5)
            
            global lost
            lost += 1
            
class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= -10:
            self.kill()
    

# Кол-во пропущенных НЛО
lost = 0
score = 0

max_lost = 10
goal_score = 10

# Фоновая музыка
mixer.init()
mixer.music.load("space.ogg")
mixer.music.play()

fire_sound = mixer.Sound("fire.ogg")

# Шрифты
font.init()
label_score_font = font.Font(None, 36)


win_width = 700
win_height = 500

window = display.set_mode((win_width, win_height))
display.set_caption("Shooter")

background = transform.scale(
    image.load("galaxy.jpg"), (win_width, win_height)
)

ship = Player("rocket.png", 5, win_height - 100, 80, 100, 10)

monsters = sprite.Group()
for _ in range(5):
    monsters.add(
        Enemy("ufo.png", 
              randint(0, win_width - 80), 
              -50, 
              80, 
              50, 
              randint(1, 5))
    )
    
asteroids = sprite.Group()
for _ in range(3):
    asteroids.add(
        Enemy("asteroid.png",
              randint(0, win_width - 80), 
              -50, 
              60, 
              40, 
              randint(1, 7))
    )
    
bullets = sprite.Group()

num_shots = 5

finish = False
run = True
reload_time = False


while run:
    time.delay(50)
    
    for e in event.get():
        if e.type == QUIT:
            run = False
    
    if not finish:
        window.blit(background, (0, 0))
        
        monsters.update()
        monsters.draw(window)
        
        bullets.update()
        bullets.draw(window)
        
        asteroids.update()
        asteroids.draw(window)
        
        ship.update()
        ship.reset()
        
        window.blit(
            label_score_font.render(
                f"Счет: {score}", True, (255, 255, 255)
            ), (10, 20)
        )
        
        window.blit(
            label_score_font.render(
                f"Пропущено: {lost}", True, (255, 255, 255)
            ), (10, 50)
        )
        
        if reload_time:
            window.blit(
                font.Font(None, 36).render(
                    "Wait, reload...", 
                    True, 
                    (255, 255, 255)),
                (260, 460)
                )
            
            if timer() - last_time >= 3:
                reload_time = False
                num_shots = 5
             
        
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for _ in collides:
            score += 1
            monsters.add(
                Enemy(
                    "ufo.png", 
                    randint(0, win_width - 80), 
                    -50, 
                    80, 
                    50, 
                    randint(1, 5)
                )
            )
        
        if (lost >= max_lost 
        or sprite.spritecollide(ship, monsters, False) 
        or sprite.spritecollide(ship, asteroids, False)):
            finish = True
            window.blit(
                font.Font(None, 80).render("YOU LOSE!", True, (255, 0, 0)),
                (200, 200)
            )
        
        if score >= goal_score:
            finish = True
            window.blit(
                font.Font(None, 80).render("YOU WIN!", True, (0, 255, 0)),
                (200, 200)
            )
        
        display.update()
    