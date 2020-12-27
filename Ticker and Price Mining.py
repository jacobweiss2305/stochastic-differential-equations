# -*- coding: utf-8 -*-
"""
Created on Thu Aug 02 09:56:01 2018

@author: jweiss
"""
#Ticker and Price Mining Process
from lxml import html  
from time import sleep
from urllib import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd
import imp
import os
import numpy as np
import sqlalchemy as sa
import requests
import bs4
from __future__ import division
import time
import datetime

fun = imp.load_source('env', "C:\\Users\\jweiss\\Desktop\\Python Codes\\my_functions.py")
auth = imp.load_source('env', os.environ['PYENV'])

sql = """  
with tmp as (select
	[tickerDate],
	[tickerID],
	[localPrice],
	case when lead(localBaseFXRate * localPrice) over (partition by tickerID order by tickerDate) = 0.0 then 0.0 else
		(lead(localBaseFXRate * localPrice) over (partition by tickerID order by tickerDate) / (localBaseFXRate * localPrice)) - 1 end priceChgDay
from
     tickerHistoryATAnalytics
)
select distinct 
	t.tickerID,
	att.description,
	att.name,
	att.bloombergTicker
from 
	tmp t
	left join atprod.[dbo].[TICKER] att on t.tickerID = att.tickerID
--	left join atprod.[dbo].[TICKER] att on t.tickerID = att.tickerID
where
	t.priceChgDay >= 1
	and t.priceChgDay is not null
	and att.putCallIndicator is null
     """
cnxn = auth.db_cnxn_pyodbc
companies = fun.getData(sql,None,cnxn)


#scrapes 5 google pages
def predictTickersGoogle(companyNames):
    search_pages = [['https://www.google.com/search?q='+j+'+ticker&ei=QlxsW9rYHMfKsQW587nADw&start='+i+'0&sa=N&biw=1857&bih=1103' 
                     for i in [str(i) for i in list(range(0,5))]] for j in [str(i) for i in companyNames]]
    res_list = [[requests.get(i) for i in search_pages[j]] for j in range(len(search_pages))]
    soup = [[bs4.BeautifulSoup(i.text,'lxml') for i in res_list[j]] for j in range(len(res_list))]
    bag = [[",".join([str(re.sub('[^A-Z]+',' ', i)) for i in filter(fun.visible, j.findAll(text=True)) 
            if len(str(re.sub('[^A-Z]+',' ', i))) >= 2]).replace(","," ") for j in soup[x]] for x in range(len(soup))]
    return [fun.most_common([x for y in [re.findall('[^NASDAQ\s][^NYSE\s][A-Z]{2,}',i) for i in bag[k]] for x in y]) for k in range(len(bag))]


a = [str(i) for i in companies['description'].tolist()][0:100]

def predictTickersBing(companyNames):
    search_pages = [['https://www.bing.com/search?q='+j+'+ticker&first='+i+'&FORM=PERE'  
                         for i in [str(i) for i in range(0,33,11)]] for j in [str(i) for i in companyNames]]
    res_list = [[requests.get(i) for i in search_pages[j]] for j in range(len(search_pages))]
    soup = [[bs4.BeautifulSoup(i.text,'lxml') for i in res_list[j]] for j in range(len(res_list))]
    secondary_pages = [list(set([i for j in [[i for j in [re.findall('https?://[A-Za-z0-9\-\.\/]+', str(link.get('href'))) for link in soup[b][z].findAll('a') if len(link) > 0]
                         for i in j][:-1] for z in range(len(soup[b]))] for i in j])) for b in range(len(soup))]
    ids = [["NO TICKER"] if len(x)==0 else x for x in [[i for j in [re.findall('[^NASDAQ|^\/NASDAQ][A-Z]{2,}', i) for i in secondary_pages[k] if len(re.findall('[A-Z]{2,}', i)) > 0] for i in j] for k in range(len(secondary_pages))]]
    return [fun.most_common(i) for i in ids]

companies

predictTickersBing(a)



#30 before CAPTCHA  
predictTickersGoogle(a)











































