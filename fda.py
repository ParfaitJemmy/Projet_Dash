from dash import html, dcc, Output, Input, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import io
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from scipy.stats import f_oneway
import numpy as np

# Stockage global du modèle et des variables explicatives
lda_model = None
fda_features = []

# Layout de la page
def layout():
    return dbc.Container([
        html.H2("Analyse Factorielle Discriminante", className="text-center mt-4"),
        html.P("Sélectionnez une variable cible (catégorielle) et des variables explicatives (numériques).", className="text-info"),

        html.Label("Variable cible (catégorielle) :"),
        dcc.Dropdown(id='fda-target-dropdown', placeholder="Sélectionnez une variable cible"),

        html.Label("Variables explicatives :"),
        dcc.Dropdown(id='fda-features-dropdown', multi=True, placeholder="Sélectionnez les variables explicatives"),

        html.Br(),
        dbc.Button("Lancer l'analyse FDA", id='run-fda', color='primary', disabled=True),

        html.Br(), html.Br(),
        dcc.Loading(dcc.Graph(id='fda-plot')),
        html.Div(id='fda-error', className='text-danger mt-2'),

        html.Hr(),
        html.H4("Corrélations et ANOVA"),
        html.Div(id='correlation-results', className='mb-4'),

        html.H4("Simulation et prédiction"),
        html.Div(id='prediction-form'),
        dbc.Button("Prédire", id='predict-btn', color='success', className='mt-2'),
        html.Div(id='prediction-output', className='mt-3'),
        dcc.Loading(dcc.Graph(id='prediction-graph'))
    ])

# Enregistrement des callbacks
def register_callbacks(app):
    @app.callback(
        [Output('fda-target-dropdown', 'options'),
         Output('fda-features-dropdown', 'options')],
        Input('data-store', 'data')
    )
    def update_dropdowns(data):
        if data:
            try:
                df = pd.read_json(io.StringIO(data), orient='split')
                df = df.dropna(axis=1, how='all')
                options = [{'label': col, 'value': col} for col in df.columns]
                return options, options
            except Exception as e:
                print(f"Erreur dans update_dropdowns : {e}")
        return [], []

    @app.callback(
        Output('run-fda', 'disabled'),
        [Input('fda-target-dropdown', 'value'),
         Input('fda-features-dropdown', 'value')]
    )
    def toggle_button(target, features):
        return not (target and features)

    @app.callback(
        [Output('fda-plot', 'figure'),
         Output('fda-error', 'children'),
         Output('prediction-form', 'children'),
         Output('correlation-results', 'children')],
        Input('run-fda', 'n_clicks'),
        State('fda-target-dropdown', 'value'),
        State('fda-features-dropdown', 'value'),
        State('data-store', 'data')
    )
    def run_fda(n, target, features, data):
        global lda_model, fda_features
        if not (n and data and target and features):
            return px.scatter(title="Sélectionnez une cible et des variables"), "Veuillez compléter les champs.", None, None
        try:
            df = pd.read_json(io.StringIO(data), orient='split')
            df = df.dropna(axis=1, how='all')

            if not pd.api.types.is_categorical_dtype(df[target]) and df[target].dtype != object:
                return px.scatter(title="Type invalide"), "🚫 La variable cible doit être qualitative (catégorielle).", None, None

            non_numeric = [col for col in features if not pd.api.types.is_numeric_dtype(df[col])]
            if non_numeric:
                return px.scatter(title="Variables non numériques"), f"🚫 Les variables explicatives suivantes ne sont pas numériques : {', '.join(non_numeric)}", None, None

            missing_info = ""
            for var in [target] + features:
                if var in df.columns:
                    pct = df[var].isnull().mean() * 100
                    if pct > 0:
                        missing_info += f"⚠️ {var} : {pct:.2f}% de valeurs manquantes\n"
            if missing_info:
                missing_info = "🚨 Données manquantes détectées :\n" + missing_info

            X = df[features]
            y = df[target]
            valid_index = X.dropna().index.intersection(y.dropna().index)
            X = X.loc[valid_index]
            y = y.loc[valid_index]

            if len(y.unique()) < 2:
                return px.scatter(title="Trop peu de classes"), "⚠️ La variable cible doit comporter au moins deux classes.", None, None

            lda_model = LDA(n_components=2)
            X_r = lda_model.fit_transform(X, y)
            fda_features = features

            fig = px.scatter(x=X_r[:, 0], y=X_r[:, 1], color=y.astype(str),
                             labels={'x': 'LD1', 'y': 'LD2'}, title="Projection FDA")

            form = html.Div([
                html.Div([
                    html.Label(var),
                    dcc.Input(id={'type': 'input-var', 'index': var}, type='number', debounce=True,
                              className='mb-2', style={'width': '100%'})
                ]) for var in features
            ])

            # Mesure de corrélation + ANOVA
            correlation_texts = []
            for feature in features:
                groups = [df[df[target] == cat][feature].dropna() for cat in df[target].unique()]
                if all(len(g) > 1 for g in groups):
                    f_stat, p_val = f_oneway(*groups)
                    correlation_texts.append(html.Div(f"{feature} : F = {f_stat:.3f}, p = {p_val:.4f}"))
                else:
                    correlation_texts.append(html.Div(f"{feature} : Pas assez de données pour ANOVA."))

            return fig, missing_info, form, correlation_texts
        except Exception as e:
            return px.scatter(title="Erreur AFD"), f"Erreur : {str(e)}", None, None

    @app.callback(
        [Output('prediction-output', 'children'),
         Output('prediction-graph', 'figure')],
        Input('predict-btn', 'n_clicks'),
        [State({'type': 'input-var', 'index': ALL}, 'value'),
         State('data-store', 'data'),
         State('fda-target-dropdown', 'value')]
    )
    def predict(n, values, data, target):
        global lda_model, fda_features
        if not n or not values or lda_model is None:
            return "Veuillez remplir tous les champs et exécuter la FDA d'abord.", px.scatter(title="Prédiction")
        try:
            df = pd.read_json(io.StringIO(data), orient='split')
            X = df[fda_features].select_dtypes(include='number').dropna()
            y = df[target].loc[X.index]

            new_point = pd.DataFrame([values], columns=fda_features)
            probs = lda_model.predict_proba(new_point)[0]
            classes = lda_model.classes_
            prediction = classes[np.argmax(probs)]

            text = f"✅ Prédiction : {prediction} \n\nProbabilités : " + ', '.join([f"{c} = {p:.2f}" for c, p in zip(classes, probs)])

            new_proj = lda_model.transform(new_point)
            X_proj = lda_model.transform(X)
            fig = px.scatter(x=X_proj[:, 0], y=X_proj[:, 1], color=y.astype(str),
                             labels={'x': 'LD1', 'y': 'LD2'})
            fig.add_scatter(x=new_proj[:, 0], y=new_proj[:, 1],
                            mode='markers', marker=dict(size=12, color='black'), name='Nouveau')

            return text, fig
        except Exception as e:
            return f"Erreur : {str(e)}", px.scatter(title="Erreur de projection")
