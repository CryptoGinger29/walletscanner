# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#https://www.covalenthq.com/docs/networks/avalanche

import yaml
import os
import requests
import pandas as pd 

class walletscanner:
    def __init__(self):
        self.init=True
        self.__location__ = os.path.realpath(
                                os.path.join(os.getcwd(), os.path.dirname(__file__)))
        
        self.configpath=os.path.join(self.__location__,'config','config.yaml')
        self.baseurl="https://api.covalenthq.com/"
        self.key="&key={}"
        self.currency="USD"
        self.format="JSON"
        self.balanceendpoint="v1/{}/address/{}/balances_v2/?quote-currency={}&format={}&nft=true&no-nft-fetch=false"
        
    
    def setconfig(self,file):
        self.config= yaml.load(file, Loader=yaml.FullLoader)
        
        return self.config
        
    def readconfig(self,path=None):
        if path is None:
            with open(self.configpath) as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)
        else:
            self.configpath=path
            with open(path) as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)            
        

        return self.config
        
        
    def scancomplete(self):
        
        walletoverview=[]
        
        self.total=0
        for i in self.config["wallets"]["wallets"]:
            
            attr=i["attributes"]
            print("Processing wallet called: {}".format(i["name"]))
            print("Scanning {} on network {} with chain id {}".format(attr["addr"],attr["network"],attr["chainid"]))
                        
            requrl=self.balanceendpoint.format(attr["chainid"],attr["addr"],self.currency,self.format) 
            apikey=self.key.format(self.config["key"])
            
            r=requests.get(self.baseurl + requrl + apikey)
            
            
            print("\n")
            print("Status")
            for i in r.json()["data"]["items"]:
                decimal=i["contract_decimals"]
                token=i["contract_ticker_symbol"]
                quote=i["quote"]
                quote24h=i["quote_24h"]
                self.total+=i["quote"]
                
                try:
                    decimal_balance=i["balance"]                
                    balance=int(decimal_balance)/(10**decimal)
                except:
                    balance=None
                
                try:
                    decimal_balane24h=i["balance_24h"]
                    balance24h=int(decimal_balane24h)/(10**decimal)
                except:
                    balance24h=None
                
                try:
                    delta_balance=(balance-balance24h)/balance
                except:
                    delta_balance=None
                    
                try:
                    delta_quote=(quote-quote24h)/quote
                except:
                    delta_quote=None
                                        
                    
                walletoverview.append([attr["addr"],attr["network"],token,balance24h,balance,delta_balance,quote24h,quote,delta_quote])
                
                print("{}: {} ({} {})".format(token,balance,quote,self.currency))
            
            print("\n")
        
        print("total: {} {}".format(self.total,self.currency))
        
        return pd.DataFrame(walletoverview,columns=["wallet","network","token","balance 24h","balance","delta balance","quote 24h","quote","delta quote"])
        
if __name__=="__main__":
    ws=walletscanner()
    ws.readconfig()
    
    
    ws.scancomplete()

