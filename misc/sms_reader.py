#/usr/bin/python

from pyadb import ADB
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker

class Sms(object):
    pass


class SmsReader():
    def __init__(self):

        self.ADB_PATH = '~/code/android-sdk/platform-tools/adb'
        # avoid using ~/ at the beginning of path
        self.phone = ADB(self.ADB_PATH)
        self.DATABASE_PATH = 'db/mmssms.db'
        self.phone.get_remote_file(
                '/data/data/com.android.telephony/databases/mmssms.db', 
                self.DATABASE_PATH
                )

        self.engine = create_engine('sqlite:///%s' % self.DATABASE_PATH, echo=False)
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
                '/data/data/com.android.telephony/databases/mmssms.db', 
                self.DATABASE_PATH
                )
        self.session.begin()
        #Session = sessionmaker(bind=self.engine)
        #self.session = Session()
        self.sms = self.session.query(Sms)
        self.messages = [msg.body for msg in self.sms]
        self.sms_num = self.sms.count()
        if self.sms_num > self.last_sms_num:
            difference = self.sms_num - self.last_sms_num
            temp_sms = self.sms.slice(self.last_sms_num, self.sms_num).all()
            self.new_sms = [x.body for x in temp_sms]

        self.session.close()     

