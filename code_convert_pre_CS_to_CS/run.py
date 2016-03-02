import numpy as np
import os
import sys
import subprocess
from uploadStdFileAsCSAndTestData import *
sys.path.insert(0, '/home/anglil/csehomedir/learner/code_convert_pre_CS_to_CS/boto_dynamic_payment')
from task_publishing import *

# ---------------- parameters ---------
# jbragg: Replace Chris's parameters with mine.
#dataFile = '/home/anglil/csehomedir/learner/data_featurized/chris_data_exp_2000'
#goldFile = '/home/anglil/csehomedir/learner/data_test/test_strict_new_feature_no_grammatic'
#db_prefix = 'chris'
#db_suffix = 'data_exp_2000'
dataFile = '/home/anglil/csehomedir/learner/data_test/test_strict_new_feature_no_grammatic_soderland'
goldFile = '/home/anglil/csehomedir/learner/data_test/test_strict_new_feature_no_grammatic_not_soderland'
db_prefix = 'jbragg'
db_suffix = 'data_164_gold_1'
hitNum = 3
maxAssignments = 1

# jbragg parameters.


# ---------------- 1. set up the database ----------------
dbName = db_prefix+"_"+db_suffix
db_new = setupDB(dbName)
uploadStdFileCS(dataFile, db_new)
uploadStdFileTest(goldFile, db_new)

# ---------------- 2. connect the Rails app to the database --------------
data = None
with open('rails_couchdb/config/couchdb.yml', 'r') as f1:
	data = f1.readlines()
data[4] = "  prefix: "+db_prefix+'\n'
data[5] = "  suffix: "+db_suffix+'\n'
data[17] = "  prefix: "+db_prefix+'\n'
data[18] = "  suffix: "+db_suffix+'\n'

with open('rails_couchdb/config/couchdb.yml', 'w') as f2:
	f2.writelines(data)

secretData = None
with open('rails_couchdb/config/secrets.yml', 'r') as f3:
	secretData = f3.readlines()
secretData[18] = "  database: \'"+dbName+"\'\n"

with open('rails_couchdb/config/secrets.yml', 'w') as f4:
	f4.writelines(secretData)

# --------------- 3. start the server -----------------
subprocess.call("./startServer.sh", shell=True)

# --------------- 4. publish the task on Mturk ------------
PublishTasks(hitNum, maxAssignments)
