import sys
import os
import subprocess
import datetime
import boto3



KEY = 'XXX'
SECRET = 'XXX'
HOST = 'sos-ch-dk-2.exo.io'
BUCKET_NAME = 'alob'
DB_USER = 'alob'
DB_PASS = 'alob'
DB = 'alob'

DAILY_KEY = 'db/daily/{}'
MONTHLY_KEY = 'db/monthly/{}'


def backup():
    '''
    Backup the database and push to Single Object Storage (SOS)
    '''

    print('Backup started: {}'.format(datetime.datetime.now()))

    BACKUP_FILE = '{}_db-{}.sql'.format(DB, datetime.date.today())
    print('Backup database {}'.format(BACKUP_FILE))
    cmd = ['/usr/local/bin/docker-compose exec -T db /usr/bin/mysqldump --user={} --password={} --databases {} > {}'.format(DB_USER, DB_PASS, DB, BACKUP_FILE)]
    return_code = subprocess.call(cmd, shell=True)

    if return_code != 0 or not os.path.exists(BACKUP_FILE):
        print('Error: File {} does not exist or dump failed.'.format(BACKUP_FILE))
        sys.exit(1)

    s3 = boto3.resource('s3',
                        aws_access_key_id=KEY, 
                        aws_secret_access_key=SECRET, 
                        endpoint_url='https://{}'.format(HOST))

    try:
        s3.create_bucket(Bucket=BUCKET_NAME)
    finally:
        bucket = s3.Bucket(BUCKET_NAME)
    
    #
    # backup to daily
    #
    bucket.put_object(Key=DAILY_KEY.format(BACKUP_FILE), Body=open(BACKUP_FILE, 'rb'))
     
    print('File written to daily buckets.')

    #
    # Backup to monthly on the first day of the month
    #
    if datetime.date.today().day == 1:
        bucket.put_object(Key=MONTHLY_KEY.format(BACKUP_FILE), Body=open(BACKUP_FILE, 'rb'))
        print('File written to monthly buckets.')


    #
    # Delete the dump
    #
    os.unlink(BACKUP_FILE)

    #
    # Check daily container and delete old buckets
    #
    now = datetime.datetime.now(datetime.timezone.utc)
    for v in bucket.objects.filter(Prefix='db/daily'):
        if (now - v.last_modified).days > 20:
            print('Bucket {} deleted.'.format(v.key))
            v.delete()


if __name__ == '__main__':

    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    print('Change to directory: {}'.format(datetime.datetime.now()))
    os.chdir(ROOT_DIR)

    backup()
