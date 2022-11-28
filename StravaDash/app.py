from strava_api import get_data,preprocess
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc
from dateutil.relativedelta import relativedelta
from datetime import date
from dash_bootstrap_templates import load_figure_template

df =get_data()
df = preprocess(df)

def get_last_n_months(data,n,baseline=False):
    if baseline:
        end_date = data.start_date.max() - relativedelta(months=n) # shift it back by n months
    else:
        end_date = data.start_date.max()
    start_date = end_date - relativedelta(months=n)
    return data.loc[start_date.strftime("%Y-%m-%d"):end_date.strftime("%Y-%m-%d")]

# ------------------------------------------------------------------------------
app = Dash(__name__,external_stylesheets=[dbc.themes.DARKLY],
           meta_tags=[{'name': 'viewport',
                       'content': 'width=device-width, initial-scale=1.0'}]
           )
load_figure_template(["slate", "lumen"])
server = app.server

# App layout
app.layout = dbc.Container([

    dbc.Row(
       dbc.Col(
           html.H1("Sports Analytics", style={'text-align': 'center'}),
       )
    ),

    dbc.Row(
           dbc.Col(
                   html.Div(style={'height': '5px','background-color': 'darkorange'}),
           )
        ),

    dbc.Row(
        dbc.Col([
            html.Div(id='output_container', children=[]),
        ]
        ),
    ),

    dbc.Row([
        dbc.Col([
            dcc.RadioItems(['Run','Ride'],'Run',id='slct_activity'),
            ],
            xs=6, sm=6, md=6, lg=1, xl=1
        ),

        dbc.Col(
            dcc.Dropdown(
                id="slct_period",
                options=[3, 6, 12],
                multi=False,
                value=3,
                style={'width': '70%', 'color': 'black'},
            ),
            xs=6, sm=6, md=6, lg=2, xl=2
        ),
    ]),

    dbc.Row([
        dbc.Col(
            dcc.Graph(id="ind1", style={'display': 'inline-block'},figure={}),
            xs=6, sm=6, md=4, lg=2, xl=2
        ),
        dbc.Col(
            dcc.Graph(id="ind2", style={'display': 'inline-block'}, figure={}),
            xs=6, sm=6, md=4, lg=2, xl=2
        ),
        dbc.Col(
            dcc.Graph(id="ind3", style={'display': 'inline-block'}, figure={}),
            xs=6, sm=6, md=4, lg=2, xl=2
        ),
        dbc.Col(
            dcc.Graph(id='bar1', config={'displayModeBar': False},figure={},className='p-1'),
        xs=12, sm=12, md=6, lg=2, xl=2),

        dbc.Col(
            dcc.Graph(id='hist1', config={'displayModeBar': False},figure={}, className='p-1'),
        xs=12, sm=12, md=6, lg=2, xl=2),

    ], align= 'center'),

    html.Div(style={'height': '10px'}),

    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id="slct_cat",
                options=[{'label': str(y), 'value': y} for y in df['dist_cat'].unique()],
                multi=False,
                value='medium',
                style={'width':'70%','color': 'black'},
            ),
        xs=6, sm=6, md=6, lg=2, xl=2),
    ]),

    html.Div(style={'height': '10px'}),

    dbc.Row([
        dbc.Col(
            dcc.Graph(id="ind4", style={'display': 'inline-block'},figure={}),
            xs=6, sm=6, md=4, lg=2, xl=2),

        dbc.Col(
            dcc.Graph(id="line1", config={'displayModeBar': False}, figure={}),
            xs=12, sm=12, md=8, lg=6, xl=6),

        dbc.Col(
            dbc.Card(
                [
                    dbc.CardImg(
                        src="https://media.giphy.com/media/l3vQX4tXkLa1PTZ2U/giphy.gif")
                ],
                style={"width": "15rem", "height": "15rem"},
            ),
            xs=6, sm=6, md=6, lg=2, xl=2)
    ],align='top'),

    html.Br(),
    html.Div("* green or red indicators mean that the performance is better or worse than the months before. ",style={'color':'grey'}),
    html.Br(),
    html.Div("This dashboard is made with python, dash & plotly. code: https://github.com/wemat", style={'color':'lightgrey'}),
    html.Div("Talk about python,BI,data science or go for a run with me:  wemat.web@gmail.com", style={'color':'lightgrey'}),

],fluid=True)
# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components

@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='ind1', component_property='figure'),
     Output(component_id='ind2', component_property='figure'),
     Output(component_id='ind3', component_property='figure'),
     Output(component_id='bar1', component_property='figure'),
     Output(component_id='hist1', component_property='figure'),
    ],
    [Input(component_id='slct_activity', component_property='value'),
     Input(component_id='slct_period', component_property='value')]
)
def update_upper_graphs(slct_act,slct_period):
    data = df.loc[df["type"] == slct_act].copy()

    last_act = data['start_date'].max().strftime("%Y-%m-%d")
    if last_act == date.today().strftime("%Y-%m-%d"):
        time_of_day = data[last_act]['name'][0].split()[-1]
        elapsed_time = data[last_act]['elapsed_time'][0]
        container = "matt went for a {} min {} today!".format(elapsed_time//60,slct_act.lower())
    else:
        container = "matt wasn't out today (yet). last {} was at {}".format(slct_act.lower(),last_act)

    ind1 = go.Figure().add_trace(go.Indicator(
            mode = "number+delta",
            value = data[data['start_date'].max().strftime("%Y-%m-%d")]['average_speed'].sum(),
            number={'suffix': " km/h", 'valueformat':'.1f'},
            ))

    ind1.update_layout(
        height=180,  # Added parameter
        width=180,  # Added parameter
        margin = dict(l=15, r=15, t=0, b=0),
        template={'data': {'indicator': [{
            'title': {'text': f"average speed <br><span style='font-size:0.8em;color:gray'>last {slct_act.lower()}</span>",
                      'font':{'size':15}},
            'mode': "number+delta+gauge",
            'delta': {'reference': get_last_n_months(data, 3)['average_speed'].mean()}}],
        }})

    ind2 = go.Figure().add_trace(go.Indicator(
            mode = "number+delta",
            value = data[data['start_date'].max().strftime("%Y-%m-%d")]['kilometres'].sum(),
            number={'valueformat': '.1f'},
            ))

    ind2.update_layout(
        height=180,  # Added parameter
        width=180,  # Added parameter
        margin = dict(l=50, r=50, t=50, b=50),
        template={'data': {'indicator': [{
            'title': {'text': f"km of last {slct_act}",
                      'font':{'size':15}},
            'mode': "number+delta+gauge",
            'delta': {'reference': get_last_n_months(data, 3)['kilometres'].mean()}}],

        }})

    ind3 = go.Figure().add_trace(go.Indicator(
            mode = "number+delta",
            value = get_last_n_months(data, slct_period)['kilometres'].sum(),
            ))

    ind3.update_layout(
        height=180,  # Added parameter
        width=180,  # Added parameter
        margin = dict(l=50, r=50, t=50, b=50),
        template={'data': {'indicator': [{
            'title': {'text': f"total km last {slct_period} months",
                      'font':{'size':15}},
            'mode': "number+delta+gauge",
            'delta': {'reference': get_last_n_months(data, slct_period, baseline=True)['kilometres'].sum()}}],
        }})


    grouped_cats = get_last_n_months(data, slct_period)[['dist_cat', 'id','kilometres']].groupby(['dist_cat']).agg({'id':'count','kilometres':'sum'}).reset_index()
    grouped_cats.columns = ['Category', 'Count','kilometres']

    bar1 = go.Figure(data=[
        go.Bar(x=grouped_cats['Category'], y=grouped_cats['Count'],text=grouped_cats['Count'],marker={'color':'lightblue'}),
    ])

    bar1.update_layout(
        title=f'total {slct_act.lower()}s of last {slct_period} months',
        height=250,
        margin=dict(l=30, r=30, t=40, b=0),
    ),

    hist1 = px.histogram(data, x="kilometres", color_discrete_sequence=['lightblue'])
    hist1.update_layout(
        height=250,  # Added parameter
        width=330,  # Added parameter
        margin = dict(l=10, r=10, t=40, b=10),
        title_text = "distribution of distances",
    )
    return container, ind1,ind2, ind3,bar1,hist1

@app.callback([
    Output(component_id='ind4', component_property='figure'),
    Output(component_id='line1', component_property='figure')
    ],
    [Input(component_id='slct_period', component_property='value'),
     Input(component_id='slct_activity', component_property='value'),
     Input(component_id='slct_cat', component_property='value')]
)
def update_lower_graphs(slct_period, slct_act,slct_cat):
    data = df.loc[(df["type"] == slct_act) & (df["dist_cat"] == slct_cat)].copy()

    ind4 = go.Figure().add_trace(go.Indicator(
            mode = "number+delta",
            value = get_last_n_months(data, slct_period)['average_speed'].mean(),
            number={'suffix': " km/h", 'valueformat':'.1f'},
        ))

    ind4.update_layout(
        height=200,  # Added parameter
        width=200,  # Added parameter
        margin=dict(l=15, r=15, t=0, b=0),
        template={'data': {'indicator': [{
            'title': {'text': f"average speed <br><span style='font-size:0.8em;color:gray'>last {slct_period}  months</span>",
                      'font':{'size':15}},
            'mode': "number+delta+gauge",
            'delta': {'reference': get_last_n_months(data, slct_period,baseline=True)['average_speed'].mean()}}],

        }})

    line1 = px.line(get_last_n_months(data, 12),
                 x='start_date',
                 y='average_speed',
                 title= f'average speed of \'{slct_cat}\' {slct_act}s over time',
                 height=270,
                 )
    line1.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
    )
    line1.update_traces(line_color='#1c5bb4')
    return ind4, line1


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True, host = '127.0.0.1')

