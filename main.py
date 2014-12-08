import urllib2
import datetime
import re
import zlib

sellers = ["rube_shop190133"]


class Item(object):
	def __init__(self, dates):
		self.dates = dates
		self.duration = (dates[0][0]-dates[len(dates)-1][0]).days
	def getDiff(self):
		dates = self.dates
		base = dates[len(dates)-1][0]
		a = []
		gap = self.duration/15
		total = 0
		for i in range(0, 15):
			limit = base+datetime.timedelta(int(gap*(i+1)))
			a.append([limit, 0])
			while True:
				if len(dates) == 0 or dates[len(dates)-1][0] > limit:
					break
				cnt = dates.pop()[1]
				a[i][1] += cnt
				total += cnt			
		self.diff = (a[14][1]-a[13][1])/total
		return self.diff


def spider(seller):
	url = "http://class.ruten.com.tw/user/index00.php?s="+seller+"&o=9"
	cookieurl = 'http://ts.ruten.com.tw/ts_sender.php'
	req_header = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding':'gzip,deflate,sdch',
			'Accept-Language':'en-US,en;q=0.8',
			'Connection':'keep-alive',
			'Referer':url,
			'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.120 Chrome/37.0.2062.120 Safari/537.36'}
	req_timeout = 10
	req = urllib2.Request(cookieurl, None, req_header)
	resp = urllib2.urlopen(req, None, req_timeout)
	s = resp.read()
	tsid = re.findall(r"'(.*)'\)\);", s)  #get the fuckin cookie!
	tsid = tsid[0]
	req_header['Cookie'] = "_ts_id="+tsid
	
	req = urllib2.Request(url, None, req_header)
	resp = urllib2.urlopen(req, None, req_timeout)
	s = zlib.decompress(resp.read(), 16+zlib.MAX_WBITS)
	g_nos = re.findall(r'<a ruten="\d+" href="http://goods.ruten.com.tw/item/show\?(\d+)"', s)
	if len(g_nos) == 0:
		g_nos = re.findall(r'<a pchome="\d+" href="http://goods.ruten.com.tw/item/show\?(\d+)"', s)
	if len(g_nos) == 0:
		raise NameError("Can't find a seller's item!")
	
	if len(g_nos) > 10:
		g_nos = g_nos[0:9]

	for g_no in [g_nos[0]]:
		url = 'http://goods.ruten.com.tw/item/historymore?'+g_no+'&more'
		dates = []
		ok = True
		limit = datetime.date.today()-datetime.timedelta(15*7) #within 15 weeks
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
		item = Item(dates)
		item.getDiff()

if __name__ == '__main__':
	for seller in sellers:
		spider(seller)
