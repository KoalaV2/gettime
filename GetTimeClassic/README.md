Style 0 (ID-WEEK-YEAR-FORCE):
	http://gettime.ga/schema/ID-WEEK-YEAR -day
	http://gettime.ga/schema/ID-WEEK-YEAR-force -day

Style 1 (VERSION-ID-WEEK-FORCE):
	http://gettime.ga/schema/v1-ID
	http://gettime.ga/schema/v1-ID-force
	http://gettime.ga/schema/v1-ID-WEEK
	http://gettime.ga/schema/v1-ID-WEEK-force

Style 2 (ID):
	http://gettime.ga/schema/ID
	http://gettime.ga/schema/ID-force

Style 3 (VERSION-ID-WEEK-FORCE-YEAR-DAY):
	http://gettime.ga/schema/v3-ID-WEEK-FORCE-YEAR-DAY

Style m (VERSION-ID)
	http://gettime.ga/schema/vm-ID

------------------------------------------------------------
CacheClearer.py :
	Runs in background, deletes old files from "/static". Wont delete files that start with "_"

discordbot2.py :
	Main script, imports all the others when it starts. (SHOULD CREATE "main.py")

Get_Time.py :
	TAKES : "Get_Time.get_for" takes my standard input data (SID) and screenshots the website
	RETURNS : If it failed, or if you are in cue, it returns False, when it succeeds, it returns the NAME of the file it created.

getFilename.py :
	TAKES : either a NSID, or SID, and then a bool (if True, it will try to convert NSID to SID, if False it will pass first argument into gettime (assuming its a SID)
	RETURNS : Path to requested file

urlCheck.py :
	TAKES : NSID
	RETURNS : SID

website.py :
	This script hosts the website