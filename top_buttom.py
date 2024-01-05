#This app requires some modules: 'flask', 'mplcyberpunk', 'matplotlib', 'yfinance'

from flask import Flask, request, render_template  
import mplcyberpunk
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import date, timedelta

def get_top(df_close, curr_index, order):
    if curr_index < order * 2 + 1:
        return False

    top = True
    k = curr_index - order
    v = df_close[k]
    for i in range(1, order + 1):
        if df_close[k + i] > v or df_close[k - i] > v:
            top = False
            break    
    return top

def get_bottom(df_close, curr_index, period):
    if curr_index < period * 2 + 1:
        return False

    bottom = True
    k = curr_index - period
    v = df_close[k]
    for i in range(1, period + 1):
        if df_close[k + i] < v or df_close[k - i] < v:
            bottom = False
            break    
    return bottom

def get_extremum(df, period, threshold_pct, only_extremum):
    tops = []
    bottoms = []
    up_trend = False
    confirm_i = 0

    df_close = df['close'].to_numpy()
    tmp_min = df.at[df.index[0], 'low']
    tmp_max = df.at[df.index[0], 'high']
    tmp_min_i = 0
    tmp_max_i = 0

    for i in range(len(df)):
        now_high  = df.at[df.index[i], 'high']
        now_low   = df.at[df.index[i], 'low']
        now_close = df.at[df.index[i], 'close']
        
        if up_trend:

            if now_close > tmp_max:
                tmp_max = now_close
                tmp_max_i = i
            
            if i - period > confirm_i and \
                    (get_top(df_close, i, period) or (not only_extremum and now_close < tmp_max - tmp_max * threshold_pct)):
                top = [i, df_close[i] * 1.1 , i - period, df_close[i - period]]
                tops.append(top)
                up_trend = False
                confirm_i = i
                tmp_min = now_low
                tmp_min_i = i

        elif not up_trend:

            if now_close < tmp_min:
                tmp_min = now_close
                tmp_min_i = i

            if i - period > confirm_i and \
                    (get_bottom(df_close, i, period) or (not only_extremum and now_close > tmp_min + tmp_min * threshold_pct)):
                bottom = [i, df_close[i]  * 0.9 , i - period, df_close[i - period]]
                bottoms.append(bottom)
                up_trend = True
                confirm_i = i
                tmp_max = now_high
                tmp_max_i = i
    return tops, bottoms

app = Flask(__name__)
@app.route("/", methods=['GET'])
def home():

    start_date = None
    end_date = None
    period = None
    threshold = None
    symbol = None

    if (request.method == 'GET') and (request.args):
        print(request.args)

        start_date = request.args.get('start_date')
        end_date   = request.args.get('end_date')
        period = int(request.args.get('period'))
        period = max(period, 2)
        threshold = int(request.args.get('threshold'))
        threshold = max(threshold, 1)
        threshold_pct = threshold / 100
        symbol = request.args.get('symbol')
        url = request.url

        show_extremum = False
        show_confirm = True
        only_extremum = False

        df = yf.Ticker(symbol).history(start=start_date, end=end_date)

        if not df.empty:
            df.columns = df.columns.str.lower()

            tops, bottoms = get_extremum(df, period, threshold_pct, only_extremum)

            plt.style.use("cyberpunk")
            plt.figure(figsize=(10,6))
            plt.tight_layout()
            df['close'].plot()

            mplcyberpunk.add_underglow()
            mplcyberpunk.add_glow_effects()
            mplcyberpunk.add_gradient_fill(alpha_gradientglow=0.5)

            for top in tops:
                if show_confirm: plt.plot(df.index[top[0]], top[1], marker='v', markersize=11, color='yellow')
                if show_extremum: plt.plot(df.index[top[2]], top[3], marker='v', markersize=11, color='gold')

            for bottom in bottoms:
                if show_confirm: plt.plot(df.index[bottom[0]], bottom[1], marker='^', markersize=11, color='white')
                if show_extremum: plt.plot(df.index[bottom[2]], bottom[3], marker='^', markersize=11, color='silver')

            if only_extremum: plt.savefig('static/only_extremum.png')
            if not only_extremum: plt.savefig('static/not_only_extremum.png')

        else:
            print('Empty dataframe', 'red')

    today = date.today().strftime("%Y-%m-%d")
    two_years_ago = (date.today() - timedelta(days=365 * 2)).strftime("%Y-%m-%d")
    return render_template('test.html', 
                           today=today, 
                           two_years_ago=two_years_ago, 
                           start_date=start_date, 
                           end_date=end_date, 
                           period=period,
                           threshold=threshold,
                           symbol=symbol,
                           )

if __name__ == "__main__":

    app.run(debug=True)

















