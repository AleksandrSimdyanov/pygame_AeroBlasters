import pygame
from Tools.demo.ss1 import center

WIDTH = 288
HEIGHT = 512

# Урон врагов по их типам
ENEMY_DAMAGE = {
    1: 10,
    2: 15,
    3: 20,
    4: 25,
    5: 30
}

class Background:
    def __init__(self):
        self.image = pygame.image.load(f"Assets/bg.png")
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.rect1 = self.image.get_rect()
        self.rect2 = self.image.get_rect()
        self.rect2.bottom = 0

    def update(self, speed):
        #оба ректа движутся
        self.rect1.y += speed
        self.rect2.y += speed
        if self.rect1.top >= HEIGHT: # если рект больше высоты, то его bottom становатся top у другог ректа
            self.rect1.bottom = self.rect2.top
        if self.rect2.top >= HEIGHT:
            self.rect2.bottom = self.rect1.top

    def draw(self, screen):
        # прорисовка
        screen.blit(self.image, self.rect1)
        screen.blit(self.image, self.rect2)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.images = [] # список картинок нашего самолета
        for i in range(1, 3): # цикл создания картинок
            image = pygame.image.load(f"Assets/player{i}.png") # загрузка картинок
            image = pygame.transform.scale(image, (100, 86))
            self.images.append(image) # добавление картинок в список
        self.image = self.images[0] # создаем атрибут с нулевым индексом нашего списка
        self.rect = self.image.get_rect() # получаем ректы у картинки
        self.rect.x = x
        self.rect.y = y
        self.index = 0 # индекс картинки
        self.counter = 0 # счетчик частоты
        self.speed = 3
        self.hp = 100
        self.alive = True
        self.fuel = 100

    def update(self, keys):
        if not self.alive:
            return
        if keys[pygame.K_a] and self.rect.left >= 0: # передвижение влево
            self.rect.x -= self.speed
        elif keys[pygame.K_d] and self.rect.right <= WIDTH: # передвижение вправо
            self.rect.x += self.speed
        self.counter += 1
        if self.counter >= 2:
            if self.index == 1: # если индекс равен единицы то обнуляем
                self.index = 0
            else:
                self.index = 1 # иначе он равен единице
            self.counter = 0
            self.image = self.images[self.index]

    def draw(self, screen):
        if self.alive:
            screen.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.x = x
        self.y = y
        self.type = type
        self.damage = ENEMY_DAMAGE.get(type, 5) # атрибут урона от соперника
        if type == 6:
            type = "red_fire"
            self.speed = -5
        elif type == 4 or type == 5:
            type = 4
            self.speed = 5
        elif 1 <= type <= 3:
            self.speed = 5
        self.image = pygame.image.load(f"Assets/Bullets/{type}.png")
        self.image = pygame.transform.scale(self.image, (20, 40))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.rect.centery += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.x = x
        self.y = y
        self.type = enemy_type
        self.hp = 100
        self.images = []
        if self.type < 4: # самолеты
            for i in range(1, 3):
                image1 = pygame.image.load(f"Assets/Enemies/enemy{self.type}-{i}.png")
                image = pygame.transform.scale(image1, (100, 86))
                self.images.append(image)
        elif 3 < self.type < 6: # вертолеты
            for i in range(1, 3):
                image1 = pygame.image.load(f"Assets/Choppers/chopper{self.type - 3}-{i}.png")
                image = pygame.transform.scale(image1, (100, 86))
                self.images.append(image)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.index = 0
        self.counter = 0
        self.speed = 1
        self.hp = 100
        self.counter_bullet = 0

    def update(self, group):
        self.rect.y += self.speed
        self.counter += 1
        if self.counter >= 2:
            if self.index == 1:
                self.index = 0
            else:
                self.index = 1
            self.counter = 0
            self.image = self.images[self.index]
        if self.hp <= 0:
            self.kill()
        self.counter_bullet += 1
        if self.counter_bullet >= 60:
            self.shoot(group)
            self.counter_bullet = 0

    def shoot(self, group):
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.type)
        group.add(bullet)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.x = x
        self.y = y
        self.type = type
        self.images = []
        if type == 1:
            self.num = 3
        else:
            self.num = 8
        for i in range(1, self.num + 1):
            image1 = pygame.image.load(f"Assets/Explosion{type}/{i}.png")
            height = image1.get_height() * 0.4
            width = image1.get_width() * 0.4
            image = pygame.transform.scale(image1, (height, width))
            self.images.append(image)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.index = 0
        self.counter = 0

    def update(self):
        self.counter += 1
        if self.counter >= 10:
            self.index += 1
            self.counter = 0
            if self.index >= self.num:
                self.kill()
            else:
                self.image = self.images[self.index]

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# объект выпадающего здоровья
class FallingPowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Assets/powerup.png")
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Button:
    def __init__(self, image, x, y, size: tuple):
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (size))
        self.rect = self.image.get_rect(center=(x, y))
        self.clicked = False
        self.size = size

    def update_image(self, image):
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, self.size)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos): # получаем позицию мыши
            if pygame.mouse.get_pressed()[0]: # проверяем нажали ли мы на кнопку
                if not self.clicked:
                    self.clicked = True
                    return True
            else:
                self.clicked = False
        return False

class Fuel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Assets/fuel.png")
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 1

    def update(self):
        self.rect.centery += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)
