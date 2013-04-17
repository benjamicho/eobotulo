#!/usr/bin/env python
# -*- coding: utf8 -*-

import re, urllib, urllib2

iso6391_to_iso6392 = {
"en": "eng",
"eo": "epo",
"af": "afr",
"sq": "alb",
"ca": "cat",
"cs": "ces",
"da": "dan",
"nl": "dut",
"fo": "fao",
"fi": "fin",
"fr": "fra",
"de": "deu",
"hu": "hun",
"is": "ice",
"it": "ita",
"la": "lat",
"no": "nor",
"nb": "nor",
"nn": "nor",
"pl": "pol",
"pt": "por",
"ro": "rom",
"ru": "rus",
"gd": "gae",
"es": "spa",
"sv": "sve",
"tl": "tgl",
"th": "tai",
"tr": "tur",
"fy": "fry"}

def x_to_unicode(text):
	text = text.replace("cx", "ĉ").replace("cX", "ĉ")
	text = text.replace("Cx", "Ĉ").replace("CX", "Ĉ")
	text = text.replace("gx", "ĝ").replace("gX", "ĝ")
	text = text.replace("Gx", "Ĝ").replace("GX", "Ĝ")
	text = text.replace("hx", "ĥ").replace("hX", "ĥ")
	text = text.replace("Hx", "Ĥ").replace("HX", "Ĥ")
	text = text.replace("jx", "ĵ").replace("jX", "ĵ")
	text = text.replace("Jx", "Ĵ").replace("JX", "Ĵ")
	text = text.replace("sx", "ŝ").replace("sX", "ŝ")
	text = text.replace("Sx", "Ŝ").replace("SX", "Ŝ")
	text = text.replace("ux", "ŭ").replace("uX", "ŭ")
	text = text.replace("Ux", "Ŭ").replace("UX", "Ŭ")
	return text

def get_html(url, lines=False, masquerade=False):	
	req = urllib2.Request(url)
	if masquerade:
		# Masquerade as Firefox in order to circumvent blocking of bots on various websites
		req.add_header("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7")
		req.add_header("Accept-Language", "en-gb,en;q=0.5")
		req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
		req.add_header("User-Agent", "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.2.10) Gecko/20100914 Firefox/3.6.10 ( .NET CLR 3.5.30729; .NET4.0E")
	f = urllib2.urlopen(req)
	html = f.readlines() if lines else f.read()
	f.close()
	return html

def strip_tags(text):
	return re.sub(r'<[^>]*?>', '', text).strip()

month_num = {"Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4", "May": "5", "Jun": "6", "Jul": "7", "Aug": "8", "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"}
def convert_old_dt(dt):
	# [06Sep2012_14:08:13] to [2012-09-06_14:08:13]
	m = re.match(r"\[(\d\d)(\w\w\w)(\d\d\d\d)_(\d\d):(\d\d):(\d\d)\]", dt)
	return "[%s-%s-%s_%s:%s:%s]" % (m.group(3), month_num[m.group(2)], m.group(1), m.group(4), m.group(5), m.group(6))
