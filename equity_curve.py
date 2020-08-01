import pandas as pd

def calculate_equity_curve(df,leverage_rate=3,c_rate=2.0/1000,min_margin_rate = 0.15):
    # =====根据pos计算资金曲线
    # ===计算涨跌幅
    df['change'] = df['close'].pct_change(1)  # 根据收盘价计算涨跌幅
    df['buy_at_open_change'] = df['close'] / df['open'] - 1  # 从今天开盘买入，到今天收盘的涨跌幅
    df['sell_next_open_change'] = df['open'].shift(-1) / df['close'] - 1  # 从今天收盘到明天开盘的涨跌幅
    df.at[len(df) - 1, 'sell_next_open_change'] = 0

    # ===选取开仓、平仓条件
    condition1 = df['pos'] != 0
    condition2 = df['pos'] != df['pos'].shift(1)
    open_pos_condition = condition1 & condition2

    condition1 = df['pos'] != 0
    condition2 = df['pos'] != df['pos'].shift(-1)
    close_pos_condition = condition1 & condition2

    # ===对每次交易进行分组
    df.loc[open_pos_condition, 'start_time'] = df['candle_begin_time']
    df['start_time'].fillna(method='ffill', inplace=True)
    df.loc[df['pos'] == 0, 'start_time'] = pd.NaT

    # ===基本参数
      # bfx交易所最多提供3倍杠杆，leverage_rate可以在(0, 3]区间选择
      # 手续费
      # 最低保证金比例，必须占到借来资产的15%
    init_cash = 100  # 初始资金
    min_margin = init_cash * leverage_rate * min_margin_rate  # 最低保证金

    # ===计算仓位变动
    # 开仓时仓位
    df.loc[open_pos_condition, 'position'] = init_cash * leverage_rate * (1 + df['buy_at_open_change'])  # 建仓后的仓位

    # 开仓后每天的仓位的变动
    group_num = len(df.groupby('start_time'))
    if group_num > 1:
        t = df.groupby('start_time').apply(lambda x: x['close'] / x.iloc[0]['close'] * x.iloc[0]['position'])
        t = t.reset_index(level=[0])
        df['position'] = t['close']
    # elif group_num == 1:
    #     t = df.groupby('start_time')[['close', 'position']].apply(lambda x: x['close'] / x.iloc[0]['close'] * x.iloc[0]['position'])
    #     df['position'] = t.T.iloc[:, 0]

    # 每根K线仓位的最大值和最小值，针对最高价和最低价
    df['position_max'] = df['position'] * df['high'] / df['close']
    df['position_min'] = df['position'] * df['low'] / df['close']

    # 平仓时仓位
    df.loc[close_pos_condition, 'position'] *= (1 + df.loc[close_pos_condition, 'sell_next_open_change'])

    # ===计算每天实际持有资金的变化
    # 计算持仓利润
    df['profit'] = (df['position'] - init_cash * leverage_rate) * df['pos']  # 持仓盈利或者损失

    # 计算持仓利润最小值
    df.loc[df['pos'] == 1, 'profit_min'] = (df['position_min'] - init_cash * leverage_rate) * df['pos']  # 最小持仓盈利或者损失
    df.loc[df['pos'] == -1, 'profit_min'] = (df['position_max'] - init_cash * leverage_rate) * df['pos']  # 最小持仓盈利或者损失

    # 计算实际资金量
    df['cash'] = init_cash + df['profit']  # 实际资金
    df['cash'] -= init_cash * leverage_rate * c_rate  # 减去建仓时的手续费
    df['cash_min'] = df['cash'] - (df['profit'] - df['profit_min'])  # 实际最小资金
    df.loc[close_pos_condition, 'cash'] -= df.loc[close_pos_condition, 'position'] * c_rate  # 减去平仓时的手续费

    # ===判断是否会爆仓
    _index = df[df['cash_min'] <= min_margin].index
    if len(_index) > 0:
        print('有爆仓')
        df.loc[_index, '强平'] = 1
        df['强平'] = df.groupby('start_time')['强平'].fillna(method='ffill')
        df.loc[(df['强平'] == 1) & (df['强平'].shift(1) != 1), 'cash_强平'] = df['cash_min']  # 此处是有问题的
        df.loc[(df['pos'] != 0) & (df['强平'] == 1), 'cash'] = None
        df['cash'].fillna(value=df['cash_强平'], inplace=True)
        df['cash'] = df.groupby('start_time')['cash'].fillna(method='ffill')
        df.drop(['强平', 'cash_强平'], axis=1, inplace=True)  # 删除不必要的数据

    # ===计算资金曲线
    df['equity_change'] = df['cash'].pct_change()
    df.loc[open_pos_condition, 'equity_change'] = df.loc[open_pos_condition, 'cash'] / init_cash - 1  # 开仓日的收益率
    df['equity_change'].fillna(value=0, inplace=True)
    df['equity_curve'] = (1 + df['equity_change']).cumprod()

    # ===删除不必要的数据
    df.drop(['change', 'buy_at_open_change', 'sell_next_open_change', 'start_time', 'position', 'position_max',
             'position_min', 'profit', 'profit_min', 'cash', 'cash_min'], axis=1, inplace=True)
    return df
