import pygame, sys, pickle, math
from pygame import mixer
from threading import Timer
from mysql import connector as sql
from tkinter import *
import worlds_menu

mycon = sql.connect(host='localhost', user='root', password='password', database='mario')
if mycon.is_connected():
    print('Success')
cursor = mycon.cursor()

def world_load(user, user_world):
    global offset, gameRunning, score, game_time, highscore, best_time, time

    pygame.init()
    font_30 = pygame.font.Font(None,30)
    font_40 = pygame.font.Font(None,40)
    font_60 = pygame.font.Font(None,60)

    coin_sound = mixer.Sound('sounds/coin_collection.wav')
    heart_sound = mixer.Sound('sounds/heart_collection.wav')
    enemy_sound = mixer.Sound('sounds/enemy_stomp.wav')
    fireball_sound = mixer.Sound('sounds/fireball.wav')
    jump_sound = mixer.Sound('sounds/jump.wav')
    damaged_sound = mixer.Sound('sounds/damaged.wav')
    death_sound = mixer.Sound('sounds/death.wav')
    level_sound = mixer.Sound('sounds/level_finished.wav')
    sounds = [coin_sound, heart_sound, enemy_sound, fireball_sound, jump_sound, damaged_sound, death_sound, level_sound]
    for sound in sounds:
        sound.set_volume(0.25)
    
    game_time = None
    highscore = None
    best_time = None

    time = 0
    score = 0    
    def show_score(score):
        score_text = font_30.render("Score: " + str(score), True, 'Black', 'White')
        screen.blit(score_text, (10, 10))

    def show_time(time):
        minutes = time // 60
        seconds = time % 60
        time_text = font_30.render(f"Time: {minutes}m {seconds}s", True, 'Black', 'White')
        screen.blit(time_text, (500, 10))
    
    gameRunning = True    
 
    with open(f"./worlds/{user_world}",'rb') as f:
        world = pickle.load(f)
        
    vec = pygame.math.Vector2

    screen = pygame.display.set_mode((640,670))
    clock = pygame.time.Clock()
    bg = pygame.transform.scale(pygame.image.load('images/sky.jpg'), (640,640))
    tile_size = 64
    offset = 0

    text_surface_1 = font_30.render('Exit',True,'Black')
    text_surface_3 = font_40.render('Try Again',True,'Red','Black')
    text_surface_4 = font_40.render('Back to menu',True,'Green','Black')

    e_rect = text_surface_1.get_rect(topleft = (595,645))
    t_rect = text_surface_3.get_rect(center = (230,395))
    b_rect = text_surface_4.get_rect(center = (390,395))
    

    grassImg = pygame.transform.scale(pygame.image.load('images/grass.png'), (64, 64)).convert()
    tileImg = pygame.transform.scale(pygame.image.load('images/tile.png'), (64, 64)).convert()
    plantImg = pygame.transform.scale(pygame.image.load('images/plant_enemy.png'), (60, 60))
    marioImg = pygame.transform.scale(pygame.image.load('images/mario.png'), (60, 60))
    heartImg = pygame.transform.scale(pygame.image.load('images/heart.png'), (48, 48))
    flagImg = pygame.transform.scale(pygame.image.load('images/flag.png'), (48, (48)*2))
    goombaImg = pygame.transform.scale(pygame.image.load('images/goomba.png'), (56, 56))
    coinImg = pygame.transform.scale(pygame.image.load('images/coin.png'), (32, 32))
    imgs = [None, grassImg, tileImg, flagImg, coinImg, goombaImg, plantImg, heartImg]
    fireballImg = pygame.transform.scale(pygame.image.load('images/fireball.png'), (32, 32))

    class player(pygame.sprite.Sprite):
        def __init__(self,image,x,y) -> None:
            super().__init__()
            self.img = image.convert_alpha()
            self.imgflip = pygame.transform.flip(image,True,False).convert_alpha()
            self.imgvul = self.img.copy()
            self.imgvulflip = self.imgflip.copy()
            self.imgvul.set_alpha(190)
            self.imgvulflip.set_alpha(190)
            self.rect = self.img.get_rect()

            self.pos = vec(x,y)
            self.vel_x = 0
            self.vel_y = 0
            
            self.jumping = False
            self.rect.x = x
            self.rect.y = y

            self.lives = 1
            self.vulnerable = True
            self.direction = 1
        
        def reset_vulnerability(self):
            self.vulnerable = True

        def take_damage(self):
            global gameRunning

            if(self.vulnerable):
                self.lives -= 1
                damaged_sound.play()
                self.vulnerable = False
                Timer(2.5, self.reset_vulnerability).start()
            if(self.lives <= 0):
                death_sound.play()
                gameRunning = False

        def update(self):
            global offset, gameRunning, score

            if(gameRunning):
                dx,dy = 0,0

                key = pygame.key.get_pressed()
                if key[pygame.K_RIGHT]:
                    dx += 5
                if key[pygame.K_LEFT]:
                    dx -= 5
                if key[pygame.K_SPACE] and not(self.jumping):
                    self.vel_y = -35
                    jump_sound.play()
                    self.jumping = True

                self.vel_y += 2
                if self.vel_y > 15:
                    self.vel_y = 15
                dy += self.vel_y

                for coin in coins:
                    distanceX = math.sqrt(math.pow(coin.x - self.rect.x, 2))
                    distanceY = math.sqrt(math.pow(coin.y - self.rect.y, 2))

                    if(distanceX < 56 and distanceY < 32):
                        coin.kill()
                        score += 1
                        coin_sound.play()

                for tile in tiles:
                    if tile.rect.colliderect(self.rect.x + dx, self.rect.y, 52, 60):
                        dx = 0

                        if(tile.img == flagImg):
                            score += 5          
                            level_sound.play()                  
                            gameRunning = False                            
                        
                        if(tile.img == heartImg):
                            self.lives += 1
                            heart_sound.play()
                            if(tile):
                                tile.kill()
                                non_player_objects.remove(tile)

                    if tile.rect.colliderect(self.rect.x, self.rect.y + dy, 52, 60):
                        if(tile.img == heartImg):
                            self.lives += 1
                            heart_sound.play()
                            if(tile):
                                tile.kill()
                                non_player_objects.remove(tile)

                        if self.vel_y < 0:
                            dy = self.rect.top - tile.rect.bottom
                            self.vel_y = 0

                            if(tile.img == flagImg):
                                score += 5
                                level_sound.play()               
                                gameRunning = False

                        if self.vel_y > 0:
                            dy = tile.rect.top - self.rect.bottom
                            if self.jumping:
                                self.jumping = False
                            if dy == 0:
                                self.vel_y = 0

                            if(tile.img == flagImg):
                                score += 5
                                level_sound.play()
                                gameRunning = False
                
                for goomba in goombas:
                    if goomba.rect.colliderect(self.rect.x + dx, self.rect.y, 52, 60):
                        dx = 0
                        self.take_damage()              

                    if goomba.rect.colliderect(self.rect.x, self.rect.y + dy, 52, 60):
                        if self.vel_y < 0: 
                            dy = goomba.rect.bottom - self.rect.top
                            self.vel_y = 0
                            self.take_damage()  
                            
                        if self.vel_y > 0: 
                            dy = goomba.rect.top - self.rect.bottom
                            if self.jumping:
                                self.jumping = False
                            if(dy == 0):
                                self.vel_y = 0;
                                goomba.kill()
                                non_player_objects.remove(goomba)
                                score += 1
                                enemy_sound.play()
                
                for plant in plants:
                    if plant.rect.colliderect(self.rect.x + dx, self.rect.y, 52, 60):
                        dx = 0

                    if plant.rect.colliderect(self.rect.x, self.rect.y + dy, 52, 60):
                        if self.vel_y > 0: 
                            dy = plant.rect.top - self.rect.bottom
                            if self.jumping:
                                self.jumping = False
                            if(dy == 0):
                                self.vel_y = 0
                                plant.kill()
                                non_player_objects.remove(plant)
                                score += 1
                                enemy_sound.play()

                for fireball in fireballs:
                    if fireball.rect.colliderect(self.rect.x + dx, self.rect.y, 52, 60):
                        self.take_damage()  
                        fireball.kill()

                    if fireball.rect.colliderect(self.rect.x, self.rect.y + dy, 52, 60):
                        self.take_damage()  
                        fireball.kill()

    
                if self.rect.right + dx > 1280:
                    dx = 1280 - self.rect.right
                if self.rect.left + dx < 0:
                    dx = -self.rect.left

                if dx < 0:
                    self.direction = -1
                elif dx > 0:
                    self.direction = 1
                
                self.rect.x += dx
                if self.rect.x >= 320 and self.rect.x <= 960:
                    offset -= dx
                if offset > 0:
                    offset = 0
                elif offset < -640:
                    offset = -640
                self.rect.y += dy

                if(self.rect.y > 640):
                    self.lives = 0

            if self.vulnerable:
                if self.direction == -1:
                    screen.blit(self.imgflip,(self.rect.x + offset ,self.rect.y))
                else:
                    screen.blit(self.img,(self.rect.x + offset ,self.rect.y))
            else:
                if self.direction == -1:
                    screen.blit(self.imgvulflip,(self.rect.x + offset ,self.rect.y))
                else:
                    screen.blit(self.imgvul,(self.rect.x + offset ,self.rect.y))

    class block(pygame.sprite.Sprite):
        def __init__(self,image,x,y) -> None:
            super().__init__()
            self.img = image
            self.pos = vec(x,y)
            self.rect = self.img.get_rect()
            self.rect.x = x
            self.rect.y = y
    
    class coin(pygame.sprite.Sprite):
        def __init__(self,image,x,y) -> None:
            super().__init__()
            self.img = image
            self.pos = vec(x,y)
            self.x = x
            self.y = y

    class goomba(pygame.sprite.Sprite):
        def __init__(self,image,x,y) -> None:
            super().__init__()
            self.img = image
            self.rect = self.img.get_rect()

            self.pos = vec(x,y)
            self.vel_x = 3
            self.vel_y = 0
            
            self.rect.x = x
            self.rect.y = y

            self.direction = -1
        
        def update(self):
            if gameRunning:
                dx,dy = 0,0
                dx += self.direction * self.vel_x

                self.vel_y += 2
                if self.vel_y > 15:
                    self.vel_y = 15
                dy += self.vel_y

                for obj in non_player_objects:
                    if(obj != self):
                        if obj.rect.colliderect(self.rect.x + dx, self.rect.y, 56, 56):
                            self.direction = -self.direction

                        if obj.rect.colliderect(self.rect.x, self.rect.y + dy, 56, 56):
                            dy = tile.rect.top - self.rect.bottom
                            if(dy == 0):
                                self.vel_y = 0
                
                for fireball in fireballs:
                    if fireball.rect.colliderect(self.rect.x + dx, self.rect.y, 56, 56):
                        self.kill()
                        fireball.kill()
                        non_player_objects.remove(self)
                
                if self.rect.right + dx > 1280:
                    self.direction = -1
                if self.rect.left + dx < 0:
                    self.direction = 1

                self.rect.x += dx
                if(dy >= 0):
                    self.rect.y += dy
                
                if(self.rect.y > 640):
                    self.kill();
                    non_player_objects.remove(self)

            screen.blit(self.img,(self.rect.x + offset ,self.rect.y))

    class plant(pygame.sprite.Sprite):
        def __init__(self,image,x,y) -> None:
            super().__init__()
            self.img = image
            self.rect = self.img.get_rect()

            self.pos = vec(x,y)

            self.vel_y = 0

            self.fireball_state = "ready"
            
            self.rect.x = x
            self.rect.y = y 
        
        def reset_fireball(self):
            self.fireball_state = "ready"

        def shoot_fireball(self, direction):
            class fireball(pygame.sprite.Sprite):
                def __init__(self2,image,x,y,direction) -> None:
                    super().__init__()
                    self2.img = image
                    self2.rect = self2.img.get_rect()

                    self2.pos = vec(x,y)
                    self2.vel_x = direction * 6
                    
                    self2.rect.x = x
                    self2.rect.y = y

                    self2.parent_plant = self
                
                def update(self2):
                    if gameRunning:
                        dx = 0
                        dx += self2.vel_x

                        for obj in non_player_objects:
                            if(obj != self2.parent_plant and obj.img != goombaImg):
                                if obj.rect.colliderect(self2.rect.x + dx, self2.rect.y, 32, 32): 
                                    self2.kill()
                        
                        if self2.rect.left > 1280:
                            self2.kill()
                        if self2.rect.right < 0:
                            self2.kill()

                        self2.rect.x += dx

                    screen.blit(self2.img,(self2.rect.x + offset, self2.rect.y))

            fireballs.add(fireball(fireballImg, self.rect.x, self.rect.y, direction))
            self.fireball_state = "fired" 
            Timer(2.5, self.reset_fireball).start()        
        
        def update(self):
            if gameRunning:
                dy = 0

                self.vel_y += 2
                if self.vel_y > 15:
                    self.vel_y = 15
                dy += self.vel_y

                for tile in tiles:
                    if tile.rect.colliderect(self.rect.x, self.rect.y + dy, 52, 60):
                        dy = tile.rect.top - self.rect.bottom

                        if(dy == 0):
                            self.vel_y = 0

                if(self.fireball_state == "ready" and mario.lives > 0):
                    distanceX = math.sqrt(math.pow((self.rect.x - mario.rect.x), 2))
                    distanceY = math.sqrt(math.pow((self.rect.y - mario.rect.y), 2))

                    if(distanceX != 0):
                        direction = (mario.rect.x - self.rect.x) / math.fabs(mario.rect.x - self.rect.x)
                    else:
                        direction = 1

                    if(distanceX < 360 and distanceY < 32):
                        fireball_sound.play()
                        self.shoot_fireball(direction)

                if(dy >= 0):
                    self.rect.y += dy

                if(self.rect.y > 640):
                    self.kill();
                    non_player_objects.remove(self)

            screen.blit(self.img,(self.rect.x + offset, self.rect.y))

    tiles = pygame.sprite.Group()
    goombas = pygame.sprite.Group()
    plants = pygame.sprite.Group()
    fireballs = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    non_player_objects = []

    def game_over():
        game_over_text = font_60.render('Game Over', True, 'Black', 'White')
        game_over_rect = game_over_text.get_rect(center = (320,320))
        screen.blit(game_over_text, game_over_rect)
        
        screen.blit(text_surface_4,b_rect)
        screen.blit(text_surface_3,t_rect)
    
    def level_finished():
        global game_time, highscore, best_time

        if(not(game_time)):
            game_time = pygame.time.get_ticks()//1000

            stats = {}
            with open(f"statistics/{user}stats.bin", 'rb') as fs:
                fs.seek(0)
                stats = pickle.load(fs)
                world_stats = stats[user_world]

                if(world_stats[0] == None or game_time < world_stats[0]):
                    world_stats[0] = game_time
                if(world_stats[1] == None or score > world_stats[1]):
                    world_stats[1] = score

                best_time = world_stats[0]
                highscore = world_stats[1]
                stats[user_world] = world_stats
            with open(f"statistics/{user}stats.bin", 'wb') as fs:
                fs.seek(0)
                pickle.dump(stats, fs)

        minutes = game_time//60
        seconds = game_time%60

        best_minutes = best_time//60
        best_seconds = best_time%60 

        level_finished_text = font_60.render('Finished Level!', True, 'Black', 'White')
        level_finished_rect = level_finished_text.get_rect(center = (320,275))
        screen.blit(level_finished_text, level_finished_rect)
        
        score_text = font_30.render(f"Score: {score}", True, 'Black', 'White')
        score_rect = score_text.get_rect(center = (320,305))
        screen.blit(score_text, score_rect)

        highscore_text = font_30.render(f"Highscore: {highscore}", True, 'Black', 'White')
        highscore_rect = highscore_text.get_rect(center = (320,325))
        screen.blit(highscore_text, highscore_rect)

        time_text = font_30.render(f"Time: {minutes}m {seconds}s", True, 'Black', 'White')
        time_rect = time_text.get_rect(center = (320,345))
        screen.blit(time_text, time_rect)

        best_time_text = font_30.render(f"Best Time: {best_minutes}m {best_seconds}s", True, 'Black', 'White')
        best_time_rect = best_time_text.get_rect(center = (320,365))
        screen.blit(best_time_text, best_time_rect)
        
        screen.blit(text_surface_4,b_rect)
        screen.blit(text_surface_3,t_rect)

    def world_init():
        row_count = 0
        for row in world:
            col_count = 0
            for num in row:
                if(num != -1):
                    tile_img = imgs[num]                
                else:
                    global mario
                    tile_img = marioImg
                    x = (tile_size * col_count + (tile_size - tile_img.get_width())/2)
                    y = tile_size * row_count + (tile_size - tile_img.get_height())
                    mario = player(marioImg,x,y)

                if(tile_img == coinImg):
                    x = (tile_size * col_count + (tile_size - tile_img.get_width())/2)
                    y = tile_size * row_count + (tile_size - tile_img.get_height())
                    coins.add(coin(coinImg, x, y))
                elif(tile_img == goombaImg):
                    x = (tile_size * col_count + (tile_size - tile_img.get_width())/2)
                    y = tile_size * row_count + (tile_size - tile_img.get_height())
                    goombas.add(goomba(goombaImg,x,y))
                elif(tile_img == plantImg):
                    x = (tile_size * col_count + (tile_size - tile_img.get_width())/2)
                    y = tile_size * row_count + (tile_size - tile_img.get_height())
                    plants.add(plant(plantImg,x,y))
                elif(tile_img != marioImg and tile_img):
                    x = tile_size * col_count + (tile_size - tile_img.get_width())/2
                    y = tile_size * row_count + (tile_size - tile_img.get_height())
                    tiles.add(block(tile_img,x,y))
                col_count += 1
            row_count += 1
    world_init()

    non_player_objects.extend(list(goombas))
    non_player_objects.extend(list(plants))
    non_player_objects.extend(list(tiles))

    def show_lives(lives):
        lives_text = font_30.render("Lives: " + str(lives), True, 'Black', 'White')
        screen.blit(lives_text, (10, 40))

    while True:
        screen.blit(bg,(0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                worlds_menu.worlds_menu(user)
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if e_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    worlds_menu.worlds_menu(user)
                    sys.exit()
                elif b_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    worlds_menu.worlds_menu(user)
                    sys.exit()
                elif t_rect.collidepoint(mouse_pos) and not(gameRunning):
                    pygame.quit()
                    world_load(user, user_world)
            
        for tile in tiles:
            screen.blit(tile.img,(tile.rect.x + offset ,tile.rect.y))
        for coin in coins:
            screen.blit(coin.img, (coin.x + offset, coin.y))

        pygame.draw.rect(screen,'grey',e_rect.inflate(5,5),border_radius = 8)        
        screen.blit(text_surface_1,e_rect)       

        mario.update()            
        for goomba in goombas:
            goomba.update()
        for plant in plants:
            plant.update()
        for fireball in fireballs:
            fireball.update()
        if(gameRunning):            
            time = pygame.time.get_ticks()//1000
        show_time(time)
        show_score(score)
        show_lives(mario.lives)

        if not(gameRunning):
            if(mario.lives <= 0):
                game_over()
            else:
                level_finished()

        pygame.display.update()
        clock.tick(50)