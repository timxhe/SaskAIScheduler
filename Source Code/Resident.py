import datetime

class Resident:
    def __init__ (self, res_id, res_name, official_days, requested_days, days_off, res_team, home_service, work_1we, work_day1, call_requested, exceptions):
        self.res_id = res_id
        self.res_name = res_name
        self.official_days = official_days
        self.requested_days = requested_days
        self.res_team = res_team
        self.home_service = home_service
        self.days_off = days_off
        self.work_day1 = work_day1
        self.work_1we = work_1we

        self.call_requested = call_requested
        self.exceptions = exceptions

        # Only official days count towards less days worked.
        #Calculated Values
        self.days_worked = 28 - days_off

        if home_service == "IM":
            self.is_IM = True
        else:
            self.is_IM = False

        # print (self.res_name, self.home_service, self.exceptions)
        # if self.exceptions == "No Weekend":
        #     print("No weekend for " + self.res_name)