@echo off

set js="static/js"
set css="static/css"
set html="templates"
set scss="static/scss"

python min.py %js% ".js" %css% ".css" %html% ".html" %scss% ".scss"

pause
