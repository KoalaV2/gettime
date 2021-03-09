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
#   Original Idea by PierreLeFevre (https://github.com/PierreLeFevre)                               #
#   Sodschema Sourcecode by PierreLeFevre (https://github.com/PierreLeFevre/sodschema)              #
#   GetTime Classic was made by TayIsAsleep (https://github.com/TayIsAsleep)                        #
#   Sodschema reboot made possible by Koala (https://github.com/KoalaV2)                            #
#                                                                                                   #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#region IMPORT
# NewGetTime Requirements:
import json
import requests

# Flask Requirements:
from flask import Flask
from flask import Markup
from flask import jsonify
from flask import request
from flask import redirect
import werkzeug.exceptions
from flask_cors import CORS
from flask_minify import minify
from werkzeug.routing import Rule
from flask import render_template
from flask_mobility import Mobility

# Other Requirements:
import os
import time
import traceback
import datetime
import logging ; logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s") #Default settings (before cfg file has been loaded in)
def setLogging(path="",filename="log.log",format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'):
    """
        Changes logging settings.
    """
    log = logging.getLogger()  # root logger
    for hdlr in log.handlers[:]:  # remove all old handlers
        log.removeHandler(hdlr)    
    a = logging.FileHandler(path+filename, 'a')
    a.setFormatter(logging.Formatter(format))
    log.addHandler(a)
#endregion

#region FUNCTIONS
def loadConfigfile(configFileName):
    """
        Loads the config.cfg file into a dict.\n
        Anything in quotes will always be converted into a string.\n
        true/True and false/False will be converted into a bool.\n
        Any number with , or . will be converted into a float.\n

        Args:
            configFileName (string): Path and name of configfile

        Returns:
            dict: all the config settings
    """
    logger = functionLogger(functionName='loadConfigfile')
    cfg = {}
    try:
        logger.info(f"Loading configfile... ({configFileName})")
        with open(configFileName,'r') as f:
            for x in f.readlines():
                a,b = x.strip('\n').split(" = ")
                
                # Checks if value is specified as string
                if (b.startswith('"') and b.endswith('"')) or (b.startswith("'") and b.endswith("'")):
                    cfg[a] = b[1:-1]
                    logger.info(f"Converted '{b}' into a string and saved to '{a}'")
                    continue

                # Checks if value is true or false
                if b.lower() == "true":
                    cfg[a] = True
                    logger.info(f"Converted '{b}' into a bool and saved to '{a}'")
                    continue
                if b.lower() == "false":
                    cfg[a] = False
                    logger.info(f"Converted '{b}' into a bool and saved to '{a}'")
                    continue
                
                # Checks if value is float
                try:
                    if "," in b or "." in b:
                        cfg[a] = float(b)
                        logger.info(f"Converted '{b}' into a float and saved to '{a}'")
                        continue
                except:
                    logger.info(f"Tried to convert '{b}' into a float, but failed.")
                    pass
                
                # Checks if value is INT
                try:
                    cfg[a] = int(b)
                    logger.info(f"Converted '{b}' into a int and saved to '{a}'")
                    continue

                # If not, saves it as string
                except:
                    cfg[a] = b
                    logger.info(f"Nothing else worked, so converted '{b}' into a string and saved to '{a}'")
                    continue
    except Exception as e:logger.exception(e);pass
    return cfg
def currentTime():
    """
        Returns a dictionary with the current time in many different formats.

        Returns:
            dict: (secound, minute, hour, day, week, month, year, weekday)
    """
    logger = functionLogger(functionName='currentTime')
    now = datetime.datetime.now() 
    return {
        'secound':now.second,
        'minute':now.minute,
        'hour':now.hour,
        'day':now.day,
        'month':now.month,
        'year':now.year,
        'week':datetime.date.today().isocalendar()[1],
        'weekday':now.weekday(),
        'datestamp':datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    }
#endregion

#region CLASSES
class functionLogger:
    def __init__(self,functionName):
        self.functionName = functionName
    def info(self,*message):
        message = [str(x) for x in message]
        logging.info(f"{self.functionName}() : {str(' '.join(message))}")
    def exception(self,*message):
        message = [str(x) for x in message]
        logging.exception(f"{self.functionName}() : {str(' '.join(message))}")
class Lesson:
    def __init__(self,lessionName,teacherName,classroomName,timeStart,timeEnd,dayOfWeekNumber):
        self.lessionName = lessionName
        self.teacherName = teacherName
        self.classroomName = classroomName
        self.timeStart = timeStart
        self.timeEnd = timeEnd
        self.dayOfWeekNumber = dayOfWeekNumber
class GetTime:
    """
        GetTime Request object
    """
    def __init__(self,_id=None,_week=currentTime()['week'],_day=0,_year=currentTime()['year'],_resolution=(1280,720)):
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
        logger = functionLogger(functionName='GetTime.getData')
        if self._id == None:
            return None #If ID is not set then it returns 0 by default
        
        #region Request 1
        logger.info("Request 1 started")
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
        logger.info("Request 1 finished")
        #endregion
        #region Request 2
        logger.info("Request 2 started")
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
        logger.info("Request 2 finished")
        #endregion
        #region Request 1
        logger.info("Request 3 started")
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
        logger.info("Request 3 finished")

        #logger.info(f"Response 1: {response1}")
        #logger.info(f"Response 2: {response2}")
        #logger.info(f"Response 3: {response3}")
        
        #endregion
        return response3
    def fetch(self):
        """
            Fetches and formats data into <Lession> objects.
            \n
            Takes:
                None
            Returns:
                List with <Lession> objects
        """
        logger = functionLogger(functionName='GetTime.fetch')
        result = self.getData()
        toReturn = []
        for x in result['data']['lessonInfo']:
            currentLesson = Lesson(
                x['texts'][0],
                x['texts'][1],
                None,
                x['timeStart'],
                x['timeEnd'],
                x['dayOfWeekNumber']
            ) 
            #Sometimes the classroomName is absent
            try:currentLesson.classroomName = x['texts'][2]
            except:currentLesson.classroomName = ""
            toReturn.append(currentLesson)
        return toReturn
    def handleHTML(self,classes=""):
        """
            Fetches and converts the <JSON> data into a SVG (for sending to HTML)
            \n
            Takes:
                classes (optional) (add custom classes to the SVG)
            Returns:
                {'html':(SVG HTML CODE),'timestamp':timeStamp}
        """
        logger = functionLogger(functionName='GetTime.handleHTML')
        timeStamp = time.time()
        toReturn = []
        scriptsToRun = []
        timeTakenToFetchData = time.time() #This value should contain when the request was recieved by the server
        j = self.getData()['data']
        timeTakenToFetchData = time.time()-timeTakenToFetchData
        
        timeTakenToHandleData = time.time() 

        #Start of the SVG
        toReturn.append(f"""<svg id="schedule" class="{classes}" style="width:{self._resolution[0]}; height:{self._resolution[1]};" viewBox="0 0 {self._resolution[0]} {self._resolution[1]}" shape-rendering="crispEdges">""")

        logger.info("Looping through boxList...")
        for current in j['boxList']:
            #toReturn.append(f"""<rect {("".join([f'{str(key)}="{str(current[key])}" ' for key in [key for key in current]]))}></rect>""")
            if current['type'].startswith("ClockFrame"):
                toReturn.append(f"""<rect x="{current['x']}" y="{current['y']}" width="{current['width']}" height="{current['height']}" style="fill:{current['bColor']};"></rect>""")
            else:
                toReturn.append(f"""<rect id="{current['id']}" x="{current['x']}" y="{current['y']}" width="{current['width']}" height="{current['height']}" style="fill:{current['bColor']};stroke:black;stroke-width:1;"></rect>""")

        scriptBuilder = {}

        #parentIdsSaved = [] #This saves the parentID when the first value has been read (value 1 is the lession name, value 2 is teacher name and value 3 is classroom name, we want value 1, but 2 and 3 overwrite 1)
        logger.info("Looping through textList...")
        for current in j['textList']:
            if current['text'] != "":
                if current['type'] == "Lesson":

                    # If the key does not exist yet, it creates an empty list for it
                    if not current['parentId'] in scriptBuilder:
                        scriptBuilder[current['parentId']] = []
                    
                    # Only takes the first 2 arguments (skips the 3rd, aka classroom name)
                    if len(scriptBuilder[current['parentId']]) <= 1:
                        scriptBuilder[current['parentId']].append(str(current['text'])) 
                    
                toReturn.append(f"""<text x="{current['x']}" y="{current['y']+12}" style="font-size:{int(current['fontsize'])}px;fill:{current['fColor']};">{current['text']}</text>""")

        # Loops through the ids, and creates scripts for them
        for x in scriptBuilder:
            scriptsToRun.append(f"""checkMyUrl('{x}','{"_".join(scriptBuilder[x])}');""") # Saves the check script for later


        logger.info("Looping through lineList...")
        for current in j['lineList']:
            x1,x2=current['p1x'],current['p2x']
            #Checks delta lenght and skips those smalled then 10px
            if int(x1-x2 if x1>x2 else x2-x1) > 10:
                toReturn.append(f"""<line x1="{current['p1x']}" y1="{current['p1y']}" x2="{current['p2x']}" y2="{current['p2y']}" stroke="{current['color']}"></line>""")
        timeTakenToHandleData = time.time() - timeTakenToHandleData

        # Add the scripts to a rect so that they can be ran after the schedule has loaded
        toReturn.append(f'<rect id="scheduleScript" style="display: none;" script="{"".join(scriptsToRun)}"></rect>')
        toReturn.append("<!-- THIS SCHEDULE WAS MADE POSSIBLE BY https://github.com/KoalaV2 -->")
        toReturn.append(f"<!-- SETTINGS USED: id: {self._id}, week: {self._week}, day: {self._day}, resolution: {self._resolution}, class: {classes} -->")
        toReturn.append(f"<!-- Time taken (Requesting data): {timeTakenToFetchData} secounds -->")
        toReturn.append(f"<!-- Time taken (Schedule generation): {timeTakenToHandleData} secounds -->")
        toReturn.append(f"<!-- Time taken (TOTAL): {(timeTakenToFetchData + timeTakenToHandleData)} secounds -->")
        
        #End of the SVG
        toReturn.append("</svg>")
        
        toReturn = "\n".join(toReturn)
        return {'html':toReturn,'timestamp':timeStamp} #toReturn
        # except Exception as e: 
            # if str(e) == "'NoneType' object is not iterable":
            #     logging.info("User ID invalid!")
            # else:
            #     raise e
            # return {'html':'<svg id="schedule"></svg>','timestamp':0}
#endregion

#region SETUP

# Set working dir to path of main.py
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Load config file
configfile = loadConfigfile("settings.cfg")

# Change logging to go to file
logFileName = f"logfile_{currentTime()['datestamp']}.log"
logFileLocation = configfile['logFileLocation']
logging.info(f"From now on, logs will be found at '{logFileLocation+logFileName}'")
setLogging(path=logFileLocation,filename=logFileName)

# Save mainLink
mainLink = configfile['mainLink']

# Setup Flask
app = Flask(__name__)
minify(app=app, html=True, js=False, cssless=True)
rules=(
    Rule('/', endpoint='index'),
    Rule('/script/_getTime', endpoint='internal_script'),
    Rule('/terminal/schedule', endpoint='TERMINAL_SCHEDULE'),
    Rule('/terminal/getall', endpoint='API_JSON'),
    Rule('/api/json', endpoint='API_JSON'),
    Rule('/API/JSON', endpoint='API_JSON'),
    Rule('/logfile', endpoint='logfile')
);[app.url_map.add(x) for x in rules]
Mobility(app) #Mobile features
CORS(app) #Behövs så att man kan skicka requests till serven (for some reason idk)
#endregion

#region FLASK ROUTES
@app.after_request #Script to help prevent caching
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.errorhandler(werkzeug.exceptions.NotFound)
def handle_bad_request404(e):
    return e,404

@app.errorhandler(Exception)
def handle_bad_request(e):
    if configfile['enableErrorHandler']:
        logging.exception(f"This is the error : {e}")
        errorMessage = []
        try:
            #errorMessage.append(f"URL : {request.url}")
            errorMessage.append(f"TIME OF ERROR : {currentTime()['datestamp']}")
            errorMessage.append("") #End of special parameters, next is traceback
        except:errorMessage.append("SOMETHING ELSE FAILED TOO")
        errorMessage.append(traceback.format_exc())
        return render_template('error.html',message="\n".join(errorMessage))
    else:
        raise e

@app.endpoint('index')
def index():
    logger = functionLogger(functionName='index')

    # You can send JS code to parseCode, and it will appear at the end of the website.
    # loadAutomaticly is used to help custom url's to work (should be "true" by default)
    try:
        request.args['id'] #Check if custom id argument was passed in
        logger.info(f"Custom ID argument found ({request.args['id']})")
    except:
        logger.info("No custom ID argument was passed in (Ignoring)")
        return render_template("sodschema.html",parseCode="",loadAutomaticly="true",requestURL=mainLink)
    

    # This will error out if no ID was specified in the link, and then it fallsback on the normal page
    toPass = f"""idnumber = "{request.args['id']}";""" + '$(".input-idnumber").val("' + request.args['id'] + '");'

    # Since the week argument is optional, it can be skipped if not included
    try:
        toPass += f"""week = "{request.args['week']}";""" + '$(".input-week").val("' + request.args['week'] + '");'
    except:
        logger.info("No custom week argument was passed in (Ignoring)")
        pass

    # Adds these to make sure it works (it just works better like this ok?)
    toPass += "console.log('Custom URL');"
    toPass += "updateTimetable();"
    
    return render_template("sodschema.html",parseCode=Markup("<script>$(document).ready(function() {" + toPass + "});</script>"), loadAutomaticly="false", requestURL=mainLink)

@app.endpoint('internal_script')
def _getTime():
    logger = functionLogger(functionName='_getTime')
    # Get the finished HTML code for the schedule (Used by the website to generate the image you see)
    myRequest = GetTime(
        _id = request.args['id'],
        _week = int(request.args['week']),
        _day = int(request.args['day']),
        _resolution = (int(request.args['width']),int(request.args['height']))
    )
    try:
        result = myRequest.handleHTML(classes=request.args['classes'])
    except:
        result = myRequest.handleHTML()
    return jsonify(result=result)#.headers.add('Access-Control-Allow-Origin', '*')  

@app.endpoint('TERMINAL_SCHEDULE')
def terminalSchedule():
    logger = functionLogger(functionName='terminalSchedule')

    # Text based request (Returns a text based schedule)
    myRequest = GetTime()
    try:myRequest._id = request.args['id']
    except:return "YOU NEED TO PASS ID ARGUMENT"
    try:myRequest._week = request.args['week']
    except:pass
    try:myRequest._day = request.args['day']
    except:myRequest._day = currentTime()['weekday']

    a = []
    for x in myRequest.getData()['data']['lessonInfo']:
        try:
            a.append(f"{x['timeStart']} SPLITHERE {x['texts'][0]}, börjar kl {x['timeStart']} och slutar kl {x['timeEnd']} i sal {x['texts'][2]}")
        except:
            a.append(f"{x['timeStart']} SPLITHERE {x['texts'][0]}, börjar kl {x['timeStart']} och slutar kl {x['timeEnd']}")
    a.sort()

    return "\n".join([i.split(' SPLITHERE ')[1] for i in a])[:-2]

@app.endpoint('API_JSON')
def getAll():
    logger = functionLogger(functionName='getAll')

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

@app.endpoint('logfile')
def logfile():
    logger = functionLogger(functionName='logfile')
    if request.args['key'] == configfile['key']:
        with open(logFileLocation+logFileName,"r") as f:
            return f"<pre>{logFileLocation+logFileName}</pre><pre>{''.join(f.readlines())}</pre>"

# Redirects (For dead links)
@app.route("/schema/<a>")
@app.route("/schema/")
@app.route("/schema")
def routeToIndex(**a):
    logging.info(f"routeToIndex : Request landed in the redirects, sending to mainLink ({mainLink})")
    return redirect(mainLink)
#endregion

# Main:
if __name__ == "__main__":
    app.run(debug=configfile['DEBUGMODE'], host=configfile['ip'], port=configfile['port'])
