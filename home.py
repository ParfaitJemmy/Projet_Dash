from dash import html, dcc
import dash_bootstrap_components as dbc
# fonction pour le style
def layout():
    return dbc.Container([
        html.H1("Analyse Factorielle Discriminante", className="text-center mt-4 mb-4"),
        html.P("Bienvenue sur la plateforme d'analyse factorielle discriminante.", className="text-center"),
        html.P("Commencez par charger un fichier CSV sur la page 'Charger les données'.", className="text-center text-info"),
        html.Div(className="text-center mt-4", children=[
            dcc.Link(dbc.Button("Charger les données", color="primary"), href="/upload", className="me-2"),
            dcc.Link(dbc.Button("Statistiques Descriptives", color="secondary"), href="/descriptive-stats", className="me-2"),
            dcc.Link(dbc.Button("Analyse FDA", color="info"), href="/fda", className="me-2"),
            dcc.Link(dbc.Button("Visualisation", color="dark"), href="/visualisation")
        ])
    ])
