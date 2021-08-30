#!/usr/bin/env python3
version = "GTD.1.0.0"
#region IMPORT
import os
import time
import json
import logging
import discord
import traceback
from discord.ext import tasks
from main import GetTime # type: ignore
from main import SetLogging # type: ignore
from main import CurrentTime # type: ignore
from main import GenerateHiddenURL # type: ignore
from main import TinyUrlShortener # type: ignore
from urllib3.exceptions import MaxRetryError

from main import init_Load
l = init_Load()
configfile = l['configfile']
allSchools = l['allSchools']
allSchoolsList = l['allSchoolsList']
allSchoolsNames = l['allSchoolsNames']
#endregion
#region INIT
os.chdir(os.path.dirname(os.path.realpath(__file__))) # Set working dir to path of main.py

logFileName = "discord_logfile.log"
logFileLocation = configfile['logFileLocation']

if configfile['logToFile']:
    SetLogging(path=logFileLocation,filename=logFileName, format=configfile['loggingFormat'])
else:
    logging.basicConfig(level=logging.DEBUG, format=configfile['loggingFormat'])

# Creates JSON file if it doesnt exist
if not os.path.isfile("users.json"):
    open("users.json",'w').close()

# Loads subscribed users into dict (from json file)
with open("users.json") as f:
    try:idsToCheck = json.load(f)
    except:idsToCheck = {}

client = discord.Client()

discordColor = discord.Colour.from_rgb(configfile['discordRGB'][0],configfile['discordRGB'][1],configfile['discordRGB'][2])
#endregion
#region FUNCTIONS
def urlEmbed(text, url) -> str:
    return f"[{text}]({url})"
def updateUserFile():
    global idsToCheck
    with open("users.json", "w") as outfile:
        json.dump(idsToCheck, outfile)
#endregion
#region CLASSES
class EmbedMessage:
    def __init__(self,title="", description=""):
        self.title = title
        self.description = description
    def send(self, sendTo):
        return sendTo.send(
            embed=discord.Embed(
                color=discordColor,
                title=self.title,
                description=self.description
            )
        )
#endregion

@client.event
async def on_message(message):
    if message.author==client.user:return # Keeps bot from responding to itself
    userMessage = message.content.split(' ')
    if userMessage[0] == configfile['discordPrefix']:

        def GetIdFromUser(messageIndex=2):
            try:
                return userMessage[messageIndex]
            except:
                if str(message.author.id) in idsToCheck:
                    return idsToCheck[str(message.author.id)]['id']
                else:
                    return None
        def GetSchoolFromUser(messageIndex=3):
            try:
                return int(userMessage[messageIndex])
            except:
                if str(message.author.id) in idsToCheck:
                    return int(idsToCheck[str(message.author.id)]['school'])
                else:
                    return None

        if userMessage[1].lower() in ('v', 'version'):
            return await EmbedMessage(
                title=f"GetTimeBot (v{version})",
                description='*"Whats wrong with it this time"* / Tay'
            ).send(message.channel)
        if userMessage[1].lower() in ('reg','notify'):

            if userMessage[2] == "help":
                return await EmbedMessage(
                    title=f"{configfile['discordPrefix']} {userMessage[1].lower()} hjälp",
                    description="\n".join((
                        f"Användning :\n{configfile['discordPrefix']} {userMessage[1].lower()} `<DITT ID HÄR>` `<DIN SKOL-ID HÄR>` `<HUR MÅNGA MINUTER I FÖRVÄG DU VILL BLI NOTIFIERAD>`",
                        "",
                        "SKOL-ID's :\n",
                        "\n".join([f"{allSchools[x]['name']} : `{allSchools[x]['id']}`" for x in allSchoolsNames])
                    )
                )).send(message.channel)


            idToCheck = GetIdFromUser()
            schoolToCheck = GetSchoolFromUser()

            if None in (idsToCheck, schoolToCheck):
                await EmbedMessage(
                    title=f"Fel användning av `{configfile['discordPrefix']} {userMessage[1].lower()}`\nSkriv `{configfile['discordPrefix']} {userMessage[1].lower()} help` för mer info."
                ).send(message.channel)
                await message.channel.send(f"> Fel användning av `{configfile['discordPrefix']} {userMessage[1].lower()}` (Inget ID)")
                return

            try:remindThisManyMinutes = int(userMessage[4])
            except:remindThisManyMinutes = 5 # Default value is 5 minutes

            #Tries to fetch the ID to see if its valid
            try:
                checkIDisValid = GetTime(_id=idToCheck,_school=schoolToCheck).getData()
            except MaxRetryError:
                await message.channel.send(f"> Försök igen senare! (MaxRetryError)")
                return

            if checkIDisValid['status'] < 0:
                if checkIDisValid['status'] == -6:
                    await message.channel.send(f"> Något gick fel! ({checkIDisValid['validation'][0]['message']})")
                else:
                    await message.channel.send(f"> Något gick fel! ({checkIDisValid['message']})")
            else:
                if str(message.author.id) in idsToCheck:
                    idsToCheck[str(message.author.id)] = {
                        'id':idToCheck,
                        'school':schoolToCheck,
                        'discordID':message.author.id,
                        'minutes':remindThisManyMinutes
                    }
                    updateUserFile()
                    await EmbedMessage(title="Dina nya inställningar är sparade!").send(message.channel)
                else:
                    idsToCheck[str(message.author.id)] = {
                        "id":idToCheck,
                        'school':schoolToCheck,
                        "discordID":message.author.id,
                        "minutes":remindThisManyMinutes
                    }

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
            userID = GetIdFromUser()
            if userID == None:
                await message.channel.send(f"> Fel användning av `{configfile['discordPrefix']} {userMessage[1].lower()}` (Inget ID)")

            currentTimeTemp = CurrentTime()
            myRequest = GetTime(
                _id=userID,
                _day=currentTimeTemp['weekday3'],
                _week=currentTimeTemp['week2']
            )

            getTimeURL = GenerateHiddenURL(configfile['key'], myRequest._id, configfile['mainLink'])[0] + f"&week={myRequest._week}&day={myRequest._day}"
            try:
                await EmbedMessage(
                    f"Här är ditt schema för {currentTimeTemp['dayNames'][myRequest._day-1].capitalize()}, v.{myRequest._week}!\n",
                    myRequest.GenerateTextSummary(mode="discord") + f"\n{urlEmbed('Öppna schemat online',getTimeURL)}"
                ).send(message.channel)
            except MaxRetryError:
                return await message.channel.send(f"> Försök igen senare! (MaxRetryError)")
        if userMessage[1].lower() in ('next'):
            idToCheck = GetIdFromUser()
            if idsToCheck == None:
                await message.channel.send(f"> Fel användning av `{configfile['discordPrefix']} {userMessage[1].lower()}` (Inget ID)")
            else:
                currentTimeTemp = CurrentTime()
                try:
                    a = GetTime(
                        _id=idToCheck,
                        _day=currentTimeTemp['weekday']
                    ).fetch(allowCache=False)
                except MaxRetryError:
                    return await message.channel.send(f"> Försök igen senare! (MaxRetryError)")

                timeScore = (currentTimeTemp['hour'] * 60) + currentTimeTemp['minute']
                for x in a:
                    lessonTimeScore = x.GetTimeScore(start=True)
                    minutesBeforeStart = lessonTimeScore-timeScore
                    if minutesBeforeStart > 0:
                        await EmbedMessage(
                            title=f"Nästa lektion är '{x.lessonName}' som börjar kl {x.timeStart[:-3]}{' i ' + x.classroomName if x.classroomName != '' else ''}!"
                        ).send(message.channel)
                        return

@client.event
async def on_ready():
    global timeNow
    logging.error(f'Logged in as\n{client.user.name}\n{client.user.id}\n------')

    timeNow = {'minute':69.420} # Defaults to a impossible value so that it will run the check at startup every time
    lessonStart.start()
    logging.error("Tasks started")

# Still needs alot of optimazation!
cacheAgeMax = 5*60 # Secounds
cachedResponses = {}
backup_cachedResponses = {}
@tasks.loop(seconds=6)
async def lessonStart():
    try:
        global timeNow, cachedResponses, backup_cachedResponses, timeScore
        currentTimeTemp = CurrentTime()

        #Checks if time is after 8PM or before 6AM, and then skips it
        if currentTimeTemp['hour'] > 20 or currentTimeTemp['hour'] < 6:
            return

        #Checks if its monday - friday OR if debugmode is on
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
                # Check if there is data cached...
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
                    logging.error("Running request...")
                    try:
                        a = GetTime(
                            _id=currentID['id'],
                            _day=currentTimeTemp['weekday'],
                            _week=currentTimeTemp['week']
                        ).fetch()

                        if 'status' in a and a['status'] < 0:
                            userDM = await client.fetch_user(user_id=int(currentID['discordID']))
                            return await userDM.send(f"⚠️ OKÄNT FEL : {str(a)}")

                        cachedResponses[str(currentID['discordID'])] = {'data':a,'age':time.time()}
                    except MaxRetryError:
                        userDM = await client.fetch_user(user_id=int(currentID['discordID']))
                        return await userDM.send(f"> Försök igen senare! (MaxRetryError)")

                # if 'status' in a and a['status'] < 0:
                #     if str(currentID['discordID']) in cachedResponses:
                #         a = backup_cachedResponses[str(currentID['discordID'])]['data']
                #     else:
                #         userDM = await client.fetch_user(user_id=int(currentID['discordID']))
                #         await EmbedMessage(
                #             title=f"Could not fetch your next lession! (Sorry!)"
                #         ).send(userDM)

                # #Backup to backup_cachedResponses
                # if not str(currentID['discordID']) in backup_cachedResponses:
                #     logging.error(f"Had to use backup_cachedResponses! Fine for now, but schedule could be outdated.")
                #     backup_cachedResponses[str(currentID['discordID'])] = {'data':a}

                for x in a:
                    lessonTimeScore = x.GetTimeScore(start=True)
                    minutesBeforeStart = lessonTimeScore-timeScore
                    if minutesBeforeStart == currentID['minutes'] or currentID['minutes'] == "always":
                        userDM = await client.fetch_user(user_id=int(currentID['discordID']))
                        await EmbedMessage(
                            title=f"'{x.lessonName}' börjar om {minutesBeforeStart} {'minut' if minutesBeforeStart == 1 else 'minuter'}{' i sal' + x.classroomName if x.classroomName != '' else ''}!"
                        ).send(userDM)
                    else:
                        pass
                        #logging.error(f"minutesBeforeStart was {minutesBeforeStart}, not {currentID['minutes']}")

            logging.error('Waiting for minute to change...')
    except:
        logging.error(traceback.format_exc()) # Catches any error and puts it in the log file (need to fix proper logging)

if __name__ == "__main__":
    logging.error("Starting Discord Bot...")
    client.run(configfile['discordKey'])

# if userMessage[1].lower() in ('help','?'):
#     c = (

#     )


#     commandsList = (
#         {
#             "commandName":"help",
#             "commandBrief":"Visar detta hjälpmeddelande.",
#             "commandExample":None
#         },
#         {
#             "commandName":"schema/today/me",
#             "commandBrief":"Visar ditt schema.",
#             "commandExample":"19_tek_a"
#         }
#     )

#     a = ""
#     for x in commandsList:
#         a += f"`{configfile['discordPrefix']} {x['commandName']}`\n{x['commandBrief']}\n\n"
#         if x['commandExample'] != None:
#             a += f"Exempel: `{configfile['discordPrefix']} {x['commandName']} {x['commandExample']}`\n"


#     embed = discord.Embed(
#         color=messageColor,
#         title="GetTime Hjälp",
#         description=a
#     );await message.channel.send(embed=embed)
