#!/usr/bin/env python
# -*- coding: utf8 -*-

import os, re
import config, util
from counter import Counter

crap = re.compile(r"[^A-Za-zĉĝĥĵŝŭĈĜĤĴŜŬ\s']")
jn = re.compile(r"j?n?$")
simple_verbs = re.compile(r"([iaou]s|u)$")
la = re.compile(r"^l'$")
o = re.compile(r"'$")
#participles = re.compile(r"[iao]n?t[aoe]$")
kioestas = re.compile(r"(^|\.|\?)\s*((\w+ ){1,3}estas\b[^\.\?]*?(\.|\?|$))", re.U |re.I)
	
nicks = []
if os.path.exists(config.nick_index_file):
	with open(config.nick_index_file) as f:
		nicks = [line.split()[0] for line in f.read().splitlines()[:50]]

def is_exception(word):
	return word in nicks or len(word) > 20

np_particles = ["esperanto", "ajn", "ĉu", "jen", "ju", "ĵus", "kaj", "minus", "plej", "plu", "plus", "tamen", "tuj", "en", "ĝis", "kun", "nun", "sen", "unu", "du", "kvin", "bis", "nu", "okej", "then", "you"]

np_words = ["iu", "kiu", "tiu", "neniu", "ĉiu"]

def parse(word):
	word = simple_verbs.sub("i", word)
	word = la.sub("la", word)
	word = o.sub("o", word)
	#word = participles.sub("i", word)
	return word	
	
def lower(text):
	# Converting a UTF-8 encoded byte stream to lowercase appears to require
	# the data to be decoded before calling lower(), however this slows the
	# procedure down way too much, so we will just manually replace the Unicode
	# chars we're interested in.
	return text.lower()\
	.replace("Ĉ", "ĉ")\
	.replace("Ĝ", "ĝ")\
	.replace("Ĥ", "ĥ")\
	.replace("Ĵ", "ĵ")\
	.replace("Ŝ", "ŝ")\
	.replace("Ŭ", "ŭ")

def main():
	d = config.log_path
	word_counter = Counter()
	nick_counter = Counter()
	kioestas_lines = []
	for log in [os.path.join(d, fn) for fn in os.listdir(d)]:
		with open(log) as f:
			for line in f:
				#[2012-09-06_14:08:13] <tommjames> this is an example message
				line = line.split(None, 2)
				if len(line) == 3:
					nick = line[1][1:-1]
					msg = line[2]
					if nick != "EoBot" and nick != "eobot":
						m = kioestas.findall(msg)
						for k in m:
							kioestas_lines.append("%s|%s" % (nick, util.x_to_unicode(k[1])))				
						if nick != "KioEstas" and nick != "kioestas" and msg and not msg[0] in "*.!":							
							msg = lower(crap.sub("", msg))
							for word in msg.split():
								if not is_exception(word):
									word = util.x_to_unicode(word)
									if word in np_particles:
										word_counter[word] += 1
										nick_counter[nick] += 1
									else:
										nocase = jn.sub("", word)
										word = nocase if nocase in np_words else parse(nocase).replace("'", "")	
										if len(word) > 1:
											word_counter[word] += 1
											nick_counter[nick] += 1
	with open(config.kioestas_file, 'w') as f:
		f.write("\n".join(kioestas_lines)) 
	with open(config.word_index_file, 'w') as f:
		for key, val in word_counter.most_common():
			f.write("%s %s\n" % (key, val))
	with open(config.nick_index_file, 'w') as f:
		for key, val in nick_counter.most_common():
			f.write("%s %s\n" % (key, val))									

if __name__ == "__main__":
	main()
