#encoding:utf-8
import MySQLdb
import itchat as it
import datetime
import sys
import base64 as b
from User import User
from itchat.content import *
reload(sys)
sys.setdefaultencoding('utf-8')

#OOB
mainObject = User()


#sql
sel_user_by_nick= 'select * from luzhibot_user where nickName = %s'
sel_friend_by_info='select * from luzhibot_friend where nickName = %s and remarkName = %s and sex = %s and centralId = %s'
sel_chatroom_by_info='select * from luzhibot_chatroom where chatRoomNickName = %s and personNum = %s and centralId = %s'
sel_dailog_by_info='select * from  luzhibot_dailog where msgPath=%s and msgType=%s and msg=%s and senderNick=%s and receiverNick=%s and time=%s'

ins_user='insert into luzhibot_user(userName,passWord,weixinId,nickName,remarkName,headImage,signature,sex) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
ins_friends='insert into luzhibot_friend(userName,weixinId,nickName,remarkName,headImage,sex,centralId) VALUES (%s,%s,%s,%s,%s,%s,%s)'
ins_chatroom='insert into luzhibot_chatroom(chatRoomUserName,personNum,chatRoomNickName,centralId,ownerUserName) VALUES (%s,%s,%s,%s,%s)'
ins_dailog='insert into luzhibot_dailog(msgPath,msgType,msg,senderNick,receiverNick,time)VALUES (%s,%s,%s,%s,%s,%s)'
conn = MySQLdb.connect(
        host = '127.0.0.1',
        port = 3306,
        user = 'root',
        passwd = '123456',
        db = 'wechat',
        charset='utf8mb4'
)
if conn :
    cur = conn.cursor()
    cur.execute("set names utf8mb4")
    cur.execute("SET CHARACTER SET utf8mb4")
    cur.execute("SET character_set_connection=utf8mb4")
    conn.commit()
else :
    exit()

#itchat  login and personly text messages
@it.msg_register(TEXT)
def process_msg(msg):
    if msg.text=='login' and not mainObject.get_loginstatus():#login
        user=it.search_friends(userName=msg.FromUserName)
        if user :
            try :
                count=cur.execute(sel_user_by_nick, [user.nickName])
                if count == 1:
                    it.send_msg('login successfully',toUserName='filehelper')

                elif count ==0:
                    cur.execute(ins_user , [user.userName,'','',user.nickName,user.remarkName,user.HeadImgUrl,user.signature,user.sex])#register new user
                    conn.commit()
                    it.send_msg('register and first logged in  successfully ', toUserName='filehelper')
                else:
                    it.send_msg('login failed','filerhelper')
            except Exception:
                print(Exception)
                it.send_msg('login failed','filehelper')

            count = cur.execute(sel_user_by_nick, [user.nickName])
            centralId = cur.fetchone()[0]

            #导入所有friend信息
            friendsList = user.core.memberList
            chatroomsList = user.core.chatroomList
            mainObject.set_all(chatroomsList,friendsList,True,user.nickName,user.userName,user.remarkName,user.signature,user.sex)

            friends ,chatrooms =[],[]
            for friend in friendsList:
                count = cur.execute(sel_friend_by_info,(friend.nickName,friend.remarkName,friend.sex,str(centralId)))
                if count ==0:
                    friends.append((friend.userName,'',friend.nickName,friend.remarkName,friend.HeadImgUrl,str(friend.sex),str(centralId)))
                elif count ==1:
                    continue
            if len(friends)>0:
                cur.executemany(ins_friends,friends)
                conn.commit()
            it.send_msg("load friends'information successful",'filehelper')

            #导入所有chatroom信息
            # sel_chatroom_by_info='select * from luzhibot_chatroom where chatRoomNickName = %s and personNum = %s and centralId = %s and ownerId = %s
            # 'ins_chatroom='insert into luzhibot_chatroom(chatRoomUserName,personNum,chatRoomNickName,centralId,ownerUserName) VALUES (%s,%s,%s,%s,%s)'
            for chatroom in chatroomsList:
                count = cur.execute(sel_chatroom_by_info,(chatroom.NickName,chatroom.MemberCount,str(centralId)))
                if count == 0:
                    if not hasattr(chatroom,'ChatRoomOwner'):
                        setattr(chatroom,'ChatRoomOwner','')
                    chatrooms.append((chatroom.UserName,chatroom.MemberCount,chatroom.NickName,str(centralId),chatroom.ChatRoomOwner))
                elif count == 1:
                    continue
            if len(chatrooms)>0:
                cur.executemany(ins_chatroom,chatrooms)
                conn.commit()
            it.send_msg('load chatrooms\'information successfully','filehelper')


    elif msg.text=='login' and mainObject.get_loginstatus():
        it.send_msg('already logged in','filehelper')


    elif msg.text=='exit'and mainObject.get_loginstatus():
        mainObject.change_loginstatus()


    elif mainObject.get_loginstatus() and not msg.ToUserName=='filehelper':
        sender=it.search_friends(userName=msg.FromUserName)
        receiver=it.search_friends(userName=msg.ToUserName)
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(ins_dailog,('','Text',msg.text,sender.NickName,receiver.NickName,dt))
        conn.commit()
        #验证emoji
        # count=cur.execute(sel_dailog_by_info,['','Text',msg.text,sender.NickName,receiver.NickName,dt])
        # if count ==1:
        #     it.send_msg(cur.fetchone()[3],'filehelper')

    else:
        print (msg.text)

#itchat grouply text message
@it.msg_register(TEXT,isGroupChat=True)
def process_group(msg):
    actualNickName=it.search_friends(userName=msg.ActualUserName).NickName
    if mainObject.get_loginstatus():
        if b.b64encode(mainObject.get_nickname())==b.b64encode(actualNickName):
            sender=it.search_friends(userName=msg.FromUserName)
            receiver = it.search_chatrooms(userName=msg.ToUserName)
        else:
            sender=it.search_friends(userName=msg.ActualUserName)
            receiver = it.search_chatrooms(userName=msg.FromUserName)

        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(ins_dailog,('','GroupText',msg.text,sender.NickName,receiver.NickName,dt))
        conn.commit()

#itchat  personly other type text message
@it.msg_register([SHARING,MAP])
def process_sm(msg):
    if mainObject.get_loginstatus():
        sender=it.search_friends(userName=msg.FromUserName)
        receiver=it.search_friends(userName=msg.ToUserName)
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(ins_dailog,(msg.Url,msg.Type,msg.text,sender.NickName,receiver.NickName,dt))
        conn.commit()
        it.send_msg('%s:%s:%s'%(msg.Type,msg.text,msg.Url),'filehelper')

@it.msg_register(CARD)
def process_card(msg):
    if mainObject.get_loginstatus():
        sender=it.search_friends(userName=msg.FromUserName)
        receiver=it.search_friends(userName=msg.ToUserName)
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(ins_dailog,('',msg.Type,msg.text.NickName,sender.NickName,receiver.NickName,dt))
        conn.commit()
        it.send_msg('%s:%s'%(msg.Type,msg.Text.NickName),'filehelper')

@it.msg_register(NOTE)
def process_note(msg):
    if mainObject.get_loginstatus():
        sender=it.search_friends(userName=msg.FromUserName)
        receiver=it.search_friends(userName=msg.ToUserName)
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(ins_dailog,('',msg.Type,msg.Text,sender.NickName,receiver.NickName,dt))
        conn.commit()
        it.send_msg('%s:%s'%(msg.Type,msg.text),'filehelper')

@it.msg_register(ATTACHMENT)
def process_file(msg):
    if mainObject.get_loginstatus():
        sender=it.search_friends(userName=msg.FromUserName)
        receiver=it.search_friends(userName=msg.ToUserName)
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(ins_dailog,('',msg.Type,msg.FileName,sender.NickName,receiver.NickName,dt))
        conn.commit()
        it.send_msg('%s:%s'%(msg.Type,msg.text),'filehelper')


#itchat  grouply other type text message
@it.msg_register([SHARING,MAP],isGroupChat=True)
def group_process_sm(msg):
    if mainObject.get_loginstatus():
        actualNickName = it.search_friends(userName=msg.ActualUserName).NickName
        if mainObject.get_loginstatus():
            if b.b64encode(mainObject.get_nickname()) == b.b64encode(actualNickName):
                sender = it.search_friends(userName=msg.FromUserName)
                receiver = it.search_chatrooms(userName=msg.ToUserName)
            else:
                sender = it.search_friends(userName=msg.ActualUserName)
                receiver = it.search_chatrooms(userName=msg.FromUserName)

        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(ins_dailog,(msg.Url,'Group'+msg.Type,msg.text,sender.NickName,receiver.NickName,dt))
        conn.commit()
        it.send_msg('%s:%s:%s'%('Group'+msg.Type,msg.text,msg.Url),'filehelper')

@it.msg_register(CARD,isGroupChat=True)
def group_process_card(msg):
    if mainObject.get_loginstatus():
        actualNickName = it.search_friends(userName=msg.ActualUserName).NickName
        if mainObject.get_loginstatus():
            if b.b64encode(mainObject.get_nickname()) == b.b64encode(actualNickName):
                sender = it.search_friends(userName=msg.FromUserName)
                receiver = it.search_chatrooms(userName=msg.ToUserName)
            else:
                sender = it.search_friends(userName=msg.ActualUserName)
                receiver = it.search_chatrooms(userName=msg.FromUserName)

        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(ins_dailog,('','Group'+msg.Type,msg.text['NickName'],sender.NickName,receiver.NickName,dt))
        conn.commit()
        it.send_msg('%s:%s'%('Group'+msg.Type,msg.text['NickName']),'filehelper')

@it.msg_register(NOTE,isGroupChat=True)# 通知信息由群发出 ，由user接收
def group_process_note(msg):
    if mainObject.get_loginstatus():
        sender = it.search_chatrooms(userName=msg.FromUserName)
        receiver = it.search_friends(userName=msg.ToUserName)

        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(ins_dailog,('','Group'+msg.Type,msg.Text,sender.NickName,receiver.NickName,dt))
        conn.commit()
        it.send_msg('%s:%s'%('Group'+msg.Type,msg.text),'filehelper')

@it.msg_register(ATTACHMENT,isGroupChat=True)
def group_process_file(msg):
    if mainObject.get_loginstatus():
        actualNickName = it.search_friends(userName=msg.ActualUserName).NickName
        if mainObject.get_loginstatus():
            if b.b64encode(mainObject.get_nickname()) == b.b64encode(actualNickName):
                sender = it.search_friends(userName=msg.FromUserName)
                receiver = it.search_chatrooms(userName=msg.ToUserName)
            else:
                sender = it.search_friends(userName=msg.ActualUserName)
                receiver = it.search_chatrooms(userName=msg.FromUserName)

        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(ins_dailog,('','Group'+msg.Type,msg.FileName,sender.NickName,receiver.NickName,dt))
        conn.commit()
        it.send_msg('%s:%s'%('Group'+msg.Type,msg.FileName),'filehelper')



def loginlookup():
    it.send_msg('please send login to filehelper',toUserName='filehelper')
    return


def saybye():
    it.send_msg('see you',toUserName='filehelper')
    return


it.auto_login(hotReload=True,loginCallback=loginlookup,exitCallback=saybye)
it.run()



