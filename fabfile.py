import os,sys,logging,time,shutil
from fabric.state import env
from fabric.api import env,local,run,sudo,put,cd,lcd,puts,task,get,hide
import requests, json, sqlite3, urllib

from settings import BUCKET_NAME,DATA_PATH,INDEX_PATH,SQLITE_PATH,DONE_DATA_PATH
from settings import RESULT_STEPS, MAX_ITER, MAX_COLLECTION, BATCH_SIZE,INDEX_RUN,CRAWL_RUN,SQLDB_NAME
from settings import START_COLLECTION,ONETIME_COUNTSTART,ITER_START_COUNT

try:
    import inception
except ImportError:
    print "could not import main module limited to boostrap actions"
    pass

from settings import USER,private_key,HOST
env.user = USER
env.key_filename = private_key
env.hosts = [HOST,]
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='logs/fab.log',
                    filemode='a')



@task
def notebook():
    """
    Run an IPython notebook on an AWS server
    """
    from IPython.lib.security import passwd
    command = "ipython notebook --ip=0.0.0.0  --certfile=mycert.pem --NotebookApp.password={} --no-browser".format(passwd())
    print command
    run(command)

@task
def gen_ssl():
    run("openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.key -out mycert.pem")


@task
def setup():
    """
    Task for initial set up of AWS instance.
    Used AMI modified for Python2.7 https://gist.github.com/AlexJoz/1670baf0b32573ca7923
    Following commands show other packages/libraries installed while setting up the AMI
    """
    sudo("rm -rf ~/deep/carousell/")
    sudo("mkdir ~/deep/")
    sudo("mkdir ~/deep/carousell/")
    sudo("mkdir ~/deep/carousell/images/")
    sudo("mkdir ~/deep/carousell/index/")
    
    #sudo("chmod 777 /mnt/") # sometimes the first one will fail due to timeout and in any case this is idempotent
    #sudo("chmod 777 /mnt/")
    
    sudo("apt-get install build-essential")
    sudo("apt-get install python-dev")  # for python2.x installs
    sudo("apt-get install git")    
    sudo("add-apt-repository ppa:kirillshkrogalev/ffmpeg-next")
    sudo("apt-get update")
    sudo("apt-get install -y ffmpeg")

    run("git clone https://github.com/AKSHAYUBHAT/VisualSearchServer")
    sudo("apt-get install python-pip")
    sudo("pip install fabric")
    sudo("pip install --upgrade awscli")
    sudo("pip install --upgrade fabric")
    sudo("pip install --upgrade flask")
    sudo("pip install --upgrade ipython")
    sudo("pip install --upgrade jupyter")
    sudo("apt-get install -y python-scipy")
    sudo("apt-get install -y libblas-dev liblapack-dev libatlas-base-dev gfortran")
    sudo("pip install --upgrade nearpy")
    sudo("sudo apt-get install sqlite3 libsqlite3-dev")
    sudo("pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.11.0rc0-cp27-none-linux_x86_64.whl")
	
@task
def localdevsetup():
    """
    Task for initial set up of local instance.
    call the setup() followed by tools installation locally
    """
    sudo("pip install  ")
    sudo("pip install  flask")
    sudo("pip install  ipython")
    sudo("pip install  jupyter")
    sudo("pip install  scipy")
    sudo("pip install  nearpy")


@task
def connect():
    """
    Creates connect.sh for the current host
    :return:
    """
    fh = open("connect.sh",'w')
    fh.write("#!/bin/bash\n"+"ssh -i "+env.key_filename+" "+"ubuntu"+"@"+HOST+"\n")
    fh.close()


@task
def server():
    """
    start server
    """
    local('python server.py')


@task
def demo_fashion():
    """
    Start Demo using precomputed index for 450 thousand female fashion images.
    """
    local('aws s3api get-object --bucket aub3visualsearch --key "fashion_index.tar.gz" --request-payer requester /mnt/fashion_index.tar.gz')
    local('cd /mnt/;tar -zxvf fashion_index.tar.gz')
    local('echo "\nDEMO=\'fashion_images\'" >> settings.py')
    local('echo "\nINDEX_PATH=\'/mnt/fashion_index/\'" >> settings.py')
    local('python server.py &')
    local('tail -f logs/server.log')

@task
def demo_nyc():
    """
    Start Demo using precomputed index for 26 thousand street view / dashcam style images.
    """
    local('aws s3api get-object --bucket aub3visualsearch --key "nyc_index.tar.gz" --request-payer requester /mnt/nyc_index.tar.gz')
    local('cd /mnt/;tar -zxvf nyc_index.tar.gz')
    local('echo "\nDEMO=\'nyc_images\'" >> settings.py')
    local('echo "\nINDEX_PATH=\'/mnt/nyc_index/\'" >> settings.py')
    local('python server.py &')
    local('tail -f logs/server.log')


@task
def index():
    """
    Index images
    """
    INDEX_RUN = str(time.time())  #reset the batch run with latest tick every time index batch is run 
    logging.info("Starting with images present in {} storing index in {}".format(DATA_PATH,INDEX_PATH))
    try:
        if os.path.isdir(INDEX_PATH)==False:
            os.mkdir(INDEX_PATH)
    except:
        print "Could not created {}, if its on /mnt/ have you set correct permissions?".format(INDEX_PATH)
        raise ValueError
    inception.load_network()
    count = 0
    start = time.time()
    with inception.tf.Session() as sess:
        for image_data in inception.get_batch(DATA_PATH, BATCH_SIZE):
            print "Batch with {} images loaded in {} seconds".format(len(image_data),time.time()-start)
            logging.info("Batch with {} images loaded in {} seconds".format(len(image_data),time.time()-start))
            start = time.time()
            count += 1
            features,files = inception.extract_features(image_data,sess)
            print "Batch with {} images processed in {} seconds".format(len(features),time.time()-start)
            logging.info("Batch with {} images processed in {} seconds".format(len(features),time.time()-start))
            start = time.time()
            inception.store_index(features,files,count,INDEX_PATH)
  

@task
def clear():
    """
    delete logs
    """
    local('rm logs/*.log &')


@task
def test():
    inception.load_network()
    count = 0
    start = time.time()
    test_images =  os.path.join(os.path.dirname(__file__),'tests/images')
    test_index = os.path.join(os.path.dirname(__file__), 'tests/index')
    try:
        shutil.rmtree(test_index)
    except:
        pass
    os.mkdir(test_index)
    with inception.tf.Session() as sess:
        for image_data in inception.get_batch(test_images,batch_size=2):
            # batch size is set to 2 to distinguish between latency associated with first batch
            if len(image_data):
                print "Batch with {} images loaded in {} seconds".format(len(image_data),time.time()-start)
                start = time.time()
                count += 1
                features,files = inception.extract_features(image_data,sess)
                print "Batch with {} images processed in {} seconds".format(len(features),time.time()-start)
                start = time.time()
                inception.store_index(features,files,count,test_index)
				

@task
def CarousellImages():
    """
    Get Carosuell Images by Scrapping
    """
    CRAWL_RUN = str(time.time())
    print 'Crawl Batch Run : ' + str(CRAWL_RUN)
    logging.info('Crawl Batch Run : ' + str(CRAWL_RUN))

    print '................................'
    print 'Runing Scrapping Now'
    print '................................'
    print 'establishing sqlite3 connection'

    #----------------------- sqllite3 connection ---------------------------
    sqlitePath = SQLITE_PATH + SQLDB_NAME
    #sqlitePath = SQLITE_PATH + 'carousell.sqlite'
    try:
        conn = sqlite3.connect(sqlitePath)
        print 'opened ' + sqlitePath + ' successfully'
        #------------drop table SellImages
        # try:
        #     conn.execute('delete from SellImages')
        #     conn.commit()
        # except sqlite3.Error as err:
        #     print err.message    

    except sqlite3.Error as connError:
        print connError.message
        print 'Exiting App'
        return None
    #-------------------------------------------------------------------------    
    
    service = 'https://carousell.com/ui/iso/api'
    collection = '/products/collections/{0}/'
    query='{{"count":{0},"start":{1}}}'
    #sqlInsert = "Insert into SellImages (id, imgurl, title, price) Values('{0}', '{1}', '{2}', {3})"
    sqlInsert = "Insert into SellImages (id, imgurl, title, price, collection, country, currency, imgpath, imgfilename, crawlrun) Values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    resSteps = RESULT_STEPS
    maxIter = MAX_ITER
    maxCollection = MAX_COLLECTION

    startCollection = START_COLLECTION
    #ONETIME_COUNTSTART
    

    downloadCount = 0
    processCount = 0
	
    for collec in range(startCollection,maxCollection):
        print 'executing : ' + service
        #--------------------------- a fix for restarting midway ------
        if collec == START_COLLECTION and ONETIME_COUNTSTART:
            iterStartCount = ITER_START_COUNT
        else:
            iterStartCount = 0
        #--------------------------- end: a fix for restarting midway ------
        for count in range (iterStartCount,maxIter) :
            queryString = ';path=' + collection.format(collec) + ';query=' + query.format(resSteps, count*resSteps+1)    
            url = service + queryString 
            print 'for query : ' + queryString
            try:
                req = requests.get(url, timeout=10)  #2 seconds timeout
            except requests.exceptions.ConnectionError as e:
                print e.message
            except requests.exceptions.Timeout as e:
                print e.message 
                #------------------ retry once here -----------------------
                time.sleep(10)
                try:
                    req = requests.get(url, timeout=10)  #2 seconds timeout
                except Exception as e:
                    print e.message
                #------------------ retry once here -----------------------
            except Exception as e:
                print e.message

            if req.status_code == requests.codes.ok:
                resJson = req.json()
                   
                if len(resJson['result']['products']) > 0:
                    for each in resJson['result']['products']:
                        print "%s\r\n%s\r\n%s\r\n%s" % (each['id'], each['primary_photo_url'], each['title'], each['price'])
                        #----- prep variables ---------------------------------
                        imgId = each['id']
                        imgUrl = each['primary_photo_url']
                        imgTitle = each['title'] 
                        imgPrice = each['price']  
                        imgCurrencySymbol = each['currency_symbol']
                        imgCollection = each['collection']['name']
                        imgCountry = each['marketplace']['country']['name']
                        imgPath = DATA_PATH
                        imgFileName = str(imgId) + ".jpg"

                        #------------------------- insret into sqllite ------------------------------------
                        try:
                            with conn:
                                processCount = processCount + 1
                                conn.execute(sqlInsert, (imgId, imgUrl, imgTitle, imgPrice, imgCollection, imgCountry, imgCurrencySymbol, imgPath, imgFileName, CRAWL_RUN))
                            #------- if insertion is ok, download the image -------------------
                            try:
                                if (os.path.isfile(DONE_DATA_PATH + str(imgId) + ".jpg") == False) and (os.path.isfile(DATA_PATH + str(imgId) + ".jpg") == False):
                                    downloadCount = downloadCount + 1
                                    urllib.urlretrieve(imgUrl, DATA_PATH + str(imgId) + ".jpg")
                            except Exception as e:
                                print e

                        except sqlite3.IntegrityError as inte:
                            print inte.message, imgId
                                    
	print 'CarousellImages completed, Total processed : ' + str(processCount)	+ ', downloaded : ' + str(downloadCount)	
    logging.info('CarousellImages completed, Total processed : ' + str(processCount)	+ ', downloaded : ' + str(downloadCount))