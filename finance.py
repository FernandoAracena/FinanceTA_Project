import sys
import subprocess

# check if the library folder already exists, to avoid building everytime you load the pahe
if not os.path.isdir("/tmp/ta-lib"):

    # Download ta-lib to disk
    with open("/tmp/ta-lib-0.4.0-src.tar.gz", "wb") as file:
        response = requests.get(
            "http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz"
        )
        file.write(response.content)
    # get our current dir, to configure it back again. Just house keeping
    default_cwd = os.getcwd()
    os.chdir("/tmp")
    # untar
    os.system("tar -zxvf ta-lib-0.4.0-src.tar.gz")
    os.chdir("/tmp/ta-lib")
    os.system("ls -la /app/equity/")
    # build
    os.system("./configure --prefix=/home/appuser")
    os.system("make")
    # install
    os.system("make install")
    # back to the cwd
    os.chdir(default_cwd)
    sys.stdout.flush()

# add the library to our current environment
from ctypes import *

lib = CDLL("/home/appuser/lib/libta_lib.so.0.0.0")
# import library
try:
    import talib
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--global-option=build_ext", "--global-option=-L/home/appuser/lib/", "--global-option=-I/home/appuser/include/", "ta-lib"])
finally:
    import talib
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import datetime
from stockstats import wrap
import streamlit as st
import investpy
import talib

st.header("My Finance Recommendations App")
# Convert datetime
# datetime.datetime.utcnow()-datetime.timedelta(days=252)


def convert_today():

    end = datetime.datetime.utcnow()
    today = end.strftime("%d/%m/%Y")
    return today


st.subheader(convert_today())

# Read Data
df = pd.read_csv('Euronext_Equities_2022-05-14.csv', encoding='unicode_escape', sep=";", index_col=0,
                 usecols=['Name', 'Symbol', 'Open', 'High', 'Low', 'Last', 'Volume'])
df = df[df['Open'].notna()]
# streamlit run c:/Users/Bruker/finance.py
# Show first 10 per Volume
df.sort_values(by='Volume', ascending=False, inplace=True)
df_volume = df.head(10)
st.subheader("Top 10 Norwegian Stocks per Volume")
st.write(df_volume)

# Show Stats
df = df.rename(columns={'Last': 'Close'})
stock = wrap(df)
stockdf = stock[['symbol',
                 'pdi',
                 'mdi',
                 'adx',
                 'close_21_sma',
                 'atr_14',
                 'close',
                 'high_6_sma',
                 'low_6_sma',
                 'volume',
                 'close_4_sma',
                 'close_9_sma',
                 'close_18_sma']]

stockdf = stockdf.assign(Buy=stockdf.close > stockdf.high_6_sma)
stockdf = stockdf.assign(Sell=stockdf.close < stockdf.low_6_sma)
stockdf = stockdf.assign(Strong=stockdf.close_21_sma < stockdf.close)

stockdf.head(10)

# Show Buy Stocks
compra = stockdf[(stockdf['buy'] == True) & (
    stockdf['Strong'] == True) & (stockdf['adx'] > 20)]
df_buy = compra.drop(['close_21_sma',
                      'buy',
                      'sell',
                      'strong',
                      'pdi',
                      'mdi',
                      'adx',
                      'atr_14',
                      'high_6_sma',
                      'low_6_sma',
                      'close_4_sma',
                      'close_9_sma',
                      'close_18_sma'], axis=1)
st.subheader("Watching BUY Stocks per Volume")
st.write(df_buy)

# Input Stock
st.header("View stock graphs")
sequence_input = "eqnr"
stock_selected = st.text_input(
    "Input a norwegian stock symbol", sequence_input)

#"Input a norwegian stock symbol"

st.subheader(convert_today())
search_results = investpy.search_quotes(text=f"{stock_selected}", products=['stocks', 'bonds'],
                                        countries=['norway'])
data = search_results[0].retrieve_historical_data(
    from_date='01/01/2002', to_date=convert_today())

# Show Stats
technical_indicators = search_results[0].retrieve_technical_indicators(
    interval="daily")
st.subheader(f"Statistics ***{stock_selected}***")
st.write(technical_indicators)

###GRAPHS###GRAPHS###GRAPHS###

# Close Price
st.subheader(f"Close Price ***{stock_selected}***")
data['EMA200'] = talib.EMA(data['Close'], timeperiod=200)
data['WMA50'] = talib.WMA(data['Close'], timeperiod=50)
st.line_chart(data[-252:][['Close', 'EMA200', 'WMA50']])

# Volume
st.subheader(f"Volume ***{stock_selected}***")
data['SMA20'] = talib.SMA(data['Close'], timeperiod=20)
st.bar_chart(data[-252:].Volume)

# Trading Systems

# Dinamic Channel
st.subheader(f"Dinamic Channel ***{stock_selected}***")
data['EMAH'] = talib.EMA(data['High'], timeperiod=6)
data['EMAL'] = talib.EMA(data['Low'], timeperiod=6)
st.line_chart(data[-65:][['EMAH', 'EMAL', 'Close']])

# Triple Medias Sistem
st.subheader(f"Triple Medias Sistem ***{stock_selected}***")
data['EMA4'] = talib.EMA(data['Close'], timeperiod=4)
data['EMA9'] = talib.EMA(data['Close'], timeperiod=9)
data['EMA18'] = talib.EMA(data['Close'], timeperiod=18)
st.line_chart(data[-65:][['EMA4', 'EMA9', 'EMA18']])
