import streamlit as st
import pandas as pd
from nba_html_summary import *
import numpy as np
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid
# df = get_raw_data_from_db()

#全局布局
st.set_page_config(layout='wide')

clean_data = get_clean_data()
dataframe = clean_data.query("season_num==@season_current")

last_week = int(dataframe['week_num'].max())


paid_type = st.sidebar.radio(
    "付费类型",
    ["free", "paid"], horizontal=True)



#
week_num = st.sidebar.slider(
    '选择星期区间',
    1, last_week, (1, last_week))

platform = list(dataframe['platform'].unique())
channel = st.sidebar.selectbox(
    '筛选渠道',
    (platform ))

start_wk = week_num[0]
end_wk = week_num[1]


#
df = clean_data.query("(paid_type==@paid_type) & (season_num in (@season_current,@season_previous) )"
                     "& (week_num>=@start_wk) & (week_num<=@end_wk)"
                     )

channel_summary = get_agg_summary(df,['platform'])
# st.write(channel_summary)
#
if channel_summary is None:
    st.write('没有比赛')
    st.stop()

st.header('NBA腾讯播放看板')
st.markdown("""---""")
st.subheader("Insight - "+paid_type+" type")
# st.write(get_summary(uploaded_file,paid_type,start_wk,end_wk,season_num))
st.markdown("""---""")



html_string = write_summary(season_current, season_previous, end_wk)
st.write(html_string, unsafe_allow_html=True)

# st.write(kpi_summary)


## kpi summary
kpi_summary = channel_summary.query("platform in ('Tencent','Wechat','Non Wechat')")

col00, col01, col02, col03, col04 = st.columns(5)
col00.write('Tencent')
col01.metric("Number of Game", int(get_cell(kpi_summary,'Tencent','game_current')), int(get_cell(kpi_summary,'Tencent','game_diff')), delta_color='normal')
col02.metric("Average Viewer per Game", '{:,}'.format(get_cell(kpi_summary,'Tencent','avg_uv_current')),get_cell(kpi_summary,'Tencent','uv_diff'), delta_color='normal')
col03.metric("Average Views per Game", '{:,}'.format(get_cell(kpi_summary,'Tencent','avg_vv_current')),get_cell(kpi_summary,'Tencent','vv_diff'), delta_color='normal')
col04.metric("Average Min. per Viewer per Game", get_cell(kpi_summary,'Tencent','avg_min_current'), get_cell(kpi_summary,'Tencent','min_diff'), delta_color='normal')

col10, col11, col12, col13, col14 = st.columns(5)
col10.write('Wechat')
col11.metric("", int(get_cell(kpi_summary,'Wechat','game_current')), int(get_cell(kpi_summary,'Wechat','game_diff')), delta_color='normal',label_visibility='hidden')
col12.metric("", '{:,}'.format(get_cell(kpi_summary,'Wechat','avg_uv_current')),get_cell(kpi_summary,'Wechat','uv_diff'), delta_color='normal',label_visibility='hidden')
col13.metric("", '{:,}'.format(get_cell(kpi_summary,'Wechat','avg_vv_current')),get_cell(kpi_summary,'Wechat','vv_diff'), delta_color='normal',label_visibility='hidden')
col14.metric("", get_cell(kpi_summary,'Wechat','avg_min_current'), get_cell(kpi_summary,'Wechat','min_diff'), delta_color='normal',label_visibility='hidden')

col20, col21, col22, col23, col24 = st.columns(5)
col20.write('Non-Wechat')
col21.metric("", int(get_cell(kpi_summary,'Non Wechat','game_current')), int(get_cell(kpi_summary,'Non Wechat','game_diff')), delta_color='normal',label_visibility='hidden')
col22.metric("", '{:,}'.format(get_cell(kpi_summary,'Non Wechat','avg_uv_current')),get_cell(kpi_summary,'Non Wechat','uv_diff'), delta_color='normal',label_visibility='hidden')
col23.metric("", '{:,}'.format(get_cell(kpi_summary,'Non Wechat','avg_vv_current')),get_cell(kpi_summary,'Non Wechat','vv_diff'), delta_color='normal',label_visibility='hidden')
col24.metric("", get_cell(kpi_summary,'Non Wechat','avg_min_current'), get_cell(kpi_summary,'Non Wechat','min_diff'), delta_color='normal',label_visibility='hidden')


col30, col31 = st.columns(2)

col30.subheader("渠道表现")
col30.write(channel_summary.query("platform not in ('Tencent','Non Wechat') "))
## weekly trend


df_selection = clean_data.query("(paid_type==@paid_type) & (season_num in (@season_current,@season_previous) )"
                     "& (week_num>=@start_wk) & (week_num<=@end_wk)"
                     "& (platform == @channel)")
#
weekly_trend = get_agg_summary(df_selection,['week_num']).reset_index()

# st.write(weekly_trend)

fig = px.line(weekly_trend, x='week_num', y=['avg_uv_current','avg_uv_previous'],
              title="<b>每周观看Uv - {}</b>".format(channel),markers=True)

col31.plotly_chart(fig, use_container_width=True )



## Team summary

st.subheader("球队表现 - "+channel)
df_selection = clean_data.query("(paid_type==@paid_type) & (season_num in (@season_current,@season_previous) )"
                     "& (week_num>=@start_wk) & (week_num<=@end_wk)"
                     "& (platform == @channel)")
home_game = df_selection.drop('away', axis=1).rename(columns={'home': 'team'})
away_game = df_selection.drop('home', axis=1).rename(columns={'away': 'team'})
all_game = pd.concat([home_game, away_game]).drop_duplicates()
valid_team_game = all_game[(all_game['team'].apply(len) == 3) & (all_game['team']!='ASG')]

team_summary = get_agg_summary(valid_team_game,['team'])
st.write(team_summary)


## seasonality summary
st.subheader("阶段表现 - "+channel)
df_selection = clean_data.query("(paid_type==@paid_type) & (season_num in (@season_current,@season_previous) )"
                     "& (week_num>=@start_wk) & (week_num<=@end_wk)"
                     "& (platform == @channel)")

seasonality_summary = get_agg_summary(df_selection,['tag','tag_detail'])
st.write(seasonality_summary)
# AgGrid(seasonality_summary)

## top game
st.subheader("Top 10 Uv 比赛 - "+channel)
df_selection = clean_data.query("(paid_type==@paid_type) & (season_num in (@season_current) )"
                     "& (week_num>=@start_wk) & (week_num<=@end_wk)"
                     "& (platform == @channel)")

top_game = df_selection.sort_values(by='uv')[-10:].set_index('game')
st.write(top_game)
# AgGrid(top_game)
