__author__ = 'aub3'
import os,sys,logging
sys.path.insert(1, os.path.join(os.path.abspath('.'), ''))
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='logs/server.log',
                    filemode='a')

from appcode import app
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=9000,debug=False)
