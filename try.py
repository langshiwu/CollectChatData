#encoding:utf-8
import itchat as it
from  itchat.content import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# TEXT       = 'Text'
# MAP        = 'Map'
# CARD       = 'Card'
# NOTE       = 'Note'
# SHARING    = 'Sharing'
# PICTURE    = 'Picture'
# RECORDING  = VOICE = 'Recording'
# ATTACHMENT = 'Attachment'
# VIDEO      = 'Video'
# FRIENDS    = 'Friends'
# SYSTEM     = 'System'

# @it.msg_register(TEXT, isGroupChat=True)
# def group_msg(msg):
#     print(msg)

# @it.msg_register(NOTE)
# def process_note(msg):
#     print(msg)

@it.msg_register([MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    msg.user.send('%s: %s' % (msg.type, msg.text))

@it.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    msg.download(msg.fileName)
    typeSymbol = {
        PICTURE: 'img',
        VIDEO: 'vid', }.get(msg.type, 'fil')
    return '@%s@%s' % (typeSymbol, msg.fileName)

@it.msg_register(FRIENDS)
def add_friend(msg):
    msg.user.verify()
    msg.user.send('Nice to meet you!')
it.auto_login(hotReload=True)
friends=it.search_friends()
chatrooms =it.search_chatrooms()
print friends.core.memberList[0].UserName
it.run()
print('ok')