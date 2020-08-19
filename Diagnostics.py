from ortools.sat.python import cp_model
import Scheduler
import Convert_Date
import xlwt
import Read_File

def diagnostics(currentSettings, res_List, opSettings, path):

    print("Running some basic statistics on output")
    diagnosticResults = Scheduler.scheduler(currentSettings, res_List, opSettings, 30, path, True)
    status = diagnosticResults[0]
    res_available = diagnosticResults[1]
    num_available = diagnosticResults[2]

    dxData = xlwt.Workbook()
    ws = dxData.add_sheet("Diagnostic Data")

    # Define bold text
    bold = xlwt.XFStyle()
    font_bold = xlwt.Font()
    font_bold.bold = True
    bold.font = font_bold

    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'D-MMM'

    ws.write(0, 0, "Diagnostic Data based on Input", bold)
    ws.write(1, 0, "Day", bold)
    ws.write(1, 1, "Date", bold)
    ws.write(1, 2, "Weekday", bold)
    ws.write(1, 3, "Blue Team Total Day Residents", bold)
    ws.write(1, 4, "Red Team Total Day Residents", bold)
    ws.write(1, 5, "Silver Team Total Day Residents", bold)

    # Overall team availability
    for d in opSettings.all_days:
        r1 = d + 2
        ws.write(r1, 0, d + 1)
        ws.write(r1, 1, Convert_Date.Convert_from_N(d, currentSettings), date_format)
        ws.write(r1, 2, Convert_Date.Convert_from_N(d, currentSettings).strftime('%A'))
        for t in opSettings.all_acteams:
            ws.write(r1, t + 3, num_available[t, d])

    # Individual Resident Availability Description
    r2 = r1 + 2
    ws.write(r2, 0, "Individual Resident Availability", bold)
    ws.write(r2 + 1, 0, "Day", bold)
    ws.write(r2 + 1, 1, "Date", bold)
    ws.write(r2 + 1, 2, "Weekday", bold)
    for n in opSettings.all_res:
        ws.write(r2+1, n+3, res_List[n].res_name)
        ws.write(r2+2, n+3, Read_File.teamConvert[res_List[n].res_team])

    for d in opSettings.all_days:
        r3 = r2 + 3 + d
        ws.write(r3, 0, d + 1)
        ws.write(r3, 1, Convert_Date.Convert_from_N(d, currentSettings), date_format)
        ws.write(r3, 2, Convert_Date.Convert_from_N(d, currentSettings).strftime('%A'))
        for n in opSettings.all_res:
            ws.write(r3, n+3, res_available[n, d])

    r4 = r3 + 2
    #Final Result Description
    ws.write(r4, 0, "Final result of diagnostic tests", bold)
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        ws.write(r4 + 1, 0, "Schedule feasible - Will run default scheduler")
    else:
        ws.write(r4 + 1, 0, "Schedule infeasible - Will run backup scheduler")

    # Save to file
    dxData.save(path + " Diagnostics.xls")

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Schedule is feasible without fly-ins and without breaking contract rules")
        return True
    else:
        print("Schedule is not feasible without fly-ins and obeying contract rules")
        return False
