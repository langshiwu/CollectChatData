#encoding:utf-8
import itchat as it
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

@it.msg_register(it.content.TEXT)
def process(msg):
    print(msg.text)

@it.msg_register(it.content.TEXT, isGroupChat=True)
def group_msg(msg):
    print(msg)
it.auto_login(hotReload=True)
friends=it.search_friends()
chatrooms =it.search_chatrooms()
print friends.core.memberList[0].UserName
it.run()
print('ok')