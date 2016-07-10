#!/bin/bash

rm lambda.zip
cd env/lib/python2.7/site-packages
zip -r9 ~/lambda/lambda.zip *
cd ~/lambda
zip -g lambda.zip handler.py

aws lambda delete-function --function-name InvenCrawler
aws lambda create-function \
    --region ap-northeast-1 \
    --function-name InvenCrawler \
    --zip-file fileb://lambda.zip \
    --role arn:aws:iam::975971076875:role/lambda_crawler_exec_role  \
    --handler handler.my_handler \
    --runtime python2.7 \
    --timeout 300 \
    --memory-size 128
