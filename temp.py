import pandas as pd
pd.set_option('expand_frame_repr',False)

df = pd.read_csv(r'C:\Users\SNJYOR\Desktop\save_0112.csv')
df['candle_begin_time'] = pd.to_datetime(df['candle_begin_time'])
period_df = df.resample(rule='1H', on='candle_begin_time', label='left', closed='left').agg(
        {'open': 'first',
         'high': 'max',
         'low': 'min',
         'close': 'last',
         'volume': 'sum',
         })
period_df.dropna(subset=['open'], inplace=True)  # 去除一天都没有交易的周期
period_df = period_df[period_df['volume'] > 0]  # 去除成交量为0的交易周期
period_df.reset_index(inplace=True)
df = period_df[['candle_begin_time', 'open', 'high', 'low', 'close', 'volume']]
print(df.tail(60))