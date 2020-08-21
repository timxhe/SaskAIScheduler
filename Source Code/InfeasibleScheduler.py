from __future__ import print_function
from ortools.sat.python import cp_model
import math
import Convert_Date
import Read_File
import xlwt

def infeasibleScheduler(currentSettings, res_List, opSettings, test_time, path):
    # To define number of residents during the day
    res_per_team = {}
    temp_team_list = []
    for r in opSettings.all_res:
        temp_team_list.append(res_List[r].res_team)
    for n in opSettings.all_acteams:
        res_per_team[n] = temp_team_list.count(n)
        # print(res_per_team[n])

    # Creates the model.
    model = cp_model.CpModel()
    print("Running model for " + str(test_time) + " seconds.")

    # Creates shift variables.
    # shifts[(r, d, t)]: resident 'r' works team 't' on day 'd'.
    shifts = {}
    for n in opSettings.all_res:
        for d in opSettings.all_days:
            for t in opSettings.all_teams:
                shifts[(n, d, t)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, t))

    day_worked = {}
    for n in opSettings.all_res:
        for d in opSettings.all_days:
            day_worked[(n, d)] = model.NewBoolVar('day_worked_n%id%i' % (n, d))
            model.AddMaxEquality(day_worked[n, d], (shifts[(n, d, t)] for t in opSettings.all_teams))

    weekend_shifts = {}
    for n in opSettings.all_res:
        for i in opSettings.all_weeks:
            weekend_range = range(7 * i + 5, 7 * i + 7)
            weekend_shifts[n, i] = model.NewBoolVar('weekend_worked_n%ii%i' % (n, i))
            model.AddMaxEquality(weekend_shifts[n, i], (day_worked[(n, d)] for d in weekend_range))

    fri_combo = {}
    thu_combo = {}
    for n in opSettings.all_res:
        for w in opSettings.all_weeks:
            fri_combo[n, w] = model.NewBoolVar('fri_combo_n%iw%i' % (n, w))
            model.Add(fri_combo[n, w] == day_worked[n, 7 * w + 4]).OnlyEnforceIf(day_worked[n, 7 * w + 6])
            model.Add(fri_combo[n, w] == 0).OnlyEnforceIf(day_worked[n, 7 * w + 6].Not())
            thu_combo[n, w] = model.NewBoolVar('thu_combo_n%iw%i' % (n, w))
            model.Add(thu_combo[n, w] == day_worked[n, 7 * w + 3]).OnlyEnforceIf(weekend_shifts[n, w])
            model.Add(thu_combo[n, w] == 0).OnlyEnforceIf(weekend_shifts[n, w].Not())

    # Add total shifts
    total_shifts = {}
    for n in opSettings.all_res:
        total_shifts[n] = model.NewIntVar(0, opSettings.max_shifts, "total_shifts_n%i" % n)
        model.Add(total_shifts[n] == sum(day_worked[n, d] for d in opSettings.all_days))

    # Residents off work during
    res_dayshift = {}
    for n in opSettings.all_res:
        for d in opSettings.all_days:
            res_dayshift[(n, d)] = model.NewBoolVar("res_off_n%id%i" % (n, d))
            if (d % 7) in range(5, 7) or d in opSettings.stat_days:
                model.Add(res_dayshift[n, d] == 0)
            elif d in res_List[n].official_days or d in res_List[n].requested_days:
                model.Add(res_dayshift[n, d] == 0)
            elif d == 0:
                model.Add(res_dayshift[n, d] == 1)
            elif d > 0:
                model.Add(res_dayshift[n, d] == 1).OnlyEnforceIf(day_worked[n, (d - 1)].Not())
                model.Add(res_dayshift[n, d] == 0).OnlyEnforceIf(day_worked[n, (d - 1)])

    # Call shifts each week
    calls_week = {}
    calls_squared = {}
    for n in opSettings.all_res:
        for w in opSettings.all_weeks:
            calls_week[n, w] = model.NewIntVar(0, 7, "calls_week_n%iw%i" % (n, w))
            calls_squared[n, w] = model.NewIntVar(0, 50, "calls_squared_n%iw%i" % (n, w))
            model.Add(calls_week[n, w] == sum(day_worked[n, d] for d in range(7*w, 7*w+7)))
            model.AddMultiplicationEquality(calls_squared[n, w], [calls_week[n, w], calls_week[n, w]])

    #Call density metric
    call_density = {}
    for n in opSettings.all_res:
        call_density[n] = model.NewIntVar(0, 20, "call_density_n%i" % (n))
        model.Add(call_density[n] == sum(calls_squared[n, w] for w in opSettings.all_weeks))

    #Cross Covering
    cc_active = {}
    cc_gold = {}
    for n in opSettings.all_res:
        for d in opSettings.all_days:
            cc_active[n, d] = model.NewBoolVar('cc_active_n%id%i' % (n, d))
            cc_gold[n, d] = model.NewBoolVar('cc_inactive_n%id%i' % (n, d))

            # Covering active team if sum of all teams - own team(1) and gold = 1.  Covering gold if sum of all teams - all actives = 1
            model.Add(cc_active[n, d] == sum(shifts[n, d, t] for t in opSettings.all_teams) - shifts[n, d, opSettings.gold_team] - 1).OnlyEnforceIf(day_worked[n, d])
            model.Add(cc_gold[n, d] == sum(shifts[n, d, t] for t in opSettings.all_teams) - sum(shifts[n, d, t] for t in opSettings.all_acteams))

    total_cc_active = {}
    total_cc_gold = {}
    for n in opSettings.all_res:
        total_cc_active[n] = model.NewIntVar(0, opSettings.max_shifts, "total_cc_active_n%i" % n)
        total_cc_gold[n] = model.NewIntVar(0, opSettings.max_shifts, "total_cc_gold_n%i" % n)
        model.Add(total_cc_active[n] == sum(cc_active[n, d] for d in opSettings.all_days))
        model.Add(total_cc_gold[n] == sum(cc_gold[n, d] for d in opSettings.all_days))

    # Total number of residents
    num_CTU_res = {}
    for t in opSettings.all_acteams:
        for d in opSettings.all_days:
            num_CTU_res[(t, d)] = model.NewIntVar(0, res_per_team[t], "res_away_t%id%i" % (t, d))
            model.Add(num_CTU_res[t, d] == sum(res_dayshift[n, d] for n in opSettings.all_res if res_List[n].res_team == t))

    shift_missing = {}
    shift_covered = {}
    for d in opSettings.all_days:
        for t in opSettings.all_teams:
            shift_missing[d, t] = model.NewBoolVar('shift_missing_d%i_t%i' % (d, t))
            shift_covered[d, t] = model.NewBoolVar('shift_covered_d%i_t%i' % (d, t))

            model.Add(shift_covered[d, t] == sum(shifts[(n, d, t)] for n in opSettings.all_res))
            model.Add(shift_missing[d, t] == shift_covered[d,t].Not())

    # Rules for Scheduler
    # Rule #1: Each shift is covered by one resident maximum.  Optional coverage in Infeasible Scheduler
    for d in opSettings.all_days:
        for t in opSettings.all_teams:
            model.Add(sum(shifts[(n, d, t)] for n in opSettings.all_res) <= 1)

    # Rule #2: Each res covers at most 2 teams per day.
    for n in opSettings.all_res:
        for d in opSettings.all_days:
            model.Add(sum(shifts[(n, d, t)] for t in opSettings.all_teams) <= 2)

    # Rule #3: Resident should always cover home team each shift.
    for n in opSettings.all_res:
        for d in opSettings.all_days:
            model.Add(shifts[n, d, res_List[n].res_team] == 1).OnlyEnforceIf(day_worked[n, d])

    # Rule #4: No two shifts in a row.
    for n in opSettings.all_res:
        for d in range(opSettings.num_days - 1):
            model.Add((day_worked[n, d] + day_worked[n, d + 1]) <= 1)

    # Rule #5: Total number of days less than sum worked /4
    for n in opSettings.all_res:
        model.Add(total_shifts[n] <= math.floor(res_List[n].days_worked / opSettings.max_freq))

    # Rule #6: Up to 2 shift difference in frequency number of shifts adjusted for days worked
    calls = {}
    callsr = {}
    for n in opSettings.all_res:
        calls[n] = model.NewIntVar(0, opSettings.max_shifts, "calls%i" % n)
        callsr[n] = model.NewIntVar(0, 28 * opSettings.max_shifts, "callsr%i" % n)
        model.Add(callsr[n] == total_shifts[n] * 28)
        model.AddDivisionEquality(calls[n], callsr[n], res_List[n].days_worked)

    min_calls = model.NewIntVar(0, opSettings.max_shifts, 'min_calls')
    max_calls = model.NewIntVar(0, opSettings.max_shifts, 'max_calls')
    model.AddMinEquality(min_calls, (calls[n] for n in opSettings.all_res))
    model.AddMaxEquality(max_calls, (calls[n] for n in opSettings.all_res))
    model.Add(max_calls - min_calls <= 2)

    # Rule #7: Follows rules for 1st day and 1st weekend
    for n in opSettings.all_res:
        if res_List[n].work_day1 is False:
            model.Add(day_worked[n, 0] == 0)
        if res_List[n].work_1we is False:
            model.Add(weekend_shifts[n, 0] == 0)

    # Rule #8: No three weekends in a row
    for n in opSettings.all_res:
        if opSettings.num_days >= 14:
            for i in range(math.floor((opSettings.num_days-14)/7)):
                model.Add((weekend_shifts[n, i] + weekend_shifts[n, i + 1] + weekend_shifts[n, i + 2]) < 3)

    #Rule 9: Off service residents will not cross-cover active CTU team
    for n in opSettings.all_res:
        if res_List[n].is_IM == False:
            for d in opSettings.all_days:
                model.Add((sum(shifts[(n, d, t)] for t in opSettings.all_teams) - shifts[n, d, res_List[n].res_team] - shifts[
                    n, d, 3]) == 0)

    # Rule #10:  Residents cannot cross active teams on weekend
    for n in opSettings.all_res:
        for d in opSettings.all_days:
            if (d % 7 == 5) or (d % 7 == 6) or d in opSettings.stat_days:
                model.Add(sum(shifts[n, d, t] for t in opSettings.all_acteams) < 2)

    # Rule #11: Meet all mandatory requests
    for n in opSettings.all_res:
        for d in res_List[n].official_days:
            model.Add(day_worked[n, d] == 0)

    # # Rule #12: At least two residents per team remaining on team on weekdays and not stat holidays.  Does not apply to InfeasibleScheduler
    # for d in opSettings.all_days:
    #     if (d % 7) in range(0, 5) and d not in opSettings.stat_days:
    #         for t in opSettings.all_acteams:
    #             model.Add(num_CTU_res[t, d] >= 2)

    # Optional Rules
    # Optional #0 (Sort of mandatory): Maximum of 2 residents on weekdays and not stat holidays
    if currentSettings.weekday_max:
        for d in opSettings.all_days:
            if (d % 7) in range(0, 5) and d not in opSettings.stat_days:
                model.Add(sum(day_worked[n, d] for n in opSettings.all_res) <= 2)

    # Optional #1a: Allow all requests days off
    if currentSettings.requests_switch:
        for n in opSettings.all_res:
            for d in res_List[n].requested_days:
                model.Add(day_worked[n, d] == 0)

            # Optional 1b: Allow all specific days for call day
            for d in res_List[n].call_requested:
                model.Add(day_worked[n, d] == 1)

    # Optional #2: No more than 2 weekends on call but at least one
    if currentSettings.max_two_weekends:
        for n in opSettings.all_res:
            if res_List[n].exceptions == "One Weekend":
                model.Add(sum(weekend_shifts[n, i] for i in opSettings.all_weeks) == 1)
            else:
                model.Add(sum(weekend_shifts[n, i] for i in opSettings.all_weeks) < 3)
                model.Add(sum(weekend_shifts[n, i] for i in opSettings.all_weeks) > 0)

    # Optional #3: Off service should not be post-call on academic days
    if currentSettings.academic_switch:
        for n in opSettings.all_res:
            if res_List[n].home_service in currentSettings.academic_days:
                dayOff = currentSettings.academic_days[res_List[n].home_service] - 1
                for d in opSettings.all_days:
                    if d % 7 == dayOff:
                        model.Add(day_worked[n, d] == 0)

    # Option #4: Maximum number of consecutive call
    for n in opSettings.all_res:
        for d in range(opSettings.num_days - 6):
            model.Add(sum(day_worked[n, i] for i in range(d, d+7)) <= currentSettings.max_consec)

    # Comparison Function: Minimize difference in work load
    loadr = {}
    for n in opSettings.all_res:
        loadr[n] = model.NewIntVar(0, 140, "loadr%i" % n)
        model.Add(loadr[n] == sum(day_worked[n, d] * currentSettings.loadConvert[d] for d in opSettings.all_days))

    # Optional adjustments
    if currentSettings.combinations_switch:
        adjustment_days = {}
        for n in opSettings.all_res:
            for w in opSettings.all_weeks:
                adjustment_days[(n, w)] = model.NewIntVar(-20, 20, 'adjustment_days_n%iw%i' % (n, w))
                model.Add(adjustment_days[n, w] == (fri_combo[n, w] * currentSettings.frisun_adjust) + (
                            thu_combo[n, w] * currentSettings.thusat_adjust))

    # For comparison function
    load = {}
    loadc = {}
    for n in opSettings.all_res:
        loadc[n] = model.NewIntVar(0, 3920, "loadc%i" % n)
        model.Add(loadc[n] == 28 * (loadr[n] + sum(adjustment_days[n, w] for w in opSettings.all_weeks)))
        load[n] = model.NewIntVar(0, 400, "load%i" % n)
        model.AddDivisionEquality(load[n], loadc[n], res_List[n].days_worked)

    # Define max and minLoad
    maxLoad = model.NewIntVar(0, 140, "maxLoad")
    minLoad = model.NewIntVar(0, 140, "minLoad")
    model.AddMaxEquality(maxLoad, ((load[n]) for n in opSettings.all_res))
    model.AddMinEquality(minLoad, ((load[n]) for n in opSettings.all_res))
    model.Add((maxLoad - minLoad) <= currentSettings.max_load_diff)

    # New comparison function
    scheduleMetric = model.NewIntVar(-5000, 5000, "scheduleMetric")
    averageLoad = model.NewIntVar(0, 140, "averageLoad")
    comboScore = model.NewIntVar(-500, 500, "tComboScore")
    flyins = model.NewIntVar(0, 200, "flyins")

    # Calculate averageLoad per resident
    totalLoad = model.NewIntVar(0, 140 * opSettings.num_res, "totalLoad")
    model.Add(totalLoad == sum(load[n] for n in opSettings.all_res))
    model.AddDivisionEquality(averageLoad, totalLoad, opSettings.num_res)

    # Decrease call density for residents
    avgDensity = model.NewIntVar(0, 20, "avgDensity")
    totalDensity = model.NewIntVar(0, 20 * opSettings.num_res, "totalDensity")
    model.Add(totalDensity == sum(call_density[n] for n in opSettings.all_res))
    model.AddDivisionEquality(avgDensity, totalDensity, opSettings.num_res)

    # Reduce off-service.  Current logic is to minimize differences in cross covering in IM residents and off-service residents
    # Adjust total cc_score based on number of days resident worked
    total_cc_score = {}
    temp_sum_score = {}
    for n in opSettings.all_res:
        total_cc_score[n] = model.NewIntVar(0, 4*opSettings.max_shifts, "cc_score%i" % n)
        temp_sum_score[n] = model.NewIntVar(0, 28*2*opSettings.max_shifts, "max_cc%i" % n)
        model.Add(temp_sum_score[n] == 28*((2*total_cc_active[n]) + total_cc_gold[n]))
        model.AddDivisionEquality(total_cc_score[n], temp_sum_score[n], res_List[n].days_worked)

    maxScoreIM = model.NewIntVar(0, 2*opSettings.max_shifts, "maxIM")
    minScoreIM = model.NewIntVar(0, 2*opSettings.max_shifts, "minIM")
    model.AddMaxEquality(maxScoreIM, ((total_cc_score[n]) for n in opSettings.all_res if res_List[n].is_IM))
    model.AddMinEquality(minScoreIM, ((total_cc_score[n]) for n in opSettings.all_res if res_List[n].is_IM))

    maxScoreOS = model.NewIntVar(0, 2*opSettings.max_shifts, "maxOS")
    minScoreOS = model.NewIntVar(0, 2*opSettings.max_shifts, "minOS")
    model.AddMaxEquality(maxScoreOS, ((total_cc_score[n]) for n in opSettings.all_res if not res_List[n].is_IM))
    model.AddMinEquality(minScoreOS, ((total_cc_score[n]) for n in opSettings.all_res if not res_List[n].is_IM))

    scoreAdjust = model.NewIntVar(0, 2*opSettings.max_shifts, "scoreAdjust")
    model.Add(scoreAdjust == maxScoreIM + maxScoreOS - minScoreIM - minScoreOS)

    #Calculate adjusted score for fly-ins
    all_sat = []
    for d in opSettings.all_days:
        if d % 7 == 5:
            all_sat.append(d)

    model.Add(flyins == 10 * sum(shift_missing[d, t] for d in opSettings.all_days for t in opSettings.all_teams) -
              5 * sum(shift_missing[d, t] for d in all_sat for t in opSettings.all_teams))

    # Calculate comboScore from Thu and Fri Combinations
    model.Add(comboScore == 2 * sum(thu_combo[n, w] for n in opSettings.all_res for w in opSettings.all_weeks) -
              sum(fri_combo[n, w] for n in opSettings.all_res for w in opSettings.all_weeks))
    model.Add(scheduleMetric == 2*(flyins + averageLoad + comboScore) + avgDensity + scoreAdjust)
    model.Minimize(scheduleMetric)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = test_time
    status = solver.Solve(model)

    print(solver.StatusName(status))
    print("Time spent is", solver.WallTime())
    print("Number of solutions checked is: ", solver.NumBranches())

    outputData = xlwt.Workbook()
    ws = outputData.add_sheet("Schedule")

    # Define bold text
    bold = xlwt.XFStyle()
    font_bold = xlwt.Font()
    font_bold.bold = True
    bold.font = font_bold

    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'D-MMM'

    ws.write(0, 0, "Nonoptimal Schedule", bold)
    ws.write(1, 0, "Day", bold)
    ws.write(1, 1, "Date", bold)
    ws.write(1, 2, "Weekday", bold)
    ws.write(1, 3, "Blue Team", bold)
    ws.write(1, 4, "Red Team", bold)
    ws.write(1, 5, "Silver Team", bold)
    ws.write(1, 6, "Gold Team", bold)

    for d in opSettings.all_days:
        r = d + 2
        ws.write(r, 0, d + 1)
        ws.write(r, 1, Convert_Date.Convert_from_N(d, currentSettings), date_format)
        ws.write(r, 2, Convert_Date.Convert_from_N(d, currentSettings).strftime('%A'))
        for t in opSettings.all_teams:
            for n in opSettings.all_res:
                if solver.Value(shifts[n, d, t]) == 1:
                    ws.write(r, t + 3, res_List[n].res_name)
    # Search results
    ws.write(5 + opSettings.num_days, 0, "Output Parameters", bold)
    ws.write(6 + opSettings.num_days, 0, "Objective value" + str(solver.ObjectiveValue()))
    ws.write(7 + opSettings.num_days, 0, "Maximum load:" + str(solver.Value(maxLoad)))
    ws.write(8 + opSettings.num_days, 0, "Minimum load:" + str(solver.Value(minLoad)))
    ws.write(9 + opSettings.num_days, 0, "Number of Fly-ins:" + str(solver.Value(
        sum(shift_missing[d, t] for d in opSettings.all_days for t in opSettings.all_teams))))
    ws.write(10 + opSettings.num_days, 0, "Average density: " + str(solver.Value(avgDensity)))
    ws.write(11 + opSettings.num_days, 0, "Adjusted CC score: " + str(solver.Value(scoreAdjust)))

    # Each resident stats
    ws.write(13 + opSettings.num_days, 0, "Resident Stats", bold)
    x = 14 + opSettings.num_days
    ws.write(x, 0, "Resident Name", bold)
    ws.write(x, 1, "Resident Team", bold)
    ws.write(x, 2, "Resident Days Worked", bold)
    ws.write(x, 3, "Resident Weekend Shifts", bold)
    ws.write(x, 4, "Resident Raw Load", bold)
    ws.write(x, 5, "Resident Corrected Load", bold)
    ws.write(x, 6, "Resident Load", bold)
    ws.write(x, 7, "Combination Days", bold)
    ws.write(x, 8, "Shifts per week", bold)
    ws.write(x, 9, "Call density", bold)
    ws.write(x, 10, "CC Score", bold)

    for n in opSettings.all_res:
        r = n + x + 1
        ws.write(r, 0, res_List[n].res_name, bold)
        ws.write(r, 1, Read_File.teamConvert[res_List[n].res_team])
        ws.write(r, 2, solver.Value(total_shifts[n]))
        ws.write(r, 3, sum(solver.Value(weekend_shifts[n, i]) for i in opSettings.all_weeks))
        ws.write(r, 4, solver.Value(loadr[n]))
        ws.write(r, 5, solver.Value(loadc[n]))
        ws.write(r, 6, solver.Value(load[n]))
        ws.write(r, 7, sum(solver.Value(adjustment_days[n,w]) for w in opSettings.all_weeks))
        callweekstr = ""
        for w in opSettings.all_weeks:
            callweekstr = callweekstr + str(solver.Value(calls_week[n, w])) + ", "
        ws.write(r, 8, callweekstr)
        ws.write(r, 9, solver.Value(call_density[n]))
        ws.write(r, 10, solver.Value(total_cc_score[n]))

    # Save to file
    outputData.save(path + "Output.xls")
