# -*- coding: utf-8 -*-
"""
wechat cient using web interface
by 木鱼
"""
import time
import requests
import re
import os
import shutil
import xml.dom.minidom
import json
import random
from collections import ChainMap
class WeChat(object):
	"""wechat web interface Class"""
	def __init__(self):
		super(WeChat, self).__init__()
		self.jar = requests.cookies.RequestsCookieJar()
		self.uuid = ''
		self.code = ''
		self.base_url = ''
		self.redirect_url = ''
		self.special_users = ['weixin','filehelper']
		self.public_users_list = dict()
		self.special_users_list = dict()
		self.group_list = dict()
		self.contact_list = dict()
		self.all_contact = ChainMap()
		self.user_name_pending = set()
		self.user = ''
		self.sync_key = ''
		self.sync_key_for_syn= ''
		self.conversation =dict()

		self.skey = ''
		self.sid = ''
		self.uin = ''
		self.pass_ticket = ''
		self.base_request = {}




		self.get_icon_base_url = 'https://wx.qq.com'
		self.set_cookies = 'Set-Cookie'
		self.deviceId = 'e455251312409684'
		self.syncheck_url_base = 'https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck'
		self.user_agent =  'Mozilla/5.0 (Windows NT 10; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
		self.path_QR = os.path.join(os.getcwd(), "qrcode.jpg")
		self.appid = 'wx782c26e4c19acffb'
		self.lang = 'zh_CN'
		self.headers = {'User-Agent' : self.user_agent,
						'Connection': 'keep-alive',
						'ContentType': 'application/json; charset=UTF-8',}

	def _Cookiesupdata(self,r):
	    if(self.set_cookies in list(r.headers.keys())):
	        regs=r'(\S+)=(\S+); Domain=(\S+); Path=(\S+); Expires=(.+?GMT),'
	        cookies_needtoset=re.findall(regs,r.headers[self.set_cookies])
	        for item in cookies_needtoset:
	            self.jar.set(item[0],item[1],domain=item[2],path=item[3])


	def _update_contact_list(self,pending_list):
		for i in range(0,len(pending_list),1):
		    contact= pending_list[i]
		    if contact['UserName'] in self.all_contact.keys():
		        print("This contact is already in list",contact['UserName'],'Update it ')	    
		    if contact['UserName'] in self.special_users:
		        self.special_users_list[contact['UserName']] = contact
		    elif  contact['VerifyFlag'] & 8 != 0:
		        self.public_users_list[contact['UserName']] = contact
		    elif '@@' in contact['UserName']:
		        self.group_list[contact['UserName']] = contact
		    else:
		        self.contact_list[contact['UserName']] = contact
		self.all_contact =  ChainMap(self.special_users_list , self.public_users_list , self.group_list , self.contact_list , {self.user['UserName'] : self.user})

	def get_uuid(self):
		url_get_uuid = 'https://login.weixin.qq.com/jslogin'
		param_get_uuid ={
                 'appid':self.appid,
                 'fun':'new',
                 'lang':self.lang,
                 '_':int(time.time()),        
		}
		data_uuid=requests.get(url_get_uuid,params=param_get_uuid,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(data_uuid)
		regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
		pm = re.search(regx, data_uuid.text)
		self.code = pm.group(1)
		self.uuid = pm.group(2)

	def get_QR(self):
		url_get_QR='https://login.weixin.qq.com/qrcode/'+self.uuid
		param_get_QR = {
		          't': 'webwx',
		          '_': int(time.time())
		}
		data_QR=requests.get(url_get_QR,params=param_get_QR,stream=True,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(data_QR)
		with open(self.path_QR , 'wb') as f:
		    data_QR.raw.decode_content = True
		    shutil.copyfileobj(data_QR.raw, f)
		os.startfile(self.path_QR )

	def get_redirect_url(self):
		url_qury='https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login'
		qury_param = {
		              'tip':'0',
		              'uuid':self.uuid,
		              'loginicon':'true',
		              '_':int(time.time()),
		}
		data_qury=requests.get(url_qury,params=qury_param,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(data_qury)
		pm = re.search(r'window.code=(\d+);', data_qury.text)
		code = pm.group(1)
		while code != '200':
		    data_qury=requests.get(url_qury,params=qury_param,cookies=requests.utils.dict_from_cookiejar(self.jar))
		    self._Cookiesupdata(data_qury)
		    pm = re.search(r'window.code=(\d+);', data_qury.text)
		    code = pm.group(1)
		pm = re.search(r'window.redirect_uri="(\S+?)";', data_qury.text)
		self.redirect_url = pm.group(1) + "&fun=new&version=v2"
		self.base_url = self.redirect_url[:self.redirect_url.rfind('/')]

	def get_info(self):
		data_info=requests.get(self.redirect_url,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(data_info)
		doc = xml.dom.minidom.parseString(data_info.text)
		root = doc.documentElement
		for node in root.childNodes:
		    if node.nodeName == 'skey':
		            self.skey = node.childNodes[0].data
		    elif node.nodeName == 'wxsid':
		            self.sid = node.childNodes[0].data
		    elif node.nodeName == 'wxuin':
		            self.uin = node.childNodes[0].data
		    elif node.nodeName == 'pass_ticket':
		            self.pass_ticket = node.childNodes[0].data
		if not all((self.skey,self.sid,self.uin,self.pass_ticket)):
		    print('from redirect_uri got something wrong')    
		self.base_request = {
		               'Uin':int(self.uin),
		               'Sid':self.sid,
		               'Skey':self.skey,
		               'DeviceID':self.deviceId,
		}  
		
	def init_connect(self):
		url_init = self.base_url + '/webwxinit?pass_ticket=%s&r=%s' % (self.pass_ticket,int(time.time()))		
		init_payload={'BaseRequest' : self.base_request}    		
		data_inital = requests.post(url_init, json=init_payload, headers=self.headers,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(data_inital)
		data_inital_dic=json.loads(data_inital.content.decode('utf-8'))
		#self.data_inital_dic = data_inital_dic
		self.user = data_inital_dic['User']
		self.sync_key = data_inital_dic['SyncKey']
		self.sync_key_for_syn='|'.join([str(keyVal['Key'])+'_'+str(keyVal['Val']) for keyVal in self.sync_key['List']])
		init_contaclist = data_inital_dic['ContactList']
#		for i in range(0,len(init_contaclist),1):
#		    contact= init_contaclist[i]
#		    if contact['UserName'] in self.all_contact.keys():
#		        print("This contact is already in list",contact['UserName'],'Update it ')	    
#		    if contact['UserName'] in self.special_users:
#		        self.special_users_list[contact['UserName']] = contact
#		    elif  contact['VerifyFlag'] & 8 != 0:
#		        self.public_users_list[contact['UserName']] = contact
#		    elif '@@' in contact['UserName']:
#		        self.group_list[contact['UserName']] = contact
#		    else:
#		        self.contact_list[contact['UserName']] = contact
#		self.all_contact =  ChainMap(self.special_users_list , self.public_users_list , self.group_list , self.contact_list)
		self._update_contact_list(init_contaclist)
		chat_set = data_inital_dic['ChatSet'].split(str(','))
		chat_set.pop()
		self.user_name_pending.update(set(chat_set) - set(self.all_contact.keys()))


	def status_notify(self):
		url_statusnotify = self.base_url+'/webwxstatusnotify?lang=zh_CN&pass_ticket=%s' % (self.pass_ticket)
		statusnotify_load = {
							'BaseRequest': self.base_request,
							"Code": 3,
							"FromUserName": self.user['UserName'],
							"ToUserName": self.user['UserName'],
							"ClientMsgId": int(time.time())
		        			}
		data_statusnotify = requests.post(url_statusnotify, json=statusnotify_load, headers=self.headers,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(data_statusnotify)	

	def get_contact(self):
		url_getcontact = self.base_url + '/webwxgetcontact?lang=%s&pass_ticket=%s&skey=%s&r=%s&seq=0' % (self.lang,self.pass_ticket,self.skey,int(time.time()))
		data_contact = requests.get(url_getcontact,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(data_contact)
		data_contact_dic=json.loads(data_contact.content.decode('utf-8'))
		#member_count =  data_contact_dic['MemberCount']
		member_list = data_contact_dic['MemberList']
#		for i in range(0,len(member_list),1):
#		    contact= member_list[i]
#		    if contact['UserName'] in self.all_contact.keys():
#		        print("This contact is already in list",contact['UserName'])	        
#		    if contact['UserName'] in self.special_users:
#		        self.special_users_list[contact['UserName']] = contact
#		    elif  contact['VerifyFlag'] & 8 != 0:
#		        self.public_users_list[contact['UserName']] = contact
#		    elif '@@' in contact['UserName']:
#		        self.group_list[contact['UserName']] = contact
#		    else:
#		        self.contact_list[contact['UserName']] = contact
#		self.all_contact =  ChainMap(self.special_users_list , self.public_users_list , self.group_list , self.contact_list)
		self._update_contact_list(member_list)		
		self.user_name_pending -=set(self.all_contact.keys())


	def get_batch_contact(self,qury_contact_list):
		url_getbatchcontact = self.base_url + '/webwxbatchgetcontact?pass_ticket=%s&skey=%s&r=%s' % (self.pass_ticket,self.skey,int(time.time()))
		batchcontact_load = {
		                      'BaseRequest':self.base_request,
		                      'Count' : len(qury_contact_list),
		                      "List": [{"UserName": g, "EncryChatRoomId":""} for g in qury_contact_list]
		                      }
		data_batchcontact = requests.post(url_getbatchcontact,json=batchcontact_load,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(data_batchcontact)
		self.data_batchcontact = data_batchcontact
		data_batchcontact_dic=json.loads(data_batchcontact.content.decode('utf-8'))
		batch_contact_list = data_batchcontact_dic['ContactList']
		self._update_contact_list(batch_contact_list)
		self.user_name_pending -=set(self.all_contact.keys())


	def syn_check(self):
		url_syncheck = 'https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck'
		syncheck_param = {
        				'r':int(time.time()),
                  		'sid':self.sid,
                  		'uin': self.uin,
                  		'skey' : self.skey,
                  		'deviceid': self.deviceId,
                  		'synckey' : self.sync_key_for_syn,
                  		'_': int(time.time()),
                  		}
		data_syncheck=requests.get(url_syncheck,params=syncheck_param,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(data_syncheck)
		#print(data_syncheck.text)
		regx = r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}'		
		pm = re.search(regx, data_syncheck.text)
		self.syn_ckeck_result={'retcode':pm.group(1),'selector':pm.group(2)}


	def web_wx_sync(self):
		''' get message from web'''
		url_syn = self.base_url+'/webwxsync?sid=%s&skey%s&lang=%s&pass_ticket=%s' %(self.sid,self.skey,self.lang,self.pass_ticket)
		syn_loard={'BaseRequest' : self.base_request,
		          'SyncKey' :  self.sync_key,
		          'rr' : '1734374280',                  
		          }
		data_syn=requests.post(url_syn, json=syn_loard, headers=self.headers,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(data_syn)
		data_syn_dic=json.loads(data_syn.content.decode('utf-8'))
		self.data_syn_dic = data_syn_dic
		self.sync_key = data_syn_dic['SyncKey']
		self.sync_key_for_syn='|'.join([str(keyVal['Key'])+'_'+str(keyVal['Val']) for keyVal in self.sync_key['List']])
		self.data_syn_dic = data_syn_dic
		for add_msg in data_syn_dic['AddMsgList']:
			if add_msg['StatusNotifyUserName'] != '':
				self.user_name_pending.update(set(add_msg['StatusNotifyUserName'].split(str(',')))-self.all_contact.keys())




	def send_message(self,message,to_user_name='filehelper'):
		url_sendmessage = self.base_url + '/webwxsendmsg?pass_ticket=%s&lang=%s' % (self.pass_ticket,self.lang)
		client_msg_id = str(int(time.time() * 1000)) + str(random.random())[:5].replace('.', '')
		sendmessage_load = {
		                     'BaseRequest': self.base_request,
		                     'Msg': {
		                             "Type": 1,
		                             "Content" : message,
		                             "FromUserName": self.user['UserName'],
		                             "ToUserName": to_user_name,
		                             "LocalID": client_msg_id,
		                             "ClientMsgId": client_msg_id
		                             }
		                    }
		data_sendmessage=requests.post(url_sendmessage, data=json.dumps(sendmessage_load,ensure_ascii=False).encode("utf-8"), headers=self.headers,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(data_sendmessage)

	def get_icon(self,username):
		if username not in 	self.all_contact.keys():	         
			return
		else:
			url_get_icon = self.get_icon_base_url + self.all_contact[username]['HeadImgUrl']

		data_icon=requests.get(url_get_icon,stream=True,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(data_icon)
		icon_name = "icon_%s_.jpg" % (self.all_contact[username]['PYInitial'])
		path_icon = os.path.join(os.getcwd(), icon_name)
		with open(path_icon , 'wb') as f:
		    data_icon.raw.decode_content = True
		    shutil.copyfileobj(data_icon.raw, f)
		os.startfile(path_icon )

	def get_content_from_web(self,data_web):
		for item in data_web['AddMsgList']:
			if item['ToUserName'] in self.conversation.keys():
				self.conversation[item['ToUserName']]['message'].append({'time':item['CreateTime'],'from':self.all_contact[item['FromUserName']]['NickName']+item['FromUserName'],'content':item['Content']})
			elif item['ToUserName'] in self.all_contact.keys():
				self.conversation[item['ToUserName']]={'nickname':self.all_contact[item['ToUserName']]['NickName'], 'message':[{'time':item['CreateTime'],'from':self.all_contact[item['FromUserName']]['NickName']+item['FromUserName'],'content':item['Content']}]}
			else:
				print('recive a message which sender to strange')

#print(__name__)

if __name__ == '__main__':
	w=WeChat();

	w.get_uuid()
	w.get_QR()
	w.get_redirect_url()
	w.get_info()
	w.init_connect()
	w.status_notify()
	w.get_contact()
	w.syn_check()
	w.web_wx_sync()
	w.get_content_from_web(w.data_syn_dic)
	w.get_batch_contact(list(w.user_name_pending))
	w.send_message('哇哇@'+str(int(time.time())))
	w.get_icon('weixin')
