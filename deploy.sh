#!/bin/bash

PROJECT_NAME=${PWD##*/}
ZIP_FILE="/tmp/$PROJECT_NAME.zip"
DEPLOYMENT_HOST="klapperslange1.semaphor.dk"
DEPLOYMENT_FOLDER="/opt/$PROJECT_NAME/$PROJECT_NAME-main"
SERVICE_NAME="$PROJECT_NAME.service"

git archive --format=zip --output $ZIP_FILE HEAD
scp $ZIP_FILE $DEPLOYMENT_HOST:/tmp/
rm $ZIP_FILE
ssh $DEPLOYMENT_HOST 'sudo unzip -o' $ZIP_FILE ' -d' $DEPLOYMENT_FOLDER
ssh $DEPLOYMENT_HOST 'rm' $ZIP_FILE

ssh $DEPLOYMENT_HOST 'cd' $DEPLOYMENT_FOLDER '&& sudo venv/bin/python3 manage.py collectstatic -l --no-input'
ssh $DEPLOYMENT_HOST 'sudo systemctl restart' $SERVICE_NAME
