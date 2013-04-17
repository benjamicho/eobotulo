#!/usr/bin/env python
# -*- coding: utf8 -*- 

import os, re, syslog, urllib, urllib2, random, json, HTMLParser
from datetime import datetime, timedelta
from botbase import BotBase
import config, util

chan_cmd = re.compile(r"\.\w+", re.U)
priv_cmd = re.compile(r"\.?\w+", re.U)
aktiva = re.compile(r"\.?(aktiva|active)$", re.I)
alfabeto = re.compile(r"\.?(alf(abeto)?|alphabet)$", re.I)
av = re.compile(r"\.?av$", re.I)
cxapeloj = re.compile(r"\.?((ĉ|c[xh])ap(eloj)?|accents)$", re.I)
diru = re.compile(r"\.?(dir[ui]|say)$", re.I)
espdic = re.compile(r"\.?(ed|espdic)$", re.I)
etim = re.compile(r"\.?(etim(ologio)?|etym(ology)?)$", re.I)
guglu = re.compile(r"\.?(gugl[uio]|google)$", re.I)
helpu = re.compile(r"\.?help[uoi]?$", re.I)
kategorio = re.compile(r"\.?(kat(egorio)?|cat(egory)?)$", re.I)
kioestas = re.compile(r"\.?(kio(estas)?|what(is)?)$", re.I)
komandoj = re.compile(r"\.?(komandoj|commands)$", re.I)
komputeko = re.compile(r"\.?komp(uteko)?$", re.I)
majstro = re.compile(r"\.?majstro$", re.I)
mortu = re.compile(r"\.?(mort[ui]|die)$", re.I)
pagxaro = re.compile(r"\.?(pa(ĝ|g[xh])aro|web(site)?)$", re.I)
ping = re.compile(r"\.?ping$", re.I)
plejaktivaj = re.compile(r"\.?(plejaktivaj|mostactive)$", re.I)
plejoftaj = re.compile(r"\.?(plejoftaj|mostoften)$", re.I)
proverbo = re.compile(r"\.?pro(verbo?)?$", re.I)
regulo = re.compile(r"\.?(reg(uloj?)?|rules?)$", re.I)
renomu = re.compile(r"\.?(renom[ui]|rename)$", re.I)
revo = re.compile(r"\.?re(ta)?vo(rtaro)?$", re.I)
rimo = re.compile(r"\.?(rim[oui]|rhyme)$", re.I)
seed = re.compile(r"\.?seed$", re.I)
sendu = re.compile(r"\.?send[ui]?$", re.I)
ssv = re.compile(r"\.?(bonalingvo|bona|ssv|bonalingvigi)$", re.I)
tajpi = re.compile(r"\.?tajpi$", re.I)
tez = re.compile(r"\.?(tez(aŭro)?|thesaurus)$", re.I)
traduku = re.compile(r"\.?(tra(d(uk[ui])?)?|trans(late)?)$", re.I)
trancxu = re.compile(r"\.?(tran(ĉ|c[xh])[ui]|cut)$", re.I)
vidita = re.compile(r"\.?(vid(ita)?|seen)$", re.I)
viki = re.compile(r"\.?viki(pedio)?$", re.I)
wiki = re.compile(r"\.?wiki(pedia)?$", re.I)

class Bot(BotBase):
	
	def run_cmd(self, nick, to, cmd, args):
		try:
			args = args.strip()
			if aktiva.match(cmd):
				return self.run_aktiva()
			elif alfabeto.match(cmd):
				return self.run_alfabeto()
			elif av.match(cmd):
				return self.run_av(args)
			elif cxapeloj.match(cmd):
				return self.run_cxapeloj(args)
			elif diru.match(cmd):
				return self.run_diru(args)
			elif espdic.match(cmd):
				return self.run_espdic(args)
			elif etim.match(cmd):
				return self.run_etim(args)
			elif guglu.match(cmd):
				return self.run_guglu(args)
			elif helpu.match(cmd):
				return self.run_helpu(args)
			elif kategorio.match(cmd):
				return self.run_kategorio(args)
			elif kioestas.match(cmd):
				return self.run_kioestas(args)
			elif komandoj.match(cmd):
				return self.run_komandoj()
			elif komputeko.match(cmd):
				return self.run_komputeko(args)
			elif majstro.match(cmd):
				return self.run_majstro(args)
			elif mortu.match(cmd):
				return self.run_mortu(args)
			elif pagxaro.match(cmd):
				return self.run_pagxaro()
			elif ping.match(cmd):
				return self.run_ping()
			elif plejaktivaj.match(cmd):
				return self.run_plejaktivaj()
			elif plejoftaj.match(cmd):
				return self.run_plejoftaj()
			elif proverbo.match(cmd):
				return self.run_proverbo(args)
			elif regulo.match(cmd):
				return self.run_regulo(args)
			elif renomu.match(cmd):
				return self.run_renomu(args)
			elif revo.match(cmd):
				return self.run_revo(args)
			elif rimo.match(cmd):
				return self.run_rimo(args)
			elif seed.match(cmd):
				return self.run_seed(args)
			elif sendu.match(cmd):
				return self.run_sendu(nick, to, args)
			elif ssv.match(cmd):
				return self.run_ssv(args)
			elif tajpi.match(cmd):
				return self.run_tajpi()
			elif tez.match(cmd):
				return self.run_tez(args)
			elif traduku.match(cmd):
				return self.run_traduku(args)
			elif trancxu.match(cmd):
				return self.run_trancxu(args)
			elif vidita.match(cmd):
				return self.run_vidita(args)
			elif viki.match(cmd):
				return self.run_viki(args)
			elif wiki.match(cmd):
				return self.run_wiki(args)
			else:
				return "%s: commando incognite. Pro adjuta reguarda %s" % (cmd, config.help)
		except Exception as e:
			error = "ERROR: %s" % str(e)
			if config.do_syslog:
				syslog.syslog(syslog.LOG_ERR, error)
			return error
	
	def url(self, nick, msg, to):
		if re.match( "^https?:", msg, re.I ):
			try:
				html = util.get_html(msg, masquerade=True)
				if html:
					m = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
					if m:
						title = m.group(1).strip()
						parser = HTMLParser.HTMLParser()
						title = parser.unescape(title)
						if type(title) == unicode:
							title = title.encode('utf-8')
						self.send(to, "Le titulo del pagina es: %s" % title)
			except Exception as e:
				error = "ERROR: %s" % str(e)
				if config.do_syslog:
					syslog.syslog(syslog.LOG_ERR, error)

	def cmd(self, nick, msg, to):
		""" Overriding from BotBase """
		regex = chan_cmd if to.startswith("#") else priv_cmd
		if regex.match(msg):
			msg = msg.split(None, 1)
			cmd = msg[0]
			args = msg[1] if len(msg) > 1 else ""
			result = self.run_cmd(nick, to, cmd, args)
			if result:
				result = result.splitlines()
				if len(result) > 5 and to.startswith("#"):
					self.send(to, "%s: Io inviava a te le rezultato de tu commando in privato, pois que illo ha plus multe que cinque lineas." % nick)
					self.send(nick, result)
				else:
					self.send(to, result)

	def run_aktiva(self):
		active = datetime.utcnow() - self.started
		hours = active.seconds/3600
		minutes = (active.seconds/60)-(hours*60)
		return "EoBot es active durante %s dies, %s horas e %s minutes." % (active.days, hours, minutes)	
			
	def run_alfabeto(self):
		return """Majuskla: ABCĈDEFGĜHĤIJĴKLMNOPRSŜTUŬVZ
Minuskla: abcĉdefgĝhĥijĵklmnoprsŝtuŭvz
Liternomoj: a bo co ĉo do e fo go ĝo ho ĥo i jo ĵo ko lo mo no o po ro so ŝo to u ŭo vo zo"""

	def run_cxapeloj(self, args):
		if re.match("-k$", args, re.I):
			return """Litero Kodo Hex
Ĉ      264  108
ĉ      265  109
Ĝ      284  11C
ĝ      285  11D
Ĥ      292  124
ĥ      293  125
Ĵ      308  134
ĵ      309  135
Ŝ      348  15C
ŝ      349  15D
Ŭ      364  16C
ŭ      365  16D"""
		else:
			return "ĉĝĥĵŝŭ ĈĜĤĴŜŬ"
	
	def run_av(self, args):
		if not args:
			return "Necesas specifi radikon. Por helpo vidu %s" % self.help_url("av")
		root = urllib.quote(util.x_to_unicode(args))
		html = util.get_html(config.av_search % root)
		mlnk = re.search(r'<td class="formo"><a href="(.+?)" title="Ligilo al la Fundamento">(.+?)</a></td>', html)
		mele = re.search(r'<td class="formo">(.+?)</td>', html)
		mbaz = re.search(r'<td class="bazformo">(.+?)</td>', html)
		msta = re.search(r'<td class="statuso">(.+?)</td>', html)
		mbro = re.search(r'<td class="bro">(.+?)</td>', html)
		if not mele:
			return 'Nenio trovita por "%s".' % args
		else:
			link = config.av_site + mlnk.group(1).strip() if mlnk else ""
			elemento = mlnk.group(2).strip() if mlnk else mele.group(1).strip()
			bazformo = mbaz.group(1).strip() if mbaz else ""
			statuso = re.sub(r".*? \+?", "", msta.group(1).strip()).upper()[0] if msta else ""
			bro = mbro.group(1).strip()[3] if mbro else ""
		ret = []
		ret.append("Elemento: %s %s" % (elemento, link))
		ret.append("Bazformo: %s" % bazformo)
		last = []
		if statuso:
			last.append("La radiko %s troviĝas en la" % elemento)
			if statuso == "F":
				last.append("Fundamento de Esperanto")
			else:
				last.append({"1": "Unua",
							 "2": "Dua",
							 "3": "Tria",
							 "4": "Kvara",
							 "5": "Kvina",
							 "6": "Sesa",
							 "7": "Sepa",
							 "8": "Oka",
							 "9": "Naŭa"}[statuso])
				last.append("Aldono al la Universala Vortaro")
		if bro:
			if statuso:
				last.append("kaj")
			else:
				last.append("La radiko %s troviĝas en" % elemento)
			last.append("Grupo %s de la Baza Radikaro Oficiala" % bro)
		ret.append(" ".join(last))
		return "\n".join(ret) + "."

	def run_diru(self, args):
		args = args.split(None, 2)
		if len(args) > 2 and args[0] == config.admin_pwd:
			self.connection.privmsg(args[1], args[2])
			
	def run_espdic(self, args):
		if not args:
			return "Necesas specifi vorton. Por helpo vidu %s" % self.help_url("espdic")
		word = util.x_to_unicode(args)
		with open(config.espdic_file) as f:
			ret = []
			regex = re.compile(r"\b%s\b" % word, re.U | re.I)
			for line in f:
				m = regex.search(line)
				if m:
					ret.append(line.strip())
		if ret:
			return "\n".join(ret)
		else: 
			return 'Nenio trovita por "%s".' % args	
	
	def run_etim(self, args):
		if not args:
			return "Necesas specifi vorton. Por helpo vidu %s" % self.help_url("etim")
		with open(config.etim_file) as f:
			etim = f.read()
		m = re.search("^%s-? =.*" % args, etim, re.U | re.I | re.M)
		if not m:
			return 'Nenio trovita por "%s".' % args
		else:
			return m.group(0)		
	
	def run_guglu(self, args):
		if not args:
			return "Necesas specifi serĉterminon. Por helpo vidu %s" % self.help_url("guglu")
		term = urllib.quote(args)
		url = config.google_search % term
		html = util.get_html(url, masquerade=True)
		m = re.search(r'<div id="?resultStats"?>((About )?(.+?) results)<(nobr|/div)>', html, re.I)
		if not m:
			return "Ne povis trovi la nombron da rezultoj."
		else:
			return m.group(1)		

	def run_helpu(self, args):
		return self.help_url(args)

	def help_url(self, args):
		if not args:
			return config.help
		elif alfabeto.match(args):
			return "%s#alfabeto" % config.help
		elif av.match(args):
			return "%s#av" % config.help
		elif cxapeloj.match(args):
			return "%s#%s" % (config.help, urllib.quote("ĉapeloj"))
		elif espdic.match(args):
			return "%s#espdic" % config.help 
		elif etim.match(args):
			return "%s#etim" % config.help
		elif guglu.match(args):
			return "%s#guglu" % config.help
		elif helpu.match(args):
			return "%s#helpu" % config.help
		elif kategorio.match(args):
			return "%s#kategorio" % config.help
		elif kioestas.match(args):
			return "%s#kioestas" % config.help
		elif komandoj.match(args):
			return "%s#komandoj" % config.help
		elif komputeko.match(args):
			return "%s#komputeko" % config.help
		elif majstro.match(args):
			return "%s#majstro" % config.help
		elif pagxaro.match(args):
			return "%s#%s" % (config.help, urllib.quote("paĝaro"))
		elif ping.match(args):
			return "%s#ping" % config.help
		elif plejaktivaj.match(args):
			return "%s#plejaktivaj" % config.help
		elif plejoftaj.match(args):
			return "%s#plejoftaj" % config.help
		elif proverbo.match(args):
			return "%s#proverbo" % config.help
		elif regulo.match(args):
			return "%s#regulo" % config.help
		elif revo.match(args):
			return "%s#revo" % config.help
		elif rimo.match(args):
			return "%s#rimo" % config.help
		elif seed.match(args):
			return "%s#seed" % config.help
		elif sendu.match(args):
			return "%s#sendu" % config.help
		elif tajpi.match(args):
			return "%s#tajpi" % config.help
		elif tez.match(args):
			return "%s#tez" % config.help
		elif traduku.match(args):
			return "%s#traduku" % config.help
		elif trancxu.match(args):
			return "%s#%s" % (config.help, urllib.quote("tranĉu"))
		elif vidita.match(args):
			return "%s#vidita" % config.help
		elif viki.match(args):
			return "%s#viki" % config.help
		elif wiki.match(args):
			return "%s#wiki" % config.help
		else:
			return "%s: nekonata komando. Por helpo vidu %s" % (args, config.help)

	def run_kategorio(self, args):
		if not args:
			return "Necesas specifi radikon. Por helpo vidu %s" % self.help_url("kategorio")
		root = util.x_to_unicode(args)
		with open(config.kategorioj_file) as f:
			for line in f:
				if line.startswith("%s/" % root):
					return line.strip()
		return 'Nenio trovita por "%s".' % args

	kioestas_index = 0
	last_kioestas_term = ""
	def run_kioestas(self, args):
		if not args:
			return "Necesas specifi terminon. Por helpo vidu %s" % self.help_url("kioestas")
		with open(config.kioestas_file) as f:
			kio = f.read()
		term = util.x_to_unicode(args)
		kio = re.findall(r"(.+?)\|(\b%s\b.*)" % term, kio, re.U | re.I)
		if kio:
			if term != self.last_kioestas_term:
				self.kioestas_index = random.randint(0, len(kio)-1)
			elif self.kioestas_index >= len(kio):
				self.kioestas_index = 0
			nick = kio[self.kioestas_index][0]
			quote = kio[self.kioestas_index][1]
			self.kioestas_index += 1
			self.last_kioestas_term = term
			return "%s\n-%s" % (quote, nick)
		else:
			return 'Nenio trovita por "%s".' % args

	def run_komandoj(self):
		return """.alfabeto .av .ĉapeloj .espdic .etim .guglu .helpu .kategorio .kioestas .komandoj .komputeko .majstro .paĝaro .ping .plejaktivaj .plejoftaj .proverbo .regulo .revo .rimo .seed .sendu .tajpi .tez .traduku .tranĉu .vidita .viki .wiki
Por pli ampleksa helpo vidu %s""" % config.help
	
	def run_komputeko(self, args):
		if not args:
			return "Necesas specifi vorton. Por helpo vidu %s" % self.help_url("komputeko")
		word = urllib.quote(util.x_to_unicode(args))
		url = config.komputeko_search % word
		html = util.get_html(url)
		if "ne ekzistas en Komputeko" in html or "Bonvolu tajpi almenaŭ" in html:
			return 'Nenio trovita por "%s".' % args
		else:
			return url
		
	def run_majstro(self, args):
		args = args.split(None, 2)
		if len(args) < 3:
			return "Necesas specifi de-lingvon kaj al-lingvon, kaj tradukotaĵon. Por helpo vidu %s" % self.help_url("majstro")
		fr = args[0].lower()
		fr = util.iso6391_to_iso6392.get(fr, fr)
		to = args[1].lower()
		to = util.iso6391_to_iso6392.get(to, to)
		word = util.x_to_unicode(args[2])
		return self.trans_majstro(fr, to, word)
		
	def run_mortu(self, args):
		args = args.split(None, 1)
		argc = len(args)
		if argc > 0 and args[0] == config.admin_pwd:
			if argc > 1:
				msg = args[1]
			else:
				msg = config.die_msg
			self.die(msg)
	
	def run_pagxaro(self):
		return config.website

	def run_ping(self):
		return "pong"
	
	def run_plejaktivaj(self):
		with open(config.nick_index_file) as f:
			lines = f.read().splitlines()
			return "Jen la 20 plej aktivaj parolantoj, kun vort-totaloj:\n%s" % ", ".join(lines[:20])

	#todo:
	#verbs
	#nouns
	#adjectives
	#adverbs
	#pronouns
	#prepositions
	#conjunctions
	#correlatives
	#numerals
	#particles

	def run_plejoftaj(self):
		with open(config.word_index_file) as f:
			lines = f.read().splitlines()
			lines = [line.split()[0] for line in lines[:100]]
			return "Jen la 100 plej oftaj vortoj:\n%s\n%s" % (", ".join(lines[:50]), ", ".join(lines[50:101]))
	
	proverbo_index = 0
	last_proverbo_word = ""
	def run_proverbo(self, args):
		with open(config.proverboj_file) as f:
			proverbs = f.read() if args else f.readlines()
		if args:
			word = util.x_to_unicode(args)
			proverbs = re.findall(r".*\b%s\b.*" % word, proverbs, re.U | re.I)
			if proverbs:
				if word != self.last_proverbo_word:
					self.proverbo_index = random.randint(0, len(proverbs)-1)
				elif self.proverbo_index >= len(proverbs):
					self.proverbo_index = 0
				proverb = proverbs[self.proverbo_index]
				self.proverbo_index += 1
				self.last_proverbo_word = word
				return proverb
			else:
				return 'Nenio trovita por "%s".' % args
		else:
			return random.choice(proverbs)

	def run_renomu(self, args):
		args = args.split(None, 1)
		if len(args) > 1 and args[0] == config.admin_pwd:
			self.connection.nick(args[1])
	
	def run_regulo(self, args):
		if not args:
			return 'Necesas specifi regulnumeron. Por helpo vidu %s' % self.help_url("reguloj")
		elif re.match("(1|unu|one)$", args, re.I):
			return '1. Ne ekzistas nedifinita artikolo. Ekzistas nur difinita artikolo "la", egala por ĉiuj genroj, kazoj, kaj nombroj.'
		elif re.match("(2|du|two)$", args, re.I):
			return '2. Substantivoj estas formataj per aldono de "o" al la radiko. Por la formado de la pluralo aldonu la finaĵon "j" al la singularo. La akuzativo aldonas "n" post la "o" aŭ la "oj". La ceteraj kazoj estas esprimataj per prepozicioj.'
		elif re.match("(3|tri|three)$", args, re.I):
			return '3. Adjektivoj estas formataj per aldono de "a" al la radiko, kaj kazoj kaj nombroj kiel ĉe substantivoj. La komparativo estas farata per "pli" kaj la superlativo per "plej".'
		elif re.match("(4|kvar|four)$", args, re.I):
			return '4. La bazaj numeraloj estas unu, du, tri, kvar, kvin, ses, sep, ok, naŭ, dek, cent, mil. La dekoj kaj centoj estas formataj per kunigo de la numeraloj. La ordigaj numeraloj havas la finaĵon "a" kaj en akuzativo "an".'
		elif re.match("(5|kvin|five)$", args, re.I):
			return '5. La personaj pronomoj estas mi, vi, li, ŝi, ĝi, si, ni, ili, oni. Posedaj pronomoj havas la finaĵon "a", kaj en akuzativo "n".'
		elif re.match("(6|ses|six)$", args, re.I):
			return '6. La verboj ne estas ŝanĝataj laŭ personoj nek nombroj. La nun-tempo finiĝas per "as", la pasinta tempo per "is", la venonta tempo per "os", la kondicionalo per "us", la imperativo per "u", kaj la infinitivo per "i". Estas ankaŭ participoj aktivaj (kun "ant", "int", "ont") kaj pasivaj (kun "at", "it", "ot"). La prepozicio ĉe la pasivo estas "de".'
		elif re.match("(7|sep|seven)$", args, re.I):
			return '7. Adverboj estas formataj per aldono de "e" al la radiko.'
		elif re.match("(8|ok|eight)$", args, re.I):
			return '8. Prepozicioj per si mem uzas la nominativon.'
		elif re.match("(9|naŭ|nine)$", args, re.I):
			return '9. Ĉiu vorto estas legata, kiel ĝi estas skribita.'
		elif re.match("(10|dek|ten)$", args, re.I):
			return '10. La akcento estas ĉiam sur la antaŭlasta silabo.'
		elif re.match("(11|dek unu|eleven)$", args, re.I):
			return '11. Kunmetitaj vortoj estas formataj per simpla kunigo de la radikoj de la vortoj. La ĉefa vorto staras je la fino.'
		elif re.match("(12|dek du|twelve)$", args, re.I):
			return '12. Se en frazo estas alia nea vorto, forlasu la "ne".'
		elif re.match("(13|dek tri|thirteen)$", args, re.I):
			return '13. Por indiki movon al loko, oni povas uzi la finiĝon "n".'
		elif re.match("(14|dek kvar|fourteen)$", args, re.I):
			return '14. Ĉiu prepozicio havas difinitan signifon. "Je" ne havas memstaran signifon.'
		elif re.match("(15|dek kvin|fifteen)$", args, re.I):
			return '15. La tiel nomataj "fremdaj vortoj" estas uzataj sen ŝanĝo. Derivaĵoj prefere estu formataj surbaze de la reguloj de la Esperanta gramatiko.'
		elif re.match("(16|dek ses|sixteen)$", args, re.I):
			return '16. La "o" de la substantivoj kaj la "a" de "la" povas esti iafoje forlasataj kaj anstataŭataj de apostrofo pro belsoneco.'
		else:
			return "%s estas nevalida regulnumero. Por helpo vidu %s" % (args, self.help_url("regulo"))

	def run_revo(self, args):
		if not args:
			return "Necesas specifi vorton. Por helpo vidu %s" % self.help_url("revo")
		if args.lower() == "sal":
			return "%s/revo/sal.html" % config.zz9pza
		word = urllib.quote(util.x_to_unicode(args))
		html = util.get_html(config.revo_search % word)
		if "Neniu trafo" in html:
			return 'Nenio trovita por "%s".' % args 
		ret = []
		esperante = False
		for line in html.splitlines():
			if line.startswith("<h1>"):
				lang = re.search(r"<h1>(.+?)</h1>", line).group(1).split()[0]
				esperante = lang=="esperante"
				ret.append("-%s-" % lang)
			if line.startswith("<a"):
				if esperante:
					m = re.search(r'href="(.+?)">(.+?)</a>', line)
					eo_word, link = m.group(2).split()[0], config.revo_site+m.group(1)
					ret.append("%s %s" % (eo_word, link))
				else:
					m = re.search(r'>(.+?)</a>', line)
					word = m.group(1)
					m = re.search(r'\(.+?href="(.+?)">(.+?)</a>', line)
					eo_word, link = m.group(2).split()[0], config.revo_site+m.group(1)
					ret.append("%s (%s) %s" % (word, eo_word, link))
		return "\n".join(ret)
	
	def run_rimo(self, args):
		if len(args) < 2:
			return "Necesas specifi fonemojn. Por helpo vidu %s" % self.help_url("rimo")
		phoneme = util.x_to_unicode(args)
		with open(config.kategorioj_file) as f:
			ret = []
			buf = []
			regex = re.compile(r"(.*%s)/" % phoneme, re.U | re.I)
			for line in f:
				m = regex.search(line)
				if m:
					buf.append(m.group(1))
				if len(buf) >= 30:
					ret.append(", ".join(buf))
					del buf[:]
		if buf:
			ret.append(", ".join(buf))	
		if ret:
			return "\n".join(ret)
		else: 
			return 'Nenio trovita por "%s".' % args
	
	def run_seed(self, args):
		if not args:
			return "Necesas specifi vorton. Por helpo vidu %s" % self.help_url("seed")
		word = urllib.quote(util.x_to_unicode(args))
		url = config.seed_search % word
		html = util.get_html(url)
		if "Word not found" in html:
			return 'Nenio trovita por "%s".' % args
		return url
	
	def run_sendu(self, nick, to, args):
		args = args.split(None, 1)
		if len(args) < 2:
			return "Necesas specifi ricevonton de komandorezulto, kaj komandon. Por helpo vidu %s" % self.help_url("sendu")
		dest = args[0]
		msg = args[1].split(None, 1)
		cmd = msg[0]
		args2 = msg[1] if len(msg) > 1 else ""
		result = self.run_cmd(nick, to, cmd, args2)		
		receiver = "la kanalo" if dest.startswith("#") else "vi"
		msg = "%s sendis al %s la jenan komandorezulton, de komando %s:" % (nick, receiver, args[1])
		self.send(dest, msg)
		self.send(dest, result)		
		return "%s: La rezulto de via komando estis sendita al %s" % (nick, dest)
	
	def run_tajpi(self):
		return """Senkosta klavarilo por esperantistoj, uzebla en Windows 2000, XP, Vista, 7, 8
Elŝutu ĝin de %s""" % config.tajpi

	def run_tez(self, args):
		if not args:
			return "Necesas specifi vorton. Por helpo vidu %s" % self.help_url("tez")
		word = util.x_to_unicode(args)
		with open(config.tez_file) as f:
			ret = []
			regex = re.compile(r"(^|, )%s($|,)" % word, re.U | re.I)
			for line in f:
				m = regex.search(line)
				if m:
					ret.append(line.strip())
		if ret:
			return "\n".join(ret)
		else: 
			return 'Nenio trovita por "%s".' % args
						
	def run_traduku(self, args):		
		m = re.search(r"(-\w+)?\s*(.*)", args)
		site = ""
		if m.group(1):
			site = m.group(1)[1:]
		args = m.group(2).split(None, 2)
		if len(args) < 3:
			return "Necesas specifi de-lingvon kaj al-lingvon, kaj tradukotaĵon. Por helpo vidu %s" % self.help_url("traduku")
		fr = args[0].lower()
		to = args[1].lower()
		translate = util.x_to_unicode(args[2])
		if not site:
			site = "m" if ((fr == "eo" or to == "eo") and " " not in translate) else "gt"
		if site == "m":
			fr = util.iso6391_to_iso6392.get(fr, fr)
			to = util.iso6391_to_iso6392.get(to, to)
			return self.trans_majstro(fr, to, translate)
		else:
			return self.trans_google(fr, to, translate)
		
	def run_ssv(self, args):
		if not args:
			return "Necesas specifi vorton."
		with open(config.ssv_file) as f:
			ssv = f.read()
		m = re.search("^%s-? =.*" % args, ssv, re.U | re.I | re.M)
		if not m:
			return 'Nenio trovita por "%s".' % args
		else:
			return m.group(0)

	def trans_majstro(self, fr, to, word):
		qword = urllib.quote(word)
		url = config.majstro_search % (fr, to, qword)
		html = util.get_html(url)
		if "could not be translated" in html:
			return 'Nenio trovita por "%s".' % word
		results = re.findall(r"<li>.+?</li>", html)
		ret = "\n".join(results)
		ret = util.strip_tags(ret)
	
		parser = HTMLParser.HTMLParser()
		ret = ret.decode('utf-8')
		ret = parser.unescape(ret)
		if type(ret) == unicode:
			ret = ret.encode('utf-8')

		ret = re.sub(": ", " → ", ret)
		ret = re.sub("; ", ", ", ret)
		return ret
		
	def trans_google(self, fr, to, translate):
		translate = urllib.quote(translate)
		url = config.google_translate_search % (translate, fr, to)
		jsn = util.get_html(url, masquerade=True)
		dic = json.loads(jsn)	
		src = dic["src"].encode('utf-8')
		trans = dic["sentences"][0]["trans"].encode('utf-8')
		translit = dic["sentences"][0]["translit"].encode('utf-8')
		ret = []
		if fr == "auto":
			ret.append('Tradukis de lingvo "%s"' % src)
		if not translit:
			ret.append(trans)
		else:
			ret.append("Traduko: %s" % trans)
			if trans != translit:
				ret.append("Transliterumo: %s" % translit)
		return "\n".join(ret)

	def run_trancxu(self, args):
		if not args:
			return "Necesas specifi vorton. Por helpo vidu %s" % self.help_url("tranĉu")
		word = urllib.quote(util.x_to_unicode(args))
		url = config.sivo_search % ("ser%c4%89o", word)
		html = util.get_html(url)
		html = re.search(r"<h2>Vortfarada Serĉo</h2>(.+?)<h2>", html, re.S).group(1)
		if "Neniu trovita" in html:
			return 'Nenio trovita por "%s".' % args
		else:
			ret = [util.strip_tags(line) for line in html.splitlines() if "<li>" in line]
			return "\n".join(ret) 
	
	def run_vidita(self, args):
		# for i in *; do mv "$i" "`stat $i | grep -Po \"(?<=Modify: )(\d\d\d\d-\d\d-\d\d)\"`.log"; done
		# command to rename old log files
		if not args:
			return "Necesas specifi nomon de uzanto. Por helpo vidu %s" % self.help_url("vidita")
		d = config.log_path
		logs = sorted([os.path.join(d, fn) for fn in os.listdir(d)], reverse=True)
		seen_line = ""
		regex = re.compile(r"<%s>" % args, re.I)
		for log in logs:
			with open(log) as f:
				for line in f:
					line = line.split(None, 2)
					if len(line) == 3:
						if regex.match(line[1]):
							seen_line = " ".join(line)
							seen_at = line[0]
				if seen_line:
					break	
		if not seen_line:
			return "Uzanto %s neniam estis vidita." % args
		else:
			try:
				seen_at_dt = datetime.strptime(seen_at, "[%Y-%m-%d_%H:%M:%S]")
			except:
				seen_at_dt = datetime.strptime(util.convert_old_dt(seen_at), "[%Y-%m-%d_%H:%M:%S]")
			ago = datetime.now() - seen_at_dt
			hours_ago = ago.seconds/3600
			minutes_ago = (ago.seconds/60)-(hours_ago*60)
			return "Uzanto %s estis vidita antaŭ %s tagoj, %s horoj kaj %s minutoj.\n%s" % (args, ago.days, hours_ago, minutes_ago, seen_line)
	
	def run_viki(self, args):
		if not args:
			return "Necesas specifi serĉesprimon. Por helpo vidu %s" % self.help_url("viki")
		term = urllib.quote(util.x_to_unicode(args))
		return config.wiki_link % ("eo", term)
		
	def run_wiki(self, args):
		m = re.search(r"(-\w+)?\s*(.*)", args)
		lang = "en"
		if m.group(1):
			lang = m.group(1)[1:]
		term = m.group(2)
		term = urllib.quote(util.x_to_unicode(term))
		if not term:
			return "Necesas specifi serĉesprimon. Por helpo vidu %s" % self.help_url("wiki")
		return config.wiki_link % (lang, term)
