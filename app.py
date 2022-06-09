# Dashboard Analítico Interativo de Vendas com Dash em Python

# Imports
import dash
import plotly
import locale
import numpy as np
import pandas as pd
import sklearn as sl
import seaborn as sns
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
import json
from pandasql import sqldf
from scipy import stats
from sklearn.preprocessing import MinMaxScaler
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
from urllib.request import urlopen
import warnings
warnings.filterwarnings("ignore")

# Carregando os dados

tp_sus=pd.read_excel('dataset/tp_sus.xlsx')
estabelecimentos=pd.read_excel('dataset/estabelecimentos.xlsx')
tp_cbo_sus=pd.read_excel('dataset/tp_cbo_sus.xlsx')
qt_ch=pd.read_excel('dataset/qt_ch3.xlsx')
br_pop=pd.read_excel('dataset/brasiluf.xlsx')
QTMedEnf=pd.read_excel('dataset/QTMedEnf.xlsx')

#### FUNÇÃO PANDAS PARA EXECUÇÃO DE LINGUAGEM SQL

query = lambda q: sqldf(q, globals())
token = 'pk.eyJ1IjoiY2FybGZpbGhvMiIsImEiOiJjbDI5cHhic3kwNXVwM2R1cG80cW1sMXBrIn0.SblIdP3C3AXHY6LSZB603Q'

############################# NORMALIZANO DADOS ###########################

def rescaledQ(var):
    q_array=np.asarray(var)
    q_array=q_array.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range = (0, 1))
    rscl = scaler.fit_transform(q_array)    
    lst = []
    for x in rscl.tolist():
        lst.extend(x)
    
    return lst
############################      SELEÇÕES      #######################################

sus_por_Estado=tp_cbo_sus[['CO_SIGLA_ESTADO','TP_SUS_NAO_SUS','CO_PROFISSIONAL_SUS']].groupby(by=['CO_SIGLA_ESTADO','TP_SUS_NAO_SUS',],as_index=False).sum()

########## Padrões de Formatação  #################
colunas_style = {'align':'left', 'border':'1px solid black', 'background-color': 'black', 'color':'white', 'padding': '6px', 'margin':'0.2rem'}
tab_style = {'border': '1px solid black', 'padding': '5px', 'margin':'1rem', 'fontWeight': 'bold'}
tab_style2 = {'padding': '5px', 'margin':'1rem', 'fontWeight': 'bold', 'color':'white', 'size':18}
tab_selected_style = {'border':'1px solid black', 'background-color': 'black', 'color':'white', 'margin':'1rem', 'padding': '6px'}

# Variáveis para formatação
title_font = {'size':20,'color':'black'}
legend_font = {'size':16,'color':'black'}
global_font = dict(family = "Roboto")

########## Dados Gerais sobre Saude no brasil

total_prof=tp_sus.CO_PROFISSIONAL_SUS.sum()
total_estabs=estabelecimentos.groupby(by='CO_SIGLA_ESTADO',as_index=False)[['CO_UNIDADE','CO_SIGLA_ESTADO']].count().sum().values[1]
total_sus=tp_sus.query("TP_SUS_NAO_SUS=='Sim'")['CO_PROFISSIONAL_SUS'].sum()
media_horas=qt_ch.QT_CARGA_HORARIA_AMBULATORIAL.mean()
total_pop=br_pop['pop'].sum()
max_media_horas=qt_ch[['CO_SIGLA_ESTADO','QT_CARGA_HORARIA_AMBULATORIAL']].groupby(by='CO_SIGLA_ESTADO', as_index=False).mean()
max_media_estado=max_media_horas.QT_CARGA_HORARIA_AMBULATORIAL.max()

Estados=tp_sus.Estado.unique()
uf=tp_sus.CO_SIGLA_ESTADO.unique()

#CLOROPETH MAP

global Brazil

with urlopen('https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson') as response:
    Brazil = json.load(response) # Javascrip object notation
state_id_map = {}
for feature in Brazil['features']:
    feature['id'] = feature['properties']['name']
    state_id_map[feature['properties']['sigla']] = feature['id']

profs=tp_sus[['Estado','CO_PROFISSIONAL_SUS']].groupby('Estado', as_index=False ).sum()
br_map_profs = px.choropleth_mapbox(
                profs, # database
                locations = 'Estado', #define the limits on the map/geography
                geojson = Brazil, #shape information
                color = "CO_PROFISSIONAL_SUS", #defining the color of the scale through the database
                hover_name = 'CO_PROFISSIONAL_SUS', #the information in the box
                hover_data =['Estado'],                                
                color_continuous_scale = 'plotly3',                
                center={"lat":-14, "lon": -55},#define the limits that will be plotted
                zoom = 2.5,# view size
                opacity = 0.5, #opacity of the map color, to appear the background
                labels = {'CO_PROFISSIONAL_SUS':'Total'},                
                ).update_layout(mapbox_style="dark",
                                mapbox_accesstoken =token, 
                                font = global_font,
                                font_color = 'white',
                                geo = dict(bgcolor = 'black'),
                             #paper_bgcolor = 'rgba(0,0,0,0)',
                             #plot_bgcolor = 'rgba(0,0,0,0)',                             
                                paper_bgcolor = 'black',
                                plot_bgcolor = 'black',
                                template = "plotly_dark",
                                margin={"r":0,"t":0,"l":0,"b":0}).update_geos(fitbounds = 'locations',visible = True)
                

br_map_estabs = px.choropleth_mapbox(
                estabelecimentos, # database
                locations = 'Estado', #define the limits on the map/geography
                geojson = Brazil, #shape information
                color = "CO_UNIDADE", #defining the color of the scale through the database
                hover_name = 'CO_UNIDADE', #the information in the box
                hover_data =['Estado'],
                color_continuous_scale = 'plotly3',                
                center={"lat":-14, "lon": -55},#define the limits that will be plotted
                zoom = 2.5, #map view size
                opacity = 0.5, #opacity of the map color, to appear the background
                labels = {'CO_UNIDADE':'Total'},
                #animation_frame = 'Estado',
                ).update_layout(mapbox_style="dark",
                                mapbox_accesstoken =token, 
                                font = global_font,
                                font_color = 'white',
                                geo = dict(bgcolor = 'black'),
                             #paper_bgcolor = 'rgba(0,0,0,0)',
                             #plot_bgcolor = 'rgba(0,0,0,0)', 
                                paper_bgcolor = 'black',
                                plot_bgcolor = 'black',
                                template = "plotly_dark",
                                margin={"r":0,"t":0,"l":0,"b":0}).update_geos(fitbounds = 'locations', visible = True)


br_map_pops = px.choropleth_mapbox(
                br_pop, # database
                locations = 'estado', #define the limits on the map/geography
                geojson = Brazil, #shape information
                color = "pop", #defining the color of the scale through the database
                hover_name = 'pop', #the information in the box
                hover_data =['estado'],                
                color_continuous_scale = 'plotly3',                                
                center={"lat":-14, "lon": -55},#define the limits that will be plotted
                zoom = 2.5, #map view size
                opacity = 0.5, #opacity of the map color, to appear the background
                labels = {'pop':'Total'},                  
                ).update_layout(mapbox_style="dark",
                                mapbox_accesstoken =token, 
                                font = global_font,
                                font_color = 'white',
                                geo = dict(bgcolor = 'black'),
                             #paper_bgcolor = 'rgba(0,0,0,0)',
                             #plot_bgcolor = 'rgba(0,0,0,0)', 
                                paper_bgcolor = 'black',
                                plot_bgcolor = 'black',
                                template = "plotly_dark",
                                margin={"r":0,"t":0,"l":0,"b":0}).update_geos(fitbounds = 'locations', visible = True)


####################### BOXSPLOT 

#box_fig = px.box(qt_ch, x="CO_SIGLA_ESTADO", y="QT_CARGA_HORARIA_AMBULATORIAL", color="CO_SIGLA_ESTADO", template='plotly_dark')
#box_fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
#box_fig2.update_traces(quartilemethod="inclusive") # or "inclusive", or "linear" by default

####################### Bootstrap ##############

text_input = html.Div(
    [
        dbc.Input(id="input", placeholder="Profissão", type="text"),        
    ]
)

scatterFig = px.scatter(QTMedEnf, x="ch_en", y='ch_md' , trendline="ols", labels={'ch_en':'Enfermeiros'}, template="plotly_dark")

##### App Dash #####

app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.DARKLY], 
                suppress_callback_exceptions = True, 
                meta_tags = [{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

server = app.server

app.title = 'Dashboard Analítico'                     

##### Barra Lateral #####

drop_items=[{"label": label, "value":label} for label in Estados]
drop_items2=[{"label": label, "value":label} for label in qt_ch.DS_ATIVIDADE_PROFISSIONAL.unique()]

radio_pie = html.Div([
        
        dbc.Checklist(
            options=[
                {"label": "Não SUS", "value": 1},                
            ],
            value=[],
            id="radio_pie",
            inline=True,
            switch=True,            
        ),
    ])

radio_map = html.Div(
    [
        dbc.RadioItems(
            id="radio_map",            
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-primary",
            labelCheckedClassName="active",            
            options=[
                {"label": "População", "value":1},
                {"label": "Estabelecimentos", "value":2},                
                {"label": "Profissionais", "value": 3},                
            ],
            value=1,            
        ),
        html.Div(id="output"),
    ],
    className="radio-group",
)


dropdown3 = dbc.Select(
               id='dropdown3',
               options=drop_items2,
               value='ENFERMEIRO', 
               style=colunas_style,
           )


# barra de navegação

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row([                        
                        dbc.Col(html.H1("Dashboard Analítico Degerts")),
                    ],
                    align="center",
                    className="g-0",
                ),                
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),            
        ], 
    ),
    color="dark",
    dark=True,
)

##### Home Page #####

# Formatar os números decimais
locale.setlocale(locale.LC_ALL, '')

# Container
h_container = dbc.Container(
    [

#############              CABEÇARIO               #####################        
        
        dbc.Row([
            dbc.Col([
                        html.P('População Total do Brasil ', 
                                style = tab_style,
                                className = 'text-white rounded-lg shadow p-1 bg-dark',
                               ),
                        html.H4('{}'.format(str(locale.format("%.2f", total_pop, grouping=True))), style = tab_style2,),
                ]),
            dbc.Col([
                        
                        html.P('Total de Profissionais de Saúde ', 
                                style = tab_style,
                                className = 'text-white rounded-lg shadow p-1 bg-dark',
                               ),
                        
                        html.H4('{}'.format(str(locale.format("%.2f", total_prof, grouping=True))), style = tab_style2,),
                ]),        
            dbc.Col([
                
                        html.P('Total de Estabelecimentos de Saúde', 
                                style = tab_style,
                                className='text-white rounded-lg shadow p-1 bg-dark',
                               ),
                        html.H4('{}'.format(str(locale.format("%.2f", total_estabs, grouping=True))), style = tab_style2,),
                ]),
            ]),
        
        dbc.Row([
            dbc.Col([
                        html.P('Profissionais que atendem pelo SUS', 
                                style = tab_style,
                                className='text-white rounded-lg shadow p-1 bg-dark',
                               ),
                        html.H4('{}'.format(str(locale.format("%.2f", total_sus, grouping=True))), style = tab_style2,),
                ]),            
            dbc.Col([
                
                        html.P('Média da Carga Horária Ambulatorial', 
                                style = tab_style,
                                className='text-white rounded-lg shadow p-1 bg-dark',
                               ),
                        html.H4('{}'.format(str(locale.format("%.2f", media_horas, grouping=True))), style = tab_style2,),
                ]),
            dbc.Col([
                        html.P('Maior média Carga Horária por Estado', 
                                style = tab_style,
                                className='text-white rounded-lg shadow p-1 bg-dark',
                               ),
                        html.H4('{}'.format(str(locale.format("%.2f", max_media_estado, grouping=True))), style = tab_style2,),
                ]),
        ]), 
        
#############              PRIMEIRA LINHA               #####################
        
        dbc.Row([
            dbc.Col(html.Div(radio_pie), width={'size':3,'offset':1}, style = {'align':'left',  'order':1},),            
            dbc.Col(html.Div(radio_map), width={'size':3,'offset':1}, style = {'align':'right', 'order':2},),             
            ], align='center', no_gutters = True, justify = 'between'),
        
        dbc.Row([                            
                dbc.Col([                                        
                    dcc.Graph(id = 'pie',figure = {}, responsive=True),                     
                    
                ],width = {'size':4, 'offset':0}, style = {'align':'left', "border": "1px solid grey", 'borderleft:':False},
                ),
                
                dbc.Col([                    
                    dcc.Graph(id = 'histSUS',figure = {}, responsive=True),
                    
                ],width = {'size':4, 'offset':0}, style = {'align':'left', "border": "1px solid grey", 'borderleft:':False},
                ),

                dbc.Col([
                    dcc.Graph(id = 'map',figure = {}, responsive=True),
                    
            ],width = {'size':4, 'offset':0}, style = {'align':'left', "border": "1px solid grey", 'borderleft:':False},),                
            ],no_gutters = True, justify = 'around', style={"border": "1px solid grey"}),      
           
            
#########################         TERCEIRA LINHA           #######################################
        
        dbc.Row([
            dbc.Col([html.P('Selecione uma profissão: ',                                 
                                className = 'text-white rounded-lg shadow p-1 bg-dark',
                                style = tab_style2,
                               )],width='auto', style = {'align':'left'}), 
            dbc.Col(html.Div(dropdown3), width=4, style = {'align':'left'}),
            dbc.Col(html.Div(text_input, style = tab_style2), width=4, style = {'align':'left'}),
            ], align='center', no_gutters = True, justify = 'start'),
                
        dbc.Row([
            dbc.Col(dcc.Graph(id = 'hist1',figure = {} , responsive=True), style={"border": "1px solid grey", 'borderTop':True}),
            dbc.Col(dcc.Graph(id = 'hist2',figure = {} , responsive=True), style={"border": "1px solid grey", 'borderTop':True}),
            dbc.Col(dcc.Graph(id = 'box1',figure = {} , responsive=True), style={"border": "1px solid grey", 'borderTop':True}),
            dbc.Col(dcc.Graph(id = 'scatter', figure = scatterFig , responsive=True), style={"border": "1px solid grey", 'borderTop':True}),            
        ], no_gutters = True, justify = 'start', style={"border": "1px solid grey"}),
    
    ], fluid = True,
)

##### Layout Principal #####

CONTENT_STYLE = {"marginLeft": "2rem",
                 "margin-right": "2rem",
                 "padding": "0rem 0rem",
                 #'background-color':'#F0F4F5',                 
                 #'background-color':'black',                 
                }

content = html.Div(id = "page-content", children = [], style = CONTENT_STYLE )


##### Layout Geral #####

app.layout = html.Div([
        dcc.Location(id = "url"),         
        navbar,
        content
    ])


##### App Callback Functions ######
# Calback para renderização das páginas
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])

def render_page_content(pathname):
    if pathname == "/":
        return [h_container]    

    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"O caminho {pathname} não foi reconhecido..."),
        ]
    )


#função do grafico de pizza
@app.callback(
    Output(component_id = 'pie', component_property = 'figure'),
    Output(component_id = 'histSUS', component_property = 'figure'),
    [Input(component_id = 'radio_pie', component_property = 'value')]
)

def update_pie(value):
    if value==[1]:
        opt='Não'
    else: opt='Sim'
        
    sus_por_Estado=tp_cbo_sus.loc[tp_cbo_sus.TP_SUS_NAO_SUS==opt,
                            ['CO_SIGLA_ESTADO','CO_PROFISSIONAL_SUS']].groupby(by=['CO_SIGLA_ESTADO'],as_index=False).sum()
    sus_por_Estado2=tp_cbo_sus.loc[tp_cbo_sus.TP_SUS_NAO_SUS==opt,
                                   ['TP_CBO_SAUDE','ST_CBO_REGULAMENTADO','CO_PROFISSIONAL_SUS']].groupby(by=['TP_CBO_SAUDE','ST_CBO_REGULAMENTADO'],as_index=False).sum()
    
    fig1 = px.pie(sus_por_Estado,
                    values=sus_por_Estado.CO_PROFISSIONAL_SUS, 
                    names=sus_por_Estado.CO_SIGLA_ESTADO,                    
                    color=sus_por_Estado.CO_SIGLA_ESTADO,                    
                    labels={'CO_PROFISSIONAL_SUS':'Profissionais'},
                    template = "plotly_dark",
                    hole=.5)    
    fig1.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
    
    fig2 = px.histogram(sus_por_Estado2, 
                  x="TP_CBO_SAUDE", 
                  y="CO_PROFISSIONAL_SUS", 
                  color="ST_CBO_REGULAMENTADO",                  
                  labels={'ST_CBO_REGULAMENTADO':'REGULAMENTADO','CO_PROFISSIONAL_SUS_sum':'Profissionais com CBO Saúde','TP_CBO_SAUDE':'CBO SAÚDE', 'TP_SUS_NAO_SUS':'SUS'},
                  barmode="group",
                  histfunc='sum',
                  histnorm='percent',
                  color_discrete_sequence=['blue','purple'],
                  template="plotly_dark",
                 )
   
    return fig1, fig2

# Callback para update do Mapa do Brasil
@app.callback(
    Output(component_id = 'map', component_property = 'figure'),
    [Input(component_id = 'radio_map', component_property = 'value')]
)

def update_output(option):

    if option==2:
        return br_map_estabs
    elif option==3:
        return br_map_profs
    else:
        return br_map_pops
    
@app.callback(Output("input", "value"), [Input("dropdown3", "value")])
def output_text(value):
    return value

@app.callback(Output("hist1", "figure"),
            Output("hist2", "figure"), 
            Output("box1", "figure"), [Input("input", "value")])

def update_histogram(option):
    
    option=str(option).upper()    
    ds_tabela_prof =query("select  DS_ATIVIDADE_PROFISSIONAL as 'Profissão', CO_SIGLA_ESTADO as 'Estado', sum(QT_CARGA_HORARIA_AMBULATORIAL) as 'Carga_Horaria' "+
                         "from qt_ch "+
                        "where DS_ATIVIDADE_PROFISSIONAL like '%"+option+"%' and DS_ATIVIDADE_PROFISSIONAL not like '%exceto%' "+
                        "group by DS_ATIVIDADE_PROFISSIONAL, CO_SIGLA_ESTADO")    
    
    
    qHist1 = px.histogram(ds_tabela_prof,                           
                          x="Carga_Horaria",                          
                          histfunc='avg',        
                          histnorm='percent',
                          template='plotly_dark',                          
                          marginal='box',
                         )

    qHist2 = px.histogram(ds_tabela_prof,
                          x="Estado",
                          y="Carga_Horaria",
                          histfunc='avg',
                          histnorm='percent',
                          template="plotly_dark",
                          marginal='box'
                        )
    
    group_labels = ['Carga_Horaria']
    hist_data= [rescaledQ(ds_tabela_prof.Carga_Horaria)]
    distPlot = ff.create_distplot(hist_data, 
                                  group_labels, bin_size=.2, curve_type='normal').update_layout(template="plotly_dark")    
    
    
    return distPlot, qHist2, qHist1

    
# Executa a app
if __name__=='__main__':
    app.run_server(debug = False, use_reloader = False, host='0.0.0.0', port='5000') 