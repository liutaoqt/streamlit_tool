import streamlit as st
import pandas as pd
import math
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


####### Tecent Data #####
@st.cache_resource
def get_data_from_excel(file_name):

    dataframe = pd.read_excel(file_name, engine='openpyxl')
    dataframe.query("week_num>0",inplace=True)
    dataframe.fillna(0, inplace=True)
    dataframe.rename(columns={'Paid Type':'paid_type'},inplace=True)
    dataframe.rename(columns={'Seasonality Category 1st': 'Seasonality_Category_1st'}, inplace=True)
    dataframe.rename(columns={'Seasonality Category 2nd': 'Seasonality_Category_2nd'}, inplace=True)
    dataframe.rename(columns={'Away, Date, Home (Combined)': 'Game'}, inplace=True)

    dataframe['All Platform Min'] = dataframe['All Platform Avg Min'] * dataframe['All Platform Uv']
    dataframe['Video Channel Min'] = dataframe['Video Channel Avg Min'] * dataframe['Video Channel Uv']
    dataframe['Tencent Min'] = dataframe['All Platform Min'] + dataframe['Video Channel Min']
    dataframe['Tencent Uv'] = dataframe['All Platform Uv'] + dataframe['Video Channel Uv']
    dataframe['Tencent Vv'] = dataframe['All Platform Vv'] + dataframe['Video Channel Vv']
    dataframe.drop(['season_num.1', 'Video Channel Online Audience', 'All Platform Avg Min', 'Video Channel Avg Min'],
                   axis=1, inplace=True)

    id_vars = ['Game',
               'Home',
               'Away',
               'season_num',
               'paid_type',
               'Seasonality_Category_1st',
               'Seasonality_Category_2nd',
               'week_num',
               'year_num',
               'Day of Date'
               ]

    long_df = pd.melt(dataframe, id_vars=id_vars, value_name='value')
    long_df['platform'] = long_df['variable'].apply(lambda x: x.rsplit(None, 1)[0])
    long_df['metrics'] = long_df['variable'].apply(lambda x: x.rsplit(None, 1)[1])

    mapping = {
        'All Platform': 'Non WeChat',
        'H5': 'Others',
        'News App': 'News App',
        'Other': 'Others',
        'Ott': 'OTT',
        'Pc': 'Others',
        'Qq Browser': 'Others',
        'Sports App': 'Sports App',
        'Video App': 'Video App',
        'Web': 'Web',
        'Video Channel': 'WeChat Channel',
        'Tencent': 'Tencent'
    }

    long_df['Channel'] = long_df['platform'].map(mapping)
    long_df.dropna(axis=0, subset=['value'], inplace=True)
    long_df.drop(['platform', 'variable'], axis=1, inplace=True)
    long_df = long_df.query("value>0")

    id_columns = [col for col in long_df.columns.to_list() if col not in ['value', 'metrics']]
    # long_df_grouped = long_df.groupby(id_columns)['value'].sum().reset_index()
    #
    # id_columns = [col for col in long_df.columns.to_list() if col != 'metrics']
    # wide_df = pd.pivot_table(long_df_grouped, values='value', index=id_columns, columns='metrics').reset_index()

    wide_df = pd.pivot_table(long_df, aggfunc='sum', index=id_columns, columns='metrics', values='value').reset_index()

    wide_df['AVG Min'] = wide_df['Min'] / wide_df['Uv']

    return wide_df

def get_agg_summary(df_selection, dimention):
    df_selection['season_num']= df_selection['season_num'].apply(lambda x: 'Current' if x=='2022/2023' else 'Previous')
    dimention1 = dimention+['season_num']
    agg_df = (df_selection.groupby(dimention1)[
                   ['Uv', 'Vv', 'Game', 'Min']].
               agg({'Uv': 'sum', 'Vv': 'sum', 'Min': 'sum', 'Game': pd.Series.nunique})).reset_index()
    agg_df['Avg Uv'] = agg_df['Uv'] / agg_df['Game']
    agg_df['Avg Vv'] = agg_df['Vv'] / agg_df['Game']
    agg_df['Avg Time'] = agg_df['Min'] / (agg_df['Avg Uv'] * agg_df['Game'])
    agg_summary = pd.pivot_table(agg_df, aggfunc='sum', index=dimention,
                                  columns=['season_num'], values=['Avg Uv', 'Avg Vv', 'Avg Time', 'Game'])
    level0 = agg_summary.columns.get_level_values(0)
    level1 = agg_summary.columns.get_level_values(1)
    agg_summary.columns = level0 + '_' + level1
    agg_summary.reset_index(inplace=True)

    agg_summary['Game_diff'] = agg_summary['Game_Current'] - agg_summary['Game_Previous']
    agg_summary['Time_diff'] = agg_summary['Avg Time_Current']/agg_summary['Avg Time_Previous'] - 1
    agg_summary['Uv_diff'] = agg_summary['Avg Uv_Current']/agg_summary['Avg Uv_Previous'] - 1
    agg_summary['Vv_diff'] = agg_summary['Avg Vv_Current'] / agg_summary['Avg Vv_Previous'] - 1
    #
    integer_columns = [ 'Avg Uv_Current', 'Avg Vv_Current',
                       'Avg Uv_Previous', 'Avg Vv_Previous']
    # 将指定列转换为整型
    for col in integer_columns:
        agg_summary[col] = agg_summary[col].apply(lambda x: round(x) if x>0 else None)

    agg_summary['Avg Time_Current'] = agg_summary['Avg Time_Current'].apply(lambda x: round(x,2) if x > 0 else None)
    agg_summary['Avg Time_Previous'] = agg_summary['Avg Time_Previous'].apply(lambda x:  round(x,2) if x > 0 else None)

    percent_columns = ['Time_diff','Uv_diff','Vv_diff']

    for col in percent_columns:
        agg_summary[col] = agg_summary[col].apply(lambda x: '{:.1%}'.format(x) if abs(x)>=0 else "")

    order = dimention+['Game_Current','Game_diff','Avg Uv_Current','Uv_diff','Avg Vv_Current','Vv_diff','Avg Time_Current','Time_diff',
              'Game_Previous','Avg Uv_Previous','Avg Vv_Previous','Avg Time_Previous']

    agg_summary = agg_summary[order].reset_index(drop=True)

    return agg_summary

def top(df, n=10 , column='Uv'):
    return df.sort_values(by=column)[-n:]


def get_float_diff(x):
    return float(x.strip("%"))/100

def get_min_max_index(df,lookup_column, find_colum,label, n):
    sorted_data = df.sort_values(lookup_column)
    if label == 'max':
        lookup_value = sorted_data[lookup_column].iloc[-n]
    if label == 'min':
        lookup_value = sorted_data[lookup_column].iloc[n-1]
    corresponding_value = sorted_data[sorted_data[lookup_column] == lookup_value][find_colum].values[0]
    return [lookup_value,corresponding_value]


def get_summary(file_name, paid_type, start_wk, end_wk, season_num):
    df = get_data_from_excel(file_name)
    df_overall = df.query("(paid_type==@paid_type) & (season_num in ('2022/2023',@season_num) )"
                          "& (week_num>=@start_wk) & (week_num<=@end_wk)")
    channel_summary = get_agg_summary(df_overall, ['Channel'])
    non_wechat_channel_summary=channel_summary.query("Channel not in ('Tencent','Non WeChat') ")

    df_tencent = df.query("(paid_type==@paid_type) & (season_num in ('2022/2023',@season_num) )"
                          "& (week_num>=@start_wk) & (week_num<=@end_wk) & (Channel=='Tencent')")

    home_game = df_tencent.drop('Away', axis=1).rename(columns={'Home': 'Team'})
    away_game = df_tencent.drop('Home', axis=1).rename(columns={'Away': 'Team'})
    all_game = pd.concat([home_game, away_game]).drop_duplicates()
    valid_team_game = all_game[(all_game['Team'].apply(len) == 3) & (all_game['Team'] != 'ASG')]
    team_summary = get_agg_summary(valid_team_game, ['Team'])

    df_tencent_2023 = df.query("(paid_type==@paid_type) & (season_num in ('2022/2023') )"
                               "& (week_num>=@start_wk) & (week_num<=@end_wk) & (Channel=='Tencent')")


    text = ('本赛季第 {} 周至第 {} 周期间，\n\n- Tencent共计播出{}场比赛(去年同期 {}场)，场均观看UV达到{}人(YoY {})，其中：\n\t'
            '- Wechat播出{}场(去年同期 {}场)，场均观看UV达到{}人(YoY {})\n\t- Non-Wechat播出{}场(去年同期 {}场)，场均观看UV达到{}人(YoY {})，'
            '增长最多的是{}渠道，同比增长{}; 下降最多的是{}渠道，同比下降{}\n\n- '
            '场均观看UV排名前三的球队是：{}、{}、{}；场均观看UV排名前三的比赛是（客队在前）：1） {}； 2） {}； 3） {}')

    summary = text.format(start_wk,end_wk,
                      channel_summary.iloc[5][1], channel_summary.iloc[5][9], '{:,}'.format(channel_summary.iloc[5,3]),channel_summary.iloc[5][4],
                      channel_summary.iloc[7][1], channel_summary.iloc[7][9], '{:,}'.format(channel_summary.iloc[7,3]),channel_summary.iloc[7][4],
                      channel_summary.iloc[1][1], channel_summary.iloc[1][9], '{:,}'.format(channel_summary.iloc[1,3]),channel_summary.iloc[1][4],
                      get_min_max_index(channel_summary, 'Uv_diff', 'Channel', 'max', 1)[1],
                      get_min_max_index(channel_summary, 'Uv_diff', 'Channel', 'max', 1)[0],
                      get_min_max_index(non_wechat_channel_summary, 'Uv_diff', 'Channel', 'min', 1)[1],
                      get_min_max_index(non_wechat_channel_summary, 'Uv_diff', 'Channel', 'min', 1)[0],
                      get_min_max_index(team_summary, 'Avg Uv_Current', 'Team', 'max', 1)[1],
                      get_min_max_index(team_summary, 'Avg Uv_Current', 'Team', 'max', 2)[1],
                      get_min_max_index(team_summary, 'Avg Uv_Current', 'Team', 'max', 3)[1],
                      get_min_max_index(df_tencent_2023, 'Uv', 'Game', 'max', 1)[1],
                      get_min_max_index(df_tencent_2023, 'Uv', 'Game', 'max', 2)[1],
                      get_min_max_index(df_tencent_2023, 'Uv', 'Game', 'max', 3)[1]
                      )
    return summary

# print(get_summary('NBA Query Table (2).xlsx','free',1,35,'2021/2022'))

# df_selection = dataframe.query("(paid_type=='free') & (season_num in ('2022/2023','2021/2022')) & (Channel='Tencent')")
# weekly_trend = get_agg_summary(df_selection,['week_num'])
# # col31.write(weekly_trend)
# #
# fig = px.bar(weekly_trend, x='week_num', y='Avg Uv_Current')
# fig.add_trace(px.line(weekly_trend, x='week_num', y='Uv_diff'))

