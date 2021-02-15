# https://web.skola24.se/timetable/timetable-viewer/it-gymnasiet.skola24.se/IT-Gymnasiet%20S%C3%B6dert%C3%B6rn/
import selenium,time,hashlib,os,logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',level=logging.INFO,datefmt='%Y-%m-%d %H:%M:%S')
status = "Busy"
debugmode = False

#region Selenium First Time Setup
headless = False
chrome_options = webdriver.ChromeOptions()
if headless:
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("window-size=1920,1080")
driver = webdriver.Chrome("chromedriver.exe",chrome_options=chrome_options)
driver.maximize_window()
driver.get('https://web.skola24.se/timetable/timetable-viewer/it-gymnasiet.skola24.se/IT-Gymnasiet%20S%C3%B6dert%C3%B6rn/')
try:
    myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'w-input')))
except TimeoutException:
    logging.info("Loading took too much time!")
inputAngeID = driver.find_element_by_class_name("w-input")
inputAngeID.clear()
inputAngeID.send_keys("19_tek_a")
inputAngeID.send_keys(Keys.ENTER)
inputVecka = driver.find_element_by_xpath("//div[2]/div[1]/div[@class='w-combobox w-block' and 1]/input[@class='w-text w-block' and 1]")
bodyWait = driver.find_element_by_xpath("html/body")
schema = driver.find_element_by_xpath("//div[@class='w-panel']/div[2]")
entireThing = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[2]')

buttonsWeek = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[1]/div[2]/div/ul/li[1]/button')
buttonsMon  = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[1]/div[2]/div/ul/li[2]/button')
buttonsTue  = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[1]/div[2]/div/ul/li[3]/button')
buttonsWed  = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[1]/div[2]/div/ul/li[4]/button')
buttonsThu  = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[1]/div[2]/div/ul/li[5]/button')
buttonsFri  = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div[1]/div[2]/div/ul/li[6]/button')

logging.info("getTimeMain first time setup is finished")
#endregion

myLastThing = 0

def turnOff():
    try:
        driver.quit()
        return True
    except:
        return False

def waitForLoading(timeOut):
    timeOutMax = timeOut
    timeOutTime = time.time()
    while bodyWait.get_attribute("class").strip() == "pace-done":
        logging.info("Waiting for page to start loading...")
        if time.time() - timeOutTime > timeOutMax:
            logging.info("STOP")
            break
    logging.info("Page started loading!")
    timeOutTime = time.time()
    while bodyWait.get_attribute("class").strip() == "pace-running":
        logging.info("Waiting for page to finish loading...")
        if time.time() - timeOutTime > timeOutMax:
            logging.info("STOP")
            break
    logging.info("Page finished loading!")
def get_for(current,*args):
    global status,myLastThing
    def hashMe(toBeHashed):
        return str(hashlib.md5(str.encode(str(toBeHashed))).hexdigest())
    
    key = f"{current[1]}{current[2]}{current[4]}{current[5]}" #Id,Week,Year,Day
    hash_object = hashMe(key)
    
    try:
        logging.info(current)
        logging.info(f"Request from {hash_object}")

        if status == "Ready":
            status = "Busy"
            logging.info(f"{hash_object} turn! Status is now 'Busy'")
            
            if myLastThing != current[5]:
                logging.info(f"{hash_object} Needs to change day")
                before = hashMe(entireThing.get_attribute('innerHTML'))
                if current[5] == 0:
                    buttonsWeek.click()
                elif current[5] == 1:
                    buttonsMon.click()
                elif current[5] == 2:
                    buttonsTue.click()
                elif current[5] == 3:
                    buttonsWed.click()
                elif current[5] == 4:
                    buttonsThu.click()
                elif current[5] == 5:
                    buttonsFri.click()
                else:
                    before = False
                if before != False:
                    while before == hashMe(entireThing.get_attribute('innerHTML')):
                        time.sleep(0.1)
                myLastThing = current[5]
                logging.info(f"{hash_object} Passed Changed day")
            else:
                logging.info(f"{hash_object} had the same day as the last retard")

            # if current[0] == "m" and current[5] != 0:
            #     driver.set_window_size(10,1080)
            # else:
            #     driver.maximize_window()

            #logging.info(f"{hash_object} Passed ")

            inputAngeID.clear()
            inputAngeID.send_keys(current[1])
            inputAngeID.send_keys(Keys.ENTER)

            while True:
                logging.info("waiting for inputVecka...")
                if inputVecka.is_displayed() and inputVecka.is_enabled():
                    break
                time.sleep(0.1)
                
            logging.info(f"{hash_object} Passed the test")

            inputVecka.clear()
            inputVecka.send_keys(f"v.{current[2]}, {str(current[4])}")
            inputVecka.send_keys(Keys.ENTER)
            #waitForLoading(2)

            time.sleep(1)


            def textSize(textInput,biggestFontOnSite,increaseFontsizeBy):
                for x in range(biggestFontOnSite):
                    textInput = textInput.replace(f"font-size: {x}px;","font-size: " + hashMe(f"{x}") + "px;")
                for x in range(biggestFontOnSite):
                    textInput = textInput.replace("font-size: " + hashMe(f"{x}") + "px;",f"font-size: {(x+increaseFontsizeBy)}px;")
                return textInput


            a = entireThing.get_attribute('innerHTML')
            a = a.replace('<img src="/timetable/timetable-viewer/Content/img/default_timetable_ng.png" alt="Skola24">',"")
            a = a.replace('<svg','<svg style="position: absolute; left: 0; top: 0; width: 100%; height: 100%;"')
            if current[0] == "m":
                #a = a.replace('<svg','<svg preserveAspectRatio="none"')
                #a = a.replace('<div class="w-timetable" style="position: relative; width: 100%; height: 656px;"','<div class="w-timetable" ')
                a = textSize(a,30,3)

            # with open(f"./static/{hash_object}_before.txt","w+") as f:
            #     f.write(a)

            if len(a) < 200:
                logging.info(f"{hash_object} was shorter then expected! ({len(a)})")
                status = "Ready"
                return "Error"

            logging.info(f"Finished working on {hash_object}, setting status to Ready")
            status = "Ready"    
            return a
        else:
            logging.info(f"GetTime not ready for {hash_object}")
            status = "Ready"
            return "Not ready"
    except Exception as e:
        logging.info(f"GETTIME ERROR: {e}, {hash_object}")
        status = "Ready"
        return "Error"

status = "Ready"
if __name__ == "__main__":
    get_for(['2', '19_tek_a', 48, False, 2020, 0])
else:
    logging.info("Imported Get_Time.py")