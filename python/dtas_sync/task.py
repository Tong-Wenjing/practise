#!/usr/bin/env python
#system modules
import sqlite3
import time
import os
import subprocess as sp
import xml.dom.minidom as md

#custom modules
import database as db
import config as cf
import common as cm
import handler

def _loadConfig(conf, module):
	xmlDomObj = cf.openConf(conf)	
	#Get each config values
	for key in cm.dtas_conf.keys():
		val = cf.getConfigByParam(xmlDomObj, module, key)
		cm.dtas_conf[key] = val
	print cm.dtas_conf
	
def _initPosDB():
	db.initPostDb()

def _initFileQue():
	"""
	Create the list which has files needed to be submitted
	"""
	print "Initialize the file queue..."
	#empty file queue
	cm.fileQue = [] 

	#open fstream_serv sqlite3 db
	conn = sqlite3.connect(cm.FSTREAM_DB)
	cur = conn.cursor()
	
	#begin a transaction
	currTime = int(time.mktime(time.localtime()))
	ageTime = currTime - (int(cm.dtas_conf["upload_age_max"]) * 24 * 60 * 60)
	cur.execute(cm.SELECT_SUBMIT_FILES, (ageTime, currTime, int(cm.dtas_conf["internal_submit_buf"])))
	print "Select the files which needs to be submitted :\n %s " % cm.SELECT_SUBMIT_FILES
	print "ageTime: %d " % ageTime
	print "currTime: %d " % currTime
	
	#retrieve the info from fstream_serv db 
	ret = cur.fetchall()
	
	#insert each file info into list
	for row in ret:
		i = 0
		node = {}
		for col in row:
			node[cm.fileNode[i]] = col
			i+=1
		print node
		cm.fileQue.append(node)

	print "fileQue: \n" , cm.fileQue

	#commit a transaction
	cur.close()
	conn.close()

def _fileDistribute():
	"""
	Distribute the files in PE/MSI format to GRID list, others to sandbox list
	"""
	for file in cm.fileQue:
		shiftFileType = file["truefiletype"] >> 16
		if (shiftFileType == cm.FILETYPE_PE or shiftFileType == cm.FILETYPE_MSI) :
			#cm.toBeGRIDQue.append(file)
			cm.toBeSbQue.append(file)
		else:
			cm.toBeSbQue.append(file)
	print "After distribute: sandbox list is as following:"
	print cm.toBeSbQue
	print "After distribute: GRID list is as following:"
	print cm.toBeGRIDQue

	cm.fileQue = []

def _checkUploadExpiredFile():
	"""
	If the files which have been uploaded but haven't get the result within
	1 day, they will be ignored and marked as analyze timeout
	"""
	print "Start to check upload expired file..."
	
	#get the expire time range
	expireAge = int(time.mktime(time.localtime())) - (int(cm.dtas_conf["uploaded_expire_day"]) * 24 * 60 * 60)
	print "Expire age time is : %d " % expireAge
	
	#Create fsream_serv sqlite3 DB connection
	conn = sqlite3.connect(cm.FSTREAM_DB)
	cur = conn.cursor()

	#Execute the update
	print "Start to execute sql : %s " % cm.UPDATE_EXPIRED_FILE
	cur.execute(cm.UPDATE_EXPIRED_FILE,(98,expireAge))
	conn.commit()
	
	#Close sqlite3 connection
	cur.close()
	conn.close()

	#Delete the expired taskid from postgresql db
	cm.POST_CURSOR.execute(cm.DELETE_EXPIRED_TASKID, (expireAge,))
	cm.POST_CONN.commit()

def _updateFileInQue():
	"""
	Calculate the number of the files would be submitted within 7 days
	"""
	print "Start to update the # of file in queue..."
	#Get the expire age
	expireTime = int(time.mktime(time.localtime())) - (int(cm.dtas_conf["upload_age_max"]) * 24 * 60 * 60)
	
	#Create fsream_serv sqlite3 DB connection
	conn = sqlite3.connect(cm.FSTREAM_DB)
	cur = conn.cursor()

	#Execute the select
	print "Start to execute sql : %s " % cm.SELECT_FILE_IN_QUE
	cur.execute(cm.SELECT_FILE_IN_QUE,(expireTime,))
	fileInQue = cur.fetchone()
	print "The # of file in queue is : %d " % fileInQue
	
	#Close sqlite3 connection
	cur.close()
	conn.close()

def _retrieveFeedback():
	"""
	Retrieve the blacklists from usandbox
	1. Call CLI: op-getblacklist
	2. Parse the feedback xml
	3. insert into tb_sandbox_feedback table
	4. Update the tb_sandbox_config_feedback table
	"""
	print "Start to retrieve the blacklist..."

	#Get the last blacklist report ID
	cm.POST_CURSOR.execute(cm.SELECT_FEEDBACK_CONFIG, (1,))
	lastID = cm.POST_CURSOR.fetchone()
	
	print "The last blacklist report ID is %d " % lastID
	
	#Call CLI : op-getblacklist
	cli = cm.CLI_COMMAND_PATH + cm.CLI_RETRIEVE_FEEDBACK + str(lastID[0])
	print cli
	
	#Get the cli returned blacklist xml
	handle = sp.Popen(cli, shell=True, stdout=sp.PIPE)	
	repSrc = handle.communicate()[0]
	
	#Parse the xml
	xmlObj = md.parseString(repSrc)
	repSets = xmlObj.getElementsByTagName("REPORT")

	count = len(repSets)
	
	#if no blacklist feedback, return
	if count == 0:
		return

	i = 0
	while i < count:
		#Parse the sections in each blacklist 
		ID = repSets[i].getElementsByTagName("ID")[0].firstChild.data
		Action = repSets[i].getElementsByTagName("Action")[0].firstChild.data
		Type = repSets[i].getElementsByTagName("Type")[0].firstChild.data
		Data = repSets[i].getElementsByTagName("Data")[0].firstChild.data
		RiskLevel = repSets[i].getElementsByTagName("RiskLevel")[0].firstChild.data
		ViolatedDTASPolicy = repSets[i].getElementsByTagName("ViolatedDTASPolicy")[0].firstChild.data
		ExpireTime = repSets[i].getElementsByTagName("ExpireTime")[0].firstChild.data
		SourceFileSHA1 = repSets[i].getElementsByTagName("SourceFileSHA1")[0].firstChild.data
		
		print "ID = %s\nAction = %s\nType = %s\nData = %s\nRiskLevel = %s\nViolatedDTASPolicy = %s\nExpireTime = %s\nSourceFileSHA1 = %s\n" % (ID, \
		Action, Type, Data, RiskLevel, ViolatedDTASPolicy, ExpireTime, SourceFileSHA1)
		
		#Check if the blacklist has already in db
		cm.POST_CURSOR.execute(cm.CHECK_BLACKLIST_DUP, (Data, Type))
		ret = cm.POST_CURSOR.fetchone()
		print "Check dup sql : %s\nThe result is : %d " % (cm.CHECK_BLACKLIST_DUP, ret[0])
		
		if ret[0] > 0:
			#update the exist record
			cm.POST_CURSOR.execute(cm.UPDATE_BLACKLIST, (Action, ExpireTime, Data, Type))
			cm.POST_CONN.commit()
			print "The backlist %s has been exist..." % ID
			i=i+1
			continue

		#No duplicate blacklist found, so insert 
		print "Insert the blacklist: %s" % cm.INSERT_BLACKLIST
		cm.POST_CURSOR.execute(cm.INSERT_BLACKLIST, (ID, ExpireTime, Action, Type, Data, ViolatedDTASPolicy, RiskLevel, SourceFileSHA1))
		cm.POST_CONN.commit()
		i=i+1
	
	#update the latest blacklist id
	cm.POST_CURSOR.execute(cm.UPDATE_FEEDBACK_CONFIG, (ID,))
	cm.POST_CONN.commit()
	print "Update the last blacklist report ID: %s " % cm.UPDATE_FEEDBACK_CONFIG

def _retrieveReport():
	"""
	Retrieve the analyze report based on the taskid
	1. Get the taskid
	2. Get the task state by call sys-getstate
	3. if the task is complete, get the result by call sys-getresult
	4. Parse the result and inser to db
	5. Delete taskid
	6. Update the rtime and threat type, severity, hasdtasres if necessary
	"""
	print "Start to retrieve report..."
	
	#Variable definition
	submittedFiles = []
	subFilesDict = {}
	reportDoneDict = {}

	#Get the taskid
	#Get sha1 from fsream_serv.db
	expireAge = int(time.mktime(time.localtime())) - int(cm.dtas_conf["uploaded_expire_day"]) * 24 * 60 * 60
	conn = sqlite3.connect(cm.FSTREAM_DB)
	cur = conn.cursor()
	cur.execute(cm.SELECT_FILE_SUBMITTED, (expireAge,))
	submittedFiles = cur.fetchall()
	print "Select submitted files: %s \t Expire time : %d " % (cm.SELECT_FILE_SUBMITTED, expireAge)
	print "submittedFiles : ", submittedFiles

	if len(submittedFiles) == 0:
		return

	#Get the taskid based on the sha1 value
	idListFile = open("/tmp/idlist", "a")	
	i=0
	while i<len(submittedFiles):
		sha1 = submittedFiles[i][0]
		print "sha1 is : %s " % sha1
		cm.POST_CURSOR.execute(cm.SELECT_TASKID, (sha1,))
		taskID = cm.POST_CURSOR.fetchone()[0]
		if taskID == None:
			continue
		print taskID
		subFilesDict[taskID] = submittedFiles[i]
		idListFile.write(str(taskID) + '\n')
		i+=1
	idListFile.close()
	print "subFilesDict : ", subFilesDict
	
	#Check the task status
	cli = cm.CLI_COMMAND_PATH + cm.CLI_RETRIEVE_REPORT_STATUS + '/tmp/idlist'
	print cli
	
	handle = sp.Popen(cli, shell=True, stdout=sp.PIPE)
	ret = handle.communicate()[0]
	print ret
	taskState = eval(ret).values()[0]
	print taskState,len(taskState)
	
	j = 0
	while j < len(taskState):
		status = taskState[j]["StatusStr"]
		if status == 'complete':
			taskid = taskState[j]["TaskID"]
			print "taskid = %d " % taskid
			print subFilesDict[taskid]
			reportDoneDict[taskid] = subFilesDict[taskid]
		j+=1
	print reportDoneDict

	#get the result of the complete task
	print reportDoneDict.keys()
	for id in reportDoneDict.keys():
		dstPath = reportDoneDict[id][1] + '_pcap'
		cli = cm.CLI_COMMAND_PATH + cm.CLI_RETRIEVE_REPORT + dstPath + ' ' + str(id)
		print cli
		os.system(cli)
		resultFile = dstPath + '/' + reportDoneDict[id][0] + '.report.xml'
		print resultFile
		parseResult = []
		handler._parseResult(resultFile, parseResult)
		#update rtime
		db._sqlite_updateRtime(reportDoneDict[id][0])	
		#Insert the report into db
		db._psql_InsertResult(parseResult, resultFile)
		#Remove the taskid 
		db._psql_RemoveTaskId(id)
		#Purge the result in u-sandbox
		cli = cm.CLI_COMMAND_PATH + cm.CLI_PURGE_RESULT + str(id)
		os.system(cli)
		cm.SLIDE_WINDOW_SIZE+=1

	#remove the idlist file
	os.system("rm -f /tmp/idlist")

def _submitFiles():
	"""
	submit new files to unified sandbox
	"""
	#calculate the expire date time
	expireAge = int(time.mktime(time.localtime())) - int(cm.dtas_conf["upload_age_max"]) * 24 * 60 * 60
	#initialize the file queue
	if len(cm.toBeSbQue) == 0: 
		_initFileQue()
		_fileDistribute()
	
	print "toBeSbQue length : %d" % len(cm.toBeSbQue)
	
	#Check if slide window is > 0
	i = -1
	toBeUpdate = []
	while abs(i) <= len(cm.toBeSbQue):
		#submit count should <= current slide window size
		if cm.SLIDE_WINDOW_SIZE <= 0: 
			break
		#Check if there're files in the list have been expired
		if cm.toBeSbQue[i]["lastdetectiontime"] < expireAge:
			del cm.toBeSbQue[i]
			i=i-1
			continue
		
		sha1 = cm.toBeSbQue[i]["sha1"]
		filePath = cm.toBeSbQue[i]["filepath"]
		#do local submit
		taskid = _doLocalSubmit(sha1, filePath)
		print "sha1 = %s\ttaskid = %d" % (sha1, taskid)

		#save the taskid
		cm.toBeSbQue[i]["taskid"] = taskid
		db._doInsertTaskid(sha1, taskid)

		#move the submitted file into to be updated list
		toBeUpdate.append(cm.toBeSbQue[i])
		print toBeUpdate
		
		#delete the file from the list
		del cm.toBeSbQue[i]
	
		i=i-1
		cm.SLIDE_WINDOW_SIZE -= 1

	#update db for the submitted files
	db._doUpdateUtime(toBeUpdate, int(time.mktime(time.localtime())))
	print "Update utime for sha1..." 
	
def _doLocalSubmit(sha1, filePath):
	"""
	Submit the file to usandbox through CLI
	"""
	#Consolate the CLI
	submitCLI = cm.CLI_COMMAND_PATH + cm.CLI_SUBMIT_SAMPLE + filePath + " | cut -d ':' -f2 "
	print submitCLI

	#do submit
	taskid = int(os.popen(submitCLI, 'r').read())
 	return taskid
	
def _doGRIDQuery():
	pass

def _doIntSandbox():
	"""
	Do the following tasks internally
	1. Check files which hasn't got the result within one day and mark it to be expired
	2. Record the file count in the queue
	3. retrieve feedback
	4. retrieve report
	5. Submit files to usandbox
	6. Update statistic info
	7. Do GRID query
	"""
	#1. update the expired files
	_checkUploadExpiredFile()
	#2. Record the file count in the queue
	_updateFileInQue()
	#3. retrieve feedback
	_retrieveFeedback()
	#4. retrieve report
	_retrieveReport()
	#5. Submit files to usandbox
	_submitFiles()
	#6. Update statistic info
	
	#7. Do GRID query
	_doGRIDQuery()
