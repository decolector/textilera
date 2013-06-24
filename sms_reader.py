#/usr/bin/python

from pyadb import ADB
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker

class Sms(object):
    pass


class SmsReader():
    def __init__(self, adb_path, local_sms_db = "sms/", remote_sms_db = '/data/data/com.android.providers.telephony/databases/mmssms.db'):

        self.ADB_PATH = adb_path
        # avoid using ~/ at the beginning of path
        self.phone = ADB(self.ADB_PATH)
        self.LOCAL_SMS_DB = local_sms_db + 'mmssms.db'        
        self.REMOTE_SMS_DB = remote_sms_db
        self.phone.get_remote_file(
                self.REMOTE_SMS_DB, 
                self.LOCAL_SMS_DB
                )
        self.engine = create_engine('sqlite:///%s' % self.LOCAL_SMS_DB, echo=False)
        self.metadata = MetaData(self.engine)
        self.sms_table = Table('sms', self.metadata, autoload=True)
        mapper(Sms,self.sms_table )
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        self.sms = self.session.query(Sms)
        self.messages = [msg.body for msg in self.sms]
        self.num_sms = self.sms.count()
        self.last_sms_num = self.num_sms
        self.new_sms  = []
        self.session.close()

    #copy sms database
    def update(self):
        self.phone.get_remote_file(
                self.REMOTE_SMS_DB, 
                self.LOCAL_SMS_DB 
                )
        self.sms = self.session.query(Sms)
        self.messages = [msg.body for msg in self.sms]
        self.sms_num = self.sms.count()
        if self.sms_num > self.last_sms_num:
            difference = self.sms_num - self.last_sms_num
            temp_sms = self.sms.slice(self.last_sms_num, self.sms_num).all()
            self.new_sms = [x.body for x in temp_sms]
            self.last_sms_num = self.sms_num

        self.session.close()

    def quit(self):
        self.session.close() 

