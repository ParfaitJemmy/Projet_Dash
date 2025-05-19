from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

# # Callback pour gérer le téléversement de fichier et la sélection
def layout():
    return dbc.Container([
        html.H2("Charger vos données"),
        dcc.Upload(
            id='upload-data',
            children=html.Div(['Glissez et déposez ou ', html.A('sélectionnez un fichier CSV')]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                'textAlign': 'center', 'margin': '10px'
            },
            multiple=False
        ),
        html.Label("Délimiteur détecté :"),
        html.Div(id='delimiter-display', className="mb-2"),
        html.Label("Modifier le délimiteur (si nécessaire) :"),
        dcc.Dropdown(
            id='delimiter-dropdown',
            options=[
                {'label': 'Virgule (,)', 'value': ','},
                {'label': 'Point-virgule (;)', 'value': ';'},
                {'label': 'Tabulation (\t)', 'value': '\t'},
                {'label': 'Espace ( )', 'value': ' '}
            ],
            placeholder="Utiliser le délimiteur détecté",
            clearable=True
        ),
        html.Div(id='file-upload-error', className='text-danger'),
        dcc.Loading(html.Div(id='data-preview', className='mt-4')),
    ])
# Fonction pour créer un tableau de données
def create_data_table(df):
    boolean_cols = [col for col in df.columns if (df[col].dtype == 'bool') or 
                    (set(str(val).lower() for val in df[col].dropna().unique()).issubset(
                        {'0', '1', 'true', 'false', 'yes', 'no', 'y', 'n', 't', 'f'}))]
    columns = [
        {
            'name': i,
            'id': i,
            'type': 'numeric' if df[i].dtype in ['float64', 'int64'] and i not in boolean_cols else 'text'
        } for i in df.columns
    ]
    style_data_conditional = [
        {
            'if': {'column_type': 'numeric'},
            'format': {'specifier': '.2f'}
        }
    ] + [
        {
            'if': {'column_id': col},
            'className': "boolean"
        } for col in boolean_cols
    ]
    return dash_table.DataTable(
        data=df.head(10).to_dict('records'),
        columns=columns,
        page_size=10,
        style_table={'overflowX': 'auto', 'maxHeight': '500px', 'overflowY': 'auto', 'border': '1px solid #dee2e6', 'borderRadius': '5px'},
        style_header={
            'backgroundColor': '#007bff',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': '1px solid #dee2e6',
            'padding': '10px'
        },
        style_cell={
            'padding': '10px',
            'border': '1px solid #dee2e6',
            'fontSize': '14px',
            'textAlign': 'left',
            'minWidth': '100px',
            'maxWidth': '200px',
            'whiteSpace': 'normal',
            'height': 'auto',
            'backgroundColor': 'white',
            'color': 'black'
        },
        style_data_conditional=style_data_conditional + [
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            },
            {
                'if': {'state': 'selected'},
                'backgroundColor': '#e9ecef',
                'border': '1px solid #007bff'
            }
        ]
    )
