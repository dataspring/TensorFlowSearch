import sys, time
import getpass
import socket

#USER = "ubuntu"
USER = "nachi"  #local user
#USER = "sgd.cloud"  #gce user
#HOST = "52.90.19.2"
#HOST = "192.168.1.117" #home wifi
HOST = "198.162.10.181" #office ether
#HOST = "104.199.121.106"  #gce public


#AWS = sys.platform != 'darwin'
AWS = sys.platform != 'linux2'
#private_key =  "~/.ssh/cs5356"
#private_key =  "/home/osboxes/nachi/keys/id_rsa"
private_key =  "/home/deep/keys/id_rsa"
CONFIG_PATH = __file__.split('settings.py')[0]

BUCKET_NAME = "aub3visualsearch"
PREFIX = "nyc"
# INDEX_PATH = "/mnt/nyc_index/"
# DATA_PATH ="/mnt/nyc_images/"


# path to files
INDEX_PATH = "/home/deep/carousell/index/"
DATA_PATH ="/home/deep/carousell/images/"
DONE_DATA_PATH ="/home/deep/carousell/done/"
SQLITE_PATH = "/home/deep/carousell/sqllite3/"

RESULT_STEPS = 100
MAX_ITER = 50
MAX_COLLECTION = 12
BATCH_SIZE = 500


START_COLLECTION = 4
ONETIME_COUNTSTART = True
ITER_START_COUNT = 41

INDEX_RUN = str(time.time())
CRAWL_RUN = str(time.time())
SQLDB_NAME = 'carousellv11.sqlite'

#for query : ;path=/products/collections/4/;query={"count":100,"start":4101}

def getusername():
    print getpass.getuser()
    return getpass.getuser()


# def getip():
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     try:
#         # doesn't even have to be reachable
#         s.connect(('10.255.255.255', 0))
#         IP = s.getsockname()[0]
#     except:
#         IP = '127.0.0.1'
#     finally:
#         s.close()
#     return IP


def getlp():
    return '127.0.0.1'       

USER = getusername
HOST = getlp
