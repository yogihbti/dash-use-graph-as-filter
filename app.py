import dash
import json
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from textwrap import dedent as d

data=pd.read_csv("Data.csv")
data['Month']=pd.to_datetime(data['Month'],format='%b-%y')
data_pivot=data.pivot_table(values='Forecast',index='Month',aggfunc=np.sum)
data_pivot_family=data.pivot_table(values='Forecast',index='Product Family',aggfunc=np.sum)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

styles = {
        'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def update_dia_filter_selection(family,dia_filter_family):
    if family in dia_filter_family:
        dia_filter_family.remove(family)
    else: 
        dia_filter_family.append(family)
    return dia_filter_family


def get_color_toggle(idx,color_list):
    color_list=list(color_list)
    if color_list[idx]=='teal':
        color_list[idx]='red'
    else: 
        color_list[idx]='teal'
    return color_list

app.layout = html.Div(children=[
    html.H1(children='Use As filter'),
    dcc.Store(id='session'),
    html.Div(id='family',style={'display': 'none'}),
    html.Div(children='''
        Tableau like use as Filter feature in Dash-Plotly.
    '''),

    dcc.Graph(
    style={'height': 200},
    id='my-graph'),

    dcc.Graph(
    style={'height': 300},
    id='my-graph2')
])

@app.callback(Output('family', 'children'), 
    [Input('my-graph2', 'clickData')],
    [State('family', 'children')])
def update_family_data(clickData,family):
    list_family=[]
    if clickData is not None:
        fam=clickData['points'][0]['x'] 
        if family is not None:
            list_family=json.loads(family)
        list_family=update_dia_filter_selection(fam,list_family)
    return json.dumps(list_family) 


@app.callback(Output('session', 'data'), 
    [Input('my-graph2', 'clickData')],
    [State('session', 'data')])
def color_data(clickData,col_data):
    if clickData is None:
        col_data=['teal'] * len(data_pivot.index)
    else:
        idx=clickData['points'][0]['pointIndex']
        col_data=get_color_toggle(idx,col_data)
    return col_data



@app.callback(
    Output('my-graph', 'figure'),[Input('family', 'children')])
def upadate_graph_one(selected_family):
    sel_fam=json.loads(selected_family)
    if len(sel_fam) == 0:
        data_pivot_filter=data_pivot
    else:
        data_pivot_filter=data[data['Product Family'].isin(sel_fam)].pivot_table(values='Forecast',index='Month',aggfunc=np.sum)
    figure=go.Figure(
        data=[go.Bar(
                x=data_pivot_filter.index.strftime("%b-%y"),
                y=data_pivot_filter['Forecast'],
                name='Forecast',
                marker=go.bar.Marker(
                    color='rgb(55, 83, 109)',
                    opacity=1
                )
                
            )],
        layout=go.Layout(
            title='Monthly Forecast',
            showlegend=True,
            legend=go.layout.Legend(
                x=0,
                y=1.0
            ),
            margin=go.layout.Margin(l=40, r=0, t=40, b=30)
        )
    )

    return figure

@app.callback(
    Output('my-graph2', 'figure'),[Input('session', 'modified_timestamp')],
    [State('session','data')])
def upadate_graph_color(clickData,col_data):
    figure=go.Figure(
        data=[go.Bar(
                x=data_pivot_family.index,
                y=data_pivot_family['Forecast'],
                name='Forecast',
                marker=go.bar.Marker(
                    color=col_data,
                    opacity=1
                )
            )],
        layout=go.Layout(
            title='Family wise total Forecast',
            showlegend=True,
            legend=go.layout.Legend(
                x=0,
                y=1.0
            ),
            margin=go.layout.Margin(l=40, r=0, t=40, b=30)
        )
    )
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)