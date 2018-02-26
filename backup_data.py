import os
import datetime
import tarfile

import boto3



KEY = 'XXX'
SECRET = 'XXX'
HOST = 'sos-ch-dk-2.exo.io'
BUCKET_NAME = 'alob'
DB_USER = 'alob'
DB_PASS = 'alob'
DB = 'alob'

DATA_KEY = 'data/{}'


def backup():
    '''
    Backup the data and push to Single Object Storage (SOS)
    '''

    print('Backup started: {}'.format(datetime.datetime.now()))

    BACKUP_FILE = '{}_data-{}.tar.gz'.format(DB, datetime.datetime.now().isoformat().rsplit('.')[0])
    print('Backup data to {}'.format(BACKUP_FILE))

    tar = tarfile.open(BACKUP_FILE, 'w:gz')
    tar.add('data/media')
    tar.close()
    s3 = boto3.resource('s3',
                        aws_access_key_id=KEY, 
                        aws_secret_access_key=SECRET, 
                        endpoint_url='https://{}'.format(HOST))

    try:
        s3.create_bucket(Bucket=BUCKET_NAME)
    finally:
        bucket = s3.Bucket(BUCKET_NAME)
    
    #
    # backup to data
    #
    bucket.put_object(Key=DATA_KEY.format(BACKUP_FILE), Body=open(BACKUP_FILE, 'rb'))
     
    print('File written to misc buckets.')

    #
    # Delete the dump
    #
    os.unlink(BACKUP_FILE)


if __name__ == '__main__':

    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    print('Change to directory: {}'.format(ROOT_DIR))
    os.chdir(ROOT_DIR)

    backup()
