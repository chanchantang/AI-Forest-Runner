import pygame
import neat
import os
import time
import random
import math

from pygame import display

pygame.init()
pygame.font.init()
SCREEN_WIDTH = 928
SCREEN_HEIGHT = 793
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Runner')
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.gravity = 0
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 # 0 = run, 1 = jump, 2 = slide, 3 = die
        self.update_time = pygame.time.get_ticks()
        self.scale = 2.5
        animation_types = ['run', 'jump']
        for animation in animation_types:
            #reset temporary list of images
            temp_list = []
            #count number of files in the folder
            num_of_frames = len(os.listdir(f'assets/animation/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'assets/animation/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect(topleft=(self.x,self.y))
        self.mask = pygame.mask.from_surface(self.image)

        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def jump(self):
        if self.rect.bottom >= 730:
            self.gravity = -20
            self.update_action(1)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.jump()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 730:
            self.update_action(0)#0: run
            self.rect.bottom = 730

    def update_animation(self):
        ANIMATION_COOLDOWN = 70
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, screen, monsters):
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        for monster in monsters:
            pygame.draw.line(screen, self.color, (self.rect.x + 80, self.rect.y + 35), monster.rect.center, 2)


    def update(self, screen):
        self.update_animation()
        self.apply_gravity()
        self.player_input()

demon_png = pygame.image.load("assets/monster/demon-idle.png").convert_alpha()
demon_scale = 1.5
demon_w = demon_scale*160
demon_h = demon_scale*144
demon_png = pygame.transform.scale(demon_png, (demon_scale*demon_png.get_width(), demon_scale*demon_png.get_height()))
 
hell_hound_png = pygame.image.load("assets/monster/hell-hound-run.png").convert_alpha()
hell_hound_scale = 3
hell_hound_w = hell_hound_scale*67
hell_hound_h = hell_hound_scale*32
hell_hound_png = pygame.transform.scale(hell_hound_png, (hell_hound_scale*hell_hound_png.get_width(), hell_hound_scale*hell_hound_png.get_height()))

class Monster(pygame.sprite.Sprite):
    def __init__(self, image, x, y, img_w, img_h):
        super().__init__()
        # screen location
        self.x = x
        self.y = y
        self.passed = False

        # image location specifics
        self.w = img_w
        self.h = img_h
        self.frame_index = 0
        self.index_x = 0
        self.update_time = pygame.time.get_ticks()
        self.image = image
    
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self, screen):
        sprite = pygame.Surface((self.w, self.h))
        sprite.set_colorkey((0,0,0))
        sprite.blit(self.image, (0,0), (self.index_x,0,self.w,self.h))
        screen.blit(sprite, (self.x, self.y))
        self.rect = sprite.get_rect(topleft=(self.x, self.y))
        self.mask = pygame.mask.from_surface(sprite)
        # drawing a rectangle
        #pygame.draw.rect(screen, (255,0,0), self.rect, 1)
        
    def update_animation(self):
        ANIMATION_COOLDOWN = 120
        self.index_x = self.frame_index * self.w
        #update image depending on current frame
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out the reset back to the start
        if  self.index_x == self.image.get_width()-self.w:
            self.frame_index = 0

    def collide(self, player):
        offset_x = self.x - player.rect.left
        offset_y = self.y - player.rect.top
        if player.mask.overlap(self.mask, (offset_x, offset_y)):
            return True
        return False

    def update(self, screen):
        self.update_animation()
        self.x -= 10
        self.draw(screen)

floor_img = pygame.image.load("assets/background/floor.png").convert()

tree1_img = pygame.image.load("assets/background/tree1.png")
tree2_img = pygame.image.load("assets/background/tree2.png")
tree3_img = pygame.image.load("assets/background/tree3.png")

class Background:
    def __init__(self, y, vel, img):
        self.width = img.get_width()
        self.x1 = 0
        self.x2 = self.width
        self.y = y
        self.vel = vel
        self.img = img

    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, screen):
        screen.blit(self.img, (self.x1, self.y))
        screen.blit(self.img, (self.x2, self.y))

    def update(self, screen):
        self.move()
        self.draw(screen)

font = pygame.font.Font("assets/font/Minecraft.ttf", 50)

def distance(pos_a, pos_b):
    dx = pos_a[0]-pos_b[0]
    dy = pos_a[1]-pos_b[1]
    return math.sqrt(dx**2+dy**2)

def display_score(screen, score):
    score_surf = font.render(f'Score: {score}',False,(64,64,64))
    score_rect = score_surf.get_rect(center = (SCREEN_WIDTH/2,100))
    screen.blit(score_surf,score_rect)

# def display_stats(screen):
#         text_1 = font.render(f'Dinosaurs Alive:  {str(len(dinosaurs))}', True, (0, 0, 0))
#         text_2 = font.render(f'Generation:  {pop.generation+1}', True, (0, 0, 0))
#         #text_3 = font.render(f'Game Speed:  {str(game_speed)}', True, (0, 0, 0))

#         screen.blit(text_1, (50, 450))
#         screen.blit(text_2, (50, 480))
#         #screen.blit(text_3, (50, 510))


def eval_genomes(genomes, config):
    nets = []
    ge = []
    players = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Player(100, 420))
        g.fitness = 0
        ge.append(g)

    tree1 = Background(0, 3, tree1_img)
    tree2 = Background(0, 2, tree2_img)
    tree3 = Background(0, 1, tree3_img)
    floor = Background(0, 5, floor_img)
    background = [tree3, tree2, tree1, floor]

    monsters = [Monster(hell_hound_png, 1000, 630, hell_hound_w, hell_hound_h)]

    score = 0

    FPS = 60

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        # drawing objects
        for bg in background: bg.update(screen)

        monster_ind = 0
        if len(players) > 0:
            if len(monsters) > 1 and players[0].x > monsters[0].x + monsters[0].w:
                monster_ind = 1

        else:
            run = False
            break

        for x, player in enumerate(players):
            player.update(screen)
            player.draw(screen, monsters)
            ge[x].fitness += 0.1
            
            output = nets[x].activate((player.y, distance((player.x, player.y), monsters[monster_ind].rect.midtop)))

            if output[0] > 0.5:
                player.jump()

        display_score(screen, score)

        rem = []
        add_monster = False
        for monster in monsters:
            monster.update(screen)
            for x, player in enumerate(players):
                if monster.collide(player):
                    ge[x].fitness -= 1
                    players.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not monster.passed and monster.x <= SCREEN_WIDTH / 2:
                    score += 1
                    monster.passed = True
                    add_monster = True

            if monster.x + monster.w < 0:
                rem.append(monster)
            
        if add_monster:
            for g in ge:
                g.fitness += 5
            
            monsters.append(Monster(hell_hound_png, 1000, 630, hell_hound_w, hell_hound_h))
            # if random.randint(0,1):
            #     monsters.append(Monster(demon_png, 1000, 420,demon_w, demon_h))
            # else:
            #     monsters.append(Monster(hell_hound_png, 1000, 630, hell_hound_w, hell_hound_h))

        for r in rem:
            monsters.remove(r)

        pygame.display.update()
        clock.tick(FPS)

def run(config_path):
    config = neat.config.Config(
            neat.DefaultGenome, 
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet, 
            neat.DefaultStagnation,
            config_path
    )

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)