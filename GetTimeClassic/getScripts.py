import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')

def getFilename(user_message,convert,*args):
    #"""Takes an input, and then a bool (if you want to convert it from NSID to SID) and then returns path to the file it created"""

    import getTime_HTML as gthtml
    if user_message == False or type(user_message) != str:
        return "Error"
    else:
        SID = user_message
        if convert:
            SID = getConvertUrl(SID)        
        
        if SID == "Error":
            return "Error"

        else:
            fromGT = "Not ready"
            while fromGT == "Not ready": #Keeps asking for the file name untill its done
                if len(args) > 0:
                    fromGT = gthtml.get_for(SID,args[0])
                else:
                    fromGT = gthtml.get_for(SID)
            if fromGT == "Error":
                return "Error"
            else:
                return [fromGT,SID]

def getConvertUrl(functionInput):
    """
    Converts NSID to SID [VX  ID  WEEK FORCE YEAR DAY]
    
    VX  ID  WEEK FORCE YEAR DAY
    
    STR STR INT  BOOL  INT  INT
    
    0   1   2    3     4    5
    """
    try:
        import datetime as d
        from getScripts import getToday
        li = functionInput.split("-") #Splits up the link into parts

        if li == ['']: #If input is empty
            logging.info("getConvertUrl : input list is empty")
            return "Error"
        #Default settings
        sVersion = "0" #!!!!HAS TO BE STRING!!!!
        sId = ""
        sWeek = 0 #0 means current week
        sForce = False
        sYear = int(d.datetime.now().year)
        sDay = 0 #0 is week, 1-5 is mon-friday
        nextWeekOffset = 0

        #CHECK VERSION
        sVersion = "2" 
        if li[0].lower() in ["v1","v2","v3","vm"]: #If link contains version data
            sVersion = li[0][1:] #sVersion = str(((li[0].lower()).split("v"))[1]) #Set linkStyle to the current linkversion

        #CHECK FORCE
        if "force" in li:
            sForce = True

        #SET SETTINGS
        if str(sVersion) == "0":
            sId,sWeek,sYear = li[0],li[1],int(li[2])
            if len(li) == 4 and sForce == False:
                sDay = int(li[3]) #this one was fucked
                sVersion = "m" #this one was fucked
            elif len(li) == 5 and sForce == True:
                sDay = int(li[4]) #this one was fucked
                sVersion = "m" #this one was fucked
            else:
                pass
        elif sVersion == "1":
            sId = li[1]
            if len(li) == 3:
                sWeek = li[2]
                if sForce:
                    sWeek = 0
            if len(li) == 4:
                sWeek = li[2]
        elif sVersion == "2":
            sId = li[0] #Set ID to ID
        elif sVersion == "3":
            sId,sWeek,sYear,sDay = li[1],li[2],li[3],li[4]
            if sForce == True:      
                sYear,sDay = li[4],li[5]
        elif sVersion == "m":
            sId = li[1]
            sDay = getToday()
        
        if getToday() == 0:
            nextWeekOffset = 1
        if int(sWeek) == 0:
            sWeek = getAbsoluteTime()[6]
            #sWeek = int(d.date.today().isocalendar()[1])

        if getAbsoluteTime()[2] > 18 and sVersion == "m":
            if sDay != 5:sDay +=1
            elif sDay == 0:sDay = 1
            else:pass

        if sId != "":
            return [str(sVersion),str(sId),int(sWeek)+nextWeekOffset,bool(sForce),int(sYear),int(sDay)]         
        logging.info("getConvertUrl : sId was empty")
        return "Error"
    except Exception as e:
        logging.info(f"getConvertUrl : fell into except ({e})")
        return "Error"

def getToday():
    """Returns int of current day (mon-fri = 1-5, sat-sun = 0 (full week))"""
    import datetime as d
    a=d.datetime.today().isoweekday()
    if a>=1 and a<=5:return a
    return 0

# def getFood():
#     """Fetches food from the website and saves it in the text file"""
#     import requests,time as t
#     t0=t.time()
#     url,headers = "https://skolmaten.se/nti-gymnasiet-sodertorn/",{'User-Azgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
#     logging.info("getFood is getting website...")
#     website = requests.get(url, headers=headers).text.split("\n")
#     logging.info(f"Website gotten, took {t.time()-t0}")
#     def insiderGetFood(whatDay):
#         foundings=0
#         for x in range(len(website)):
#             if website[x].strip() == '<div class="items"><p>': #str(x).endswith('<div class="items"><p>'):
#                 if foundings == whatDay:return str(website[x+1]).strip()
#                 else:foundings += 1
#     with open("getFood.txt","w")as f:
#         for y in range(5):
#             f.write(f'{insiderGetFood(y)[6:-14].replace("&amp;","&").strip("</s")}\n')
#     logging.info(f"getFood finished, took {t.time()-t0} in total")
#     return []

# def fetchFood(requestedDay):
#     """Fetches food for you for a sepecific day, or all days if 0"""
#     import os
#     if not os.path.exists("getFood.txt"):
#         logging.info("Could not find getFood.txt, starting to generate now.")
#         getFood()
#     with open("getFood.txt","r")as f:
#         if requestedDay==0:
#             return[x.strip("\n") for x in f.readlines()]
#         return f.readlines()[requestedDay-1].strip("\n")

def getCacheClearer(fName,maxAge):
    """Deletes old cached images from the server"""
    import os.path,time#,winshell
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    cDel,cSkip,tNow=0,0,time.time()
    logging.info(f"Clearing files older then {str(maxAge)} in {fName}\n") #Sets path to the right thing  
    for filename in os.listdir(fName):
        fDir=f"{fName}/{filename}"
        fAgeM=round((tNow-os.path.getmtime(fDir))/60) #Sets fDir to the full path to the current file
        if filename[0]=="_":
            logging.info(f"Skipped '{filename}' because it was tagged with '_'")
            cSkip+=1
        else:
            if fAgeM>=maxAge:
                os.remove(fDir)
                logging.info(f"Deleted '{filename}' because it was to old. ({fAgeM} minutes old)")
                cDel+=1 #If age is older then maxAge:   
            else:
                logging.info(f"Skipped '{filename}' because it wasn't old enough. ({fAgeM} minutes old)")
                cSkip+=1
    #winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False);logging.info(f"Deleted {cDel} files and skipped {cSkip} files out of all {cDel+cSkip} files in the folder.\n")

def getAbsoluteTime():
    """Returns list with
    
    [Secounds, Minutes, Hours, Day(date), Month, Year, WeekNum, Day(0/1-5)]"""
    # Returns list with 
    # Secounds, Minutes, Hours, Day(date), Month, Year, WeekNum, Day(0/1-5)
    # 0         1        2      3          4      5     6        7
    from time import localtime,strftime
    from datetime import date
    from getScripts import getToday
    a = [int(x) for x in strftime(f"%S/%M/%H/%d/%m/%Y/{date.today().isocalendar()[1]}/{getToday()}",localtime()).split("/")]
    return a
    # if len(args)>0 and args[0]<len(a)and args[0]>0:
    #     return a[args[0]]

def getAbsoluteTime2():
    """Returns list with
    
    [Secounds, Minutes, Hours, Day(date), Month, Year, WeekNum, Day(0/1-5)]"""
    b = getAbsoluteTime()
    return {
        'secounds':b[0],
        'minutes':b[1],
        'hours':b[2],
        'day':b[3],
        'month':b[4],
        'year':b[5],
        'week':b[6],
        'daynum':b[7]    
    }

def getFood(requestedWeek):
    try:
        if requestedWeek == 0:
            requestedWeek = getAbsoluteTime()[6]
        logging.info("Starting getFood...")
        import selenium, time
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--log-level 3")
        chrome_options.add_argument('--disable-logging') 
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        logging.info("Loading Chrome...")
        driver = webdriver.Chrome("chromedriver.exe",chrome_options=chrome_options)
        logging.info("Chrome loaded.")

        driver.get("https://skolmaten.se/nti-gymnasiet-sodertorn/")

        weekOnPage = int(driver.find_element_by_xpath('/html/body/main/div[1]/div[1]/div[1]/h3/span').text)
        if int(requestedWeek) != weekOnPage:
            nextWeekButton = driver.find_element_by_xpath('//*[@id="controls"]/a[1]')
            previousWeekButton = driver.find_element_by_xpath('//*[@id="controls"]/a[2]')
            while int(requestedWeek) != weekOnPage:
                if int(requestedWeek) > weekOnPage:
                    logging.info("up")
                    driver.execute_script("arguments[0].click();", nextWeekButton)
                    weekOnPage += 1
                else:
                    logging.info("down")
                    driver.execute_script("arguments[0].click();", previousWeekButton)
                    weekOnPage -= 1
                time.sleep(0.5) 
                
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,f'//*[@data-week-of-year="{requestedWeek}"]/*[2]')))
        foodExist = True if (driver.find_element_by_xpath(f'//*[@data-week-of-year="{requestedWeek}"]/*[2]').get_attribute('class') == "row") else False
        
        toReturn = []
        if foodExist:
            with open(f"getFood{requestedWeek}.txt","w") as f:
                for currentDay in range(1,6,1):
                    #foodA = driver.find_element_by_xpath(f'/html/body/main/div[1]/div[1]/div/div[{currentDay}]/div[2]/p[1]/span').text.strip("\n")
                    #foodB = driver.find_element_by_xpath(f'/html/body/main/div[1]/div[1]/div/div[{currentDay}]/div[2]/p[2]/span').text.strip("\n")
                    foodA = driver.find_element_by_xpath(f'//*[@data-week-of-year="{requestedWeek}"]/div[{currentDay}]/div[2]/p[1]/span').text.strip("\n")
                    foodB = driver.find_element_by_xpath(f'//*[@data-week-of-year="{requestedWeek}"]/div[{currentDay}]/div[2]/p[2]/span').text.strip("\n")
                    toReturn.append(foodA)
                    toReturn.append(foodB)
                    f.write(f"{foodA}\n{foodB}\n")
            logging.info("getFood finished correctly.")
            driver.close()
            return toReturn
        else:
            logging.info("getFood did not run (foodExist was False)")
            driver.close()
            return None
    except Exception as e:
        logging.info(f"getFood error : {e}")
        driver.close()
        return None

def fetchFood(requestedDay,requestedWeek):
    import os
    if os.path.exists(f"getFood{requestedWeek}.txt"):
        with open(f"getFood{requestedWeek}.txt","r") as f:
            foodList = [x.strip("\n") for x in f.readlines()]
    else:
        logging.info(f"Could not find getFood{requestedWeek}.txt, starting to generate now.")
        a = getFood(requestedWeek)
        if a != None:
            foodList = [x.strip("\n") for x in a]
        else:
            return "Error"
    if requestedDay == 0:
        return foodList
    return (foodList[requestedDay-1],foodList[requestedDay])

def getMyHash(toBeHashed):
    import hashlib
    return str(hashlib.md5(str.encode(str(toBeHashed))).hexdigest())