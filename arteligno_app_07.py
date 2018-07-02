# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 19:11:18 2018

@author: cameg
"""

from flask import Flask
import os
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

server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(name = __name__, server = server)
app.config.supress_callback_exceptions = True

mapbox_access_token = 'pk.eyJ1IjoicGV0ZXJib3Jzb3MiLCJhIjoiY2poODB4aHRhMGJpMzJ3cXl6MGVtMjE1MiJ9.cz4Mg24W6JWliw_v6k72ww'

#app.css.config.serve_locally = True
#app.scripts.config.serve_locally = True

#### THIS IS TO CREATE THE SKILL GRAPH
##Prepare the graph with networkx
with open('esco_vis_02.json') as json_data:
    graph_visualization_data = json.load(json_data)

###creating filter values as lists
labels=[]
group=[]
skills = []
occupations = []
isco_categories = []


for node in graph_visualization_data['nodes']:

    group.append(node['group'])

    if node['level'] == 'SKILL':
        skills.append(node['id'].lower())
    elif node['level'] == 'OCCUPATION':
        occupations.append(node['id'].lower())
    else:
        isco_categories.append(node['id'].lower())


###importing matched job posts
multi_job_vis = pd.read_excel('esco_matched_for_vis_2018_05_04.xlsx')


###creating base data for top job visualization
multi_job_vis['row_count'] = 1
multi_job_vis_aggr = multi_job_vis[['occupationUri', 'preferred_occupation_label', 'row_count']].groupby(['occupationUri', 'preferred_occupation_label']).sum()
multi_job_vis_aggr.reset_index(inplace=True)
multi_job_vis_aggr.sort_values('row_count', ascending=False, inplace=True)


#import logo
image_filename = 'arteligno_logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())


#Define HTML layout
app.layout = html.Div([

        #Import logo
        html.Div([
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height='254', width='258')
        ], className="ten columns padded"),


            html.Div([

                #Header
                html.Div([
                        html.H5(
                                'The skill based job search portal')
                        ], className="twelve columns padded")

                    ], className="row gs-header gs-text-header"),



                        html.Br([]),

                        #Mission Statement and brief description
                        html.P(""" Finding your next job in the IT Sector can be a painful process.
                               On most sites you can only search for vague position names and only a few keywords. Why waste your time
                               looking for job posts which does not fit your skillset at all? Our application uses Machine Learning
                               technologies and the power of the ESCO (European Skills/Competences, qualifications and Occupations) database, which makes skill
                               based and true multilangual job search a reality.
                               Find your next dreamjob with selecting the skills you have (or wish to have), or simply select the occupations that you would be interested in.
                        """),

                        html.Br([]),
                        #Dropdowns for filtering
                        html.Div([
                                        dcc.Dropdown(id='isco_dropdown',
                                            options=[
                                                {'label': isco, 'value': isco} for isco in isco_categories
                                                ],
                                                value= [],
                                                placeholder='Select an ISCO category',
                                                multi=True

                                            ),
                                        dcc.Dropdown(id='occupation_dropdown',
                                            options=[
                                                {'label': occup, 'value': occup} for occup in occupations
                                                ],
                                                value= [],
                                                placeholder='Select an occupation',
                                                multi=True
                                                ),
                                        dcc.Dropdown(id='skill_dropdown',
                                            options=[
                                                {'label': skill, 'value': skill} for skill in skills
                                                ],
                                                value= [],
                                                placeholder='Select a skill',
                                                multi=True
                                                ),

                           ]),

                        html.Br([]),

                        #3D Skill Graph
                        html.Div([
                                        dcc.Graph(id='skill_graph')

                        ]),

                        html.Div([
                            html.Div(className="row",
                            children=[
                                    html.Div(className="four columns",
                                             children = [
                                                     html.Div(children = [
                                                        #Table for additional filtering and listing out the positions
                                                        dt.DataTable(
                                                            rows=[{}], # initialise the rows
                                                            row_selectable=True,
                                                            filterable=True,
                                                            sortable=True,
                                                            selected_row_indices=[],
                                                            id='datatable'
                                                            ),
                        #                                 dcc.Graph(
                        #                                    id='top_jobs',
                        #                                        )
                                                            ])
                                                        ]
                                                    ),


                                                html.Div(className="four columns",

                                                         children=html.Div([

                                                            #Mapbox map for extra visualization for GEO data
                                                            dcc.Graph(id='job_map')

                                                                 ])
                                                        ),
                                                html.Div(className="four columns",

                                                         children=html.Div([


                                                            #Placeholder vizualization
                                                            dcc.Graph(id='top_jobs')

                                                             ])
                                                        )


                            ]
                        )
                    ])

                ])

#Base css for basic features
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})
#

###Decorator for 3D graph vizualisation

@app.callback(
        Output(component_id='skill_graph', component_property='figure'),
        [Input(component_id='isco_dropdown', component_property='value'),
         Input(component_id='occupation_dropdown', component_property='value'),
         Input(component_id='skill_dropdown', component_property='value')])

def update_graph(isco_data, occupation_data, skill_data):

    #CONTENT HERE NEEDS TO BE MODIFIED TO A FUNCTION

    input_data = isco_data + occupation_data + skill_data

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




        Xn_skill=[pos[k][0] for k in pos if k in skills]
        Yn_skill=[pos[k][1] for k in pos if k in skills]
        Zn_skill=[pos[k][2] for k in pos if k in skills]

        skill_labels = [k for k in pos if k in skills]



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
         title="Skills required for IT jobs",
         titlefont=dict(color='white'),
         showlegend=False,
         height=800,
         scene=go.Scene(
         xaxis=go.XAxis(axis),
         yaxis=go.YAxis(axis),
         zaxis=go.ZAxis(axis),
        ),
                margin=go.Margin(
                t=100


        ),
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




        Xn_skill=[pos[k][0] for k in pos if k in skills]
        Yn_skill=[pos[k][1] for k in pos if k in skills]
        Zn_skill=[pos[k][2] for k in pos if k in skills]

        skill_labels = [k for k in pos if k in skills]



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
         title="Skills required for IT jobs",
         titlefont=dict(color='white'),
         showlegend=False,
         height=800,
         scene=go.Scene(
         xaxis=go.XAxis(axis),
         yaxis=go.YAxis(axis),
         zaxis=go.ZAxis(axis),
        ),
                margin=go.Margin(
                t=100


        ),
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



### Decorator for data table visualisatiion

@app.callback(
        Output(component_id='datatable', component_property='rows'),
        [Input(component_id='occupation_dropdown', component_property='value')]
        )

def update_datatable(occupation_data):
    if occupation_data == []:
        return multi_job_vis[['jobtitle', 'company', 'joblocation_address', 'language', 'preferred_occupation_label']].to_dict('records')
    else:

        occupation_keys = multi_job_vis[['preferred_occupation_label', 'occupationUri']].drop_duplicates()
        occupation_key_need = occupation_keys[occupation_keys['preferred_occupation_label'].isin(occupation_data)]

        multi_job_vis_02 = multi_job_vis[['jobtitle', 'company', 'joblocation_address', 'language', 'preferred_occupation_label']][multi_job_vis['occupationUri'].isin(occupation_key_need['occupationUri'])]
        return multi_job_vis_02.to_dict('records')


### Decorator for top jobs visualisation

@app.callback(
        Output(component_id='top_jobs', component_property='figure'),
        [Input(component_id='occupation_dropdown', component_property='value')]
        )

def update_top_jobs(occupation_data):
    if occupation_data == []:
        size = [20, 40, 60, 80, 100, 80, 60, 40, 20, 40]
        trace0 = go.Scatter(
            x=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            y=[11, 12, 10, 11, 12, 11, 12, 13, 12, 11],
            mode='markers',
            marker=dict(
                size=size,
                sizemode='area',
                sizeref=2.*max(size)/(40.**2),
                sizemin=4
            )
        )
    data = [trace0]
    fig=go.Figure(data=data)
    return fig

#Decorator for MapBox
@app.callback(
        Output(component_id='job_map', component_property='figure'),
        [Input(component_id='occupation_dropdown', component_property='value')]
        )

def update_map(occupation_data):
    if occupation_data == []:
        data = [
        go.Scattermapbox(
            lat=['45.5017'],
            lon=['-73.5673'],
            mode='markers',
            marker=dict(
                size=14
            ),
            text=['Montreal'],
        )
    ]

        layout = go.Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=45,
                lon=-73
            ),
            pitch=0,
            zoom=5
        ),
    )

        fig = dict(data=data, layout=layout)
        return fig






if __name__ == '__main__':
    app.run_server(debug=True)
