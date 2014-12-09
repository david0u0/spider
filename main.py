# -*- coding: utf-8 -*-
#############################
sellers = ["rube_shop190133"]
# 在sellers[]中填入欲查詢的賣家
UNIT = 15
MULT = 5
# UNIT為統計時的單位，以日計算
# MULT代表「共需計算多少個單位」
# e.g. 若以「星期」為單位，共計算10個禮拜，則(UNIT, MULT) = (7, 10)
# 索引：within_how_many_days
#
# 目前算法 => partition: 用最近一個UNIT的銷量除以總銷量
#############################
import urllib2
import datetime
import re
import zlib
items = []

class Item(object):
	def __init__(self, dates, g_no):
		self.g_no = g_no
		self.dates = dates
		self.duration = (datetime.date.today()-dates[len(dates)-1][0]).days
		self.setup()
		self.compute_partition()
	def setup(self):
		dates = self.dates
		base = dates[len(dates)-1][0]
		a = []
		gap = 1.0*self.duration/MULT
		total = 0
		for i in range(0, MULT):
			limit = base+datetime.timedelta(int(gap*(i+1)))
			a.append([limit, 0])
			while True:
				if len(dates) == 0 or dates[len(dates)-1][0] > limit:
					break
				cnt = dates.pop()[1]
				a[i][1] += cnt
				total += cnt			
		a.reverse()
		self.a = a
		self.total = total
	def compute_partition(self):
		total = self.total
		self.partition = 1.0*self.a[0][1]/total if total>0 else 0
	def key(self):
		return self.partition

def spider(seller):
	url = "http://class.ruten.com.tw/user/index00.php?s="+seller+"&o=9"
	cookieurl = 'http://ts.ruten.com.tw/ts_sender.php'
	req_header = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding':'gzip,deflate,sdch',
			'Accept-Language':'en-US,en;q=0.8',
			'Connection':'keep-alive',
			'Referer':url,
			'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.120 Chrome/37.0.2062.120 Safari/537.36'}
	req_timeout = 100
	req = urllib2.Request(cookieurl, None, req_header)
	resp = urllib2.urlopen(req, None, req_timeout)
	s = resp.read()
	tsid = re.findall(r"'(.*)'\)\);", s)  #get the fuckin cookie!
	tsid = tsid[0]
	req_header['Cookie'] = "_ts_id="+tsid

	req = urllib2.Request(url, None, req_header)
	resp = urllib2.urlopen(req, None, req_timeout)
	s = zlib.decompress(resp.read(), 16+zlib.MAX_WBITS)
	g_nos = re.findall(r'valign="middle">\n<a ruten="\d+" href="http://goods.ruten.com.tw/item/show\?(\d+)"', s)
	if len(g_nos) == 0:
		g_nos = re.findall(r'valign="middle">\n<a pchome="\d+" href="http://goods.ruten.com.tw/item/show\?(\d+)"', s)
	if len(g_nos) == 0:
		raise NameError("Can't find a seller's item!")

	for g_no in g_nos:
		url = 'http://goods.ruten.com.tw/item/historymore?'+g_no+'&more'
		dates = []
		ok = True
		limit = datetime.date.today()-datetime.timedelta(UNIT*MULT) #within_how_many_days
		req = urllib2.Request(url, None, req_header)
		resp = urllib2.urlopen(req, None, req_timeout)
		s = zlib.decompress(resp.read(), 16+zlib.MAX_WBITS)
		a = re.findall(r'(\d+-\d+-\d+).*\n.*\n.*sans-serif">(\d+)', s) 
		for elt in a:
			d = datetime.date(*[int(i) for i in elt[0].split('-')])
			cnt = int(elt[1])
			if d < limit or len(dates) > 500:
				break
			dates.append((d, cnt))
		item = Item(dates, g_no)
		items.append(item)

if __name__ == '__main__':
	for seller in sellers:
		spider(seller)
	items = sorted(items, key=lambda item : -item.key())
	for item in items:
		print "http://goods.ruten.com.tw/item/show?"+str(item.g_no)+" partition="+str(item.partition)
		for i in item.a:
			print str(i[0])+" => "+str(i[1])
