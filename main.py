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
import datetime
import requests
import traceback
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

#region FUNCTIONS
def SetLogging(path="",filename="log.log",format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'):
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
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()
def DecodeString(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)
def GenerateHiddenURL(key,idInput,mainLink):
    a = EncodeString(key,idInput)
    return mainLink + f"?a={a}",a
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
    def __init__(self,lessonName=None,teacherName=None,classroomName=None,timeStart=None,timeEnd=None,insertDict=None):
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
    def GetTimeScore(self,start=True,end=False):
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
    def getData(self):
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
            return None #If ID is not set then it returns None by default
        
        logger.info("Request 1 started")
        #region Request 1
        headers1 = {
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
            "X-Scope": "8a22163c-8662-4535-9050-bc5e1923df48",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://web.skola24.se/timetable/timetable-viewer/it-gymnasiet.skola24.se/IT-Gymnasiet%20S%C3%B6dert%C3%B6rn/",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "en-US;q=0.5",
            "Cookie": "ASP.NET_SessionId=5hgt3njwnabrqso3cujrrj2p"
        }
        url1 = 'https://web.skola24.se/api/encrypt/signature'
        payload1 = {"signature":self._id}
        response1 = requests.post(url1, data=json.dumps(payload1), headers=headers1).text.split('"signature": "')[1].split('"')[0]
        #endregion
        logger.info("Request 1 finished, request 2 started")
        #region Request 2
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
            "Cookie": "ASP.NET_SessionId=5hgt3njwnabrqso3cujrrj2p",
            "Sec-GPC": "1",
            "DNT":"1"
        }
        url2 = 'https://web.skola24.se/api/get/timetable/render/key'
        payload2 = "null"
        response2 = requests.post(url2, data=payload2, headers=headers2).text.split('"key": "')[1].split('"')[0]
        #endregion
        logger.info("Request 2 finished, request 3 started")
        #region Request 3
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
        response3 = json.loads(requests.post(url3, data=json.dumps(payload3), headers=headers3).text)
        #endregion
        logger.info("Request 3 finished")

        if response3 == None:
            logger.info("Response3 is None!")
        return response3
    def CheckIfIDIsValid(self):
        response = self.getData()

        if response['error'] != None:
            # Error -1 : 'error' was not empty
            return -1,response['error']
        if len(response['validation']) != 0:
            # Error -2 : 'validation' was not empty
            return -2,response['validation']
        # If nothing seems to be wrong, it returns code 0 and the response
        return 0,response
    def fetch(self):
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
        response = self.CheckIfIDIsValid()

        if response[0] < 0:
            logger.info('ERROR!',response)
            return []

        if response[1]['data']['lessonInfo'] == None:
            return [] # No lessions this day

        for x in response[1]['data']['lessonInfo']:
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
    def handleHTML(self,classes="", privateID=False):
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
        j = self.getData()

        if len(j['validation']) > 0:
            return {'html':"None"}

        timeTakenToFetchData = time.time()-timeTakenToFetchData
        
        timeTakenToHandleData = time.time() 

        # Start of the SVG
        toReturn.append(f"""<svg id="schedule" class="{classes}" style="width:{self._resolution[0]}; height:{self._resolution[1]};" viewBox="0 0 {self._resolution[0]} {self._resolution[1]}" shape-rendering="crispEdges">""")

        logger.info("Looping through boxList...")
        for current in j['data']['boxList']:
            if current['type'].startswith("ClockFrame"):
                toReturn.append(f"""<rect x="{current['x']}" y="{current['y']}" width="{current['width']}" height="{current['height']}" style="fill:{current['bColor']};"></rect>""")
            else:
                toReturn.append(f"""<rect id="{current['id']}" x="{current['x']}" y="{current['y']}" width="{current['width']}" height="{current['height']}" style="fill:{current['bColor']};stroke:black;stroke-width:1;"></rect>""")

        scriptBuilder = {}
        logger.info("Looping through textList...")
        for current in j['data']['textList']:
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
        for current in j['data']['lineList']:
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
    def GenerateTextSummary(self,mode="normal",lessons=None):
        if lessons == None:lessons = self.fetch()
        if mode == "normal":
            return "\n".join([(f"{x.lessonName} börjar kl {x.timeStart[:-3]} och slutar kl {x.timeEnd[:-3]}" + f" i sal {x.classroomName}" if x.classroomName != None else "") for x in lessons])
        if mode == "discord":
            return "\n".join([(f"**`{x.lessonName}`** börjar kl {x.timeStart[:-3]} och slutar kl {x.timeEnd[:-3]}" + f" i sal {x.classroomName}" if x.classroomName != None else "") for x in lessons])
    def GenerateLessonJSON(self,lessons=None):
        """
            Generates a dict used to create the SIMPLE_JSON API.
            Takes:
                <List> lessons (optional) (If you have allready runned .fetch() then you can simply convert that data to SIMPLE_JSON)
            Returns:
                <Dict> SIMPLE_JSON format
        """
        if lessons == None:lessons = self.fetch()
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
    def HasDayEnded(self,lessons=None):
        if lessons == None:lessons = self.fetch()
        return CurrentTime()['timeScore'] >= lessons[-1].GetTimeScore(end=True)
    # def GetLessonsLeft(self,lessons=None,a=0):
    #     if lessons == None:
    #         lessons = self.fetch()
    #     timeScore = int(f"{self._year}{self._week}{self._day}{CurrentTime()['timeScore']}")
    #     try:
    #         # Mode 1 checks if the last lesson has ended for the day, and if so, it goes to the next day
    #         if a == 1:
    #             if self.HasDayEnded(lessons=lessons):
    #                 self._day += 1
    #                 if self._day > 5:
    #                     self._day = 1
    #                     self._week += 1
    #             else:
    #                 # If the last lession hasnt ended yet, it reuses the lessons data, since it should be identical
    #                 lessons = self.GenerateLessonJSON(lessons=lessons)
    #         # Mode 2 always goes to the next day
    #         if a == 2:
    #             self._day += 1
    #             if self._day > 5:
    #                 self._day = 1
    #                 self._week += 1
    #     except:pass
    #     lessons = self.GenerateLessonJSON()
    #     toReturn = []
    #     for currentLesson in lessons['lessons']:
    #         a = Lesson(insertDict=currentLesson,dateScore=(self._year,self._week,self._day))
    #         b = a.GetTimeScore()
    #         if b > timeScore:
    #             toReturn.append(a)
#endregion

if __name__ == "__main__":
    #region INIT
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s") # Sets default logging settings (before cfg file has been loaded in)

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

        #Logfiles
        Rule('/logfile', endpoint='logfile'),
        Rule('/discord_logfile', endpoint='discord_logfile'),

        #Reserved
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
        if 'daymode' in request.args: # ...or daymode is specified in the URL.
            if str(request.args['daymode']) == "1":
                initDayMode = True
            elif str(request.args['daymode']) == "0":
                initDayMode = False
        if 'debugmode' in request.args:
            if str(request.args['debugmode']) == "1":
                debugmode = True
            elif str(request.args['debugmode']) == "0":
                debugmode = False

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
            initDay=initDay
        )

    # API
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
            return jsonify(result=myRequest.handleHTML(classes=request.args['classes'],privateID=True if request.args['privateID'] == "1" else False))
        else:
            return jsonify(result=myRequest.handleHTML(privateID=True if request.args['privateID'] == "1" else False))
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
                print(1)
                response1 = myRequest.fetch()
        
                temp = response1[len(response1)-1].timeEnd.split(':')
                lessonTimeScore = (int(temp[0]) * 60) + int(temp[1])

                timeScore = (currentTime['hour'] * 60) + currentTime['minute']
                
                if timeScore >= lessonTimeScore:
                    print(11)
                    myRequest._day += 1
                    if myRequest._day > 5:
                        myRequest._day = 1
                        myRequest._week += 1
                else:
                    print(12)
                    # If the last lession hasnt ended yet, it reuses the response1 data, since it should be identical
                    return jsonify(myRequest.GenerateLessonJSON(lessons=response1))
            # Mode 2 always goes to the next day
            if int(request.args['a']) == 2:
                print(2)
                myRequest._day += 1
                if myRequest._day > 5:
                    myRequest._day = 1
                    myRequest._week += 1
        except:pass
        return jsonify(myRequest.GenerateLessonJSON())

    # Logs
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

    app.run(debug=configfile['DEBUGMODE'], host=configfile['ip'], port=configfile['port']) # Run website
else:
    logging.info("main.py was imported")
