import requests
import time
import json

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
        response3 = requests.post(url3,data=json.dumps(payload3),headers=headers2)
        result = json.loads(response3.text)
        return result

    def fetch(self):
        result = self.getData()
        with open("results.json","w") as f:
            f.write(json.dumps(result))

        toReturn = []
        for x in result['data']['lessonInfo']:
            toReturn.append(Lesson(
                x['texts'][0],
                x['texts'][1],
                x['texts'][2],
                x['timeStart'],
                x['timeEnd'],
                x['dayOfWeekNumber'])
                )
        return toReturn
    
    def handleHTML(self):
        j = self.getData()
        toReturn = ""
        
        toReturn += f"""<svg id="schedule" style="width:{self._resolution[0]}; height:{self._resolution[1]};" viewBox="0 0 {self._resolution[0]} {self._resolution[1]}" shape-rendering="crispEdges">\n"""

        for current in j['data']['boxList']:
            _x = f'''x="{current['x']}"'''
            _y = f'''y="{current['y']}"'''
            _width = f'''width="{current['width']}"'''
            _height = f'''height="{current['height']}"'''
            #_box_type = f'''box-type="{current['type']}"'''
            #_box_id = f'''box-id="{current['id']}"'''
            if current['type'] == "ClockFrameStart" or current['type'] == "ClockFrameEnd":
                _style = f'''style="fill:{current['bColor']};"'''
            else:
                _style = f'''style="fill:{current['bColor']};stroke:rgb(0,0,0);stroke-width:1;"'''
            #{_box_type} {_box_id}
            a = f"""<rect {_x} {_y} {_width} {_height} {_style}></rect>\n"""
            toReturn += a

        for current in j['data']['textList']:
            #text-id="{current['id']}"
            _fontsize = current['fontsize']
            if str(current['fontsize']).endswith('.0'):
                _fontsize = int(current['fontsize'])
            a = f"""<text x="{current['x']}" y="{current['y']+12}" style="font-size:{_fontsize}px;fill:{current['fColor']};">{current['text']}</text>\n"""
            toReturn += a

        for current in j['data']['lineList']:
            dif = 0
            x1 = current['p1x']
            x2 = current['p2x']
            if x1 > x2:
                dif += x1 - x2
            else:
                dif += x2 - x1
            y1 = current['p1y']
            y2 = current['p2y']
            if y1 > y2:
                dif += y1 - y2
            else:
                dif += y2 - y1

            if dif > 10:
                a = f"""<line x1="{current['p1x']}" y1="{current['p1y']}" x2="{current['p2x']}" y2="{current['p2y']}" stroke="{current['color']}"></line>\n"""
                toReturn += a


        toReturn += "</svg>\n"
        toReturn += "<!-- THIS SCHEDULE WAS GENERATED WITH GETTIME2.0! -->\n"
        toReturn += f"<!-- SETTINGS USED: id:{self._id}, week:{self._week}, day:{self._day}, resolution:{self._resolution} -->\n"
        
        return toReturn



if False:
    myRequest = GetTime(
            _id = "19_tek_a",
            _week = 5,
            _day = 0,
            _resolution = (1920,1080)
    )

    lektioner = myRequest.fetch()

    for x in lektioner:
        print(x.lessionName)

