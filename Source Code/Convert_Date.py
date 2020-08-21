import datetime

def delete_null (array):
    while ' ' in array:
        array.remove(' ')
    while '' in array:
        array.remove('')
    return array

def Convert_from_N (n, settings):
    calcDate = settings.first_Date + datetime.timedelta(days=n)
    return calcDate

def Convert_from_Date(date, settings):
    calcN = (date - settings.first_Date).days
    return calcN

def Convert_from_String (DateString, settings):
     DateS = DateString + " " + str(settings.first_Date.year)
     Date = datetime.datetime.strptime(DateS, '%b %d %Y')
     # print(Date)
     return Date

def convertDate (dateArray, settings):
    dates = delete_null(dateArray)
    datesN = []
    for n in range(len(dates)):
        # print (dates[n])
        dates[n] = Convert_from_String(str(dates[n]), settings)
        datesN.append(Convert_from_Date(dates[n], settings))
    return datesN
