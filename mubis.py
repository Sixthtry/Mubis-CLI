import time
import datetime

def tarih_monday():
    gunFarki_monday = (datetime.datetime.isoweekday(datetime.datetime.now())-1)
    monday=(int(datetime.datetime.now().strftime("%d")) - gunFarki_monday)
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    mon_ = datetime.datetime(current_year,current_month,monday,0,0,0,0).timetuple()
    mon__ = int(time.mktime(mon_))
    return mon__

def tarih_saturday():
    gunFarki_saturday = (datetime.datetime.isoweekday(datetime.datetime.now())-6)
    saturday = (int(datetime.datetime.now().strftime("%d")) - gunFarki_saturday)
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year
    sat_ = datetime.datetime(current_year,current_month,saturday,0,0,0,0).timetuple()
    sat__ = int(time.mktime(sat_))
    return sat__

