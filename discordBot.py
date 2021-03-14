#region IMPORT
import os
import time
import json
import logging
import discord
import traceback
from main import GetTime
from main import SetLogging
from main import CurrentTime
from discord.ext import tasks
#from main import loadConfigfile
#endregion

#Set path
os.chdir(os.path.dirname(os.path.realpath(__file__)))

with open("settings.json") as f:
    try:configfile = json.load(f)
    except:configfile = {}

#Default settings (before cfg file has been loaded in)
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s") 

logFileName = "discord_logfile.log"
logFileLocation = configfile['logFileLocation']
# logging.error(f"From now on, logs will be found at '{logFileLocation+logFileName}'")
SetLogging(path=logFileLocation,filename=logFileName)

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
            except:await message.channel.send(f"> Incorrect usage of `!gt {userMessage[1].lower()}` (No ID was passed in)")

            try:remindThisManyMinutes = int(userMessage[3])
            except:remindThisManyMinutes = 5 # Default value is 5 minutes
            
            for x in range(len(idsToCheck)):
                #If this is true, that means that discord ID has allready been registred, so it will instead update that entry
                if idsToCheck[x]['discordID'] == message.author.id:
                    idsToCheck[x]['id'] = idToCheck
                    idsToCheck[x]['minutes'] = remindThisManyMinutes
                    updateUserFile()
                    await message.channel.send("> Updated your notification!")
                    return

            idsToCheck.append({"id":idToCheck,"discordID":message.author.id,"minutes":remindThisManyMinutes})
            await message.channel.send(f"> You will now be notified {remindThisManyMinutes} {'minute' if remindThisManyMinutes == 1 else 'minutes'} before every lession!")
            updateUserFile()
        
        if userMessage[1].lower() in ('unreg','unnotify'):
            for x in range(len(idsToCheck)):
                if idsToCheck[x]['discordID'] == message.author.id:
                    del idsToCheck[x]
                    updateUserFile()
                    await message.channel.send("> You will no longer be notified about when the next lessions start.")
                    return

@client.event
async def on_ready():
    global timeNow
    logging.error(f'Logged in as\n{client.user.name}\n{client.user.id}\n------')

    timeNow = {'minute':69.420} # Defaults to a impossible value so that it will run the check at startup every time
    lessionStart.start()
    logging.error("Tasks started")

# Still needs alot of optimazation!
cacheAgeMax = 5*60 #Secounds
cachedResponses = {}
@tasks.loop(seconds=6)
async def lessionStart():
    try:
        # timeNow is a variable that 

        global timeNow, cachedResponses, timeScore
        currentTimeTemp = CurrentTime()

        #Checks if its monday - friday
        if currentTimeTemp['weekday'] in (1,2,3,4,5) or configfile['DEBUGMODE'] == True:

            #Checks if the minute has changed
            if currentTimeTemp['minute'] == timeNow['minute']:
                logging.error('Minute had not changed yet')
                return
            
            timeNow = currentTimeTemp
            timeScore = (currentTimeTemp['hour'] * 60) + currentTimeTemp['minute']
            
            # Iterates through all the ID's
            for currentID in idsToCheck:
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
                    a = GetTime(_id=currentID['id'],_day=currentTimeTemp['weekday']).fetch()
                    cachedResponses[str(currentID['discordID'])] = {'data':a,'age':time.time()}

                for x in a:
                    temp = x.timeStart.split(':')
                    lessionTimeScore = (int(temp[0]) * 60) + int(temp[1])
                    minutesBeforeStart = lessionTimeScore-timeScore

                    logging.error(f"'{x.lessionName}' starts in {minutesBeforeStart}")

                    if minutesBeforeStart == currentID['minutes']:
                        userDM = await client.fetch_user(user_id=int(currentID['discordID']))
                        await userDM.send(f"'{x.lessionName}' starts in {minutesBeforeStart} {'minute' if minutesBeforeStart == 1 else 'minutes'}{' in ' + x.classroomName if x.classroomName != '' else ''}!")
                        logging.error('Notified user')
                    else:
                        logging.error('Did not notify user')

            logging.error('Waiting for minute to change...')
        else:
            logging.error("Skipping (Not monday-friday)")
    except:
        logging.error(traceback.format_exc()) # Catches any error and puts it in the log file (need to fix proper logging)
if __name__ == "__main__":
    logging.error("Starting Discord Bot...")
    client.run(configfile['discordKey'])
