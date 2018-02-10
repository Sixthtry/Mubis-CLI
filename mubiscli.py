#!/bin/python3.6

# to-do
# Error checking
# --> if there is no internet and no file


import getpass                      # Parola görünmez oluyor
import requests
import codecs                       # encoding="utf-8" desteği
import dateutil.parser as dparse
import time
import json
import calendar
import argparse
import os                           # $HOME path'i için
from bs4 import BeautifulSoup
from datetime import datetime


user_sessions = 'http://mubistip.maltepe.edu.tr/user_sessions'

parser = argparse.ArgumentParser()
nexti = parser.add_argument('-n', '--next', action='store_true', 
        help='Show the next week\'s program.', dest="nexti")
prev = parser.add_argument('-p', '--previous', action='store_true', 
        help='Show previous week\'s program.', dest="prev")
cach = parser.add_argument('-c', '--cache', action='store_true',
        help='Show the cached calendar.', dest='cach')
args = parser.parse_args()

# Argümana göre dosya adı belirlenmesi
if args.nexti:
    fname = ".takvim_next.json"
elif args.prev:
    fname = ".takvim_prev.json"
else:
    fname = ".takvim.json"
fname = os.path.join(os.path.expandvars("$HOME"),fname)

# Pazartesi ve Cumartesi 00:00 zamanı
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

# POST içeriğindeki öğrenci numarası
def html_parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    ogrenci_no = soup.find("td").find("input")["title"].split("/")[3]
    return ogrenci_no


# MUBIS'e giriş bilgileri
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

# Takvimi almak için gönderilen POST paketini oluşturma
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

# Takvimi dosyaya yazma
def wrtefile(buff):
    jfilew = open(fname, "w")
    jfilew.write(buff)
    jfilew.close()
    return 0

# Takvim sıralamasının düzenlenmesi
def listing(jfile):
    jbuff = json.load(jfile) #object_pairs_hook=collections.OrderedDict)
    
    # Gün bazlı ayırma için listeler
    gun_programi, mon, tue, wed, thu, fri= ([] for q in range(6))
    
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
    
    if mon:
        gun_programi.append(list(mon))
    if tue:
        gun_programi.append(list(tue))
    if wed:
        gun_programi.append(list(wed))
    if thu:
        gun_programi.append(list(thu))
    if fri:
        gun_programi.append(list(fri))
   

    # I did not understand anything in here but it works...
    for liste in gun_programi:
        for mem in liste:
            liste.sort(key=lambda mem:mem['start'])

    return gun_programi

# Takvimi output ederkenki düzenin belirlenmesi
def outputing(gun_programi):
    for gun in gun_programi:
        _date=dparse.parse(gun[0]['start'].split("T")[0]).date()
        _date_int = calendar.day_name[_date.weekday()]
        print("---------------------------")
        print(_date,"-",_date_int)
        for entry in gun:
            ders = entry['title'] 
            _end_h=dparse.parse(entry['end']
                    .split("+")[0]).time().strftime("%H:%M")       
            _start_h = dparse.parse(entry['start']
                   .split("+")[0]).time().strftime("%H:%M")
            print("{}-{}:{}".format(_start_h, _end_h, ders))
        print("---------------------------")
        print("\n")
if not args.cach:
    try:
        with requests.Session() as s:
            payload = usr_inf()
            p = s.post(user_sessions, data=payload)
            if p.url == user_sessions:
                print("MUBIS çalışmıyor. Kaydedilmiş program açılıyor.\n")
                jfile = codecs.open(fname, mode="r", encoding="utf-8")
                outputing(listing(jfile))
                jfile.close()
            else:
                print("Oturum açıldı.")
                url = url_prep()
                _json_buff = s.get(url)
                wrtefile(_json_buff.text)
                print("Yedek alındı.\n")
                jfile = codecs.open(fname, mode="r", encoding="utf-8")
                outputing(listing(jfile))
                jfile.close()
    except requests.exceptions.RequestException as exc:
        print("Bağlantı problemi:", exc)
        print("Kaydedilmiş ders programı açılıyor.\n")
        jfile = codecs.open(fname, mode="r", encoding="utf-8")
        outputing(listing(jfile))
        jfile.close()
else:
    print("Kaydedilmiş ders programı açılıyor.\n")
    jfile = codecs.open(fname, mode="r", encoding="utf-8")
    outputing(listing(jfile))
    jfile.close()

