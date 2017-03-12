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
            c.execute('SELECT * FROM URLS WHERE url=(?)', (match.group(1),))
            data = c.fetchone()
            if data:
                update_post_count(match.group(1), str(message.author))
                c.execute('SELECT * FROM URLS WHERE url=(?)', (match.group(1),))
                new_data = c.fetchone()
                c.execute('SELECT * FROM user_count WHERE poster = (?)', (str(message.author),))
                new_user_data = c.fetchone()
                em = discord.Embed(title=random_string(), description='You have reposted {} times now.'.format(new_user_data[1]), colour=0x282B30)
                em.set_author(name=str(message.author).split("#")[0], icon_url=message.author.avatar_url)
                em.add_field(name="{}".format(new_data[2]), value="Has been reposted {} times.".format(new_data[3]), inline=True)
                await client.send_message(message.channel, embed=em)
            else:
                insert_table(str(message.timestamp), str(message.author), match.group(1), 1)


def update_post_count(url, user):
    c.execute('SELECT * FROM user_count WHERE poster=(?)', (user,))
    user_dat = c.fetchone()
    if not user_dat:
        print("no user")
        create_user(user)
    c.execute('SELECT * FROM URLS WHERE url= (?)', (url,))
    data_url = c.fetchone()
    count = data_url[3] + 1
    c.execute('UPDATE URLS SET post_count = (?) WHERE url = (?)', (count, url,))
    c.execute('SELECT * FROM user_count WHERE poster=(?)', (user,))
    data_user = c.fetchone()
    count_two = data_user[1] + 1
    c.execute('UPDATE user_count set post_count = (?) WHERE poster = (?)', (count_two, user,))
    conn.commit()

def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS URLS(date_entered TEXT, poster TEXT, url TEXT, post_count INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS user_count(poster TEXT, post_count INTEGER)')

def insert_table(cur_date, user, url, count):
    c.execute('INSERT INTO URLS (date_entered, poster, url, post_count) VALUES (?, ?, ?, ?)',
                (cur_date, user, url, count))
    conn.commit()

def create_user(user):
    c.execute('INSERT INTO user_count (poster, post_count) VALUES (?, ?)', (user, 0))
    conn.commit()

def read_from_db():
    c.execute('SELECT * FROM URLS')
    data = c.fetchall()
    print("Keeping track of {} URL's for reposts".format(len(data)))

create_table()
read_from_db()
client.accept_invite("https://discord.gg/5wjr9")
client.run('I REMEMBERED TO REMOVE THE API KEY THIS TIME')
