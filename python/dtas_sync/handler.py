#!/usr/bin/env python

#system module
import xml.dom.minidom as md


def _parseResult(fileToBeParse, parseResult):
	"""
	1. Parse the result xml to extract the common info of parent file and all child files
	2. save each file's common info to list
	"""
	parseRetDict = {}

	#Open the result xml file to create an minidom object
	resDom = md.parse(fileToBeParse)
	fileAnaResList = resDom.getElementsByTagName("FILE_ANALYZE_REPORT")
	for fileAnalyzeResult in fileAnaResList:
		dupSha1 = fileAnalyzeResult.getElementsByTagName("DuplicateSHA1")[0].firstChild.data
		if dupSha1 == 1:
			continue
	
		if fileAnalyzeResult.getElementsByTagName("ParentSHA1") == [] :
			parseRetDict["parentSha1"] = ''
		else:
			parseRetDict["parentSha1"] = fileAnalyzeResult.getElementsByTagName("ParentSHA1")[0].firstChild.data
		
		parseRetDict["sha1"] = fileAnalyzeResult.getElementsByTagName("FileSHA1")[0].firstChild.data
		parseRetDict["OverallSeverity"] = fileAnalyzeResult.getElementsByTagName("OverallROZRating")[0].firstChild.data
		parseRetDict["severity"] = fileAnalyzeResult.getElementsByTagName("ROZRating")[0].firstChild.data
		parseRetDict["analyzeTime"] = fileAnalyzeResult.getElementsByTagName("AnalyzeTime")[0].firstChild.data
		parseRetDict["analyzeStartTime"] = fileAnalyzeResult.getElementsByTagName("AnalyzeStartTime")[0].firstChild.data
		parseRetDict["fileMD5"] = fileAnalyzeResult.getElementsByTagName("FileMD5")[0].firstChild.data
		parseRetDict["oriFileName"] = fileAnalyzeResult.getElementsByTagName("OrigFileName")[0].firstChild.data
		if fileAnalyzeResult.getElementsByTagName("MalwareSourceIP")[0].firstChild == None:
			parseRetDict["malSrcIP"] = ""
		else:
			parseRetDict["malSrcIP"] = fileAnalyzeResult.getElementsByTagName("MalwareSourceIP")[0].firstChild.data
		if fileAnalyzeResult.getElementsByTagName("MalwareSourceHost")[0].firstChild == None:
			parseRetDict["malSrcHost"] = ""
	 	else:
	 		parseRetDict["malSrcHost"] = fileAnalyzeResult.getElementsByTagName("MalwareSourceHost")[0].firstChild.data
		parseRetDict["trueFileType"] = fileAnalyzeResult.getElementsByTagName("TrueFileType")[0].firstChild.data
		parseRetDict["fileSize"] = fileAnalyzeResult.getElementsByTagName("FileSize")[0].firstChild.data
		parseRetDict["pcapReady"] = fileAnalyzeResult.getElementsByTagName("PcapReady")[0].firstChild.data

		print parseRetDict

		parseResult.append(parseRetDict)

		parseRetDict = {}
	
	print parseResult


