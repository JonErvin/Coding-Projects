# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 09:14:06 2020

@author: Jon Ervin
"""

# Goal: Pull analyst ratings from MarketBeat

import requests
from bs4 import BeautifulSoup as bs
import re
import locale
import pandas as pd
import time

# Initialize locale (for converting to float) and Marketbeat URL string
locale.setlocale(locale.LC_ALL,'')
MARKETBEAT_NASDAQ_URL = 'http://www.marketbeat.com/stocks/NASDAQ/{0}'


# Function to download/organize HMTL and pull data out
# Input

def getdata(tick):
    
    url = MARKETBEAT_NASDAQ_URL.format(tick)
    page = requests.get(url)
    soup = bs(page.text, features=None, builder=None)
    
    key_string_1 = soup.find(string=re.compile('average rating score is'))
    key_string_2 = soup.find(string=re.compile('consensus price target of'))
    
    if key_string_1 == None:
        score = buy = hold = sell = 'n/a'
    
    else:
        list_1 = key_string_1.split()
        
        
        #list 1 values pulled (score, buy, hold, sell)
        score_index = list_1.index('score')
        score = float(list_1[score_index + 2].strip(','))
        buy = list_1[score_index + 7]
        hold = list_1[score_index + 10]
        sell = list_1[score_index + 14] 
    
    if key_string_2 == None:
        price_target = current = upside = 'n/a'
        return score, buy, hold, sell, price_target, current, upside
     
    else:
        list_2 = key_string_2.split()
        
        #List 2 values pulled (price target, upside/downside, current)
        price_target = locale.atof(list_2[7].strip('$,'))
        current_index = list_2.index('current')
        current = locale.atof(list_2[current_index + 3].strip('$.'))
        if list_2[current_index - 5] == 'downside':
            upside = locale.atof(list_2[current_index - 3].strip('%')) * -.01
        elif list_2[current_index - 5] == 'upside':
            upside = locale.atof(list_2[current_index - 3].strip('%')) * .01 
        else:
            upside = 0
        
        return score, buy, hold, sell, price_target, current, upside

# Function to run the script for a given ticker

def run_script(symbols_list):
    
    # initialize empty dataframe for results
    results = pd.DataFrame(columns=('symbol','company_name','score','buy','hold','sell','price_target','current','upside'))
    start_time = time.time()
    
    #iterate over list running getdata()
    for symbol, company_name in symbols_list.itertuples(index=False):
        loop_start = time.time()
        try:
            (score, buy, hold, sell, price_target, current, upside) = getdata(symbol)
            results = results.append({
                           'symbol':symbol,
                           'company_name':company_name,
                           'score':score,
                           'buy':buy,
                           'hold':hold,
                           'sell':sell,
                           'price_target':price_target,
                           'current':current,
                           'upside':upside},ignore_index=True)
            loop_end = time.time()
            print(symbol,' complete.  Time: ',loop_end-loop_start)
        except:
            print('Error: ',symbol, ' could not be completed.')
        
    end_time = time.time()
    print(end_time - start_time)
    
    return results
    
# Define symbol list and run

symbols = pd.read_csv('nasdaqlisted.csv')
symbols_list = symbols.iloc[:,0:2]
# symbols_list_test = symbols_list[0:100]
# symbols_list_test = ['AAPL','GOOGL','FB','NFLX']

results = run_script(symbols_list)

# Save results to file
results.to_csv('2021-12-01 Full Nasdaq.csv')




        