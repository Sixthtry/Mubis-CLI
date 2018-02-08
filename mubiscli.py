#!/bin/python3.6

# to-do
# Saate göre sıralama!

import getpass
import requests
import codecs
import dateutil.parser as dparse
import json
import calendar
import argparse
import sys
import time
import os
from bs4 import BeautifulSoup
from datetime import datetime


user_sessions = 'http://mubistip.maltepe.edu.tr/user_sessions'

parser = argparse.ArgumentParser()
nexti = parser.add_argument('-n', '--next', action='store_true', 
        help='Show the next week\'s program.', dest="nexti")
prev = parser.add_argument('-p', '--previous', action='store_true', 
        help='Show previous week\'s program.', dest="prev")
args = parser.parse_args()

if args.nexti:
    fname = ".takvim_next.json"
elif args.prev:
    fname = ".takvim_prev.json"
else:
    fname = ".takvim.json"
fname = os.path.join(os.path.expandvars("$HOME"),fname)

def mond():
    gunFarki_monday = (datetime
            .isoweekday(datetime.now())-1)
    monday=(int(datetime.now()
        .strftime("%d")) - gunFarki_monday)
    current_month = datetime.now().month
    current_year = datetime.now().year
    mon_ = datetime(current_year,current_month,
            monday,0,0,0,0).timetuple()
    mon__ = int(time.mktime(mon_))
    return mon__

def satu():
    gunFarki_saturday = (datetime
            .isoweekday(datetime.now())-6)
    saturday = (int(datetime.now()
        .strftime("%d")) - gunFarki_saturday)
    current_month = datetime.now().month
    current_year = datetime.now().year
    sat_ = datetime(current_year,current_month,
            saturday,0,0,0,0).timetuple()
    sat__ = int(time.mktime(sat_))
    return sat__

def html_parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    ogrenci_no = soup.find("td").find("input")["title"].split("/")[3]
    return ogrenci_no

def usr_inf():
    okul_no = input("Okul Numarası: ")
    passw = getpass.getpass()
    payload = {
            "user_session[login]" : okul_no,
            "user_session[password]" : passw,
            "authenticity_token" : "3s5T/B0TpuFuwNFwNrqsDIqwW3FnA6lb4Z6/3FXb6B4=",
            "utf8" : "✓",
            "commit" : "Giriş Yap"
            }
    return payload

def url_prep():
    st_num = html_parse(p.text)
    _url = 'http://mubistip.maltepe.edu.tr/ajanda/ogrenci_event_list.json?ogrenci='
    start = mond()
    end = satu()
    if args.nexti:
        # 604800 = Epoch değerinde 1 hafta
        start = (start + 604800)
        end = (end + 604800)
    elif args.prev:
        start = (start - 604800)
        end = (end - 604800)
    url = '{0}{1}&start={2}&end={3}'.format(_url ,st_num, start, end)
    return url 

def wrtefile(buff):
    jfilew = open(fname, "w")
    jfilew.write(buff)
    jfilew.close()
    return 0

def listing(jfile):
    jbuff = json.load(jfile)
    
    gun_programi = []
    mon=[]
    tue=[]
    wed=[]
    thu=[]
    fri=[]
    for entry in jbuff:
        _ders_gunu = datetime.isoweekday(dparse.
               parse(entry['start'].split("T")[0].split("-")[2]))
        if _ders_gunu == 1:
            mon.append(entry)
        elif _ders_gunu == 2:
            tue.append(entry)
        elif _ders_gunu == 3:
            wed.append(entry)
        elif _ders_gunu == 4:
            thu.append(entry)
        else:
            fri.append(entry)

    gun_programi.append(list(mon))
    gun_programi.append(list(tue))
    gun_programi.append(list(wed))
    gun_programi.append(list(thu))
    gun_programi.append(list(fri))
    
    return gun_programi

def outputing(gun_programi):
    for dumpy in gun_programi:
        for entry in dumpy:
            ders = entry['title'] 
        # Parse, JSON'daki tarihi düzgün göstermeye yarıyor.
            _date=dparse.parse(entry['start'].split("T")[0]).date()
        # Split(T)[0], Zaman bilgisindeki tarih kısmını alıyor
            _end_h=dparse.parse(entry['end'].split("+")[0]).time().strftime("%H:%M")       
        # date() eklendi çünkü parse datetime objesi oluşturuyor ve saatleri 0 yapıyor.
            _start_h = dparse.parse(entry['start']
                   .split("+")[0]).time().strftime("%H:%M")
        # Split(+)[0], Zaman ve tarih bilgisini direk alıyor.
            _date_int = calendar.day_name[_date.weekday()]
            print("{0}-{1}\n{2}-{3}:{4}".format(_date,_date_int,_start_h,_end_h,ders))
        print('\n')
try:
    with requests.Session() as s:
        payload = usr_inf()
        p = s.post(user_sessions, data=payload)
        if p.url == user_sessions:
            print("MUBIS çalışmıyor. Kaydedilmiş program açılıyor.\n")
            jfile = codecs.open(fname, mode="r", encoding="utf-8")
            outputing(listing(jfile))
        else:
            print("Oturum açıldı.")
            url = url_prep()
            _json_buff = s.get(url)
            wrtefile(_json_buff.text)
            print("Yedek alındı.\n")
            jfile = codecs.open(fname, mode="r", encoding="utf-8")
            outputing(listing(jfile))

except requests.exceptions.RequestException as exc:
    print("Bağlantı problemi:", exc)
    print("Kaydedilmiş ders programı açılıyor.\n")
    jfile = codecs.open(fname, mode="r", encoding="utf-8")
    outputing(listing(jfile))
