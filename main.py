#region ASCII ART
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#               _   _   _                    __            _          _                             #
#              | | | | (_)                  / /           | |        | |                            #
#     __ _  ___| |_| |_ _ _ __ ___   ___   / /__  ___   __| |___  ___| |__   ___ _ __ ___   __ _    #
#    / _` |/ _ \ __| __| | '_ ` _ \ / _ \ / / __|/ _ \ / _` / __|/ __| '_ \ / _ \ '_ ` _ \ / _` |   #
#   | (_| |  __/ |_| |_| | | | | | |  __// /\__ \ (_) | (_| \__ \ (__| | | |  __/ | | | | | (_| |   #
#    \__, |\___|\__|\__|_|_| |_| |_|\___/_/ |___/\___/ \__,_|___/\___|_| |_|\___|_| |_| |_|\__,_|   #
#     __/ |                                                                                         #
#   |___/                                                                                           #
#                                                                                                   #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                                   #
#        Original Idea by PierreLeFevre (https://github.com/PierreLeFevre)                          #
#        Sodschema Sourcecode by PierreLeFevre (https://github.com/PierreLeFevre/sodschema)         #
#        GetTime Classic was made by TayIsAsleep (https://github.com/TayIsAsleep)                   #
#        Sodschema reboot made possible by Koala (https://github.com/KoalaV2)                       #
#                                                                                                   #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#endregion

#region IMPORT
import os
import time
import json
import base64
import logging
import hashlib
import datetime
import requests
import traceback
import threading
import feedparser
from urllib.parse import quote as urlsafe
from operator import attrgetter
from flask import Flask
from flask import Markup
from flask import jsonify
from flask import request
from flask import redirect
from flask import render_template
from flask_cors import CORS
from flask_minify import minify
from flask_mobility import Mobility
from werkzeug.routing import Rule
from werkzeug.exceptions import NotFound
#endregion

#region CACHE SETTINGS
getDataMaxAge = 2*60 # Secounds
getFoodMaxAge = 60*60 # Secounds
dataCache = {}
#endregion

#region FUNCTIONS
def SetLogging(path="", filename="log.log", format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'):
    """
        Changes logging settings.
    """
    open(path+filename, 'w').close() # Clear Logfile
    log = logging.getLogger() # root logger
    for hdlr in log.handlers[:]: # remove all old handlers
        log.removeHandler(hdlr)
    a = logging.FileHandler(path+filename, 'r+', encoding="utf-8")
    a.setFormatter(logging.Formatter(format))
    log.addHandler(a)
def CurrentTime():
    """
        Returns a dictionary with the current time in many different formats.

        Returns:
            dict: (secound, minute, hour, day, week, week2, month, year, weekday, weekday2, datestamp, dayNames)\n
            'weekday2' returns 1-5, but 0 if its Saturday or Sunday.\n
            'week2' returns the current week, but if its Saturday or Sunday, it returns the next week.\n
    """
    #logger = FunctionLogger(functionName='CurrentTime')
    now = datetime.datetime.now()
    a = {
        'secound':now.second,
        'minute':now.minute,
        'hour':now.hour,
        'day':now.day,
        'month':now.month,
        'year':now.year,
        'week':datetime.date.today().isocalendar()[1],
        'weekday':now.isoweekday(),
        'datestamp':datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S'),
        'dayNames':("måndag", "tisdag", "onsdag", "torsdag", "fredag", "lördag", "söndag")
    }
    isSundayOrSaturday = True if a['weekday'] in (6,7) else False
    a['weekday2'] = 0 if isSundayOrSaturday else a['weekday']
    a['weekday3'] = 1 if isSundayOrSaturday else a['weekday']
    a['week2'] = a['week'] + (1 if isSundayOrSaturday else 0)
    a['timeScore'] = (a['hour'] * 60) + a['minute']
    return a
def EncodeString(key, clear):
    # Code from https://stackoverflow.com/a/16321853
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()
def DecodeString(key, enc):
    # Code from https://stackoverflow.com/a/16321853
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)
def GenerateHiddenURL(key, idInput, mainLink):
    a = EncodeString(key,idInput)
    return mainLink + f"?a={a}",a
def sha256(hash_string):
    # Code from https://tinyurl.com/2k3ds62p
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature
def arg01_to_bool(args,argName):
    """
        This function takes {request.args} and check if the argName is 1 or 2.\n
        If argName is "1", it returns True.\n
        If argname is "0", it returns False.\n
        And if it is anything else, or if it does not exist, it returns False aswell.
    """
    if str(argName) in args:
        if str(args[str(argName)]) == "1":
            return True
        if str(args[str(argName)]) == "0":
            return False
    return False
def GetFood(allowCache=True,week=None):
    t = CurrentTime()
    week = week if week != None else t['week']
    myHash = sha256(f"{week}{t['week']}")

    if allowCache and myHash in dataCache and time.time() - dataCache[myHash]['age'] < dataCache[myHash]['maxage']:
        toReturn = dataCache[myHash]['data']
    else:
        NewsFeed = feedparser.parse("https://skolmaten.se/nti-gymnasiet-sodertorn/rss/weeks/?offset=" + str(week - t['week']))
        
        toReturn = {"data":{"food":[],"week":week if week != None else t['week']}}
        
        for x in range(5):
            try:
                post = NewsFeed.entries[x]

                temp = post.summary.split("<br />") # This might break in the future
                toReturn['data']['food'].append({'regular':temp[0],'veg':temp[1]})
                toReturn['data']['week'] = int(post.title.split(" ")[3]) # This might break in the future
            except:pass

    if allowCache:
        dataCache[myHash] = {'maxage':getFoodMaxAge,'age':time.time(),'data':toReturn}
    return toReturn
#endregion

#region CLASSES
class FunctionLogger:
    """
        Object that helps make logfiles slightly easier to read\n
        In the beginning of a function you create a FunctionLogger object\n
        with "functionName" set to whatever name the function is.\n
        Then you log like normal, but instead of using logging.info(), you use FunctionLogger.info()
    """
    def __init__(self,functionName):
        self.functionName = functionName
        logging.info(f"{self.functionName} : FunctionLogger Object created.")
    def info(self,*message):
        message = [str(x) for x in message]
        logging.info(f"{self.functionName}() : {str(' '.join(message))}")
    def exception(self,*message):
        message = [str(x) for x in message]
        logging.exception(f"{self.functionName}() : {str(' '.join(message))}")
class Lesson:
    def __init__(self, lessonName=None, teacherName=None, classroomName=None, timeStart=None, timeEnd=None, insertDict=None):
        if insertDict != None:
            self.lessonName = insertDict['lessonName']
            self.teacherName = insertDict['teacherName']
            self.classroomName = insertDict['classroomName']
            self.timeStart = insertDict['timeStart']
            self.timeEnd = insertDict['timeEnd']
        else:
            self.lessonName = lessonName
            self.teacherName = teacherName
            self.classroomName = classroomName
            self.timeStart = timeStart
            self.timeEnd = timeEnd
    def GetTimeScore(self, start=True, end=False):
        if end == True:start = False
        #KNOWN ISSUE: 
        #If time is 23:00, and you try and get timescore for a lesson that starts 01:00 the next day, it will not return 2 hours
        #This is because timescore does not care about dates, only hours and minutes
        
        secounds = sum(x * int(t) for x, t in zip([1, 60, 3600], reversed((self.timeStart if start else self.timeEnd).split(":"))))
        return int(secounds / 60)       
class GetTime:
    """
        GetTime Request object
    """
    t = CurrentTime()
    def __init__(self, _id=None, _week=t['week2'], _day=t['weekday2'], _year=t['year'], _resolution=(1280,720)):
        self._id = _id
        self._week = _week
        self._day = _day
        self._year = _year
        self._resolution = _resolution
    def getHash(self):
        return sha256("".join([str(x) for x in (self._id,self._week,self._day,self._year,self._resolution)]))
    def getData(self, allowCache=True):
        """
            This function makes a request to Skola24's servers and returns the schedule data
            \n
            Takes:
                None
            Returns:
                <JSON> object with the data inside
        """
        logger = FunctionLogger(functionName='GetTime.getData')

        if self._id == None:
            logger.info("Returning None because _id was None")
            return {"status":-7,"message":"_id was None (No ID specified)","data":None} #If ID is not set then it returns None by default
        
        myHash = self.getHash()
        if allowCache and myHash in dataCache and time.time() - dataCache[myHash]['age'] < dataCache[myHash]['maxage']:
            logger.info("Using cache!")
            toReturn = dataCache[myHash]['data']
        else:
            #region Request 1
            logger.info("Request 1")
            headers1 = {
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
                "X-Scope": "8a22163c-8662-4535-9050-bc5e1923df48",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Referer": "https://web.skola24.se/timetable/timetable-viewer/it-gymnasiet.skola24.se/IT-Gymnasiet%20S%C3%B6dert%C3%B6rn/",
                #"Referer": f"https://web.skola24.se/timetable/timetable-viewer/it-gymnasiet.skola24.se/{urlsafe(testSchool[3])}/",
                "Accept-Encoding": "gzip,deflate",
                "Accept-Language": "en-US;q=0.5",
                "Cookie": "ASP.NET_SessionId=5hgt3njwnabrqso3cujrrj2p"
            }
            url1 = 'https://web.skola24.se/api/encrypt/signature'
            payload1 = {"signature":self._id}
            response1 = requests.post(url1, data=json.dumps(payload1), headers=headers1)
            try:response1 = json.loads(response1.text)['data']['signature']
            except:return {"status":-2,"message":"Response 1 Error","data":response1}
            #endregion
            #region Request 2
            logger.info("Request 2")
            headers2 = {
                "Host": "web.skola24.se",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Content-Type": "application/json",
                "X-Scope": "8a22163c-8662-4535-9050-bc5e1923df48",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Length": "4",
                "Origin": "https://web.skola24.se",
                "Connection": "close",
                "Referer": "https://web.skola24.se/timetable/timetable-viewer/it-gymnasiet.skola24.se/IT-Gymnasiet%20S%C3%B6dert%C3%B6rn/",
                #"Referer": f"https://web.skola24.se/timetable/timetable-viewer/it-gymnasiet.skola24.se/{urlsafe(testSchool[3])}/",
                "Cookie": "ASP.NET_SessionId=5hgt3njwnabrqso3cujrrj2p",
                "Sec-GPC": "1",
                "DNT":"1"
            }
            url2 = 'https://web.skola24.se/api/get/timetable/render/key'
            payload2 = "null"
            response2 = requests.post(url2, data=payload2, headers=headers2)
            try:response2 = json.loads(response2.text)['data']['key']
            except:return {"status":-3,"message":"Response 2 Error","data":response2}
            #endregion
            #region Request 3
            logger.info("Request 3")
            headers3 = headers2
            url3 = 'https://web.skola24.se/api/render/timetable'
            payload3 = {
                "renderKey":response2,
                "host":"it-gymnasiet.skola24.se",
                "unitGuid":"ZTEyNTdlZjItZDc3OC1mZWJkLThiYmEtOGYyZDA4NGU1YjI2",
                "startDate":"null",
                "endDate":"null",
                "scheduleDay":int(self._day),
                "blackAndWhite":"false",
                "width":int(self._resolution[0]),
                "height":int(self._resolution[1]),
                "selectionType":4,
                "selection":response1,
                "showHeader":"false",
                "periodText":"",
                "week":int(self._week),
                "year":int(self._year),
                "privateFreeTextMode":"false",
                "privateSelectionMode":"null",
                "customerKey":""
            }
            response3 = requests.post(url3, data=json.dumps(payload3), headers=headers3)
            try:response3 = json.loads(response3.text)
            except:return {"status":-4,"message":"Response 3 Error","data":response3}
            #endregion
            toReturn = {"status":0,"message":"OK","data":response3}
            
            logger.info("Request 3 is finished. Will now check for errors")
            #Error Checking
            try:
                if response3['error'] != None:
                    toReturn = {'status':-5,'message':"error was not None","data":response3}
                if len(response3['validation']) != 0:
                    toReturn = {'status':-6,'message':"validation was not empty : " + ','.join([x['message'] for x in response3['validation']]),"data":response3,"validation":response3['validation']}
            except:
                toReturn = {'status':-8,'message':f"An error occured when trying to check for other errors! Here is the traceback : {traceback.format_exc()}","data":response3}
            
            if allowCache:
                dataCache[myHash] = {'maxage':getDataMaxAge,'age':time.time(),'data':toReturn}
        return toReturn
    def fetch(self, allowCache=True):
        """
            Fetches and formats data into <lesson> objects.
            \n
            Takes:
                None
            Returns:
                List with <lesson> objects
        """
        logger = FunctionLogger(functionName='GetTime.fetch')
        toReturn = []
        response = self.getData(allowCache=allowCache)
        if response['status'] < 0:
            logger.info('ERROR!',response)
            return response

        if response['data']['data']['lessonInfo'] == None:
            return [] # No lessions this day

        for x in response['data']['data']['lessonInfo']:
            currentLesson = Lesson(
                lessonName=x['texts'][0],
                teacherName=x['texts'][1],
                timeStart=x['timeStart'],
                timeEnd=x['timeEnd']
            ) 
            #Sometimes the classroomName is absent
            try:currentLesson.classroomName = x['texts'][2]
            except:currentLesson.classroomName = ""
            toReturn.append(currentLesson)
        toReturn.sort(key=attrgetter('timeStart'))
        return toReturn
    def handleHTML(self, classes="", privateID=False, allowCache=True):
        """
            Fetches and converts the <JSON> data into a SVG (for sending to HTML)
            \n
            Takes:
                classes (optional) (add custom classes to the SVG)
            Returns:
                {'html':(SVG HTML CODE),'timestamp':timeStamp}
        """
        logger = FunctionLogger(functionName='GetTime.handleHTML')

        toReturn = []
        timeTakenToFetchData = time.time()
        j = self.getData(allowCache=allowCache)
        
        if j['status'] < 0:
            return {'html':"""<div id="schedule" style="all: initial;*{all:unset;}">""" + f"""<p style="color:white">{j['message']}</p>""" + j['data'].text + "</div>"}

        timeTakenToFetchData = time.time()-timeTakenToFetchData
        
        timeTakenToHandleData = time.time() 
         
        #_id="{EncodeString(configfile['key'],self._id)}" _week="{self._week}" _day="{self._day}" _resolution="{self._resolution}" class="{classes}"
        # Start of the SVG 
        toReturn.append(f"""<svg id="schedule" class="{classes}" style="width:{self._resolution[0]}; height:{self._resolution[1]};" viewBox="0 0 {self._resolution[0]} {self._resolution[1]}" shape-rendering="crispEdges">""")

        logger.info("Looping through boxList...")
        for current in j['data']['data']['boxList']:
            if current['type'].startswith("ClockFrame"):
                toReturn.append(f"""<rect x="{current['x']}" y="{current['y']}" width="{current['width']}" height="{current['height']}" style="fill:{current['bColor']};"></rect>""")
            else:
                toReturn.append(f"""<rect id="{current['id']}" x="{current['x']}" y="{current['y']}" width="{current['width']}" height="{current['height']}" style="fill:{current['bColor']};stroke:black;stroke-width:1;"></rect>""")

        scriptBuilder = {}
        logger.info("Looping through textList...")
        for current in j['data']['data']['textList']:
            if current['text'] != "":
                # If the text is of a Lession type, that means that it sits ontop of a block that the user should be able to click to set a URL.
                # This only happens if privateID is false, because if the ID is private, it doesnt add the scripts anyways, so why bother generating them in the first place?
                if privateID == False and current['type'] == "Lesson":

                    # If the key does not exist yet, it creates an empty list for it
                    if not current['parentId'] in scriptBuilder:
                        scriptBuilder[current['parentId']] = []
                    
                    # Only takes the first 2 arguments (skips the 3rd, aka classroom name)
                    if len(scriptBuilder[current['parentId']]) <= 1:
                        scriptBuilder[current['parentId']].append(str(current['text'])) 
                
                # Adds text object to list
                toReturn.append(f"""<text x="{current['x']}" y="{current['y']+12}" style="font-size:{int(current['fontsize'])}px;fill:{current['fColor']};">{current['text']}</text>""")

        logger.info("Looping through lineList...")
        for current in j['data']['data']['lineList']:
            x1,x2=current['p1x'],current['p2x']
            # Checks delta lenght and skips those smalled then 10px
            if int(x1-x2 if x1>x2 else x2-x1) > 10:
                toReturn.append(f"""<line x1="{current['p1x']}" y1="{current['p1y']}" x2="{current['p2x']}" y2="{current['p2y']}" stroke="{current['color']}"></line>""")
        
        # Add the scripts to a rect so that they can be ran after the schedule has loaded (Skips this when ID is hidden)
        if privateID == False:
            scriptsToRun = [f"""checkMyUrl('{x}','{"_".join(scriptBuilder[x])}');""" for x in scriptBuilder] # Loops through the ids, and creates scripts for them
            toReturn.append(f'<rect id="scheduleScript" style="display: none;" script="{"".join(scriptsToRun)}"></rect>')
        
        timeTakenToHandleData = time.time() - timeTakenToHandleData

        # Comments 
        toReturn.append("<!-- THIS SCHEDULE WAS MADE POSSIBLE BY https://github.com/KoalaV2 -->")
        toReturn.append(f"<!-- SETTINGS USED: id: {'[HIDDEN]' if privateID else self._id}, week: {self._week}, day: {self._day}, resolution: {self._resolution}, class: {classes} -->")
        toReturn.append(f"<!-- Time taken (Requesting data): {timeTakenToFetchData} secounds -->")
        toReturn.append(f"<!-- Time taken (Schedule generation): {timeTakenToHandleData} secounds -->")
        toReturn.append(f"<!-- Time taken (TOTAL): {(timeTakenToFetchData + timeTakenToHandleData)} secounds -->")
        
        # End of the SVG
        toReturn.append("</svg>")

        return {'html':"\n".join(toReturn)}
    def GenerateTextSummary(self, mode="normal", lessons=None, allowCache=True):
        if lessons == None:lessons = self.fetch(allowCache=allowCache)
        try:
            if lessons[0] < 0:return str(lessons[1])
        except:pass
        if mode == "normal":
            return "\n".join([(f"{x.lessonName} börjar kl {x.timeStart[:-3]} och slutar kl {x.timeEnd[:-3]}" + f" i sal {x.classroomName}" if x.classroomName != None else "") for x in lessons])
        if mode == "discord":
            return "\n".join([(f"**`{x.lessonName}`** börjar kl {x.timeStart[:-3]} och slutar kl {x.timeEnd[:-3]}" + f" i sal {x.classroomName}" if x.classroomName != None else "") for x in lessons])
    def GenerateLessonJSON(self, lessons=None, allowCache=True):
        """
            Generates a dict used to create the SIMPLE_JSON API.
            Takes:
                <List> lessons (optional) (If you have allready runned .fetch() then you can simply convert that data to SIMPLE_JSON)
            Returns:
                <Dict> SIMPLE_JSON format
        """
        if lessons == None:lessons = self.fetch(allowCache=allowCache)

        try:
            if lessons['status'] < 0:return lessons
        except:pass
        lessons.sort(key=attrgetter('timeStart'))
        return{
            'id':self._id,
            'week':self._week,
            'day':self._day,
            'year':self._year,
            'lessons':[
                {'lessonName':x.lessonName,
                'teacherName':x.teacherName,
                'classroomName':x.classroomName,
                'timeStart':x.timeStart,
                'timeEnd':x.timeEnd
                }for x in lessons
            ]
        }
    def GetFood(self, allowCache=True):
        return GetFood(allowCache=allowCache,week=self._week)
#endregion

if __name__ == "__main__":
    
    #region INIT
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s") # Sets default logging settings (before cfg file has been loaded in)

    os.chdir(os.path.dirname(os.path.realpath(__file__))) # Set working dir to path of main.py

    # Load config file
    with open("settings.json") as f:
        try:configfile = json.load(f)
        except:configfile = {}

    # Change logging to go to file
    if configfile['logToFile']:
        if configfile['logToSameFile']:
            logFileName = "logfile.log"
        else:
            logFileName = f"logfile_{CurrentTime()['datestamp']}.log"
        logFileLocation = configfile['logFileLocation']
        logging.info(f"From now on, logs will be found at '{logFileLocation+logFileName}'")
        SetLogging(path=logFileLocation,filename=logFileName)
    else:
        logging.info("From now on, logging will continue in the console.")

    # Setup Flask
    app = Flask(__name__)
    minify(app=app, html=True, js=False, cssless=True)
    Mobility(app) # Mobile features
    CORS(app) # Behövs så att man kan skicka requests till serven (for some reason idk)
    #endregion
    
    #region FLASK ROUTES
    [app.url_map.add(x) for x in (
        #INDEX
        Rule('/', endpoint='index'),

        #API
        Rule('/API/QR_CODE', endpoint='API_QR_CODE'),
        Rule('/API/SHAREABLE_URL', endpoint='API_SHAREABLE_URL'),
        Rule('/API/GENERATE_HTML', endpoint='API_GENERATE_HTML'),
        Rule('/API/JSON', endpoint='API_JSON'),
        Rule('/API/SIMPLE_JSON', endpoint='API_SIMPLE_JSON'),
        Rule('/API/TERMINAL_SCHEDULE', endpoint='API_TERMINAL_SCHEDULE'),
        Rule('/API/FOOD', endpoint='API_FOOD'),

        #Logfiles
        Rule('/logfile', endpoint='logfile'),
        Rule('/discord_logfile', endpoint='discord_logfile'),

        #Reserved
        Rule('/contact', endpoint='contact'),
        Rule('/theo', endpoint='TheoCredit'),
        Rule('/pierre', endpoint='PierreCredit'),
        Rule('/ඞ', endpoint='ඞ'),

        # Obsolete/Old formats
        Rule('/terminal/schedule', endpoint='API_TERMINAL_SCHEDULE'),
        Rule('/terminal/getall', endpoint='API_JSON'),
        Rule('/script/API_SHAREABLE_URL', endpoint='API_SHAREABLE_URL'),
        Rule('/script/API_GENERATE_HTML', endpoint='API_GENERATE_HTML'),
        Rule('/api/json', endpoint='API_JSON')
    )]

    #region Error handling and cache settings
    @app.after_request # Script to help prevent caching
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response
    @app.errorhandler(NotFound)
    def handle_bad_request_404(e):
        return e,404
    @app.errorhandler(Exception)
    def handle_bad_request(e):
        if configfile['enableErrorHandler']:
            logging.exception(f"This is the error : {e}")
            errorMessage = []
            try:
                #errorMessage.append(f"URL : {request.url}") # Sometimes leaked server IP
                errorMessage.append(f"TIME OF ERROR : {CurrentTime()['datestamp']}")
                errorMessage.append("") # End of special parameters, next is traceback
            except:errorMessage.append("SOMETHING ELSE FAILED TOO")
            errorMessage.append(traceback.format_exc())
            return render_template('error.html',message="\n".join(errorMessage))
        else:
            raise e
    #endregion

    # INDEX
    @app.endpoint('index')
    def index():
        logger = FunctionLogger(functionName='index')

        # Default values
        t = CurrentTime()
        initID = ""
        initDayMode = False
        initWeek = t['week2']
        initDay = t['weekday3']
        debugmode = False
        privateURL = False
        saveIdToCookie = True
        mobileRequest = request.MOBILE
        
        # Check parameters
        if 'id' in request.args:
            initID = request.args['id']
            saveIdToCookie = False
            logger.info(f"Custom ID argument found ({initID})")
        if 'a' in request.args:
            initID = DecodeString(configfile['key'],request.args['a'])
            privateURL = True
            saveIdToCookie = False
            logger.info(f"Custom Encoded ID argument found ({initID})")
        if 'week' in request.args:
            try:initWeek = int(request.args['week'])
            except:pass
        initDayMode = mobileRequest # initDayMode is True by default if the request is a mobile request unless...
        if 'day' in request.args:
            try:
                initDay = int(request.args['day'])
                initDayMode = True # ...day is specified...
            except:pass
        if 'daymode' in request.args: 
            initDayMode = arg01_to_bool(request.args,"daymode") # ...or daymode is specified in the URL.
        debugmode = arg01_to_bool(request.args,"debugmode")

        credit = [
            {
                'name':'Isak Karlsen (19_tek_a)',
                'email':'isak@gettime.ga',
                'links':[
                    ('GitHub','https://github.com/TayIsAsleep')
                ]
            },
            {
                'name':'Theodor Johanson (20_el_a)',
                'email':'theo@gettime.ga',
                'links':[
                    ('GitHub','https://github.com/KoalaV2')
                ]
            },
            {
                'name':'Pierre Le Fevre',
                'email':'pierre@gettime.ga',
                'links':[
                    ('GitHub','https://github.com/PierreLeFevre')
                ]
            }
        ]


        return render_template(
            template_name_or_list="sodschema.html",
            parseCode="",
            requestURL=configfile['mainLink'],
            privateURL=privateURL,
            saveIdToCookie=saveIdToCookie,
            mobileRequest=mobileRequest,
            debugmode=debugmode,
            initID=initID,
            initDayMode=initDayMode,
            initWeek=initWeek,
            initDay=initDay,
            credit=credit
        )

    #region API
    @app.endpoint('API_QR_CODE')
    def API_QR_CODE():
        return render_template(
            'qrCodeTemplate.html',
            requestURL=configfile['mainLink'],
            passedID=None if not 'id' in request.args else request.args['id'],
            privateID=False if not 'p' in request.args else (True if str(request.args['p']) == "1" else False)
        )
    @app.endpoint('API_SHAREABLE_URL')
    def API_SHAREABLE_URL():
        global configfile
        a = GenerateHiddenURL(configfile['key'],request.args['id'],configfile['mainLink'])
        return jsonify(result={'url':a[0],'id':a[1]})
    @app.endpoint('API_GENERATE_HTML')
    def API_GENERATE_HTML():
        #logger = FunctionLogger(functionName='API_GENERATE_HTML')
        # This function generates the finished HTML code for the schedule (Used by the website to generate the image you see)
        myRequest = GetTime(
            _id = request.args['id'],
            _week = int(request.args['week']),
            _day = int(request.args['day']),
            _resolution = (int(request.args['width']),int(request.args['height']))
        )
        if 'classes' in request.args: 
            return jsonify(result=myRequest.handleHTML(classes=request.args['classes'],privateID=arg01_to_bool(request.args,"privateID")))
        else:
            return jsonify(result=myRequest.handleHTML(privateID=arg01_to_bool(request.args,"privateID")))
        #return jsonify(result=result) #.headers.add('Access-Control-Allow-Origin', '*')  
    @app.endpoint('API_JSON')
    def API_JSON():
        #logger = FunctionLogger(functionName='API_JSON')

        # Custom API (gets the whole JSON file for the user to mess with)
        # This is what the Skola24 website seems to get.
        # It contains all the info you need to rebuild the schedule image.

        myRequest = GetTime()
        try:myRequest._id = request.args['id']
        except:raise
        try:myRequest._week = request.args['week']
        except:pass
        try:myRequest._day = request.args['day']
        except:pass
        try:myRequest._resolution = request.args['res'].split(",")
        except:pass
        return jsonify(myRequest.getData())
    @app.endpoint('API_SIMPLE_JSON')
    def API_SIMPLE_JSON():
        myRequest = GetTime()
        currentTime = CurrentTime()

        try:myRequest._id = request.args['id']
        except:raise
        try:myRequest._week = int(request.args['week'])
        except:myRequest._week = currentTime['week2']
        try:myRequest._day = int(request.args['day'])
        except:myRequest._day = currentTime['weekday3']

        try:
            # Mode 1 checks if the last lesson has ended for the day, and if so, it goes to the next day
            if int(request.args['a']) == 1:
                response1 = myRequest.fetch()
                try:
                    if response1[0] < 0:
                        return jsonify({"error":response1})
                except:pass
        
                temp = response1[len(response1)-1].timeEnd.split(':')
                lessonTimeScore = (int(temp[0]) * 60) + int(temp[1])

                timeScore = (currentTime['hour'] * 60) + currentTime['minute']
                
                if timeScore >= lessonTimeScore:
                    myRequest._day += 1
                    if myRequest._day > 5:
                        myRequest._day = 1
                        myRequest._week += 1
                else:
                    # If the last lession hasnt ended yet, it reuses the response1 data, since it should be identical
                    return jsonify(myRequest.GenerateLessonJSON(lessons=response1))
            # Mode 2 always goes to the next day
            if int(request.args['a']) == 2:
                myRequest._day += 1
                if myRequest._day > 5:
                    myRequest._day = 1
                    myRequest._week += 1
        except:pass
        return jsonify(myRequest.GenerateLessonJSON())
    @app.endpoint('API_TERMINAL_SCHEDULE')
    def API_TERMINAL_SCHEDULE():
        myRequest = GetTime()
        currentTime = CurrentTime()

        try:myRequest._id = request.args['id']
        except:raise
        try:myRequest._week = int(request.args['week'])
        except:myRequest._week = currentTime['week2']
        try:myRequest._day = int(request.args['day'])
        except:myRequest._day = currentTime['weekday3']

        
        if arg01_to_bool(request.args,"text"):
            return myRequest.GenerateTextSummary()
        return jsonify({'result':myRequest.GenerateTextSummary()})
    @app.endpoint('API_FOOD')
    def API_FOOD():
        if 'week' in request.args:
            week = int(request.args['week'])
        else:
            week = None
        
        return GetFood(week=week)
    #endregion

    #region Logs
    @app.endpoint('logfile')
    def logfile():
        #logger = FunctionLogger(functionName='logfile')
        if request.args['key'] == configfile['key']:
            with open(logFileLocation+logFileName,"r") as f:
                return f"<pre>{logFileLocation+logFileName}</pre><pre>{''.join(f.readlines())}</pre>"
    @app.endpoint('discord_logfile')
    def discord_logfile():
        #logger = FunctionLogger(functionName='discord_logfile')
        if request.args['key'] == configfile['key']:
            with open(logFileLocation+'discord_logfile.log',"r") as f:
                return f"<pre>{logFileLocation+logFileName}</pre><pre>{''.join(f.readlines())}</pre>"
    #endregion
    
    # Special easter egg URL's for the creators/contributors AND AMOGUS ඞ
    @app.endpoint('TheoCredit')
    def TheoCredit():
        return redirect('https://koalathe.dev/')
    @app.endpoint('PierreCredit')
    def PierreCredit():
        return redirect('https://github.com/PierreLeFevre')
    @app.endpoint('ඞ')
    def ඞ():
        return render_template('AmongUs.html')

    # Redirects (For dead links)
    @app.route("/schema/<a>")
    @app.route("/schema/")
    @app.route("/schema")
    def routeToIndex(**a):
        logger = FunctionLogger(functionName='routeToIndex')
        logger.info(f"routeToIndex : Request landed in the redirects, sending to mainLink ({configfile['mainLink']})")
        return redirect(configfile['mainLink'])
    #endregion
    
    def cacheClearer():
        logger = FunctionLogger('cacheClearer')
        while 1:
            try:
                toDelete = []
                for x in dataCache:
                    if time.time() - dataCache[x]['age'] > dataCache[x]['maxage']:
                        toDelete.append(x)
                for x in toDelete:
                    logger.info(f"Deleting {x} from cache")
                    del dataCache[x]
            except RuntimeError as e:
                logger.info(e)
                pass
            except:
                logger.exception(traceback.format_exc())
                pass
            time.sleep(1)

    threading.Thread(target=cacheClearer, args=(), daemon=True).start()
    app.run(debug=configfile['DEBUGMODE'], host=configfile['ip'], port=configfile['port']) # Run website
else:
    logging.info("main.py was imported")
