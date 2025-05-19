from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import io
# fonction pour afficher la visualisation dynamique des données
def layout():
    return dbc.Container([
        html.H2("Visualisation Dynamique", className="text-center mt-4"),
        html.P("Créez un graphique en sélectionnant les axes X et Y.", className="text-info"),
        
        html.Label("Axe X"),
        dcc.Dropdown(id='x-axis-dropdown', placeholder="Sélectionnez l'axe X"),
        
        html.Label("Axe Y"),
        dcc.Dropdown(id='y-axis-dropdown', placeholder="Sélectionnez l'axe Y"),
        
        html.Label("Type de graphique"),
        dcc.Dropdown(
            id='graph-type-dropdown',
            options=[
                {'label': 'Nuage de points (scatter)', 'value': 'scatter'},
                {'label': 'Histogramme', 'value': 'histogram'},
                {'label': 'Boxplot', 'value': 'box'},
                {'label': 'Barres', 'value': 'bar'}
            ],
            placeholder="Sélectionnez un type de graphique"
        ),
        
        html.Br(),
        dcc.Loading(dcc.Graph(id='dynamic-plot')),
        html.Div(id='visualisation-error', className='text-danger mt-2'),

        html.Hr(),
        html.H4("Matrice de corrélation (Heatmap)", className="mt-4"),
        dcc.Loading(dcc.Graph(id='correlation-matrix'))
    ])
# Fonction pour créer un tableau de données
def register_callbacks(app):
    @app.callback(
        [Output('x-axis-dropdown', 'options'),
         Output('y-axis-dropdown', 'options')],
        Input('data-store', 'data')
    )
    def update_dropdowns(data):
        if data:
            try:
                df = pd.read_json(io.StringIO(data), orient='split')
                options = [{'label': col, 'value': col} for col in df.columns]
                return options, options
            except Exception as e:
                print(f"Erreur dans update_dropdowns : {e}")
        return [], []

    @app.callback(
        [Output('dynamic-plot', 'figure'),
         Output('visualisation-error', 'children')],
        [Input('x-axis-dropdown', 'value'),
         Input('y-axis-dropdown', 'value'),
         Input('graph-type-dropdown', 'value')],
        State('data-store', 'data')
    ) # fonction pour mettre à jour le graphique
    def update_graph(x, y, graph_type, data):
        if not data:
            return px.scatter(title="Aucune donnée chargée"), "Veuillez charger des données."
        try:
            df = pd.read_json(io.StringIO(data), orient='split')
            if not x or not y:
                return px.scatter(title="Sélectionnez les axes X et Y"), ""

            if graph_type == 'scatter':
                fig = px.scatter(df, x=x, y=y, title=f"{y} vs {x}")
            elif graph_type == 'histogram':
                fig = px.histogram(df, x=x, y=y, barmode='overlay', title=f"Histogramme de {y} selon {x}")
            elif graph_type == 'box':
                fig = px.box(df, x=x, y=y, title=f"Boxplot de {y} par {x}")
            elif graph_type == 'bar':
                fig = px.bar(df, x=x, y=y, title=f"Barres de {y} selon {x}")
            else:
                fig = px.scatter(title="Type de graphique inconnu")

            return fig, ""
        except Exception as e:
            return px.scatter(title="Erreur"), f"Erreur : {str(e)}"

    @app.callback(
        Output('correlation-matrix', 'figure'),
        Input('data-store', 'data')
    ) # fonction pour mettre à jour la matrice de corrélation
    def update_correlation_heatmap(data):
        if data:
            try:
                df = pd.read_json(io.StringIO(data), orient='split')
                numeric_df = df.select_dtypes(include=['float64', 'int64'])
                if numeric_df.empty:
                    return px.imshow([[0]], labels={'color': 'Corr'}, title="Aucune donnée numérique")
                corr = numeric_df.corr().round(2)
                fig = px.imshow(
                    corr,
                    text_auto=True,
                    color_continuous_scale='RdBu_r',
                    zmin=-1,
                    zmax=1,
                    title="Matrice de corrélation"
                )
                fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
                return fig
            except Exception as e:
                print(f"Erreur dans la heatmap : {e}")
        return px.imshow([[0]], labels={'color': 'Corr'}, title="Aucune donnée chargée")
