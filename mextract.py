# mextract.py
"""
Created on Sat March 18 2023
Modified on Fri November 1 2024
version 1.2.0

The program is designed to extract statements from MPLUS into csv format for further analysis. 
Statements from the 2023 version are compatible, while older versions can still be accessed 
using `extract_pdf()`. The statements should be placed in an `extract_mplus_pdf` folder prior 
to extraction, and once successfully extracted, the files will be moved to the `mplus_pdf` folder.

@author: khairulakmal

"""

import pdfplumber
import os, fnmatch
import re
import pandas as pd
from collections import namedtuple
import matplotlib.pyplot as plt

class mextract:

    def __init__(self):
        """
            The program is designed to extract statements from MPLUS into csv format for further analysis. 
            Statements from the 2023 version are compatible, while older versions can still be accessed 
            using `extract_pdf()`. The statements should be placed in an `extract_mplus_pdf` folder prior 
            to extraction, and once successfully extracted, the files will be moved to the `mplus_pdf` folder.
            
        """   

        # Define folder path for the pre-extraction and post-extraction stages.     
        self.path_origin = '../extract_mplus_pdf/' 
        self.destination_directory = '../Mplus_pdf/'


    def extract_pdf(self):
        """
            This function is to extract older format of Mplus statement
        """        
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

    def new_extract_pdf(self):
        """
        The function converts each PDF file into text to enable extraction of important data. 
        To locate this data within the text, regular expressions are applied, followed by creating 
        a DataFrame for the extracted data. The function returns a Pandas DataFrame containing the 
        data from the extraction.

        Returns:
            Pandas Dataframe: Data from the extraction. 
        """        

        # arr akan dapatkan nama file di dalam path self.path_origin
        path = self.path_origin
        # senarai file akan di simpan dalam arr
        arr = fnmatch.filter(os.listdir(path), '*.pdf')

        # proses extraction bermula disini
        combine = []
        for x in range(len(arr)):

            data = path + arr[x]
            #data = arr[x]
            #print(data)
            
            with pdfplumber.open(data) as pdf:
                page = pdf.pages[0]
                text = page.extract_text()
            
            #print (text)
            Tx = namedtuple('Tx', 'contract stock_no price qty proceed brk_amt stamp clr_fee total_amt')
            Sx = namedtuple('Sx', 'dd mm yyyy stock_name')
            tx_line_re = re.compile(r'([A-z]{3}\d{1,}-\d{1,}) (\d\w{1,}) (\d{1,}\.\d{1,}) (\d{1,}) (\d{1,}.\d{1,}) (\d{1,}\.\d{1,}) (\d{1,}.\d{1,}) (\d{1,}.\d{1,}) (\-?\d{1,}.\d{1,}) (\d{1,}.\d{1,})')
            stock_line_re = re.compile(r'^(\d{2})\/(\d{2})\/(\d{4}) (\w.{1,})')
            
            line_items = []

            for line in text.split('\n'):
                # print(line)
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
                    total_amt = line.group(10)
                    line_items.append(Tx(contract, stock_no, price, qty, proceed, brk_amt, stamp, clr_fee, total_amt)) 

            stock_items = []
            for line in text.split('\n'):
                line = stock_line_re.search(line)
                if line:
                    dd = line.group(1)
                    mm = line.group(2)
                    yyyy = line.group(3)
                    stock_name = line.group(4)
                    stock_items.append(Sx(dd, mm, yyyy, stock_name))    
                    
            cx = namedtuple ('cx', 'dd mm yyyy contract stock_no stock_name price qty proceed brk_amt stamp clr_fee total_amt')
            
            y = len(stock_items)
            
            for x in range(y):
                combine.append(cx(stock_items[x].dd, stock_items[x].mm, stock_items[x].yyyy, line_items[x].contract, line_items[x].stock_no, stock_items[x].stock_name, line_items[x].price, line_items[x].qty, line_items[x].proceed, line_items[x].brk_amt, line_items[x].stamp, line_items[x].clr_fee, line_items[x].total_amt))
            

        df_final = pd.DataFrame(combine)


        df_final['Buy'] = df_final['contract'].str.contains('P')
        df_final['Buy'] = df_final.Buy.map({True : 'Buy' , False : 'Sell'})


        temp = df_final['date_temp'] = df_final['mm'] + '/' + df_final['dd'] + '/' + df_final['yyyy']
        #print(df_final)
        df_final.insert(0,'date', temp) 
        #print(df_final)
        df_final['date'] = pd.to_datetime(df_final['date'])
        #print(df_final)
        df_final = df_final.drop('date_temp',1)
        # print(df_final)

        # data yang disimpan dalam pandas dataframe selepas extraction
        self.df_final = df_final
        self.combine = combine
        return df_final


    def key_extract(self):
        """
        The function is designed to locate only key data from the DataFrame generated by the 
        `new_extract_pdf` function. 

        Returns:
            Pandas Dataframe: Locate only key data. 
        """        
        df = self.df_final[['date', 'stock_name', 'price', 'qty', 'total_amt', 'Buy']]
        df_key = df.copy()
        df_key = df_key.sort_values(by=['date'])
        self.df_key = df_key 
        return df_key
    
    def save_csv(self):
        """
        The function saves data from the `new_extract_pdf` and `key_extract` functions in CSV format, 
        generating two files: `transaction.csv` and `key_transaction.csv`.
        """        
        print("Total file extract: ", len(self.combine))

        ### run this to append existing csv file
        path_csv = self.path_origin
        self.df_final.to_csv(path_csv  + 'transaction.csv', mode = 'a', header = False, index = False) #append file existing

        #path_csv = '.'
        self.df_key.to_csv(path_csv  + 'key_transaction.csv', mode = 'a', header = False, index = False) #append file existing

        print("Succesfully data saved.")

    def move_file(self):
        """
        Once the statement has been extracted, the file is moved to the post-extraction folder.
        """        

        # list of the file
        arr = fnmatch.filter(os.listdir(self.path_origin), '*.pdf')

        # Each file is moved to the post-extraction folder.
        for x in range(len(arr)):
            
            # Define the source path and the destination path
            source_path = self.path_origin + arr[x]
            destination_path = self.destination_directory + arr[x]

            if os.path.isfile(destination_path):
                print("The file exists.")
            else:
                os.rename(source_path, destination_path)


    def run(self):
        """
            The function runs an extraction process for Mplus statements by sequentially activating 
            the extraction function, extracting only key data, saving the data in CSV format, and 
            moving the file from the pre-extraction folder to the post-extraction folder.  
        """        
        # self.extract_pdf()
        self.new_extract_pdf()
        self.key_extract()
        self.save_csv()
        self.move_file()

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
