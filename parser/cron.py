# -*- coding: utf-8 -*-
import sys, hashlib, csv, time, json
from os import walk
from random import randint
from misc import *
# reload(sys)
# sys.setdefaultencoding("utf-8")

'''
for (dirpath, dirnames, filenames) in walk("data/lex.justice.md/html/meta-raw"):
    saved = set([fn[:-5] for fn in filenames])
    print len(saved)
    with open("logs/parsed-docs.csv", "rb") as f:
        log = list(csv.reader(f))
        print len(log)
        parsed = set([a[1] for a in log[1:] if int(a[2]) > 0])
        print len(parsed)
        unparsed = parsed - saved
        print len(unparsed)
        print len(parsed) - len(unparsed)
    break

for doc_id in list(unparsed):
    sleep_sec = randint(0, 3)
    time.sleep(sleep_sec)
    meta_html = save_meta_raw_html(doc_id)
    meta_text = save_meta_text(doc_id, meta_html)
    print doc_id, len(meta_text)
'''


with open("logs/parsed-docs.csv", 'rb') as fca:
    rd = [l[1] for l in list(csv.reader(fca))]
    for doc_id in range(127824, 500000):
        if str(doc_id) not in rd:
        # if r[3] == "" or r[3] == "1197f290bae092c70a6cf07a223ed8bc": # int(r[2]) < 2000:
            # doc_id = r[1]
            sleep_sec = randint(0, 3)
            time.sleep(sleep_sec)
            html = save_raw_html(doc_id)
            # soup = save_parse_ready_html(doc_id, html)
            # text = save_text(doc_id, soup)
            # save_feats({doc_id:text})
            meta_html = save_meta_raw_html(doc_id)
            meta_text = save_meta_text(doc_id, meta_html)
            with open("logs/parsed-docs.csv", "a") as fc:
                wr = csv.writer(fc, quoting=csv.QUOTE_ALL)
                wr.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), doc_id,
                    "%8d" % (len(html) if html is not None else 0),
                    hashlib.md5(html).hexdigest() if html is not None else "",
                    # "meta" # if Fişa actului juridic was saved
                ])
                fc.truncate()
            print doc_id
    fca.truncate()

'''
rng = range(1, 285000) + range(375498, 500000)
for doc_id in rng:
    sleep_sec = randint(0, 3)
    time.sleep(sleep_sec)
    html = save_raw_html(doc_id)
    soup = save_parse_ready_html(doc_id, html)
    text = save_text(doc_id, soup)
    # save_feats({doc_id:text})
    meta_html = save_meta_raw_html(doc_id)
    meta_text = save_meta_text(doc_id, meta_html)
    with open("logs/parsed-docs.csv", "a") as fc:
        wr = csv.writer(fc, quoting=csv.QUOTE_ALL)
        wr.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), doc_id,
            "%8d" % (len(html) if html is not None else 0),
            hashlib.md5(html).hexdigest() if html is not None else "",
            # "meta" # if Fişa actului juridic was saved
        ])
        fc.truncate()
    print doc_id
'''
'''
    with open("logs/last-parsed-mo-no.txt", "r+") as ft:
        mo_no = int(ft.read()) - 1
        mo_html = save_mo_raw_html(mo_no)
        with open("logs/parsed-mo.csv", "a") as fcm:
            wr = csv.writer(fcm, quoting=csv.QUOTE_ALL)
            wr.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), mo_no,
                "%8d" % (len(mo_html) if mo_html is not None else 0)
            ])
            fcm.truncate()
        ft.seek(0)
        ft.write(str(mo_no))
        ft.truncate()


    with open("logs/last-parsed-doc-ids.js", "r+") as fj:
        try:
            l_ids = json.loads(fj.read())
        except ValueError, e:
            l_ids = [0, 0, 0, 0]
        # print l_ids
        id_sp = sleep_sec % 4 # there are 4 starting points to parse by id
        # print l_ids[id_sp]
        if l_ids[id_sp] != 0:
            doc_id = l_ids[id_sp] + 1
        else:
            doc_id  = 285251 + id_sp * 21855
        l_ids[id_sp] = doc_id
        html = save_raw_html(doc_id)
        soup = save_parse_ready_html(doc_id, html)
        text = save_text(doc_id, soup)
        # save_feats({doc_id:text})
        meta_html = save_meta_raw_html(doc_id)
        meta_text = save_meta_text(doc_id, meta_html)
        with open("logs/parsed-docs.csv", "a") as fc:
            wr = csv.writer(fc, quoting=csv.QUOTE_ALL)
            wr.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), doc_id,
                "%8d" % (len(html) if html is not None else 0),
                hashlib.md5(html).hexdigest() if html is not None else "",
                # "meta" # if Fişa actului juridic was saved
            ])
            fc.truncate()
        fj.seek(0)
        fj.write(json.dumps(l_ids))
        fj.truncate()
'''

# (372670−285251)/24/30/12=10.117939815 10 years
# (372670−285251)/60/24/30=2.02358796 2 months
