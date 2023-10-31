import streamlit as st
import requests
import pandas as pd
import plotly.express as px

def number_format(value, prefix=''):
    for unit in ['', 'thousands']:
        if value <1000:
            return f'{prefix} {value:.2f} {unit}'
        value /=1000
    return f'{prefix} {value:.2f} millions'

st.set_page_config(page_title='Streamlit Alura course', layout='wide')

st.title('Sales Dashboard :shopping_trolley:')


url = 'https://labdados.com/produtos'
REGION = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filters')
region = st.sidebar.selectbox('Region', REGION)

if region == 'Brasil':
    region = ''

all_years = st.sidebar.checkbox('Data from all years', value=True)

if all_years == True:
    year = ''
else:
    year = st.sidebar.slider('Select year', 2020, 2023)

query_string = {'regiao':region.lower(),'ano':year}
response = requests.get(url, params=query_string)
data = pd.DataFrame.from_dict(response.json())
data['Data da Compra'] = pd.to_datetime(data['Data da Compra'], format='%d/%m/%Y')

sellers_filter = st.sidebar.multiselect('Sellers', data['Vendedor'].unique())
if sellers_filter:
    data = data[data['Vendedor'].isin(sellers_filter)]

revenue = data['Preço'].sum()
qtd_sales = len(data)

## Revenue Tables
state_revenue = data.groupby(['Local da compra'])[['Preço']].sum().sort_values(by='Preço', ascending=False)
state_revenue = data.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(state_revenue, left_on = 'Local da compra', right_index = True)

monthly_revenue = data.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].agg(['sum', 'count']).reset_index()
monthly_revenue['Year'] = monthly_revenue['Data da Compra'].dt.year
monthly_revenue['Month'] = monthly_revenue['Data da Compra'].dt.month_name()

category_revenue = data.groupby(['Categoria do Produto'])[['Preço']].sum().sort_values(by='Preço', ascending=False)

## Number of sales Tables
state_qty = data.groupby(['Local da compra'])[['Preço']].count().sort_values(by='Preço', ascending=False).reset_index()

## Sellers Table
sellers = pd.DataFrame(data.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Plots
fig_revenue_map = px.scatter_geo(state_revenue, 
                                 lat='lat', 
                                 lon='lon',
                                 scope='south america',
                                 size='Preço',
                                 template='seaborn',
                                 hover_name='Local da compra',
                                 hover_data={'lat':False, 'lon':False})

fig_monthly_revenue = px.line(monthly_revenue,
                              x='Month',
                              y='sum',
                              markers=True,
                              range_y=[0, monthly_revenue.max()],
                              color='Year',
                              line_dash='Year',
                              title='Monthly Revenue')

fig_monthly_revenue.update_layout(yaxis_title='Revenue')

fig_state_revenue_bar = px.bar(state_revenue.head(),
                               x='Local da compra',
                               y='Preço',
                               text_auto=True,
                               title='Top 5 States (Revenue)')

fig_state_revenue_bar.update_layout(yaxis_title='Revenue')

fig_category_revenue_bar = px.bar(category_revenue,
                                  text_auto=True,
                                  title='Top 5 Categories (Revenue)')

fig_category_revenue_bar.update_layout(yaxis_title='Revenue')

## Sales Qty plot
fig_state_units_sold = px.bar(state_qty.sort_values(by='Preço', ascending=True).head(),
                              x='Preço',
                              y='Local da compra',
                              text_auto=True,
                              title='Top 5 States by Units sold')

fig_state_units_sold.update_layout(yaxis_title='State', xaxis_title='Units sold')

fig_monthly_units_sold = px.line(monthly_revenue,
                              x='Month',
                              y='count',
                              markers=True,
                              range_y=[0, monthly_revenue.max()],
                              color='Year',
                              line_dash='Year',
                              title='Monthly Units sold')

fig_monthly_units_sold.update_layout(yaxis_title='Units sold')


tab1, tab2, tab3 = st.tabs(['Revenue', 'Sales Qty', 'Sellers'])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Revenue', number_format(revenue, '$'), help='Sum of sales')
        st.plotly_chart(fig_revenue_map, use_container_width=True)
        st.plotly_chart(fig_state_revenue_bar, use_container_width=True)
    with col2:
        st.metric('QTD Sales', number_format(qtd_sales), help='Number of sales')
        st.plotly_chart(fig_monthly_revenue, use_container_width=True)
        st.plotly_chart(fig_category_revenue_bar, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Revenue', number_format(revenue, '$'), help='Sum of sales')
        st.plotly_chart(fig_state_units_sold, use_container_width=True)

    with col2:
        st.metric('QTD Sales', number_format(qtd_sales), help='Number of sales')
        st.plotly_chart(fig_monthly_units_sold, use_container_width=True)

with tab3:
    qty_sellers = st.number_input('Sellers quantity', 2, 10, 5)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Revenue', number_format(revenue, '$'), help='Sum of sales')
        fig_sellers_revenue = px.bar(sellers[['sum']].sort_values(by='sum', ascending=False).head(qty_sellers),
                                     x='sum',
                                     y=sellers[['sum']].sort_values(by='sum', ascending=False).head(qty_sellers).index,
                                     text_auto=True,
                                     title=f'Top {qty_sellers} Sellers by Revenue')
        st.plotly_chart(fig_sellers_revenue, use_container_width=True)

    with col2:
        st.metric('QTD Sales', number_format(qtd_sales), help='Number of sales')
        fig_sellers_qty_sales = px.bar(sellers[['count']].sort_values(by='count', ascending=False).head(qty_sellers),
                                     x='count',
                                     y=sellers[['count']].sort_values(by='count', ascending=False).head(qty_sellers).index,
                                     text_auto=True,
                                     title=f'Top {qty_sellers} Sellers by N° sales')
        st.plotly_chart(fig_sellers_qty_sales, use_container_width=True)



    st.dataframe(data)


