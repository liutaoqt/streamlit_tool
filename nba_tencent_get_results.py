from nba_tencent_data_process import *


def word_format(content):
    if content.isnumeric():
        if int(content) > 1000000:
            txt = '<b>{}M</b>'.format(round(int(content) / 1000000, 1))
        elif int(content) > 1000:
            txt = '<b>{}K</b>'.format(round(int(content) / 1000))
        else:
            txt = '<b>{}</b>'.format(content)
    elif '-' in content and content != '-':
        txt = '<span style="color:red">{}</span>'.format(content)
    elif '+' in content:
        txt = '<span style="color:green">{}</span>'.format(content)
    else:
        txt = content
    return txt


# season_current= '2022/2023'
# season_previous = '2021/2022'
# end_week = 35
def get_cell(df, row_index, col_index):
    try:
        return df.loc[row_index,col_index]
    except KeyError as e:
        return 0

def get_numbers( season_current, season_previous, end_week=None):
    df = get_clean_data()
    numbers_list = {}
    if end_week is None:
        df_free = df.query("(paid_type=='free') & (season_num in (@season_current,@season_previous)) "
                       "& (week_num>0)")
    else:
        df_free = df.query("(paid_type=='free') & (season_num in (@season_current,@season_previous)) "
                       "& (week_num>0) & (week_num<=@end_week)")

    numbers_list['date'] = get_wk_dt(df_free)

    free_channel_summary = get_agg_summary(df_free, ['platform']).drop(['Tencent', 'Non Wechat'])
    free_most_viewer = get_max_from_uv(free_channel_summary)

    numbers_list['free_most_viewer_channel'] = free_most_viewer[0]
    numbers_list['free_most_viewer_channel_uv'] = word_format(str(free_most_viewer[1]))
    numbers_list['free_most_viewer_channel_yoy'] = word_format(str(free_most_viewer[2]))

    free_channel_summary.drop(numbers_list['free_most_viewer_channel'], inplace=True)

    if 'Other' in free_channel_summary.index:
        free_channel_summary.drop(['Other'], inplace=True)

    free_channel_min_max_diff = get_min_max_from_uv_diff(free_channel_summary)
    numbers_list['free_biggest_drop_channel'] = free_channel_min_max_diff[3]
    numbers_list['free_biggest_drop_channel_uv'] = word_format(str(free_channel_min_max_diff[4]))
    numbers_list['free_biggest_drop_channel_yoy'] = word_format(str(free_channel_min_max_diff[5]))

    numbers_list['free_biggest_increase_channel'] = free_channel_min_max_diff[0]
    numbers_list['free_biggest_increase_channel_uv'] = word_format(str(free_channel_min_max_diff[1]))
    numbers_list['free_biggest_increase_channel_yoy'] = word_format(str(free_channel_min_max_diff[2]))

    free_df_current = df_free.query("(season_num ==@season_current ) & platform == 'Tencent'")
    free_pop = get_pop_game(free_df_current)
    numbers_list['free_pop_game'] = free_pop[0]
    numbers_list['free_pop_game_uv'] = word_format(str(free_pop[1]))

    free_df_last_week = df_free.query(" week_num == @end_week")
    free_channel_summary_last_week = get_agg_summary(free_df_last_week, ['platform'])
    free_df_last = free_df_last_week.query("(season_num ==@season_current ) & platform == 'Tencent'")

    if free_channel_summary_last_week is not None:
        numbers_list['free_game_num_last'] = free_channel_summary_last_week.loc['Tencent', 'game_current']
        numbers_list['free_game_uv_last'] = word_format(
            str(free_channel_summary_last_week.loc['Tencent', 'avg_uv_current']))
        numbers_list['free_game_yoy_last'] = word_format(str(free_channel_summary_last_week.loc['Tencent', 'uv_diff']))
        free_pop_last_week = get_pop_game(free_df_last)
        numbers_list['free_pop_game_last'] = free_pop_last_week[0]
        numbers_list['free_pop_game_uv_last'] = word_format(str(free_pop_last_week[1]))
    else:
        numbers_list['free_game_num_last'] = 0
        numbers_list['free_game_uv_last'] = '-'
        numbers_list['free_game_yoy_last'] = '-'
        numbers_list['free_pop_game_last'] = '-'
        numbers_list['free_pop_game_uv_last'] = '-'

    if end_week is None:
        df_paid = df.query("(paid_type=='paid') & (season_num in (@season_current,@season_previous)) "
                       "& (week_num>0)")
    else:
        df_paid = df.query("(paid_type=='paid') & (season_num in (@season_current,@season_previous)) "
                       "& (week_num>0) & (week_num <= @end_week)")

    paid_channel_summary = get_agg_summary(df_paid, ['platform']).drop(['Tencent', 'Non Wechat'])
    paid_wechat_performance = get_wechat_performance(paid_channel_summary)
    numbers_list['paid_wechat_label'] = paid_wechat_performance[0]
    numbers_list['paid_wechat_yoy'] = word_format(str(paid_wechat_performance[1]))
    numbers_list['paid_wechat_uv'] = word_format(str(paid_wechat_performance[2]))

    if 'Wechat' in paid_channel_summary.index:
        paid_channel_summary.drop(['Wechat'], inplace=True)

    if 'Other' in paid_channel_summary.index:
        paid_channel_summary.drop(['Other'], inplace=True)

    paid_channel_min_max_diff = get_min_max_from_uv_diff(paid_channel_summary)
    numbers_list['paid_biggest_drop_channel'] = paid_channel_min_max_diff[3]
    numbers_list['paid_biggest_drop_channel_uv'] = word_format(str(paid_channel_min_max_diff[4]))
    numbers_list['paid_biggest_drop_channel_yoy'] = word_format(str(paid_channel_min_max_diff[5]))

    numbers_list['paid_biggest_increase_channel'] = paid_channel_min_max_diff[0]
    numbers_list['paid_biggest_increase_channel_uv'] = word_format(str(paid_channel_min_max_diff[1]))
    numbers_list['paid_biggest_increase_channel_yoy'] = word_format(str(paid_channel_min_max_diff[2]))

    paid_df_current = df_paid.query("(season_num ==@season_current ) & platform == 'Tencent'")
    paid_pop = get_pop_game(paid_df_current)
    numbers_list['paid_pop_game'] = paid_pop[0]
    numbers_list['paid_pop_game_uv'] = word_format(str(paid_pop[1]))
    numbers_list['paid_pop_game_season'] = paid_pop[2]

    paid_tag_summary = get_agg_summary(df_paid, ['tag'])
    paid_most_viewer = get_max_from_uv(paid_tag_summary)
    numbers_list['paid_most_viewer_season'] = paid_most_viewer[0]
    numbers_list['paid_most_viewer_uv'] = word_format(str(paid_most_viewer[1]))
    numbers_list['paid_most_viewer_yoy'] = word_format(str(paid_most_viewer[2]))

    paid_df_last_week = df_paid.query(" week_num == @end_week")
    paid_channel_summary_last_week = get_agg_summary(paid_df_last_week, ['platform'])
    paid_df_last = paid_df_last_week.query("(season_num ==@season_current ) & platform == 'Tencent'")

    if paid_channel_summary_last_week is not None:
        numbers_list['paid_game_num_last'] = paid_channel_summary_last_week.loc['Tencent', 'game_current']
        numbers_list['paid_game_uv_last'] = word_format(
            str(paid_channel_summary_last_week.loc['Tencent', 'avg_uv_current']))
        numbers_list['paid_game_yoy_last'] = word_format(str(paid_channel_summary_last_week.loc['Tencent', 'uv_diff']))
        paid_pop_last_week = get_pop_game(paid_df_last)
        numbers_list['paid_pop_game_last'] = paid_pop_last_week[0]
        numbers_list['paid_pop_game_uv_last'] = word_format(str(paid_pop_last_week[1]))
    else:
        numbers_list['paid_game_num_last'] = 0
        numbers_list['paid_game_uv_last'] = '-'
        numbers_list['paid_game_yoy_last'] = '-'
        numbers_list['paid_pop_last_week'] = '-'
        numbers_list['paid_pop_game_last'] = '-'
        numbers_list['paid_pop_game_uv_last'] = '-'

    return numbers_list

