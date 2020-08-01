from transfer_cycle import transfer_data
from signal_explore import ta_BBANDS_signal
from equity_curve import calculate_equity_curve
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 1000)

'''
bitfinex数据读取
'''

class ReadData:

    # =====导入数据
    def btc_bitfinex_data(self):
        df = pd.read_csv(
            r'./currencies_date/bitfinex/bitfinex_BTC_history_data_1_min.csv')
        return df,'btc_bitfinex_data'


    def eth_bitfinex_data(self):
        df = pd.read_csv(
            r'/Users/apple/学习/python量化/binance/back_exchange_files/currencies_date/bitfinex/bitfinex_ETH_history_data_1_min.csv')
        return df,'eth_bitfinex_data'


    def bch_bitfinex_data(self):
        df = pd.read_csv(
            r'/Users/apple/学习/python量化/binance/back_exchange_files/currencies_date/bitfinex/bitfinex_BCH_history_data_1_min.csv')
        return df,'bch_bitfinex_data'


    def ltc_bitfinex_data(self):
        df = pd.read_csv(
            r'/Users/apple/学习/python量化/binance/back_exchange_files/currencies_date/bitfinex/bitfinex_LTC_history_data_1_min.csv')
        return df,'ltc_bitfinex_data'


    def eos_bitfinex_data(self):
        df = pd.read_csv(
            r'/Users/apple/学习/python量化/binance/back_exchange_files/currencies_date/bitfinex/bitfinex_EOS_history_data_1_min.csv')
        return df,'eos_bitfinex_data'


    '''
    币安数据读取
    '''


    def btc_binance_data(self):
        df = pd.read_csv(
            r'/Users/apple/学习/python量化/binance/back_exchange_files/currencies_date/binance/binance_BTC_history_data_1_min.csv')
        return df,'btc_binance_data'


    def eth_binance_data(self):
        df = pd.read_csv(
            r'/Users/apple/学习/python量化/binance/back_exchange_files/currencies_date/binance/binance_ETH_history_data_1_min.csv')
        return df,'eth_binance_data'


    def bch_binance_data(self):
        df = pd.read_csv(
            r'/Users/apple/学习/python量化/binance/back_exchange_files/currencies_date/binance/binance_BCH_history_data_1_min.csv')
        return df,'bch_binance_data'


    def ltc_binance_data(self):
        df = pd.read_csv(
            r'/Users/apple/学习/python量化/binance/back_exchange_files/currencies_date/binance/binance_LTC_history_data_1_min.csv')
        return df,'ltc_binance_data'


    def eos_binance_data(self):
        df = pd.read_csv(
            r'/Users/apple/学习/python量化/binance/back_exchange_files/currencies_date/binance/binance_EOS_history_data_1_min.csv')
        return df,'eos_binance_data'


def main(df,crypt):
    df['candle_begin_time'] = pd.to_datetime(df['candle_begin_time'])
    df = transfer_data(df, rule_type='1H')
    # df = BBANDS_signal(df,para=[130,2])      # 手动调参发现[100，1.88]参数最优
    df = ta_BBANDS_signal(df, para=[130, 2, 2, 0])  # 130 最优参数为21.1倍
    df = calculate_equity_curve(df, leverage_rate=3)
    print(df.head())
    print(df.tail())
    df['equity_curve'].plot()
    plt.title(crypt)
    plt.savefig('./pics/'+crypt+'.png')
    plt.show()

if __name__ == '__main__':
    data = ReadData()
    df, which = data.eos_bitfinex_data()
    main(df,which)


