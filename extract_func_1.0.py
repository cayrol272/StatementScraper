# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 20:36:25 2022
version 1.0

@author: khairulakmal
"""
#import requests
import pdfplumber
import os, fnmatch
import re
import pandas as pd
from collections import namedtuple

#senarai file yang berada didalam sesautu directory dengan filter extention file
path = '.'
# path = '../Document family/Saham/Note Contract'

arr = fnmatch.filter(os.listdir(path), '*.pdf')
# sorted(arr)
# print(len(arr))
#print(arr)

# for y in range(len(arr)):
#     print(y)
#     print(arr[y])

combine = []
for x in range(len(arr)):

    data = path + '/' + arr[x]
    #print(data)
    
    with pdfplumber.open(data) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        
    Tx = namedtuple('Tx', 'contract stock_no price qty proceed brk_amt stamp clr_fee total_amt')
    Sx = namedtuple('Sx', 'dd mm yyyy stock_name brk_st')
    tx_line_re = re.compile(r'([A-z]{3}\d{1,}-\d{1,}) (\d\w{1,}) (\d{1,}\.\d{1,}) (\d{1,}) (\d{1,}.\d{1,}) (\d{1,}\.\d{1,}) (\d{1,}.\d{1,}) (\d{1,}.\d{1,}) (\-?\d{1,}.\d{1,})')
    stock_line_re = re.compile(r'(\d{2})\/(\d{2})\/(\d{4}) (\w.{1,}) (\d{1,}\.\d{1,})')
    
    line_items = []

    for line in text.split('\n'):
        line = tx_line_re.search(line)
        if line:
            #print(line.group(9))
            #print(line)
            contract = line.group(1)
            stock_no = line.group(2)
            price = line.group(3)
            qty = line.group(4)
            proceed = line.group(5)
            brk_amt = line.group(6)
            stamp = line.group(7)
            clr_fee = line.group(8)
            total_amt = line.group(9)
            line_items.append(Tx(contract, stock_no, price, qty, proceed, brk_amt, stamp, clr_fee, total_amt)) 

    stock_items = []
    for line in text.split('\n'):
        line = stock_line_re.search(line)
        if line:
            dd = line.group(1)
            mm = line.group(2)
            yyyy = line.group(3)
            stock_name = line.group(4)
            brk_st = line.group(5)
            stock_items.append(Sx(dd, mm, yyyy, stock_name, brk_st))    
            
    cx = namedtuple ('cx', 'dd mm yyyy contract stock_no stock_name price qty proceed brk_amt stamp clr_fee brk_st total_amt')
    
    y = len(stock_items)
    
    for x in range(y):
        combine.append(cx(stock_items[x].dd, stock_items[x].mm, stock_items[x].yyyy, line_items[x].contract, line_items[x].stock_no, stock_items[x].stock_name, line_items[x].price, line_items[x].qty, line_items[x].proceed, line_items[x].brk_amt, line_items[x].stamp, line_items[x].clr_fee, stock_items[x].brk_st, line_items[x].total_amt))
    

df_final = pd.DataFrame(combine)
df_final['Buy'] = df_final['contract'].str.contains('P')
df_final['Buy'] = df_final.Buy.map({True : 'Buy' , False : 'Sell'})
temp = df_final['date_temp'] = df_final['mm'] + '/' + df_final['dd'] + '/' + df_final['yyyy']
df_final.insert(0,'date', temp) 
df_final['date'] = pd.to_datetime(df_final['date'])
df_final = df_final.drop('date_temp',1)


#line_items

#stock_items

print("Total file extract: ", len(combine))

### run this to append existing csv file
path_csv = '.'
df_final.to_csv(path_csv + '/' + 'transaction.csv', mode = 'a', header = False, index = False) #append file existing

print("Extract succesfully done")

