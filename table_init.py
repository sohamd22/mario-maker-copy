import mysql.connector as sql

mycon = sql.connect(host='localhost', user='root', password='password')
if mycon.is_connected():
    print('Success')
cursor = mycon.cursor()

cursor.execute('create database mario')
cursor.execute('use mario')

cursor.execute('''create table users(
UID INT PRIMARY KEY,
Username VARCHAR(20) UNIQUE,
Password VARCHAR(20),
Worlds VARCHAR(10000));''')

cursor.execute('''create table user_stats(
SID INT PRIMARY KEY,
Username VARCHAR(20) UNIQUE,
Stats VARCHAR(30),
FOREIGN KEY (Username) REFERENCES users(Username)
);''')

cursor.execute("insert into users values(1, 'guest', '', 'guestworld1.bin')")
cursor.execute("insert into user_stats values(1, 'guest', 'gueststats.bin')")
cursor.execute("insert into users values(0, 'admin', 'password', '')")

mycon.commit()
mycon.close()

