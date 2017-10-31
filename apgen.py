#!/usr/bin/env python2.7
# APERTIF PARSET GENERATOR (apgen.py)
# Will generate a parset from a list of input source parameters
# Input: source text file
# V.A. Moss 26/10/2017 (vmoss.astro@gmail.com)

import os
import sys
from astropy.io import ascii
from datetime import datetime,timedelta

def ra2dec(ra):
    if not ra:
        return None
      
    r = ra.split(':')
    if len(r) == 2:
        r.append(0.0)
    return (float(r[0]) + float(r[1])/60.0 + float(r[2])/3600.0)*15


def dec2dec(dec):
    if not dec:
        return None
    d = dec.split(':')
    if len(d) == 2:
        d.append(0.0)
    if d[0].startswith('-') or float(d[0]) < 0:
        return float(d[0]) - float(d[1])/60.0 - float(d[2])/3600.0
    else:
        return float(d[0]) + float(d[1])/60.0 + float(d[2])/3600.0

# Read in the source file
try:
	fname = sys.argv[1]
except:
	fname = 'input.txt'

# Get the observation type:
# Note: can be "multi" or "single"
try:
	obstype = sys.argv[2]
except:
	obstype = 'single'

# Read file
d = ascii.read(fname,delimiter='\s',guess=False)
print d.keys() 

# Start the file
out = open('%s_params.txt' % fname.split('.')[0],'w')
out.write('#!/bin/bash\n# Script to create parsets for APERTIF\n# Original form by Boudewijn Hut 25/07/2017\n# Adapted by V.A. Moss 27/10/2017\n\n# values that change per measurement\n')
out.flush()

# scopes
scopes = '[RT2, RT4, RT5, RT6, RT7, RT8, RT9, RTB]'


# Loop through sources
for i in range(0,len(d)):

	# Details source
	src = d['Source'][i]

	# Account for RFI sources:
	if 'deg' in d['RA'][i]:
		ra = float(d['RA'][i].split('deg')[0])
		dec = float(d['DEC'][i].split('deg')[0])

	else:
		ra = ra2dec(d['RA'][i].replace('h',':').replace('m',':').replace('s',''))
		dec = dec2dec(d['DEC'][i].replace('d',':').replace('m',':').replace('s',''))
	
	# Details obs
	stime = d['UTC1'][i]
	etime = d['UTC2'][i]
	date = d['Date'][i]

	# Details system
	lo = d['LO'][i]
	sub1 = d['SUB1'][i]
	scan = d['Scan'][i]

	# Fix times if they aren't the right length
	if len(stime.split(':')[0]) < 2:
		stime = '0'+stime
	if len(etime.split(':')[0]) < 2:
		etime = '0'+etime

	# do a check for the end time
	stime_dt = datetime.strptime(stime,'%H:%M')
	etime_dt = datetime.strptime(etime,'%H:%M')
	if etime_dt < stime_dt:
		date2 = datetime.strptime(date,'%Y-%m-%d')+timedelta(days=1)
		date2 = datetime.strftime(date2,'%Y-%m-%d')
	else:
		date2 = date


	# exception
	if i == 0:

		exectime = datetime.strptime(stime,'%H:%M')-timedelta(seconds=58)
		exectime = datetime.strftime(exectime,'%H:%M')

		out.write("""TASKIDS=(    '%s')
EXEC_TIMES=( 'utcnow()')
START_TIMES=('%s %s:00')
STOP_TIMES=( '%s %s:00')
LO1FREQS=(   '%s')
SUBBAND1=(    %s)
SOURCENAMES=('%s')
SOURCE_RAS=( '%.4f')
SOURCE_DECS=('%.4f')
INTFACTORS=( '30')

""" % (scan,date,stime,date2,etime,lo,sub1,src,ra,dec))
		out.flush()

	else:
		exectime = datetime.strptime(old_etime,'%H:%M')+timedelta(seconds=2)
		exectime = datetime.strftime(exectime,'%H:%M')

		out.write("""TASKIDS+=(    '%s')
EXEC_TIMES+=( '%s %s:02')
START_TIMES+=('%s %s:00')
STOP_TIMES+=( '%s %s:00')
LO1FREQS+=(   '%s')
SUBBAND1+=(    %s)
SOURCENAMES+=('%s')
SOURCE_RAS+=( '%.4f')
SOURCE_DECS+=('%.4f')
INTFACTORS+=( '30')

""" % (scan,date,exectime,date,stime,date2,etime,lo,sub1,src,ra,dec))
		out.flush()		


	old_etime = etime

out.write("""# constant value for all measurements
TELESCOPES="%s"   # "[RT2, RT3, RT4, RT5, RT6, RT7, RT8, RT9, RTA, RTB, RTC, RTD]"
""" % scopes)
out.flush()

# Determine which file to concatenate with
if obstype == 'multi':
	outname = '%s_params.txt' % fname.split('.')[0]
	outname2 = '%s_params.sh' % fname.split('.')[0]
	os.system('cat %s create_parset_multi_element_beams.txt > %s' % (outname,outname2))

elif obstype == 'single':
	outname = '%s_params.txt' % fname.split('.')[0]
	outname2 = '%s_params.sh' % fname.split('.')[0]
	os.system('cat %s create_parset.txt > %s' % (outname,outname2))

else:
	print 'You have specified something weird!'
