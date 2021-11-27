#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 15:50:47 2021

@author: kkr
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table


cols=["name","addresse","network","chainid"]

layout = html.Div([
    html.H2("Input wallets in the table below:"),
    html.Div("Fill out the table and download the json file. This is only a help to write the wallet data into a structured format that then can be used to look up the adresses"),
    html.Br(),
    html.Br(),
    html.H3("Conversion table"),
    html.Div(id="cont_tbl_add"),
    html.Div(html.Button('Add Row', id='editing-rows-button', n_clicks=0)),
    html.Div(html.Button('Convert wallet overview', id='download-button', n_clicks=0)),
    html.Div(id="download-table"), 
    html.Br(),
    html.Br(),
    html.H2("Available chains:"),
    html.Div(id="cont_tbl_chains")
])