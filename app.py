import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import io
import csv
import plotly.express as px

from pages import home, upload, descriptive_stats, fda, visualisation, about

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/styles.css'],
    suppress_callback_exceptions=True
)
server = app.server

# --------------------- App Layout -----------------------
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='data-store', storage_type='session'),
    html.Div(id='page-content'),
    dbc.Nav([
        dbc.NavLink("Accueil", href="/", active="exact"),
        dbc.NavLink("Charger les données", href="/upload", active="exact"),
        dbc.NavLink("Statistiques Descriptives", href="/descriptive-stats", active="exact"),
        dbc.NavLink("Analyse FDA", href="/fda", active="exact"),
        dbc.NavLink("Visualisation", href="/visualisation", active="exact"),
        dbc.NavLink("À propos", href="/about", active="exact"),
    ], pills=True, className="mb-4")
])

# ------------------ Navigation --------------------------
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/upload':
        return upload.layout()
    elif pathname == '/descriptive-stats':
        return descriptive_stats.layout()
    elif pathname == '/fda':
        return fda.layout()
    elif pathname == '/visualisation':
        return visualisation.layout()
    elif pathname == '/about':
        return about.layout()
    else:
        return home.layout()

# ------------------ Upload & Save -----------------------
@app.callback(
    [
        Output('data-preview', 'children'),
        Output('file-upload-error', 'children'),
        Output('data-store', 'data'),
        Output('delimiter-display', 'children')
    ],
    [
        Input('upload-data', 'contents'),
        Input('delimiter-dropdown', 'value')
    ],
    [
        State('upload-data', 'filename')
    ]
)
def update_data_preview(contents, delimiter, filename):
    if contents and filename and filename.lower().endswith('.csv'):
        try:
            content_type, content_string = contents.split(',', 1)
            decoded = base64.b64decode(content_string)
            text = decoded.decode('utf-8')

            # Détection automatique
            if not delimiter:
                try:
                    sniffer = csv.Sniffer()
                    detected_delimiter = sniffer.sniff(text).delimiter
                except:
                    detected_delimiter = ';'
            else:
                detected_delimiter = delimiter

            try:
                df = pd.read_csv(io.StringIO(text), delimiter=detected_delimiter)
            except:
                text = decoded.decode('latin-1')
                df = pd.read_csv(io.StringIO(text), delimiter=detected_delimiter)

            preview = html.Div([
                html.H5(f"Aperçu des données : {filename}", className="mt-3"),
                upload.create_data_table(df)
            ])
            delimiter_text = f"Délimiteur utilisé : {detected_delimiter}"
            return preview, "", df.to_json(date_format='iso', orient='split'), delimiter_text
        except Exception as e:
            return "", f"Erreur lors du chargement : {str(e)}", None, ""
    return "", "Veuillez charger un fichier CSV valide", None, ""

# ------------------ Statistiques Descriptives ----------
@app.callback(
    Output('descriptive-stats-results', 'children'),
    Input('url', 'pathname'),
    State('data-store', 'data')
)
def display_stats(pathname, data):
    if pathname == '/descriptive-stats':
        if data:
            try:
                df = pd.read_json(io.StringIO(data), orient='split')
                return descriptive_stats.create_stats_table(df)
            except Exception as e:
                return html.P(f"Erreur lors du calcul des statistiques : {str(e)}", className="text-danger")
        return html.P("Aucune donnée disponible. Veuillez charger un fichier CSV sur la page 'Charger les données'.", className="text-info")
    return html.P("")

# ------------------ Register Page-specific Callbacks ---
fda.register_callbacks(app)
visualisation.register_callbacks(app)

# ------------------ Run App -----------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
