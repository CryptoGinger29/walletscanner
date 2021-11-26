### Import Packages ###
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

from dash.dependencies import Input, Output, State
### Import Dash Instance ###
from app import app
### Page 1 Layout and Callback ###
import io
import datetime
from src.main import walletscanner
import base64

ws=walletscanner()
#%%
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(dbc.NavbarBrand("WalletScanner", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        ]
    ),
    color="dark",
    dark=True,
)


#%%
layout = html.Div([
    navbar,
    html.H1("Upload a yaml file:"),
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-image-upload'),
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'yaml' in filename:
            ws.setconfig(decoded.decode('utf-8'))
            # Assume that the user uploaded a CSV file
            overview=ws.scancomplete()
            
            overview=overview[overview["balance"]>0].copy()

            
            tbl_all=dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i} for i in overview.columns],
                        data=overview.to_dict('records'),
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                    )
            
            df_grouped=overview.groupby(["network","token"]).sum().reset_index()
                        
            tbl_acc=dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i} for i in df_grouped.columns],
                        data=df_grouped.to_dict('records'),
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                    )
            
            header=html.H1("All held tokens:")
            header2=html.H1("Balance of held tokens:")

            return  html.Div(children=[header,tbl_all,header2,tbl_acc])
                                
            
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@app.callback(Output('output-image-upload', 'children'),
              Input('upload-image', 'contents'),
              State('upload-image', 'filename'),
              State('upload-image', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children 
