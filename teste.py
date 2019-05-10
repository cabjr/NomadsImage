#!/usr/bin/python3
# linha para adicionar ao crontab:
# * */4 * * * /usr/bin/python3 ./diretorio/teste.py
# adicionar a linha acima no crontab por meio do comando: crontab -e
import datetime
from datetime import timedelta
from requests import get
#import psycopg2
import os
import glob


dirSave = "/home/"
hr = ""
now = datetime.date.today()
date = str(datetime.date.today().year) + str(datetime.date.today().month).zfill(2) + str(datetime.date.today().day).zfill(2)
print (date)
# INFOS BD
mhost = ""
db = ""
usr = ""
pwd = ""

if ( datetime.datetime.now() >= datetime.datetime(now.year, now.month, now.day, 13, 15) and datetime.datetime.now() < datetime.datetime(now.year, now.month, now.day, 19, 15)):
    hr = "12"
elif ( datetime.datetime.now() >= datetime.datetime(now.year, now.month, now.day, 19, 15) and datetime.datetime.now() < datetime.datetime(now.year, now.month, now.day+1, 1, 15)):
    hr = "18"
elif ( datetime.datetime.now() >= datetime.datetime(now.year, now.month, now.day, 1, 15) and datetime.datetime.now() < datetime.datetime(now.year, now.month, now.day, 7, 15)):
    hr = "00"
elif ( datetime.datetime.now() >= datetime.datetime(now.year, now.month, now.day, 7, 15) and datetime.datetime.now() < datetime.datetime(now.year, now.month, now.day, 13, 15)):
    hr = "06"

print(hr)

def download(url, file_name):
    with open(file_name, "wb") as file:
        response = get(url)
        file.write(response.content)

def checkFile(fileName, term):
    try:
        with open(fileName) as f:
            datafile = f.readlines()
            found = False  # This isn't really necessary
            for line in datafile:
                if term in line:
                    return True
            return False  # Because you finished the search without finding
    except:
        return False



for i in range (1,121):
    fhr = str(i).zfill(3)
    URL="https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25_1hr.pl?file=gfs.t"+hr+"z.pgrb2.0p25.f"+fhr+"&var_APCP=on&subregion=&leftlon=-62&rightlon=-45&toplat=-15&bottomlat=-30&dir=%2Fgfs."+date+""+hr+""
    download(URL, "./gfs_"+date+"_"+hr+"_"+fhr+"")
    if glob.glob("./gfs_"+date+"_"+hr+"_"+fhr+""):
        if checkFile("./gfs_"+date+"_"+hr+"_"+fhr+"", "html") is not True:
            #os.system("cdo -f nc copy gfs_"+date+"_"+hr+"_"+fhr+" gfs_"+date+"_"+hr+"_"+fhr+".nc") 
            os.system("gdal_translate -a_srs EPSG:4326 gfs_"+date+"_"+hr+"_"+fhr+" -of Gtiff gfs_"+date+"_"+hr+"_"+fhr+".tif")
            os.system("saga_cmd grid_tools 0 -INPUT:gfs_"+date+"_"+hr+"_"+fhr+".tif -OUTPUT:gfs_"+date+"_"+hr+"_"+fhr+" -SCALE_UP:1 -SCALE_DOWN:1 -TARGET_USER_SIZE:0.005")
            os.system("saga_cmd io_gdal 2 -GRIDS:gfs_"+date+"_"+hr+"_"+fhr+".sdat -FILE:gfs_"+date+"_"+hr+"_"+fhr+".tif")
            os.system("rm *.mgrd *.prj *sdat *sgrd *xml")
            os.system("raster2pgsql -s 4326 -t 100x100 -I -C -M gfs_"+date+"_"+hr+"_"+fhr+".tif public.gfs > gfs_"+date+"_"+hr+"_"+fhr+".sql")
            #with psycopg2.connect(host=mhost, database=db, user=usr,  password=pwd) as cursor:
            #    cursor.execute(open("gfs_"+date+"_"+hr+"_"+fhr+".sql", "r").read())
            os.system("rm gfs_"+date+"_"+hr+"_"+fhr+".sql")
        os.system("rm gfs_"+date+"_"+hr+"_"+fhr+"")

