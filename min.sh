#!/bin/sh

js=("static/js")
css=("static/css")
html=("templates")

c() { echo "$(printf " %s " "$@")" | sed 's/,$//g' ; }

python min.py $(c "${js[@]}") ".js" $(c "${css[@]}") ".css" $(c "${html[@]}") ".html"
