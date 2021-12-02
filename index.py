import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
from pages import menu,home,howto
from dash_table import DataTable, FormatTemplate
from flask import Flask


from src.main import walletscanner
import base64
import json 

ws=walletscanner()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],server=Flask(__name__))

server=app.server

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

TABLE_STYLE={'minWidth': '100%'}

TABLE_CELL_STYLE={
        # all three widths are needed
        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
    }

TABLE_CONDITIONALFORMAT=[
        {
            'if': {
                'filter_query': '{delta balance} < 0',
                'column_id': 'delta balance',
            },
            'color': 'tomato',
        },
        {
            'if': {
                'filter_query': '{delta quote} < 0',
                'column_id': 'delta quote',
            },
            'color': 'tomato',
        },        
        {
            'if': {
                'filter_query': '{delta balance} > 0',
                'column_id': 'delta balance',
            },
            'color': '#3D9970',
        },
        {
            'if': {
                'filter_query': '{delta quote} > 0',
                'column_id': 'delta quote',
            },
            'color': '#3D9970',
        },          
        ]


money = FormatTemplate.money(2)
percentage = FormatTemplate.percentage(2)

content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div([
    dcc.Location(id="url"), 
    menu.sidebar, 
    content,
    dcc.Store(id="walletoverview_upload",storage_type="session"),
    dcc.Store(id="walletoverview_tbl",storage_type="session"),
    dcc.Store(id="walletoverview_global",storage_type="session")
])



#%% REDIRECT
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return home.layout
    elif pathname == "/howto":
        return howto.layout
    elif pathname == "/about":
        return html.P("This is the content of page 1. Yay!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

#%%

def colsetup(columns):
    cols=[]
    percentagecols=["delta balance","delta quote"]
    moneycols=["quote","quote 24h"]
    dropdowncols=["chainid"]
    for i in columns:
        if i in percentagecols:
            cols.append({"id":i,"name":i,"type":'numeric', "format":percentage})
        elif i in moneycols:
            cols.append({"id":i,"name":i,"type":'numeric', "format":money})
        elif i in dropdowncols:
            cols.append({"id":i,"name":i,"type":'text','presentation':'dropdown'})
        else:
            cols.append({"id":i,"name":i,"type":"text"})
            
    return cols

def parse_contents(contents):
    try:
        ws.setwallets(contents)
        # Assume that the user uploaded a CSV file
        overview=ws.scancomplete()
        
        overview=overview[overview["balance"]>0].copy()

        
        cols=colsetup(overview.columns)
        tbl_all=DataTable(
                    id='table',
                    columns=cols,
                    data=overview.to_dict('records'),
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    fixed_columns={ 'headers': True, 'data': 1 },
                    style_table=TABLE_STYLE,
                    style_cell=TABLE_CELL_STYLE,
                    style_data_conditional=TABLE_CONDITIONALFORMAT
                )
        
        df_grouped=overview.groupby(["token"]).sum().reset_index()
        
        
        cols=colsetup(df_grouped.columns)
        tbl_acc=DataTable(
                    id='table',
                    columns=cols,
                    data=df_grouped.to_dict('records'),
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    fixed_columns={ 'headers': True, 'data': 1 },
                    style_table=TABLE_STYLE,
                    style_cell=TABLE_CELL_STYLE,
                    style_data_conditional=TABLE_CONDITIONALFORMAT
                )
        
        header=html.H1("All held tokens:")
        header2=html.H1("Balance of held tokens:")
        
        return  html.Div(children=[header,tbl_all,header2,tbl_acc])
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file'
        ])

@app.callback(Output('output-image-upload', 'children'),
              Input('walletoverview_global', 'data'),
              Input("updater","n_intervals"))
def update_output(data,intervals):
    if data is not None:
        return parse_contents(data[0]) 
    return html.Div()


@app.callback(Output('walletoverview_upload','data'),
              Input('upload-image', 'contents'),
              prevent_initial_call=True,
              )
    
def uploadconfig(list_of_contents):
    if list_of_contents is None:
        return None
    if len(list_of_contents)==0:
        return None
    elif len(list_of_contents)==1:
        content_type, content_string = list_of_contents[0].split(',')
        return [json.loads(base64.b64decode(content_string))]
    else:
        return None  
    

@app.callback(Output('walletoverview_global','data'),
              Input('walletoverview_upload', 'data'),
              Input('walletoverview_tbl', 'data'),
              Input('walletoverview_global', 'data'),
              )
    
def globalconfig(upload_data,tbl_data,curr_config):
    ctx = dash.callback_context

    if not ctx.triggered:
        triggerid = 'No clicks yet'
    else:
        triggerid = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggerid=="walletoverview_upload":
        if upload_data is not None:
            return upload_data
        else:
            return curr_config
    elif triggerid=="walletoverview_tbl":
        if tbl_data is not None:
            return tbl_data
        else:
            return curr_config
    else:
        return None

@app.callback(Output('walletoverview_tbl','data'),
              Output("download-table", "children"),
              Input("download-button", "n_clicks"),
              State('table-editing-wallets', 'data'),
              prevent_initial_call=True,
              )
    
def tblconfig(n_clicks,tbl_data):
    
    content={"wallets":tbl_data}
    data_string = json.dumps(content)

    downloadlink=html.A(
        "Download Data",
        id="download-link",
        download="download.json",
        href=f"data:text/json;charset=utf-8,{data_string}",
        target="_blank",
        )  

    
    return [content],downloadlink
    
    
@app.callback(
    Output('table-editing-wallets', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('table-editing-wallets', 'data'),
    State('table-editing-wallets', 'columns'),
    prevent_initial_call=True,)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

@app.callback(
    Output("cont_tbl_chains", "children"),
    Input("cont_tbl_chains", "children"),
    prevent_initial_call=False,
)
def chainreader(trigger):
    
    json_chains=ws.getchains()
    
    cols=colsetup(json_chains[0].keys())

    
    return DataTable(
                id='table',
                columns=cols,
                data=json_chains,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                fixed_columns={ 'headers': True, 'data': 1 },
                style_table=TABLE_STYLE,
                style_cell=TABLE_CELL_STYLE,
                style_data_conditional=TABLE_CONDITIONALFORMAT
            )

@app.callback(
    Output("cont_tbl_add", "children"),
    Input("cont_tbl_add", "children"),
    State('walletoverview_global', 'data'),
    prevent_initial_call=False,
)
def setupaddtable(trigger,data):
    cols=colsetup(["name","addresse","chainid"])
    
    r=ws.getchains()

    dropdowns={"chainid":{
                'options': [
                    {'label': i["label"], 'value': i["chain_id"]}
                    for i in r
                ]
            },
        }
    if data is None:
        return DataTable(
                id='table-editing-wallets',
                columns=cols,
                data=[],
                dropdown=dropdowns,
                css = [{
                    "selector": ".Select-menu-outer",
                    "rule": 'display : block!important'
                }],
                editable=True,
                row_deletable=True
            )
    else:
        return DataTable(
                id='table-editing-wallets',
                columns=cols,
                data=data[0]["wallets"],
                dropdown=dropdowns,
                css = [{
                    "selector": ".Select-menu-outer",
                    "rule": 'display : block!important'
                }],
                editable=True,
                row_deletable=True
            )       
