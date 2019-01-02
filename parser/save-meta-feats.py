# -*- coding: utf-8 -*-
import sys, MySQLdb, re, json
from os import walk
from bs4 import BeautifulSoup as bs
from time import time
from inspect import currentframe, getframeinfo
from misc import format_date, common_replace
reload(sys)
sys.setdefaultencoding("utf-8")

cf = currentframe()
t0 = time()
# filename = getframeinfo(cf).filename
def pub_no_range(pub_no):
    try:
        pub_no_s = pub_no.split("-")
        return [int(pub_no_s[0])] if len(pub_no_s) == 1 else range(int(pub_no_s[0]), int(pub_no_s[1]) + 1)
    except ValueError, e:
        return []

db = MySQLdb.connect(host="localhost", port=3306, user="root", passwd="", db="lex", charset="utf8")
# local
# remote
dmr = "data/lex.justice.md/html/meta-raw/"
#date_re 	= r"([0-9]{2}\.[0-9]{2}\.[0-9]{2,4})"
code_full_re = r"([A-ZĂÂÎŞŢ]+)(.*)\/[0-9]{4}"
pub_date_re 	= r"[0-9]{2}\.[0-9]{2}\.[0-9]{4}|[0-9]{2}\.[0-9]{2}\.[0-9]{2}"
pub_cat_re 		= r"n (.*)"
pub_no_re 		= r"Nr\. *([^ ]+)"
pub_no_ref_re   = r"art Nr *:(.*)"
doc_id_skip = ["367898", # duplicates
    "325971", "325028", "350116"] # incomplete data
code_full_errors = {"329504":"DPO1910/2008", "372427":"HGO914/2017",
    "333869":"OCNVM67/2/2006", "303202":"HGO584/2000", "370129":"HGO1286/2016",
    "372196":"LPO207/2017", "372796":"DCCA15/95/2017", "371607":"OBN23-01009/3/2017",
    "325453":"HGA1085/207/2007", "303027":"HGO561/2004", "334297":"OSVC128/2230",
    "313476":"MJ2105/1999", "366384":"HGO997/2016", "313340":"MAIAO213/2005",
    "330721":"DGO15/2009", "349865":"HCNPFC11/10/2010", "303546":"HGO631/2000",
    "372472":"HGO956/2017", "360248":"MMAE/2002", "371947":"DCNH517/2016", "332267":"HGO563/2009",
    "350681":"OSVC569/2013", "342258":"HPO1043/2002", "305118":"HGO850/2003",
    "332132":"HGO526/2009", "347481":"LPO40/2013","345408":"OMAEIEC1127-b-174/2012",
    "314624":"VMO37/3/2005", "320624":" DGO207/1996", "367899":"OMS917/2016",
    "320625":"DGO208/1996", "372685":"DPO449/2017", "371276":" HGC655/2017",
    "309277":"HPO561/2001", "341528":"HCEC1021/2011", "345003":" HCNPFC34/8/2012",
    "371596":"HCSM396/18/2017", "367801":"HGM1286/2016", "302412":"HGO485/2005",
    "347618":"HCNPF18/16/2013", "368849":"DCIMCCM26-11/2-22/01/2017", "371337":"DCIMCCC26-11/2-22/01/2017",
    "349488":"HCNPF41/13/2013", "324525":"DPO1212/2007", "325238":"HCNPF45/3/2007",
    "329507":"DPO1913/2008", "346400":"DCIMCCC26-11/2-22/02/2012", "331606":"HGO361/2009",
    "301176":"HGO337/2004", "336559":"HCNAA05/1-1/2010", "348559":"*HCEC1897/2013",
    "309103":"HPO47/2003", "343230":"HCNPF20/14/2012", "352811":"DPO1138/2014",
    "324072":"HGO669/2007", "302905":"HGO545/2004", "350205":"HGO866/2013",
    "285675":"RBNM43/1996", "323289":"DGO47/2007", "353747":"HGO524/2014",
    "308742":"HPO300/2003", "324921":"HKK37/2007", "366486":"HCEC28/2016",
    "325087":"LPM156/2007", "346491":"OMDRC138/2012", "373041":"*LPC156/2007",
    "326317":"HCNPF60/7/2007", "325247":"EMO146/2007", "365465":"DPO2126/2016",
    "308757":"HPO306/2003", "371637":"HGO743/2017", "312941":"LPO1273/2000",
    "357904":"HCEC3223/2015", "333137":"HFGDSB101/1/2009", "318549":"DPO552/1998",
    "336561":"HCNAA05/1-3/2010", "325652":"HCNPFC53/3/2007", "366777":"HGC1057/2016",
    "302655":"HGO51/2003", "336560":"HCNAA05/1-2/2010", "349125":"HCNPFC26/10/2013",
    "347452":"HGO266/2013", "310725":"IMF455/2000", "357823":"OIFPS230/2015",
}
agent_id_errors = {"357631":23, "351927":17, "315447":7, "286112":19, "314238":51,
    "357522":23,
}
no_misses = ["311496", "363979", "367775", "347245", # CONSTITUŢIA
    "306317"]
no_errors = {"332267":"563", "347481":"40", "367899":"917", "372685":"449", "324525":"1212",
    "347452":"266"
}
date_errors = {"349518":"12.08.1987", "325729":"24.05.2007", "349125":"13.06.2013"}
name_misses = ["324622", "286956", "353421", "358105", "367971", "313709", "314264"]
name_errors = {"347481":"pentru completarea Codului penal al Republicii Moldova nr. 985-XV din 18 aprilie 2002",
    "347452":"Hotărîre cu privire la modificarea destinației unui teren",
}
pub_date_errors = {"326531":"0", "370646":"23.06.2017", "336688":"25.11.1999",
    "358105":"17.04.2015", "325729":"01.06.2007"}
pub_no_errors = {"326531":"0", "357706":"0", "311903":"000", "286112":"000"}
pub_cat_errors_doc_id = {"290571":"ve","286994":"ve", "311903":"bo", "373448":"mo",
    "313486":"mo", "359851":"mo", "359233":"ti", "357522":"ti", "363725":"ti",
}
pub_cat_errors_str_ti = ["36 2004-10-26 mo", "36 2004-03-29 mo", "36 2004-09-30 mo",
    "36 2005-10-05 mo", "36 2005-11-17 mo", "36 2002-10-06 mo", "36 2004-05-26 mo",
    "36 2005-06-20 mo", "36 2003-07-08 mo", "36 2003-11-13 mo", "36 2004-04-06 mo",
    "36 2002-06-24 mo", "36 2006-02-16 mo", "36 2005-08-17 mo", "36 2005-04-21 mo", "36 2004-11-01 mo",
    "41 2009-01-01 mo", "30 2005-12-30 mo", "18 1999-01-01 mo", "16 1999-12-31 undefined",
]
pub_id_errors_data_str = {"240 2015-08-26 mo":107, "1-4 2005-01-01 mo":1015,
    "103 2009-06-16 mo":1526, "181 2004-10-01 mo":1108, "84-86 2003-04-16 mo":1202,
    "84 2003-04-16 mo":1202, "234 2003-11-24 mo":1171, "201-2013 2017-06-23 mo":1976,
    "224-233 2010-08-21 mo":105, "124-130 2014-05-22 mo":89, "000 2006-03-22 mo":6489,
    "36-40 2013-04-22 mo":1838, "000 2005-03-25 mo":6456, "205-207 2012-09-29 mo":1808,
    "248-251 2012-11-07 mo":1821, "134-137 2006-09-25 mo":1225, "163-169 2003-08-01 mo":1149,

}
pub_id_errors_doc_id = {"326531":None, "325133":None, "337928":None,
    "332246":1543, "361573":118, "313337":1149, "332267":1543, "344556":1800, "359824":98, "361989":127, "367464":197, "314779":1039, "334241":1601,
    "326210":5846, "342001":1754, "361972":70, "318107":1312, "355567":55, "297241":1237, "342106":5642, "340841":1737, "359924":5586, "299656":1262,
    "344592":1801, "319745":5416, "310402":1174, "311219":1132, "325288":1113, "288199":1137, "348673":1869, "328715":1072, "302694":1288, "331791":1531,
    "325120":1348, "327809":1411, "315771":1208, "313284":1256, "328392":1430, "340099":1728, "319845":6276, "285293":1146, "370341":1972, "325672":1370,
    "288255":1148, "317119":1226, "363140":142, "295797":1169, "332641":1559, "363309":87, "295560":1009, "321885":1335, "372685":2006, "365338":156,
    "363191":142, "356222":64, "323713":1344, "286120":1090, "357885":78, "291171":1251, "285744":5357, "354654":39, "358776":90, "301310":1090,
    "344624":1802, "325971":1372, "361511":118, "329768":1472, "332915":1219, "324525":1354, "347957":1858, "319400":1325, "370392":1972, "314128":1131,
    "297594":1240, "339657":1720, "340283":1729, "316085":1211, "366376":179, "342484":1763, "346376":1831, "286113":6859, "338676":1706, "372437":2002,
    "368588":216, "360206":101, "352866":1950, "350101":1892, "291414":1159, "290066":1003, "364928":159, "368457":214, "319578":1325, "351577":1933,
    "324599":1349, "347274":1847, "311966":1252, "320843":1331, "330349":1321, "314127":1205, "316000":1209, "325067":1361, "311993":1231, "362544":131,
    "314024":1233, "334031":1056, "371382":1982, "315469":1123, "364514":156, "342196":1758, "340839":1737, "328617":1034, "297528":1240, "369693":1961,
    "354919":45, "354896":45, "356905":70, "346059":1825, "363313":143, "296102":1067, "368701":217, "299632":1262, "366632":182, "324595":1353, "300844":1186,
    "370863":1979, "358289":87, "360539":105, "307713":1236, "345558":1819, "354453":35, "356906":70, "367072":192, "320826":1331, "327521":1039, "366941":189,
}
#for (dirpath, dirnames, filenames) in walk(dmr):
with open("logs/html-meta-raw-filenames.json", "r+") as fj:
    for fn in ["373251.html"]: # json.loads(fj.read()):
        doc_id 	= fn[:-5]
        count_doc_id_qs = "SELECT count(id) FROM doc WHERE id = '{0}'"
        c = db.cursor()
        c.execute(count_doc_id_qs.format(doc_id))
        r = c.fetchone()
        if r and doc_id not in doc_id_skip and r[0] == 0:
            print "---", doc_id
            code_full = code_a = no_try = no = agent_name = agent_id = cat_id = name = date = None
            pub_date = pub_cat = pub_no = pub_id = clsf_id = None
            f 		= open(dmr + fn, "r")
            #print f.read()
            #sys.exit()
            soup 	= bs(common_replace(f.read()), "html.parser")
            f.close()
            for i, td in enumerate(soup.find_all("td")):
                if i == 2:
                    # DOCUMENT CODENAME
                    try:
                        if doc_id in code_full_errors:
                            code_full = code_full_errors[doc_id]
                        else:
                            code_full = td.contents[0].strip()
                        code_full_re_m = re.search(code_full_re, code_full)
                        if code_full_re_m:
                            code_a = code_full_re_m.group(1).strip() #alpha code
                            no_try = code_full_re_m.group(2).strip()
                    except IndexError, e:
                        print doc_id, "code_full", "code_a", "no_try"
                    if not code_full or not code_a:
                        print doc_id, "code_full", "code_a", code_full
                        sys.exit()

                elif i == 3:
                    # ISSUING AUTHORITY
                    if doc_id in agent_id_errors:
                        agent_id = agent_id_errors[doc_id]
                    else:
                        try:
                            agent_name = td.contents[1].contents[0]
                            agent_name = " ".join(agent_name.lower().split()).strip()
                        except IndexError, e:
                            print doc_id, "agent_name"
                            #sys.exit()
                        if not agent_name and code_a in ["OMDRCC", "OMDRC", "OMDRCA", "OMDRCM"]:
                            agent_id = 31
                        elif agent_name:
                            get_agent_id_qs = "SELECT id FROM agent WHERE name = '{0}'"
                            add_agent_name_qs = "INSERT INTO agent (name) VALUES ('{0}')"
                            try:
                                c = db.cursor()
                                c.execute(get_agent_id_qs.format(agent_name))
                                r = c.fetchone()
                                if r:
                                    agent_id = r[0]
                                else:
                                    try:
                                        ca = db.cursor()
                                        ca.execute(add_agent_name_qs.format(agent_name))
                                        db.commit()
                                        agent_id = ca.lastrowid
                                    except Exception as e:
                                        print cf.f_lineno, e
                                        db.rollback()
                            except Exception as e:
                                print cf.f_lineno, e
                                db.rollback()
                    if not agent_id:
                        print doc_id, "agent_id"
                        sys.exit()

                elif i == 4:
                    # DOC CATEGORY (TYPE)
                    try:
                        cat = td.contents[0].contents[0]
                        cat = " ".join(cat.split()).lower().strip()
                        #type_babel 			= get_senses(typefull)
                    except IndexError, e:
                        print doc_id, "doc_cat"
                        sys.exit()
                    if cat:
                        get_cat_id_qs = "SELECT id FROM cat WHERE name = '{0}'"
                        add_cat_name_qs = "INSERT INTO cat (name) VALUES ('{0}')"
                        c = db.cursor()
                        c.execute(get_cat_id_qs.format(cat))
                        r = c.fetchone()
                        if r:
                            cat_id = r[0]
                        else:
                            try:
                                c = db.cursor()
                                c.execute(add_cat_name_qs.format(cat))
                                db.commit()
                                cat_id = c.lastrowid
                            except Exception as e:
                                print cf.f_lineno, e
                                db.rollback()
                                #continue #sys.exit()
                    if not cat_id:
                        print doc_id, "cat_id"
                        sys.exit()

                    # DOC NUMBER
                    if doc_id in no_misses:
                        no = "0"
                    elif doc_id in no_errors:
                        no = no_errors[doc_id]
                    else:
                        try:
                            no = td.contents[1].strip()[3:].strip()
                            no = no.replace("--", "-").replace(" ", "")
                        except IndexError, e:
        					print doc_id, "no"
                        #if no_try != no:
                            #print doc_id, "no != no_try"
                    if not no:
                        print doc_id, "no"
                        if no_try:
                            no = no_try
                        else:
                            sys.exit()

                    # DOC DATE
                    if doc_id in date_errors:
                        date = format_date(date_errors[doc_id])
                    else:
                        try:
        					date_raw 	= td.contents[3]
        					date		= format_date(date_raw.strip()[3:])
                        except IndexError, e:
                            print doc_id, "date"
                    if not date:
                        print doc_id, "date"
                        sys.exit()

                elif i == 5:
                    # DOC NAME
                    if doc_id in name_misses:
                        name = cat
                    elif doc_id in name_errors:
                        name = name_errors[doc_id]
                    else:
                        name = " ".join(" ".join(s.split()) for s in td.stripped_strings)
                    if not name:
                        print doc_id, "name"
                        sys.exit()
                    #print "document name is:", name

                elif i == 6:
                    if doc_id in pub_id_errors_doc_id:
                        pub_id = pub_id_errors_doc_id[doc_id]
                    else:
                        pub_date_re_m 	= re.search(pub_date_re, td.text)
                        pub_cat_re_m 	= re.search(pub_cat_re, td.text)
                        pub_no_re_m 	= re.search(pub_no_re, td.text)
                        pub_no_ref_re_m = re.search(pub_no_ref_re, td.text)
                        # PUBLICATION DATE
                        if doc_id in pub_date_errors:
                            pub_date = pub_date_errors[doc_id]
                            if pub_date != "0":
                                pub_date = format_date(pub_date)
                        elif pub_date_re_m:
                            pub_date = format_date(pub_date_re_m.group(0))
                        if not pub_date:
                            print doc_id, "pub_date"
                            sys.exit()
                            #print "document publication date is: " + pub_date
                            #print "document publication date could not be found"

                        # PUBLICATION NO.
                        if doc_id in pub_no_errors:
                            pub_no = pub_no_errors[doc_id]
                        elif pub_no_re_m:
                            pub_no		= pub_no_re_m.group(1).strip()
                            if pub_no and len(pub_no) > 1 and pub_no[:2].lower() == "ed":
                                pub_no = "ed.speciala"
                            elif pub_no and pub_no not in ["000", "00", "0"]:
                                pub_no = "-".join([s.lstrip("0") for s in pub_no.split("-")])
                        if not pub_no:
                            print doc_id, "pub_no"
                            sys.exit()

                        # PUBLICATION INSIDE REFERENCE ID
                        if pub_no_ref_re_m:
                            pub_id_ref		= pub_no_ref_re_m.group(1).strip()
                            if pub_id_ref and pub_id_ref not in ["000", "00", "0"]:
                                pub_id_ref = "-".join([s.lstrip("0") for s in pub_id_ref.split("-")])
                        if not pub_id_ref:
                            print doc_id, "pub_no_ref_re_m"
                            sys.exit()

                        #print "document publication no.:", pub_no
                        #print "document publication no. could not be found"

                        # PUBLICATION CATEGORY
                        if doc_id in pub_cat_errors_doc_id:
                            pub_cat = pub_cat_errors_doc_id[doc_id]
                        elif pub_cat_re_m:
                            pub_cat_name = pub_cat_re_m.group(1).strip().encode("utf8")
                            pub_cat_dict = {
                                "Monitorul Oficial": "mo",
                                "Tratate Internationale": "ti",
                                "Monitorul Parlamentului": "mp",
                                "Veştile": "ve",
                                "B.Of.": "bo",
                                "Nepublicat": "np",
                                "undefined": "undefined",
                                #"Orice": None
                            }
                            if pub_cat_name in ["Orice", "1"] and int(pub_date[:4]) < 1991:
                                pub_cat = "ve"
                            elif pub_cat_name in pub_cat_dict:
                                pub_cat = pub_cat_dict[pub_cat_name]
                                pub_id_data_str = " ".join([pub_no, pub_date, pub_cat])
                                if pub_id_data_str in pub_cat_errors_str_ti:
                                    pub_cat = "ti"
                            else:
                                print doc_id, "pub_cat_name", pub_cat_name
                                sys.exit()
                            if not pub_cat or pub_cat == "undefined":
                                print doc_id, "pub_cat"
                                sys.exit()
                            #print "document publication category:", pub_cat
                            #print "document publication category could not be found"

                        # PUBLICATION ID
                        pub_id_data_str = " ".join([pub_no, pub_date, pub_cat])
                        if pub_id_data_str in pub_id_errors_data_str:
                            pub_id = pub_id_errors_data_str[pub_id_data_str]
                        else:
                            get_pub_id_qs = "SELECT id FROM pub WHERE no = '{0}' AND date = '{1}' AND cat = '{2}'"
                            add_pub_id_qs = "INSERT INTO pub (no, date, cat) VALUES ('{0}', '{1}', '{2}')"
                            get_pub_date_qs = "SELECT id, no FROM pub WHERE date = '{0}'"
                            c = db.cursor()
                            c.execute(get_pub_id_qs.format(pub_no, pub_date, pub_cat))
                            r = c.fetchone()
                            if r:
                                pub_id = r[0]
                            elif pub_cat != "mo" or int(pub_date[:4]) < 2002:
                                try:
                                    c = db.cursor()
                                    c.execute(add_pub_id_qs.format(pub_no, pub_date, pub_cat))
                                    db.commit()
                                    pub_id = c.lastrowid
                                except Exception as e:
                                    print cf.f_lineno, e
                                    db.rollback()
                            else:
                                c = db.cursor()
                                c.execute(get_pub_date_qs.format(pub_date))
                                for r in c.fetchall():
                                    min_pub_no, max_pub_no = set(pub_no_range(pub_no)), set(pub_no_range(r[1]))
                                    #print min_pub_no, max_pub_no
                                    #sys.exit()
                                    if min_pub_no and max_pub_no and min_pub_no < max_pub_no:
                                        pub_id = r[0]
                                        break
                        if not pub_id:
                            print doc_id, "pub_id", pub_no, pub_date, pub_cat
                            sys.exit()

                elif i == 7:
                    #html = " ".join([" ".join(s.split()) for s in td.stripped_strings])
    				#print "document classification:", clsf
                    if td.text.strip():
                        clsf_id = 1
                    #get_clsf_id_qs = "SELECT id FROM clsf WHERE name = '{0}'"
                    #add_clsf_name_qs = "INSERT INTO clsf (name) VALUES ('{0}')"
                    #clsf_name = " ".join(td.text.split()).strip()
                    #if clsf_name:
                    #    c = db.cursor()
                    #    c.execute(get_clsf_id_qs.format(clsf_name))
                    #    r = c.fetchone()
                    #    if r:
                    #        clsf_id = r[0]
                    #    else:
                    #        try:
                    #            c = db.cursor()
                    #            c.execute(add_clsf_name_qs.format(clsf_name))
                    #            db.commit()
                    #            clsf_id = c.lastrowid
                    #        except Exception as e:
                    #            print cf.f_lineno, e
                    #            db.rollback()
                    #if not clsf_id:
                    #    print doc_id, "clsf_id"
            add_doc_qs = ("INSERT INTO doc "
                "(id, name, agent_id, date, code_full, code_a, no, cat_id, pub_id, pub_id_ref, clsf_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            try:
                c = db.cursor()
                c.execute(add_doc_qs, (int(doc_id), name, agent_id, date, code_full,
                    code_a, no, cat_id, pub_id, pub_id_ref, clsf_id))
                db.commit()
            except Exception as e:
                print cf.f_lineno, e
                print name, agent_id, date, code_full, code_a, no, cat, cat_id, pub_id, pub_id_ref, clsf_id
                db.rollback()
                sys.exit()
            #print "time:", round(time() - t0, 3), "s"
            #sys.exit()
	#break
db.close()

# 'no': '44', 'agent': 'preşedintele republicii moldova', 'pub_date': '30.06.1991', 'pub_no': '006',
# 'cname': 'DPO44/1991', 'date': '10.06.1991', 'acode': 'DPO', 'type': 'decret', 'clasf': ''}

#if d["agent"] == "any":
    #print k.encode('UTF8'), d.encode('UTF8')
