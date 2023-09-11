import streamlit as st
import pandas as pd
from NBA_Data_Process_Update import *
import numpy as np
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid



#全局布局
st.set_page_config(layout='wide')

st.sidebar.text('-------------上传文件------------')

uploaded_file = st.sidebar.file_uploader("选择文件")

if uploaded_file is not None:
    dataframe = get_data_from_excel(uploaded_file)

else:
    st.write("文件上传后可看")
    # st.write("这是一个列表：\n\n- 项目1\n- 项目2\n- 项目3")
    st.stop()

st.sidebar.text('-------------筛选区域------------')

paid_type = st.sidebar.radio(
    "付费类型",
    ["free", "paid"], horizontal=True)

week_num = st.sidebar.slider(
    '选择星期区间',
    1, int(dataframe['week_num'].max()), (1, int(dataframe['week_num'].max())))

# st.sidebar.write(week_num[1])
start_wk = week_num[0]
end_wk = week_num[1]

season_num = st.sidebar.selectbox(
    '比较周期',
    ('2021/2022','2020/2021'))

channel = st.sidebar.selectbox(
    '筛选渠道',
    ( 'Tencent', 'Non WeChat', 'WeChat Channel', 'Others','News App', 'OTT','Sports App', 'Video App', 'Web' ))

seasonality = st.sidebar.multiselect(
    '筛选赛季阶段',
    dataframe['Seasonality_Category_1st'].unique(),
    dataframe['Seasonality_Category_1st'].unique())

# st.sidebar.write('You selected:', seasonality)

if seasonality == []:
    st.write('请选择赛季阶段')
    st.stop()

st.header('NBA腾讯播放看板')
st.markdown("""---""")
st.subheader("Insight - "+paid_type+" type")
st.write(get_summary(uploaded_file,paid_type,start_wk,end_wk,season_num))
st.markdown("""---""")

df = dataframe.query("(paid_type==@paid_type) & (season_num in ('2022/2023',@season_num) )"
                     "& (week_num>=@start_wk) & (week_num<=@end_wk)"
                     "& (Seasonality_Category_1st in @seasonality)"
                     )
channel_summary = get_agg_summary(df,['Channel'])

kpi_summary = channel_summary.query("Channel in ('Tencent','WeChat Channel','Non WeChat')")
kpi_summary.set_index('Channel')
# st.write(kpi_summary)

## kpi summary
col00, col01, col02, col03, col04 = st.columns(5)
col00.write('Tencent')
col01.metric("Number of Game", int(kpi_summary.iloc[1,1]), int(kpi_summary.iloc[1,2]), delta_color='normal')
col02.metric("Average Viewer per Game", '{:,}'.format(kpi_summary.iloc[1,3]), kpi_summary.iloc[1,4], delta_color='normal')
col03.metric("Average Views per Game", '{:,}'.format(kpi_summary.iloc[1,5]), kpi_summary.iloc[1,6], delta_color='normal')
col04.metric("Average Min. per Viewer per Game", kpi_summary.iloc[1,7], kpi_summary.iloc[1,8], delta_color='normal')

col10, col11, col12, col13, col14 = st.columns(5)
col10.write('WeChat')
col11.metric("", int(kpi_summary.iloc[2,1]), int(kpi_summary.iloc[2,2]), delta_color='normal',label_visibility='hidden')
col12.metric("", '{:,}'.format(kpi_summary.iloc[2,3]), kpi_summary.iloc[2,4], delta_color='normal', label_visibility='hidden')
col13.metric("", '{:,}'.format(kpi_summary.iloc[2,5]), kpi_summary.iloc[2,6], delta_color='normal',label_visibility='hidden')
col14.metric("", kpi_summary.iloc[2,7], kpi_summary.iloc[2,6], delta_color='normal',label_visibility='hidden')

col20, col21, col22, col23, col24 = st.columns(5)
col20.write('Non-WeChat')
col21.metric("", int(kpi_summary.iloc[0,1]), int(kpi_summary.iloc[0,2]), delta_color='normal',label_visibility='hidden')
col22.metric("", '{:,}'.format(kpi_summary.iloc[0,3]), kpi_summary.iloc[0,4], delta_color='normal',label_visibility='hidden')
col23.metric("", '{:,}'.format(kpi_summary.iloc[0,5]), kpi_summary.iloc[0,6], delta_color='normal',label_visibility='hidden')
col24.metric("", kpi_summary.iloc[0,7], kpi_summary.iloc[0,8], delta_color='normal',label_visibility='hidden')


## channel summary

col30, col31 = st.columns(2)

col30.subheader("渠道表现")
col30.write(channel_summary.query("Channel not in ('Tencent','Non WeChat') "))
## weekly trend


df_selection = dataframe.query("(paid_type==@paid_type) & (season_num in ('2022/2023',@season_num) )"
                     "& (week_num>=@start_wk) & (week_num<=@end_wk)"
                     "& (Seasonality_Category_1st in @seasonality)"
                     "& (Channel == @channel)")
#
weekly_trend = get_agg_summary(df_selection,['week_num'])
# st.write(weekly_trend)

fig = px.line(weekly_trend, x='week_num', y=['Avg Uv_Current','Avg Uv_Previous'],  title="<b>每周观看Uv - {}</b>".format(channel),)

col31.plotly_chart(fig, use_container_width=True )

## Team summary

st.subheader("球队表现 - "+channel)
df_selection = dataframe.query("(paid_type==@paid_type) & (season_num in ('2022/2023',@season_num) )"
                     "& (week_num>=@start_wk) & (week_num<=@end_wk)"
                     "& (Seasonality_Category_1st in @seasonality)"
                     "& (Channel == @channel)")
home_game = df_selection.drop('Away', axis=1).rename(columns={'Home': 'Team'})
away_game = df_selection.drop('Home', axis=1).rename(columns={'Away': 'Team'})
all_game = pd.concat([home_game, away_game]).drop_duplicates()
valid_team_game = all_game[(all_game['Team'].apply(len) == 3) & (all_game['Team']!='ASG')]

team_summary = get_agg_summary(valid_team_game,['Team'])
# st.write(team_summary)
AgGrid(team_summary)

## seasonality summary
st.subheader("阶段表现 - "+channel)
df_selection = dataframe.query("(paid_type==@paid_type) & (season_num in ('2022/2023',@season_num) )"
                     "& (week_num>=@start_wk) & (week_num<=@end_wk)"
                     "& (Seasonality_Category_1st in @seasonality)"
                     "& (Channel == @channel)")

seasonality_summary= get_agg_summary(df_selection,['Seasonality_Category_1st','Seasonality_Category_2nd'])
# st.write(seasonality_summary)
AgGrid(seasonality_summary)

## top game
st.subheader("Top 10 Uv 比赛 - "+channel)
df_selection = dataframe.query("(paid_type==@paid_type) & (season_num in ('2022/2023') )"
                     "& (week_num>=@start_wk) & (week_num<=@end_wk)"
                     "& (Seasonality_Category_1st in @seasonality)"
                     "& (Channel == @channel)")

top_game = top(df_selection)
# st.write(top_game)
AgGrid(top_game)



#
# seasonality_summary = get_seasonality_summary(df_selection)
# st.write