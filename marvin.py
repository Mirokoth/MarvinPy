import discord
import asyncio
import re
import sqlite3
from datetime import datetime
from modules.random_str import *

client = discord.Client()
conn = sqlite3.connect('URL.db')
c = conn.cursor()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.author.id != client.user.id:
        if message.content.startswith('!die') and str(message.author).split("#")[0] == "Mirokoth":
            c.close()
            conn.close()
            exit()

        match = re.search("(?i)\\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", message.content)
        if match:
            c.execute('SELECT * FROM URLS WHERE url=(?) AND server=(?)', (match.group(1),str(str(message.server)),))
            data = c.fetchone()
            if data:
                update_post_count(str(message.server), match.group(1), str(message.author), "URLS")
                c.execute('SELECT * FROM URLS WHERE url=(?) AND server=(?)', (match.group(1),str(message.server),))
                new_data = c.fetchone()
                c.execute('SELECT * FROM user_count WHERE poster = (?) AND server=(?)', (str(message.author),str(message.server),))
                new_user_data = c.fetchone()
                em = discord.Embed(title=random_string(), description='You have reposted {} times now.'.format(new_user_data[2]), colour=0x282B30)
                em.set_author(name=str(message.author).split("#")[0], icon_url=message.author.avatar_url)
                em.add_field(name="{}".format(new_data[3]), value="Has been reposted {} time(s).".format(new_data[4]), inline=True)
                await client.send_message(message.channel, embed=em)
            else:
                insert_table(str(message.server), str(message.timestamp), str(message.author), match.group(1), 1)

        if len(message.attachments) > 0:
            file_details = message.attachments[0]
            c.execute('SELECT * FROM file_count WHERE server=(?) AND size=(?) AND height=(?) AND width=(?)',
                        (str(message.server), file_details['size'], file_details['height'], file_details['width'],))
            data = c.fetchone()
            if data:
                c.execute('SELECT * FROM file_count WHERE server=(?) AND size=(?) AND height=(?) AND width=(?)',
                            (str(message.server), file_details['size'], file_details['height'], file_details['width'],))
                new_data = c.fetchone()
                update_post_count(str(message.server), [file_details['size'], file_details['height'], file_details['width']], str(message.author), "file_count")
                c.execute('SELECT * FROM user_count WHERE poster = (?) AND server=(?)', (str(message.author),str(message.server),))
                new_user_data = c.fetchone()
                em = discord.Embed(title=random_string(), description='You have reposted {} times now.'.format(new_user_data[2]), colour=0x282B30)
                em.set_author(name=str(message.author).split("#")[0], icon_url=message.author.avatar_url)
                em.add_field(name="That image", value="has been reposted {} time(s).".format(new_data[2]), inline=True)
                await client.send_message(message.channel, embed=em)

            else:
                create_file(str(message.server), str(message.author), 1, file_details['size'], file_details['height'], file_details['width'],)



        if message.content.startswith("!server"):
            await client.send_message(message.channel, str(message.server))

def update_post_count(server, data, user, database):
    c.execute('SELECT * FROM user_count WHERE poster=(?) AND server=(?)', (user, server,))
    user_dat = c.fetchone()
    if not user_dat:
        print("")
        create_user(server, user)
    if database == "URLS":
        c.execute('SELECT * FROM URLS WHERE url=(?) AND server=(?)', (data, server,))
        data_url = c.fetchone()
        count = data_url[4] + 1
        c.execute('UPDATE URLS SET post_count = (?) WHERE url = (?) AND server=(?)', (count, data, server,))
    if database == "file_count":
        c.execute('SELECT * FROM file_count WHERE server=(?) AND size=(?) AND height=(?) AND width=(?)',
                    (server, data[0], data[1], data[2],))
        data_file = c.fetchone()
        count = data_file[2] + 1
        c.execute('UPDATE file_count SET post_count = (?) WHERE server=(?) AND size=(?) AND height=(?) AND width=(?)',
                    (count, server, data[0], data[1], data[2],))
    c.execute('SELECT * FROM user_count WHERE poster=(?) AND server=(?)', (user, server,))
    data_user = c.fetchone()
    count_two = data_user[2] + 1
    c.execute('UPDATE user_count set post_count = (?) WHERE poster = (?) AND server=(?)', (count_two, user, server,))
    conn.commit()

def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS URLS(server TEXT, date_entered TEXT, poster TEXT, url TEXT, post_count INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS user_count(server TEXT, poster TEXT, post_count INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS file_count(server TEXT, poster TEXT, post_count INTEGER, size INTEGER, height INTEGER, width INTEGER)')

def insert_table(server, cur_date, user, url, count):
    c.execute('INSERT INTO URLS (server, date_entered, poster, url, post_count) VALUES (?, ?, ?, ?, ?)',
                (server, cur_date, user, url, count))
    conn.commit()

def create_user(server, user):
    c.execute('INSERT INTO user_count (server, poster, post_count) VALUES (?, ?, ?)', (server, user, 0))
    conn.commit()

def create_file(server, poster, post_count, size, height, width):
    c.execute('INSERT INTO file_count (server, poster, post_count, size, height, width) VALUES (?, ?, ?, ?, ?, ?)',
                (server, poster, post_count, size, height, width,))
    conn.commit()

def read_from_db():
    c.execute('SELECT * FROM URLS')
    data = c.fetchall()
    print("Keeping track of {} URL's for reposts".format(len(data)))

create_table()
read_from_db()
client.accept_invite("https://discord.gg/5wjr9")
client.run('DISCORD API KEY')
