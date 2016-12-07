import sys, time
import getpass
import socket

#USER = "ubuntu"
USER = "nachi"  #local user
LOCALUSER = "nachi"
#USER = "sgd.cloud"  #gce user

#HOST = "52.90.19.2"
#HOST = "192.168.1.117" #home wifi
LOCALHOST = "127.0.0.1" #office ether
HOST = "104.198.123.110"  #gce public


#AWS = sys.platform != 'darwin'
AWS = sys.platform != 'linux2'

localhost_private_key =  "~/.ssh/id_rsa"
#private_key =  "/home/deep/keys/id_rsa"
private_key =  "~/.ssh/id_rsa"
CONFIG_PATH = __file__.split('settings.py')[0]


BUCKET_NAME = "aub3visualsearch"
PREFIX = "nyc"


# path to files
INDEX_PATH = "/home/deep/shopsite/index/"
DATA_PATH ="/home/deep/shopsite/images/"
DONE_DATA_PATH ="/home/deep/shopsite/done/"
SQLITE_PATH = "/home/deep/shopsite/sqllite3/"

# trial run settings 
RESULT_STEPS = 10
MAX_ITER = 5
MAX_COLLECTION = 5
BATCH_SIZE = 5

# full run settings for crawling and batch size for tensorflow feature file size
# RESULT_STEPS = 100
# MAX_ITER = 50
# MAX_COLLECTION = 12
# BATCH_SIZE = 500

# This is required whenever you want to restart the crawling in the event of failure
# Set ONETIME_COUNTSTART = True and also last start_collection value and the iteration count where it failed 
START_COLLECTION = 4
ONETIME_COUNTSTART = False
ITER_START_COUNT = 41

INDEX_RUN = str(time.time())
CRAWL_RUN = str(time.time())
SQLDB_NAME = 'carousellv11.sqlite'

#for query : ;path=/products/collections/4/;query={"count":100,"start":4101}



