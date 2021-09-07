#!pip install --quiet jupyter-dash pyngrok

#import dash 
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from pyngrok import ngrok
import pandas as pd
import dash
from dash.dependencies import Input, Output


DATA_URL = 'http://peaoc.pea.co.th/loadprofile/files/%s/%s'
REGIONS = {'All areas':'13', 'Northern area':'14', 'Northeastern area':'15', 'Central area':'16', 'Southern area':'17'}
CUSTOMERS = {'Small house':'10', 'Large house':'11', 'Small business':'20', 'Medium business':'30', 'Large business':'40'}
MONTHS = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
YEARS = {'2555':'12', '2556':'13', '2557':'14', '2558':'15', '2559':'16', '2560':'17', '2561':'18', '2562':'19', '2563':'20', '2564':'21'}


# นำเข้าข้อมูลในรูปแบบ DataFrame
def import_data(region, customer, month, year):
  fname = "dt%s%s%s%s.xls"%(REGIONS[region], YEARS[year], MONTHS[month], CUSTOMERS[customer])
  url = DATA_URL%(REGIONS[region], fname)
  try:
    col_names = ['TIME', 'PEAKDAY', 'WORKDAY', 'SATURDAY', 'SUNDAY']
    df = pd.read_excel(url, sheet_name='Source', skiprows=4, usecols='A:E', names=col_names, nrows=97)
  except:
    col_names = ['TIME', 'PEAKDAY', 'SUNDAY', 'SATURDAY', 'WORKDAY']
    df = pd.read_excel(url, sheet_name='Sheet1', skiprows=2, usecols='A:E', names=col_names, nrows=97)
  return df 

# จัดรูปแบบข้อมูลเป็นรายชั่วโมง
def align_trim_data(orig_df):
  df = orig_df.copy()
  df.iloc[0:96, 1:] = df.iloc[1:97, 1:].values
  df.drop(96, inplace=True)
  new_idx = pd.TimedeltaIndex(data=range(0,15*96,15), unit='m')
  df.set_index(new_idx, inplace=True)
  hr_df = df.resample('1H').mean()
  hr_df['TIME'] = pd.date_range(start="00:00", end="23:00", freq='h')
  return hr_df

# prepare Dash runtime
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# สร้างข้อมูล
df = import_data('All areas', 'Large house', 'Jan', '2564')
hr_df = align_trim_data(df)

# create graph component
fig = px.line(hr_df, x=hr_df.index, y='WORKDAY')

# create table
def generate_table(df, rows):
  head = html.Thead(html.Tr([html.Th(col) for col in df.columns]))
  body = html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), rows))
        ])
  table = html.Table([head, body])
  return table

app.layout = html.Div(children=[
  html.H1(children='Hello Dash'),

dcc.Dropdown(
    id='month',
    options=[
        {'label': 'ม.ค.', 'value': 'Jan'},
        {'label': 'ก.พ.', 'value': 'Feb'},
        {'label': 'มี.ค.', 'value': 'Mar'},
        {'label': 'เม.ษ.', 'value': 'Apr'},
        {'label': 'พ.ค.', 'value': 'May'},

    ],
    value='Jan',

    searchable=False
  ),
  dcc.Dropdown(
    id='daytype',
    options=[
        {'label': 'WORKDAY', 'value': 'WORKDAY'},
        {'label': 'SATURDAY', 'value': 'SATURDAY'},
        {'label': 'SUNDAY', 'value': 'SUNDAY'}
    ],
        value='WORKDAY',

    searchable=False
  ),

  html.Div(
      children='Demo line plot.',
      style={'textAlign': 'center', 'color': '#23A223'}
  ),
  dcc.Graph(
      id='graph',
      figure=fig
  ),
  html.Div(
      children='Demo table.',
      style={'textAlign': 'left', 'color': '#2323A2'}
  ),
  html.Div(id='my-output'),
  generate_table(hr_df, 5)
])

@app.callback(
    Output('graph','figure'),

    Input(component_id='month', component_property='value'),
    Input(component_id='daytype', component_property='value')

)
def update_figure(month, daytype):
    # ctx = dash.callback_context
    # print(ctx)
    print('hello')
    df = import_data('All areas', 'Large house', month, '2564')
    hr_df = align_trim_data(df)

    # create graph component
    fig = px.line(hr_df, x=hr_df.index, y=daytype)

    return fig
  
print("Start Server")
http_tunnel = ngrok.connect(8400)
print(http_tunnel)
app.run_server(port=8400, mode='external', debug=True)
