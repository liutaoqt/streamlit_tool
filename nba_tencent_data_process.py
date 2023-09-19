import streamlit as st
import pandas as pd
import pymysql
from pymysql import Error
import datetime
import math
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

season_current= '2022/2023'
season_previous = '2021/2022'

def get_raw_data_from_db():
    conn = None
    column_names=[]

    try:
        db_connection_config = {'host': 'rm-uf665hke06d92567f.mysql.rds.aliyuncs.com',
                                'user': 'tliu',
                                'password': 'afda_3123'
                                }
        conn = pymysql.connect(**db_connection_config)
        if conn.open:
            print('Connected to MySQL database')

        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * from nba_data_integration.video_match_performance_tencent")
            df = cursor.fetchall()
            # 获取列名
            column_names = [description[0] for description in cursor.description]
    except Error as e:
        print(e)

    finally:
        if conn is not None and conn.open:
            conn.close()

    df = pd.DataFrame(list(df))
    df.columns = column_names

    # df.to_csv('tencent_query_data.csv', index=False)
    return df

@st.cache_resource
def get_clean_data():
    df_raw = get_raw_data_from_db()
    df = df_raw.query("week_num>0")
    df.fillna(0, inplace=True)
    df['non_wechat_min'] = df['all_platform_min'].astype(float) * df['all_platform_uv']
    df['wechat_min'] = df['video_channel_avg_min'] .astype(float)* df['video_channel_uv']
    df['tencent_min'] = df['non_wechat_min'] + df['wechat_min']
    df['tencent_uv'] = df['all_platform_uv'] + df['video_channel_uv']
    df['tencent_vv'] = df['all_platform_vv'] + df['video_channel_vv']

    df.rename(columns={'all_platform_uv': 'non_wechat_uv', 'all_platform_vv': 'non_wechat_vv',
                       'video_channel_uv': 'wechat_uv', 'video_channel_vv': 'wechat_vv'},inplace=True)

    df['game'] = df['away'] + '(away) vs ' + df['home'] + '(home) on ' + df['date'].apply(
            lambda x: x.strftime("%Y-%m-%d"))

    special_game_inx= df['away'].str.startswith('AS')

    df.loc[special_game_inx,'game']= df.loc[special_game_inx,'away'] +' on ' + df.loc[special_game_inx,'date'].apply(lambda x:x.strftime("%Y-%m-%d"))

    df.drop(['time', 'all_platform_min', 'channel_name', 'create_time','channel_name','create_time','platform_name',
         'game_type', 'update_time' ,'user_performed_insert','video_channel_avg_min','video_channel_online_audience'], axis=1, inplace=True)

    id_vars = ['game', 'home', 'away', 'season_num', 'paid_type', 'tag_detail', 'tag', 'week_num', 'year_num', 'date']

    long_df = pd.melt(df, id_vars=id_vars, value_name='value')

    long_df['platform'] = long_df['variable'].apply(lambda x: x[:x.rfind('_')])
    long_df['metrics'] = long_df['variable'].apply(lambda x: x[x.rfind('_')+1:])
    long_df['platform'] = long_df['platform'].apply(lambda x: 'other' if x in (['h5','pc','qq_browser']) else x)
    long_df['platform'] = long_df['platform'].apply(lambda x: x.replace('_',' ').title())

    long_df.dropna(axis=0, subset=['value'], inplace=True)
    long_df.drop(['variable'], axis=1, inplace=True)
    long_df = long_df.query("value>0")

    id_columns = [col for col in long_df.columns.to_list() if col not in ['value', 'metrics']]

    wide_df = pd.pivot_table(long_df, aggfunc='sum', index=id_columns, columns='metrics', values='value').reset_index()
    return wide_df

def get_agg_summary(df_selection, dimention):
    df_selection['season']= df_selection['season_num'].apply(lambda x: 'current' if x == season_current else 'previous')
    dimention1 = dimention+['season']
    agg_df = (df_selection.groupby(dimention1)[
                       ['uv', 'vv', 'game', 'min']].
                   agg({'uv': 'sum', 'vv': 'sum', 'min': 'sum', 'game': pd.Series.nunique})).reset_index()
    agg_df['avg_uv'] = agg_df['uv'] / agg_df['game']
    agg_df['avg_vv'] = agg_df['vv'] / agg_df['game']
    agg_df['avg_min'] = agg_df['min'] / (agg_df['avg_uv'] * agg_df['game'])
    agg_summary = pd.pivot_table(agg_df, aggfunc='sum', index=dimention,
                                      columns=['season'], values=['avg_uv', 'avg_vv', 'avg_min', 'game'])
    level0 = agg_summary.columns.get_level_values(0)
    level1 = agg_summary.columns.get_level_values(1)
    agg_summary.columns = level0 + '_' + level1
    agg_summary.reset_index(inplace=True)

    if 'game_current' not in agg_summary.columns:
        return None
    elif 'game_previous' not in agg_summary.columns:
        agg_summary['game_previous'] = 0
        agg_summary['avg_uv_previous'] = 0
        agg_summary['avg_vv_previous'] = 0
        agg_summary['avg_min_previous'] = 0
        agg_summary['game_diff'] = agg_summary['game_current']
        agg_summary['min_diff'] = '-'
        agg_summary['min_diff'] = '-'
        agg_summary['min_diff'] = '-'
    else:
        agg_summary['game_diff'] = agg_summary['game_current'] - agg_summary['game_previous']
        agg_summary['min_diff'] = agg_summary['avg_min_current']/agg_summary['avg_min_previous'] - 1
        agg_summary['uv_diff'] = agg_summary['avg_uv_current']/agg_summary['avg_uv_previous'] - 1
        agg_summary['vv_diff'] = agg_summary['avg_vv_current'] / agg_summary['avg_vv_previous'] - 1
    #
    integer_columns = ['avg_uv_current', 'avg_vv_current','avg_uv_previous', 'avg_vv_previous']
    # 将指定列转换为整型
    for col in integer_columns:
        agg_summary[col] = agg_summary[col].apply(lambda x: round(x) if x >0 else 0)

    agg_summary['avg_min_current'] = agg_summary['avg_min_current'].apply(lambda x: round(x,2) if x > 0 else 0)
    agg_summary['avg_min_previous'] = agg_summary['avg_min_previous'].apply(lambda x:  round(x,2) if x > 0 else 0)

    percent_columns = ['min_diff','uv_diff','vv_diff']

    for col in percent_columns:
        agg_summary[col] = agg_summary[col].apply(lambda x: '-' if math.isnan(x) else '{:+.1%}'.format(x))

    order = dimention + ['game_current','game_diff','avg_uv_current','uv_diff','avg_vv_current','vv_diff','avg_min_current','min_diff',
                  'game_previous','avg_uv_previous','avg_vv_previous','avg_min_previous']

    agg_summary = agg_summary[order].set_index(dimention)
    return agg_summary

def get_min_max_from_uv_diff(df_selection):
    df_selection = df_selection[df_selection['uv_diff']!='-']
    idxmax = df_selection['uv_diff'].str.strip('%').astype(float).idxmax()
    idxmin = df_selection['uv_diff'].str.strip('%').astype(float).idxmin()
    max_diff = df_selection.loc[idxmax,'uv_diff']
    min_diff = df_selection.loc[idxmin,'uv_diff']
    max_uv = df_selection.loc[idxmax,'avg_uv_current']
    min_uv = df_selection.loc[idxmin,'avg_uv_current']
    if float(max_diff.strip('%'))>0 and float(min_diff.strip('%'))>0 :
        return [idxmax, max_diff,max_uv,'-','-','-']
    elif float(max_diff.strip('%'))>0 and float(min_diff.strip('%'))<0 :
        return [idxmax, max_diff,max_uv,idxmin,min_diff,min_uv]
    else:
        return ['-','-','-', idxmin, min_diff, min_uv]

# df_selection = df.query("(paid_type=='free') & (season_num in ('2022/2023','2021/2022'))")
# channel_summary = get_agg_summary(df_selection, ['platform'])
# print(get_min_max_from_uv_diff(channel_summary))

def get_pop_game(df_selection):
    df_selection.set_index(['game'],inplace=True)
    idxmax = df_selection['uv'].idxmax()
    return [idxmax, int(df_selection.loc[idxmax, 'uv']), df_selection.loc[idxmax, 'tag']]

# print(get_pop_game(df_selection))

def get_wechat_performance(df_selection):
    # df_selection.set_index('platform',inplace=True)
    if 'Wechat' not in df_selection.index:
        return ['-','-','-']
    else :
        uv_current = df_selection.loc['Wechat','avg_uv_current']
    # print(uv_current)
    uv_diff = df_selection.loc['Wechat', 'uv_diff']
    if uv_diff == '-' and uv_current>0:
        label = 'up'
    elif float(uv_diff.strip('%'))>0:
        label = 'up'
    else:
        label = 'down'
    return [label,uv_diff, uv_current]

# print(get_wechat_performance(channel_summary))

def get_max_from_uv(df_selection):
    idxmax = df_selection['avg_uv_current'].idxmax()
    max_uv = df_selection.loc[idxmax,'avg_uv_current']
    max_uv_diff = df_selection.loc[idxmax, 'uv_diff']
    return [idxmax, max_uv,max_uv_diff]

# print(get_max_from_uv(channel_summary))

def get_wk_dt(df_selection):
    dt = df_selection['date'].max()
    end_dt = (dt + datetime.timedelta(days=7 - dt.weekday())).strftime('%b %d ， %Y')
    return end_dt

# print(get_wk_dt(df))
#
# print(channel_summary['uv_diff'].str.strip('%').astype(float).idxmax())
# print(channel_summary['uv_diff'].str.strip('%').astype(float).idxmin())