import streamlit as st
import pandas as pd
import altair as alt
import yfinance as yf


st.title('米国株価可視化アプリ')

st.sidebar.write('''
# GAFA株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
## 表示日数選択
''')

days = st.sidebar.slider('日数', 1, 50, 20)

st.write(f'''
### 過去 **{days}日間** のGAFAの株価
''')

@st.cache_data
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try: 
    st.sidebar.write('## 株価の範囲指定')

    min_stock_range, max_stock_range = st.sidebar.slider('範囲を指定してください。', 0.0, 1000.0, (0.00, 1000.0))

    tickers = {'google':'GOOG',
                'amazon':'AMZN',
                'facebook':'META',
                'apple':'AAPL',
                'microsoft':'MSFT',
                'Netflix':'NFLX'}

    df = get_data(days, tickers)

    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['google', 'apple']
    )

    if not companies:
        st.error('少なくとも一社は選んでください。')
    else:
        data = df.loc[companies]
        st.write("### 株価（USD", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[min_stock_range, max_stock_range])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error('Oops! Try Again')

