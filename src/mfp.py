import urllib  # accessing site
import cookielib  # storing cookies for access
from bs4 import BeautifulSoup  # for reading data from site
import time  # for sleep timers between page requests
import datetime  # organizing dates to scrape
import pandas as pd  # dataframe workhorse
import json # for json structured calorie/macro goals from MFP
import sqlite3 # for loading data into db
from selenium import webdriver
import selenium as selenium
import warnings
from extractor import MfpExtractor
warnings.filterwarnings('ignore')

def start_extract(un, pw, *args):
    """
    This will scrape MFP for all user's data

    :param un: username(str)
    :param pw: password(str)
    :param args: start date(datetime object)
                OR default last 1500 days if none entered
    :return: pandas dataframe indexed by date containing profile MFP info
             pandas dataframe indexed by date containing all nutritional+etc MFP info
    """

    username = un
    password = pw

    # check how many days to retrieve
    if len(args) == 1:
        # start date specified
        start_date = datetime.datetime.strptime(args[0], "%Y-%m-%d").date()
        end_date = datetime.date.today()
        num_days = (end_date - start_date)
#        start_date = end_date - datetime.timedelta(args[0])    
    else:
        # no dates specified, default to 1500 days from today ( about 4 years)
        end_date = datetime.date.today()
        num_days = datetime.timedelta(days=1500.0)
        start_date = end_date - num_days

    print('Retrieving data for %s days' % str(num_days.days+1))

    # initialise an MfpExtractor and login to the website
    mfp = MfpExtractor(username, password)
    mfp.login()

    def scrapeProfile():
        profiledict = {}

        # guided_goals
        time.sleep(3)
        html = mfp.access_page('account/change_goals_guided/', un,'')
        soup = BeautifulSoup(html)

        # determine whether imperial or metric
        profiledict['Imperial'] = [True]
        if soup.find('label', {'for':'weight_value_display_value'}).string != 'lbs':
            profiledict['Imperial'] = [False]
        profiledict['GoalWeight'] = [float(soup.find('input', {'id':'profile_goal_weight_display_value'})['value'])]
        
        # determine gender
        profiledict['Gender'] = ['male']
        if soup.find_all('input', {'checked':'checked', 'name':'profile[sex]'})[0]['value'] != 'M':
            profiledict['Gender'] = ['female']


        # determine activity level
        activitydict = {'1': 'sedentary', '2': 'light', '3': 'moderate', '4': 'heavy'}
        profiledict['Activity'] = [activitydict[soup.find_all('input', {'checked': 'checked', 'name': 'profile[pal]'})[0]['value']]]

        # determine weekly weight loss desired
        profiledict['WeeklyChange'] = [float(soup.find('select', {'id': 'profile_goal_loss_per_week'}).find('option', {'selected':'selected'})['value'])]

        # determine height in inches or cm
        if profiledict['Imperial'] == [True]:
            ftquery = float(soup.find_all('input', {'id': 'profile_height_large_value'})[0]['value'])
            inquery = float(soup.find_all('input', {'id': 'profile_height_small_value'})[0]['value'])
            profiledict['Height'] = [round(ftquery*12 + inquery, 1)]
        else:
            profiledict['Height'] = [float(soup.find_all('input', {'id': 'profile_height_display_value'})[0]['value'])]


        # determine age
        # UPDATED FOR NEW CHANGES
        url = 'profile/' + un + '/'
        html = mfp.access_page(url, '')
        soup = BeautifulSoup(html)
        profiledict['Age'] = soup.find_all('h5')[0].get_text().split(" ")[0]
#         dob = [int(x['value']) for x in soup.find_all('option', {'selected':'selected'}, limit=3)]
#         dob = datetime.date(dob[2], dob[0], dob[1])
#         today = datetime.date.today()
#         profiledict['Age'] = [today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))]

            
        # macro goals
        
        # Obsolete due to changes in site to javascript
#         time.sleep(3)
#         html = mfp.access_page('account/my_goals/','')
#         soup = BeautifulSoup(html)

#         query = soup.find_all(lambda tag: tag.name == 'script' and len(tag.attrs) == 0)#[1].string[70:-105]
#         jsonprep = '{%s}' % (query.split('{', 1)[1].rsplit('}', 1)[0],)
#         jsoned = json.loads(jsonprep)

#         profiledict['CalGoal'] = [jsoned['user']['goal_preferences']['daily_energy_goal']['value']]
#         profiledict['CarbRatio'] = [jsoned['user']['goal_preferences']['carb_ratio']]
#         profiledict['ProteinRatio'] = [jsoned[#39;user']['goal_preferences']['protein_ratio']]
#         profiledict['FatRatio'] = [jsoned['user']['goal_preferences']['fat_ratio']]
        
        url = 'http://www.myfitnesspal.com/account/my_goals/daily_nutrition_goals'
        driver = webdriver.PhantomJS()
        driver.set_window_size(1120, 550)

        driver.get(url)
        driver.implicitly_wait(10)

        if driver.current_url == url:
            # we are logged in getting results
            pass
        else:
            # log in if necessary using this engine
            # print("Logging In")
            try:
                username = driver.find_element_by_id("username").send_keys(un)
                password = driver.find_element_by_id("password").send_keys(pw)

                driver.find_element_by_xpath("//input [@type='submit' and  @value='Log In']").click()
                time.sleep(10)
            except:
                pass

        # check that we are in the right place now, else redirect
        if driver.current_url == url:
            pass
        else:
            driver.get(url)
            time.sleep(10)

        profiledict['CalGoal'] = driver.find_element_by_xpath("//input [@type='text' \
                                    and  @id='ember1677']").get_attribute("value")
        profiledict['CarbRatio'] = webdriver.support.ui.Select(driver.find_element_by_id('ember1728'))\
                                    .first_selected_option.text.strip("%")
        profiledict['FatRatio'] = webdriver.support.ui.Select(driver.find_element_by_id('ember1780'))\
                                    .first_selected_option.text.strip("%")
        profiledict['ProteinRatio'] = webdriver.support.ui.Select(driver.find_element_by_id('ember1824'))\
                                    .first_selected_option.text.strip("%")

        profiledf = pd.DataFrame.from_dict(profiledict, dtype='float')

        return profiledf

    def scrapeData():
        dates = [start_date + datetime.timedelta(days=x) for x in range(0, num_days.days+1)]

        totaldict = {}

        # fitness measurements
        fitness_paths = {'ExerciseMins': 'Exercise%20Minutes', 'CalsBurned': 'Calories%20Burned'}
        for key in fitness_paths:
            time.sleep(3)
            html = mfp.get_fitness_report(fitness_paths[key], num_days.days+1)
            soup = BeautifulSoup(html)
            vals = soup.find_all('number')
            temp = []
            for val in vals:
                temp.append(val.string)
            totaldict[key] = temp

        '''
        progress measurements including custom entries, for custom entries go to
        "view-source:http://www.myfitnesspal.com/reports" in your browser and search for 
        "MFP.Reports.menu.init". Immediately following you will find a similar dict 
        structure with any custom variables. Below I include an example using my custom 
        entry "Body Fat"
        '''
        prog_paths = {'Weight': '1', 'Bodyfat': '94738698'}
        # bodyfat is a custom measurement example, remove or replace here and below in orderedcols
        for key in prog_paths:
            time.sleep(3)
            try:
                html = mfp.get_progress_report(prog_paths[key], num_days.days+1)
                soup = BeautifulSoup(html)
                vals = soup.find_all('number')
                temp = []
                for val in vals:
                    temp.append(val.string)
                totaldict[key] = temp
            except:
                print('No ' + str(key) + ' found.')

        # nutrition measurements
        nutr_paths = {'Calories': 'Calories', 'Carbs': 'Carbs', 'Fat': 'Fat', 'Protein': 'Protein',
                      'Fiber': 'Fiber', 'Sugar': 'Sugar', 'SatFat': 'Saturated%20Fat',
                      'PolyFat': 'Polyunsaturated%20Fat', 'MonoFat': 'Monounsaturated%20Fat',
                      'TransFat': 'Trans%20Fat', 'Cholesterol': 'Cholesterol', 'Sodium': 'Sodium',
                      'Potassium': 'Potassium', 'VitA': 'Vitamin%20A', 'VitC': 'Vitamin%20C',
                      'Iron': 'Iron', 'Calcium': 'Calcium', 'NetCals': 'Net%20Calories'}
        for key in nutr_paths:
            time.sleep(3)
            html = mfp.get_nutrition_report(nutr_paths[key], num_days.days+1)
            soup = BeautifulSoup(html)
            vals = soup.find_all('number')
            temp = []
            for val in vals:
                temp.append(val.string)
            totaldict[key] = temp
            
        mfp_daily = pd.DataFrame.from_dict(totaldict, orient='columns', dtype='float')
        mfp_daily.index = dates
        mfp_daily.index.name = 'Date'

        # note that bodyfat is a custom column below, remove if only using default MFP categories
        orderedcols = ['Weight', 'Calories', 'Protein', 'Fat', 'Carbs', 'Fiber', 'Sugar', 'Sodium', 'SatFat',
                       'TransFat', 'PolyFat', 'MonoFat', 'Cholesterol', 'Potassium', 'VitA', 'VitC',
                       'Iron', 'Calcium', 'Bodyfat', 'ExerciseMins', 'CalsBurned', 'NetCals']

        mfp_daily = mfp_daily[orderedcols]

        print("Done scraping " + str(num_days.days+1) + " days worth of data.")

        return mfp_daily

    return scrapeProfile(), scrapeData()


def loadMfp(username, password, mfpDB="mfp_clean.db", *args):
    conn = sqlite3.connect(mfpDB)
    mfp_profile, mfp_data = start_extract(username, password, *args)
    mfp_profile.to_sql('mfp_profile', conn, if_exists='replace')
    mfp_data.to_sql('mfp_data', conn, if_exists='replace')
    conn.commit()
    conn.close()
