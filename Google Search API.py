# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 12:38:48 2018

@author: jweiss
"""

from googleapiclient.discovery import build
import pprint

api_key = 'AIzaSyDDwLAPEnFQ_20NwsDP-FNQv-RHmaUATBM'
search_engine = '014081993580904946958:bvg-u_w3xnw'


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']




results = google_search('apple stock price', api_key, search_engine, num=10)

[i for i in set([item for sublist in[[results[j][i] for i in [str(i) for i in results[0].keys() if str(i) in ('htmlFormattedUrl','formattedUrl')]]  for j in range(len(results))] for item in sublist])]








