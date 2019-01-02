# -*- coding: utf-8 -*-
import sys, requests, io, re, json # urllib2
from os import walk
from bs4 import BeautifulSoup as bs
from HTMLParser import HTMLParser # Python 2.7
#from html.parser import HTMLParser # Python 3
#from include.misc import *
reload(sys)
sys.setdefaultencoding("utf-8")


def format_date(d):
	""" turns 12.08.1994 and 12.08.94 to 1994-08-12 """
	date = d.strip()
	if len(date) == 10 or len(date) == 8:
		parts = date.split(".")
		if len(date) == 8:
			if int(parts[2]) > 80:
				parts[2] = "19" + parts[2]
			else:
				parts[2] = "20" + parts[2]
		return "-".join(parts[::-1])


def common_replace(text):
	for f, r in [["G U V E R N U L", "GUVERNUL"],["T i t l u l", "Titlul"],
["CAPITOLUL", "Capitolul"],["d e c r e t e a z ă", "decretează"],
["h o t ă r ă ş t e", "hotărăşte"],["&ˆn", "în"],["&Ibr /circ;", "Î"],
["d e c i d e", "decide"],["D I S P O Z I Ţ I E", "DISPOZIŢIE"],
["D E C L A R A Ţ I A", "DECLARAŢIA"],["&#354", "Ţ"],["E R A T Ă","ERATĂ"],
["superior beneficiază de drbr /ˆnbsp; (1) Dreptul la  eptul  la autonomie.",
"superior beneficiază de dreptul la autonomie."]]:
		text = text.replace(f, r) # f.decode("utf-8"), r.decode("utf-8")
	return text

def get_html(url):
	html 	= requests.get(url).text
	if html != "":
		h 		= HTMLParser()
		return h.unescape(html)

def write_html(doc_id, adr, html):
	with io.open(adr + str(doc_id) + ".html", "w", encoding="utf8") as f:
		f.write(unicode(html))
		f.close()

def save_raw_html(doc_id):
	html 	= get_html("http://lex.justice.md/md/" + str(doc_id))
	if html is not None:
		write_html(doc_id, "data/lex.justice.md/html/raw/", html)
	return html

def save_meta_raw_html(doc_id):
	html 	= get_html("http://lex.justice.md/index.php?action=view&view=additional&id=" + str(doc_id) + "&lang=1")
	if html is not None:
		write_html(doc_id, "data/lex.justice.md/html/meta-raw/", html) # "/home/am/backups/lex.justice.md/html/meta-raw/"
	return html

def save_mo_raw_html(doc_id):
	html 	= get_html("https://www.monitorul.md/monitor/v-%s-v/" % str(doc_id))
	if html is not None:
		write_html(doc_id, "data/lex.justice.md/mo-html/raw/", html)
	return html

'''
def save_raw_parse_highligted(doc_id, soup):
	h 		= HTMLParser()
	write_html(doc_id, "data/lex.justice.md/html/raw-parse-highligted/", h.unescape(unicode(soup)))
'''

def save_parse_ready_html(doc_id, html = None):
	# if html is None:
	# 	html 	= get_html(doc_id)
	# assert(isinstance(html, str) or isinstance(html, unicode))
	if html is not None:
		html	= common_replace(html)
		html 	= " ".join(html.split())
		soup 	= bs(html, "html.parser")
		for t in soup.find_all("br"):
			t.replace_with(" ")
		for tn in ["style", "script", "img", "head", "link"]:
			for t in soup.find_all(tn):
				t.decompose()
		for tn in ["div", "span", "font", "tr", "td"]:
			for t in soup.find_all(tn):
				if t.get_text().strip() == "":
					t.decompose()
		head_tag = soup.new_tag("head")
		jquery_tag = soup.new_tag("script", src="https://code.jquery.com/jquery-3.2.1.min.js")
		script_tag = soup.new_tag("script", src="../js/parse.js")
		link_tag = soup.new_tag("link", rel="stylesheet", href="../css/master.css")
		meta_tag = soup.new_tag("meta", content="text/html;charset=utf-8")
		meta_tag["http-equiv"] = "Content-Type"
		tag = soup.html
		tag.insert(0, head_tag)
		tag = soup.head
		tag.insert(0, meta_tag)
		tag.insert(1, jquery_tag)
		tag.insert(2, link_tag)
		tag = soup.body
		tag.insert(0, script_tag)
		write_html(doc_id, "data/lex.justice.md/html/parse-ready/", soup)
		return soup

def save_text(doc_id, soup = None):
	if soup is not None:
		f = open("data/lex.justice.md/html/text/" + str(doc_id) + ".txt", "a+")
		text = soup.get_text().encode("utf8", "replace")
		# text = " ".join(text.split())
		f.write(text)
		f.close()
		return text

def save_meta_text(doc_id, html = None):
	if html is not None:
		f = open("data/lex.justice.md/html/meta-text/" + str(doc_id) + ".txt", "a+")
		soup 	= bs(html, "html.parser")
		text 	= soup.get_text().encode("utf8", "replace")
		for s in ["Версия на русском", "Fişa actului juridic", "table#master{border:0px;}", "td.noborder{border:0px;}"]:
			text = text.replace(s, "")
		text	= common_replace(text.strip())
		f.write(text)
		f.close()
		return text

"""
group(1)	'HPO'
group(2)	'476'
group(3)	'PARLAMENTUL  HOTĂRÎRE'
group(4)	'476'
group(5)	'04.12.2003'
group(6)	'cu privire la numirea unui membru al Curţii de Conturi'
"""
def save_feats(texts):
	if texts is not None:
		with open("data/lex.justice.md/log/doc-feat.json", "r+") as fj:
			try:
				dfs = json.loads(fj.read())
			except ValueError, e:
				dfs = {}
			r = r"([A-ZĂÂÎŞŢ]+)(.*)\/[0-9]{4} {2,}ID intern unic: [0-9]{6} {2,}"\
				"Версия на русском {2,}Fişa actului juridic {2,}"\
				"([A-ZĂÂÎŞŢ ]+) Nr\. (.*) {2,}din ([0-9]{2}\.[0-9]{2}\.[0-9]{2,4}) {2,}"\
				"([0-9a-zA-ZăĂâÂîÎşŞţŢ&%!@:;,\.\-\(\)„”“_ ]+) {2,}Publicat"
			for doc_id, t in texts.iteritems():
				m = re.search(r, t)
				df = {}
				if m is not None:
					df["acode"] = m.group(1) # alpha code
					df["agent_type"] = m.group(3).strip()
					df["date"] = m.group(5)
					df["name"] = m.group(6).strip()
		 		# analyze doc structure
				crt_m = re.findall(r"(Cartea) *([a-zăâîşţ]+)", t) # Cartea întîi
				ttl_m = re.findall(r"(Titlul) *([IVX]+)", t) # Titlul I
				cap_m = re.findall(r"(Capitolul) *([IVX]+)", t) # Capitolul VI
				sec_m = re.findall(r"(Secţiunea) *a? ([0-9]+)-?a?", t) # Secţiunea a 2
				art_m = re.findall(r"(Articolul) *([IVX]{1,4}|[0-9]{1,4}[-0-9]*)?", t) # Articolul III Articolul 3
				al_m = re.findall(r"\(([0-9]+)\) [A-ZĂÂÎŞŢ]", t)
				df["crt"] = len(crt_m)
				df["ttl"] = len(ttl_m)
				df["cap"] = len(cap_m)
				df["sec"] = len(sec_m)
				df["art"] = len(art_m)
				df["al"] = len(al_m)
				dfs[str(doc_id)] = df
			fj.seek(0)
			fj.write(json.dumps(dfs, ensure_ascii=False).encode("utf8"))
			fj.truncate()


def convert_raw_to_parse_ready():
	for (dirpath, dirnames, filenames) in walk("data/lex.justice.md/html/raw"):
	    for fn in filenames:
			f = open("data/lex.justice.md/html/raw/" + fn)
			save_parse_ready_html(fn[:-5], f.read())
			f.close()
	    break


def convert_parse_ready_to_text():
	for (dirpath, dirnames, filenames) in walk("data/lex.justice.md/html/parse-ready"):
	    for fn in filenames:
			f 		= open("data/lex.justice.md/html/parse-ready/" + fn)
			soup 	= bs(f.read(), "html.parser")
			save_text(fn[:-5], soup)
			f.close()
	    break

def convert_text_to_feats():
	for (dirpath, dirnames, filenames) in walk("data/lex.justice.md/html/text"):
		texts = {}
		for fn in filenames:
			f = open("data/lex.justice.md/html/text/" + fn)
			texts[fn[:-4]] = f.read()
			f.close()
		save_feats(texts)
		break
