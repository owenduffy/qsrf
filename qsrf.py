#Copyright: Owen Duffy 2025. All rights reserved.
import urllib.request
import re
from pathlib import PurePath
import numpy as np
from scipy.interpolate import CubicSpline
import getopt, sys

ver="v0.02"
p=PurePath(sys.argv[0])
url='https://services.swpc.noaa.gov/text/solar_radio_flux.txt'
url2='ftp://ftp.swpc.noaa.gov/pub/lists/radio/45day_rad.txt'

def usage():
  print('Usage: '+p.stem+' [-l] <interpolation MHz freq list blank separated>')
  print('   -l long output (45 day)')
  sys.exit(2)

try:
  opts, args = getopt.getopt(sys.argv[1:], "hlv", ["help", "output="])
except getopt.GetoptError as err:
  # print help information and exit:
  print(err)  # will print something like "option -a not recognized"
  usage()
  sys.exit(2)
output = None
verbose = False
for o, a in opts:
  if o == "-l":
    url=url2
  if o == "-v":
    verbose = True
  elif o in ("-h", "--help"):
    usage()
    sys.exit()

print(p.stem+' '+ver)

#build the fout array
fout=[]
for x in args:
  fout.append(float(x))
fout=np.array(fout)

lines=urllib.request.urlopen(url) #fetch request content
print('-----------------------------------------------------------------------------')

#read another line from the request
def getline():
  line=lines.readline()
  if(len(line)==0):
    return 0
  return line.decode("utf-8") #return line terminated with \n

line=getline()
while(line!=0): #while not EOF
  line=line.rstrip()
  print(line)
  if(re.match('^\\d{4} \\w{3} \\d{1,2}$',line)):
    print('NOAA data:')
    site=[]
    for i in range(7):
      site.append([[],[],0])
    line=getline()
    while(line!=0 and len(line)>1): #loop over obs lines
      line=line.rstrip()
      print(line)
      fr=float(line[0:7])
      val=float(line[6:16])
      if(val!=-1):
        site[0][0].append(fr)
        site[0][1].append(val)
        site[0][2]+=1
      val=float(line[15:26])
      if(val!=-1):
        site[1][0].append(fr)
        site[1][1].append(val)
        site[1][2]+=1
      val=float(line[25:36])
      if(val!=-1):
        site[2][0].append(fr)
        site[2][1].append(val)
        site[2][2]+=1
      val=float(line[35:46])
      if(val!=-1):
        site[3][0].append(fr)
        site[3][1].append(val)
        site[3][2]+=1
      val=float(line[46:58])
      if(val!=-1):
        site[4][0].append(fr)
        site[4][1].append(val)
        site[4][2]+=1
      val=float(line[57:68])
      if(val!=-1):
        site[5][0].append(fr)
        site[5][1].append(val)
        site[5][2]+=1
      val=float(line[67:77])
      if(val!=-1):
        site[6][0].append(fr)
        site[6][1].append(val)
        site[6][2]+=1
      line=getline() #next obs
    #no more obs for this date, loop over sites writing results
    print('Calculated cubic spline interpolations / extrapolations:')
    css=[0,0,0,0,0,0,0]
    i=0
    for i in range(7):
      try:
        css[i]=CubicSpline(site[i][0],site[i][1])
      except:
        pass
    for j,f in enumerate(fout):
      sfns=[-1,-1,-1,-1,-1,-1,-1]
      for i in range(7):
        if(site[i][2]>1 and f>site[i][0][0]/2 and f<site[i][0][-1]*2 and css[i]!=0):
          sfns[i]=css[i](f)+0
      print('{:6.0f}{:9.0f}{:10.0f}{:10.0f}{:11.0f}{:11.0f}{:10.0f}{:10.0f}'.\
      format(f,sfns[0],sfns[1],sfns[2],sfns[3],sfns[4],sfns[5],sfns[6]))
    print('-----------------------------------------------------------------------------')
  line=getline() #next date
