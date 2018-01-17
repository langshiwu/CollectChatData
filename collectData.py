#encoding:utf-8
import MySQLdb
import itchat as it
import datetime
import sys
import base64 as b
from User import User
reload(sys)
sys.setdefaultencoding('utf-8')

#OOB
mainObject = User()


#sql
sel_user_by_nick= 'select * from luzhibot_user where nickName64 = %s'
sel_friend_by_info='select * from luzhibot_friend where nickName64 = %s and remarkName = %s and sex = %s and centralId = %s'
sel_chatroom_by_info='select * from luzhibot_chatroom where chatRoomNickName = %s and personNum = %s and centralId = %s'

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
        charset = 'utf8mb4',
)
if conn :
    cur = conn.cursor()
else :
    exit()

#itchat  login and personly text messages
@it.msg_register(it.content.TEXT)
def process_msg(msg):
    if msg.text=='login' and not mainObject.get_loginstatus():#login
        user=it.search_friends(userName=msg.FromUserName)
        if user :
            try :
                count=cur.execute(sel_user_by_nick, [b.b64encode(user.nickName)])
                if count == 1:
                    it.send_msg('login successfully',toUserName='filehelper')

                elif count ==0:
                    cur.execute(ins_user , [user.userName,'','',b.b64encode(user.nickName),user.remarkName,user.HeadImgUrl,user.signature,user.sex])#register new user
                    conn.commit()
                    it.send_msg('register and first logged in  successfully ', toUserName='filehelper')
                else:
                    it.send_msg('login failed','filerhelper')
            except Exception:
                print(Exception)
                it.send_msg('login failed','filehelper')

            count = cur.execute(sel_user_by_nick, [b.b64encode(user.nickName)])
            centralId = cur.fetchone()[0]

            #导入所有friend信息
            friendsList = user.core.memberList
            chatroomsList = user.core.chatroomList
            mainObject.set_all(chatroomsList,friendsList,True,user.nickName,user.userName,user.remarkName,user.signature,user.sex)

            friends ,chatrooms =[],[]
            for friend in friendsList:
                count = cur.execute(sel_friend_by_info,(b.b64encode(friend.nickName),friend.remarkName,friend.sex,str(centralId)))
                if count ==0:
                    friends.append((friend.userName,'',b.b64encode(friend.nickName),friend.remarkName,friend.HeadImgUrl,str(friend.sex),str(centralId)))
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
                count = cur.execute(sel_chatroom_by_info,(b.b64encode(chatroom.NickName),chatroom.MemberCount,str(centralId)))
                if count == 0:
                    if not hasattr(chatroom,'ChatRoomOwner'):
                        setattr(chatroom,'ChatRoomOwner','')
                    chatrooms.append((chatroom.UserName,chatroom.MemberCount,b.b64encode(chatroom.NickName),str(centralId),chatroom.ChatRoomOwner))
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
        cur.execute(ins_dailog,('','Text',msg.text,b.b64encode(sender.NickName),b.b64encode(receiver.NickName),dt))
        conn.commit()


    else:
        print (msg.text)

#itchat grouply text message
@it.msg_register(it.content.TEXT,isGroupChat=True)
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
        cur.execute(ins_dailog,('','GroupText',msg.text,b.b64encode(sender.NickName),b.b64encode(receiver.NickName),dt))
        conn.commit()

def loginlookup():
    it.send_msg('please send login to filehelper',toUserName='filehelper')
    return


def saybye():
    it.send_msg('see you',toUserName='filehelper')
    return


it.auto_login(hotReload=True,loginCallback=loginlookup,exitCallback=saybye)
it.run()



