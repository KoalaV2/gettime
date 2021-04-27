@echo off

set js="static/js" 
set css="static/css" 
set html="templates" 

python min.py %js% ".js" %css% ".css" %html% ".html"

pause