# mextract.py
"""
Created on Sat March 18 2023
version 1.0

@author: khairulakmal

"""

import pdfplumber
import os, fnmatch
import re
import pandas as pd
from collections import namedtuple
import matplotlib.pyplot as plt

class mextract:

    def __init__(self) -> None:
        pass

    def extract_pdf(self):
        
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

        # create combine list
        combine = []

        # interation to extract data from pdf
        for x in range(len(arr)):

            data = path + '/' + arr[x]
            #print(data)
            
            # start extarcting data
            with pdfplumber.open(data) as pdf:
                page = pdf.pages[0]
                text = page.extract_text()

            # create namedtuple    
            Tx = namedtuple('Tx', 'contract stock_no price qty proceed brk_amt stamp clr_fee total_amt')
            Sx = namedtuple('Sx', 'dd mm yyyy stock_name brk_st')

            # create regular expression
            tx_line_re = re.compile(r'([A-z]{3}\d{1,}-\d{1,}) (\d\w{1,}) (\d{1,}\.\d{1,}) (\d{1,}) (\d{1,}.\d{1,}) (\d{1,}\.\d{1,}) (\d{1,}.\d{1,}) (\d{1,}.\d{1,}) (\-?\d{1,}.\d{1,})')
            stock_line_re = re.compile(r'(\d{2})\/(\d{2})\/(\d{4}) (\w.{1,}) (\d{1,}\.\d{1,})')
            
            # create line items list
            line_items = []

            # extarction for line items list
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

            # create stock items list
            stock_items = []

            # extracting for stock items list
            for line in text.split('\n'):
                line = stock_line_re.search(line)
                if line:
                    dd = line.group(1)
                    mm = line.group(2)
                    yyyy = line.group(3)
                    stock_name = line.group(4)
                    brk_st = line.group(5)
                    stock_items.append(Sx(dd, mm, yyyy, stock_name, brk_st))    

            # create namedtuple for combination of the list       
            cx = namedtuple ('cx', 'dd mm yyyy contract stock_no stock_name price qty proceed brk_amt stamp clr_fee brk_st total_amt')
            
            y = len(stock_items)
            
            # copy data into combine list using cx namedtuple
            for x in range(y):
                combine.append(cx(stock_items[x].dd, stock_items[x].mm, stock_items[x].yyyy, line_items[x].contract, line_items[x].stock_no, stock_items[x].stock_name, line_items[x].price, line_items[x].qty, line_items[x].proceed, line_items[x].brk_amt, line_items[x].stamp, line_items[x].clr_fee, stock_items[x].brk_st, line_items[x].total_amt))
            

        # copy data from combine list into panda dataframe
        df_final = pd.DataFrame(combine)

        # determine buy and sell contract
        df_final['Buy'] = df_final['contract'].str.contains('P')
        df_final['Buy'] = df_final.Buy.map({True : 'Buy' , False : 'Sell'})

        # convert date
        temp = df_final['date_temp'] = df_final['mm'] + '/' + df_final['dd'] + '/' + df_final['yyyy']
        df_final.insert(0,'date', temp) 
        df_final['date'] = pd.to_datetime(df_final['date'])
        df_final = df_final.drop('date_temp',1)

        # make global variable
        self.df_final = df_final
        self.combine = combine
        #print(df_final)

    def key_extract(self):
        df = self.df_final[['date', 'stock_name', 'price', 'qty', 'total_amt', 'Buy']]
        df_key = df.copy()
        df_key = df_key.sort_values(by=['date'])
        self.df_key = df_key 
    
    def save_csv(self):
        print("Total file extract: ", len(self.combine))

        ### run this to append existing csv file
        path_csv = '.'
        self.df_final.to_csv(path_csv + '/' + 'transaction.csv', mode = 'a', header = False, index = False) #append file existing

        path_csv = '.'
        self.df_key.to_csv(path_csv + '/' + 'key_transaction.csv', mode = 'a', header = False, index = False) #append file existing

        print("Succesfully data saved.")


    def run(self):
        self.extract_pdf()
        self.key_extract()
        self.save_csv()

    def plot_histogram(self, path, clmn, x_number=10):
        # init


        # Import data from CSV file
        # data = pd.read_csv(path)
        data = pd.read_excel(path)

        # Plot histogram
        plt.hist(data[clmn], bins=x_number)
        plt.xlabel('Percent change')
        plt.ylabel('Freq')
        plt.title(clmn + ' ' + path)
        plt.grid(True)
        plt.show()


if __name__ == "__main__":
    
    pdf = mextract()
    # data = mextract()

    # pdf.extract_pdf()
    # # print(pdf.df_final)
    # # print(pdf.combine)
    # pdf.save_csv()
    pdf.run()
    # path = '../stock_price/'
    # file = 'mahsing.xlsx'
    # change = 'Change'
    # high_low = 'High_low'
    # change_low = 'Change_low'
    # change_high = 'Change_high'
    # full_path = path + file
    # bins = 10

    # data.plot_histogram(full_path, change, bins)
    # data.plot_histogram(full_path, high_low, bins)
    # data.plot_histogram(full_path, change_low, bins)
    # data.plot_histogram(full_path, change_high, bins)
