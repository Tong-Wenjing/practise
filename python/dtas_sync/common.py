#Global config
IGSA_CONF = "/mr_etc/igsa.conf"
DB_CONF = "/mr_etc/database.conf"
FSTREAM_DB = "/var/log/fstream_serv.db"
#Global variable definitions
SLIDE_WINDOW_SIZE = 1 

#file type
FILETYPE_PE = 7
FILETYPE_MSI = 123

#usandbox CLIs
CLI_COMMAND_PATH = "/usr/bin/python /var/log/u-sandbox/usandbox/cli/usbxcli.py "
CLI_SUBMIT_SAMPLE = "op-submitsample "
CLI_RETRIEVE_REPORT_STATUS = "op-getstatus --idlist "
CLI_RETRIEVE_REPORT = "op-getresult --dst "
CLI_RETRIEVE_FEEDBACK = "op-getblacklist --id "
CLI_PURGE_RESULT = "op-purgeresult --id "


#Configurations from igsa.conf
dtas_conf = {
                #"license_sandbox_enable":"",\
                "enable":"",\
                "interval":"",\
                "retry_count":"",\
                "retry_pause":"",\
                "discard_count":"",\
                "upload_potential":"",\
                "upload_all_exe":"",\
                "upload_age_max":"",\
                "uploaded_expire_day":"",\
                "queue_type":"",\
                #grid
                "grid_enable":"",\
                "grid_query_timeout":"",\
                "internal_submit_buf":"",\
                "batch_grid_count":"",\
                "enable_record_grid_unknown":"",\
                "sliding_window_size":"",\
                "file_count_one_tgz":"",\
                "upload_size_max":"",\
                "switch_dtas_flag":"",\
                "file_size_max":"",\
                "cavlog_size_max":"",\
                "feedback_active":"",\
                "connect_timeout":"",\
                "transfer_timeout":"",\
                "skip_cleanup":"",\
                "sandbox_module":"",\
                "enable_cef_log":"",\
                "max_cef_log_folder_size":"",\
                "inbox_dtas_interval":"",\
                "purge_inbox_pcap_report_enable":""
                }

#node in to be sandbox queue
fileNode =("sha1","filepath","type","truefiletype","lastdetectiontime")

#all file queue
fileQue = []
#to be sandbox queue
toBeSbQue = []
#to be GRID queue
toBeGRIDQue = []

###############
# Database
###############

#Postgresql 
#DB connection
POST_CONN = ''
POST_CURSOR = '' 

#SQL statment
#Insert
INSERT_SANDBOX_RESULT = "insert into tb_sandbox_result (ReceivedTime, SHA1, Severity, OverallSeverity, Report, filemd5, parentsha1, origfilename, malwaresourceip, malwaresourcehost, analyzetime, truefiletype, filesize, pcapready) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
INSERT_SANDBOX_FEEDBACK = "insert into tb_sandbox_feedback values(%s);"
INSERT_TASKID = "insert into tb_sandbox_sha1_taskid_mapping (sha1, taskid, last_update_time) values(%s, %s, %s);"
INSERT_BLACKLIST = "insert into tb_sandbox_feedback (ReportID, Expiration, Action, Type, Data, PolicyID, Severity, SourceFileSHA1) values (%s, %s, %s, %s, %s, %s, %s, %s);"
#Delete
DELETE_TASKID = "delete from tb_sandbox_sha1_taskid_mapping where taskid=%s;"
DELETE_EXPIRED_TASKID = "delete from tb_sandbox_sha1_taskid_mapping where last_update_time <= to_timestamp(%s);"
#Modify
UPDATE_FEEDBACK_CONFIG = "update tb_sandbox_config_feedback set last_retrieve_feedback_id = %s where sandbox_type=1;"
UPDATE_BLACKLIST = "update tb_sandbox_feedback set action = %s, expiration = %s where data = %s and type = %s;"
#Query
SELECT_FEEDBACK_CONFIG = "select last_retrieve_feedback_id from tb_sandbox_config_feedback where sandbox_type = %s;"
SELECT_TASKID = "select taskid from tb_sandbox_sha1_taskid_mapping where sha1 = %s;"
CHECK_BLACKLIST_DUP = "select count(*) from tb_sandbox_feedback where data = %s and type = %s;"

#Sqlite3 
#SQL statment
#Modify
UPDATE_UTIME = "update sha1 set utime = ? where sha1_value = ?;"
UPDATE_RTIME = "update sha1 set rtime = ? where sha1_value = ?;"
UPDATE_EXPIRED_FILE = "update sha1 set rtime = ? where dtasenabled = 1 and utime > 0 and utime < ? and rtime = 0;"  
#Query
SELECT_SUBMIT_FILES = "select sha1_value,sha1_path,type,vsapi_file_type,LastDetectionTime from sha1 where (type >= 100 and type <= 102) and utime = 0 and rtime = 0 and dtasenabled = 1 and lastdetectiontime >= ? and lastdetectiontime < ? order by lastdetectiontime desc limit ?;"
SELECT_FILE_IN_QUE = "select count(sha1_value) from sha1 where utime <= 0 and rtime <= 0 and dtasenabled = 1 and lastdetectiontime > ?;"
SELECT_FILE_SUBMITTED = "select sha1_value, sha1_path from sha1 where utime > ? and rtime <= 0;"
