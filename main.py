# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#https://www.covalenthq.com/docs/networks/avalanche

import yaml
import os
import requests

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
                
                self.total+=i["quote"]
                
                decimal_balance=i["balance"]                
                balance=int(decimal_balance)/(10**decimal)
                
                print("{}: {} ({} {})".format(token,balance,quote,self.currency))
            
            print("\n")
        
        print("total: {} {}".format(self.total,self.currency))
        
if __name__=="__main__":
    ws=walletscanner()
    ws.readconfig()
    
    
    ws.scancomplete()

