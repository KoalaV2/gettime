# GetTime/Sodschema
Get schedule for NTI gymnasiet söderntörn.

***

## How does `settings.json` work?

```json
{
    "DEBUGMODE": false,
    "ip": "0.0.0.0",
    "port": "5000",
    "logToFile": true,
    "logToSameFile": true,
    "logFileLocation": "logs/",
    "mainLink": "http://0.0.0.0:5000/",
    "key": "",
    "enableErrorHandler": true,
    "discordKey": "",
    "discordPrefix": "!gt",
    "discordRGB": [138,194,241],
    "formLink": ""
}
```

### DEBUGMODE
Enables or disables debug mode. This should always be set to false on the live server.

### ip
The IP address the server will run on.

### port
The port that the server will run on.

### logToFile
If set to true, then all the logging will be sent to a file, instead of the console window. This applies to both the main program and the Discord bot

### logToSameFile
If set to true, then it will create one log file, and overwrite it every time you start the server. If you set it to false, then it will instead create new files for every time you run it, with the current date as the filename. 

### logFileLocation
Where the log files should go (Default is “logs/”)

### mainLink
This is where you put the URL that the server will run on. (So for the live server it should be https://www.gettime.ga/, but if you are running it on your own computer for testing, then it should be the same as your IP:port with “http://” in front and “/” at the end) If this is not set correctly, then many features will break!

### key
Key is just a random string of characters. It is used in some places to create hashes and stuff, and if it is changed, then no private URLs will work anymore (And probably some other stuff too).

### enableErrorHandler
This enables or disables the custom error catcher. Most of the time, when something goes wrong with the Python backend, it should display the traceback, which helps programmers to know what went wrong without having to find the error in the logs. I don’t know why you would want to turn it off, but if you do, then it will instead just display the regular “Server is busy or unresponsive” error page. The only exception to this error handler is 404 errors (missing files), as the default 404 error page is easier to understand than what the error handler spits out.

### discordKey
API key to the Discord bot.

### discordPrefix
The prefix used by the Discord bot.

### discordRGB
The RGB code that the Discord bot will use in most places.

### formLink
Link to a Google form, where users can request their school to be added.

***

## How does `schools.json` work?

Here is an example of what one entry in `schools.json` could look like.

```json
{
    "NTI Södertörn": {
        "id": 0, 
        "name": "NTI Södertörn",
        "Referer": "https://web.skola24.se/timetable/timetable-viewer/it-gymnasiet.skola24.se/IT-Gymnasiet%20S%C3%B6dert%C3%B6rn/",
        "host": "it-gymnasiet.skola24.se",
        "unitGuid": "ZTEyNTdlZjItZDc3OC1mZWJkLThiYmEtOGYyZDA4NGU1YjI2",
        "lunchLink": "https://skolmaten.se/nti-gymnasiet-sodertorn/"
    }
}
```

### id
This is a number assigned to every school. This number is the value that gets saved in your cookies when you select what school you want. This number should never be changed, and if for some reason a school needs to be removed, the ID of that school should never be reused again. This is to ensure that no other private links breaks, as they contain the ID number, and not the actual name of the school.

### name
Should be the same as the key for that entry.

### Referer
KOALA FILL THIS IN PLZ

### host
KOALA FILL THIS IN PLZ

### unitGuid
KOALA FILL THIS IN PLZ

### lunchLink
This should contain a link to the school lunch for that school.

***

# Credit
Thanks to https://github.com/PierreLeFevre for creating Sodschema.

Thanks to https://github.com/TayIsAsleep for creating the original GetTime code, and for porting and updating Sodschema's code.

Thanks to https://github.com/KoalaV2 for creating the new backend and for hosting the website.
