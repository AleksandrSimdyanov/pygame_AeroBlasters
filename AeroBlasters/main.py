import pygame
from pygame import K_SPACE
import random

from objects import Background, Player, Bullet, Enemy, Explosion, FallingPowerUp, Button, Fuel

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("Sounds/Defrini - Spookie.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)

#Группы
bullets_player = pygame.sprite.Group()
bullets_enemy = pygame.sprite.Group()
enemies = pygame.sprite.Group()
explosions = pygame.sprite.Group()
power_up_groups = pygame.sprite.Group()
fuel_groups = pygame.sprite.Group()

# изображение картинок
fighter = pygame.image.load("Assets/fighter.png")
logo = pygame.image.load("Assets/logo.png")
plane = pygame.image.load("Assets/plane.png")
# надпись конца игры
game_over_font = pygame.font.Font("Fonts/ghostclan.ttf", 30)
image_game_over = game_over_font.render("GAME OVER", True, pygame.color.Color("white"))
# tap to start
tap_to_start = pygame.font.Font("Fonts/Aladin-Regular.ttf", 30)
image_tap_to_start = tap_to_start.render("Tap To Play", True, pygame.color.Color("white"))
# красный счетчик
counter = 0
stats = pygame.font.Font("Fonts/DalelandsUncialBold-82zA.ttf", 25)

#функция стрельбы нашего самолета
def shoot_bullet_player():
    bullet_1 = Bullet(player.rect.centerx - 30, player.rect.centery, 6)
    bullet_2 = Bullet(player.rect.centerx + 30, player.rect.centery, 6)
    bullets_player.add(bullet_1, bullet_2)

# функция перезапуска игры
def restart():
    global counter
    player.alive = True
    player.hp = 100
    player.fuel = 100
    enemies.empty()
    bullets_enemy.empty()
    bullets_player.empty()
    explosions.empty()
    power_up_groups.empty()
    fuel_groups.empty()
    counter = 0

# размер картинки
WIDTH = 288
HEIGHT = 512
# частота инициализации противников
ENEMY_SPAWN_TIME = 4500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AeroBlasters")

FPS = 60
clock = pygame.time.Clock()

background = Background()
player = Player(WIDTH / 2 - 50, HEIGHT - 100)


# создание кнопок
sound_play = True
button_home = Button("Assets/Buttons/homeBtn.png", WIDTH / 2 - 75, 400, (20, 24))
button_replay = Button("Assets/Buttons/replay.png", WIDTH / 2, 400, (30, 35))
button_sound = Button("Assets/Buttons/soundOnBtn.png", WIDTH / 2 + 75, 400, (20, 24))

# звуки
sound_blast = pygame.mixer.Sound("Sounds/blast.wav")
sound_blast.set_volume(0.5)
sound_fuel = pygame.mixer.Sound("Sounds/fuel.wav")
sound_fuel.set_volume(0.5)
sound_mini_exp = pygame.mixer.Sound("Sounds/mini_exp.mp3")
sound_mini_exp.set_volume(0.5)
sound_gun_shot = pygame.mixer.Sound("Sounds/gunshot.wav")
sound_gun_shot.set_volume(0.5)
sound_click = pygame.mixer.Sound("Sounds/click.mp3")
sound_click.set_volume(0.5)
sound_chopper = pygame.mixer.Sound("Sounds/chopper.mp3")
sound_chopper.set_volume(0.5)
sound_plane = pygame.mixer.Sound("Sounds/plane.mp3")
sound_plane.set_volume(0.5)

last_enemy_time = 0

level = 1
counter_enemy = 0

game_start = False
game_over = False

while True:
    background.draw(screen)
    stats_image = stats.render(str(counter), True, pygame.color.Color("red"))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == K_SPACE:
                if game_start: # игра началась
                    shoot_bullet_player()
                    sound_gun_shot.play()
                    game_over = False
                if game_over and game_start is False: # игра закончилась
                    game_start = True
                    game_over = False
                    restart()
                if game_start is False and game_over is False: # игра не началась
                    game_start = True

    keys = pygame.key.get_pressed()
    # если игра началась и не закончилась
    if game_start and game_over is False:
        counter += 1
        player.fuel -= 0.05
        #Создание врага
        current_time = pygame.time.get_ticks()
        if current_time - last_enemy_time >= ENEMY_SPAWN_TIME:
            enemy_spawn_x = random.randint(50, 238)
            if 0 < level < 4:
                type_enemy = level
            elif level == 4:
                type_enemy = random.randint(4, 5)
            elif level == 5:
                type_enemy = random.randint(1, 5)
            enemy = Enemy(enemy_spawn_x, -86, type_enemy)
            enemies.add(enemy)
            last_enemy_time = current_time
        # попадание пуль по врагам
        for bullet in bullets_player:
            enemy_collide = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in enemy_collide:
                explosion = Explosion(bullet.rect.centerx, bullet.rect.centery, 1)
                explosions.add(explosion)
                enemy.hp -= 10
                if enemy.hp <= 0:
                    sound_blast.play()
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, 2)
                    explosions.add(explosion)
                    counter_enemy += 1
                    if random.random() < 0.35: # выпадение здоровья после уничтожения врагов рандомным образом
                        power_up = FallingPowerUp(enemy.rect.centerx, enemy.rect.centery)
                        power_up_groups.add(power_up)
                    if random.random() < 0.7:
                        fuel = Fuel(enemy.rect.centerx, enemy.rect.centery)
                        fuel_groups.add(fuel)
                bullet.kill()

        # попадание пуль по нашему самолету
        player_collide = pygame.sprite.spritecollide(player, bullets_enemy, True)
        for bullet in player_collide:
            if player.alive:
                player.hp -= bullet.damage
                if player.hp <= 0 or player.fuel <= 0:
                    sound_blast.play()
                    player.alive = False
                    game_start = False
                    game_over = True

            explosion = Explosion(player.rect.centerx, player.rect.centery, 1)
            explosions.add(explosion)

        # столкновение нашего и вражеского самолетов
        plane_collide = pygame.sprite.spritecollide(player, enemies, True)
        for enemy in plane_collide:
            sound_blast.play()
            explosion_player = Explosion(player.rect.centerx, player.rect.centery, 2)
            explosion_enemy = Explosion(enemy.rect.centerx, enemy.rect.centery, 2)
            explosions.add(explosion_enemy, explosion_player)
            player.alive = False
            game_start = False
            game_over = True
        explosions.update()
        explosions.draw(screen)

        # столкновение выпадающего здоровья
        if pygame.sprite.spritecollide(player, power_up_groups, True):
            player.hp += 10
            if player.hp >= 100:
                player.hp = 100
            sound_mini_exp.play()

        # столкновение выпадающего топлива
        if pygame.sprite.spritecollide(player, fuel_groups, True):
            player.fuel += 25
            if player.fuel >= 100:
                player.fuel = 100
            sound_fuel.play()

        # после 5 убитых врагов увеличивется левел и тип вражеский самолетов
        if counter_enemy >= 5:
            if level <= 4:
                level += 1
                counter_enemy = 0

        # обновление объектов
        background.update(1)
        player.update(keys)
        bullets_player.update()
        bullets_enemy.update()
        enemies.update(bullets_enemy)
        power_up_groups.update()
        fuel_groups.update()

        #Отрисовка объектов
        bullets_player.draw(screen)
        bullets_enemy.draw(screen)
        player.draw(screen)
        enemies.draw(screen)
        power_up_groups.draw(screen)
        fuel_groups.draw(screen)
        screen.blit(stats_image, (230, 15))

        # отрисовка здоровья и топлива
        pygame.draw.rect(screen, pygame.color.Color("red"), (35, 30, 100, 10), 5, border_radius=4)
        pygame.draw.rect(screen, pygame.color.Color("green"), (35, 30, player.hp, 10), 5, border_radius=4)
        pygame.draw.rect(screen, pygame.color.Color("red"), (35, 40, 100, 10), 5, border_radius=4)
        pygame.draw.rect(screen, pygame.color.Color("blue"), (35, 40, player.fuel, 10), 5, border_radius=4)
        screen.blit(plane, (7, 25))

    # если игра не началась
    if game_start is False:
        screen.fill(pygame.color.Color("black"))
        screen.blit(logo, (WIDTH // 2 - logo.get_width() / 2, 100))
        screen.blit(fighter, (WIDTH / 2 - fighter.get_width() / 2, HEIGHT / 2))
        screen.blit(image_tap_to_start, (WIDTH / 2 - image_tap_to_start.get_width() / 2, 430))

    # если игра закончилась
    if game_over:
        player.alive = False
        screen.fill(pygame.color.Color("black"))
        screen.blit(logo, (WIDTH // 2 - logo.get_width() / 2, 50))
        screen.blit(image_game_over, (WIDTH / 2 - image_game_over.get_width() / 2, HEIGHT / 2 - image_game_over.get_height() / 2))
        screen.blit(stats_image, (WIDTH / 2 - stats_image.get_width() / 2, HEIGHT / 2 - stats_image.get_height() / 2 + 50))
        if button_sound.draw(screen):
            if sound_play:
                sound_play = False
                pygame.mixer.music.stop()
                button_sound.image = pygame.image.load(f"Assets/Buttons/soundOffBtn.png")
                button_sound.image = pygame.transform.scale(button_sound.image, (20, 24))
            else:
                button_sound.image = pygame.image.load(f"Assets/Buttons/soundOnBtn.png")
                button_sound.image = pygame.transform.scale(button_sound.image, (20, 24))
                sound_play = True
                pygame.mixer.music.play(-1)
        if button_home.draw(screen):
            game_start = False
            game_over = False
            restart()
            level = 0
        if button_replay.draw(screen):
            game_start = True
            game_over = False
            restart()

    clock.tick(FPS)
    pygame.display.update()