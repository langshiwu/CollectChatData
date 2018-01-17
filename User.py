#encoding:utf-8
import base64

class User(object):
    def __init__(self):
        self._chatrooms=[]
        self._friends=[]
        self._loginstatus=False
        self._nickName=''
        self._userName=''
        self._remarkName=''
        self._signature=''
        self._sex=''

    def set_all(self,chatrooms,friends,loginstatus,nickname,username,remarkname,signature,sex):
        self._chatrooms=chatrooms
        self._friends=friends
        self._loginstatus=loginstatus
        self._nickName=nickname
        self._userName=username
        self._remarkName=remarkname
        self._sex=sex
        self._signature=signature

    def change_loginstatus(self):
        self._loginstatus = not self._loginstatus

    def get_loginstatus(self):
        return self._loginstatus

    def get_chatrooms(self):
        return self._chatrooms

    def get_friends(self):
        return self._friends

    def get_sex(self):
        return self._sex

    def get_signature(self):
        return self._signature

    def get_nickname(self):
        return self._nickName




