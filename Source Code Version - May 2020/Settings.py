class Settings:
    def __init__(self, loadTable, num_days, num_teams, max_freq, test_time, first_Date, last_Date,  thusat_adjust, frisun_adjust, academic_days, stat_holidays, combinations_switch, requests_switch, max_two_weekends, academic_switch, weekday_max, max_load_diff):
        self.loadConvert = loadTable
        self.num_days = num_days
        self.num_teams = num_teams
        self.max_freq = max_freq
        self.test_time = test_time

        self.first_Date = first_Date
        self.last_Date = last_Date
        self.thusat_adjust = thusat_adjust
        self.frisun_adjust = frisun_adjust

        self.academic_days = academic_days

        self.combinations_switch = combinations_switch
        self.requests_switch = requests_switch
        self.max_two_weekends = max_two_weekends
        self.academic_switch = academic_switch

        self.weekday_max = weekday_max
        self.max_load_diff = max_load_diff

        self.temp_stats = stat_holidays

