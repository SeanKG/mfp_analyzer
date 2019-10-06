import urllib  # accessing site
import http.cookiejar as cookielib  # storing cookies for access
from bs4 import BeautifulSoup  # for reading data from site
import time  # for sleep timers between page requests
import datetime  # organizing dates to scrape
import pandas as pd  # dataframe workhorse
import json # for json structured calorie/macro goals from MFP
import sqlite3 # for loading data into db
from selenium import webdriver
import selenium as selenium
import warnings
warnings.filterwarnings('ignore')

class MfpExtractor(object):
    def __init__(self, username, password):
        # url for website
        self.base_url = 'http://www.myfitnesspal.com'
        # login action we want to post data to
        self.login_action = '/account/login'
        # file for storing cookies
        self.cookie_file = 'mfp.cookies'

        # user provided username and password
        self.username = username
        self.password = password

        # set up a cookie jar to store cookies
        self.cj = cookielib.MozillaCookieJar(self.cookie_file)

        # set up opener to handle cookies, redirects etc
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPRedirectHandler(),
            urllib.request.HTTPHandler(debuglevel=0),
            urllib.request.HTTPSHandler(debuglevel=0),
            urllib.request.HTTPCookieProcessor(self.cj)
        )

        self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    def access_page(self, path, num_days):
        # strip the path
        path = path.lstrip('/')
        path = path.rstrip('/')

        # construct the url
        url = self.base_url + '/' + path + '/' + str(num_days)
        print('Retrieving the page ' + str(url))

        # retrieve the web page
        try:
            response = self.opener.open(url)
        except urllib.error.HTTPError as e:
            raise e
        except urllib.error.URLError as e:
            raise e

        # return the data from the page
        return response.read()

    # method to do login
    def login(self):

        # open the front page of the website to set and save initial cookies
        response = self.opener.open(self.base_url)
        soup = BeautifulSoup(response)
        token = soup.find('input', attrs={'name': 'authenticity_token'})['value']

        login_data = urllib.parse.urlencode({
            'username': self.username,
            'password': self.password,
            'remember_me': True,
            'authenticity_token': token
        }).encode('ascii')

        # construct the url
        login_url = 'https://www.myfitnesspal.com' + self.login_action
        # then open it
        try:
            self.opener.open(login_url, login_data)
        except urllib.error.URLError as e:
            raise e
        # save the cookies
        self.cj.save()

    # method to get progress data i.e. weight and any custom entries
    def get_progress_report(self, path, num_days):
        report_path = 'reports/results/progress/' + path
        return self.access_page(report_path, num_days)

    # method to get nutrition data i.e. macros, micros, cals
    def get_nutrition_report(self, path, num_days):
        report_path = 'reports/results/nutrition/' + path
        return self.access_page(report_path, num_days)

    def get_fitness_report(self, path, num_days):
        report_path = 'reports/results/fitness/' + path
        return self.access_page(report_path, num_days)
