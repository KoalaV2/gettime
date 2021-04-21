#!/bin/sh

echo "Chowning path so koala can write to path"

sudo chown -R koala gettime

cd gettime

echo "Git pulling"

git pull 


cd ..

echo "Chowning back permissions to gettime"

sudo chown -R gettime gettime

echo "Restarting gettime service"

sudo systemctl restart gettime

sleep 1.5

sudo systemctl status gettime
