# ============================================Imports================================
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import dash

from app import *
 
import plotly.express as px
import plotly.graph_objects as go


#======================================Processamento dos Dados==============================
df_data = pd.read_csv("supermarket_sales.csv")
df_data["Date"] = pd.to_datetime(df_data["Date"])


# =========  Layout  =========== #
app.layout = html.Div(children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.H2("Sales Super Market", style={"font-family":"Voltaire"}),
                            html.Hr(),

                            html.H5("Cidades:"),
                            dcc.Checklist(df_data["City"].value_counts().index,
                            df_data["City"].value_counts().index, id="check_city",
                            inputStyle={"margin-right":"5px", "margin-left":"20px"}),

                            html.H5("Variável de análise:", style={"margin-top":"30px"}),
                            dcc.RadioItems(["gross income", "Rating"], "gross income", id="main_variable",
                            inputStyle={"margin-top":"5px", "margin-left": "20px", "margin-right":"5px"}),
  
                        ], style={"height":"90vh", "margin":"20px", "padding":"20px"}) 
                    ], sm=3),
                            
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([dcc.Graph(id="city_fig")], sm=4),
                            dbc.Col([dcc.Graph(id="gender_fig")], sm=4),
                            dbc.Col([dcc.Graph(id="pay_fig")], sm=4),
                        ]),
                        dbc.Row([dcc.Graph(id="income_per_date_fig")]),
                        dbc.Row([dcc.Graph(id="income_per_product_fig")]),

                    ], sm=9)
                ])
            ]
        )


# ======================================  Callbacks  ============================== #
@app.callback([
                Output("city_fig", "figure"),
                Output("gender_fig", "figure"),
                Output("pay_fig", "figure"),
                Output("income_per_date_fig", "figure"),
                Output("income_per_product_fig", "figure"),
            ], 
                [
                    Input("check_city", "value"),
                    Input("main_variable", "value"),
                ])
def render_page_content(cities, main_variable):
    operation = np.sum if main_variable == "gross income" else np.mean
    df_filtered = df_data[df_data["City"].isin(cities)]

    df_city = df_filtered.groupby("City")[main_variable].apply(operation).to_frame().reset_index()
    df_gender = df_filtered.groupby(["Gender", "City"])[main_variable].apply(operation).to_frame().reset_index()
    df_payment = df_filtered.groupby("Payment")[main_variable].apply(operation).to_frame().reset_index()
    
    df_income_time = df_filtered.groupby("Date")[[main_variable]].apply(operation).reset_index()
    df_product_income = df_filtered.groupby(["Product line", "City"])[[main_variable]].apply(operation).reset_index()

    fig_city = px.bar(df_city, x="City", y=main_variable)
    fig_gender = px.bar(df_gender, x="Gender", y=main_variable, color="City", barmode="group")
    fig_payment = px.bar(df_payment, y="Payment", x=main_variable, orientation="h", barmode="group")
    fig_product_income = px.bar(df_product_income, x=main_variable, y="Product line", color="City", orientation="h")
    fig_income_date = px.bar(df_income_time, y=main_variable, x="Date")
    
    for fig in [fig_city, fig_payment, fig_gender, fig_income_date]:
        fig.update_layout(margin=dict(l=0, r=20, t=20, b=20), height=200, template="minty")
    
    fig_product_income.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=500, barmode="group")
    
    return fig_city, fig_gender, fig_payment, fig_income_date, fig_product_income


#========================================Server=====================================
if __name__ == "__main__":
    app.run_server(port=8050, debug=True)