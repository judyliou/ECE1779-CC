import os

# SECRET_KEY="\x8d\xfcg5\xfe\x00\xbe\x83\xdf>\x19\x01\xd8\xd3QP\x04\xe8\x94s\x9a.\x1a\xe2W\xfb\x93X\xa7E&_"
SECRET_KEY = 'hard to guess'

S3_BUCKET = 'ece1779-junbang-a1'
#
# S3_BUCKET = os.environ.get("S3_BUCKET")
# S3_KEY = os.environ.get("S3_ACCESS_KEY")
# S3_SECRET = os.environ.get("S3_SECRET_ACCESS_KEY")
# S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

# db_config = {'user': 'ece1779', 
#              'password': 'secret',
#              'host': '127.0.0.1',
#              'database': 'ece1779'}

# change!
db_config = {'user': 'root',
             'password': '3263025++',
             'host': '127.0.0.1',
             'database': 'newdb'}
