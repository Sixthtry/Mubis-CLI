#!/bin/python3.6

# to-do
# Sorting for days and lessons

import getpass
import requests
import codecs
import dateutil.parser as dparse
import json
import calendar
import argparse
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import time
from mubis import tarih_saturday as satu
from mubis import tarih_monday as mond

user_sessions = 'http://mubistip.maltepe.edu.tr/user_sessions'
parser = argparse.ArgumentParser()
nexti = parser.add_argument('-n', '--next', action='store_true', 
        help='Show the next week\'s program.', dest="nexti")
prev = parser.add_argument('-p', '--previous', action='store_true', 
        help='Show previous week\'s program.', dest="prev")
args = parser.parse_args()
if args.nexti:
    fname = "takvim_next.json"
elif args.prev:
    fname = "takvim_prev.json"
else:
    fname = "takvim.json"

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
    localdate = datetime.today()

    gun_programi = []

    for entry in jbuff:
        ders_start = entry['start'].split("+")[0]
        ders_end = entry['end'].split("+")[0]
        ders_start_ = dparse.parse(ders_start)
        ders_end_ = dparse.parse(ders_end)

        if ders_start_ < localdate or ders_end_ > localdate:
            gun_programi.append(entry)
        else:
            print("No ders today.")
    return gun_programi

def outputing(gun_programi):

    for entry in gun_programi:
        ders = entry['title'] 
        # Parse, JSON'daki tarihi düzgün göstermeye yarıyor.
        _date=dparse.parse(entry['start'].split("T")[0]).date() 
        # Split(T)[0], Zaman bilgisindeki tarih kısmını alıyor
        _end_h=dparse.parse(entry['end'].split("+")[0]).time().strftime("%H:%M")       
        # date() eklendi çünkü parse datetime objesi oluşturuyor ve saatleri 0 yapıyor.
        _start_h = dparse.parse(entry['start'].split("+")[0]).time().strftime("%H:%M")
        # Split(+)[0], Zaman ve tarih bilgisini direk alıyor.
        _date_int = calendar.day_name[_date.weekday()]
        print("{0}-{1}\n{2}-{3}:{4}".format(_date,_date_int,_start_h,_end_h,ders))
with requests.Session() as s:
    payload = usr_inf()
    p = s.post(user_sessions, data=payload)
    if p.url == user_sessions:
        print("MUBIS ÇÖKMÜŞ. BİR ÖNCEKİ OTURUMDAKİ AJANDA GÖSTERİLİYOR.\n")
        jfile = codecs.open("takvim.json", mode="r", encoding="utf-8")
        outputing(listing(jfile))
    else:
        print("Oturum açıldı.")
        url = url_prep()
        _json_buff = s.get(url)
        wrtefile(_json_buff.text)
        print("Yedek alındı.")
        jfile = codecs.open(fname, mode="r", encoding="utf-8")
        outputing(listing(jfile))
        #jfile = codecs.open("takvim.json", mode="r", encoding="utf-8")
        #outputing(listing(jfile))


