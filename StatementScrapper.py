# moomooScrapper.py
"""
Created on Mon June 24 2024
version 1.0

@author: khairulakmal

"""

import requests
#import pdfplumber
import os, fnmatch
import re
import pandas as pd
from pypdf import PdfReader

class StatementScrapper:
    """ class to scrap required data from statement of Moomoo.
    """
    def __init__(self):
        self.path_origin = '../extract_pdf/' 
        self.destination_directory = '../Moomoo_pdf/'


    def list_file(self):
        """List of the files that to be scarp

        Returns:
            list : list of files
        """        
        # find a file to extract
        #path = '../extract_pdf/'
        self.list_file = fnmatch.filter(os.listdir(self.path_origin), '*.pdf')

        # sorted(arr)
        # print(len(arr))
        #print(arr)
        #print(len(arr))

        return self.list_file;

    def read_moomoo(self, pdf_path):
        """to read Moomoo statement in pdf and convert it text

        Args:
            pdf_path (string): directory path where the file locate

        Returns:
            string: Moomoo statement in text
        """        
        reader = PdfReader(self.path_origin + pdf_path)

        # Print the number of pages in the PDF
        #print(f"There are {len(reader.pages)} Pages")

        # Get the first page (index 0) 
        page = reader.pages[0]
        # Use extract_text() to get the text of the page
        #print(page.extract_text())
        text =''

        # Go through every page and get the text
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            text = text + page.extract_text()
            #print(text)
        
        return text
    
    def match_pattern(self, text, option=True):
        """to match pattern of required data from the text 

        Args:
            text (string): moomoo statement in text
            option (bool, optional): if true it match stock transaction else it match fee charge. Defaults to True.

        Returns:
            list : list of required information, true or false. 
        """
        if option:
            # Regex pattern to match the required fields
            pattern = re.compile(
                r'(Buy to Open|Sell to Close)\s+(\w+)\s+(\d{4})\s+[A-Z]+\s+[A-Z]+\s+(\d{4})\/(\d{2})\/(\d{2})\s+\d{2}:\d{2}:\d{2}\s+(\d+\.\d{4})\s+(\d+)'
            )
        else:
            # Regex pattern to match the required fields
            pattern = re.compile(
                #r'Net Transaction Amount:\s*(-?\d{1,3}(?:,\d{3})*\.\d{2})\s+-?\d{1,3}(?:,\d{3})*\.\d{2}\s+Commission:\s*(\d+\.\d{2})\s+\d+\.\d{2}\s+Platform Fees:\s*(\d+\.\d{2})\s+\d+\.\d{2}\s+Clearing Fee:\s*(\d+\.\d{2})\s+\d+\.\d{2}\s+Stamp Duty:\s*(\d+\.\d{2})\s+\d+\.\d{2}\s+'
                r'Net Transaction Amount:\s*(-?\d{1,3}(?:,\d{3})*\.\d{2})\s+-?\d{1,3}(?:,\d{3})*\.\d{2}\s+Commission:\s*(\d+\.\d{2})\s+\d+\.\d{2}\s+Platform Fees:\s*(\d+\.\d{2})\s+\d+\.\d{2}\s+Clearing Fee:\s*(\d+\.\d{2})\s+\d+\.\d{2}\s+Stamp Duty:\s*(\d+\.\d{2})\s+\d+\.\d{2}\s+Settlement Date:\s+\d{4}\/\d{2}\/\d{2}\s+\d{4}\/\d{2}\/\d{2}\s+Reference No:\s*([\w\/]+)'
            )

        # Search for the pattern in the text
        match = pattern.findall(text)

        # If a match is found, extract the groups
        if match:
            #extracted_data = match.groups()
            #print(extracted_data)
            return match
            
        else:
            return "No match found."
        
    def single_scarpper(self, text):
        """to scarp the text into useful data

        Args:
            text (string): moomoo statement in text

        Returns:
            pandas data frame: useful data that have been scarp in panda dataframe
        """        
        stock = self.match_pattern(text, option=True)
        fee = self.match_pattern(text, option=False)

        #convert to dataframe
        df_stock = pd.DataFrame(stock)
        df_stock.rename(columns ={0 : 'position', 1 : 'stock', 2 : 'code', 3 : 'year', 4 : 'month', 5 : 'day', 6 : 'price', 7 : 'unit'}, inplace = True)
        df_stock['date'] = df_stock['day'] + '/' + df_stock['month'] + '/' + df_stock['year']
        df_stock['unit'] = df_stock['unit'].astype(int)
        df_stock['price'] = df_stock['price'].astype(float)
        df_stock['subtotal'] = df_stock['price'] * df_stock['unit']

        #df_stock
        
        df_fee = pd.DataFrame(fee)
        df_fee.rename(columns ={0 : 'total', 1 : 'commision', 2 : 'brk_fee', 3 : 'clear_fee', 4 : 'stamp', 5 : 'ref'}, inplace = True)
        df_fee['total'] = df_fee['total'].str.replace(',', '').astype(float)
        df_fee['total'] = df_fee['total'].abs()
        
        result = pd.concat([df_stock, df_fee], axis=1)
        new_order = ['date', 'day', 'month', 'year', 'ref', 'code', 'stock', 'price', 'unit','subtotal', 'brk_fee', 'stamp', 'clear_fee', 'commision','total', 'position']
        result = result[new_order]
        
        return result
    
    def scrapper(self):
        """to convert moomoo statement into useful data. The data will save as key.csv and result.csv
        """        
        # find a file to extract
        #path = '../extract_pdf/'
        #arr = fnmatch.filter(os.listdir(path), '*.pdf')
        arr = self.list_file()

        for x in range(len(arr)):
            text = self.read_moomoo(arr[x])
            df=self.single_scarpper(text)
            df.to_csv(self.path_origin + 'result.csv', mode='a', index=False, header=False)
            df = df[['date','stock','price','unit','total','position']]
            df.to_csv(self.path_origin + 'key.csv', mode='a', index=False, header=False)
            self.move_file(arr[x])

        print("Total file extract: ", len(arr))
        print("Succesfully data saved.")

    def move_file(self, file):
        """move file to new destination

        Args:
            file (string): directory path and filename to move
        """
        # Define the source path and the destination path
        source_path = self.path_origin + file
        destination_path = self.destination_directory + file

        if os.path.isfile(destination_path):
            print("The file exists.")
        else:
            os.rename(source_path, destination_path)

 
        

if __name__ == "__main__":

    moomoo = StatementScrapper()
    # arr = moomoo.list_file()
    # moomoo.move_file(arr[0])
    # text = moomoo.read_moomoo(arr[0])
    # match_text = moomoo.match_pattern(text, False)
    #print(type(match_text))
    # scrapper = moomoo.single_scarpper(text)
    scrapper = moomoo.scrapper()
    # print(type(scrapper))