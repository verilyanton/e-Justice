# -*- coding: utf-8 -*-
import sys, re, requests, nltk, p# print
from __future__ import division
from bs4 import BeautifulSoup as bs
from HTMLParser import HTMLParser # Python 2.7
#from html.parser import HTMLParser # Python 3
from include.sqlite import *
from include.babelnet import *
from include.misc import *

def hl_text(soup, text):
	""" highlight a piece of text """
	text 	= text.decode("utf-8")
	tag 	= soup.find(string=re.compile(text))
	new_tag = tag.replace(text, '<span style="background-color: yellow">' + text + '</span>', 1)
	tag.replace_with(new_tag)
	return soup

def hl_tag(tag):
	tag["style"] = "background-color: yellow"
	return tag

"""
extracts
id 			according to lex.md db
no 			number
type		document type (constitutie, lege, )
agent		adopting institution
date		date adopted
jursd		jurisdiction (country or region)
codename	CRM/1994 is formed from adopting agent, no and year
name 		constitutia
status 		1 - in vigoare, 2 - abrogat
pubs 		josn published including republications [('date', 'article_no')]
modifs		list of modifications
notes		notes
Abrogat prin HG1030/03.10.05, MO132-134/07.10.05 art.1099
Abrogată prin HANRE118 din 19.02.04, MO35-38/27.02.04 art.82
ABROGAT PRIN HG993/17.09.2001, MO114/20.09.2001 art. 1041
ABROGAT 21.12.2000
Abrogat la 24.12.1998
"""
def parse(doc_id):
	doc_id_re	= r"[0-9]{6}"
	text_re 	= r"([a-zA-ZăĂâÂîÎşŞţŢ]+)"
	uc_text_re 	= r"([A-ZĂÂÎŞŢ, ]+)"
	date_re 	= r"([0-9]{2}\.[0-9]{2}\.[0-9]{2,4})"
	codename_re = r"([A-Z]+)([0-9]*)/([0-9]*/)?([0-9]{4})"
	f 			= open("data/lex.justice.md/html/raw/" + doc_id + ".html", "r")
	soup_hl 	= bs(f.read(), "html.parser")
	f.close()
	f 			= open("data/lex.justice.md/html/parse-ready/" + doc_id + ".html", "r")
	soup 		= bs(f.read(), "html.parser")
	f.close()
	jursd 		= "md"
	# print "jurisdiction assumed to be: " + jursd
	for i, tag in enumerate(soup.find_all("td")):
		t = tag.get_text().strip().encode("utf-8")
		if i == 0:
			# print "---"
			# print t
			# print "---"
			codename_re_m = re.search(codename_re, t)
			if codename_re_m is not None:
				codename 	= codename_re_m.group(0)
				law_code 	= codename_re_m.group(1)
				no 			= codename_re_m.group(2)
				prob_year 	= codename_re_m.group(4)
				hl_text(soup_hl, codename)
				#sys.exit()
				# print "codename is: " + codename
				prob_dtype 	= ""
				if law_code[0] == "L":
					prob_dtype 	= "lege"
				elif law_code[0] == "H":
					prob_dtype 	= "hotarîre"
				elif law_code[0] == "C":
					prob_dtype 	= "cod"
				prob_agent 	= ""
				if law_code[1] == "P":
					prob_agent 	= "Parliament"
				elif law_code[1] == "G":
					prob_agent 	= "Government"
				if no == "":
					# print "document number was not found"
				else:
					# print "document number is: " + no
				if prob_year == "":
					# print "year of issue was not found"
				elif 1994 > int(prob_year) or int(prob_year) > 2020:
					# print "year of issue is wrong: " + prob_year
				else:
					# print "year of issue assumed to be: " + prob_year
		elif i == 2:
			# print "---"
			# print t
			# print "---"
			# print "assumed agent is: " + prob_agent
			agent_re_m 		= re.search(uc_text_re, t)
			if agent_re_m:
				hl_text(soup_hl, agent_re_m.group(0))
				agent 			= get_senses(agent_re_m.group(0))
				# print "agent is: " + agent
			else:
				# print "agent could not be found"
		elif i == 3:
			# print "---"
			# print t
			# print "---"
			# print "assumed document type is: " + prob_dtype
			dtype_re_m 		= re.search(uc_text_re, t)
			if dtype_re_m:
				# print dtype_re_m.group(0)
				hl_text(soup_hl, dtype_re_m.group(0))
				dtype 			= get_senses(dtype_re_m.group(0))
				# print "document type is: " + dtype
			else:
				# print "document type could not be found"
			date_re_m 		= re.search(date_re, t)
			if date_re_m:
				date 			= format_date(date_re_m.group(0))
				hl_text(soup_hl, date_re_m.group(0))
				# print "document issue date is: " + date
			else:
				# print "document issue date could not be found"
		elif i == 4:
			# print "---"
			# print t
			# print "---"
			name_re_m 		= re.search(uc_text_re, t)
			if name_re_m:
				name 			= name_re_m.group(0)
				hl_text(soup_hl, name)
				# print "document name is: " + name
			else:
				# print "document name could not be found"
		elif i == 5:
			# print "---"
			# print t
			# print "---"
			pub_date_re 	= "Publicat *: *([0-9]{2}\.[0-9]{2}\.[0-9]{4})"
			frc_date_re 	= "vigoare *: *([0-9]{2}\.[0-9]{2}\.[0-9]{4})"
			issue_no_re 	= "Nr\. *([^ ]+)"
			pub_date_re_m 	= re.search(pub_date_re, t)
			if pub_date_re_m:
				hl_text(soup_hl, pub_date_re_m.group(0))
				pub_date 		= format_date(pub_date_re_m.group(1))
				# print "document publication date is: " + pub_date
			else:
				# print "document publication date could not be found"
			frc_date_re_m 	= re.search(frc_date_re, t)
			if frc_date_re_m:
				hl_text(soup_hl, frc_date_re_m.group(0))
				frc_date 		= format_date(frc_date_re_m.group(1))
				# print "document in force date: " + frc_date
			else:
				# print "document in force date could not be found"
			issue_no_re_m 	= re.search(issue_no_re, t)
			if issue_no_re_m:
				hl_text(soup_hl, issue_no_re_m.group(0))
				issue_no		= issue_no_re_m.group(1)
				# print "Official Journal issue no.: " + issue_no
			else:
				# print "Official Journal issue no. could not be found"
		elif i == 6:
			if re.search("MODIFICAT", t) and 1 == 2:
				mdfs = []
				for ttag in tag.find_all("a"):
					hl_text(soup_hl, ttag.get_text())
					mdf_old_href_re_m = re.search(r"document_rom\.php\?id=[A-Z0-9]{8}:[A-Z0-9]{8}", ttag["href"])
					mdf_id_t 		= requests.get("http://lex.justice.md/" + mdf_old_href_re_m.group(0)).text if mdf_old_href_re_m else ttag["href"]
					mdf_id_re_m 	= re.search(doc_id_re, mdf_id_t)
					if mdf_id_re_m:
						mdfs.append(mdf_id_re_m.group(0))
						# print "modification document id: " + mdf_id_re_m.group(0)
						ttag.decompose()
			#for ttag in tag.find_all(string=re.compile(text))
	return r
	#save_raw_parse_highligted(doc_id, soup_hl)
	#sys.exit()

"""
ids
311496 Constituţia
331491 Regulamentul circulaţiei rutiere
360122 privind achiziţiile publice
331268 codul penal
325085 codul civil
326757 codul muncii
"""
#save_raw_html("331491")
save_parse_ready_html("326757")
#doc_structure = {}
#parse("311496")
