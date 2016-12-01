__author__ = 'aub3'
import jinja2,os
TEST = True
DBNAME = 'visiondb'
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
S3BUCKET = "" #bucket to store results
CONFIG_PATH = __file__.split('__init__.py')[0]
EC2_MODE = True
