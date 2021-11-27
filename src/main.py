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
import json

class walletscanner:
    def __init__(self):
        
        
        self.init=True
        self.__location__ = os.path.realpath(
                                os.path.join(os.getcwd(), os.path.dirname(__file__)))
        
        self.configpath=os.path.join('config','config.yaml')

        self.readconfig()

        self.baseurl="https://api.covalenthq.com/"
        self.key="&key={}".format(self.config["key"])
        self.currency="USD"
        self.format="JSON"
        self.balanceendpoint="v1/{}/address/{}/balances_v2/?quote-currency={}&format={}&nft=true&no-nft-fetch=false"
        self.chainsendpoint="v1/chains/?quote-currency=USD&format=JSON"
        self.wallets=None
    
    def setwallets(self,file):
        self.wallets= json.loads(file)
        
        return self.wallets
        
    def readconfig(self,path=None):
        if path is None:
            with open(self.configpath) as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)
        else:
            self.configpath=path
            with open(path) as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)            
        

        return self.config
        
    def getchains(self):
        r=requests.get(self.baseurl + self.chainsendpoint + self.key)
        
        return r.json()["data"]["items"]
        
    
    def scancomplete(self):
        
        walletoverview=[]
        
        self.total=0
        for i in self.wallets["wallets"]:
            
            attr=i
            print("Processing wallet called: {}".format(i["name"]))
            print("Scanning {} with chain id {}".format(attr["addresse"],attr["chainid"]))
                        
            requrl=self.balanceendpoint.format(attr["chainid"],attr["addresse"],self.currency,self.format) 
            
            r=requests.get(self.baseurl + requrl + self.key)
            
            
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
                                        
                    
                walletoverview.append([attr["addresse"],token,balance24h,balance,delta_balance,quote24h,quote,delta_quote])
                
                print("{}: {} ({} {})".format(token,balance,quote,self.currency))
            
            print("\n")
        
        print("total: {} {}".format(self.total,self.currency))
        
        return pd.DataFrame(walletoverview,columns=["wallet","token","balance 24h","balance","delta balance","quote 24h","quote","delta quote"])
        
if __name__=="__main__":
    ws=walletscanner()
    

    wallet=False
    if wallet==True:
        f = open('../input/personalsettings.json')
        ws.setwallets(f)
    
        ws.scancomplete()
    else:
        ws.getchains()
