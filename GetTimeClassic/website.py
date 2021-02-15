from flask import Flask,render_template,request,redirect
from flask import Markup
from flask_mobility import Mobility
#from flask_cors import CORS
import os
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')
app = Flask(__name__)
Mobility(app)
#CORS(app)

mainLink = "https://www.gettime.ga/"

@app.after_request #Script to help prevent caching
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/schema/")
@app.route("/schema")
def routeToMainpage():
    return render_template("error.html",errorMessage="Invalid link formating!")

@app.route("/")
def mainpage(): #STARTPAGE
    return render_template("index.html")

@app.route("/",methods=['POST',"GET"])
def my_form_post(): 
    idData = request.form['id_input']
    
    if idData.startswith("raw "):
        return redirect(f"{mainLink}schema/{idData[-4:]}")
    else:
        if request.MOBILE:
            setting = "vm"
            if str(request.form.get("getFullScheduleData")) == "on":
                setting = "v1"
        else:
            setting = "v1"
            if str(request.form.get("getJustToday")) == "on":
                setting = "vm"
        for x in idData.split("-"):
            if x == "":
                return render_template("error.html",errorMessage="Invalid link formating!")
        return redirect(f"{mainLink}schema/{setting}-{idData}")

@app.route("/penis")
def penis():
    return render_template("error.html",errorMessage="bro why you go to /penis? aint that a bit gay? 👀")

@app.route("/schema/<fromurl>")
def schema(fromurl):
    import getScripts
    fromGT = getScripts.getFilename(fromurl,True)
    if fromGT == "Error":
        return render_template("error.html",errorMessage="Could not get your schedule.")
    else:
        return render_template("schema.html",htmlSchema=Markup(fromGT[0]),fullSchema=fromGT[1][5],SID=fromGT[1])

@app.route("/generateFood")
def generateFood():
    from getScripts import getFood
    logging.info("Forcing getFood to run...")
    getFood(0)
    return redirect(mainLink+"mat")

@app.route("/getfood")
@app.route("/food")
@app.route("/mat")
def getFoodReRoute():
    from getScripts import getAbsoluteTime
    return redirect(f"{mainLink}mat/{getAbsoluteTime()[6]}")

@app.route("/mat/<selectedWeek>")
def getFoodSite(selectedWeek):
    from getScripts import fetchFood
    weekFood = fetchFood(0,int(selectedWeek))
    if weekFood == "Error":
        return render_template('food.html',foodSend=[None,None,None,None],dagar=["Mån","Tis","Ons","Tor","Fre"],selectedWeek=selectedWeek,isError=True)
    else:
        return render_template('food.html',foodSend=[weekFood[x] for x in range(0,len(weekFood)-1,2)],dagar=["Mån","Tis","Ons","Tor","Fre"],selectedWeek=selectedWeek,isError=False)

def bootServer(ipInput):
    try:
        app.run(debug=False,host=ipInput[0],port=ipInput[1])
    except OSError:
        input("ERROR : Incorrect IP")
    else:
        pass

if __name__ == "__main__":
    try:
        ipConfig = []
        with open("private.txt","r+") as f:
            for x in f.readlines():
                ipConfig.append(x.strip("\n"))
        app.run(debug=False, host=ipConfig[0], port=ipConfig[1])
    except FileNotFoundError:
        input("ERROR : Could not find IP file, please create a file called 'ip.txt' in the root and put server ip and port")
    except OSError:
        input("ERROR : Incorrect IP")
    else:
        pass