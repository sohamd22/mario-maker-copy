import pygame, sys, math, pickle, os
from mysql import connector as sql
import worlds_menu

mycon = sql.connect(host='localhost', user='root', password='password', database='mario')
if mycon.is_connected():
    print('Success')
cursor = mycon.cursor()

def world_generation(user, user_world=''):
    pygame.init()
    screen = pygame.display.set_mode((640,670))
    clock = pygame.time.Clock()
    bg = pygame.transform.scale(pygame.image.load('images/sky.jpg'), (640,640))
    font_100 = pygame.font.Font(None,100)
    font_40 = pygame.font.Font(None,40)
    font_30 = pygame.font.Font(None,30)

    active_world = 1

    tile_size = 64
    def initialize_world():
        global world1, world2, active_world, worlds
        active_world = 1

        if(not(user_world)):
            world1 = [[0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,-1,0,0,0,0,0,0,0,0],
            [1,1,1,1,1,1,1,1,1,1]
            ]

            world2 = [[0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [1,1,1,1,1,1,1,1,1,1]
            ]
        else:
            with open(f"./worlds/{user_world}", 'rb') as uw:
                world = pickle.load(uw)
            world1 = []
            world2 = []
            for row in world:
                world1.append(row[:10])
                world2.append(row[10:])

        worlds = [None,world1,world2]
    initialize_world()

    def reset_world():
        global world1, world2, active_world, worlds
        active_world = 1

        world1 = [[0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,-1,0,0,0,0,0,0,0,0],
        [1,1,1,1,1,1,1,1,1,1]
        ]

        world2 = [[0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [1,1,1,1,1,1,1,1,1,1]
        ]

        worlds = [None,world1,world2]

    def world_init(world_num):
        world = worlds[world_num]
        tiles = []
        row_count = 0
        for row in world:
            col_count = 0
            for num in row:
                if(num != -1):
                    tile_img = imgs[num]                
                else:
                    global mario
                    tile_img = marioImg
                    tile_rect = tile_img.get_rect()
                    tile_rect.x = tile_size * col_count + (tile_size - tile_img.get_width())/2
                    tile_rect.y = tile_size * row_count + (tile_size - tile_img.get_height())
                    
                    tile = (tile_img, tile_rect)
                    mario = tile
                    tiles.append(tile)
                
                if(tile_img != marioImg and tile_img):
                    tile_rect = tile_img.get_rect()
                    tile_rect.x = tile_size * col_count + (tile_size - tile_img.get_width())/2
                    tile_rect.y = tile_size * row_count + (tile_size - tile_img.get_height())
                    tile = (tile_img, tile_rect)
                    tiles.append(tile)
                col_count += 1
            row_count += 1
        return tiles

    grassImg = pygame.transform.scale(pygame.image.load('images/grass.png'), (64, 64))
    tileImg = pygame.transform.scale(pygame.image.load('images/tile.png'), (64, 64))
    plantImg = pygame.transform.scale(pygame.image.load('images/plant_enemy.png'), (60, 60))
    marioImg = pygame.transform.scale(pygame.image.load('images/mario.png'), (60, 60))
    heartImg = pygame.transform.scale(pygame.image.load('images/heart.png'), (48, 48))
    flagImg = pygame.transform.scale(pygame.image.load('images/flag.png'), (48, (48)*2))
    goombaImg = pygame.transform.scale(pygame.image.load('images/goomba.png'), (56, 56))
    coinImg = pygame.transform.scale(pygame.image.load('images/coin.png'), (32, 32))
    imgs = [None, grassImg, tileImg, flagImg, coinImg, goombaImg, plantImg, heartImg]

    text_surface_1 = font_100.render('1', True, 'Black')
    text_surface_2 = font_100.render('2', True, 'Black')
    text_surface_3 = font_40.render('...World Saved...', True, 'Black', 'White')
    text_surface_4 = font_30.render('Save world',True,'Black')
    text_surface_5 = font_30.render('<',True,'Black')
    text_surface_6 = font_30.render('>',True,'Black')
    text_surface_7 = font_30.render('Reset',True,'Black')
    text_surface_8 = font_30.render('Exit',True,'Black')

    text_rect = text_surface_1.get_rect(center = (50,50))
    save_world_rect = text_surface_4.get_rect(topleft = (10,645))
    move_left = text_surface_5.get_rect(topleft = (140,645))
    move_right = text_surface_6.get_rect(topleft = (170,645))
    reset_text = text_surface_7.get_rect(topleft = (205,645))
    save_text_rect = text_surface_3.get_rect(center = (320,320))
    exit_rect = text_surface_8.get_rect(topleft = (595,645))
    text_surfaces = [text_surface_1,text_surface_2]

    def on_mouse_click():
        mouse_presses = pygame.mouse.get_pressed()
        if active_world == 1:
            if mouse_presses[0]:
                x,y = pygame.mouse.get_pos()
                
                row = math.floor(y/tile_size)
                col = math.floor(x/tile_size)
                if row == 8 and col == 1:
                    pass
                elif world1[row][col] == len(imgs)-1:
                    world1[row][col] = 0
                else:
                    world1[row][col] += 1
        if active_world == 2:
            if mouse_presses[0]:
                x,y = pygame.mouse.get_pos()
                row = math.floor(y/tile_size)
                col = math.floor(x/tile_size)
                if row == 8:
                    pass
                if world2[row][col] == len(imgs)-1:
                    world2[row][col] = 0
                else:
                    world2[row][col] += 1
                        
    display_save = False
    save_tick = 0

    os.chdir('./worlds')
    if(user_world):
        newfile=user_world
    else:
        last_world_num = 0
        for i in os.listdir():
            if i.startswith(user+'world'):
                world_num = i[i.rfind('world')+5:i.rfind('.bin')]
                if(int(world_num) > last_world_num):
                    last_world_num = int(world_num)
        newfile = f"{user}world{int(last_world_num)+1}.bin"
    os.chdir('../')

    def save_world():
        print('done')
        world = []
        for row in range(10):
            row_data = []
            row_data.extend(world1[row])
            row_data.extend(world2[row])
            world.append(row_data)

        cursor.execute(f"select worlds from users where username='{user}'")
        worlds = cursor.fetchone()[0]
        if(worlds):
            worlds += ','
        if(newfile not in worlds.split(',')):
            cursor.execute(f"update users set worlds='{worlds + newfile}' where username='{user}'")
            mycon.commit()
        
        os.chdir('./worlds')
        with open(newfile, 'wb') as fw:
            pickle.dump(world,fw)
        os.chdir('../')
        stats = {}
        with open(f"statistics/{user}stats.bin", 'rb') as fs:
            fs.seek(0)
            stats = pickle.load(fs)
            stats[newfile] = [None, None]
        with open(f"statistics/{user}stats.bin", 'wb') as fs:
            fs.seek(0)
            pickle.dump(stats, fs)

    while True:
        screen.blit(bg, (0,0))

        if active_world == 1:
            color_move_left = 'red'
            color_move_right = 'green'
        else:
            color_move_left = 'green'
            color_move_right = 'red'
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                worlds_menu.worlds_menu(user)
                sys.exit()
                             
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] < 640 and mouse_pos[1] < 640:
                    on_mouse_click()
                elif save_world_rect.collidepoint(mouse_pos):
                    display_save = True
                    save_world()
                elif move_left.collidepoint(mouse_pos) and color_move_left == 'green':
                    if active_world == 1:
                        active_world = 2
                    else:
                        active_world = 1
                elif move_right.collidepoint(mouse_pos) and color_move_right == 'green':
                    if active_world == 1:
                        active_world = 2
                    else:
                        active_world = 1
                elif reset_text.collidepoint(mouse_pos):
                    reset_world()
                elif exit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    worlds_menu.worlds_menu(user)
                    sys.exit()

        for tile in world_init(active_world):
            screen.blit(tile[0], tile[1])

        pygame.draw.rect(screen,'White',text_rect,border_radius = 10)
        screen.blit(text_surfaces[active_world-1],text_rect)
        pygame.draw.rect(screen,'grey',save_world_rect.inflate(5,5),border_radius = 8)
        pygame.draw.rect(screen,color_move_left,move_left.inflate(5,5),border_radius = 8)
        pygame.draw.rect(screen,color_move_right,move_right.inflate(5,4),border_radius = 8)
        pygame.draw.rect(screen,'grey',reset_text.inflate(5,5),border_radius = 8)
        pygame.draw.rect(screen,'grey',exit_rect.inflate(5,5),border_radius = 8)
        screen.blit(text_surface_4,save_world_rect)
        screen.blit(text_surface_5,move_left)
        screen.blit(text_surface_6,move_right)
        screen.blit(text_surface_7,reset_text)
        screen.blit(text_surface_8,exit_rect)
        
        if display_save:
            if save_tick <= 90:
                screen.blit(text_surface_3,save_text_rect)
                save_tick += 1
            else:
                save_tick = 0
                display_save = False

        pygame.display.update()
        clock.tick(60)
