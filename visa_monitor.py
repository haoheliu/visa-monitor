#coding:utf -8
 

import re
from bs4 import BeautifulSoup
import urllib.request
import time

import random
import smtplib #smtp服务器
from email.mime.text import MIMEText #邮件文本


sender = "realhaoheliu@163.com"#发送方
recver = "haoheliu@outlook.com"#接收方
password = "" # 163邮箱的授权码


class Visa():
	def __init__(self):
		self.url = "https://tuixue.online/visa/?from=singlemessage&isappinstalled=0"
		self.head = ["更新时间","北京","成都","广州","上海","沈阳"]
		self.pattern = re.compile(r'<td>\S*')
		self.log = ""
		self.html = ""
		self.retry_time = 5
		self.append_log("Initializing Visa listener...")
		self.append_log("Trying to get and parser html for the first time")
		self.refresh_html()
		self.up_to_date = self.get_current()
		self.send_email(content = "Program start listening",subject = "[Visa] Program start")

	def refresh_html(self):
		self.append_log("Refreshing html...")
		response = urllib.request.urlopen(self.url)
		self.html = str(response.read().decode('utf-8'))
		code = response.getcode()
		if(code == 200):
			self.append_log("Success refresh html")
			return True
		else:
			self.append_log("Error code: ",code)
			return False

	def get_current(self):
		soup = BeautifulSoup(self.html, "html.parser",from_encoding="utf-8")
		table = soup.find_all("tr")
		currenttime = str(table[1]).split("</td>")
		date = []
		for each in currenttime:
			pat = self.pattern.findall(str(each))
			if(len(pat) != 0):
				date.append(pat[0][4:])
		return date

	def compare_date(self,prev,now):
		# format yyyy/mm/dd
		prev = prev.split("/")
		now = now.split("/")
		if(len(prev) < 3):
			return False
		if(int(prev[1])>int(now[1]) or int(prev[2])>int(now[2])):
			return True
		return False

	def append_log(self,info,log_time = True,end = "\n"):
		print(info)
		if(log_time):
			current = time.asctime(time.localtime(time.time()))
			info = str(current)+" "+info
		if(end == '\n'):
			content = info+"\n"
		else: 
			content = info
		self.log += content
		f = open('log', 'a')
		f.write(content)
		f.close()

	# append_log("Here we got!!!: "+h+"previous:"+p+"; now:"+n)
	def compare(self,prev,now):
		res_compare = []
		if(len(prev) != len(now)):
			raise ValueError("Error: internal error, prev value should have the same length as now")
		else:
			for h,p,n in zip(self.head,prev,now):
				if(self.compare_date(p,n)):
					self.append_log("Great! We got one!"+str(h)+"previous: "+str(p)+"now: "+str(n))
					res_compare.append([h,p,n])
		return res_compare

	def report(self,res_compare:list):
		if(len(res_compare) != 0):
			for each in res_compare:
				h,p,n = each
				log = "Hurry Up! We got one!"+str(h)+"previous: "+str(p)+"now: "+str(n)
				self.append_log("Send email: "+log)
				self.sendmail(content = log,subject = "[Visa] Hurry Up!!!!!!!")
				self.append_log("Email sending success")
		else:
			self.append_log("No update")


	def refresh(self):
		for i in range(self.retry_time):
			if(self.refresh_html()):
				break
			else:
				self.append_log("Retry a second time")
				continue
		now = self.get_current()
		res_compare = self.compare(self.up_to_date,now)
		self.up_to_date = now
		self.report(res_compare)

	def send_email(self,content,subject = "[Visa] New update"):
		message = MIMEText(content,"plain","utf-8")
		message['Subject'] = subject #邮件标题
		message['To'] = recver #收件人
		message['From'] = sender #发件人
		self.append_log("Send email to"+recver+"\nSubject: "+subject+"\nContent: "+content)
		smtp = smtplib.SMTP_SSL("smtp.163.com",994) #实例化smtp服务器
		smtp.login(sender,password)#发件人登录
		smtp.sendmail(sender,[recver,sender],message.as_string()) #as_string 对 message 的消息进行了封装
		smtp.close()

def random_interval():
	return random.random()*10+5

if __name__ == "__main__":
	intervel = random_interval()
	visa = Visa()
	visa.append_log("Next refresh will start after "+str(int(intervel))+" minutes")
	cnt = 0
	try:
		while(True):
			cnt += 1
			if(cnt % 10 == 0):
				visa.send_email(content = "The program is still listening...",subject = "[Visa] Ping Program success")
			time.sleep(intervel*60)
			visa.refresh()
			intervel = random_interval()
			visa.append_log("Next refresh will start after "+str(int(intervel))+" minutes")
	except:
		visa.send_email(content="The program quit unexpectedly",subject="[Visa] System error, program quit")
		print("program quit")



