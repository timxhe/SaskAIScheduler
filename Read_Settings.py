import xlrd
import Settings as set
import datetime

#Read Excel File and import object Settings

def Read_Settings(fileLoc):
    loc = fileLoc
    # Open the workbook
    data = xlrd.open_workbook(loc)
    inputData = data.sheet_by_name("Settings")

    num_days = int(inputData.cell_value(2, 1))
    num_teams = int(inputData.cell_value(3, 1))
    max_freq = int(inputData.cell_value(4, 1))
    test_time = int(inputData.cell_value(5, 1))

    first_Date = xlrd.xldate_as_datetime(inputData.cell_value(7, 1), data.datemode)
    last_Date = xlrd.xldate_as_datetime(inputData.cell_value(8, 1), data.datemode)
    if (((last_Date - first_Date).days + 1) != num_days):
        print("Number of Days not equal to duration of input.")

    frisun_adjust = int(inputData.cell_value(9,1))
    thusat_adjust = int(inputData.cell_value(10,1))
    total_specialities = int(inputData.cell_value(11, 1))
    academic_days = {}
    for n in range(total_specialities):
        academic_days[inputData.cell_value(8+n, 4)] = inputData.cell_value(8+n, 5)

    # Read LoadConvert table
    indent = 17
    stat_holidays = inputData.cell_value(14, 1).split(";")
    loadTable = []
    for x in range(num_days):
        # Adjusted for first ten rows
        loadTable.append(int(inputData.cell_value(x+indent, 1)))
        # print (inputData.cell_value(x+indent, 1))

    indent2 = indent + num_days + 2
    combinations_switch = inputData.cell_value(indent2, 1)
    requests_switch = inputData.cell_value(indent2+1, 1)
    max_two_weekends = inputData.cell_value(indent2+2, 1)
    # print((inputData.cell_value(indent2+2, 1)))
    academic_switch = inputData.cell_value(indent2+3, 1)

    weekday_max = inputData.cell_value(indent2+4, 1)
    max_load_diff = int(inputData.cell_value(indent2+5, 1))
    max_consec = int(inputData.cell_value(indent2+6, 1))

    inputSettings = set.Settings(loadTable, num_days, num_teams, max_freq, test_time, first_Date, last_Date, thusat_adjust, frisun_adjust, academic_days, stat_holidays, combinations_switch, requests_switch, max_two_weekends, academic_switch, weekday_max, max_load_diff, max_consec)

    # print (academic_days, first_Date, loadTable)

    return inputSettings

# Read_Settings("Block8.xlsx")