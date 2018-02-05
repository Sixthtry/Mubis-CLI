#!/bin/python3.6

from bs4 import BeautifulSoup

def html_parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    p = soup.find("td").find("input")["title"]
    p = p.split("/")[3]
    print(p)

hfile = open("html.html", "r").read()
html_parse(hfile)
