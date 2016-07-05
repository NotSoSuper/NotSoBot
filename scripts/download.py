import urllib.request, urllib.error, urllib.parse

base = 'https://vaporwave.me/archive/Images/Cachemonet%20resources/'
with open('a.html', 'r') as f:
	html = f.read()


downlist = set()
for i in html.split('"'):
	if ('gif' in i or 'jpg' in i or 'png' in i or 'jpeg' in i) and i.replace('.','').isalnum():
		downlist.add(i)
for l in list(downlist):
	url = base + l
	f = urllib.request.urlopen(url)
	data = f.read()
	with open(l, "wb") as pic:
	    pic.write(data)
	print(l)