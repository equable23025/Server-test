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


app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

if __name__ == '__main__':
  
  app.run_server(debug=True)

