import discord
import asyncio
import re
import sqlite3
import requests
import json
from datetime import datetime
from datetime import timedelta
from pytz import timezone
from bs4 import BeautifulSoup, UnicodeDammit
import random
import urllib


from modules.random_str import *



client = discord.Client()
conn = sqlite3.connect('URL.db')
c = conn.cursor()
poll_running = False
poll_yes = 0
poll_no = 0
poll_voters = []
proposed_new = {}
proposed_new_voters = []
global proposal
proposal = False

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name='$HELP for commands'))


@client.event
async def on_message(message):
    try:
        if message.content[0] == "$":
            Command = True
        else:
            Command = False
    except:
        pass
        Command = False
    # REGEX Match to determine if post is URL.
    regex_pattern = "(?i)\\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    match = re.search(regex_pattern, message.content)
    if match and message.author.id != client.user.id and Command != True:
        c.execute('SELECT * FROM URLS WHERE url=(?) AND server=(?)', (match.group(1),str(str(message.server)),))
        data = c.fetchone()
        if data:
            c.execute('SELECT * FROM IGNORE WHERE URL=(?)',(match.group(1),))
            ignore = c.fetchone()
            if not ignore:
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


    if message.author.id != client.user.id:
        if message.content.startswith('$die') and str(message.author).split("#")[0] == "Mirokoth":
            c.close()
            conn.close()
            exit()


        if str(message.author).split("#")[0] == "Mee6":
            if random.randrange(0,30) <= 1:
                reply = ["Come on Mee6, stop showing off. I can do bot stuff too! Bleep Bloop", "Fuck up Mee6", "\"I'm Mr Mee6\" ...Fuck you Mee6!"]
                await client.send_message(message.channel, reply[random.randrange(0,3)])


        if "PIZZA" in str(message.content).upper() or "PINEAPPLE" in str(message.content).upper():
            if random.randrange(0,10) <= 1:
                await client.send_file(message.channel, 'Static/pineapple/{}.jpg'.format(random.randrange(0,6)))


        if message.content.startswith('$'):
            content = message.content.split('$')[1].upper()
            command = content.split(" ")[0]
            print(command)


            if "HELP" in command:
                message_out = "Marving Help:\n"
                message_out += "\n$RANK - See your current repost rank"
                message_out += "\n$RANK @<user> - Check another users rank"
                message_out += "\n$SCOREBOARD - Display high score for reposts"
                message_out += "\n$POLL <time> <question> - Time between 1 and 10 minutes. Question can current only be yes or no"
                message_out += "\n$NEW <proposed command> <URL for img or gif> - Propose new command be added to Marvin. Requires 3 approvals to go accepted."
                message_out += "\n$BURN - List of Australian burn centres"
                message_out += "\n$CAGE - Random image from the OneTrueGod sub-reddit"
                message_out += "\n$OZBARGAIN - List newest 10 OzBargain posts"
                message_out += "\n$OZALERT 'string' - Alert when a new OzBargain deal is posted matching your string"
                message_out += "\n$OZLIST - List your current OzBargain searches"
                message_out += "\n$OZREMOVE 'string' - Remove string from OzBargain Alerts"
                message_out += "\n\n$User added commands from $new:"
                c.execute('SELECT * FROM USER_SUBMITTED')
                new_data = c.fetchall()
                for command in new_data:
                    message_out += "\n${}".format(command[3])
                print(new_data)
                await client.send_message(message.author, "```{}```".format(message_out))


            if "RANK" in command:
                if "@" in content:
                    try:
                        user = await client.get_user_info((content.split("@")[1]).split(">")[0])
                        if len(content.split("@")[1]) > 1:
                            rank = top_score(message.server, user)
                    except:
                        await client.send_message(message.channel, "Robot error: user not found")
                else:
                    rank = top_score(message.server, message.author)
                    user = message.author
                if rank != False:
                    em = discord.Embed(title="You are ranked #{}!\n".format(rank[3]), description='   \n   \nKeep up the quality shitposts.', colour=0x282B30)
                    em.set_author(name=str(user).split("#")[0], icon_url=user.avatar_url)
                    await client.send_message(message.channel, embed=em)
                elif rank == False:
                    em = discord.Embed(title="Sorry buddy, you have not reposted yet...", description=' ', colour=0x282B30)
                    em.set_author(name=str(user).split("#")[0], icon_url=user.avatar_url)
                    await client.send_message(message.channel, embed=em)

            if "SCOREBOARD" in command:
                rank = top_score(message.server, False)
                sb_str = "   \n   \n"
                count = 1
                print("rank: {}".format(len(rank) - 1 ))
                if count != (len(rank) - 1) and count < 5:
                    for user in range(0, len(rank)):
                        print(count)
                        sb_str += "#{} - {} - With {} Reposts\n".format(count, rank[count - 1][1].split("#")[0],rank[count - 1][2])
                        count += 1

                em = discord.Embed(title="Repost Scoreboard:\n", description=sb_str, colour=0x282B30)
                #em.set_author(name=str(client.user).split("#")[0], icon_url=client.user.avatar_url)
                await client.send_message(message.channel, embed=em)

            if "BOTH" in command or "WHYNOTBOTH" in command:
                await client.send_file(message.channel, 'Static/whynotboth.jpg')

            if "MINT" in command:
                await client.send_file(message.channel, 'Static/fuckingmint.jpg')

            if "VN" in command or "VAPENAYSH" in command:
                await client.send_file(message.channel, 'Static/vn.png')

            if "BURN" in command:
                await client.send_message(message.channel, "https://en.wikipedia.org/wiki/List_of_burn_centres_in_Australia")

            if "GDQ" in command:
                with open('gdq.json') as data_file:
                    data = json.load(data_file)
                fmt_date = "%Y-%m-%d"
                fmt_time = "%H:%M:%S"
                tz = ['Canada/Central']
                now_time = datetime.now(timezone('Canada/Central'))
                print(now_time.strftime(fmt_date))
                cur_date = now_time.strftime(fmt_date)
                cur_time = now_time.strftime(fmt_time)
                found = False
                count = 0
                response = urllib.request.urlopen('http://twitch.tv/gamesdonequick')
                response = BeautifulSoup(response, 'lxml')
                http_resp = "Oops"
                for td in response.find_all('meta'):
                    if "Summer Games Done Quick 2017" in str(td):
                        http_resp = str(td).split('-')[1].split('" property="')[0]
                print(len(data['schedule']['items']))
                for item in data['schedule']['items']:
                    date = data['schedule']['items'][count]['scheduled'].split("T")[0]
                    time = data['schedule']['items'][count]['scheduled'].split("T")[1].split("-")[0]
                    if count + 1 != len(data['schedule']['items']):
                        date_next = data['schedule']['items'][count + 1]['scheduled'].split("T")[0]
                        time_next = data['schedule']['items'][count + 1]['scheduled'].split("T")[1].split("-")[0]
                        if date == cur_date:
                            if datetime.strptime(cur_date + " " + cur_time,"%Y-%m-%d %H:%M:%S") > datetime.strptime(date + " " + time,"%Y-%m-%d %H:%M:%S") \
                                and datetime.strptime(cur_date + " " + cur_time,"%Y-%m-%d %H:%M:%S") < datetime.strptime(date_next + " " + time_next,"%Y-%m-%d %H:%M:%S"):
                                output = "```Games Done Quick:\n\nShitty schedule response (fuck time zone math):\nCurrently playing: {}\nNext up: {}\n\nActually playing on Twitch.TV:\n{}```".format(data['schedule']['items'][count]['data'][0], data['schedule']['items'][count + 1]['data'][0], http_resp)
                                found = True
                                await client.send_message(message.channel, output)
                    count += 1
                if found == False:
                    await client.send_message(message.channel, "Games Done Quick:\n\nCurrently playing: {}")

            if "CAGE" in command or "CAGEME" in command or "ONETRUEGOD" in command:
                #if str(message.channel).upper() == "NSFW":
                nick_url = "https://www.reddit.com/r/onetruegod/hot.json"
                c.execute('SELECT * FROM REDDIT WHERE URL=(?)',[nick_url])
                data = c.fetchone()
                if data:
                    if data[1] <= datetime.today().strftime("%d/%m/%y/%H/%M"):
                        request = get_reddit_json(nick_url)
                        c.execute('UPDATE REDDIT SET LASTRUN = (?), JSON = (?) WHERE URL = (?)', (datetime.today(), request.text, nick_url,))
                        conn.commit()
                        json_data = request.text
                    else:
                        json_data = data[2]
                else:
                    request = get_reddit_json(nick_url)
                    future_date = (datetime.today() + timedelta(hours=12)).strftime("%d/%m/%y-%H:%M")
                    c.execute('INSERT INTO REDDIT (URL, LASTRUN, JSON) VALUES (?, ?, ?)',
                                (nick_url, future_date, request.text))
                    conn.commit()
                    json_data = request.text
                json_data = json.loads(json_data)
                cage_out = []
                for x in json_data['data']['children']:
                    ext = ['.jpg', 'gifv', '.gif', '.bmp']
                    if str(x['data']['url'])[-4:] in ext:
                        cage_out.append(str(x['data']['url']))
                await client.send_message(message.channel, "{}".format(cage_out[random.randint(0,len(cage_out)-1)]))

            if "OZBARGAIN" in command:
                c.execute('SELECT * FROM OZBARGAIN ORDER BY ID DESC LIMIT 10')
                data = c.fetchall()
                message_out = "```"
                count = 1
                for entry in data:
                    entry =  str(entry)
                    for ch in ["(",")","'"]:
                        if ch in entry:
                            entry = entry.replace(ch,"")
                    entry = entry.split(",")
                    message_out += "{} - {}\n{}\n\n".format(count,entry[1],entry[2])
                    count += 1
                message_out += "```"
                print(message_out)
                await client.send_message(message.author, message_out)

            if "OZALERT" in command:
                alert = content.split("OZALERT ")[1]
                c.execute('INSERT INTO OZALERT (ALERT, USER) VALUES (?, ?)',
                            (alert, str(message.author)))
                conn.commit()
                message_out = "You will be alerted when I find an ozbargain post with **{}** in it.".format(alert)
                message_out += "\nTo unsubscribe from this alert enter $OZREMOVE {}".format(alert)
                await client.send_message(message.channel, message_out)

            if "OZREMOVE" in command:
                alert = content.split("OZREMOVE ")[1]
                c.execute('DELETE FROM OZALERT WHERE ALERT=(?) AND USER=(?)',
                            (alert, str(message.author)))
                conn.commit()
                await client.send_message(message.author, "You will no longer receive updates for {}".format(alert))

            if "OZLIST" in command:
                c.execute('SELECT * FROM OZALERT WHERE USER=(?)', (str(message.author),))
                data = c.fetchall()
                message_out = ""
                for entry in data:
                    message_out += str(entry)
                if len(message_out) < 1:
                    await client.send_message(message.author, "Nothing in your list")
                else:
                    await client.send_message(message.author, message_out)

            if "IGNORE" in command:
                regex_pattern = "(?i)\\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                match = re.search(regex_pattern, message.content)
                ignore = content.split("IGNORE ")[1]
                c.execute('INSERT INTO IGNORE (URL, USER) VALUES (?, ?)',
                            (match.group(1), str(message.author)))
                conn.commit()
                await client.send_message(message.channel, "k.")


            if "POLL" in command:
                print(command)
                global poll_question
                global poll_timer
                global poll_message
                global poll_running
                if poll_running == True:
                    await client.send_message(message.channel, "A poll is currently running, please wait until completion before creating another one.")
                else:
                    if len(content.replace("POLL","")) <= 2:
                        await client.send_message(message.channel, "Please provide a valid question. $poll help might help ;)")
                    else:
                        poll_question = content.split("POLL ")[1]
                        if poll_question[0:] == "HELP":
                            await client.send_message(message.channel, "```$POLL <time> <question>\nTime is between 1 and 10 minutes```")
                        else:
                            try:
                                poll_request_time = int(poll_question.split(" ")[0])
                                poll_question = message.content[len(str(poll_request_time)) + 6:]
                                if poll_request_time >= 1 and poll_request_time <= 10:
                                    poll_timer = poll_request_time * 60
                                else:
                                    poll_timer = 300
                            except:
                                poll_timer = 300
                            print("got here")
                            poll_message = message
                            poll_running = True

            if "YES" in command and poll_running == True:
                if str(message.author) in poll_voters:
                    await client.send_message(message.channel, "You have already voted.")
                else:
                    # global poll_yes
                    # global poll_voters
                    poll_yes += 1
                    poll_voters.append(str(message.author))


            if "NO" in command and poll_running == True:
                if str(message.author) in poll_voters:
                    await client.send_message(message.channel, "You have already voted.")
                else:
                    global poll_no
                    # global poll_voters
                    poll_no += 1
                    poll_voters.append(str(message.author))

            if "NEW" in command:
                global proposal
                if proposal != True:
                    command_param = content.split("NEW ")[1]
                    if command_param[0:] == "HELP":
                        await client.send_message(message.channel, "```$NEW <proposed command> <URL for img or gif>\nExample: $new wut www.imgur.com/wut.gif\nKnown to work with imgur.```")
                    c.execute('SELECT * FROM USER_SUBMITTED WHERE command=(?)',
                                (command_param.split(" ")[0],))
                    new_data = c.fetchone()
                    print(str(new_data))
                    if str(new_data) == "None":
                        if len(message.attachments) > 0 or re.search(regex_pattern, command_param.split(" ")[1]):
                            # global proposed_new
                            # global proposal
                            proposed_new['proposed_command'] = command_param.split(" ")[0]
                            if len(message.attachments) > 0:
                                proposed_new['proposed_url'] = message.attachments[0]['url']
                            else:
                                proposed_new['proposed_url'] = message.content.split(" ")[2]
                            if proposed_new['proposed_url'][-4:] == "gifv":
                                proposed_new['proposed_url'] = proposed_new['proposed_url'][0:len(proposed_new['proposed_url'])-1]
                            print(proposed_new['proposed_url'])
                            proposed_new['proposed_message'] = message
                            proposed_new['approved'] = False
                            proposed_new['denied'] = False
                            proposed_new['yay_count'] = 0
                            print(proposed_new['proposed_message'].channel)
                            proposal = True
                        else:
                            await client.send_message(message.channel, "Could not find file in URL: {}".format(command_param.split(" ")[1]))
                    else:
                        await client.send_message(message.channel, "Sorry, the command {} is already in use".format(command_param.split(" ")[0]))
                else:
                    await client.send_message(message.channel, "Please wait until current proposal has finished.")

            if "YAY" in command and proposal == True:
                # global proposed_new
                # global proposed_new_voters
                if str(message.author) in proposed_new_voters:
                    await client.send_message(message.channel, "You have already voted.")
                else:
                    proposed_new['yay_count'] += 1
                    if proposed_new['yay_count'] >= 3:
                        proposed_new['approved'] = True
                    proposed_new_voters.append(str(message.author))

            if "NAY" in command and proposal == True:
                # global proposed_new_voters
                if str(message.author) in proposed_new_voters:
                    await client.send_message(message.channel, "You have already voted.")
                else:
                    # global proposed_new
                    proposed_new['denied'] = True
                    proposed_new_voters.append(str(message.author))

            # if "NEW" not in command:


            c.execute('SELECT * FROM USER_SUBMITTED WHERE command=(?)',(command,))
            new_data = c.fetchone()
            if str(new_data) != "None":
                if command == new_data[3]:
                    await client.send_file(message.channel, 'Static/User/{}'.format(new_data[2]))

        if len(message.attachments) > 0 and Command != True:
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



        if message.content.startswith("$server"):
            await client.send_message(message.channel, str(message.server))


        # Alyx#9261

        if str(message.author) == "Mirokoth#2461" and message.content.startswith("$annoyalyx"):
            with open('matrix.json') as json_file:
                matrix = json.load(json_file)
                with open('matrix.json', 'w') as json_file_out:
                    json.dump({"up_to": matrix['up_to'], "run": 0 }, json_file_out)
            await client.send_message(message.channel, "Matrix mode activated")

        if str(message.author) == "Mirokoth#2461" and message.content.startswith("$sorryalyx"):
            with open('matrix.json') as json_file:
                matrix = json.load(json_file)
                with open('matrix.json', 'w') as json_file_out:
                    json.dump({"up_to": matrix['up_to'], "run": 1 }, json_file_out)
            await client.send_message(message.channel, "Matrix mode disabled")

        if str(message.author) == "Alyx#9261":
            with open('matrix.json') as json_file:
                matrix = json.load(json_file)
                if matrix['run'] == 0:
                    with open('matrix.txt') as script:
                        str_out = str(script.read()[matrix['up_to']:matrix['up_to'] + 1800])
                        await client.send_message(message.author, "```{}```".format(str_out))
                    with open('matrix.json', 'w') as json_file_out:
                        if matrix['up_to'] >= 96590:
                            json.dump({"up_to": 0}, json_file_out)
                        else:
                            json.dump({"up_to": (matrix['up_to'] + 1800), "run": matrix['run'] }, json_file_out)

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

    c.execute('CREATE TABLE IF NOT EXISTS IGNORE(URL TEXT, USER TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS USER_SUBMITTED(server TEXT, user TEXT, file TEXT, command TEXT, url TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS URLS(server TEXT, date_entered TEXT, poster TEXT, url TEXT, post_count INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS REDDIT(URL TEXT, LASTRUN TEXT, JSON TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS OZALERT(ALERT TEXT, USER TEXT, ALERTED TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS OZBARGAIN(ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, TITLE TEXT NOT NULL, URL TEXT NOT NULL)')
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

def top_score(server, user):
    print('Fetching SQL data...')
    c.execute('SELECT * FROM user_count WHERE server=(?)', (str(server),))
    rank_data = c.fetchall()
    rank_data = sorted(rank_data, key=lambda rank: rank[2], reverse=True)
    count = 1
    print('Ranking users...')
    for x in range(0, len(rank_data)):
        rank_data[x] += (count,)
        count += 1
    if user != False:
        print('Matching user... {}'.format(str(user)))
        for x in rank_data:
            print(x)
            if str(user) in x[1]:
                print('Matched' + str(user))
                return(x)
        return(False)
    else:
        return(rank_data)

def get_reddit_json(URL):
    header = {'User-Agent':'Marvin Discord Robit'}
    return requests.get(URL, headers=header)

async def create_command():
    await client.wait_until_ready()
    while not client.is_closed:
        global proposal
        if proposal == True:
            # global proposal
            global proposed_new_voters
            print(proposed_new)
            await client.change_presence(game=discord.Game(name='New command request running'))
            em = discord.Embed(title="New Marvin command has been proposed with the above 'image'?", description="\n\nNeed 3 $yay in the next 10 minutes to approve\nOr 1 $nay to shut this shit down.", colour=0x282B30)
            em.set_author(name=str(proposed_new['proposed_message'].author).split("#")[0], icon_url=proposed_new['proposed_message'].author.avatar_url)
            await client.send_message(proposed_new['proposed_message'].channel, embed=em)
            time_count = 0
            while time_count < 300:
                if proposed_new['approved'] == True:
                    # dostuf
                    c.execute('INSERT INTO USER_SUBMITTED (server, user, file, command, url) VALUES (?, ?, ?, ?, ?)',
                                (str(proposed_new['proposed_message'].server), str(proposed_new['proposed_message'].author), re.search("[^/\\&\?]+\.\w{3,4}(?=([\?&].*$|$))", proposed_new['proposed_url']).group(0),
                                proposed_new['proposed_command'], proposed_new['proposed_url'],))
                    conn.commit()
                    print(proposed_new['proposed_url'])
                    filename = "Static/User/{}".format(re.search("[^/\\&\?]+\.\w{3,4}(?=([\?&].*$|$))", proposed_new['proposed_url']).group(0))
                    with open(filename, 'wb') as file:
                        response = requests.get(proposed_new['proposed_url'])
                        file.write(response.content)
                    em = discord.Embed(title="New Marvin command has been Approved", description="${} is the new command. Enjoy the shitposts".format(proposed_new['proposed_command']), colour=0x282B30)
                    em.set_author(name=str(proposed_new['proposed_message'].author).split("#")[0], icon_url=proposed_new['proposed_message'].author.avatar_url)
                    await client.send_message(proposed_new['proposed_message'].channel, embed=em)
                    time_count = 301
                    proposed_new_voters = []
                    await client.change_presence(game=discord.Game(name='$HELP for commands'))
                elif proposed_new['denied'] == True:
                    # dostuff
                    em = discord.Embed(title="New Marvin command has been Denied", description=" ", colour=0x282B30)
                    em.set_author(name=str(proposed_new['proposed_message'].author).split("#")[0], icon_url=proposed_new['proposed_message'].author.avatar_url)
                    await client.send_message(proposed_new['proposed_message'].channel, embed=em)
                    time_count = 301
                    proposed_new_voters = []
                    await client.change_presence(game=discord.Game(name='$HELP for commands'))
                else:
                    time_count += 1
                    await asyncio.sleep(2)
            if time_count > 300:
                if proposed_new['approved'] == True or proposed_new['denied'] == True:
                    pass
                else:
                    em = discord.Embed(title="Approval has timed out", description="You will need 3 $yay approvals for your command to be submitted.", colour=0x282B30)
                    em.set_author(name=str(proposed_new['proposed_message'].author).split("#")[0], icon_url=proposed_new['proposed_message'].author.avatar_url)
                    await client.send_message(proposed_new['proposed_message'].channel, embed=em)
                    proposed_new_voters = []
                proposal = False
                await client.change_presence(game=discord.Game(name='$HELP for commands'))

        await asyncio.sleep(2)

async def poll_background():
    await client.wait_until_ready()
    while not client.is_closed:
        global poll_running
        global poll_yes
        global poll_no
        if poll_running == True:
            await client.change_presence(game=discord.Game(name="Poll running"))
            em = discord.Embed(title="Poll started - {} minutes".format(poll_timer / 60), description=poll_question, colour=0x282B30)
            em.set_author(name=str(poll_message.author).split("#")[0], icon_url=poll_message.author.avatar_url)
            em.add_field(name="To Answer: ", value="$Yes or $No", inline=True)
            await client.send_message(poll_message.channel, embed=em)
            await asyncio.sleep(poll_timer) # task runs every 60 seconds
            if poll_yes > poll_no:
                em = discord.Embed(title="Yes Wins!", description="With {} votes".format(poll_yes), colour=0x282B30)
                em.set_author(name=str(poll_message.author).split("#")[0], icon_url=poll_message.author.avatar_url)
                em.add_field(name="The Question was:", value=poll_question, inline=True)
                await client.send_message(poll_message.channel, embed=em)
                await client.change_presence(game=discord.Game(name='$HELP for commands'))
            elif poll_no > poll_yes:
                em = discord.Embed(title="No Wins!", description="With {} votes".format(poll_no), colour=0x282B30)
                em.set_author(name=str(poll_message.author).split("#")[0], icon_url=poll_message.author.avatar_url)
                em.add_field(name="The Question was:", value=poll_question, inline=True)
                await client.send_message(poll_message.channel, embed=em)
                await client.change_presence(game=discord.Game(name='$HELP for commands'))
            elif poll_no == poll_yes:
                em = discord.Embed(title="It was a tie", description="With {} votes for each yes and no".format(poll_yes), colour=0x282B30)
                em.set_author(name=str(poll_message.author).split("#")[0], icon_url=poll_message.author.avatar_url)
                em.add_field(name="The Question was:", value=poll_question, inline=True)
                await client.send_message(poll_message.channel, embed=em)
                await client.change_presence(game=discord.Game(name='$HELP for commands'))
            poll_voters = []
            poll_yes = 0
            poll_no = 0
            poll_running = False
        await asyncio.sleep(2)

async def ozbargain():
    print("Running ozbargain loop")
    while not client.is_closed:
        try:
            await asyncio.sleep(90)
            response1 = requests.get('https://www.ozbargain.com.au/deals/feed', timeout=240)
            response1 = BeautifulSoup(response1.content, 'xml')
            response1results = response1.findAll('item')
            c.execute("SELECT * FROM ozbargain ORDER BY ID")
            temp_out = [dict((c.description[i][0], value) for i, value in enumerate(row)) for row in c.fetchall()]
            for result in response1results:
                if re.sub('<(.*?)>', '', str(result.find('link'))) not in str(temp_out):
                    c.execute("INSERT INTO ozbargain (title, url) VALUES (?,?)", (re.sub('<(.*?)>', '', str(result.find('title'))), re.sub('<(.*?)>', '', str(result.find('link')))))
                    conn.commit()
                else:
                    pass
                # MATCH AGAINST SQLITE DB AND ALERT USER
                c.execute('SELECT * FROM OZALERT')
                data = c.fetchall()
                for entry in data:
                    entry = str(entry)
                    for ch in ["(",")","'"]:
                        if ch in entry:
                            entry = entry.replace(ch,"")
                    entry = str(entry).split(",")
                    if entry[0] in re.sub('<(.*?)>', '', str(result.find('title'))).upper():
                        title = re.sub('<(.*?)>', '', str(result.find('title')))
                        for ch in ["(",")","'"]:
                            if ch in title:
                                title = str(entry).replace(ch,"")
                        if len(str(entry[2])) > 0:

                            if re.sub('<(.*?)>', '', str(result.find('link'))) not in str(entry[2][1:]):
                                c.execute('UPDATE OZALERT SET ALERTED = (?) WHERE ALERT = (?) AND USER = (?)', (str(entry[2][1:]) + re.sub('<(.*?)>', '', str(result.find('link'))) + ";", entry[0], entry[1][1:],))
                                conn.commit()
                                for server in client.servers:
                                    for user in server.members:
                                        if str(user.name) in entry[1]:
                                            await client.send_message(user, "Hey! I found a match for an OzBargain alert you setup - {}\n$ozalert - $ozlist - $ozremove\n{}".format(entry[0],re.sub('<(.*?)>', '', str(result.find('link')))))
                    else:
                        pass
        except requests.exceptions.RequestException as e:
            print(e)
            continue


create_table()
read_from_db()
client.loop.create_task(poll_background())
client.loop.create_task(create_command())
client.loop.create_task(ozbargain())
# Marvin:
client.run('API')
# Test Bot:
# client.run('API')
