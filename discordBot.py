#region IMPORT
import os
import time
import json
import logging
import discord
import traceback
from subprocess import run
from main import GetTime
from main import SetLogging
from main import CurrentTime
from main import GenerateHiddenURL
from discord.ext import tasks
from urllib.parse import urlencode
#endregion

#region INIT
os.chdir(os.path.dirname(os.path.realpath(__file__))) # Set working dir to path of main.py

with open("settings.json") as f:
    try:configfile = json.load(f)
    except:configfile = {}

logFileName = "discord_logfile.log"
logFileLocation = configfile['logFileLocation']
SetLogging(path=logFileLocation,filename=logFileName)

# Creates JSON file if it doesnt exist
if not os.path.isfile("users.json"):
    open("users.json",'w').close()

# Loads subscribed users into dict (from json file)
with open("users.json") as f:
    try:idsToCheck = json.load(f)
    except:idsToCheck = {}

client = discord.Client()
messageColor = discord.Colour.from_rgb(138,194,241)
#endregion

def TinyUrlShortener(urlInput):
    try:
        a = run(f'curl "http://tinyurl.com/api-create.php?{urlencode({"url":urlInput})}"',capture_output=1).stdout.decode('utf-8')
        if a == "Error":
            return urlInput
        return a
    except:
        return urlInput

def updateUserFile():
    global idsToCheck
    with open("users.json", "w") as outfile: 
        json.dump(idsToCheck, outfile) 

@client.event
async def on_message(message):   
    if message.author == client.user:return # Keeps bot from responding to itself
    if message.content.lower().startswith("!gt"):
        userMessage = message.content.split(' ')
        
        def GetIdFromUser(messageIndex=2):
            try:
                return userMessage[messageIndex]
            except:
                if str(message.author.id) in idsToCheck:
                    return idsToCheck[str(message.author.id)]['id']
                else:
                    return None

        if userMessage[1].lower() in ('reg','notify'):
            idToCheck = GetIdFromUser()
            if idsToCheck == None:
                await message.channel.send(f"> Fel användning av `!gt {userMessage[1].lower()}` (Inget ID)")
                return

            try:remindThisManyMinutes = int(userMessage[3])
            except:remindThisManyMinutes = 5 # Default value is 5 minutes
            
            #Tries to fetch the ID to see if its valid
            checkIDisValid = GetTime(_id=idToCheck).getData()['validation']
            if len(checkIDisValid) != 0:
                try:
                    await message.channel.send(f"> Något gick fel! ({checkIDisValid[0]['message']})")
                except:
                    await message.channel.send("> Något gick fel!")
            else:
                if str(message.author.id) in idsToCheck:
                    idsToCheck[str(message.author.id)] = {
                        'id':idToCheck,
                        'discordID':message.author.id,
                        'minutes':remindThisManyMinutes
                    }
                    updateUserFile()
                    await message.channel.send("> Inställningar sparade!")
                else:
                    idsToCheck[str(message.author.id)] = {"id":idToCheck,"discordID":message.author.id,"minutes":remindThisManyMinutes}
                    updateUserFile()
                    await message.channel.send(f"> Du kommer nu bli notifierad {remindThisManyMinutes} {'minut' if remindThisManyMinutes == 1 else 'minuter'} innan varje lektion!")
        if userMessage[1].lower() in ('unreg','unnotify'):
            if str(message.author.id) in idsToCheck:
                del idsToCheck[str(message.author.id)]
                updateUserFile()
                await message.channel.send("> Du kommer inte längre bli notifierad innan en lektion börjar.")
            else:
                await message.channel.send("> Du har inte registrerat dig!")
        if userMessage[1].lower() in ('schema','today','me'):
            try:
                userID = userMessage[2]
            except:
                if str(message.author.id) in idsToCheck:
                    userID = idsToCheck[str(message.author.id)]['id']
                else:
                    await message.channel.send(f"> Fel användning av `!gt {userMessage[1].lower()}` (Inget ID)")
                    return
            
            currentTimeTemp = CurrentTime()
            myRequest = GetTime(_id=userID,_day=currentTimeTemp['weekday3'],_week=currentTimeTemp['week2'])

            getTimeURL = GenerateHiddenURL(configfile['key'],myRequest._id,configfile['mainLink'])[0] #TinyUrlShortener(GenerateHiddenURL(configfile['key'],myRequest._id,configfile['mainLink'])) 
            
            embed = discord.Embed(
                color=messageColor,
                title=f"Här är ditt schema för {currentTimeTemp['dayNames'][myRequest._day-1].capitalize()}, v.{myRequest._week}!\n",
                description=myRequest.GenerateTextSummary(mode="discord") + f"\n[Öppna schemat online]({getTimeURL})"
            );await message.channel.send(embed=embed)
        # if userMessage[1].lower() in ('next'):
        #     idToCheck = GetIdFromUser()
        #     if idsToCheck == None:
        #         await message.channel.send(f"> Fel användning av `!gt {userMessage[1].lower()}` (Inget ID)")
        #         return
                    
        #     a = json.loads(run(f'curl "https://gettime.ga/API/SIMPLE_JSON?{urlencode({"a":1,"id":idToCheck})}"',capture_output=1).stdout.decode('utf-8'))
            
        #     currentTimeTemp = CurrentTime()

        #     timeScore = (currentTimeTemp['hour'] * 60) + currentTimeTemp['minute']

        #     for x in a['lessons']:
        #         temp = x['timeStart'].split(':')
        #         lessonTimeScore = (int(temp[0]) * 60) + int(temp[1])

        #         if lessonTimeScore > timeScore:
        #             print(f"Nästa lektion är '{x['lessonName']}' som börjar kl {x['timeStart']} {' i ' + x['classroomName'] if x['classroomName'] != '' else ''}!")



@client.event
async def on_ready():
    global timeNow
    logging.error(f'Logged in as\n{client.user.name}\n{client.user.id}\n------')

    timeNow = {'minute':69.420} # Defaults to a impossible value so that it will run the check at startup every time
    lessonStart.start()
    logging.error("Tasks started")

# Still needs alot of optimazation!
cacheAgeMax = 5*60 #Secounds
cachedResponses = {}
@tasks.loop(seconds=6)
async def lessonStart():
    try:
        global timeNow, cachedResponses, timeScore
        currentTimeTemp = CurrentTime()

        #Checks if its monday - friday
        if currentTimeTemp['weekday'] in (1,2,3,4,5) or configfile['DEBUGMODE'] == True:

            #Checks if the minute has changed
            if currentTimeTemp['minute'] == timeNow['minute']:
                #logging.error('Minute had not changed yet')
                return
            
            timeNow = currentTimeTemp
            timeScore = (currentTimeTemp['hour'] * 60) + currentTimeTemp['minute']
            
            # Iterates through all the ID's
            for currentKey in idsToCheck:
                currentID = idsToCheck[currentKey]
                logging.error(f"Checking id: {currentID}...")           
                
                a = None
                if str(currentID['discordID']) in cachedResponses:
                    logging.error(str(currentID['discordID']) + ' was cached, checking age...')

                    if time.time() - cachedResponses[str(currentID['discordID'])]['age'] < cacheAgeMax:
                        a = cachedResponses[str(currentID['discordID'])]['data']
                        logging.error('used cache from ' + str(currentID['discordID']))
                    else:
                        logging.error(str(currentID['discordID']) + ' was to old!')
                        del cachedResponses[str(currentID['discordID'])]
                else:
                    logging.error(str(currentID['discordID']) + ' was NOT cached')

                if a == None:
                    logging.error("Running request")
                    a = GetTime(
                        _id=currentID['id'],
                        _day=currentTimeTemp['weekday']
                    ).fetch()
                    cachedResponses[str(currentID['discordID'])] = {'data':a,'age':time.time()}

                for x in a:
                    temp = x.timeStart.split(':')
                    lessonTimeScore = (int(temp[0]) * 60) + int(temp[1])
                    minutesBeforeStart = lessonTimeScore-timeScore
                    if minutesBeforeStart == currentID['minutes']:
                        userDM = await client.fetch_user(user_id=int(currentID['discordID']))

                        embed = discord.Embed(
                            color=messageColor,
                            title=f"'{x.lessonName}' börjar om {minutesBeforeStart} {'minut' if minutesBeforeStart == 1 else 'minuter'}{' i ' + x.classroomName if x.classroomName != '' else ''}!"
                        );await userDM.send(embed=embed)

            logging.error('Waiting for minute to change...')
    except:
        logging.error(traceback.format_exc()) # Catches any error and puts it in the log file (need to fix proper logging)

if __name__ == "__main__":
    logging.error("Starting Discord Bot...")
    client.run(configfile['discordKey'])
