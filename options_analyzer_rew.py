import yfinance as yf
import pandas as pd
import datetime
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Impostazioni 

ticker_name = "TSLA"
zoom_grafico = 15

#data 

class oper:
    def __init__(self,datetime,time_delta):
        self.datetime = datetime 
        self.time_delta = time_delta
        self.previous_date = datetime - time_delta
    def now__vec(self):
        return [str(self.datetime.year),str(self.datetime.month),str(self.datetime.day)]
    def previous_vec(self):
        return [str(self.previous_date.year),str(self.previous_date.month),str(self.previous_date.day)]

#previous_date = datetime_now - timedelta(days = 60)
prova1 = oper(datetime.now(),timedelta(days = 60))

end_date,start_date = '-'.join(prova1.now__vec()),'-'.join(prova1.previous_vec())

# Dati

expirations = yf.Ticker(ticker_name).options
price_history = yf.Ticker(ticker_name).history(start=start_date, end=end_date)

# Vettori Vuoti

call_contracts, call_strikes, call_premiums, call_open_interests, put_contracts, put_strikes, put_premiums, put_open_interests, strikes_array, liquidity_array, total_strike_prices= [],[],[],[],[],[],[],[],[],[],[]

# Raccolgo le informazioni delle opzioni di ogni scadenza, dividendole per call e per put e le inserisco in array diversi

for expiration in expirations:
    option_chain = yf.Ticker(ticker_name).option_chain(expiration)
    call_options = option_chain[0]
    put_options = option_chain[1]

    for k in range(len(call_options)):call_contracts.append(call_options['contractSymbol'][k]),call_strikes.append(call_options['strike'][k]),call_premiums.append(call_options['lastPrice'][k]),call_open_interests.append(call_options['openInterest'][k])
    for i in range(len(put_options)):put_contracts.append(put_options['contractSymbol'][i]),put_strikes.append(put_options['strike'][i]),put_premiums.append(put_options['lastPrice'][i]),put_open_interests.append(put_options['openInterest'][i])

# Unisco i dati creando due dataframe separati per le Call e le Put

df_calls = pd.DataFrame(list(zip(call_contracts,call_strikes,call_premiums,call_open_interests)),columns=['Contract Name', 'Strike Price',"Premium", "Open Interest"])
df_puts = pd.DataFrame(list(zip(put_contracts,put_strikes,put_premiums,put_open_interests)),columns=['Contract Name', 'Strike Price',"Premium", "Open Interest"])

# Filtro il dataframe per eliminare i duplicati
# in modo da ottenere esclusivamente gli strike price esistenti

call_strike_prices = df_calls['Strike Price'].unique()
put_strike_prices = df_puts['Strike Price'].unique()

# Creo un dataframe per le call e per le put 

open_interest_puts = df_puts.groupby("Strike Price")['Open Interest'].sum().reset_index()
open_interest_calls = df_calls.groupby("Strike Price")['Open Interest'].sum().reset_index()

# Trovo tutti gli strike esistenti per le call e faccio l'append in un unico vettore

total_strike_prices_2 = put_strikes + call_strikes
for i in total_strike_prices_2:
    if i not in total_strike_prices: total_strike_prices.append(i)

# Prendo l'OI per le put e le call ad ogni livello di prezzo e faccio la differenza

for counter in range(len(total_strike_prices)):
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

# Credo il dataframe finale da plottare

final_dataframe = pd.DataFrame(list(zip(strikes_array, liquidity_array)),columns=['Strike Price', 'Liquidity'])

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

new_df = pd.DataFrame(list(zip(new_strike,new_liquidity)),columns=['strike','liquidity'])

new_df_positive = new_df[(new_df['liquidity']>= 0) & (new_df['strike']<= (new_df['strike'].max()/100)*zoom_grafico)]
new_df_negative = new_df[(new_df['liquidity']<0) & (new_df['strike']<= (new_df['strike'].max()/100)*zoom_grafico)]
new_df_negative['liquidity'] = new_df_negative['liquidity'].abs()

# Plot 

fig , ax = plt.subplots(figsize=(18,18))    
plt.plot([i for i in range(len(price_history))],price_history['Close'],linewidth=2,color='b')
plt.axhline(y=price_history['Close'].iloc[len(price_history)-1], color='orange', linestyle='-',linewidth=1.5)
title = ticker_name + " Open Interest Analysis"
plt.title(title)
ax.twiny()
plt.scatter(new_df_positive['liquidity'],new_df_positive['strike'],s=1,color='g')
plt.scatter(new_df_negative['liquidity'],new_df_negative['strike'],s=1,color='r')
plt.show()