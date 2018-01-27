#!/bin/python3.6

import getpass
import requests
import codecs
import dateutil.parser as dparse
import json
from datetime import datetime
from mubis import tarih_saturday as satu
from mubis import tarih_monday as mond

user_sessions = 'http://mubistip.maltepe.edu.tr/user_sessions'

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

def wrtefile(buff):
    jfilew = open("takvim.json", "w")
    jfilew.write(buff)
    jfilew.close()
    return 0

def readfile(jfile):
    buff = jfile.read()
    jfile.close()
    return buff

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
        start = dparse.parse(entry['start'].split("+")[0])
        end =dparse.parse(entry['end'].split("+")[0])
        print("{0} - {1}\n\t{2}".format(start, end, ders))


with requests.Session() as s:
    payload = usr_inf()
    p = s.post(user_sessions, data=payload)
    if p.url == user_sessions:
        print("MUBIS ÇÖKMÜŞ. BİR ÖNCEKİ OTURUMDAKİ AJANDA GÖSTERİLİYOR.\n")
        jfile = codecs.open("takvim.json", mode="r", encoding="utf-8")
        outputing(listing(jfile))
    else:
        print("Oturum açıldı.")
        _url = 'http://mubistip.maltepe.edu.tr/ajanda/ogrenci_event_list.json?ogrenci=16868'
        start = mond()
        end = satu()
        url = '{0}&start={1}&end={2}'.format(_url, start, end)
        _json_buf = s.get(url)
        resp = wrtefile(_json_buf.text)
        if resp == 0:
            print("Dosyaya yazıldı.")
        else:
            print("Bir problem var. Dosyaya yazılamadı.")
        jfile = codecs.open("takvim.json", mode="r", encoding="utf-8")
        outputing(listing(jfile))
