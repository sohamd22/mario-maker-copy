import os, pickle
from tkinter import *
from tkinter import ttk
from mysql import connector as sql
import world_generation, world_load

mycon = sql.connect(host='localhost', user='root', password='password', database='mario')
if mycon.is_connected():
    print('Success')
cursor = mycon.cursor()

def get_user_worlds(user):
    mycon.commit()
    cursor.execute(f"select worlds from users where username='{user}'")
    user_worlds = cursor.fetchone()[0]
    if(user_worlds):
        return user_worlds.split(',')
    return []

def world_generation_command(user, root, world=''):
    root.destroy()
    world_generation.world_generation(user, world)

def delete_world(user, root, world):
    root.destroy()
    mycon.commit()
    cursor.execute(f"select worlds from users where username='{user}'")
    user_worlds = cursor.fetchone()[0].split(',')
    user_worlds.remove(world)
    user_worlds = ','.join(user_worlds)
    cursor.execute(f"update users set worlds='{user_worlds}' where username='{user}'")
    mycon.commit()
    os.chdir('./worlds')
    os.remove(world)
    os.chdir('../')
    stats = {}
    with open(f"statistics/{user}stats.bin", 'rb') as fs:
        fs.seek(0)
        stats = pickle.load(fs)
        stats.pop(world, None)
    with open(f"statistics/{user}stats.bin", 'wb') as fs:
        fs.seek(0)
        pickle.dump(stats, fs)
    worlds_menu(user)

def play_world(user, root, world):
    root.destroy()
    world_load.world_load(user, world)

def logout_command(root):
    root.destroy()  
    os.system('python -m login.py')      

def how_to_play(root):
    t_win = Toplevel(root)
    t_win.geometry('600x450')
    t_win.configure(bg = 'black')

    with open('how-to-play.txt','r') as f:
        t = f.read()
    
    e_l = Label(t_win,text = '',font = 'courier 10',fg = 'white',bg = 'black')
    Label_1 = Label(t_win,text = t,font = 'courier 10',fg = 'white',bg = 'black')
    e_l.pack()
    Label_1.pack()

def worlds_menu(user):
    root = Tk()
    root.geometry('330x400')
    root.title('Worlds')
    root.lift()
    root.attributes("-topmost", True)

    root.configure(bg = '#FED420')

    label_1 = Label(root,text = f"{user.title()}'s Worlds",font = 'helvatica 30', fg="white", bg = '#e7bc01',padx = 30)

    label_1.grid(row = 0,column = 0,columnspan = 3)

    user_worlds = get_user_worlds(user)

    cur_row = 1
    for i in user_worlds:
        world_num = i[i.rfind('world')+5:i.rfind('.bin')]

        with open(f"statistics/{user}stats.bin", 'rb') as fs:
            fs.seek(0)
            stats = pickle.load(fs)
            world_stats = stats[i]

            best_time = world_stats[0]
            if(best_time == None):
                best_time='N/A'
            else:
                best_minutes = best_time//60
                best_seconds = best_time%60
                best_time = f"{best_minutes}m {best_seconds}s"
                
            highscore = world_stats[1]
            if(highscore == None):
                highscore='N/A'               

        label_w = Label(root,text = f"World {world_num}",font = 'helvatica 10',bg = '#FED420')
        label_s = Label(root,text = f"Highscore: {highscore} | Best Time: {best_time}",font = 'helvatica 10',bg = '#FFE369', pady = 10, padx=30)
        button_p = Button(root,text = 'Play',font = 'helvatica 10',padx = 20, bg="black", fg="white", command=lambda world=i: play_world(user, root, world))
        
        if(i != 'guestworld1.bin'):
            button_u = Button(root,text = 'Update',font = 'helvatica 10',padx = 20,bg="black", fg="white",  command=lambda world=i: world_generation_command(user, root, world))
            button_d = Button(root,text = 'Delete',font = 'helvatica 10',padx = 20,bg="black", fg="white",  command=lambda world=i: delete_world(user, root, world))

        label_w.grid(row = cur_row,column = 0)
        label_s.grid(row = cur_row+1,column = 0, columnspan=3)
        button_p.grid(row = cur_row+2,column = 0)
        
        if(i != 'guestworld1.bin'):
            button_u.grid(row = cur_row+2,column = 1)
            button_d.grid(row = cur_row+2,column = 2)

        separator = ttk.Separator(root, orient='horizontal')
        separator.grid(row = cur_row+3, column=0, columnspan = 3, sticky="ew", pady=10)
        cur_row += 4

    separator = ttk.Separator(root, orient='horizontal')
    separator.grid(row = cur_row, column=0, columnspan = 3, sticky="ew", pady=5)
    cur_row += 1

    button_exit = Button(root,text = 'Exit',bg="black", fg="white", font = 'helvatica 10',padx = 20, command=root.destroy)
    button_logout = Button(root,text = 'Logout',bg="black", fg="white", font = 'helvatica 10',padx = 20, command=lambda: logout_command(root))
    button_wg = Button(root,text = 'New World',bg="black", fg="white", font = 'helvatica 10',padx = 20, command=lambda: world_generation_command(user, root))
    button_q = Button(root, text = 'How To Play',font = 'helvatica 10',padx = 5, pady = 5, bg="black", fg="white", command =lambda: how_to_play(root))

    button_exit.grid(row = cur_row,column = 0)
    button_logout.grid(row = cur_row,column = 1)
    button_wg.grid(row = cur_row,column = 2)
    button_q.grid(row = cur_row + 1, column = 1, pady = 10)

    root.mainloop()
    mycon.close()
