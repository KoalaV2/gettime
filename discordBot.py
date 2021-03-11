from main import GetTime
from main import currentTime
from main import loadConfigfile
import json
import time
import discord,asyncio
import os
from discord.ext import tasks, commands

#Set path
os.chdir(os.path.dirname(os.path.realpath(__file__)))

configfile = loadConfigfile("settings.cfg")

# Gets discord bot token from configfile
TOKEN = configfile['discordKey']

#Creates JSON file if it doesnt exist
if not os.path.isfile("users.json"):
    open("users.json",'w').close()

#Loads subscribed users into dict (from json file)
with open("users.json") as f:
    try:idsToCheck = json.load(f)
    except:idsToCheck = []

def updateUserFile():
    global idsToCheck
    with open("users.json", "w") as outfile: 
        json.dump(idsToCheck, outfile) 

client = discord.Client()

@client.event
async def on_message(message):   
    if message.author == client.user:return #keep bot from responding to itself 
    if message.content.lower().startswith("!gt"):
        userMessage = message.content.split(' ')
        
        if userMessage[1].lower() in ('reg','notify'):
            try:idToCheck = userMessage[2]
            except:await message.channel.send(f"> Incorrect usage of `!gt {userMessage[1].lower()}` (No ID)")

            try:remindThisManyMinutes = int(userMessage[3])
            except:remindThisManyMinutes = 5 #default value 5 minutes
            
            userAllreadyRegged = False
            for x in range(len(idsToCheck)):
                if idsToCheck[x]['discordID'] == message.author.id:
                    userAllreadyRegged = True
                    idsToCheck[x]['id'] = idToCheck
                    idsToCheck[x]['minutes'] = remindThisManyMinutes
                    await message.channel.send("> Updated your notification!")
                    
            if userAllreadyRegged == False:
                idsToCheck.append({"id":idToCheck,"discordID":message.author.id,"minutes":remindThisManyMinutes})
                await message.channel.send(f"> You will now be notified {remindThisManyMinutes} {'minute' if remindThisManyMinutes == 1 else 'minutes'} before every lession!")
            
            updateUserFile()
        
        if userMessage[1].lower() in ('unreg','unnotify'):
            userAllreadyRegged = False
            for x in range(len(idsToCheck)):
                if idsToCheck[x]['discordID'] == message.author.id:
                    del idsToCheck[x]
                    updateUserFile()
                    await message.channel.send("> You will no longer be notified about when the next lessions start.")
                    return

@client.event
async def on_ready():
    global timeNow
    print(f'Logged in as\n{client.user.name}\n{client.user.id}\n------')

    timeNow = {'minute':69.420} #Defaults to a impossible value so that it will run the check at startup every time
    lessionStart.start()
    print("Tasks started")

# Needs alot of optimazation!
# Needs to cache user lession data, so that it doesnt have to make new request every minute
# Timescore is just ticking up, could just be a normal number that increases.
@tasks.loop(seconds=6)
async def lessionStart():
    global timeNow
    if currentTime()['minute'] == timeNow['minute']:
        print('Minute had not changed yet')
        return
    timeNow = currentTime()
    timeScore = (timeNow['hour'] * 60) + timeNow['minute']
    print("TimeScore:",timeScore)
    
    for currentID in idsToCheck:
        print(f"Checking id: {currentID}...")
        a = GetTime(
            _id=currentID['id'],
            _day=currentTime()['weekday']+1
        ).fetch()

        for x in a:
            timeNowTemp = x.timeStart.split(':')
            timeScoreTemp = (int(timeNowTemp[0]) * 60) + int(timeNowTemp[1])
            minutesBeforeStart = timeScoreTemp-timeScore

            if minutesBeforeStart == currentID['minutes']:
                a = await client.fetch_user(user_id=int(currentID['discordID']))
                await a.send(f"'{x.lessionName}' starts in {minutesBeforeStart} {'minute' if minutesBeforeStart == 1 else 'minutes'}!")

    print('Waiting for minute to change...')

if __name__ == "__main__":
    print("Starting Discord Bot...")
    client.run(TOKEN)
