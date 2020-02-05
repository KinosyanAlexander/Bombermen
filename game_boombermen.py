#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import os
from copy import deepcopy
import random as rn
import time


def load_image(name, colorkey=None):
    way = os.getcwd()
    #print(way)
    fullname = way + '\\' + os.path.join('data\\images\\', name)
    #print(fullname)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
cell_size = 32
is_full_screen = 0
is_game_now = False
is_it_start = True
is_music_playing = 1
is_sounds_playing = 1


with open('data\\stages\\stage_1.txt', encoding='utf-8') as f:
    stage = list(map(lambda x: list(x), f.read().split('\n')))


pygame.init()



pygame.font.init()
myfont = pygame.font.SysFont('sitkasmallsitkatextbolditalicsitkasubheadingbolditalicsitkaheadingbolditalicsitkadisplaybolditalicsitkabannerbolditalic', 35, bold = True)

#pygame.mouse.set_visible(False)

w, h = cell_size * 15 + 10, cell_size * 13 + 55 #490, 471

sc = pygame.display.set_mode((w, h))

def resize_sp(sp, zoom=0):
    '''
    for i, v in enumerate(sp):
        sp[i] = pygame.transform.scale(v, (int(v.get_width() * 1), int(v.get_height() * 1)))
    '''
    if not zoom:
        for i, v in enumerate(sp):
            sp[i] = pygame.transform.scale2x(v)
    return sp


orange_left_anim = resize_sp([load_image(f'norm_orange_bombermen\\men{i}.png', -1) for i in range(3)])
orange_front_anim = resize_sp([load_image(f'norm_orange_bombermen\\men{i}.png', -1) for i in range(3, 6)])
orange_right_anim = resize_sp([load_image(f'norm_orange_bombermen\\men{i}.png', -1) for i in range(6, 9)])
orange_nazad_anim = resize_sp([load_image(f'norm_orange_bombermen\\men{i}.png', -1) for i in range(9, 12)])
orange_die_anim = resize_sp([load_image(f'norm_orange_bombermen\\men{i}.png', -1) for i in range(12, 18)])
orange_victory = resize_sp([load_image(f'norm_orange_bombermen\\orange_win.png', -1) for i in range(1)])[0]

white_nazad_anim = resize_sp([load_image(f'white_bombermen\\men{i}.png', -1) for i in range(3)])
white_left_anim = resize_sp([load_image(f'white_bombermen\\men{i}.png', -1) for i in range(3, 6)])
white_front_anim = resize_sp([load_image(f'white_bombermen\\men{i}.png', -1) for i in range(6, 9)])
white_right_anim = resize_sp([load_image(f'white_bombermen\\men{i}.png', -1) for i in range(9, 12)])
white_die_anim = resize_sp([load_image(f'white_bombermen\\men{i}.png', -1) for i in range(12, 21)])
white_victory = resize_sp([load_image(f'white_bombermen\\white_win.png', -1) for i in range(1)])[0]


stone = pygame.transform.scale2x(load_image('enviroment\\stone.png'))
brick = pygame.transform.scale2x(load_image('enviroment\\bricks.png'))
grass = pygame.transform.scale2x(load_image('enviroment\\grass.png'))
grass_2 = pygame.transform.scale2x(load_image('enviroment\\grass_2.png'))
ugol_grass = pygame.transform.scale2x(load_image('enviroment\\ugol_grass.png'))

bomb_anim = resize_sp([load_image(f'events_on_pole\\bomb\\bomb{i + 1}.png') for i in range(3)])

fire_centers = resize_sp([load_image(f'events_on_pole\\fire\\center{i + 1}.png') for i in range(5)])
fire_ends = resize_sp([load_image(f'events_on_pole\\fire\\end{i + 1}.png') for i in range(5)])
fire_parts = resize_sp([load_image(f'events_on_pole\\fire\\part{i + 1}.png') for i in range(5)])

fire_brick = resize_sp([load_image(f'events_on_pole\\brick_on_fire\\st{i + 1}.png') for i in range(6)])

bonus_plus_bomb = resize_sp([load_image(f'bonuses\\plus_bomb{i + 1}.png') for i in range(2)])
bonus_plus_fire_size = resize_sp([load_image(f'bonuses\\plus_fire_size{i + 1}.png') for i in range(2)])
bonus_plus_speed = resize_sp([load_image(f'bonuses\\plus_speed{i + 1}.png') for i in range(2)])
bonus_podrivnik = resize_sp([load_image(f'bonuses\\podrivnik{i + 1}.png') for i in range(2)])
bonus_die = resize_sp([load_image(f'bonuses\\die{i + 1}.png') for i in range(2)])


game_over_pole = load_image(f'dich.png')
victory_word = resize_sp([load_image(f'victory_word.png', -1) for i in range(1)])[0]

start_im = load_image('start_image.png')

sounds_im_sp = [load_image('icons\\sounds_off.png'), load_image('icons\\sounds_on.png')]
music_im_sp = [load_image('icons\\music_off.png'), load_image('icons\\music_on.png')]

FPS = 60
clock = pygame.time.Clock()
bonus_sp = ((bonus_plus_bomb, 'plus_bomb'),
            (bonus_plus_fire_size, 'plus_fire_size'),
            (bonus_plus_speed, 'plus_speed'),
            (bonus_podrivnik, 'podrivnik'), 
            (bonus_die, 'die'))


pygame.mixer.init()


def play_music(music_name):
    #music_name = 'BGM #06'
    pygame.mixer.music.load(f'data\\music\\{music_name}.mp3')
    pygame.mixer.music.play(-1)
    if not is_music_playing % 2:
        pygame.mixer.music.pause()
    pygame.mixer.music.set_volume(0.3)

def play_sound(sound):
    if is_sounds_playing % 2:
        sound.play()


Global_Music = 'BGM #06'

boom = pygame.mixer.Sound('data\\sounds\\boom.wav')
boom.set_volume(0.3)
bonus_sound = pygame.mixer.Sound('data\\sounds\\bonus.wav')
bonus_sound.set_volume(0.3)


class Board():
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.left = 5
        self.top = 50
        self.cell_size = cell_size
        #self.surfaces = [[rn.choice((stone, brick, 'grass')) for i in range(self.w)] for j in range(self.h)]
        
        self.pole = deepcopy(stage)
        
        # Переделка уровня в файле на surface
        self.surfaces = deepcopy(stage)
        for y, v in enumerate(self.surfaces):
            for x, k in enumerate(v):
                if k == 'g':
                    if y == 0:
                        self.surfaces[y][x] = grass_2
                        if x == self.w - 1:
                            self.surfaces[y][x] = pygame.transform.rotate(ugol_grass, 0)
                        elif x == 0:
                            self.surfaces[y][x] = pygame.transform.rotate(ugol_grass, 90)
                    elif y == self.h - 1:
                        self.surfaces[y][x] = pygame.transform.rotate(grass_2, 180)
                        if x == self.w - 1:
                            self.surfaces[y][x] = pygame.transform.rotate(ugol_grass, -90)
                        elif x == 0:
                            self.surfaces[y][x] = pygame.transform.rotate(ugol_grass, 180)
                    elif x == 0 and y not in (0, self.h - 1):
                        self.surfaces[y][x] = pygame.transform.rotate(grass_2, 90)
                    elif x == self.w - 1 and y not in (0, self.h - 1):
                        self.surfaces[y][x] = pygame.transform.rotate(grass_2, -90)
                    else:
                        self.surfaces[y][x] = grass
                elif k == 'k':
                    self.surfaces[y][x] = brick
                elif k == 's':
                    self.surfaces[y][x] = stone
        
        self.rects = [[pygame.Rect((self.left + i * self.cell_size, self.top + j * self.cell_size),
                                    (self.cell_size, self.cell_size))
                       for i in range(self.w)] for j in range(self.h)]
    
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.surfaces = [[rn.choice((stone, brick)) for i in range(self.w)] for j in range(self.h)]
        self.rects = [[pygame.Rect((self.left + i * self.cell_size, self.top + j * self.cell_size),
                                    (self.cell_size, self.cell_size)) 
                       for i in range(self.w)] for j in range(self.h)]
    
    def render(self):
        for i in range(self.h):
            for u in range(self.w):
                sc.blit(self.surfaces[i][u], self.rects[i][u])
    
    def get_cell(self, mouse_pos):
        n = 0
        for i in range(self.h):
            for u in range(self.w):
                if self.rects[i][u].collidepoint(mouse_pos):
                    n = 1
                    return (i, u)
                    break
            if n:
                break
    
    def on_called(self, rect_id):
        self.rects[rect_id[0]][rect_id[1]].x = 500


class Bombermen(pygame.sprite.Sprite):
    def __init__(self, pos, uprav_keys, anim_keys):
        pygame.sprite.Sprite.__init__(self)
        self.uprav_keys = uprav_keys
        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]
        self.anim_keys = anim_keys
        
        self.front_anim = anim_keys['front']
        self.left_anim = anim_keys['left']
        self.right_anim = anim_keys['right']
        self.nazad_anim = anim_keys['nazad']
        self.die_anim = anim_keys['die']
        self.victory_im = anim_keys['victory']
        
        self.sp = self.front_anim
        self.c = 0
        self.v = 100
        self.lim = 18
        self.rect = self.sp[self.c].get_rect()
        self.rect.bottomleft = self.pos
        self.last_move = ('self.y -= 0', 'midbottom', 'bottomleft', 'bottomright', 'y')
        self.bombs = pygame.sprite.Group()
        self.fires = pygame.sprite.Group()
        self.lim_bombs = 1
        self.max_size_fire = 2
        self.lifes = 1
        self.is_he_life = True
        self.is_podrivnik = False
    
    def update(self):
        #self.anim(keys)
        '''
        surf = self.sp[(self.c // (self.lim // len(self.sp))) % len(self.sp)]
        self.rect = surf.get_rect()
        self.rect.bottomleft = (int(self.x), int(self.y))
        '''
        if self.bombs:
            for i in self.bombs:
                pos = i.update()
                if pos:
                    self.fires.add(Fire(pos, i.max_size_fire))
        
        self.fires.update()
        
        
        coord = board.get_cell(self.rect_in.center)
        cell = board.pole[coord[0]][coord[1]]
        
        
        if cell == 'f':
            if self.lifes > 0:
                self.lifes -= 1
        elif cell == 'plus_bomb':
            self.lim_bombs += 1
        elif cell == 'plus_speed':
            self.v += 25
        elif cell == 'plus_fire_size':
            self.max_size_fire += 1
        elif cell == 'podrivnik':
            self.is_podrivnik = True
        elif cell == 'die':
            self.lifes -= 1
        
        
        for i in bonuses:
            if i.pos == coord:
                play_sound(bonus_sound)
                i.die()
                break
        
        if self.lifes == 0:
            if self.is_he_life == True:
                self.c = 0
                self.is_he_life = False
                self.sp = self.die_anim
                if len(self.sp) > 6:
                    self.lim = len(self.sp) * 6
                else:
                    self.lim = len(self.sp) * 10
                self.x, self.y = self.rect.center
                
                for i in self.bombs:
                    bombs.add(i)
                    self.bombs.remove(i)
                
                for i in self.fires:
                    fires.add(i)
                    self.fires.remove(i)
                
            self.die()
    
    def draw(self, surf):
        sc.blit(surf, self.rect)
    
    def anim(self, keys):
        if keys[self.uprav_keys['execute_bomb']]:
            if len(self.bombs) < self.lim_bombs:
                pos = board.get_cell(self.rect_in.center)
                if board.pole[pos[0]][pos[1]] == 'g':
                    self.bombs.add(Bomb(pos, self.max_size_fire, self.is_podrivnik))
        
        if keys[self.uprav_keys['podriv']]:
            if self.is_podrivnik:
                for i in self.bombs:
                    i.is_podriv = True
        
        
        if keys[self.uprav_keys['down']]:
            self.sp = self.front_anim
            self.c += 1
            self.y += self.v / FPS
            self.last_move = ('self.y -= self.v / FPS', 'bottom', 'bottomleft', 'bottomright', 'y')
        elif keys[self.uprav_keys['up']]:
            self.sp = self.nazad_anim
            self.c += 1
            self.y -= self.v / FPS
            self.last_move = ('self.y += self.v / FPS', 'top', 'topleft', 'topright', 'y')
        elif keys[self.uprav_keys['left']]:
            self.sp = self.left_anim
            self.c += 1
            self.x -= self.v / FPS
            self.last_move = ('self.x += self.v / FPS', 'left', 'topleft', 'bottomleft', 'x')
        elif keys[self.uprav_keys['right']]:
            self.sp = self.right_anim
            self.c += 1
            self.x += self.v / FPS
            self.last_move = ('self.x -= self.v / FPS', 'right', 'topright', 'bottomright', 'x')
        else:
            self.c = 0
            self.lim = 18
            self.sp = self.front_anim
        
        if self.c > self.lim:
            self.c = 0
        
        #self.rect.bottomleft = (int(self.x), int(self.y))
        # Теперь проверки на то, не заезжает ли куда не надо герой
        
        while not (board.left + 10) <= int(self.x) <= board.left + board.w * cell_size - 35:
            if int(self.x) < board.left + 10:
                self.x += 1
            elif int(self.x) > board.left + board.w * cell_size - 35:
                self.x -= 1
        
        while not (board.top + 10) <= int(self.y) <= board.top + board.h * cell_size - 10:
            if int(self.y) < board.top + 10:
                self.y += 1
            elif int(self.y) > board.top + board.h * cell_size - 10:
                self.y -= 1
        
        
        
        
        surf = self.sp[(self.c // (self.lim // len(self.sp))) % len(self.sp)]
        self.rect = surf.get_rect()
        self.rect.bottomleft = (int(self.x), int(self.y))
        
        
        self.rect_in = pygame.Rect((self.rect.topleft[0] + int((1/5 * self.rect.width)), 
                                    self.rect.topleft[1] + int((1/1.8 * self.rect.height))), 
                                    (self.rect.width - 2.5 * int((1/5 * self.rect.width)), 
                                    self.rect.height - int((1/1.8 * self.rect.height))))
        
        for i in range(board.h):
            for u in range(board.w):
                if board.pole[i][u] in ('s', 'k', 'b'):
                    col_rect = self.rect_in.clip(board.rects[i][u])
                    if col_rect and not col_rect.collidepoint(self.rect_in.center):
                        pyta = board.rects[i][u]
                        
                        sp_x = range(pyta.left, pyta.right + 1)
                        sp_y = range(pyta.top, pyta.bottom + 1)
                        
                        if eval(f'self.rect_in.{self.last_move[1]}') in eval(f'sp_{self.last_move[-1]}'):
                            exec(self.last_move[0])
                        self.rect.bottomleft = (self.x, self.y)
        
        self.draw(surf)
        # коммент ниже рисует рект, по которому определяются пересечения
        #pygame.draw.rect(sc, RED, self.rect_in)
    def die(self):
        
        custome_id = (self.c // (self.lim // len(self.sp))) % len(self.sp)
        
        
        if len(self.sp) == 6 and custome_id == 5:
            self.c += 0.5
        else:
            self.c += 1
        
        surf = self.sp[int(custome_id)]
        self.rect = surf.get_rect()
        self.rect.center = (int(self.x), int(self.y))
        
        self.draw(surf)
        
        if self.c == self.lim:
            pygame.mixer.music.stop()
            self.kill()


class Bomb(pygame.sprite.Sprite):
    sp = bomb_anim
    
    def __init__(self, pos, max_size_fire, podriv):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.c = 0
        self.is_podriv = False
        self.podriv = podriv
        self.lim_anim = 51
        self.timer = 0
        self.max_size_fire = max_size_fire
    
    def update(self):
        if not self.timer % 2:
            self.c += 1
        else:
            self.c -= 1
        if self.c >= self.lim_anim:
            self.c = self.lim_anim - 3
            self.timer += 1
        elif self.c <= 0:
            self.c = 3
            self.timer += 1
        
        
        surf = self.sp[(self.c // (self.lim_anim // len(self.sp))) % len(self.sp)]
        board.pole[self.pos[0]][self.pos[1]] = 'b'
        board.surfaces[self.pos[0]][self.pos[1]] = surf
        if (self.timer >= 4 and not self.podriv) or (self.podriv and self.is_podriv):
            self.die()
            return self.pos
            
            
        
    def die(self):
        play_sound(boom)
        self.kill()
        board.pole[self.pos[0]][self.pos[1]] = 'g'
        board.surfaces[self.pos[0]][self.pos[1]] = grass


class Fire(pygame.sprite.Sprite):
    def __init__(self, center, max_size):
        pygame.sprite.Sprite.__init__(self)
        self.center = center
        okrug = (((0, -1), (90, False)), ((0, 1), (90, True)), ((-1, 0), (0, False)), ((1, 0), (0, True)))
        self.sp = [[self.center, 'fire_centers', (0, False)]]
        board.pole[center[0]][center[1]] = 'f'
        self.max_size_fire = max_size
        deep = 0
        
        def found_all_victims(pos, okrug, angle):
            nonlocal deep 
            deep += 1
            next_cell_pos = (pos[0] + okrug[0], pos[1] + okrug[1])
            next_cell = board.pole[next_cell_pos[0]][next_cell_pos[1]]
            if next_cell in ('g') and deep <= self.max_size_fire:
                self.sp.append([next_cell_pos, 'fire_parts', angle])
                board.pole[next_cell_pos[0]][next_cell_pos[1]] = 'f'
                return found_all_victims(next_cell_pos, okrug, angle)
            else:
                if self.sp[-1][1] != 'fire_centers':
                    self.sp[-1][1] = 'fire_ends'
                if next_cell in ('k'):
                    dying_bricks.add(FireBrick(next_cell_pos))
                if next_cell in ('b'):
                    
                    
                    def proverka_bomb(bomb_sp):
                        for i in bomb_sp:
                            if i.pos == next_cell_pos:
                                i.podriv = True
                                i.is_podriv = True
                                break
                    
                    
                    proverka_bomb(players.sprites()[0].bombs)
                    proverka_bomb(players.sprites()[1].bombs)
                    proverka_bomb(bombs)
                if next_cell in list(map(lambda x: x[1], bonus_sp)):
                    for i in bonuses:
                        if i.pos == next_cell_pos:
                            i.die()
                            break
                    
        
        for i in range(4):
            deep = 0
            found_all_victims(center, okrug[i][0], okrug[i][1])
        
        self.timer = 0
        self.c = 0
        self.lim_anim = 30
        
    def update(self):
        costume_id = (self.c // (self.lim_anim // 5)) % 5
        
        if not self.timer % 2:
            if costume_id != 4:
                self.c += 2
            else:
                self.c += 1
        else:
            if costume_id != 4:
                self.c -= 2
            else:
                self.c -= 1
        if self.c >= self.lim_anim:
            self.c = self.lim_anim - 1
            self.timer += 1
        elif self.c <= 0:
            self.timer += 1
        
        costume_id = (int(self.c) // (self.lim_anim // 5)) % 5
        
        for i in self.sp:
            if i[2][1]:
                xbool, ybool = (i[2][0] == 90, i[2][0] == 0)
                board.surfaces[i[0][0]][i[0][1]] = eval(f'pygame.transform.flip(pygame.transform.rotate({i[1]}[{costume_id}], {i[2][0]}), {xbool}, {ybool})')
            else:
                board.surfaces[i[0][0]][i[0][1]] = eval(f'pygame.transform.rotate({i[1]}[{costume_id}], {i[2][0]})')
        
        if self.timer == 2:
            self.die()
    
    def die(self):
        for i in self.sp:
            board.pole[i[0][0]][i[0][1]] = 'g'
            board.surfaces[i[0][0]][i[0][1]] = grass
        self.kill()


class FireBrick(pygame.sprite.Sprite):
    sp = fire_brick
    
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.y = pos[0]
        self.x = pos[1]
        self.pos = pos
        self.c = 0
        self.lim_anim = 30
    
    def update(self):
        self.c += 1
        
        surf = self.sp[(self.c // (self.lim_anim // len(self.sp))) % len(self.sp)]
        board.pole[self.y][self.x] = 'b'
        board.surfaces[self.y][self.x] = surf
        if self.c == self.lim_anim:
            self.kill()
            
            if rn.randint(0, len(bonus_sp) * 6) % 3 == 0:
                bonus = rn.choice(bonus_sp)
                bonuses.add(Bonus(self.pos, bonus[0], bonus[1]))
            else:
                board.pole[self.y][self.x] = 'g'
                board.surfaces[self.y][self.x] = grass


class Bonus(pygame.sprite.Sprite):
    def __init__(self, pos, anim_sp, bonus):
        pygame.sprite.Sprite.__init__(self)
        self.sp = anim_sp
        self.lim_anim = 10
        self.c = 0
        self.pos = pos
        #self.men = men
        self.bonus = bonus
    
    def update(self):
        self.c += 1
        surf = self.sp[(self.c // (self.lim_anim // len(self.sp))) % len(self.sp)]
        board.pole[self.pos[0]][self.pos[1]] = self.bonus
        board.surfaces[self.pos[0]][self.pos[1]] = surf
    
    def die(self):
        board.pole[self.pos[0]][self.pos[1]] = 'g'
        board.surfaces[self.pos[0]][self.pos[1]] = grass
        self.kill()


class MusicSet(pygame.sprite.Sprite):
    def __init__(self, im_sp, pos, tip):
        pygame.sprite.Sprite.__init__(self)
        self.sp = im_sp
        if tip == 'music':
            self.image = self.sp[is_music_playing % 2]
        elif tip == 'sounds':
            self.image = self.sp[is_sounds_playing % 2]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.tip = tip
    
    def on_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.func()
    
    def func(self):
        global is_music_playing, is_sounds_playing
        if self.tip == 'music':
            is_music_playing += 1
            if is_music_playing % 2:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.pause()
            self.image = self.sp[is_music_playing % 2]
        elif self.tip == 'sounds':
            is_sounds_playing += 1
            self.image = self.sp[is_sounds_playing % 2]
    
    def draw(self):
        sc.blit(self.image, self.rect)

dict_2 = {'execute_bomb': pygame.K_RETURN,
          'up': pygame.K_UP,
          'down': pygame.K_DOWN,
          'left': pygame.K_LEFT,
          'right': pygame.K_RIGHT,
          'podriv': pygame.K_RSHIFT}

dict_1 = {'execute_bomb': pygame.K_e,
          'up': pygame.K_w,
          'down': pygame.K_s,
          'left': pygame.K_a,
          'right': pygame.K_d,
          'podriv': pygame.K_TAB}


anim_keys_1 = {'front': orange_front_anim,
               'nazad': orange_nazad_anim,
               'left': orange_left_anim,
               'right': orange_right_anim,
               'die': orange_die_anim,
               'victory': orange_victory}

anim_keys_2 = {'front': white_front_anim,
               'nazad': white_nazad_anim,
               'left': white_left_anim,
               'right': white_right_anim,
               'die': white_die_anim,
               'victory': white_victory}



def settings():
    global board, players, bonuses, fires, bombs, dying_bricks, is_game_now, is_it_start, music_sets
    
    play_music(Global_Music)
    
    board = Board(15, 13)
    #board.set_view(5, 50, cell_size)
    dying_bricks = pygame.sprite.Group()
    
    player_1 = Bombermen((cell_size + 5, 40 + cell_size * 2), dict_1, anim_keys_1)
    player_2 = Bombermen((cell_size * 14 - 25, 45 + cell_size * 12), dict_2, anim_keys_2)

    players = pygame.sprite.Group()

    players.add(player_1)
    players.add(player_2)

    music_sets = pygame.sprite.Group()
    music_sets.add(MusicSet(music_im_sp, (w - 50, 5), 'music'))
    music_sets.add(MusicSet(sounds_im_sp, (w - 100, 5), 'sounds'))
    
    bonuses = pygame.sprite.Group()
    #ban = Bonus((2, 2), bonus_plus_bomb, 'plus_bomb')
    #ban3 = Bonus((4, 5), bonus_plus_bomb, 'plus_bomb')
    #ban2 = Bonus((6, 5), bonus_plus_bomb, 'plus_bomb')
    #bonuses.add(ban)
    #bonuses.add(ban2)
    #bonuses.add(ban3)


    fires = pygame.sprite.Group()


    bombs = pygame.sprite.Group()
    is_game_now = True
    is_it_start = False



run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            elif event.key == pygame.K_F5:
                if is_full_screen:
                    sc = pygame.display.set_mode((w, h))
                    is_full_screen = 0
                else:
                    sc = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
                    is_full_screen = 1
            elif event.key == pygame.K_f:
                if not is_game_now:
                    pygame.mixer.music.stop()
                    time.sleep(0.5)
                    settings()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i in music_sets:
                i.on_click(event.pos)
                    
    
    keys = pygame.key.get_pressed()
    
    
    if is_game_now:
        sc.fill(BLACK)
        
        
        board.render()
        
        music_sets.draw(sc)
        for i in players:
            if i.lifes:
                i.anim(keys)
        players.update()
        dying_bricks.update()
        bonuses.update()
        
        for i in bombs:
            pos = i.update()
            if pos:
                fires.add(Fire(pos, i.max_size_fire))
        
        fires.update()
        if len(players) != 2:
            is_game_now = False
            time.sleep(0.5)
            if players:
                winner = players.sprites()[0]
        #sc.blit(music_on_im, (w - 50, 5))
    else:
        if not pygame.mixer.music.get_busy():
            if is_it_start:
                play_music('Title Theme')
            else:
                play_music('Victory')
        if is_it_start:
            sc.blit(start_im, (0, 0))
        else:
            sc.blit(game_over_pole, (0, 0))
            sc.blit(victory_word, (100, 10))
            sc.blit(winner.victory_im, (150, 120))
            sc.blit(myfont.render('  press F to restart', True, RED), (60, 400))
            
    
    clock.tick(FPS)
    pygame.display.flip()
    pygame.display.update()
pygame.quit()
