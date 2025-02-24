#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from datetime import datetime



# In[32]:

df=pd.read_csv('ejemplo.csv', index_col=0)
dff=df.copy()
dff['fac_fecha'] = pd.to_datetime(dff['fac_fecha']) 
dff.loc[:, 'fecha_sin_hora'] = dff['fac_fecha'].dt.date

df_fig1 = dff.groupby(['fac_fecha', 'Vendedor_Nombre'])['SubtotaliVA'].sum().reset_index()
df_fig1b = dff.groupby(['fac_fecha', 'Cluster'])['SubtotaliVA'].sum().reset_index()





# In[59]:


#Calcular tabla de recencia
recencia = dff.groupby('IDClteDireccion')['fac_fecha'].max().reset_index()
recencia['Recencia'] = recencia['fac_fecha'].apply(lambda x: (pd.Timestamp.now() - x).days)
#Calcular tabla de antiguedad
antiguedad = dff.groupby('IDClteDireccion')['fac_fecha'].min().reset_index()
antiguedad['Antiguedad'] = antiguedad['fac_fecha'].apply(lambda x: (pd.Timestamp.now() - x).days)
duracion = pd.merge(recencia, antiguedad, on='IDClteDireccion')
duracion['Duracion'] = duracion['Antiguedad'] - duracion['Recencia']
duracion = duracion[['IDClteDireccion', 'Recencia', 'Antiguedad','Duracion']]



import dash
from dash import dcc, html, Input, Output, State, Dash
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_table
import plotly.graph_objects as go

# Datos de ventas
ventas_hoy = 15264440
ventas_semana = 75240600
ventas_mes = 1288532498

# Definición de las tarjetas informativas
card_ventas_hoy = dbc.Card(
    dbc.CardBody([
        html.H5("Ventas de Hoy", className="card-title"),
        html.H3(f"UM$ {ventas_hoy:,.0f}".replace(",", "."), className="card-text")
    ]),
    className="text-center shadow-sm",
    style={"width": "100%"}
)

card_ventas_semana = dbc.Card(
    dbc.CardBody([
        html.H5("Ventas de la Semana", className="card-title"),
        html.H3(f"UM$ {ventas_semana:,.0f}".replace(",", "."), className="card-text")
    ]),
    className="text-center shadow-sm",
    style={"width": "100%"}
)

card_ventas_mes = dbc.Card(
    dbc.CardBody([
        html.H5("Ventas del Mes", className="card-title"),
        html.H3(f"UM$ {ventas_mes:,.0f}".replace(",", "."), className="card-text")
    ]),
    className="text-center shadow-sm",
    style={"width": "100%"}
)

app = Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server

fig_1 = {}
fig_2 = {}
fig_3 = {}
fig_4 = {}

app.layout = html.Div([
    html.Hr(),
    html.Div([
        html.H3("Análisis Comercial", style={'text-align': 'center', 'margin': '0'})
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),

    html.Hr(),

    # Fila para los botones y el date picker
    dbc.Row([
        dbc.Col(
            html.Div([
                dbc.Button("General", id="general-btn", n_clicks=0, style={'margin-right': '10px', 'margin-left':'20px'}),
                dbc.Button("Clientes", id="clientes-btn", n_clicks=0, style={'margin-right': '10px'}),
                dbc.Button("Productos", id="producto-btn", n_clicks=0),
            ], style={'text-align': 'left'}),
            width=12, md=6
        ),
        dbc.Col(
            html.Img(src='/assets/CAMBRA.png', 
            style={'height': '60px', 'margin-right': '40px'}),
            width=12, md=2
        ),
        dbc.Col(
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date='2023-01-01',
                end_date='2023-01-31',
                display_format='YYYY-MM-DD',
                month_format='MMMM YYYY',
                start_date_placeholder_text='Inicio',
                end_date_placeholder_text='Fin',
            ),
            width=12, md=4, style={'text-align': 'right'}
        ),
    ], style={'margin-top': '10px'}),

    html.Hr(),

    # Ajusta las columnas para pantallas pequeñas
    dbc.Row([
        dbc.Col(card_ventas_hoy, width=12, md=4),
        dbc.Col(card_ventas_semana, width=12, md=4),
        dbc.Col(card_ventas_mes, width=12, md=4)
    ], className="justify-content-center"),

    html.Hr(),

    # Fila de gráficos y cuadro de texto
    dbc.Row([
        dbc.Col(dcc.Graph(id='line-plot', figure=fig_1, responsive=True), width=12, md=4),
        dbc.Col(dcc.Graph(id='pie-plot', figure=fig_2, responsive=True), width=12, md=4),
        dbc.Col(dcc.Graph(id='segmento-plot', figure=fig_3, responsive=True), width=12, md=4)
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col(dcc.Graph(id='box-plot', figure=fig_4, responsive=True), width=12, md=4),
        # Fila para el DataTable
        dbc.Col(
            dash_table.DataTable(
                id='ventas-table',
                columns=[],
                style_table={'height': '300px', 'overflowY': 'auto'},
                style_cell={'textAlign': 'center'},
                data=[],  # Se actualizará vía callback
                filter_action='native',
                sort_action='native',
            ),
            width=12, md=8  # Asegúrate de asignar el ancho aquí para que ocupe todo el espacio disponible
        )
    ], style={'margin-top': '10px'})
])




@app.callback(
    [Output('line-plot', 'figure'),
     Output('pie-plot', 'figure'),
     Output('segmento-plot', 'figure'),
     Output('box-plot', 'figure'),
     Output('ventas-table', 'data'),
    Output('ventas-table', 'columns')],
    [Input("general-btn", 'n_clicks'),
     Input("clientes-btn", 'n_clicks'),
     Input("producto-btn", 'n_clicks'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_dashboard(general_clicks, clientes_clicks, producto_clicks, start_date, end_date):
    # Filtrar el dataframe según el rango de fechas
    dff_filtrado = dff[(dff['fac_fecha'] >= start_date) &
                       (dff['fac_fecha'] <= end_date)]
    dff_fig1 = df_fig1[(df_fig1['fac_fecha'] >= start_date) &
                       (df_fig1['fac_fecha'] <= end_date)]
    dff_fig1b = df_fig1b[(df_fig1b['fac_fecha'] >= start_date) &
                       (df_fig1b['fac_fecha'] <= end_date)]
    
    mix = dff_filtrado.groupby(['fac_fecha', 'Vendedor_Nombre'])['Producto_Linea'].nunique().reset_index()
    ventas_por_vendedor = dff_filtrado.groupby('Vendedor_Nombre')['SubtotaliVA'].sum().reset_index()
    dff_filtrado['fac_fecha'] = pd.to_datetime(dff_filtrado['fac_fecha']).dt.strftime('%d-%m-%Y')

    dff_categoria = dff_filtrado.groupby(['Producto_Categoria'], as_index=False)['SubtotaliVA'].sum()
    dff_grupo_familia = dff_filtrado.groupby(['Producto_Categoria', 'Producto_GrupoFamilia'], as_index=False)['SubtotaliVA'].sum()
    dff_linea = dff_filtrado.groupby(['Producto_Categoria', 'Producto_GrupoFamilia', 'Producto_Linea'], as_index=False)['SubtotaliVA'].sum()
     # Crear listas para el Sunburst
    labels = []
    parents = []
    values = []
    # Agregar Categorías (Nivel Superior)
    labels.extend(dff_categoria['Producto_Categoria'])
    parents.extend([''] * len(dff_categoria['Producto_Categoria']))  # Categoría no tiene padre
    values.extend(dff_categoria['SubtotaliVA'])

    # Agregar Grupos de Familia (Nivel Intermedio)
    labels.extend(dff_grupo_familia['Producto_GrupoFamilia'])
    parents.extend(dff_grupo_familia['Producto_Categoria'])  # Cada grupo familia pertenece a una categoría
    values.extend(dff_grupo_familia['SubtotaliVA'])

    # Agregar Líneas de Productos (Nivel Inferior)
    labels.extend(dff_linea['Producto_Linea'])
    parents.extend(dff_linea['Producto_GrupoFamilia'])  # Cada línea pertenece a un grupo familia
    values.extend(dff_linea['SubtotaliVA'])
#--------------------------------------------------------------------------------------------------------------------------------------
   
    dff_filtrado_grouped = dff_filtrado.groupby(['fac_fecha','Cluster'])['Producto_Linea'].nunique().reset_index()
    cluster_sales = dff_filtrado.groupby('Cluster')['SubtotaliVA'].sum().reset_index()
    cluster_sales_iva = dff_filtrado.groupby(['Cluster', 'Producto_Categoria'])['SubtotaliVA'].sum().reset_index()
#---------------------------------------------------------------------------------------------------------------------
    
    frecuencia = dff_filtrado.groupby('IDClteDireccion').size().reset_index(name='frecuencia')
    Monto_Comprado = dff_filtrado.groupby('IDClteDireccion')['SubtotaliVA'].sum().reset_index(name='monto_comprado')
    Kilos_Comprado = dff_filtrado.groupby('IDClteDireccion')['Kilos'].sum().reset_index(name='kilos_comprados')
    Productos_comprados = dff_filtrado.groupby('IDClteDireccion')['Producto_Linea'].nunique().reset_index(name='productos_distintos')
    Cantidad_Comprada = dff_filtrado.groupby('IDClteDireccion')['Qty'].sum().reset_index(name='cantidad_comprada')
    clientes = pd.merge(frecuencia, Monto_Comprado, on='IDClteDireccion')
    clientes = pd.merge(clientes, Kilos_Comprado, on='IDClteDireccion')
    clientes = pd.merge(clientes, Productos_comprados, on='IDClteDireccion')
    clientes = pd.merge(clientes, Cantidad_Comprada, on='IDClteDireccion')
    clientes = pd.merge(clientes, duracion, on = 'IDClteDireccion')
    #-----------------------------------------------------------------------------------------------------------------------------

    popularidad = dff_filtrado.groupby('Producto_Linea' )['IDClteDireccion'].nunique().reset_index(name='popularidad_absolutos')
    popularidad['popularidad']= popularidad['popularidad_absolutos'] / dff_filtrado['IDClteDireccion'].nunique() * 100 
    popularidad['popularidad']= popularidad['popularidad'].round(2)
    soporte = dff_filtrado.groupby('Producto_Linea' )['Id_Factura'].nunique().reset_index(name='soporte')
    participacion = dff_filtrado.groupby('Producto_Linea' )['SubtotaliVA'].sum().reset_index(name='monto')
    participacion['participacion']=participacion['monto'] / participacion['monto'].sum() * 100
    participacion['participacion'] = participacion['participacion'].round(2)
    cantidad = dff_filtrado.groupby('Producto_Linea' )['Qty'].sum().reset_index(name='cantidad')
    categoria = dff_filtrado.groupby('Producto_Linea')['Producto_Categoria'].first().reset_index(name='Producto_Categoria')
    productos = pd.merge(popularidad, soporte, on='Producto_Linea')
    productos = pd.merge(productos, participacion, on='Producto_Linea')
    productos = pd.merge(productos, cantidad, on='Producto_Linea')
    productos = pd.merge(productos, categoria, on='Producto_Linea')
    #-------------------------------------------------------------------------------------------------------------------------
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'general-btn'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Si el botón 'general-btn' fue presionado, hacemos las actualizaciones correspondientes
    if button_id == 'general-btn':

        # Gráfico de caja (Distribución de Montos de Venta por Día)
        fig_1 = go.Figure()
        fig_1.add_trace(go.Box(
            x=mix["Vendedor_Nombre"],  # Vendedores
            y=mix["Producto_Linea"],  # Número de productos distintos vendidos
            name="Distribución de Mix de Productos",  # Nombre de la traza
            hoverinfo="x",  # Mostrar solo el número de productos y el nombre de la traza
            #hovertemplate='<b>Vendedor: %{x}</b><br>Productos Vendidos: %{y}<extra></extra>',  # Mostrar información personalizada
        ))

        # Configurar el layout del gráfico
        fig_1.update_layout(
            title="Distribución de Mix de Productos", 
            xaxis_title="Vendedor", 
            yaxis_title="Mix Vendido",
            showlegend=False
            )

        # Eliminar las etiquetas de los ejes X si no se quieren ver
        fig_1.update_xaxes(showticklabels=False)

     



# Crear el gráfico Sunburst
        fig_2 = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total"
        ))

        # Configurar el layout
        fig_2.update_layout(
            title="Composicion de productos vendidos",
            sunburstcolorway=["#636EFA", "#EF553B", "#00CC96"]
        )


        # Configurar el layout
        fig_2.update_layout(
            title="Composición de productos vendidos",
            sunburstcolorway=["#636EFA", "#EF553B", "#00CC96", "#FFA15A", "#AB63FA"]
        )



        fig_3 = px.bar(
            ventas_por_vendedor, 
            x='Vendedor_Nombre', 
            y='SubtotaliVA',
            title='Ventas Totales por Vendedor',
            labels={'Vendedor_Nombre': 'Vendedor', 'SubtotaliVA': 'Monto Vendido'}
        )
        fig_3.update_xaxes(showticklabels=False)


        # Crear figura
        fig_4 = go.Figure()

        # Agregar la venta total
        total_data = dff_fig1.groupby('fac_fecha')['SubtotaliVA'].sum().reset_index()
        fig_4.add_trace(go.Scatter(
            x=total_data['fac_fecha'],
            y=total_data['SubtotaliVA'],
            mode='lines',
            name='Total',
            line=dict(width=3, color='black')  # Línea más gruesa y negra para diferenciarla
        ))

        # Agregar cada cluster con visibilidad oculta por defecto
        for vendedor in dff_fig1['Vendedor_Nombre'].unique():
            cluster_data = dff_fig1[dff_fig1['Vendedor_Nombre'] == vendedor]
            fig_4.add_trace(go.Scatter(
                x=cluster_data['fac_fecha'],
                y=cluster_data['SubtotaliVA'],
                mode='lines',
                name=str(vendedor),
                visible="legendonly"  # Hace que los clusters estén ocultos al inicio
            ))

        # Configuración del gráfico
        fig_4.update_layout(
            title="Evolucion de Monto Vendido",
            xaxis_title='Fecha',
            yaxis_title='Monto Vendido'
        )


    
        # Para la tabla se usan los datos filtrados
        data_table = dff_filtrado.to_dict('records')
        columns=[
                    {'name': 'Factura ID', 'id': 'Id_Factura'},
                    {'name': 'Cliente', 'id': 'IDClteDireccion'},
                    {'name': 'Fecha de Factura', 'id': 'fac_fecha'},
                    {'name': 'Monto', 'id': 'SubtotaliVA'},
                    {'name': 'Vendedor', 'id': 'Vendedor_Nombre'}
                ]

        # Retornar los outputs en el orden definido, incluyendo la vista previa de datos filtrados
        return fig_1, fig_2, fig_3, fig_4, data_table, columns
    
#-----------------------------------------------------------------------------------------------------------------------------------
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    elif button_id == "clientes-btn":


        fig_1 = px.bar(cluster_sales_iva, 
        y='SubtotaliVA',                # Monto comprado por cada cluster
        x='Cluster',                    # Nombre del cluster
        orientation='v', 
        color='Producto_Categoria',          
        title="Monto Comprado por Cluster",
        labels={'SubtotaliVA': 'Monto Comprado', 'Cluster': 'Cluster'})
        


        # Crear el gráfico de pastel
        fig_2 = px.pie(cluster_sales, 
                    names='Cluster',                # Nombre del cluster
                    values='SubtotaliVA',              # Monto vendido por cluster
                    title="Participación Ventas por Cluster")




        # Crear el gráfico de violín
        fig_3 = px.violin(dff_filtrado_grouped, 
                        y='Producto_Linea',  # Cantidad promedio de productos distintos vendidos
                        x='Cluster',             # Segmento (Cluster)
                        box=True,                # Incluir caja en el gráfico de violín
                        points="all",            # Mostrar todos los puntos de datos
                        title="Distribución de Mix de Productos por Cluster", 
                        labels={"Promedio_Productos": "Cantidad de Productos Distintos Vendidos", 
                                "Cluster": "Cluster"})


        # Crear figura
        fig_4 = go.Figure()

        # Agregar la venta total
        total_datab = dff_fig1b.groupby('fac_fecha')['SubtotaliVA'].sum().reset_index()
        fig_4.add_trace(go.Scatter(
            x=total_datab['fac_fecha'],
            y=total_datab['SubtotaliVA'],
            mode='lines',
            name='Total',
            line=dict(width=3, color='black')  # Línea más gruesa y negra para diferenciarla
        ))

        # Agregar cada cluster con visibilidad oculta por defecto
        for cluster in dff_fig1b['Cluster'].unique():
            cluster_data = dff_fig1b[dff_fig1b['Cluster'] == cluster]
            fig_4.add_trace(go.Scatter(
                x=cluster_data['fac_fecha'],
                y=cluster_data['SubtotaliVA'],
                mode='lines',
                name=str(cluster),
                visible="legendonly"  # Hace que los clusters estén ocultos al inicio
            ))

        # Configuración del gráfico
        fig_4.update_layout(
            title="Evolucion de Monto Vendido",
            xaxis_title='Fecha',
            yaxis_title='Monto Vendido'
        )

# Mostrar el gráfico

    
        # Para la tabla se usan los datos filtrados
        data_table = clientes.to_dict('records')
        columns=[
            {'name': 'Cliente', 'id': 'IDClteDireccion'},
            {'name': 'Duracion', 'id': 'Duracion'},
            {'name': 'Recencia', 'id': 'Recencia'},
            {'name': 'Frecuencia', 'id': 'frecuencia'},
            {'name': 'Monto', 'id': 'monto_comprado'},
            {'name': 'Kilos', 'id': 'kilos_comprados'},
            {'name': 'Mix', 'id': 'productos_distintos'},
            {'name': 'Cantidad', 'id': 'cantidad_comprada'}
        ]


        # Retornar los outputs en el orden definido, incluyendo la vista previa de datos filtrados
        return fig_1, fig_2, fig_3, fig_4, data_table, columns
    

#------------------------------------------------------------------------------------------------------------------------------------------
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    
    elif button_id == "producto-btn":

        productos_head = productos.sort_values(by='popularidad', ascending=False).head(10)
        fig_1 = px.bar(productos_head, 
        y='popularidad',                # Monto comprado por cada cluster
        x='Producto_Linea',                  
        orientation='v', 
        title="Popularidad de Producto",
        labels={'Popularidad': 'Popularidad', 'Producto_Linea': 'Producto_Linea'})
        

# Crear el gráfico Sunburst
        fig_2 = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total"
        ))

        # Configurar el layout
        fig_2.update_layout(
            title="Composicion de productos vendidos",
            sunburstcolorway=["#636EFA", "#EF553B", "#00CC96"]
        )


        # Configurar el layout
        fig_2.update_layout(
            title="Composición de productos vendidos",
            sunburstcolorway=["#636EFA", "#EF553B", "#00CC96", "#FFA15A", "#AB63FA"]
        )

        fig_3 = px.bar(productos, 
        y='monto',                # Monto comprado por cada cluster
        x='Producto_Categoria',                  
        orientation='v', 
        title="Ventas de Categoria Producto",
        labels={'Monto': 'monto', 'Producto_Categoria': 'Producto_Categoria'})


        fig_4 = go.Figure()

        # Agregar trazas para cada categoría de producto
        for categoria in productos["Producto_Categoria"].unique():
            df_cat = productos[productos["Producto_Categoria"] == categoria]
            
            fig_4.add_trace(go.Scatter(
                x=df_cat["soporte"],  # Frecuencia
                y=df_cat["cantidad"],  # Cantidad
                mode="markers",
                marker=dict(
                    size=df_cat["monto"] / df_cat["monto"].max() * 60,  # Escalar el tamaño
                    sizemode="diameter",
                    opacity=0.6,
                ),
                name=categoria,
                text=df_cat["Producto_Linea"],  # Tooltip con nombre del producto
                hoverinfo="text+x+y"
            ))

        # Configurar diseño
        fig_4.update_layout(
            title="Descripcion de Productos",
            xaxis=dict(title="Frecuencia"),
            yaxis=dict(title="Cantidad"),
            showlegend=True
        )
        





# Mostrar el gráfico

    
        # Para la tabla se usan los datos filtrados
        data_table = productos.to_dict('records')
        columns=[
            {'name': 'Producto', 'id': 'Producto_Linea'},
            {'name': 'Popularidad', 'id': 'popularidad'},
            {'name': 'Frecuencia', 'id': 'soporte'},
            {'name': 'Monto', 'id': 'monto'},
            {'name': 'Participacion', 'id': 'participacion'},
            {'name': 'Kilos', 'id': 'kilos'},
            {'name': 'Cantidad', 'id': 'cantidad'}
        ]

        # Retornar los outputs en el orden definido, incluyendo la vista previa de datos filtrados
        return fig_1, fig_2, fig_3, fig_4, data_table, columns

if __name__ == '__main__':
    app.run_server()




