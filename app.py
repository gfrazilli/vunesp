import dash
from dash import html, dcc
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
 
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

app = dash.Dash(
    external_stylesheets=[dbc.themes.FLATLY]) 
server = app.server #instanciando o servidor

df_data = pd.read_csv("vendas.csv", sep=";", decimal =',')
df_data["DATA"] = pd.to_datetime(df_data["DATA"])


# =========  Layout  =========== #
app.layout = html.Div(children=[
    html.H5("Vendedores:", className="test"), #o className vai pegar a estilização especifica do css
    dcc.Checklist(df_data['VENDEDOR'].value_counts().index, #para criar um checklist contei os vendedor, criou uma series e o index da serie é o nome de cada um
                  df_data['VENDEDOR'].value_counts().index, #mostrando quais do checklist estarão marcados, no caso todos
                  id = "check_vendedor"), #id desse checklist para outras partes do código mexerem nele
    
    html.H5("Variaveis de análise:"),
    dcc.RadioItems(["TOTAL", "COMISSAOCOBRADA"], #quais os itens do radiobuton
                    "TOTAL", #qual item do radio vem selecionado por padrão
                    id="main_variable"),
    
    dcc.Graph(id="soma_fig"), #criando componentes de gráfico para colocar algo dentro deles depois
    dcc.Graph(id="cidade_fig"),
    dcc.Graph(id="cond_pag_fig"),
])


# ======== Callbacks ========== #
  #a primeira lista do callback é o output, o segundo o input e o terceiro(opcional) é o state
  # #ou seja, sempre que tiver uma mudança nos inputs pelo usuário, acontecerão mudanças no outpu
@app.callback([
        Output('soma_fig', 'figure'), #o id do elemento que vou fazer o output é o soma_fig, e o elemento(parâmetro do Graph) é o "figure"
        Output('cidade_fig', 'figure'),
        Output('cond_pag_fig', 'figure'),
    ],
    [
        Input('check_vendedor', 'value'), #o input é o id do checklist, segundo parametro 'value' vai acionar quando alterarem o valor do checklist
        Input('main_variable', 'value')
    ])
def frazilli_dash(check_vendedor, main_variable): #essa é a função principal que vai trabalhar com os inputs e outputs acima
    
    ######## PRIMEIRO GRAFICO ###############
    df_filtered = df_data[df_data["VENDEDOR"].isin(check_vendedor)] #criei um dataframe apenas com os vendedores que estão no checklist
    
    operation = np.sum
    df_vendedores = df_filtered.groupby("VENDEDOR")[main_variable].apply(operation).to_frame().reset_index() 
    #até o apply operation eu agrupei por vendedores e apliquei a operation(soma) na main_variable(valor venda ou comissão). 
    # Ou seja, soma de cada vendedor. Mas ele é uma series. Então coloco to_frame para transformar num df pq não da para fazergrafico com series
    # Fazendo acima, nome do vendeodr é index e o plotly não faz gráfico com indice, então damos reset_index para criar os indices

    fig_soma = px.bar(df_vendedores, x='VENDEDOR', y = main_variable)
    ########## FIM DO PRIMEIRO GRAFICO
    ########## SEGUNDO GRAFICO ############
    df_cidades = df_filtered.groupby("CIDADE")[main_variable].apply(operation).to_frame().reset_index() 
    fig_cidades = px.bar(df_cidades, x='CIDADE', y=main_variable)

    ########## FIM DO SEGUNDO GRAFICO
    ########## TERCEIRO GRAFICO ############
    #esse terceiro vai ser mais incrementado, também vou dividir por ano#
    df_cond = df_filtered.groupby(["COND", "ANO"])[main_variable].apply(operation).to_frame().reset_index() 
    fig_cond = px.bar(df_cond, x = main_variable, y='COND', color = "ANO", orientation='h', barmode="group")
    
    ########## FIM DO TERCEIRO GRAFICO   
    
    return fig_soma, fig_cidades ,fig_cond

# Run server
if __name__ == '__main__':
    app.run_server(debug=True)
