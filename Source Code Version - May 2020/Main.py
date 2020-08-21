import Scheduler
import Read_File
import Diagnostics
import Read_Settings
import calcSettings
from ortools.sat.python import cp_model
import InfeasibleScheduler

def main(path):
    # Read excel files

    filepath = path + ".xlsx"
    currentSettings = Read_Settings.Read_Settings(filepath)
    res_List = Read_File.Read_File(filepath, currentSettings)
    opSettings = calcSettings.calcSettings(currentSettings, res_List)

    feasible = Diagnostics.diagnostics(currentSettings, res_List, opSettings, path)
    if feasible:
        Scheduler.scheduler(currentSettings, res_List, opSettings, currentSettings.test_time, path, False)
    else:
        InfeasibleScheduler.infeasibleScheduler(currentSettings, res_List, opSettings, currentSettings.test_time, path)

if __name__ == '__main__':
    path = input("Please enter input file name: ")
    main(path)
