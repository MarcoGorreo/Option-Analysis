import yfinance as yf
import pandas as pd
import datetime
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Impostazioni 

ticker_name = "TSLA"
zoom_grafico = 15

# Date

datetime_now = datetime.now()
datetime_now_year = datetime_now.year
datetime_now_month = datetime_now.month
datetime_now_day = datetime_now.day

previous_date = datetime_now - timedelta(days = 60)
previous_date_year = previous_date.year
previous_date_month = previous_date.month
previous_date_day = previous_date.day

end_date = str((str(datetime_now_year) + "-" + str(datetime_now_month) + "-" + str(datetime_now_day)))
start_date = str((str(previous_date_year) + "-" + str(previous_date_month) + "-" + str(previous_date_day)))

# Dati

expirations = yf.Ticker(ticker_name).options
price_history = yf.Ticker(ticker_name).history(start=start_date, end=end_date)

# Variabili

k = 0
i = 0 
calls = 0
puts = 1
counter = 0
open_interest_for_strike = 0

# Vettori Vuoti

call_contracts = []
call_strikes = []
call_premiums = []
call_open_interests = []
put_contracts = []
put_strikes = []
put_premiums = []
put_open_interests = []
total_strike_prices = []
total_strike_prices_2 = []
strikes_array = []
liquidity_array = []

# Script

# Raccolgo le informazioni delle opzioni di ogni scadenza, dividendole per call e per put e le inserisco in array diversi

for expiration in expirations:
    option_chain = yf.Ticker(ticker_name).option_chain(expiration)
    call_options = option_chain[calls]
    put_options = option_chain[puts]

    k = 0
    i = 0

    while k in range(len(call_options)):
        call_contracts.append(call_options['contractSymbol'][k])
        call_strikes.append(call_options['strike'][k])
        call_premiums.append(call_options['lastPrice'][k])
        call_open_interests.append(call_options['openInterest'][k])
        k = k + 1 
    while i in range(len(put_options)):
        put_contracts.append(put_options['contractSymbol'][i])
        put_strikes.append(put_options['strike'][i])
        put_premiums.append(put_options['lastPrice'][i])
        put_open_interests.append(put_options['openInterest'][i])
        i = i + 1 

# Unisco i dati creando due dataframe separati per le Call e le Put

list_tuples = list(zip(call_contracts,call_strikes,call_premiums,call_open_interests))
df_calls = pd.DataFrame(list_tuples,columns=['Contract Name', 'Strike Price',"Premium", "Open Interest"])
list_tuples = list(zip(put_contracts,put_strikes,put_premiums,put_open_interests))
df_puts = pd.DataFrame(list_tuples,columns=['Contract Name', 'Strike Price',"Premium", "Open Interest"])

# Filtro il dataframe per eliminare i duplicati
# in modo da ottenere esclusivamente gli strike price esistenti

call_strike_prices = df_calls['Strike Price'].unique()
put_strike_prices = df_puts['Strike Price'].unique()

# Creo un dataframe per le call e per le put 

open_interest_puts = df_puts.groupby("Strike Price")['Open Interest'].sum().reset_index()
open_interest_calls = df_calls.groupby("Strike Price")['Open Interest'].sum().reset_index()

# Trovo tutti gli strike esistenti per le call e faccio l'append in un unico vettore

for strike_1 in put_strikes:
    total_strike_prices_2.append(strike_1)

for strike_2 in call_strikes:
    total_strike_prices_2.append(strike_2)

for i in total_strike_prices_2:
    if i not in total_strike_prices:
        total_strike_prices.append(i)

# Prendo l'OI per le put e le call ad ogni livello di prezzo e faccio la differenza

while counter in range(len(total_strike_prices)):
    liquidity = 0
    strike_price = int(total_strike_prices[counter])
    call_strike_index = open_interest_calls[open_interest_calls['Strike Price']==strike_price]
    put_strike_index = open_interest_puts[open_interest_puts['Strike Price']==strike_price]
    if not call_strike_index.empty and not put_strike_index.empty:
        liquidity = int(call_strike_index['Open Interest'].iloc[0] - put_strike_index['Open Interest'].iloc[0])
    elif not call_strike_index.empty and put_strike_index.empty:
        liquidity = int(call_strike_index['Open Interest'])
    elif call_strike_index.empty and not put_strike_index.empty:
        liquidity = int(0 - put_strike_index['Open Interest'])
    
    strikes_array.append(strike_price)
    liquidity_array.append(liquidity)

    counter = counter + 1

# Credo il dataframe finale da plottare

list_tuples = list(zip(strikes_array, liquidity_array))
final_dataframe = pd.DataFrame(list_tuples,columns=['Strike Price', 'Liquidity'])

# Elimino i valori nulli
final_dataframe.dropna(inplace=True) 

# Sorto il dataframe 

final_dataframe.sort_values(by='Strike Price',ascending=False,inplace=True)

new_df2 = final_dataframe['Liquidity']
new_df = final_dataframe['Strike Price']
new_liquidity = []
new_strike = []
for i in range(len(new_df2)):
    ref_liquidity = new_df2[i]
    ref_strike = new_df[i]
    if ref_liquidity > 10:
        while ref_liquidity > 0:
            ref_liquidity -= 10
            new_liquidity.append(ref_liquidity)
            new_strike.append(ref_strike)
    else:
        while ref_liquidity < 0:
            ref_liquidity += 10
            new_liquidity.append(ref_liquidity)
            new_strike.append(ref_strike)

new_list = list(zip(new_strike,new_liquidity))
new_df = pd.DataFrame(new_list,columns=['strike','liquidity'])

new_condition = (new_df['strike'].max()/100)*zoom_grafico
new_df_positive = new_df[(new_df['liquidity']>= 0) & (new_df['strike']<= new_condition)]
new_df_negative = new_df[(new_df['liquidity']<0) & (new_df['strike']<= new_condition)]
new_df_negative['liquidity'] = new_df_negative['liquidity'].abs()

# Plot 

x = [i for i in range(len(price_history))]
fig , ax = plt.subplots(figsize=(18,18))    
plt.plot(x,price_history['Close'],linewidth=2,color='b')
plt.axhline(y=price_history['Close'].iloc[len(price_history)-1], color='orange', linestyle='-',linewidth=1.5)
title = ticker_name + " Open Interest Analysis"
plt.title(title)
ax.twiny()
plt.scatter(new_df_positive['liquidity'],new_df_positive['strike'],s=1,color='g')
plt.scatter(new_df_negative['liquidity'],new_df_negative['strike'],s=1,color='r')
plt.show()