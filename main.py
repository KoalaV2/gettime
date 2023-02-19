#!/usr/bin/env python3
version = "GTM.1.3.2"
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
import tinynumpy as np
from functools import lru_cache
from urllib.parse import urlencode
from operator import attrgetter
from flask import Flask
from flask import Markup
from flask import jsonify
from flask import request
from flask import redirect
from flask import render_template
from flask import send_from_directory
from flask_cors import CORS
from flask_minify import minify
from flask_mobility import Mobility
from werkzeug.routing import Rule
from werkzeug.exceptions import NotFound
from waitress import serve
from bs4 import BeautifulSoup
#endregion
#region FUNCTIONS
def searchInDict(listInput, keyInput, valueInput):
    #Code from https://stackoverflow.com/a/8653568
    a = enumerate(listInput)
    for x, y in a:
        if y[keyInput] == valueInput:
            return x
    return None
@lru_cache(maxsize=32)
def getSchoolByID(schoolID):
    """
        Returns `True, {school data}` if `schoolID` was an int\n
        Returns `False, {school data}` if `schoolID` was an string, and if it existed in the school list\n
        Returns `None, None` if `schoolID` was not in the school list at all.
    """
    global allSchools, allSchoolsList
    try:
        b = searchInDict(allSchoolsList,'id',int(schoolID))
        try:
            return True, allSchools[allSchoolsList[b]['unitId']]
        except Exception as e:
            return None,None,-1,str(e)
    except Exception as e:
        try:
            # Tests if schoolID was just the school name
            return False, allSchools[schoolID]
        except:
            return None,None,-2,str(e)
def SetLogging(path="", filename="log.log", format=None): # '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    """
        Changes logging settings.
    """
    if format == None:
        format = configfile['loggingFormat']
    try:os.mkdir(path)
    except:pass
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
def TinyUrlShortener(url, alias="") -> str:
    return requests.get(f"https://www.tinyurl.com/api-create.php?{urlencode({'url':url,'alias':alias})}").text
@lru_cache(maxsize=32)
def EncodeString(key, clear):
    # Code from https://stackoverflow.com/a/16321853
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()
@lru_cache(maxsize=32)
def DecodeString(key, enc):
    # Code from https://stackoverflow.com/a/16321853
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)
@lru_cache(maxsize=32)
def GenerateHiddenURL(key, idInput, schoolInput, mainLink):
    a = EncodeString(key,idInput + "½" + str(getSchoolByID(schoolInput)[1]['id']))
    return mainLink + f"?a={a}",a
@lru_cache(maxsize=32)
def sha256(hash_string):
    # Code from https://tinyurl.com/2k3ds62p
    return hashlib.sha256(hash_string.encode()).hexdigest()
def arg01_to_bool(args, argName):
    """
        This function takes {request.args} and check if the argName is 1 or 0.\n
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
def getFood(allowCache=True, week=None):
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
        dataCache[myHash] = {'maxage':configfile['getFoodMaxAge'],'age':time.time(),'data':toReturn}
    return toReturn
@lru_cache(maxsize=32)
def color_convert(color, reverse=False):
    if reverse:
        if color[1] == "hex":
            return '#%02x%02x%02x' % color[0] # Code from https://stackoverflow.com/a/3380739
        if color[1] == "rgb":
            return color[0]
        if color[1] == "rgb_L":
            return list(color[0])

    if type(color) == str: # Assuming its HEX
        typeToReturn = "hex"
        if color.startswith("#"):
            color = color.lstrip('#')
        color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4)) # Code from https://stackoverflow.com/a/29643643
    elif type(color) == list and len(color) == 3: # Assuming its RGB, but as a list
        typeToReturn = "rgb_L"
        color = tuple(color)
    elif type(color) == tuple and len(color) == 3: # Assuming its RGB in the right format
        typeToReturn = "rgb"
    return color,typeToReturn
@lru_cache(maxsize=32)
def fadeColor(color, percent):
    """
        if `0 > percent >= -1` then it fades to black.\n
        if `1 > percent >=  0` then it fades to white.
    """
    color,typeToReturn = color_convert(color)

    # Code from https://stackoverflow.com/a/28033054
    color = np.array(color)
    x = color + (np.array([0,0,0] if percent < 0 else [255,255,255]) - color) * (percent if percent > 1 else percent * -1)
    x = (round(x[0]) if x[0] > 0 else 0 ,round(x[1]) if x[1] > 0 else 0 ,round(x[2]) if x[2] > 0 else 0 )

    return color_convert((color,typeToReturn),reverse=True)
@lru_cache(maxsize=32)
def grayscale(color):
    color,typeToReturn = color_convert(color)

    x = int(sum(color) / 3)
    color = (x,x,x)

    return color_convert((color,typeToReturn),reverse=True)
@lru_cache(maxsize=32)
def invertColor(color):
    color,typeToReturn = color_convert(color)

    color = (255-color[0],255-color[1],255-color[2])

    return color_convert((color,typeToReturn),reverse=True)
def global_time_argument_handler(request, handle_overflow=True):
    """
        Handles all time related arguments.

        This function handles date overflow (if week is 53, it sets the
        week to 1 and adds one year instead)

        It also handles offset operators (`<` and `>`)

        Takes:
            `request` object
        Returns:
            `dict` object with `initDayMode`, `initWeek`, `initYear` and `initDay`
    """

    t = CurrentTime()
    initDayMode = None
    initDayModeWasForced = False
    initWeek = t['week2']
    initYear = t['year']
    initDay = t['weekday3']
    initDateWasSet = False
    initDateActualWeekday = None

    if 'day' in request.args:
        if request.args['day'].startswith(">"):
            try:
                initDay = t['weekday3'] + int(request.args['day'][1:])
                initDayMode = True
            except:pass
        elif request.args['day'].startswith("<"):
            try:
                initDay = t['weekday3'] - int(request.args['day'][1:])
                initDayMode = True
            except:pass
        else:
            try:
                initDay = int(request.args['day'])
                initDayMode = True
            except:pass
    if 'week' in request.args:
        if request.args['week'].startswith(">"):
            try:initWeek = t['week'] + int(request.args['week'][1:])
            except:pass
        elif request.args['week'].startswith("<"):
            try:initWeek = t['week'] - int(request.args['week'][1:])
            except:pass
        else:
            try:initWeek = int(request.args['week'])
            except:pass
    if 'year' in request.args:
        if request.args['year'].startswith(">"):
            try:initYear = t['year'] + int(request.args['year'][1:])
            except:pass
        elif request.args['year'].startswith("<"):
            try:initYear = t['year'] - int(request.args['year'][1:])
            except:pass
        else:
            try:initYear = int(request.args['year'])
            except:pass
    if 'date' in request.args:
        initDateWasSet = True
        try:
            if request.args['date'].count("-") == 0:
                d = datetime.datetime.strptime(f"{request.args['date']}-{t['month']}-{t['year']}", '%d-%m-%Y')
            elif request.args['date'].count("-") == 1:
                d = datetime.datetime.strptime(f"{request.args['date']}-{t['year']}", '%d-%m-%Y')
            elif request.args['date'].count("-") == 2:
                d = datetime.datetime.strptime(request.args['date'], '%d-%m-%Y')

            initDayMode = True
            initDay = d.weekday() + 1
            initDateActualWeekday = d.weekday() + 1
        except:
            d = datetime.datetime.strptime(request.args['date'], '%Y-%m')

        initYear = d.year
        initWeek = d.isocalendar()[1]
    if 'daymode' in request.args:
        initDayMode = arg01_to_bool(request.args,"daymode")
        initDayModeWasForced = True

    # Fix values
    if handle_overflow:
        while initDay > 5:
            initDay -= 5
            initWeek += 1
        while initDay < 0:
            initDay += 5
            initWeek -= 1

        while initWeek < 0:
            initYear -= 1
            initWeek += 52
        while initWeek > 52:
            initYear += 1
            initWeek -= 52

    return{
        "initDayMode": initDayMode,
        "initDayModeWasForced":initDayModeWasForced, # Is true if 'daymode' was specified in the URL (gets prio over everything)
        "initWeek": initWeek,
        "initYear": initYear,
        "initDay": initDay,
        "initDateWasSet":initDateWasSet, # Is true if a date was specified
        "initDateActualWeekday":initDateActualWeekday
    }
#endregion
#region CLASSES
class HTMLObject:
    def __init__(self, tag, arguments):
        self.tag = tag
        self.arguments = arguments
    def render(self):
        a = ' '.join((f'{key}="{str(self.arguments[key])}"' if key != 'innerHTML' else "") for key in self.arguments)
        b = "" if not 'innerHTML' in self.arguments else self.arguments['innerHTML']
        return f"<{self.tag} {a}>{b}</{self.tag}>"
class Lesson:
    def __init__(self, lessonName=None, teacherName=None, classroomName=None, timeStart=None, timeEnd=None, insertDict=None) -> None:
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
    @lru_cache(maxsize=32)
    def GetTimeScore(self, start=True, end=False):
        if end == True:start = False
        #KNOWN ISSUE:
        #If time is 23:00, and you try and get timescore for a lesson that starts 01:00 the next day, it will not return 2 hours
        #This is because timescore does not care about dates, only hours and minutes

        secounds = sum(x * int(t) for x, t in zip([1, 60, 3600], reversed((self.timeStart if start else self.timeEnd).split(":"))))
        return int(secounds / 60)
class GetTime:
    """
        GetTime Request object.

        Once created, it can generate alot of information. (HTML schedule, Text schedule, Food, ect)
    """
    t = CurrentTime()
    def __init__(self, _id=None, _week=t['week2'], _day=t['weekday2'], _year=t['year'], _resolution=(1280,720), _school='IT-Gymnasiet Södertörn') -> None:
        self._id = _id
        self._week = _week
        self._day = _day
        self._year = _year
        self._resolution = _resolution
        self._s = requests.Session()
        self._s.headers.update({
            "X-Scope": "8a22163c-8662-4535-9050-bc5e1923df48",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
        })
        try:
            # If user has entered the school ID instead, then this converts it back to the name
            # (SHOULD BE THE OTHER WAY AROUND BUT THAT WILL TAKE SOME MORE TIME TO FIX)
            int(_school)
            self._school = getSchoolByID(_school)[1]['unitId']
        except:
            self._school = _school
    def getHash(self) -> str:
        """
            Generates a sha256 hash of all the settings of this object.
            Usefull to figure out if we can use cache or not (If getHash() is the same, then the data inside is the same aswell)

            Returns:
                str: SHA256 hash
        """
        return sha256("".join([str(x) for x in (self._id,self._week,self._day,self._year,self._resolution,self._school)]))
    def getData(self, allowCache=True) -> dict:
        """
            This function makes a request to Skola24's servers and returns the schedule data
            \n
            Takes:
                None
            Returns:
                <JSON> object with the data inside
        """

        if self._id == None:
            logging.info("Returning None because _id was None")
            return {"status":-7,"message":"_id was None (No ID specified)","data":None} # If ID is not set then it returns None by default

        # Default values
        response1 = ""
        response2 = ""
        response3 = ""

        myHash = self.getHash()
        if allowCache and myHash in dataCache and time.time() - dataCache[myHash]['age'] < dataCache[myHash]['maxage']:
            logging.info("Using cache!")
            toReturn = dataCache[myHash]['data']
        else:
            try:
                #region Request 1
                logging.info("Request 1")
                url1 = 'https://web.skola24.se/api/encrypt/signature'
                try:
                    response1 = self._s.post(url1, data=json.dumps({"signature":self._id}))
                except TimeoutError:
                    return {"status":-9,"message":"Response 1 Error (TimeoutError)","data":""}
                except Exception:
                    return {"status":-10,"message":"Response 1 Error (Other)","data":traceback.format_exc()}

                try:
                    response1 = json.loads(response1.text)['data']['signature']
                except Exception as e:
                    logging.info(f"Response 1 Error : {str(e)}")

                    if "Our service is down for maintenance. We apologize for any inconvenience this may cause." in response1.text or "The service is unavailable." in response1.text:
                        return {"status":-69.1,"message":f"Skola24 is currently down for maintenance (Request 1)","data":response1.text}

                    return {"status":-2,"message":f"Response 1 Error : {str(e)}","data":str(response1)}
                #endregion
                #region Request 2
                logging.info("Request 2")
                url2 = 'https://web.skola24.se/api/get/timetable/render/key'
                response2 = self._s.post(url2, data="null")
                try:
                    response2 = json.loads(response2.text)['data']['key']
                except TimeoutError:
                    return {"status":-11,"message":"Response 2 Error (TimeoutError)","data":""}
                except Exception as e:
                    logging.info(f"Response 2 Error : {str(e)}")

                    if "The service is unavailable." in response2.text:
                        return {"status":-69.2,"message":f"Skola24 is currently down for maintenance (Request 2)","data":response2.text}

                    return {"status":-3,"message":f"Response 2 Error : {str(e)}","data":str(response2)}
                #endregion
                #region Request 3
                logging.info("Request 3")
                url3 = 'https://web.skola24.se/api/render/timetable'
                payload3 = {
                    "renderKey":response2,
                    "host": allSchools[self._school]['hostName'],
                    "unitGuid": allSchools[self._school]['unitGuid'],
                    "scheduleDay":int(self._day),
                    "width":int(self._resolution[0]),
                    "height":int(self._resolution[1]),
                    "selectionType":4,
                    "selection":response1,
                    "week":int(self._week),
                    "year":int(self._year),
                }
                response3 = self._s.post(url3, data=json.dumps(payload3))
                try:response3 = json.loads(response3.text)
                except TimeoutError:
                    return {"status":-12,"message":"Response 3 Error (TimeoutError)","data":""}
                except Exception as e:
                    logging.info(f"Response 3 Error : {str(e)}")
                    return {"status":-4,"message":f"Response 3 Error : {str(e)}","data":str(response3)}
                #endregion
                toReturn = {"status":0,"message":"OK","data":response3}
            except Exception as e:
                toReturn = {"status":-99,"message":"GENERAL ERROR","data":traceback.format_exc()}
                logging.info(str(toReturn))
                return toReturn
            logging.info("Request 3 is finished. Will now check for errors")
            #Error Checking
            if response1 == "":
                return {"status":-30.1,"message":"response1 was empty","data":None}
            if response2 == "":
                return {"status":-30.2,"message":"response2 was empty","data":None}
            if response3 == "":
                return {"status":-30.3,"message":"response3 was empty","data":None}
            try:
                if response3['error'] != None:
                    return {'status':-5,'message':"error was not None","data":response3}
                if len(response3['validation']) > 0:
                    return {'status':-6,'message':','.join([x['message'] for x in response3['validation']]),"data":response3,"validation":response3['validation']}
            except:
                return {'status':-8,'message':f"An error occured when trying to check for other errors! (Yes, really.) Here is the traceback : {traceback.format_exc()}","data":response3}

            if allowCache:
                dataCache[myHash] = {'maxage':configfile['getDataMaxAge'],'age':time.time(),'data':toReturn}
        return toReturn
    def getMoreData(self, allowCache=True) -> dict:

        # myHash = self.getHash()
        # if allowCache and myHash in dataCache and time.time() - dataCache[myHash]['age'] < dataCache[myHash]['maxage']:
        #     logging.info("Using cache!")
        #     toReturn = dataCache[myHash]['data']
        # else:
        #     pass

        toReturn = {
            "data": {
                "classes": [],
                "courses": [],
                "groups": [],
                "periods": [],
                "rooms": [],
                "students": [],
                "subjects": [],
                "teachers": []
            },
            "error": None,
            "exception": None,
            "validation": []
        }

        if self._school in allSchools:
            try:
                headers = {
                    'X-Scope': '8a22163c-8662-4535-9050-bc5e1923df48',
                    'X-Requested-With': 'XMLHttpRequest',
                }

                data = '''{
                    "hostName":"%s",
                    "unitGuid":"%s",
                    "filters":{
                        "class":true,
                        "course":true,
                        "group":true,
                        "period":true,
                        "room":true,
                        "student":true,
                        "subject":true,
                        "teacher":true
                    }
                }''' % (
                    allSchools[self._school]['hostName'],
                    allSchools[self._school]['unitGuid']
                )

                response = self._s.post('https://web.skola24.se/api/get/timetable/selection', headers=headers, data=data)

                try:
                    toReturn = response.json()
                except:
                    toReturn['error'] = 'BAD DATA'
                    toReturn['traceback'] = traceback.format_exc()
                    toReturn['BAD_DATA'] = response.text
            except:
                toReturn['error'] = 'Other Error'
                toReturn['traceback'] = traceback.format_exc()
        else:
            toReturn['error'] = f'"{self._school}" is not a valid school ID'

        if "overwriteOtherData" in allSchools[self._school]:
            overwriteData = allSchools[self._school]["overwriteOtherData"]['data']

            for key in overwriteData:
                for x in overwriteData[key]:
                    toReturn["data"][key].append(x)

        return toReturn
    def fetch(self, allowCache=True) -> list:
        """
            Fetches and formats data into <lesson> objects.
            \n
            Takes:
                None
            Returns:
                List with <lesson> objects
        """
        toReturn = []
        response = self.getData(allowCache=allowCache)
        if response['status'] < 0:
            logging.info('ERROR!',response)
            return response

        try:
            if response['data']['data']['lessonInfo'] == None:
                return [] # No lessions this day
        except Exception as e:
            logging.info(f"Before i die! : {str(response)}")
            raise e

        for x in response['data']['data']['lessonInfo']:
            try:
                currentLesson = Lesson()

                try:currentLesson.lessonName=x['texts'][0]
                except:pass
                try:currentLesson.teacherName=x['texts'][1]
                except:pass
                try:currentLesson.timeStart=x['timeStart']
                except:pass
                try:currentLesson.timeEnd=x['timeEnd']
                except:pass

                #Sometimes the classroomName is absent
                try:currentLesson.classroomName = x['texts'][2]
                except:currentLesson.classroomName = ""

                if currentLesson.classroomName == "":
                    currentLesson.classroomName = None

                toReturn.append(currentLesson)
            except:pass
        toReturn.sort(key=attrgetter('timeStart'))
        return toReturn
    def handleHTML(self, classes="", privateID=False, allowCache=True, darkMode=False, darkModeSetting=1, isMobile=False) -> dict:
        """
            Fetches and converts the <JSON> data into a SVG (for sending to HTML)
            \n
            Takes:
                classes (optional) (add custom classes to the SVG)
            Returns:
                {'html':(SVG HTML CODE),'timestamp':timeStamp}
        """
        #region init
        toReturn = []
        timeTakenToFetchData = time.time()
        j = self.getData(allowCache=allowCache)

        if j['status'] < 0:
            try:
                return {'html':"""<!-- ERROR --> <div id="schedule" style="all: initial;*{all:unset;}">""" + f"""<p style="color:white">{j['message']}</p>""" + j['data'].text + "</div>",'data':j}
            except AttributeError:
                return {'html':"""<!-- ERROR --> <div id="schedule" style="all: initial;*{all:unset;}">""" + f"""<p style="color:white">{j['message']}</p>{j['data']}</div>""",'data':j}

        timeTakenToFetchData = time.time()-timeTakenToFetchData
        timeTakenToHandleData = time.time()
        #endregion
        #region Start of the SVG
        toReturn.append(f"""<svg id="schedule" class="{classes}" style="width:{self._resolution[0]}px; height:{self._resolution[1]}px;" viewBox="0 0 {self._resolution[0]} {self._resolution[1]}" shape-rendering="crispEdges">""")
        #region boxList
        logging.info("Looping through boxList...")
        toReturn_boxList = []
        colors = []
        for current in j['data']['data']['boxList']:
            # Saves the color in a seperate variable so that we can modify it
            bColor = current['bColor']

            if current['type'] == "Lesson":
                # Add bodycolor to dictionary and leaave fColor empty to store the bodycolor.
                colors.append({ "bColor": bColor, "fColor": []})
                if darkModeSetting == 2:
                    bColor = "#525252"
                elif darkModeSetting == 3:
                    bColor = grayscale(bColor)
                elif darkModeSetting == 4:
                    bColor = invertColor(bColor)
            else:
                if darkMode:
                    if bColor == "#FFFFFF":
                        bColor = "#282828"
                    if bColor == "#CCCCCC":
                        bColor = "#373737"

            toReturn_boxList.append(
                HTMLObject(
                    tag='rect',
                    arguments={
                        'id':current['id'],
                        'x':current['x'],
                        'y':current['y'],
                        'width':current['width'],
                        'height':current['height'],
                        'class':f"rect-{current['type'].replace(' ','-')}",
                        'style':f'fill:{bColor};'
                    }
                )
            )
        #endregion
        #region textList
        scriptBuilder = {}
        logging.info("Looping through textList...")
        toReturn_textList = []
        numlist = []
        for i,current in enumerate(j['data']['data']['textList']):
            # Saves the color in a seperate variable so that we can modify it
            fColor = current['fColor']

            if current['type'] == "Lesson":
                # Add current lesson number to numlist.
                numlist.append(i)

                # Turn the existing 32,33,34 etc dictionary into 1,2,3,4.
                newi = numlist[-1]-numlist[0]
                # Store fontcolor in dictionary and divide newi by 3 since there is 3 fonts per lesson.
                try:
                    colors[newi//3]["fColor"].append(fColor)

                    newbColor = colors[newi//3]["bColor"]
                    newFcolor = colors[newi//3]["fColor"][0]

                    # Calculate the color luminance: https://stackoverflow.com/questions/9780632/how-do-i-determine-if-a-color-is-closer-to-white-or-black
                    FY = (tuple(int(newFcolor[i:i + 2], 16) / 255. for i in (1, 3, 5)))
                    BY = (tuple(int(newbColor[i:i + 2], 16) / 255. for i in (1, 3, 5)))
                    whitescalefont = 0.2126*FY[0]+0.7152*FY[1]+0.0722*FY[2]
                    whitescalebody = 0.2126*BY[0]+0.7152*BY[1]+0.0722*BY[2]

                    # # If lesson body is bright and font is bright change font to dark.
                    if whitescalebody > 0.5 and whitescalefont == 1.0:
                        fColor = "#000000"

                    # # If lesson body is dark and font is dark change font to bright.
                    # if whitescalebody < 0.5 and whitescalefont == 0.0:
                    #     fColor = "#FFFFFF"
                except:
                    pass

                if darkModeSetting == 2:
                    fColor = "#FFFFFF"
                elif darkModeSetting == 4:
                    fColor = invertColor(fColor)
            else:
                if darkMode:
                    if fColor == "#000000":
                        fColor = "#FFFFFF"

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

                y_offset = 12
                if current['type'] in ('HeadingDay','ClockAxisBox'):
                    y_offset += 5
                if isMobile and current['type'] in ('ClockFrameStart','ClockFrameEnd'):
                    y_offset -= 3

                size_offset = -2
                if current['type'] == "Lesson":
                    size_offset += -1
                if current['type'] in ('ClockFrameStart','ClockFrameEnd'):
                    size_offset += 1

                toReturn_textList.append(
                    HTMLObject(
                        tag='text',
                        arguments={
                            'x':current['x'],
                            'y':current['y'] + y_offset,
                            'class':f"text-{current['type'].replace(' ','-')}",
                            'style':f'font-size:{int(current["fontsize"])+size_offset}px;fill:{fColor};',
                            'innerHTML':current['text']
                        }
                    )
                )
        #endregion
        #region lineList
        logging.info("Looping through lineList...")
        toReturn_lineList = []
        for current in j['data']['data']['lineList']:
            color = current['color']
            if darkMode:
                if color == "#000000":
                    color = "#525252"
            x1,x2=current['p1x'],current['p2x']
            # Checks delta lenght and skips those smalled then 10px
            if int(x1-x2 if x1>x2 else x2-x1) > 10:
                toReturn_lineList.append(
                    HTMLObject(
                        tag='line',
                        arguments={
                            'x1':current['p1x'],
                            'y1':current['p1y'],
                            'x2':current['p2x'],
                            'y2':current['p2y'],
                            'stroke':color,
                            'class':f"line-{current['type'].replace(' ','-')}"
                        }
                    )
                )
        #endregion
        #region Scripts
        if privateID == False:
            a = [x.arguments for x in toReturn_boxList]

            for key in scriptBuilder:
               toReturn_boxList[searchInDict(a,'id',key)].arguments['onclick'] = f"""iWasClicked('{key}','{"_".join(scriptBuilder[key])}');"""

        for x in toReturn_boxList + toReturn_textList + toReturn_lineList:
            toReturn.append(x.render())

        timeTakenToHandleData = time.time() - timeTakenToHandleData
        #endregion
        #region Comments
        toReturn.append("<!-- THIS SCHEDULE WAS MADE POSSIBLE BY https://github.com/KoalaV2 -->")
        toReturn.append(f"<!-- SETTINGS USED: id: {'[HIDDEN]' if privateID else self._id}, week: {self._week}, day: {self._day}, resolution: {self._resolution}, class: {classes} -->")
        toReturn.append(f"<!-- Time taken (Requesting data): {timeTakenToFetchData} secounds -->")
        toReturn.append(f"<!-- Time taken (Schedule generation): {timeTakenToHandleData} secounds -->")
        toReturn.append(f"<!-- Time taken (TOTAL): {(timeTakenToFetchData + timeTakenToHandleData)} secounds -->")
        #endregion

        toReturn.append("</svg>")
        # End of the SVG
        #endregion
        return {'html':"\n".join(toReturn)}
    def GenerateTextSummary(self, mode="normal", lessons=None, allowCache=True):
        if lessons == None:lessons = self.fetch(allowCache=allowCache)
        try:
            if lessons[0]<0:return str(lessons[1])
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
        """
            Runs `getFood()` on this object (using `self._week`)

            Args:
                allowCache (bool, optional): If set to `False` then it skips any existing cache. Defaults to True.

            Returns:
                dict: dictionary with all the food information.
        """
        return getFood(allowCache=allowCache,week=self._week)
class DropDown_Button:
    def __init__(self, button_text={'short':'','long':''}, button_icon="", button_type="link", button_arguments={}, button_id="") -> None:
        self.button_text = button_text #Max : 17 characters long
        self.button_icon = button_icon
        self.button_type = button_type
        self.button_arguments = button_arguments
        self.button_id = button_id
    def checkVariables(self):
        if type(self.button_text) == str:
            self.button_text = {'short':self.button_text,'long':self.button_text}
    def render(self):
        self.checkVariables()

        arguments = " ".join([f'{key}="{self.button_arguments[key]}"' for key in self.button_arguments])

        types = {
            'link':f"""
            <a {arguments} class="control control-container">
                <span id="{self.button_id}" class="menu-option-text" shortText="{self.button_text['short']}&nbsp;&nbsp;" longText="{self.button_text['long']}&nbsp;&nbsp;">{self.button_text['long']}&nbsp;&nbsp;</span>
                <i class="{self.button_icon} control-right"></i>
            </a>
            """,

            'switch':f"""
                <label class="toggleBox control-container" for="{self.button_id}">
                    <span id="{self.button_id}-text" class="menu-option-text" shortText="{self.button_text['short']}&nbsp;&nbsp;" longText="{self.button_text['long']}&nbsp;&nbsp;">{self.button_text['long']}&nbsp;&nbsp;</span>
                    <label class="switch">
                        <input type="checkbox" {arguments} class="input-switch" name="{self.button_id}" id="{self.button_id}"/>
                        <span class="slider round control control-right"></span>
                    </label>
                </label>
            """
        }
        return Markup(types[self.button_type])
#endregion
#region Load data
def init_Load():
    """
        This function loads in all of the external files (such as .json files)
    """
    toLogLater = [] #Contains things to log after all the logging and such has been configured, to make sure it shows up in the logfile

    # Set working dir to path of main.py
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Load config file
    default_template = { # Default template. Uses values from here when it cant be found in settings.json
        "DEBUGMODE": False,
        "limpMode": True,
        "ip": "0.0.0.0",
        "port": "5000",
        "logToFile": True,
        "logToSameFile": True,
        "logFileLocation": "logs/",
        "loggingFormat": "%(asctime)s %(levelname)10s %(funcName)15s() : %(message)s",
        "mainLink": "http://0.0.0.0:5000/",
        "key": "Default template",
        "enableErrorHandler": True,
        "discordKey": "Default template",
        "discordPrefix": "!gt",
        "discordRGB": [138,194,241],
        "formLink": "",
        "getDataMaxAge": 300,
        "getFoodMaxAge": 3600
    }
    configWasFine = True
    try:
        with open("settings.json", encoding="utf-8") as f:
            configfile = json.load(f)
            for key in default_template:
                if not key in configfile:
                    toLogLater.append(("critical",f"THE KEY \"{key}\" IS MISSING FROM \"settings.json\"! USING DEFAULT VALUE ({default_template[key]})! ALL FEATURES MIGHT NOT BE WORKING AS INTENDED!"))
                    configfile[key] = default_template[key]
                    configWasFine = False
    except Exception:
        toLogLater.append(("critical","UNABLE TO LOAD FROM \"settings.json\"! USING DEFAULT TEMPLATE! ALL FEATURES MIGHT NOT BE WORKING AS INTENDED!"))
        configfile = default_template
        configWasFine = False

    if configWasFine:
        toLogLater.append(("info","\"settings.json\" loaded without issues."))

    # Load contacts

    try:
        with open("contacts.json", encoding="utf-8") as f:
            contacts = json.load(f)
        toLogLater.append(("info","\"contacts.json\" loaded without issues."))
    except:
        toLogLater.append(("critical","\"contacts.json\" did not load successfully. Please make sure the file exists."))
        contacts = {}

    # Load menus
    try:
        with open("menus.json", encoding="utf-8") as f:
            menus = json.load(f)
        toLogLater.append(("info","\"menus.json\" loaded without issues."))
    except:
        toLogLater.append(("critical","\"menus.json\" did not load successfully. Please make sure the file exists."))
        menus = {}

    # Load schools file
    unitssession = requests.Session()
    def getUnits(hostname):
        headers = {
            'X-Scope': '8a22163c-8662-4535-9050-bc5e1923df48',
            'X-Requested-With': 'XMLHttpRequest',
        }
        unitssession.headers.update(headers)

        json_data = {
            'getTimetableViewerUnitsRequest': {
                'hostName': hostname,
            },
        }

        response = unitssession.post(
            'https://web.skola24.se/api/services/skola24/get/timetable/viewer/units',
            json=json_data,
        )
        return response



    toLogLater.append(("info","Authentication request."))
    response = requests.get(
        'https://www.skola24.se/Applications/Authentication/login.aspx'
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    domain_dropdown = soup.find(id='DomainDropDown')
    options = domain_dropdown.find_all('option')
    counter = 0
    allSchools = {}
    toLogLater.append(("info","Get units request. ( This will take a while. )"))
    print("Get units request. ( This will take a while. ) ")
    for option in options:
        if option.text == "(Välj domän)":
            continue
        results = getUnits(option.text).json()
        for units in results["data"]["getTimetableViewerUnitsResponse"]["units"]:
            if units['unitId'] == "IT-Gymnasiet-Södertörn":
                allSchools[units["unitId"]] = {
                    'id': int(counter),
                    'hostName': option.text,
                    'unitGuid': units['unitGuid'],
                    'unitId': units['unitId'],
                    'lunchLink': "https://skolmaten.se/nti-gymnasiet-sodertorn/"
                    }
            else:
                allSchools[units["unitId"]] = {
                    'id': int(counter),
                    'hostName': option.text,
                    'unitGuid': units['unitGuid'],
                    'unitId': units['unitId'],
                    'lunchLink': "https://skolmaten.se/nti-gymnasiet-sodertorn/"
                    }
            counter += 1
    try:
        allSchoolsList = [allSchools[x] for x in allSchools] # Contains all the school objects, but in a list
        allSchoolsNames = [x for x in allSchools] # Contains all the names, sorted by alphabetical order
        allSchoolsNames.sort()
        toLogLater.append(("info","skola24 api data was parsed successfully."))
    except Exception as e:
        print(e)
        toLogLater.append(("critical","skola 24 api data was NOT parsed successfully. This is bad..."))
        try:
            with open("schools.json", encoding="utf-8") as f:
                allSchools = json.load(f)
            toLogLater.append(("info","\"schools.json\" loaded without issues."))
        except:
            toLogLater.append(("critical","\"schools.json\" did not load successfully. Please make sure the file exists."))
            allSchools = {}

    return{
        'toLogLater':toLogLater,
        'configfile':configfile,
        "allSchools":allSchools,
        "allSchoolsList":allSchoolsList,
        "allSchoolsNames":allSchoolsNames,
        "contacts":contacts,
        "menus":menus
    }
l = init_Load()
toLogLater = l['toLogLater']
configfile = l['configfile']
allSchools = l['allSchools']
allSchoolsList = l['allSchoolsList']
allSchoolsNames = l['allSchoolsNames']
contacts = l['contacts']
menus = l['menus']

dataCache = {}
#endregion
if __name__ == "__main__":
    #region INIT
    # Sets default logging settings (before cfg file has been loaded in)
    logging.basicConfig(level=logging.INFO, format=configfile['loggingFormat']) #%(levelname)s %(name)s

    # Change logging to go to file
    if configfile['logToFile']:
        if configfile['logToSameFile']:
            logFileName = "logfile.log"
        else:
            logFileName = f"logfile_{CurrentTime()['datestamp']}.log"
        logFileLocation = configfile['logFileLocation']
        logging.info(f"Logging config loaded. From now on, logs will be found at '{logFileLocation+logFileName}'")
        SetLogging(path=logFileLocation,filename=logFileName)
    else:
        logging.info("Logging config loaded. From now on, logging will continue in the console.")

    # Setup Flask
    app = Flask(__name__, static_url_path='/static')
    minify(app=app, html=True, js=False, cssless=True, passive=True)
    Mobility(app) # Mobile features
    cors = CORS(app, resources={r"/API/*": {"origins": "*"}}) #CORS(app) # Behövs så att man kan skicka requests till serven (for some reason idk)

    #endregion
    #region Flask Routes
    [app.url_map.add(x) for x in (
        #INDEX
        Rule('/', endpoint='INDEX'),

        #API
        Rule('/robots.txt', endpoint='textfiles'),
        Rule('/security.txt', endpoint='textfiles'),
        Rule('/gpg.txt', endpoint='textfiles'),

        Rule('/API/QR_CODE', endpoint='API_QR_CODE'),
        Rule('/API/SHAREABLE_URL', endpoint='API_SHAREABLE_URL'),
        Rule('/API/GENERATE_HTML', endpoint='API_GENERATE_HTML'),
        Rule('/API/JSON', endpoint='API_JSON'),
        Rule('/API/SIMPLE_JSON', endpoint='API_SIMPLE_JSON'),
        Rule('/API/TERMINAL_SCHEDULE', endpoint='API_TERMINAL_SCHEDULE'),
        Rule('/API/FOOD', endpoint='API_FOOD'),
        Rule('/API/FOOD_REDIRECT', endpoint='FOOD_REDIRECT'),
        Rule('/API/MORE_DATA', endpoint='MORE_DATA'),
        Rule('/API/HEALTH', endpoint='HEALTH'),

        #PWA stuff
        Rule('/service-worker.js', endpoint="SW"),

        #Logfiles
        Rule('/logfile', endpoint='logfile'),
        Rule('/discord_logfile', endpoint='discord_logfile'),

        #Reserved
        Rule('/theo', endpoint='TheoCredit'),
        Rule('/pierre', endpoint='PierreCredit'),
        Rule('/ඞ', endpoint='ඞ'),
        Rule('/contact', endpoint='CONTACT'),
        Rule('/about', endpoint='CONTACT'),
        Rule('/form', endpoint='FORM'),

        # Obsolete/Old formats
        Rule('/terminal/schedule', endpoint='API_TERMINAL_SCHEDULE'),
        Rule('/terminal/getall', endpoint='API_JSON'),
        Rule('/script/API_SHAREABLE_URL', endpoint='API_SHAREABLE_URL'),
        Rule('/script/API_GENERATE_HTML', endpoint='API_GENERATE_HTML'),
        Rule('/api/json', endpoint='API_JSON')
    )]
    #region Error handling and response headers
    @app.after_request
    def after_request(response):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN 2'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        #response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; object-src 'none'; frame-src 'none'; base-uri 'none';"

        # This helps preventing caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"

        return response
    @app.errorhandler(NotFound)
    def handle_bad_request_404(e):
        """
            404 errors always land here (because it makes more senses)
        """
        return e,404
    @app.errorhandler(Exception)
    def handle_bad_request(e):
        """
            If error is not 404, then it lands here.\n
            If `enableErrorHandler` is `true` in the config file then it will use the special configfile.
        """
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
    #region INDEX
    buttons = {
        # Redirect to school lunch link
        'food':DropDown_Button(
            button_text={
                'short':'Mat',
                'long':'Skollunch'
                },
            button_icon="fas fa-utensils",
            button_type="link",
            button_id='button-text-food',
            button_arguments={
                'onclick':f"""window.location.href = '{configfile["mainLink"]}API/FOOD_REDIRECT?school='+encodeURI(school)"""
            }
        ),

        # Generate savable link
        'generateSavableLink':DropDown_Button(
            button_text={
                'short':'Privat länk',
                'long':'Skapa privat länk'
                },
            button_icon="fas fa-user-lock",
            button_type="link",
            button_id="button-text-private",
            button_arguments={
                'onclick':"""window.location.href = getShareableURL()['url'];"""
            }
        ),

        # Copy savable link
        'copySavableLink':DropDown_Button(
            button_text={
                'short':'Kopiera länk',
                'long':'Kopiera privat länk'
                },
            button_icon="fas fa-user-lock",
            button_type="link",
            button_id="button-text-copy",
            button_arguments={
                'onclick':"""updateClipboard(window.location.href);"""
            }
        ),

        # Generate QR code
        'generateQrCode':DropDown_Button(
            button_text={
                'short':'QR kod',
                'long':'Skapa QR kod'
                },
            button_icon="fas fa-qrcode",
            button_type="link",
            button_id="button-text-qr",
            button_arguments={
                'onclick':"""clickOn_QRCODE()"""
            }
        ),

        # Go back to main page
        'mainPage':DropDown_Button(
            button_text="Startsida",
            button_icon="far fa-calendar-alt",
            button_type="link",
            button_arguments={
                'onclick':"""window.location.href = requestURL;"""
            }
        ),

        # Day only mode toggle switch
        'dayMode':DropDown_Button(
            button_text={
                'short':'Dag',
                'long':'Visa bara dag'
                },
            button_type="switch",
            button_id='input-day'
        ),

        # Contact button
        'contact':DropDown_Button(
            button_text={
                'short':'Om oss',
                'long':'Om GetTime'
                },
            button_icon="far fa-address-book",
            button_type="link",
            button_id="button-text-gotostart",
            button_arguments={
                'onclick':"""textBoxOpen('#text_contact_info');"""
            }
        ),

        # Show saved timetables button
        'showSaved':DropDown_Button(
            button_text={
                'short':'Länkar',
                'long':"Sparade länkar"
                },
            button_icon="far fa-save",
            button_type="link",
            button_id="button-text-saved",
            button_arguments={
                'onclick':"""clickOn_SAVEDLINKS();"""
            }
        ),

        # Toggle Dark mode
        'darkmode':DropDown_Button(
            button_text={
                'short':'Mörk',
                'long':"Mörkt läge"
                },
            button_type="switch",
            button_id='input-darkmode',
            button_arguments={
                'onclick':"""toggleDarkMode();"""
            }
        ),

        # Toggle Dark mode
        'changeSchool':DropDown_Button(
            button_text={
                'short':'Skola',
                'long':"Byt skola"
                },
            button_type="link",
            button_icon="fas fa-school",
            button_id='input-change-school',
            button_arguments={
                'onclick':"""textBoxOpen('#text_school_selector');"""
            }
        )
    }
    @app.endpoint('INDEX')
    def INDEX(alternativeArgs=None):
        # alternativeArgs can be used to pass in URL arguments.
        if alternativeArgs != None:
            request.args = alternativeArgs

        #region Default values
        t = CurrentTime()
        parseCode = ""
        requestURL = configfile['mainLink']
        hideNavbar = False
        initID = ""
        initSchool = None #If set to "null" then it will ALWAYS ask what shcool it should use
        initDarkMode = "null"
        darkModeSetting = 1
        debugmode = False # Not the actual debugmode, but the debug console window thingy
        privateURL = False
        saveIdToCookie = True
        mobileRequest = request.MOBILE
        showContactOnLoad = False
        autoReloadSchedule = False
        dropDownButtons = []
        ignorecookiepolicy = False
        oldPrivateUrl = False
        initPWA = False
        #endregion
        #region Check parameters
        d = global_time_argument_handler(request)
        initDayMode = d['initDayMode']
        initWeek = d['initWeek']
        initYear = d['initYear']
        initDay = d['initDay']

        initPWA = arg01_to_bool(request.args, "PWA")
        if not d['initDayModeWasForced']:
            # If date was specified, and it was a sunday/saturday, then show the whole schedule
            if d['initDateWasSet'] and d['initDateActualWeekday'] > 5:
                initDay = 1
                initDayMode = False
            elif initDayMode == None:
                initDayMode = mobileRequest
        if 'id' in request.args:
            initID = request.args['id']
            saveIdToCookie = False
            logging.info(f"Custom ID argument found ({initID})")
        if 'a' in request.args:
            temp = DecodeString(configfile['key'],request.args['a'])
            if "½" in temp:
                initID,initSchool = temp.split("½")
                initSchool = int(initSchool)
            else:
                initID = temp
                initSchool = "null"
                oldPrivateUrl = True

            privateURL = True
            saveIdToCookie = False
            logging.info(f"Custom Encoded ID argument found ({initID})")
        if 'school' in request.args:
            initSchool = request.args['school']
        if 'debugmode' in request.args:
            debugmode = arg01_to_bool(request.args,"debugmode")
        if 'contact' in request.args:
            showContactOnLoad = arg01_to_bool(request.args,"contact")
        if 'rl' in request.args:
            autoReloadSchedule = arg01_to_bool(request.args,"rl")
        if 'ignorecookiepolicy' in request.args:
            ignorecookiepolicy = arg01_to_bool(request.args,"ignorecookiepolicy")
        if 'darkmode' in request.args:
            initDarkMode = str(arg01_to_bool(request.args,"darkmode")).lower()
        if 'filter' in request.args:
            if request.args['filter'] == 'flat':
                darkModeSetting = 2
            if request.args['filter'] == 'grayscale':
                darkModeSetting = 3
            if request.args['filter'] == 'invert':
                darkModeSetting = 4
        hideNavbar = 'fullscreen' in request.args

        menus_params = ["desktop", "normal"]
        if mobileRequest:
            menus_params[0] = 'mobile'
        if privateURL:
            menus_params[1] = 'private'
        if initPWA:
            menus_params[1] = 'pwa'

        dropDownButtons = [buttons[x].render() for x in menus[menus_params[0]][menus_params[1]]]
        #endregion
        return render_template(
            template_name_or_list="sodschema.html",
            version=version,
            limpMode=configfile['limpMode'],
            DEBUGMODE=configfile['DEBUGMODE'],
            contacts=contacts,
            parseCode=parseCode,
            requestURL=requestURL,
            initPWA=initPWA,
            initID=initID,
            initSchool=initSchool,
            initDayMode=initDayMode,
            initWeek=initWeek,
            initYear=initYear,
            initDay=initDay,
            initDarkMode=initDarkMode,
            debugmode=debugmode,
            privateURL=privateURL,
            saveIdToCookie=saveIdToCookie,
            mobileRequest=mobileRequest,
            showContactOnLoad=showContactOnLoad,
            autoReloadSchedule=autoReloadSchedule,
            dropDownButtons=dropDownButtons,
            ignorecookiepolicy=ignorecookiepolicy,
            darkModeSetting=darkModeSetting,
            hideNavbar=hideNavbar,
            allSchools=allSchools,
            oldPrivateUrl=oldPrivateUrl,
            allSchoolsNames=allSchoolsNames
        )
    #endregion
    #region API
    @app.endpoint('MORE_DATA')
    def MORE_DATA():

        myRequest = GetTime(
            _school=request.args['school']
        )

        return jsonify(myRequest.getMoreData())

    @app.endpoint('textfiles')
    def textfiles():
        return send_from_directory('static', str(request.url_rule)[1:])

    @app.endpoint('API_QR_CODE')
    def API_QR_CODE():
        return render_template(
            'qrCodeTemplate.html',
            requestURL=configfile['mainLink'],
            passedID=None if not 'id' in request.args else request.args['id'],
            privateID=arg01_to_bool(request.args,"p")
        )
    @app.endpoint('API_SHAREABLE_URL')
    def API_SHAREABLE_URL():
        global configfile
        a = GenerateHiddenURL(configfile['key'],request.args['id'],request.args['school'],configfile['mainLink'])
        return jsonify(result={'url':a[0],'id':a[1]})
    @app.endpoint('API_GENERATE_HTML')
    def API_GENERATE_HTML():
        """
            This function generates the finished HTML code for the schedule (Used by the website to generate the image you see)
        """

        #Checks if school was the school ID, and if so, grabs the name

        myRequest = GetTime(
            _id = request.args['id'],
            _week = int(request.args['week']),
            _day = int(request.args['day']),
            _resolution = (
                int(float(request.args['width'])),
                int(float(request.args['height']))
            ),
            _school=getSchoolByID(str(request.args['school']))[1]['unitId'],
            _year=int(request.args['year'])
        )
        if 'classes' in request.args:
            classes = request.args['classes']
        else:
            classes = ""
        result = myRequest.handleHTML(
            classes=classes,
            privateID=arg01_to_bool(request.args,"privateID"),
            darkMode=arg01_to_bool(request.args,"darkmode"),
            isMobile=arg01_to_bool(request.args,"isMobile"),
            darkModeSetting=int(request.args["darkmodesetting"])
        )

        try:
            return jsonify(result=result)
        except:
            print("JSONIFY ERROR : ",result)
            try:
                return jsonify(result=str(result))
            except:
                return result
    @app.endpoint('API_JSON')
    def API_JSON():

        # Custom API (gets the whole JSON file for the user to mess with)
        # This is what the Skola24 website seems to get.
        # It contains all the info you need to rebuild the schedule image.

        d = global_time_argument_handler(request)

        myRequest = GetTime(
            _id=request.args['id'],
            _week=d['initWeek'],
            _day=d['initDay'],
            _year=d['initYear'],
            _school=getSchoolByID(request.args['school'])[1]['name']
        )
        return jsonify(myRequest.getData())
    @app.endpoint('API_SIMPLE_JSON')
    def API_SIMPLE_JSON():
        currentTime = CurrentTime()
        d = global_time_argument_handler(request)
        myRequest = GetTime(
            _id=request.args['id'],
            _week=d['initWeek'],
            _day=d['initDay'],
            _year=d['initYear'],
            _school=getSchoolByID(request.args['school'])[1]['name']
        )

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
        d = global_time_argument_handler(request)
        myRequest = GetTime(
            _id=request.args['id'],
            _week=d['initWeek'],
            _day=d['initDay'],
            _year=d['initYear'],
            _school=getSchoolByID(request.args['school'])[1]['name']
        )
        if arg01_to_bool(request.args,"text"):
            return myRequest.GenerateTextSummary()
        return jsonify({'result':myRequest.GenerateTextSummary()})
    @app.endpoint('API_FOOD')
    def API_FOOD():
        if 'week' in request.args:
            week = int(request.args['week'])
        else:
            week = None

        return getFood(week=week)
    @app.endpoint('FOOD_REDIRECT')
    def FOOD_REDIRECT():
        try:
            b = searchInDict(allSchoolsList,'id',int(request.args["school"]))
            flink = allSchoolsList[b]
        except:
            flink = allSchools[request.args["school"]]
        if "lunchLink" in flink:
            logging.info(flink)
            return redirect(flink["lunchLink"])
        return("Finns ingen matlänk för din skola, om detta är fel kontakta gärna oss på https://gettime.ga/?contact=1")
    @app.endpoint('HEALTH')
    def HEALTH():
        return "OK"
    #endregion
    #region Logs
    @app.endpoint('logfile')
    def logfile():
        if request.args['key'] == configfile['key']:
            with open(logFileLocation+logFileName,"r") as f:
                return f"<pre>{logFileLocation+logFileName}</pre><pre>{''.join(f.readlines())}</pre>"
    @app.endpoint('discord_logfile')
    def discord_logfile():
        if request.args['key'] == configfile['key']:
            with open(logFileLocation+'discord_logfile.log',"r") as f:
                return f"<pre>{logFileLocation+logFileName}</pre><pre>{''.join(f.readlines())}</pre>"
    #endregion
    #region Special easter egg URL's for the creators/contributors AND AMOGUS ඞ
    @app.endpoint('TheoCredit')
    def TheoCredit():
        return redirect('https://theolikes.tech/')
    @app.endpoint('PierreCredit')
    def PierreCredit():
        return redirect('https://github.com/PierreLeFevre')
    @app.endpoint('ඞ')
    def ඞ():
        return render_template('AmongUs.html')
    @app.endpoint('CONTACT')
    def CONTACT():
        a = dict(request.args)
        a['contact'] = "1"
        return INDEX(alternativeArgs=a)
    @app.endpoint('FORM')
    def FORM():
        return redirect(configfile['formLink'])
    #endregion
    #region PWA
    @app.endpoint('SW')
    def SW():
        return app.send_static_file('service-worker.js')
    #endregion
    #region Redirects (For dead links)
    @app.route("/schema/<a>")
    @app.route("/schema/")
    @app.route("/schema")
    def routeToIndex(**a):
        logging.info(f"routeToIndex : Request landed in the redirects, sending to mainLink ({configfile['mainLink']})")
        return redirect(configfile['mainLink'])
    #endregion
    #endregion

    # NEEDS CLEANUP/REDESIGN
    def cacheClearer():
        """
            Checks for outdated cached data and deletes it to save on memory.
        """
        while 1:
            try:
                toDelete = []
                for x in dataCache:
                    if time.time() - dataCache[x]['age'] > dataCache[x]['maxage']:
                        toDelete.append(x)
                for x in toDelete:
                    logging.info(f"Deleting {x} from cache")
                    del dataCache[x]
            except RuntimeError as e:
                logging.info(e)
                pass
            except:
                logging.exception(traceback.format_exc())
                pass
            time.sleep(1)

    for x in toLogLater:exec(f"logging.{x[0]}('{x[1]}')") # Logs all of the things that happend before logging was configured

    # Makes it so that the cacheclearer runs at the same time (probably needs reworking)
    threading.Thread(target=cacheClearer, args=(), daemon=True).start()

    if configfile['DEBUGMODE']:
        logging.warning('"DEBUGMODE" is true. The server is not live... right?')
    if configfile['limpMode']:
        logging.warning('"limpMode" is true. This should be a backup server.')

    if not configfile['DEBUGMODE']:
        serve(app, host=configfile['ip'], port=configfile['port'])
    else:
        app.run(debug=configfile['DEBUGMODE'], host=configfile['ip'], port=configfile['port'], use_reloader=False) # Run website


else:
    logging.info("main.py was imported")
