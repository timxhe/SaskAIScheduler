import Convert_Date
import opSettings as op
import math

def calcSettings(currentSettings, res_List):
    num_res = len(res_List)
    num_teams = currentSettings.num_teams
    num_days = int(currentSettings.num_days)
    num_weeks = int(num_days / 7)
    all_res = range(num_res)
    all_teams = range(num_teams)
    all_acteams = range(num_teams - 1)
    all_days = range(num_days)
    all_weeks = range(num_weeks)

    max_freq = currentSettings.max_freq
    max_shifts = math.ceil(num_days / max_freq)

    # Define Stat Days
    # print(currentSettings.temp_stats)
    stat_days = Convert_Date.convertDate(currentSettings.temp_stats, currentSettings)
    # print(stat_days)

    return op.opSettings(num_res, num_teams, num_days, num_weeks, all_res, all_teams, all_acteams, all_days, all_weeks, max_freq, max_shifts, stat_days)