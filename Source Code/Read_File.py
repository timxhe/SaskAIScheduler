import xlrd
import Resident as res
import Read_Settings
import datetime
import Convert_Date

teamConvert = {
    "Blue": 0,
    "Red": 1,
    "Silver": 2,
    "Gold": 3,
    0: "Blue",
    1: "Red",
    2: "Silver",
    3: "Gold"
}

boolConvert = {
    "Yes": True,
    "No": False
}
resident_List = []

#Read Excel File and crete list of residents with attributes
def Read_File(fileLoc, settings):
    loc = fileLoc
    currentSettings = settings

    # Open the workbook
    data = xlrd.open_workbook(loc)
 #   settings = data.sheet_by_name("Settings")
    inputData = data.sheet_by_name("Input")

    num_res = inputData.nrows - 2
    # print (inputData.nrows)

    for x in range(num_res):
        # Adjusted for first two rows
        row_number = x + 2

        # Convert ID, name and days away
        temp_id = int(inputData.cell_value(row_number, 0))
        temp_name = inputData.cell_value(row_number, 1)
        temp_official_days = Convert_Date.convertDate(inputData.cell_value(row_number, 2).split(";"), currentSettings)
        temp_requested_days = Convert_Date.convertDate(inputData.cell_value(row_number, 3).split(";"), currentSettings)
        temp_home_service = inputData.cell_value(row_number, 6)
        temp_call_requested = Convert_Date.convertDate(inputData.cell_value(row_number, 9).split(";"), currentSettings)
        temp_exceptions = inputData.cell_value(row_number, 10)

        #Total Days off to Calc Days Worked
        temp_days_off = int(inputData.cell_value(row_number, 4))

        # Convert team to team ID
        temp_res_team = int(teamConvert[inputData.cell_value(row_number, 5)])

        # Convert data to boolean variables
        temp_work_1we = boolConvert[inputData.cell_value(row_number, 7)]
        temp_work_day1 = boolConvert[inputData.cell_value(row_number, 8)]

        #print(temp_id, temp_name, temp_official_days, temp_requested_days, temp_res_team, temp_is_IM, temp_work_1we, temp_work_day1)
        resident_List.append(res.Resident(temp_id, temp_name, temp_official_days, temp_requested_days, temp_days_off, temp_res_team, temp_home_service, temp_work_1we, temp_work_day1, temp_call_requested, temp_exceptions))

    return resident_List

# settings = Read_Settings.Read_Settings("Block8.xlsx")
# Read_File("Block8.xlsx", settings)