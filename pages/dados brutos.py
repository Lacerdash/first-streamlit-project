import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title='Dataset', layout='wide')
@st.cache_data

def convert_csv(df):
    return df.to_csv(index=False, encoding='utf-8')

def succes_message():
    succes = st.success('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(5)
    succes.empty()
    return 

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

response = requests.get(url)
data = pd.DataFrame.from_dict(response.json())
data['Data da Compra'] = pd.to_datetime(data['Data da Compra'], format = '%d/%m/%Y')


with st.expander('Columns filter'):
    columns = st.multiselect('Select columns', list(data.columns), list(data.columns))

st.sidebar.title('Filters')
with st.sidebar.expander('Product Name'):
    products = st.multiselect('Select products', data['Produto'].unique(), data['Produto'].unique())
with st.sidebar.expander('Product Category'):
    categories= st.multiselect('Select categories', data['Categoria do Produto'].unique(), data['Categoria do Produto'].unique())
with st.sidebar.expander('Price'):
    price = st.slider('Select price', 0, 5000, (0,5000))
with st.sidebar.expander('Freight'):
    freight = st.slider('Feight', 0,250, (0,250))
with st.sidebar.expander('Date of purchase'):
    purchase_date = st.date_input('Select date', (data['Data da Compra'].min(), data['Data da Compra'].max()))
with st.sidebar.expander('Seller'):
    sellers = st.multiselect('Select sellers', data['Vendedor'].unique(), data['Vendedor'].unique())
with st.sidebar.expander('Purchase state'):
    purchase_state = st.multiselect('Select purchase state', data['Local da compra'].unique(), data['Local da compra'].unique())
with st.sidebar.expander('Purchase evaluation'):
    evaluation = st.slider('Selec purchase evaluation',1,5, value = (1,5))
with st.sidebar.expander('Payment Type'):
    payment_type = st.multiselect('Select payment type', data['Tipo de pagamento'].unique(), data['Tipo de pagamento'].unique())
with st.sidebar.expander('Installments quantity'):
    qty_installments = st.slider('Select installments quantity', 1, 24, (1,24))


query = '''
Produto in @products and \
`Categoria do Produto` in @categories and \
@price[0] <= Preço <= @price[1] and \
@freight[0] <= Frete <= @freight[1] and \
@purchase_date[0] <= `Data da Compra` <= @purchase_date[1] and \
Vendedor in @sellers and \
`Local da compra` in @purchase_state and \
@evaluation[0]<= `Avaliação da compra` <= @evaluation[1] and \
`Tipo de pagamento` in @payment_type and \
@qty_installments[0] <= `Quantidade de parcelas` <= @qty_installments[1]
'''

filtered_data = data.query(query)
filtered_data = data[columns]

st.dataframe(filtered_data)

st.markdown(f'The table has :blue[{filtered_data.shape[0]}] rows and :blue[{filtered_data.shape[1]}] columns')

st.markdown('Escreva um nome para o arquivo')

col1, col2 = st.columns(2)
with col1:
    file_name = st.text_input('', label_visibility='collapsed', value='data')
    file_name += '.csv'
with col2:
     st.download_button('Fazer o download da tabela em csv', data = convert_csv(filtered_data), file_name = file_name, mime = 'text/csv', on_click = succes_message) 