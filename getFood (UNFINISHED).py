def NEW(requestedWeek):
    from lxml import html
    import requests

    def getbyxpath(website,xpath):
        return html.fromstring(requests.get(website).content).xpath(xpath)[0]

    url = "https://skolmaten.se/nti-gymnasiet-sodertorn/"
    with open(f"getFood{requestedWeek}.txt","w") as f:
        for currentDay in range(1,6,1):
            foodA = getbyxpath(url,f'//*[@data-week-of-year="{requestedWeek}"]/div[{currentDay}]/div[2]/p[1]/span').text.strip("\n")
            foodB = getbyxpath(url,f'//*[@data-week-of-year="{requestedWeek}"]/div[{currentDay}]/div[2]/p[2]/span').text.strip("\n")
            f.write(f"{foodA}\n{foodB}\n")
    #logging.info("getFood finished correctly.")


NEW(7)

def getFood(requestedWeek):
    try:
        if requestedWeek == 0:
            requestedWeek = getAbsoluteTime()[6]
        logging.info("Starting getFood...")


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
