# -*- coding: utf-8 -*-
"""
wechat cient using web interface

"""
import time
import requests
import re
import os
import shutil
import xml.dom.minidom
import json
import random

class WeChat(object):
	"""wechat web interface Class"""
	def __init__(self):
		super(WeChat, self).__init__()
		self.jar = requests.cookies.RequestsCookieJar()
		self.uuid = ''
		self.code = ''
		self.base_url = ''
		self.redirect_url = ''
		self.special_users = []
		self.public_users_list = []
		self.special_users_list = []
		self.group_list = []
		self.contact_list = []
		self.current_total_contact = set()
		self.user = ''
		self.sync_key = ''
		self.sync_key_for_syn= ''


		self.skey = ''
		self.sid = ''
		self.uin = ''
		self.pass_ticket = ''
		self.base_request = {}


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
	    if(set_cookies in list(r.headers.keys())):
	        regs=r'(\S+)=(\S+); Domain=(\S+); Path=(\S+); Expires=(.+?GMT),'
	        cookies_needtoset=re.findall(regs,r.headers[set_cookies])
	        for item in cookies_needtoset:
	            self.jar.set(item[0],item[1],domain=item[2],path=item[3])


	def get_uuid(self):
		url_get_uuid = 'https://login.weixin.qq.com/jslogin'
		param_get_uuid ={
                 'appid':appid,
                 'fun':'new',
                 'lang':lang,
                 '_':int(time.time()),        
		}
		data_uuid=requests.get(url_get_uuid,params=param_get_uuid,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(self.jar,data_uuid)
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
		self._Cookiesupdata(self.jar,data_QR)
		with open(self.path_QR , 'wb') as f:
		    data_QR.raw.decode_content = True
		    shutil.copyfileobj(data_QR.raw, f)
		os.startfile(self.path_QR )

	def get_redirect_url(self):
		url_qury='https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login'
		qury_param = {
		              'tip':'0',
		              'uuid':uuid,
		              'loginicon':'true',
		              '_':int(time.time()),
		}
		data_qury=requests.get(url_qury,params=qury_param,cookies=requests.utils.dict_from_cookiejar(self.jar))
		Cookiesupdata(self.jar,data_qury)
		pm = re.search(r'window.code=(\d+);', data_qury.text)
		code = pm.group(1)
		while code != '200':
		    data_qury=requests.get(url_qury,params=qury_param,cookies=requests.utils.dict_from_cookiejar(self.jar))
		    Cookiesupdata(self.jar,data_qury)
		    pm = re.search(r'window.code=(\d+);', data_qury.text)
		    code = pm.group(1)
		pm = re.search(r'window.redirect_uri="(\S+?)";', data_qury.text)
		self.redirect_url = pm.group(1) + "&fun=new&version=v2"
		self.base_url = redirect_url[:redirect_uri.rfind('/')]

	def get_info(self):
		data_info=requests.get(self.redirect_uri,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(self.jar,data_info)
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
		url_init = self.base_uri + '/webwxinit?pass_ticket=%s&r=%s' % (self.pass_ticket,int(time.time()))		
		init_payload={'BaseRequest' : self.BaseRequest}    		
		data_inital = requests.post(url_init, json=init_payload, headers=self.headers,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(self.jar,data_inital)
		#data_inital_dic = json.loads(data_inital.text.encode('unicode_escape').decode('string_escape'))
		data_inital_dic=json.loads(data_inital.content.decode('utf-8'))
		self.user = data_inital_dic['User']
		self.sync_key = data_inital_dic['SyncKey']
		self.sync_key_for_syn='|'.join([str(keyVal['Key'])+'_'+str(keyVal['Val']) for keyVal in self.sync_key['List']])
		init_contaclist = data_inital_dic['ContactList']
		self.current_total_contact.update([i['UserName'] for i in init_contaclist])
		for i in range(0,len(init_contaclist),1):
		    contact= init_contaclist[i]
		    if  contact['VerifyFlag'] & 8 != 0:
		        self.public_users_list.append(contact)
		    elif contact['UserName'] in special_users:
		        self.special_users_list.append(contact)
		    elif '@@' in contact['UserName']:
		        self.group_list.append(Contact)
		    else:
		        self.contact_list.append(Contact)

	def status_notify(self):
		url_statusnotify = self.base_uri+'/webwxstatusnotify?lang=zh_CN&pass_ticket=%s' % (self.pass_ticket)
		statusnotify_load = {
							'BaseRequest': self.base_request,
							"Code": 3,
							"FromUserName": self.user['UserName'],
							"ToUserName": self.user['UserName'],
							"ClientMsgId": int(time.time())
		        			}
		data_statusnotify = requests.post(url_statusnotify, json=statusnotify_load, headers=self.headers,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(self.jar,data_statusnotify)	

	def get_contact():
		url_getcontact = self.base_uri + '/webwxgetcontact?lang=%s&pass_ticket=%s&skey=%s&r=%s&seq=0' % (self.lang,self.pass_ticket,self.skey,int(time.time()))
		data_contact = requests.get(url_getcontact,cookies=requests.utils.dict_from_cookiejar(self.jar))
		Cookiesupdata(self.jar,data_contact)
		data_contact_dic=json.loads(data_contact.content.decode('utf-8'))
		member_count =  data_contact_dic['MemberCount']
		member_list = data_contact_dic['MemberList']
		for i in range(0,len(member_list),1):
		    contact= member_list[i]
		    if contact['UserName'] in self.current_total_contact:
		        print("This contact is already in list",contact['UserName'])
		        continue
		    else:
		        self.current_total_contact.add(contact['UserName'])
		    if  contact['VerifyFlag'] & 8 != 0:
		        self.public_users_lList.append(contact)
		    elif contact['UserName'] in SpecialUsers:
		        self.special_users_list.append(contact)
		    elif '@@' in contact['UserName']:
		        self.group_list.append(contact)
		    else:
		        self.contact_list.append(contact)



	def syn_check(self)
		url_syncheck = 'https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck'
		syncheck_param = {
        				'r':int(time.time()),
                  		'sid':self.sid,
                  		'uin': self.uin,
                  		'skey' : self.skey,
                  		'deviceid': self.deviceId,
                  		'synckey' : self.synckey,
                  		'_': int(time.time()),
                  		}
		data_syncheck=requests.get(url_syncheck,params=syncheck_param,cookies=requests.utils.dict_from_cookiejar(jar))
		self._Cookiesupdata(jar,data_syncheck)
		print(data_syncheck.text)


	def web_wx_sync(self)
		''' get message from web'''
		url_syn = self.base_uri+'/webwxsync?sid=%s&skey%s&lang=%s&pass_ticket=%s' %(self.sid,skey,self.lang,self.pass_ticket)
		syn_loard={'BaseRequest' : BaseRequest,
		          'SyncKey' :  SyncKey,
		          'rr' : '1734374280',                  
		          }
		data_syn=requests.post(url_syn, json=syn_loard, headers=self.headers,cookies=requests.utils.dict_from_cookiejar(self.jar))
		self._Cookiesupdata(self.jar,data_syn)
		data_syn_dic=json.loads(data_syn.content.decode('utf-8'))
		self.sync_key = data_syn_dic['SyncKey']
		self.sync_key_for_syn='|'.join([str(keyVal['Key'])+'_'+str(keyVal['Val']) for keyVal in self.sync_key['List']])

