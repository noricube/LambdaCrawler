# -*0 encoding: utf8 -*-
import boto3, botocore
import csv
import StringIO
import requests
from bs4 import BeautifulSoup
import math

class Crawler:
    s3 = None
    bucket = None

    def __init__(self):
        self.s3 = boto3.client('s3')
        self.bucket = 'qurare-crawler'

    def fetch_latest_count(self, board_id):
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key='count.' + board_id)
            return int(response['Body'].read())
        except (botocore.exceptions.ClientError) as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return 0
            raise e

    def save_latest_count(self, board_id, count):
        self.s3.put_object(Bucket=self.bucket, Key='count.' + board_id, Body=str(count))

    def fetch_latest_target_count(self, board_id):
        r = requests.get('http://www.inven.co.kr/board/powerbbs.php?come_idx=' + str(board_id))
        soup = BeautifulSoup(r.text, "html.parser")
        first_article = soup.find('tr', class_='ls tr tr2')
        bbsNo = first_article.find('td',class_= 'bbsNo').text
        return int(bbsNo)

    def fetch_article(self, board_id, article_id):
        url = 'http://www.inven.co.kr/board/powerbbs.php?come_idx=' + str(board_id) + '&l=' + str(article_id)
        r = requests.get(url)

        soup = BeautifulSoup(r.text, 'html.parser')

        try:
            come_idx = int(soup.find('input', id='forScrapForderSelectComeIdx')['value'])
            uid = int(soup.find('input', id='forScrapForderSelectUid')['value'])
            title = soup.find('div', class_='articleTitle').text.strip()
            content = soup.find('div', id='powerbbsContent').text.strip()
            date = soup.find('div', class_='articleDate').text.strip()
            writer = soup.find('div', class_='articleWriter').text.strip()

            article_document = {
                    'no': article_id,
                    'title': title,
                    'content': content,
                    'date': date,
                    'writer' : writer
            }
            return article_document
        except:
            return None

    def save_articles(self, board_id, articles):
        if articles.__len__() == 0:
            return

        output = StringIO.StringIO()

        article_writer = csv.writer(output, delimiter=',',quotechar='\'', quoting=csv.QUOTE_ALL)
        article_writer.writerow(['no', 'title', 'content', 'date', 'writer'])

        for x in articles:
            article_writer.writerow([x['no'], x['title'].encode('utf8'), x['content'].encode('utf8'), x['date'].encode('utf8'), x['writer'].encode('utf8')])

        file_id = int(math.floor(articles[0]['no'] / 10) * 10)
        self.s3.put_object(Bucket=self.bucket, Key=board_id +'/' + str(file_id), Body=str(output.getvalue()))

        print file_id

    def do(self):
        board_id = '3779'
        count = self.fetch_latest_count(board_id) + 1
        target = self.fetch_latest_target_count(board_id)

        articles = []
        for i in range(count, target):
            article = self.fetch_article(board_id, i)
            if article != None:
                articles.append(article)
            if i % 10 == 9:
                self.save_articles( board_id, articles )
                self.save_latest_count(board_id, i)
                articles = []

        if articles.__len__() > 0:
            self.save_articles( board_id, articles )
        #print self.fetch_article(board_id,1)
        #self.save_latest_count(board_id, count+1)

def my_handler(event, context):
        #output = StringIO.StringIO()
        #spamwriter = csv.writer(output, delimiter=',',quotechar='\'', quoting=csv.QUOTE_MINIMAL)
        #spamwriter.writerow(['aaaa'] * 5 + ['b'])
        #print output.getvalue()
        cralwer = Crawler()
        cralwer.do()

        return {'message' : 'ok'}

if __name__ == '__main__':
        my_handler(None, None)
