import sqlite3, shutil
import time,glob,re,sys,logging,os,tempfile
import numpy as np
import tensorflow as tf
from scipy import spatial
from settings import AWS,INDEX_PATH,CONFIG_PATH,DATA_PATH,DONE_DATA_PATH,BUCKET_NAME,PREFIX
from settings import SQLITE_PATH,INDEX_RUN,CRAWL_RUN,SQLDB_NAME,BATCH_SIZE
from os.path import basename



try:
    from settings import DEMO
except ImportError:
    DEMO = None
    pass
from tensorflow.python.platform import gfile
from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='logs/worker.log',
                    filemode='a')

DIMENSIONS = 2048
PROJECTIONBITS = 16
ENGINE = Engine(DIMENSIONS, lshashes=[RandomBinaryProjections('rbp', PROJECTIONBITS,rand_seed=2611),
                                      RandomBinaryProjections('rbp', PROJECTIONBITS,rand_seed=261),
                                      RandomBinaryProjections('rbp', PROJECTIONBITS,rand_seed=26)])



class NodeLookup(object):
    def __init__(self):
        label_lookup_path = CONFIG_PATH+'/data/imagenet_2012_challenge_label_map_proto.pbtxt'
        uid_lookup_path = CONFIG_PATH+'/data/imagenet_synset_to_human_label_map.txt'
        self.node_lookup = self.load(label_lookup_path, uid_lookup_path)

    def load(self, label_lookup_path, uid_lookup_path):
        proto_as_ascii_lines = gfile.GFile(uid_lookup_path).readlines()
        uid_to_human = {}
        p = re.compile(r'[n\d]*[ \S,]*')
        for line in proto_as_ascii_lines:
            parsed_items = p.findall(line)
            uid = parsed_items[0]
            human_string = parsed_items[2]
            uid_to_human[uid] = human_string
        node_id_to_uid = {}
        proto_as_ascii = gfile.GFile(label_lookup_path).readlines()
        for line in proto_as_ascii:
            if line.startswith('  target_class:'):
                target_class = int(line.split(': ')[1])
            if line.startswith('  target_class_string:'):
                target_class_string = line.split(': ')[1]
                node_id_to_uid[target_class] = target_class_string[1:-2]
        node_id_to_name = {}
        for key, val in node_id_to_uid.items():
            if val not in uid_to_human:
                tf.logging.fatal('Failed to locate: %s', val)
            name = uid_to_human[val]
            node_id_to_name[key] = name
        return node_id_to_name

    def id_to_string(self, node_id):
        if node_id not in self.node_lookup:
            return ''
        return self.node_lookup[node_id]


def load_network(png=False):
    with gfile.FastGFile(CONFIG_PATH+'/data/network.pb', 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        if png:
            png_data = tf.placeholder(tf.string, shape=[])
            decoded_png = tf.image.decode_png(png_data, channels=3)
            _ = tf.import_graph_def(graph_def, name='incept',input_map={'DecodeJpeg': decoded_png})
            return png_data
        else:
            _ = tf.import_graph_def(graph_def, name='incept')


def load_index():
    index,files,findex = [],{},0
    print "Using index path : {}".format(INDEX_PATH+"*.npy")
    for fname in glob.glob(INDEX_PATH+"*.npy"):
        logging.info("Starting {}".format(fname))
        try:
            t = np.load(fname)
            if max(t.shape) > 0:
                index.append(t)
            else:
                raise ValueError
        except:
            logging.error("Could not load {}".format(fname))
            pass
        else:
            for i,f in enumerate(file(fname.replace(".feats_pool3.npy",".files")).readlines()):
                files[findex] = f.strip()
                ENGINE.store_vector(index[-1][i,:],"{}".format(findex))
                findex += 1
            logging.info("Loaded {}".format(fname))
    index = np.concatenate(index)
    return index,files


def nearest(query_vector,index,files,n=12):
    query_vector= query_vector[np.newaxis,:]
    temp = []
    dist = []
    logging.info("started query")
    for k in xrange(index.shape[0]):
        temp.append(index[k])
        if (k+1) % 50000 == 0:
            temp = np.transpose(np.dstack(temp)[0])
            dist.append(spatial.distance.cdist(query_vector,temp))
            temp = []
    if temp:
        temp = np.transpose(np.dstack(temp)[0])
        dist.append(spatial.distance.cdist(query_vector,temp))
    dist = np.hstack(dist)
    ranked = np.squeeze(dist.argsort())
    logging.info("query finished")
    return [files[k] for i,k in enumerate(ranked[:n])]


def nearest_fast(query_vector,index,files,n=12):
    return [files[int(k)] for v,k,d in ENGINE.neighbours(query_vector)[:n]]


def get_batch(path,batch_size = 1000):
    """
    Args:
        path: directory containing images
    Returns: Generator with dictionary  containing image_file_nameh : image_data, each with size =  BUCKET_SIZE
    """
    path += "/*"
    image_data = {}
    logging.info("starting with path {}".format(path))
    for i,fname in enumerate(glob.glob(path)):
        try:
            image_data[fname] = gfile.FastGFile(fname, 'rb').read()
        except:
            logging.info("failed to load {}".format(fname))
            pass
        if (i+1) % batch_size == 0:
            logging.info("Loaded {}, with {} images".format(i,len(image_data)))
            yield image_data
            image_data = {}
    yield image_data


def move_files_updatedb(files, feat_fname, files_name):

    print "Making entires into sqllite db for indexed files of count : " + str(BATCH_SIZE) + '....'
    logging.info("Making entires into sqllite db for indexed files of count : " + str(BATCH_SIZE) + '....')
    #----------------------- sqllite3 connection ---------------------------
    sqlitePath = SQLITE_PATH + SQLDB_NAME
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
    sqlInsert = "Insert into IndexImages (id, imgpath, imgfilename, indexpath, npyfilename, npyfilelist, indexrun) Values(?, ?, ?, ?, ?, ?, ?)"
    npyfilename = basename(feat_fname)
    npyfilelist = basename(files_name)  

    count = 0
    for each in files:
        
        #----- prep variables ---------------------------------
        imgId = os.path.splitext(basename(each))[0]
        imgFileName = basename(each)
        #------------------------- insret into sqllite ------------------------------------
        try:
            with conn:
                conn.execute(sqlInsert, (imgId, DATA_PATH, imgFileName, INDEX_PATH, npyfilename, npyfilelist, INDEX_RUN))
                count = count + 1
        except sqlite3.Error as inte:
            print inte.message, imgId

    print "Made " + str(count) +" entires into sqllite db for indexed files"
    logging.info("Made " + str(count) +" entires into sqllite db for indexed files")


def move_indexed_files(DONE_DATA_PATH, files):
    print 'Moving processed files of count : '+ str(BATCH_SIZE)
    count = 0
    for each in files:
        try:
            shutil.move(each, DONE_DATA_PATH)
            count = count+1
        except shutil.Error as err:
            print err.message
    print 'Moved successfully ' + str(count) + ' files '
    logging.info('Moved successfully ' + str(count) + ' files ')


def store_index(features,files,count,index_dir,bucket_name=BUCKET_NAME,prefix=PREFIX):
    feat_fname = "{}/{}-{}.feats_pool3.npy".format(index_dir,CRAWL_RUN,count)
    files_fname = "{}/{}-{}.files".format(index_dir,CRAWL_RUN,count)
    logging.info("storing in {}".format(index_dir))
    with open(feat_fname,'w') as feats:
        np.save(feats,np.array(features))
    with open(files_fname,'w') as filelist:
        filelist.write("\n".join(files))
    if AWS:
        os.system('aws s3 cp {} s3://{}/{}_index/ --region "us-east-1"'.format(feat_fname,bucket_name,prefix))
        os.system('aws s3 cp {} s3://{}/{}_index/ --region "us-east-1"'.format(files_fname,bucket_name,prefix))
        logging.info("uploaded {} and {} to s3://{}/{}_index/ ".format(feat_fname,files_fname,bucket_name,prefix))
    move_files_updatedb(files, feat_fname, files_fname)
    move_indexed_files(DONE_DATA_PATH, files)  


def extract_features(image_data,sess):
    pool3 = sess.graph.get_tensor_by_name('incept/pool_3:0')
    features = []
    files = []
    for fname,data in image_data.iteritems():
        try:
            pool3_features = sess.run(pool3,{'incept/DecodeJpeg/contents:0': data})
            features.append(np.squeeze(pool3_features))
            files.append(fname)
        except:
            logging.error("error while processing fname {}".format(fname))
    return features,files


def download(filename):
    if DEMO:
        command = 'aws s3api get-object --bucket aub3visualsearch --key "{}/{}" --request-payer requester appcode/static/examples/{}'.format(DEMO,filename,filename)
        logging.info(command)
        os.system(command)
    else:
        os.system("cp {}/{} appcode/static/examples/{}".format(DATA_PATH,filename.split("/")[-1],filename.split("/")[-1])) # this needlessly slows down the code, handle it elegantly by using the same directory as static dir in flask.


def getsqlRes(idList):
    
    retList = []
    #----------------------- sqllite3 connection ---------------------------
    sqlitePath = SQLITE_PATH + SQLDB_NAME
    try:
        conn = sqlite3.connect(sqlitePath).cursor()
        print 'opened ' + sqlitePath + ' successfully'

    except sqlite3.Error as connError:
        print connError.message
        print 'Exiting App'
        # return None
        return retList
    #-------------------------------------------------------------------------    
    
    sqlInsert = "Select * from SellImages where id = ?"

    #idList = ['71851375.jpg', '71820714.jpg', '71821009.jpg', '71828693.jpg', '71834857.jpg', '71824377.jpg', '71842809.jpg', '71826205.jpg', '71839376.jpg', '71832426.jpg', '71833280.jpg', '71833201.jpg']
    
	
    for count in range (0,len(idList)) :
        #------------------------- insret into sqllite ------------------------------------
        try:
            res = conn.execute(sqlInsert, [idList[count][:-4]])
            fetch = res.fetchone()
        except sqlite3.Error as inte:
            print inte.message, idList[count]
        
        if fetch is None:
            # {k[0]: None for k in fetch.description}
            # do nothing 
            pass
        else:
           retList.append({k[0]: v for k, v in list(zip(res.description, fetch))})

    #print retList
    if conn:
        conn.close()
        del conn

    return retList

    



    
    