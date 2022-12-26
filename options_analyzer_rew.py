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

datetime_now = datetime.now()
datetime_now__vec = [datetime_now.year,datetime_now.month,datetime_now.day]
previous_date = datetime_now - timedelta(days = 60)
previous_date_vec = [previous_date.year,previous_date.month,previous_date.day]