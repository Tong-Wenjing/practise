#!/usr/bin/env python

#system import
import time
from datetime import datetime
import sqlite3
#custom import
import config as cf
import common as cm

#Postgresql
import psycopg2

#######
# DB initialization
#######
def initPostDb():
	#get db connection info from config file
	xmlDomObj = cf.openConf(cm.DB_CONF)
	dbName = cf.getConfigByParam(xmlDomObj, 'postgresql', 'db_name')
	dbUser = cf.getConfigByParam(xmlDomObj, 'postgresql', 'db_user')
	dbPassword = cf.getConfigByParam(xmlDomObj, 'postgresql', 'db_password')
	connStr = "dbname=%s user=%s password=%s" % (dbName, dbUser, dbPassword)
	cm.POST_CONN = psycopg2.connect(connStr)
	cm.POST_CURSOR = cm.POST_CONN.cursor()

def closePostDb():
	cm.POST_CURSOR.close()
	cm.POST_CONN.close()

def _doInsertTaskid(sha1, taskid):
	"""
	Save the taskid and sha1 mapping into tb_sandbox_sha1_taskid_mapping
	"""
	currTime = time.strftime("%Y-%m-%d %X", time.localtime())
	print "sha1 = %s\ntaskid = %d\ncurrTime = %s" % (sha1, taskid, currTime)
	cm.POST_CURSOR.execute(cm.INSERT_TASKID, (sha1, taskid, currTime))
	cm.POST_CONN.commit()

def _psql_RemoveTaskId(taskid):
	"""
	Remove the completed taskid from db
	"""
	cm.POST_CURSOR.execute(cm.DELETE_TASKID, (taskid,))
	cm.POST_CONN.commit()

def _psql_InsertResult(parsedResult, repSrcFile):
	"""
	Insert the parsed parent/child analyze info into DB one by one
	Input parameters:
		1. Parsed analyze result list
		2. Source analyze file
	"""
	#prepare the repot xml
	fileHd = open(repSrcFile, 'r')
	repSrc = fileHd.read()
	
	#calculate receive time in utc
	recUTC = datetime.utcnow()
	receivedTime = str(recUTC.year) + '-' + str(recUTC.month) + '-' + str(recUTC.day) + ' ' + str(recUTC.hour) + ':' + str(recUTC.minute) + ':' + str(recUTC.second)
	#Iterate the parsed result list and insert one by one
	for ret in parsedResult:
		sha1 = ret["sha1"]
		severity = ret["severity"]
		overallseverity = ret["OverallSeverity"]
		filemd5 = ret["fileMD5"]
		parentsha1 = ret["parentSha1"]
		origfilename = ret["oriFileName"]
		malwaresourceip = ret["malSrcIP"]
		malwaresourcehost = ret["malSrcHost"]
		analyzetime = ret["analyzeTime"]
		truefiletype = ret["trueFileType"]
		filesize = ret["fileSize"]
		pcapready = ret["pcapReady"]
		if parentsha1 == '':
			report = repSrc	
		else:
			report = ''
		
		#Do insert tb_sandbox_result
		cm.POST_CURSOR.execute(cm.INSERT_SANDBOX_RESULT, (receivedTime, sha1, severity, overallseverity, report, filemd5, parentsha1, origfilename, malwaresourceip, malwaresourcehost, analyzetime, truefiletype, filesize, pcapready))

	#commit the transaction	
	cm.POST_CONN.commit()
	#close the file handler
	fileHd.close()

def _doUpdateUtime(fileList, time):
	"""
	Iterate to update the utime for those files which have been uploaded
	"""
	#Create fsream_serv sqlite3 DB connection
	conn = sqlite3.connect(cm.FSTREAM_DB)
	cur = conn.cursor()

	#Execute the update
	for file in fileList:
		cur.execute(cm.UPDATE_UTIME ,(time, file["sha1"]))
		conn.commit()

	#Close sqlite3 connection
	cur.close()
	conn.close()

def _sqlite_updateRtime(sha1):
	"""
	Update rtime for files have been analyzed
	"""
	conn = sqlite3.connect(cm.FSTREAM_DB)
	cur = conn.cursor()
	
	currentTime = int(time.mktime(time.localtime()))

	cur.execute(cm.UPDATE_RTIME, (currentTime, sha1))
	conn.commit()

	cur.close()
	conn.close()
