#!/usr/bin/python
import sqlite3 as sql
import sys
import operator
import re
import cgi
import time
import csv
from collections import OrderedDict

#Global Variables
tablename = "SANS575_index"
index = []


#Reads the CVS file into Index List
filename = sys.argv[1]
with open(filename, 'rU') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            t = row['Title']
            index.append([cgi.escape(row['Title'].upper()), row['Book'], row['Page'], row['Description']])        
        except:
            pass

#Sorts Index
index = sorted(index, key=operator.itemgetter(0))

#Prints Index
pos = 0
for item in index:
    key = item[0].strip('"').rstrip('"')

    #Create Section Header
    if key.startswith("A") or key.startswith("a"):
        if pos != 1:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Aa</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 1
    elif key.startswith("B") or key.startswith("b"):
        if pos != 2:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Bb</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"

            pos = 2
    elif key.startswith("C") or key.startswith("c"):
        if pos != 3:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Cc</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 3
    elif key.startswith("D") or key.startswith("d"):
        if pos != 4:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Dd</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 4
    elif key.startswith("E") or key.startswith("e"):
        if pos != 5:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Ee</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 5
    elif key.startswith("F") or key.startswith("f"):
        if pos != 6:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Ff</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 6
    elif key.startswith("G") or key.startswith("g"):
        if pos != 7:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Gg</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 7
    elif key.startswith("H") or key.startswith("h"):
        if pos != 8:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Hh</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 8
    elif key.startswith("I") or key.startswith("i"):
        if pos != 9:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Ii</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 9
    elif key.startswith("J") or key.startswith("j"):
        if pos != 10:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Jj</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 10
    elif key.startswith("K") or key.startswith("k"):
        if pos != 11:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Kk</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 11
    elif key.startswith("L") or key.startswith("l"):
        if pos != 12:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Ll</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 12
    elif key.startswith("M") or key.startswith("m"):
        if pos != 13:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Mm</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 13
    elif key.startswith("N") or key.startswith("n"):
        if pos != 14:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Nn</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 14
    elif key.startswith("O") or key.startswith("o"):
        if pos != 15:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Oo</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 15
    elif key.startswith("P") or key.startswith("p"):
        if pos != 16:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Pp</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 16
    elif key.startswith("Q") or key.startswith("q"):
        if pos != 17:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Qq</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 17
    elif key.startswith("R") or key.startswith("r"):
        if pos != 18:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Rr</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 18
    elif key.startswith("S") or key.startswith("s"):
        if pos != 19:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Ss</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 19
    elif key.startswith("T") or key.startswith("t"):
        if pos != 20:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Tt</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 20
    elif key.startswith("U") or key.startswith("u"):
        if pos != 21:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Uu</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 21
    elif key.startswith("V") or key.startswith("v"):
        if pos != 22:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Vv</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 22
    elif key.startswith("W") or key.startswith("w"):
        if pos != 23:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Ww</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 23
    elif key.startswith("X") or key.startswith("x"):
        if pos != 24:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Xx</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 24
    elif key.startswith("Y") or key.startswith("y"):
        if pos != 25:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Yy</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 25
    elif key.startswith("Z") or key.startswith("z"):
        if pos != 26:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Zz</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 26
    else:
        if pos != 27:
            print "<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;color:black'>Numbers & Special Characters</span></b></span><span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
            pos = 27

#Print Details
    if item[0] != "":
        print "<span class=topic><b><span style='color:blue'>"
        print " %s " % (item[0])
        print "</span></b></span><span style='color:black'>&nbsp;"
        print "<br><i>{b-%s / p-%s}</i><br>%s<br></span>" % (item[1], item[2], item[3])