# -*- coding: utf-8 -*-
"""
Created on Thu Aug 02 09:31:38 2018

@author: jweiss
"""

#most used functions
import pyodbc as db
from urllib import urlopen
from bs4 import BeautifulSoup
import re
import time
import datetime
import pandas as pd
import pandas.io.sql as pds

def sendToExcel(dataFrame, fileName):
    writer = pd.ExcelWriter('C:/Users/jweiss/Desktop/' + fileName + '.xlsx', engine='xlsxwriter')
    dataFrame.to_excel(writer, sheet_name='returns')
    writer.save()


#tickers_list = ['AAPL','FDS']
#start = '01/01/2016'
#end = '08/01/2018'   
def priceScraper(tickerList, start, end):
    columns = ['timetrade','open','High','Low','Close','Volume','adjClose']
    url_list = [str('https://finance.yahoo.com/quote/'+i+'/history?period1='
                + str(int(time.mktime(datetime.datetime.strptime(start, "%m/%d/%Y").timetuple())))
                +'&period2='+str(int(time.mktime(datetime.datetime.strptime(end, "%m/%d/%Y").timetuple())))
                +'&interval=1d&filter=history&frequency=1d' ) for i in tickerList]
    BeautifulSoup_List = [str(BeautifulSoup(i, 'html.parser')) for i in [urlopen(i) for i in url_list]]
    text_start = "HistoricalPriceStore"
    text_end = "isPending"
    raw_data = [i[i.find(text_start)+len(text_start):i.rfind(text_end)][13:len(i)-3] for i in BeautifulSoup_List]
    pandas_list = [pd.DataFrame([[i.split(',') for i in [re.sub('[^0-9\.\}\,]+','',i).split('},') 
                    for i in raw_data][j] if len(i) > 1] for j in range(len([re.sub('[^0-9\.\}\,]+','',i).split('},') 
                    for i in raw_data]))][k]) for k in range(len(raw_data))]
    for i in range(len(pandas_list)):
        pandas_list[i].columns = columns
        pandas_list[i] = pandas_list[i].dropna()
        pandas_list[i] = pandas_list[i][['adjClose']]
        pandas_list[i] = pandas_list[i].apply(pd.to_numeric)
    return pandas_list

def getData(query,index_column,conn):
    if index_column is None:
        data = pds.read_sql_query(query,conn)
    else:
        data = pds.read_sql_query(query,conn,index_col = pd.to_datetime(index_column))
    return data

def most_common(lst):
    return max(set(lst), key=lst.count)

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('ascii', 'ignore'))):
        return False
    return True