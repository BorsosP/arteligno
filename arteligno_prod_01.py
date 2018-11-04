# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 19:11:18 2018

@author: cameg
"""

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import networkx as nx
import json
import plotly.plotly as py
import plotly.graph_objs as go
import dash_table_experiments as dt
import base64
import os
from flask import send_from_directory
from flask import Flask

server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(name = __name__, server = server)
app.config.supress_callback_exceptions = True

mapbox_access_token = 'pk.eyJ1IjoicGV0ZXJib3Jzb3MiLCJhIjoiY2poODB4aHRhMGJpMzJ3cXl6MGVtMjE1MiJ9.cz4Mg24W6JWliw_v6k72ww'
      
#import logo
image_filename = 'arteligno_logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())


with open('live_demo_skill_graph_01.json') as json_data:
    graph_visualization_data = json.load(json_data)

###creating filter values as lists
labels=[]
group=[]
skills_graph = []
occupations = []


for node in graph_visualization_data['nodes']:

    group.append(node['group'])

    if node['level'] == 'SKILL':
        skills_graph.append(node['id'].lower())
    elif node['level'] == 'OCCUPATION':
        occupations.append(node['id'].lower())




multi_job_vis = pd.read_excel('live_demo_classified_skill_matched_geocoded.xlsx')
multi_job_vis = multi_job_vis.sample(frac=1).reset_index(drop=True)
multi_job_vis.fillna('mv-9', inplace=True)
multi_job_vis = multi_job_vis[multi_job_vis['max_prob'] > 0.4]


skills = list(multi_job_vis['preferred_skill_label'].drop_duplicates().dropna().sort_values())
roles = list(multi_job_vis['prediction'].drop_duplicates().dropna().sort_values())
languages = list(multi_job_vis['language'].drop_duplicates().dropna().sort_values())
countries = list(multi_job_vis['country'].drop_duplicates().dropna().sort_values())
locations = list(multi_job_vis['city_name'].drop_duplicates().dropna().sort_values())

#Define HTML layout
app.layout = html.Div([
        
        
        html.Div([

           
            
            html.Div(
                html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height='150', width='150')
                )
            ],
            className="row header"
            ),
        html.P(),

    html.Div( children=[

    html.Div(className="row", children=[
                
       dcc.Dropdown(id='role_dropdown',
                    options=[
                        {'label': role, 'value': role} for role in roles
                        ],
                        value= [],
                        placeholder='Select a job category',
                        multi=True
                        , className="two columns"),   
                    
        
        dcc.Dropdown(id='skill_dropdown',
                        options=[
                            {'label': skill, 'value': skill} for skill in skills
                            ],
                            value= [],
                            placeholder='Select a skill',
                            multi=True
                            , className="two columns"),
                     
                     
        dcc.Dropdown(id='lang_dropdown',
                        options=[
                            {'label': lang, 'value': lang} for lang in languages
                            ],
                            value= [],
                            placeholder='Select a language',
                            multi=True
                            , className="two columns"),
                     
                     
       dcc.Dropdown(id='country_dropdown',
                        options=[
                            {'label': country, 'value': country} for country in countries
                            ],
                            value= [],
                            placeholder='Select a country',
                            multi=True
                            , className="two columns"),
                     
                     
        dcc.Dropdown(id='location_dropdown',
                        options=[
                            {'label': loc, 'value': loc} for loc in locations
                            ],
                            value= [],
                            placeholder='Select a city',
                            multi=True
                            , className="two columns")
                     
        
                     ]),
                     
                     
        html.Div(className="row", children=[
                
                  html.Div(className="twelve columns chart_div", children=[  
                            
                       dt.DataTable(
                            rows=[{}], # initialise the rows
                            filterable=False,
                            sortable=True,
                           selected_row_indices=[],
                           id='datatable'
                              )
                
                
                        ]),
                       
                       

                       
                       
                       
                       
        ]),
                       
                       
      html.Div(className="row", children=[
              
              
        html.Div(className="eight columns", children=[  
                
           dcc.Graph(id='job_map'
                      )
        ]),
        
          html.Div(className="four columns chart_div", children=[  
                    
              dcc.Graph(id='most_frequent_roles'
                      ),
                       
                        ]),
                       
      
           
           
#           html.Div(className="three columns chart_div", children=[  
#                
#                       dcc.Graph(id='number_of_jobs_by_languages'
#                                  )
#                                   
#                    
#                    
#                            ])
                     
        
     ]),
           
    html.Div(className="row", children=[
            
        
            
        html.Div(className="eight columns", children=[  
                
           dcc.Graph(id='skill_graph'
                      )
        ]),
           
         html.Div(className="four columns chart_div", children=[  
                
           dcc.Graph(id='most_frequent_skills'
                      )
           ]),
            
            
            
            
            
            ])
                       
  ], style={'margin': '1% 3%'})           
                       
])
           
         
#Base css for basic features
app.css.append_css({
    'external_url': ['static/base_01.css',
                     'static/base_02.css']
})



@app.server.route('/static/<path:path>')
def static_file(path):
    static_folder = os.path.join(os.getcwd(), 'static')
    return send_from_directory(static_folder, path)


@app.callback(
        Output(component_id='datatable', component_property='rows'),
        [Input(component_id='role_dropdown', component_property='value'),
         Input(component_id='skill_dropdown', component_property='value'),
         Input(component_id='lang_dropdown', component_property='value'),
         Input(component_id='country_dropdown', component_property='value'),
         Input(component_id='location_dropdown', component_property='value')]
        )

def update_datatable(role, skill, language , country, location):
    
    columns = ['company', 'position', 'description', 'language', 'url', 'prediction', 'country', 'city_name']
    
    
    multi_job_dt = multi_job_vis[columns + ['preferred_skill_label']].groupby(columns)['preferred_skill_label'].apply(list).reset_index()

    multi_job_dt['skill_flag'] = multi_job_dt['preferred_skill_label'].apply(lambda skill_data: all(x in skill_data for x in skill))

    cond1 = multi_job_dt['prediction'].isin(role)
    cond2 = multi_job_dt['skill_flag']==True
    cond3 = multi_job_dt['language'].isin(language)
    cond4 = multi_job_dt['country'].isin(country)
    cond5 = multi_job_dt['city_name'].isin(location)
    
    
    input_data = role + skill + language + country + location

#    
    if input_data == []:
        
        return multi_job_dt[columns].to_dict('records')
    
    
    elif role != []	and skill != [] and language != [] and country != [] and location != []:
        
        return multi_job_dt[columns][cond1 & cond2 & cond3 & cond4 & cond5].to_dict('records')
    
    
    elif  skill != [] and language != [] and country != [] and location != []:
        
        return multi_job_dt[columns][ cond2 & cond3 & cond4 & cond5].to_dict('records')
    
    elif  role != [] and language != [] and country != [] and location != []:
        
        return multi_job_dt[columns][ cond1 & cond3 & cond4 & cond5].to_dict('records')
    elif  role != [] and skill != [] and country != [] and location != []:
        
        return multi_job_dt[columns][ cond1 & cond2 & cond4 & cond5].to_dict('records')
    elif  role != [] and skill != [] and language != [] and location != []:
        
        return multi_job_dt[columns][ cond1 & cond2 & cond3 & cond5].to_dict('records')
    elif  role != [] and skill != [] and language != [] and country != []:
        
        return multi_job_dt[columns][ cond1 & cond2 & cond3 & cond4].to_dict('records')
    
    
    
    elif role != []	and skill != [] and language != []:
        
        return multi_job_dt[columns][cond1 & cond2 & cond3].to_dict('records')
    elif skill != []	and skill != [] and country != []:
        
        return multi_job_dt[columns][cond2 & cond3 & cond4].to_dict('records')
    elif language != []	and country != [] and location != []:
        
        return multi_job_dt[columns][cond3 & cond4 & cond5].to_dict('records')
    elif country != []	and location != [] and role != []:
        
        return multi_job_dt[columns][cond4 & cond5 & cond1].to_dict('records')
    
    elif role != []	and skill != [] and location != []:
        
        return multi_job_dt[columns][cond1 & cond2 & cond5].to_dict('records')
    elif role != []	and language != [] and country != []:
        
        return multi_job_dt[columns][cond1 & cond3 & cond4].to_dict('records')
    
    elif skill != []	and country != [] and location != []:
        
        return multi_job_dt[columns][cond2 & cond4 & cond5].to_dict('records')
    elif role != []	and skill != [] and country != []:
        
        return multi_job_dt[columns][cond1 & cond2 & cond4].to_dict('records')
    elif role != []	and language != [] and location != []:
        
        return multi_job_dt[columns][cond1 & cond3 & cond5].to_dict('records')
    elif skill != []	and language != [] and location != []:
        
        return multi_job_dt[columns][cond2 & cond3 & cond5].to_dict('records')
    
    
    
    
    
    
    
    
    elif role != []	and skill != []:
        
        return multi_job_dt[columns][cond1 & cond2].to_dict('records')
    elif role != []	and language != []:
        
        return multi_job_dt[columns][cond1 & cond3].to_dict('records')
    elif role != []	and country != []:
        
        return multi_job_dt[columns][cond1 & cond4].to_dict('records')
    elif role != []	and location != []:
        
        return multi_job_dt[columns][cond1 & cond5].to_dict('records')
    elif skill != []	and language != []:
        
        return multi_job_dt[columns][cond2 & cond3].to_dict('records')
    elif skill != []	and country != []:
        
        return multi_job_dt[columns][cond2 & cond4].to_dict('records')
    elif skill != []	and location != []:
        
        return multi_job_dt[columns][cond2 & cond5].to_dict('records')
    elif language != []	and country != []:
        
        return multi_job_dt[columns][cond3 & cond4].to_dict('records')
    
    elif language != []	and location != []:
        
        return multi_job_dt[columns][cond3 & cond5].to_dict('records')
    elif country != []	and location != []:
        
        return multi_job_dt[columns][cond4 & cond5].to_dict('records')
    
    
    
    
    
    
    elif role != []:
        
        return multi_job_dt[columns][cond1].to_dict('records')
    elif skill != []:
        
        return multi_job_dt[columns][cond2].to_dict('records')
    elif language != []:
        
        return multi_job_dt[columns][cond3].to_dict('records')
    elif country != []:
        
        return multi_job_dt[columns][cond4].to_dict('records')
    elif location != []:
        
        return multi_job_dt[columns][cond5].to_dict('records')
 


@app.callback(
        Output(component_id='most_frequent_roles', component_property='figure'),
        [Input(component_id='role_dropdown', component_property='value')]
        )

def update_roles(role):
    
    roles = multi_job_vis[['job_id', 'prediction']].drop_duplicates().groupby('prediction').count().reset_index().sort_values('job_id', ascending=False)
    roles = roles[0:10]
    labels = roles['prediction']
    values = roles['job_id']
    colors = ['#0B5DAF', '#1C7BB4', '#1E9EAF', '#1DB2B2', '1DB2AA', '1DB2A0', '1DB28E', '1DB2A0', '1DB295', '1DB250']
    
    data = [go.Pie(labels=labels, values=values, hole=0.7,
               hoverinfo='label', textinfo='value', marker=dict(colors=colors),
               textfont=dict(size=12)
               )]
    
    layout=go.Layout(
         title="Top 10 jobs by category ",
         margin=dict(l=0, r=0, t=40, b=0),
          legend=dict(orientation="h", font=dict(
            size=10
        )))

    
    fig = go.Figure(data=data, layout=layout)
    return fig



@app.callback(
        Output(component_id='most_frequent_skills', component_property='figure'),
        [Input(component_id='skill_dropdown', component_property='value')]
        )

def update_skills(skill):
    
    top_skills = multi_job_vis[['job_id', 'preferred_skill_label']].drop_duplicates().groupby('preferred_skill_label').count().reset_index().sort_values('job_id', ascending=False)
    top_skills = top_skills[top_skills['preferred_skill_label']!='mv-9'].copy()
    top_skills = top_skills[0:10]
    labels = top_skills['preferred_skill_label']
    values = top_skills['job_id']
    colors = ['#0B5DAF', '#1C7BB4', '#1E9EAF', '#1DB2B2', '1DB2AA', '1DB2A0', '1DB28E', '1DB2A0', '1DB295', '1DB250']
    
    data = [go.Pie(labels=labels, values=values,
               hoverinfo='label', textinfo='value', hole=0.7, marker=dict(colors=colors),
               textfont=dict(size=12)
               )]
    
    layout=go.Layout(
         title="Top 10 skills required",
         margin=dict(l=0, r=0, t=40, b=0),
         legend=dict(orientation="h", font=dict(
            size=10
        )))

    
    fig = go.Figure(data=data, layout=layout)
    return fig


#
#@app.callback(
#        Output(component_id='number_of_jobs_by_languages', component_property='figure'),
#        [Input(component_id='skill_dropdown', component_property='value')]
#        )
#
#def update_geo(geo):
#    
#    top_skills = multi_job_vis[['job_id', 'language']].drop_duplicates().groupby('language').count().reset_index().sort_values('job_id', ascending=False)
#    top_skills = top_skills[top_skills['language']!='mv-9'].copy()
#    #top_skills = top_skills[0:10]
#    labels = top_skills['language']
#    values = top_skills['job_id']
#    
#    data = [go.Pie(labels=labels, values=values,
#               hoverinfo='label', textinfo='value', hole=0.4,
#               textfont=dict(size=14)
#               )]
#    
#    layout=go.Layout(
#         title="Jobs by languages")
#
#    
#    fig = go.Figure(data=data, layout=layout)
#    return fig


@app.callback(
        Output(component_id='job_map', component_property='figure'),
        [Input(component_id='location_dropdown', component_property='value')]
        )

def update_map(location):
    
    location_df = multi_job_vis[['job_id', 'city_name', 'lat', 'long']].drop_duplicates().groupby(['lat', 'long', 'city_name']).count().reset_index().sort_values('job_id', ascending=False)
    
    
    if location == []:
        data = [
        go.Scattermapbox(
            lat=location_df['lat'],
            lon=location_df['long'],
            mode='markers',
            marker=dict(
                    size=10,
                    color="#086CB1"
                ),
            text=location_df['job_id'].astype(str) +  ' jobs in ' + location_df['city_name'],
        )
    ]
    
        layout = go.Layout(
        autosize=True,
        hovermode='closest',
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox=dict(
            style = 'dark',
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=59,
                lon=18
            ),
            pitch=0,
            zoom=5
        ),
    )

        fig = dict(data=data, layout=layout)
        return fig


    
         


 

##Decorator for 3D graph vizualisation
    
@app.callback(
        Output(component_id='skill_graph', component_property='figure'),
        [Input(component_id='role_dropdown', component_property='value'),
         Input(component_id='skill_dropdown', component_property='value')])
    
def update_graph(occupation_data, skill_data):
    
    #CONTENT HERE NEEDS TO BE MODIFIED TO A FUNCTION
    
    input_data =  occupation_data + skill_data
    input_data = [a.lower() for a in input_data]
    
    if input_data == []:
        
        fix_position_list = ['web developer', 'ict project manager', 'ict business analyst', 
            'software developer', 'ict network engineer', 'database administrator', 
            'ict consultant', 'data analyst', 'ict application developer', 'mobile app developer']
        
        for key, value in graph_visualization_data.items():
            if key == 'nodes':
                nodes_new = [k for k in value if k['id'].lower() in fix_position_list]
            if key == 'links':
                links_new = [k for k in value if k['source'].lower() in fix_position_list or
                 k['target'].lower() in fix_position_list ]
        
        new_graph_data = {'nodes' : nodes_new, 'links' : links_new}
        
        G = nx.json_graph.node_link_graph(new_graph_data)
        pos=nx.spring_layout(G, dim=3)
        
        
                
        Xn_role=[pos[k][0] for k in pos if k in occupations]
        Yn_role=[pos[k][1] for k in pos if k in occupations]
        Zn_role=[pos[k][2] for k in pos if k in occupations]
            
        role_labels = [k for k in pos if k in occupations]
        
        
        
        
        Xn_skill=[pos[k][0] for k in pos if k in skills_graph]
        Yn_skill=[pos[k][1] for k in pos if k in skills_graph]
        Zn_skill=[pos[k][2] for k in pos if k in skills_graph]
            
        skill_labels = [k for k in pos if k in skills_graph]
        
        
        
        Xe=[]
        Ye=[]
        Ze=[]
        for e in G.edges():
            Xe.extend([pos[e[0]][0], pos[e[1]][0], None])
            Ye.extend([pos[e[0]][1], pos[e[1]][1], None])
            Ze.extend([pos[e[0]][2], pos[e[1]][2], None])
        
    
        trace_nodes_role=go.Scatter3d(
                     x=Xn_role, 
                     y=Yn_role,
                     z=Zn_role,
                     mode='markers',
                     marker=dict(size='18', symbol='dot', color='rgb(255,140,0)'),
                     text=role_labels,
                     hoverinfo='text')
        
        trace_nodes_skill=go.Scatter3d(
                     x=Xn_skill, 
                     y=Yn_skill,
                     z=Zn_skill,
                     mode='markers',
                     marker=dict(symbol='dot', color='rgb(33,188,235)'),
                     text=skill_labels,
                     hoverinfo='text')
        
        trace_edges=go.Scatter3d(
                     mode='lines',
                     x=Xe,
                     y=Ye,
                     z=Ze,
                     line=dict(width=0.6, color='rgb(119,136,153)'),
                     hoverinfo='none' 
                    ) 
        
        axis=dict(showline=False, # hide axis line, grid, ticklabels and  title
              zeroline=False,
              showgrid=False,
              showticklabels=False,
              showbackground=False,
              title='' 
              )
        
        layout_skill_graph=go.Layout(
         title="Skill tree for Jobs",
         titlefont=dict(color='white'),
         showlegend=False,
         scene=go.Scene(
         xaxis=go.XAxis(axis),
         yaxis=go.YAxis(axis),
         zaxis=go.ZAxis(axis),
        ),
        margin=dict(l=0, r=0, t=40, b=0),
            
           
        
        hovermode='closest',
        plot_bgcolor='#131827',
        paper_bgcolor='#131827', #set background color            
        annotations=go.Annotations([
           go.Annotation(
           showarrow=False,
            text="",
            xref='paper',
            yref='paper',
            x=0,
            y=0.1,
            xanchor='left',
            yanchor='bottom',
            font=go.Font(
            size=14
            )
            )
            ])
        
        )  
        
        data=go.Data([trace_edges, trace_nodes_role, trace_nodes_skill])
        fig=go.Figure(data=data, layout=layout_skill_graph)
        
        return fig    
    
    else:
        
        for key, value in graph_visualization_data.items():
            if key == 'nodes':
                nodes_new = [k for k in value if k['id'].lower() in input_data]
            if key == 'links':
                links_new = [k for k in value if k['source'].lower() in input_data or
                 k['target'].lower() in input_data ]
        
        new_graph_data = {'nodes' : nodes_new, 'links' : links_new}
        
        G = nx.json_graph.node_link_graph(new_graph_data)
        pos=nx.spring_layout(G, dim=3)
                
                 
        Xn_role=[pos[k][0] for k in pos if k in occupations]
        Yn_role=[pos[k][1] for k in pos if k in occupations]
        Zn_role=[pos[k][2] for k in pos if k in occupations]
            
        role_labels = [k for k in pos if k in occupations]
        
        
        
        
        Xn_skill=[pos[k][0] for k in pos if k in skills_graph]
        Yn_skill=[pos[k][1] for k in pos if k in skills_graph]
        Zn_skill=[pos[k][2] for k in pos if k in skills_graph]
            
        skill_labels = [k for k in pos if k in skills_graph]
        
        
        
        Xe=[]
        Ye=[]
        Ze=[]
        for e in G.edges():
            Xe.extend([pos[e[0]][0], pos[e[1]][0], None])
            Ye.extend([pos[e[0]][1], pos[e[1]][1], None])
            Ze.extend([pos[e[0]][2], pos[e[1]][2], None])
        
    
        trace_nodes_role=go.Scatter3d(
                     x=Xn_role, 
                     y=Yn_role,
                     z=Zn_role,
                     mode='markers',
                     marker=dict(size='18', symbol='dot', color='rgb(255,140,0)'),
                     text=role_labels,
                     hoverinfo='text')
        
        trace_nodes_skill=go.Scatter3d(
                     x=Xn_skill, 
                     y=Yn_skill,
                     z=Zn_skill,
                     mode='markers',
                     marker=dict(symbol='dot', color='rgb(33,188,235)'),
                     text=skill_labels,
                     hoverinfo='text')
        
        trace_edges=go.Scatter3d(
                     mode='lines',
                     x=Xe,
                     y=Ye,
                     z=Ze,
                     line=dict(width=0.6, color='rgb(119,136,153)'),
                     hoverinfo='none' 
                    ) 
        
        axis=dict(showline=False, # hide axis line, grid, ticklabels and  title
              zeroline=False,
              showgrid=False,
              showticklabels=False,
              showbackground=False,
              title='' 
              )
        
        layout_skill_graph=go.Layout(
         title="Skill tree for Jobs",
         titlefont=dict(color='white'),
         showlegend=False,
         
         scene=go.Scene(
         xaxis=go.XAxis(axis),
         yaxis=go.YAxis(axis),
         zaxis=go.ZAxis(axis),
        ),
        margin=dict(l=0, r=0, t=40, b=0),
                
            
           
        
        hovermode='closest',
        plot_bgcolor='#131827',
        paper_bgcolor='#131827', #set background color            
        annotations=go.Annotations([
           go.Annotation(
           showarrow=False,
            text="",
            xref='paper',
            yref='paper',
            x=0,
            y=0.1,
            xanchor='left',
            yanchor='bottom',
            font=go.Font(
            size=14
            )
            )
            ])
        
        )  
        
        data=go.Data([trace_edges, trace_nodes_role, trace_nodes_skill])
        fig=go.Figure(data=data, layout=layout_skill_graph)
        
        return fig    
#    
#
#
#### Decorator for data table visualisatiion    
#    
#@app.callback(
#        Output(component_id='datatable', component_property='rows'),
#        [Input(component_id='occupation_dropdown', component_property='value')]
#        )
#
#def update_datatable(occupation_data):
#    if occupation_data == []:
#        return multi_job_vis[['jobtitle', 'company', 'joblocation_address', 'language', 'preferred_occupation_label']].to_dict('records')
#    else:
#        
#        occupation_keys = multi_job_vis[['preferred_occupation_label', 'occupationUri']].drop_duplicates()
#        occupation_key_need = occupation_keys[occupation_keys['preferred_occupation_label'].isin(occupation_data)]
#        
#        multi_job_vis_02 = multi_job_vis[['jobtitle', 'company', 'joblocation_address', 'language', 'preferred_occupation_label']][multi_job_vis['occupationUri'].isin(occupation_key_need['occupationUri'])]
#        return multi_job_vis_02.to_dict('records')
#    
#        
#### Decorator for top jobs visualisation
#        
#@app.callback(
#        Output(component_id='top_jobs', component_property='figure'),
#        [Input(component_id='occupation_dropdown', component_property='value')]
#        )
#
#def update_top_jobs(occupation_data):
#    if occupation_data == []:
#        size = [20, 40, 60, 80, 100, 80, 60, 40, 20, 40]
#        trace0 = go.Scatter(
#            x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
#            y=[11, 12, 10, 11, 12, 11, 12, 13, 12, 11],
#            mode='markers',
#            marker=dict(
#                size=size,
#                sizemode='area',
#                sizeref=2.*max(size)/(40.**2),
#                sizemin=4
#            )
#        )
#    data = [trace0]
#    fig=go.Figure(data=data)
#    return fig
#
##Decorator for MapBox
#@app.callback(
#        Output(component_id='job_map', component_property='figure'),
#        [Input(component_id='occupation_dropdown', component_property='value')]
#        )
#
#def update_map(occupation_data):
#    if occupation_data == []:
#        data = [
#        go.Scattermapbox(
#            lat=['45.5017'],
#            lon=['-73.5673'],
#            mode='markers',
#            marker=dict(
#                size=14
#            ),
#            text=['Montreal'],
#        )
#    ]
#    
#        layout = go.Layout(
#        autosize=True,
#        hovermode='closest',
#        mapbox=dict(
#            accesstoken=mapbox_access_token,
#            bearing=0,
#            center=dict(
#                lat=45,
#                lon=-73
#            ),
#            pitch=0,
#            zoom=5
#        ),
#    )
#
#        fig = dict(data=data, layout=layout)
#        return fig
#





if __name__ == '__main__':
    app.run_server(debug=True)



