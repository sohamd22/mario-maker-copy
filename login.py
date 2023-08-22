import os, pickle
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from mysql import connector as sql
import worlds_menu

mycon = sql.connect(host='localhost', user='root', password='password', database='mario')
if mycon.is_connected():
    print('Success')
cursor = mycon.cursor()

logged_in = False
current_user = None

win = Tk()

win.geometry('300x400')
win.configure(bg = '#FED420')
win.title('Main Window')

def login(username, password):
    global current_user, logged_in

    cursor.execute('select username from users')
    usernames = cursor.fetchall()
    for i in range(len(usernames)):
        usernames[i] = usernames[i][0]

    cursor.execute('select password from users')
    passwords = cursor.fetchall()
    for i in range(len(passwords)):
        passwords[i] = passwords[i][0]

    username = username.lower()
    
    if(username in usernames):
        cursor.execute(f"select password from users where username='{username}'")
        user_password = cursor.fetchone()[0]
        if(password == user_password):
            if username != 'admin':
                l_button_click()
                on_click()                
            else:
                l_button_click()
                admin_win()
                messagebox.showinfo('Popup','You have logged in as the administrator.')
                return

            logged_in = True
            messagebox.showinfo('Popup','You have successfully logged in!') 
            current_user = username
            worlds_menu.worlds_menu(current_user)                                            
        else:
            messagebox.showinfo('Popup','Incorrect password.')
    else:
        messagebox.showinfo('Popup','This user does not exist!')  

def admin_win():
    admin_w = Toplevel(win)
    admin_w = Tk()
    admin_w.title('Administrator window')

    c1_width = 15
    c2_width = 17
    c3_width = 17
    c4_width = 16

    cursor.execute('select * from users')
    rows = cursor.fetchall()

    admin_w.geometry(f'810x{29*(len(rows)+1)}')

    entry1 = Entry(admin_w,font = 'courier 15 bold', width= c1_width, border = 2, justify = 'center')
    entry2 = Entry(admin_w,font = 'courier 15 bold', width= c2_width, border = 2, justify = 'center')
    entry3 = Entry(admin_w,font = 'courier 15 bold', width= c3_width, border = 2, justify = 'center')
    entry4 = Entry(admin_w,font = 'courier 15 bold', width= c4_width, border = 2, justify = 'center')
    lst = [entry1,entry2,entry3, entry4]
    txt = ['User Id','Username','Password','No. of Worlds']
    for i,j in enumerate(lst):
        j.insert(0 ,txt[i])

    entry1.grid(row = 0,column= 0)
    entry2.grid(row = 0,column= 1)
    entry3.grid(row = 0,column= 2)
    entry4.grid(row = 0,column= 3)

    entry1.configure(state = 'disabled')
    entry2.configure(state = 'disabled')
    entry3.configure(state = 'disabled')
    entry4.configure(state = 'disabled')
    
    for num,record in enumerate(rows):
        e1 = Entry(admin_w,font = 'courier 15', width= c1_width, border = 2, justify = 'center')
        e2 = Entry(admin_w,font = 'courier 15', width= c2_width, border = 2, justify = 'center')
        e3 = Entry(admin_w,font = 'courier 15', width= c3_width, border = 2, justify = 'center')
        e4 = Entry(admin_w,font = 'courier 15', width= c4_width, border = 2, justify = 'center')

        e1.insert(0, record[0])        
        e2.insert(0, record[1])
        e3.insert(0, record[2])
        e4.insert(0, len(record[3].split(',')))

        e1.configure(state = 'disabled')
        e2.configure(state = 'disabled')
        e3.configure(state = 'disabled')
        e4.configure(state = 'disabled')

        e1.grid(row = num+1,column= 0)
        e2.grid(row = num+1,column= 1)
        e3.grid(row = num+1,column= 2)
        e4.grid(row = num+1,column= 3)

def signup(username, password):
    cursor.execute('select username from users')
    usernames = cursor.fetchall()
    for i in range(len(usernames)):
        usernames[i] = usernames[i][0]

    cursor.execute('select uid from users')
    ids = cursor.fetchall()
    for i in range(len(ids)):
        ids[i] = ids[i][0]
    if(len(ids) == 0):
        prev = 0
    else:
        prev = max(ids)

    username = username.lower()

    if(username not in usernames):
        cursor.execute(f"insert into users values ({prev + 1}, '{username}', '{password}', '')")
        cursor.execute(f"insert into user_stats values ({prev + 1}, '{username}', '{username}stats.bin')")
        with open(f"statistics/{username}stats.bin", 'wb') as stats_file:
            stats_file.seek(0)
            pickle.dump({}, stats_file)
        mycon.commit()
        s_button_click()
        messagebox.showinfo('Popup','User created!')        
    else:
        messagebox.showinfo('Popup','User already exits!')

def guest_command():
    on_click()
    current_user = 'guest'
    worlds_menu.worlds_menu('guest')

def delete(username, password):
    cursor.execute('select username from users')
    usernames = cursor.fetchall()
    for i in range(len(usernames)):
        usernames[i] = usernames[i][0]

    cursor.execute('select password from users')
    passwords = cursor.fetchall()
    for i in range(len(passwords)):
        passwords[i] = passwords[i][0]

    username = username.lower()
    
    if(username == 'guest' or username == 'admin'):
        messagebox.showinfo('Popup','Cannot delete that user.')
        return

    if(username in usernames):
        cursor.execute(f"select password from users where username='{username}'")
        user_password = cursor.fetchone()[0]
        if(password == user_password):
            cursor.execute(f"select worlds from users where username='{username}'")
            user_worlds = cursor.fetchone()[0]
            if(user_worlds):
                for world in user_worlds.split(','):
                    os.remove(f"worlds/{world}")
            os.remove(f"statistics/{username}stats.bin")
            cursor.execute(f"delete from user_stats where username='{username}'")
            cursor.execute(f"delete from users where username='{username}'")
            mycon.commit()
            d_button_click()
            messagebox.showinfo('Popup','User was deleted successfully.') 
        else:
            messagebox.showinfo('Popup','Incorrect password.') 
    else:
        messagebox.showinfo('Popup','This user does not exist!') 

def on_click():
    win.destroy()    

def login_win():
    global l_button_click

    l_win = Toplevel(win)
    l_win.geometry('300x400')
    l_win.title('Login')
    l_win.configure(bg = '#FED420')

    def l_button_click():
        l_win.destroy()

    l_label = Label(l_win,text = 'Enter login credentials',font = 'helvatica 20', bg = '#FED420',padx = 15,pady = 20)
    u_label = Label(l_win,text = 'Username',font = 'helvatica 12', bg = '#FED420',padx = 15,pady = 10)
    entry_username = Entry(l_win, width = 25, font = 'helvatica 12', border = 5, justify= 'center')
    p_label = Label(l_win,text = 'Password',font = 'helvatica 12', bg = '#FED420',padx = 15,pady = 10)
    entry_password = Entry(l_win, width = 25, font = 'helvatica 12', border = 5, justify= 'center',show = '*')
    e_label = Label(l_win,text = '',font = 'helvatica 12', bg = '#FED420',padx = 15,pady = 10)
    button_login = Button(l_win, text = 'Login',font = 'helvatica 10', fg='white', bg = 'black',padx = 65, pady = 5, command = lambda: login(entry_username.get(),entry_password.get()))
    l_button_exit = Button(l_win, text = 'Back',font = 'helvatica 10', fg='white', bg = 'black',padx = 65, pady = 5, command = l_button_click)

    l_label.pack()
    u_label.pack()
    entry_username.pack()
    p_label.pack()
    entry_password.pack()
    e_label.pack()
    button_login.pack()
    l_button_exit.pack()

def signup_win():
    global s_button_click

    s_win = Toplevel(win)
    s_win.geometry('300x400')
    s_win.title('Signup')
    s_win.configure(bg = '#FED420')

    def s_button_click():
        s_win.destroy()

    s_label = Label(s_win,text = 'Enter signup credentials',font = 'helvatica 20', bg = '#FED420',padx = 3,pady = 20)
    u_label = Label(s_win,text = 'Username',font = 'helvatica 12', bg = '#FED420',padx = 15,pady = 10)
    entry_username = Entry(s_win, width = 25, font = 'helvatica 12', border = 5, justify= 'center')
    p_label = Label(s_win,text = 'Password',font = 'helvatica 12', bg = '#FED420',padx = 15,pady = 10)
    entry_password = Entry(s_win, width = 25, font = 'helvatica 12', border = 5, justify= 'center', show = '*')
    e_label = Label(s_win,text = '',font = 'helvatica 12', bg = '#FED420',padx = 15,pady = 10)
    button_signup = Button(s_win, text = 'Signup',font = 'helvatica 10', fg='white', bg = 'black',padx = 65, pady = 5, command = lambda: signup(entry_username.get(),entry_password.get()))
    s_button_exit = Button(s_win, text = 'Back',font = 'helvatica 10', fg='white', bg = 'black',padx = 65, pady = 5, command = s_button_click)
    s_label.pack()
    u_label.pack()
    entry_username.pack()
    p_label.pack()
    entry_password.pack()
    e_label.pack()
    button_signup.pack()
    s_button_exit.pack()

def delete_win():
    global d_button_click

    d_win = Toplevel(win)
    d_win.geometry('300x400')
    d_win.title('Delete User')

    d_win.configure(bg = '#FED420')

    def d_button_click():
        d_win.destroy()

    d_label = Label(d_win,text = 'Enter user credentials',font = 'helvatica 20', bg = '#FED420',padx = 15,pady = 20)
    u_label = Label(d_win,text = 'Username',font = 'helvatica 12', bg = '#FED420',padx = 15,pady = 10)
    entry_username = Entry(d_win, width = 25, font = 'helvatica 12', border = 5, justify= 'center')
    p_label = Label(d_win,text = 'Password',font = 'helvatica 12', bg = '#FED420',padx = 15,pady = 10)
    entry_password = Entry(d_win, width = 25, font = 'helvatica 12', border = 5, justify= 'center', show = '*')
    e_label = Label(d_win,text = '',font = 'helvatica 12', bg = '#FED420',padx = 15,pady = 10)
    button_delete = Button(d_win, text = 'Delete User',font = 'helvatica 10', fg='white', bg = 'black',padx = 65, pady = 5, command = lambda: delete(entry_username.get(),entry_password.get()))
    d_button_exit = Button(d_win, text = 'Back',font = 'helvatica 10', fg='white', bg = 'black',padx = 65, pady = 5, command = d_button_click)

    d_label.pack()
    u_label.pack()
    entry_username.pack()
    p_label.pack()
    entry_password.pack()
    e_label.pack()
    button_delete.pack()
    d_button_exit.pack()

def how_to_play():
    t_win = Toplevel(win)
    t_win.geometry('600x380')
    t_win.configure(bg = 'black')

    with open('how-to-start.txt','r') as f:
        t = f.read()
    
    e_l = Label(t_win,text = '',font = 'courier 10',fg = 'white',bg = 'black')
    Label_1 = Label(t_win,text = t,font = 'courier 10',fg = 'white',bg = 'black')
    e_l.pack()
    Label_1.pack()

label_1 = Label(win,text = 'Pyrio',font = 'courier 40', bg = '#FED420',fg = 'black',padx = 70,pady = 20)

button_login = Button(win, text = 'Login',font = 'helvatica 10', bg = 'black',fg = '#FED420',padx = 70, pady = 5, command = login_win)
button_signup = Button(win, text = 'Sign Up',font = 'helvatica 10', bg = 'black',fg = '#FED420',padx = 65, pady = 5, command = signup_win)
button_guest = Button(win, text = 'Play As Guest',font = 'helvatica 10', bg = 'black',fg = 'white',padx = 70, pady = 5, command = guest_command)
button_delete_user = Button(win, text = 'Delete User',font = 'helvatica 10', bg = 'black',fg = 'white',padx = 65, pady = 5, command = delete_win)
button_exit = Button(win, text = 'Exit',font = 'helvatica 10', bg = 'black',fg = 'white',padx = 65, pady = 5, command = on_click)
q_button = Button(win, text = 'How To Play',font = 'helvatica 10', bg = 'black',fg = 'white',padx = 5, pady = 5, command = how_to_play)

label_1.pack()
button_login.pack()
button_signup.pack()
button_guest.pack()
button_delete_user.pack()

separator = ttk.Separator(win, orient='horizontal')
separator.pack(pady=10, fill='x')

q_button.pack()
button_exit.pack()

win.mainloop()