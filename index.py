import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
from pages import menu,home
from dash_table import DataTable, FormatTemplate

from src.main import walletscanner
import base64

ws=walletscanner()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

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
app.layout = html.Div([dcc.Location(id="url"), menu.sidebar, content])



#%% REDIRECT
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return home.layout
    elif pathname == "/howto":
        return html.P("This is the content of page 1. Yay!")
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
    for i in columns:
        if i in percentagecols:
            cols.append({"id":i,"name":i,"type":'numeric', "format":percentage})
        elif i in moneycols:
            cols.append({"id":i,"name":i,"type":'numeric', "format":money})
        else:
            cols.append({"id":i,"name":i,"type":"text"})

    return cols

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'yaml' in filename:
            ws.setconfig(decoded.decode('utf-8'))
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
            
            df_grouped=overview.groupby(["network","token"]).sum().reset_index()
            
            
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
            'There was an error processing this file.'
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