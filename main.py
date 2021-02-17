#NewGetTime Requirements:
import json
import requests

#Flask Requirements:
from flask import Flask
from flask import Markup
from flask import jsonify
from flask import request
from flask_cors import CORS
from flask import render_template
from flask_mobility import Mobility

#Other Requirements:
import os
import time
import logging
import datetime as dt
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')


#Functions:
def alltime():
    """
    Returns a dictionary with (secound, minute, hour, day, week, month, year, daynum)
    """
    def getToday():
        """Returns int of current day (mon-fri = 1-5, sat-sun = 0 (full week))"""
        a=dt.datetime.today().isoweekday()
        if a>=1 and a<=5:return a
        return 0
    b = [int(x) for x in time.strftime(f"%S/%M/%H/%d/%m/%Y/{dt.date.today().isocalendar()[1]}/{getToday()}",time.localtime()).split("/")]
    return{'secounds':b[0], 'minutes':b[1], 'hours':b[2], 'day':b[3], 'month':b[4], 'year':b[5], 'week':b[6], 'daynum':b[7]}


#NewGetTime Setup:
class Lesson:
    def __init__(self,lessionName,teacherName,classroomName,timeStart,timeEnd,dayOfWeekNumber):
        self.lessionName = lessionName
        self.teacherName = teacherName
        self.classroomName = classroomName
        self.timeStart = timeStart
        self.timeEnd = timeEnd
        self.dayOfWeekNumber = dayOfWeekNumber
class GetTime:
    def __init__(self,_id,_week,_day,_resolution):
        self._id = _id
        self._week = _week
        self._day = _day
        self._resolution = _resolution
    def getData(self):
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
        url1='https://web.skola24.se/api/encrypt/signature'
        payload1 = {"signature":self._id}
        response1 = requests.post(url1, data=json.dumps(payload1), headers=headers1)
        response1 = response1.text
        response1 = response1.split('"signature": "')[1].split('"')[0]

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
        response2 = requests.post(url2, data=payload2, headers=headers2)
        response2 = response2.text
        response2 = response2.split('"key": "')[1].split('"')[0]

        headers3 = headers2
        url3='https://web.skola24.se/api/render/timetable'
        payload3 = {
            "renderKey":response2,
            "host":"it-gymnasiet.skola24.se",
            "unitGuid":"ZTEyNTdlZjItZDc3OC1mZWJkLThiYmEtOGYyZDA4NGU1YjI2",
            "startDate":"null",
            "endDate":"null",
            "scheduleDay":self._day,
            "blackAndWhite":"false",
            "width":self._resolution[0],
            "height":self._resolution[1],
            "selectionType":4,
            "selection":response1,
            "showHeader":"false",
            "periodText":"",
            "week":self._week,
            "year":2021,
            "privateFreeTextMode":"false",
            "privateSelectionMode":"null",
            "customerKey":""
        }
        response3 = requests.post(url3, data=json.dumps(payload3), headers=headers3)
        response3 = response3.text
        response3 = json.loads(response3)
        return response3
    def fetch(self):
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
            try:
                currentLesson.classroomName = x['texts'][2]
            except:
                currentLesson.classroomName = ""
            toReturn.append(currentLesson)
        return toReturn    
    def handleHTML(self,classes=""):
        try:
            timeStamp = time.time()
            toReturn = []
            timeTakenToFetchData = time.time() #This value should contain when the request was recieved by the server
            j = self.getData()['data']
            timeTakenToFetchData = time.time()-timeTakenToFetchData
            
            timeTakenToHandleData = time.time() 

            #Start of the SVG
            toReturn.append(f"""<svg id="schedule" class="{classes}" style="width:{self._resolution[0]}; height:{self._resolution[1]};" viewBox="0 0 {self._resolution[0]} {self._resolution[1]}" shape-rendering="crispEdges">""")

            for current in j['boxList']:
                try:
                    if current['type'].startswith("ClockFrame"):
                        toReturn.append(f"""<rect x="{current['x']}" y="{current['y']}" width="{current['width']}" height="{current['height']}" style="fill:{current['bColor']};"></rect>""")
                    else:
                        toReturn.append(f"""<rect x="{current['x']}" y="{current['y']}" width="{current['width']}" height="{current['height']}" style="fill:{current['bColor']};stroke:rgb(0,0,0);stroke-width:1;"></rect>""")
                    logging.info("THE NEW BOXLIST THING IS WORKING")
                except:
                    if current['type'] == "ClockFrameStart" or current['type'] == "ClockFrameEnd":
                        _style = f'''style="fill:{current['bColor']};"'''
                    else:
                        _style = f'''style="fill:{current['bColor']};stroke:rgb(0,0,0);stroke-width:1;"'''
                    toReturn.append(f"""<rect x="{current['x']}" y="{current['y']}" width="{current['width']}" height="{current['height']}" {_style}></rect>""")
                    logging.info("THE NEW BOXLIST THING IS NOT WORKING")

            for current in j['textList']:
                toReturn.append(f"""<text x="{current['x']}" y="{current['y']+12}" style="font-size:{int(current['fontsize'])}px;fill:{current['fColor']};">{current['text']}</text>""")

            for current in j['lineList']:
                try:
                    x1,x2= current['p1x'],current['p2x'];dif=int(x1-x2 if x1>x2 else x2-x1)
                    logging.info("THE NEW LINELIST THING IS WORKING")
                except:
                    dif = 0
                    x1 = current['p1x']
                    x2 = current['p2x']
                    if x1 > x2:
                        dif += x1 - x2
                    else:
                        dif += x2 - x1
                    logging.info("THE NEW LINELIST THING IS NOT WORKING")

                if dif > 10:
                   toReturn.append(f"""<line x1="{current['p1x']}" y1="{current['p1y']}" x2="{current['p2x']}" y2="{current['p2y']}" stroke="{current['color']}"></line>""")
            timeTakenToHandleData = time.time() - timeTakenToHandleData

            toReturn.append("<!-- THIS SCHEDULE WAS MADE POSSIBLE BY https://github.com/KoalaV2 -->")
            toReturn.append(f"<!-- SETTINGS USED: id: {self._id}, week: {self._week}, day: {self._day}, resolution: {self._resolution}, class: {classes} -->")
            toReturn.append(f"<!-- Time taken (Requesting data): {timeTakenToFetchData} secounds -->")
            toReturn.append(f"<!-- Time taken (Schedule generation): {timeTakenToHandleData} secounds -->")
            toReturn.append(f"<!-- Time taken (TOTAL): {(timeTakenToFetchData + timeTakenToHandleData)} secounds -->")
            
            #End of the SVG
            toReturn.append("</svg>")
            
            toReturn = "\n".join(toReturn)
            return {'html':toReturn,'timestamp':timeStamp} #toReturn
        except Exception as e:
            if str(e) == "'NoneType' object is not iterable":
                logging.info("User ID invalid!")
            else:
                raise e
            return """<svg id="schedule"></svg>"""


#Flask Setup:
mainLink = "https://www.gettime.ga/"
app = Flask(__name__)
Mobility(app) #Mobile features
CORS(app) #Behövs så att man kan skicka requests till serven (for some reason idk)
#app.logger.disabled = True
#logging.getLogger('werkzeug').disabled = True

@app.after_request #Script to help prevent caching
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def mainpage():
    try:
        # This will error out if no ID was specified in the link, and then it fallsback on the normal page
        toPass = f"""idnumber = "{request.args['id']}";""" + '$(".input-idnumber").val("' + request.args['id'] + '");'

        # Since the week argument is optional, it can be skipped if not included
        try:toPass += f"""week = "{request.args['week']}";""" + '$(".input-week").val("' + request.args['week'] + '");'
        except:pass

        # try:
        #     # I honestly dont know what this one does tbh
        #     toPass += f"""document.getElementById("input-day").checked = {str(int(request.args['day'])==0).lower()};"""
        #     toPass += 'var dateDay = date.getDay();'
        # except:pass

        # Adds these to make sure it works (it just works better like this ok?)
        toPass += "console.log('Custom URL');"
        toPass += "updateTimetable();"
        
        return render_template("sodschema.html",parseCode=Markup("<script>$(document).ready(function() {" + toPass + "});</script>"),loadAutomaticly="false")
    except:
        return render_template("sodschema.html",parseCode="",loadAutomaticly="true")

@app.route("/script/_getTime")
def _getTime():
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
    return jsonify(result=result) 

@app.route('/terminal/schedule')
def terminalSchedule():
    # Text based request (Returns a text based schedule)
    try:
        myRequest = GetTime(
            _id = None,
            _week = None,
            _day = None,
            _resolution = (1280,720)
        )
        try:myRequest._id = request.args['id']
        except:return "YOU NEED TO PASS ID ARGUMENT"
        try:myRequest._week = request.args['week']
        except:myRequest._week = alltime()['week']
        try:myRequest._day = request.args['day']
        except:myRequest._day = alltime()['daynum']

        a = []
        for x in myRequest.getData()['data']['lessonInfo']:
            try:
                temp = f"{x['timeStart']} SPLITHERE {x['texts'][0]}, börjar kl {x['timeStart']} och slutar kl {x['timeEnd']} i sal {x['texts'][2]}\n"
            except:
                temp = f"{x['timeStart']} SPLITHERE {x['texts'][0]}, börjar kl {x['timeStart']} och slutar kl {x['timeEnd']}\n"
            a.append(temp)
        a.sort()

        return "".join([i.split(' SPLITHERE ')[1] for i in a])[:-2]
    except Exception as e:
        return str(e)

@app.route("/API")
@app.route('/terminal/getall')
def getAll():
    # Custom API (gets the whole JSON file for the user to mess with)
    # This is what the Skola24 website seems to get.
    # It contains all the info you need to rebuild the schedule image.
    myRequest = GetTime(
        _id = None,
        _week = None,
        _day = None,
        _resolution = (1280,720)
    )
    try:myRequest._id = request.args['id']
    except:return "YOU NEED TO PASS ID ARGUMENT"
    try:myRequest._week = request.args['week']
    except:myRequest._week = alltime()['week']
    try:myRequest._day = request.args['day']
    except:myRequest._day = alltime()['daynum']
    
    return jsonify(myRequest.getData())

# CODE FROM OLD GETTIME THAT HAS TO BE FIXED
# @app.route("/getfood")
# @app.route("/food")
# @app.route("/mat")
# def getFoodReRoute():
#     return redirect(f"{mainLink}mat/{alltime()['week']}")
# @app.route("/mat/<selectedWeek>")
# def getFoodSite(selectedWeek):
#     from getScripts import fetchFood
#     weekFood = fetchFood(0,int(selectedWeek))
#     if weekFood == "Error":
#         return render_template('food.html',foodSend=[None,None,None,None],dagar=["Mån","Tis","Ons","Tor","Fre"],selectedWeek=selectedWeek,isError=True)
#     else:
#         return render_template('food.html',foodSend=[weekFood[x] for x in range(0,len(weekFood)-1,2)],dagar=["Mån","Tis","Ons","Tor","Fre"],selectedWeek=selectedWeek,isError=False)
# @app.route('/terminal/food')
# def teminalFood():
#     try:currentWeek = request.args['week']
#     except:currentWeek = alltime()['week']
#     from getScripts import fetchFood
#     return fetchFood(0,int(currentWeek))


#Redirects (For dead links)
@app.route("/schema/")
@app.route("/schema")
def routeToMainpage():
    return mainpage()
@app.route("/schema/<a>")
def routeToMainpage2(a):
    return mainpage()

#Main:
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port="7331")
