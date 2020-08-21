class opSettings:
    def __init__(self, num_res, num_teams, num_days, num_weeks, all_res, all_teams, all_acteams, all_days, all_weeks, max_freq, max_shifts, stat_days, all_weekends, all_weekdays):
        # Define consistent variables used in all modules
        self.num_res = num_res
        self.num_teams = num_teams
        self.num_days = num_days
        self.num_weeks = num_weeks
        self.gold_team = 3

        self.all_res = all_res
        self.all_teams = all_teams
        self.all_acteams = all_acteams
        self.all_days = all_days
        self.all_weeks = all_weeks

        # Set weekends and weekdays
        self.all_weekends = all_weekends
        self.all_weekdays = all_weekdays

        self.max_freq = max_freq
        self.max_shifts = max_shifts

        self.stat_days = stat_days
