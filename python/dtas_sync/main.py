#!/usr/bin/env python

#system module
import sqlite3
import time

#custom module
import common as cm
import database as db
import handler as hd
import task as tk
import config as conf

#Module functions
def loadconfig(conf, module):
	tk._loadConfig(conf, module)

def initDB():
	tk._initPosDB()

def initQue():
	tk._initFileQue()
	tk._fileDistribute()

def IntSandbox():
	tk._doIntSandbox()

if __name__ == "__main__":
	"""Start of main program"""
	#load the dtas config from ggb.conf and igsa.conf
	print "Start to load configuration..."
	loadconfig(cm.IGSA_CONF, 'dtas')
	print "Load configuration successfully...\n"
	print "<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>\n"
	#initialize database
	print "Start to initialize DB..."
	initDB()
	print "Initialize DB successfully...\n"
	print "<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>\n"
	#initialize queue (submittion/GRID)
	print "Start to initialize the file queue..."
	initQue()
	print "Initialize the file queue successfully...\n"
	print "<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>\n"
	#do internal virutal analysis routine
	while 1:
		print "Start interval sandbox work flow..."
		IntSandbox()
		print "\n"
		print "<<<<<<<<<<<<<Sleep %s seconds>>>>>>>>>>>>>>>>" % (20)
		time.sleep(20)

