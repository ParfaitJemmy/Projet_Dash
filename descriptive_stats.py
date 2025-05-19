from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output, State
import io
# fonction pour afficher les statistiques descriptives des données
def layout():
    return dbc.Container([
        html.H2("Statistiques Descriptives"),
        html.P("Affichez les statistiques descriptives des données chargées.", className="text-info"),
        dcc.Loading(html.Div(id='descriptive-stats-results', className="mt-4"))
    ])

def create_stats_table(df):
    boolean_cols = [col for col in df.columns if (df[col].dtype == 'bool') or 
                    (set(str(val).lower() for val in df[col].dropna().unique()).issubset(
                        {'0', '1', 'true', 'false', 'yes', 'no', 'y', 'n', 't', 'f'}))]
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    if numeric_df.empty:
        return html.P("Aucune colonne numérique pour les statistiques.", className="text-warning")
    stats = numeric_df.describe().transpose().reset_index()
    columns = [
        {'name': col, 'id': col, 'type': 'numeric' if stats[col].dtype in ['float64', 'int64'] else 'text'}
        for col in stats.columns
    ]
    style_data_conditional = [
        {
            'if': {'column_type': 'numeric'},
            'format': {'specifier': '.2f'}
        },
        *[
            {
                'if': {'column_id': col},
                'className': 'boolean'
            } for col in boolean_cols if col in stats.columns
        ]
    ]
    return dash_table.DataTable(
        data=stats.to_dict('records'),
        columns=columns,
        page_size=10,
        style_data_conditional=style_data_conditional
    )
# Fonction pour créer un tableau de données
def register_callbacks(app):
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
                    return create_stats_table(df)
                except Exception as e:
                    return html.P(f"Erreur lors du calcul des statistiques : {str(e)}", className="text-danger")
            return html.P("Aucune donnée disponible. Veuillez charger un fichier CSV sur la page 'Charger les données'.", className="text-info")
        return html.P("")

