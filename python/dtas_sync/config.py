#!/usr/bin/env python

#system module
import xml.dom.minidom as md

def openConf(conf):
	filesource = open(conf, 'r')
	#construct the xml Document object
	xmldom = md.parse(filesource)
	return xmldom

def getConfigByParam(xmldom, module, param, index=0):
	#locate the module
	mod = xmldom.getElementsByTagName(module)
	if mod:
		#locate the param
		para = mod[0].getElementsByTagName(param)
		#retrieve the parameter value
		vl = para[index].attributes['value'].value
		return vl
	else:
		print "The configuration doesn't exist!"

if __name__ == "__main__":
	pass
	#xmlDoc = openConfig('/mr_etc/igsa.conf')	
	#ret = getConfigByParam(xmlDoc, 'dtas', 'internal_submit_buf')
	#print ret
	#getConfig()
	#for key in dtas_conf.keys():
	#	print "%s ==> %s" % (key, dtas_conf[key])
