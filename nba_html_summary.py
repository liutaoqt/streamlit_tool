from nba_tencent_get_results import *
import os
import warnings
warnings.filterwarnings('ignore')

def write_summary(season_current,season_previous,end_week = None):

    numbers_list = get_numbers(season_current, season_previous, end_week)

    date = numbers_list['date']
    free_most_viewer_channel = numbers_list['free_most_viewer_channel']
    free_most_viewer_channel_uv = numbers_list['free_most_viewer_channel_uv']
    free_most_viewer_channel_yoy = numbers_list['free_most_viewer_channel_yoy']
    free_biggest_drop_channel = numbers_list['free_biggest_drop_channel']
    free_biggest_drop_channel_uv = numbers_list['free_biggest_drop_channel_uv']
    free_biggest_drop_channel_yoy = numbers_list['free_biggest_drop_channel_yoy']
    free_biggest_increase_channel = numbers_list['free_biggest_increase_channel']
    free_biggest_increase_channel_uv = numbers_list['free_biggest_increase_channel_uv']
    free_biggest_increase_channel_yoy = numbers_list['free_biggest_increase_channel_yoy']
    free_pop_game = numbers_list['free_pop_game']
    free_pop_game_uv = numbers_list['free_pop_game_uv']
    free_game_num_last = int(numbers_list['free_game_num_last'])
    free_game_uv_last = numbers_list['free_game_uv_last']
    free_game_yoy_last = numbers_list['free_game_yoy_last']
    free_pop_game_last = numbers_list['free_pop_game_last']
    free_pop_game_uv_last = numbers_list['free_pop_game_uv_last']
    paid_wechat_label = numbers_list['paid_wechat_label']
    paid_wechat_yoy = numbers_list['paid_wechat_yoy']
    paid_wechat_uv = numbers_list['paid_wechat_uv']
    paid_biggest_drop_channel = numbers_list['paid_biggest_drop_channel']
    paid_biggest_drop_channel_uv = numbers_list['paid_biggest_drop_channel_uv']
    paid_biggest_drop_channel_yoy = numbers_list['paid_biggest_drop_channel_yoy']
    paid_biggest_increase_channel = numbers_list['paid_biggest_increase_channel']
    paid_biggest_increase_channel_uv = numbers_list['paid_biggest_increase_channel_uv']
    paid_biggest_increase_channel_yoy = numbers_list['paid_biggest_increase_channel_yoy']
    paid_pop_game = numbers_list['paid_pop_game']
    paid_pop_game_uv = numbers_list['paid_pop_game_uv']
    paid_pop_game_season = numbers_list['paid_pop_game_season']
    paid_most_viewer_season = numbers_list['paid_most_viewer_season']
    paid_most_viewer_uv = numbers_list['paid_most_viewer_uv']
    paid_most_viewer_yoy = numbers_list['paid_most_viewer_yoy']
    paid_game_num_last = int(numbers_list['paid_game_num_last'])
    paid_game_uv_last = numbers_list['paid_game_uv_last']
    paid_game_yoy_last = numbers_list['paid_game_yoy_last']
    paid_pop_game_last = numbers_list['paid_pop_game_last']
    paid_pop_game_uv_last = numbers_list['paid_pop_game_uv_last']

    txt = f"<p>Dear all, </p> <p>Please find the NBA China Viewership Summary for <b>{date}</b>. </p>".format(date)

    txt = txt + '<p><a name="_Hlk145598413"><b><u><span style="font-size:14.0pt;line-height:105%;color:#002060">Insights:</span></u></b></a></p>'
    txt = txt + f"<p><span style=\"mso-bookmark:_Hlk145598413\">• For Tencent Free in this season,  {free_most_viewer_channel} is the channel with the most viewers (avg UV {free_most_viewer_channel_uv}) and YOY {free_most_viewer_channel_yoy}. Except {free_most_viewer_channel}"
    if free_biggest_drop_channel!='-':
        txt = txt + f", the biggest drop is in {free_biggest_drop_channel} (YoY {free_biggest_drop_channel_yoy} to {free_biggest_drop_channel_uv})"
    if free_biggest_increase_channel!='-':
        txt = txt + f", the biggest increase is in {free_biggest_increase_channel} (YoY {free_biggest_increase_channel_yoy} to {free_biggest_increase_channel_uv})"
    txt = txt +  f". {free_pop_game} is the most game with {free_pop_game_uv} UV. In the recent week, Tencent Free has broadcast a total of {free_game_num_last} games"
    if free_game_num_last > 0:
        txt = txt + f", with an average of {free_game_uv_last} UV per game (YoY {free_game_yoy_last}). The most popular game is: {free_pop_game_last} (UV {free_pop_game_uv_last})\n"
    txt = txt+f"<p><span style=\"mso-bookmark:_Hlk145598413\">• For Tencent Paid in this season, "
    if paid_wechat_label !='-':
        txt = txt + f"WeChat Channel was {paid_wechat_label} by {paid_wechat_yoy} to {paid_wechat_uv}, in Non-WeChat Channel (excluding Other)"
    if paid_biggest_drop_channel!='-':
        txt = txt + f", the biggest drop is in {paid_biggest_drop_channel} (YoY {paid_biggest_drop_channel_yoy} to {paid_biggest_drop_channel_uv})"
    if paid_biggest_increase_channel!='-':
        txt = txt + f", the biggest increase is in {paid_biggest_increase_channel} (YoY {paid_biggest_increase_channel_yoy} to {paid_biggest_increase_channel_uv})"
    txt= txt + f". {paid_pop_game} in {paid_pop_game_season} is the most popular game, with {paid_pop_game_uv} UV. {paid_most_viewer_season} have averaged {paid_most_viewer_uv} UV per Game, YoY {paid_most_viewer_yoy}. In the recent week, Tencent Paid has broadcast a total of {paid_game_num_last} games"
    if paid_game_num_last > 0:
        txt = txt + f", with an average of {paid_game_uv_last} UV per game (YoY {paid_game_yoy_last}). The most popular game is: {paid_pop_game_last} (UV {paid_pop_game_uv_last})"

    txt = txt + """<p><b><span style="color:#CC3300">For more information, check out Dashboards in the attachments!</span></b></p>
    <p>Please contact Valery Dai <a href="mailto:jdai@nba.com">jdai@nba.com</a> with any questions.</p>"""
    return txt

if __name__ == '__main__':
    # text 1
    for week in range(35):
        txt = write_summary(season_current, season_previous, week+1)
        # 将内容写入HTML文件
        with open("nba_summary_{}.html".format(week+1), "w") as f:
            f.write(txt)

    # text 2
    # txt = write_summary(season_current, season_previous,35)
    # with open("nba_summary.html", "w") as f:
    #     f.write(txt)
    # os.startfile("nba_summary.html")