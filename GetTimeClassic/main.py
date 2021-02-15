import discord,asyncio,multitasking,os,getTime_HTML
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')

with open("private.txt","r+") as f: #Gets discord bot token from TOKEN.txt
    TOKEN = f.readlines()[2].strip("\n")
client = discord.Client() 
getFoodHasChecked,getFoodHasCheckedToday=False,False

@client.event
async def on_message(message):   
    if message.author == client.user:return #keep bot from responding to itself 
    if message.content.lower().startswith("!gt"):
        userMessage = (message.content)[4:].lower() #Strips away "!gt " so you are left with the command itself
        if userMessage == "":
            return
        import base64,hashlib
        from getScripts import getToday 

        def deEncode(keyInput, stringInput,enOrDe): #enOrDe should be set to "en" for encoding and "de" for decoding
            key,string,ec = str(keyInput),str(stringInput),[]
            for i in range(len(string)):
                if enOrDe == "en":ec.append(chr(ord(string[i]) + ord(key[i % len(key)]) % 256))
                else:ec.append(chr((ord(string[i]) - ord(key[i % len(key)]) + 256) % 256))       
            return ''.join(ec)

        theFileName = f"discordIds/{str(hashlib.md5(str.encode(str(message.author.id))).hexdigest())}.txt"

        if userMessage == "help" or userMessage == "faq" :
            #messageToFetch = f"discord{userMessage.capitalize()}Message.txt" #TO CHANGE WHEN I FINISH FAQ
            helpMessage = ""
            with open("discordHelpMessage.txt","r") as f: 
                for x in f.readlines():
                    helpMessage+=x
            await message.channel.send(helpMessage)          
        elif userMessage.startswith("setme"):
            toSet = (userMessage.split("setme")[1])[1:]
            if toSet != "":
                import io
                with io.open(theFileName,"w+", encoding="utf-8") as textFile:
                    textFile.write(deEncode((message.author.id),toSet,"en"))
                await message.channel.send("> Your custom schedule has been saved, use `!gt me` to see it!")
            else:await message.channel.send("> Incorrect usage of `!gt setme`, check `!gt help` for more info")
        elif userMessage == "me" or userMessage == "me-force" or userMessage == "vm-me" or userMessage == "vm-me-force":
            import os,getScripts,io
            if os.path.exists(theFileName):
                loadingMessage = await message.channel.send("> Please wait...")
                with io.open(theFileName,"r", encoding="utf-8") as textFile:
                    converted = getScripts.getConvertUrl(deEncode(message.author.id,textFile.readline(),"de"))
                if userMessage.endswith("-force"):converted[3] = True
                if userMessage.startswith("vm"):converted[5],converted[0] = getToday(),"vm"
                getFilenameResult = getScripts.getFilename(converted,False)
                await discord.Message.delete(loadingMessage) 
                if getFilenameResult == None:  await message.channel.send("> There was an error when getting your schedule, or you entered an incorrect ID")
                else:await message.channel.send("> Here is your schedule!",file=discord.File(getFilenameResult[0]))
            else:
                await message.channel.send('> You dont have a schedule saved. You need to use `!gt setme [ID]` before you can use `!gt me`')        
        elif userMessage == "checkme":
            import os,io
            if os.path.exists(theFileName):
                try:
                    with io.open(theFileName,"r", encoding="utf-8") as textFile:
                        await message.channel.send(f'> You have "{deEncode(message.author.id,textFile.readline(),"de")}" saved in `!gt me`')
                except:await message.channel.send("> Something went wrong, please try again.")
            else:await message.channel.send("> No schedule was found with your ID linked to it, have you set one using `!gt setme`?")
        elif userMessage == "clearme":
            import os
            if os.path.exists(theFileName): #If the file exists
                try:os.remove(theFileName);await message.channel.send("> Successfully deleted your `!gt me` shortcut!")
                except:await message.channel.send("> Something went wrong, please try again.")
            else:await message.channel.send("> No schedule was found with your ID linked to it, have you set one using `!gt setme`?")
        elif userMessage == "food":
            msg = ">>> **GetFood**\n\n"
            dagar = ["Mån","Tis","Ons","Tor","Fre"]
            with open("getFood.txt","r") as f:
                foods = f.readlines()
            for x in range(5):
                msg += f"{dagar[x]} : {foods[x].strip()}\n"
            await message.channel.send(msg)
        else:
            loadingMessage = await message.channel.send("> Please wait...")
            import getScripts
            getFilenameResult = getScripts.getFilename(userMessage,True)
            await discord.Message.delete(loadingMessage) 
            if getFilenameResult == None:await message.channel.send("> There was an error when getting your schedule, or you entered an incorrect ID")
            else:await message.channel.send("> Here is your schedule!",file=discord.File(getFilenameResult[0]))

@multitasking.task
def runWebsite():
    import website
    with open("private.txt","r+") as f:
        website.bootServer(f.readlines())

def runCacheClearer(thePath,theAge,thePause):
    from getScripts import getCacheClearer
    getCacheClearer(thePath,theAge)
    logging.info(f"Looping again in {thePause} secounds...")  

@multitasking.task
def doTimeTasks():
    global getFoodHasChecked, getFoodHasCheckedToday
    import time
    from datetime import datetime as date 
    from getScripts import getFood as getFoodRun
    while True:
        #runCacheClearer("./static",30,60) #Starts cache clearer
        
        dayCheck = date.today().strftime("%A")
        if dayCheck != "Monday":
            getFoodHasCheckedToday = False
        if getFoodHasChecked == False or (dayCheck == "Monday" and getFoodHasCheckedToday == False and int(date.today().hour) >= 6):
            getFoodRun(0)
            getFoodHasChecked = True
            getFoodHasCheckedToday = True
        # if (dayCheck == "Monday" and getFoodHasCheckedToday == False and int(date.today().hour) >= 6):
        #     getFoodRun()
        #     getFoodHasChecked = True
        #     getFoodHasCheckedToday = True
                
        time.sleep(60)

# @client.event
# async def on_ready(): 
#     logging.info(f'Logged in as\n{client.user.name}\n{client.user.id}\n------')
#     runWebsite() #Starts website
#     doTimeTasks()

if __name__ == "__main__":
    # try:
    #     os.mkdir("static")
    # except:
    #     pass
    # logging.info("Starting Discord Bot...")
    # client.run(TOKEN)
    runWebsite() #Starts website
    doTimeTasks()