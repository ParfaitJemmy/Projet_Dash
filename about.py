from dash import html
import dash_bootstrap_components as dbc

def layout():
    return dbc.Container([
        html.H2("A propos"),
        html.P("Application d'analyse factorielle discriminante avec Dash et Python.", className="text-center"),
        html.P("Chargez des données, explorez des statistiques, effectuez une FDA et visualisez les résultats. Réalisé par Parfait Jemmy Prodige NGOYI, Analyste statisticien (AS)", className="text-center text-info")
    ])