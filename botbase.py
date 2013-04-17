#!/usr/bin/env python
# -*- coding: utf8 -*-

import os, re, time, syslog
from datetime import datetime
from time import localtime, strftime, sleep
from ircbot import SingleServerIRCBot
from irclib import nm_to_n
import config

class BotBase(SingleServerIRCBot):

	def log(self, nick, msg):
		msg = msg.strip()
		if msg:
			t = time.localtime()
			logfile = os.path.join(config.log_path, "%s.log" % strftime("%Y-%m-%d", t))
			with open(logfile, 'a') as f:
				f.write("%s <%s> %s\n" % (strftime("[%Y-%m-%d_%H:%M:%S]", t), nick, msg))

	def on_ctcp(self, c, e):
		nick = nm_to_n(e.source())
		ctcp = e.arguments()[0].upper()
		if ctcp in ("VERSION", "FINGER", "SOURCE", "USERINFO"):
			c.ctcp_reply(nick, config.version_reply)
		elif ctcp == "PING":
			c.ctcp_reply(nick, "PING")
		elif ctcp == "TIME":
			c.ctcp_reply(nick, strftime("%Y-%m-%d %H:%M:%S", localtime()))

	def on_action(self, c, e):
		nick = nm_to_n(e.source())
		action = e.arguments()[0]
		if e.target() == config.channel:
			self.log(nick, "* %s" % action)

	def on_join(self, c, e):
		nick = nm_to_n(e.source())
		channel = e.target()
		self.log(nick, "* Eniras kanalon %s" % channel)

	def on_part(self, c, e):
		nick = nm_to_n(e.source())
		channel = e.target()
		self.log(nick, "* Eliras kanalon %s" % channel)

	def on_quit(self, c, e):
		nick = nm_to_n(e.source())
		msg = e.arguments()[0]
		self.log(nick, "* Eliras el IRC (%s)" % msg)

	def on_mode(self, c, e):
		nick = nm_to_n(e.source())
		channel = e.target()
		mode = e.arguments()[0]
		self.log(nick, "* Starigas reĝimon %s por kanalo %s" % (mode, channel))

	def on_kick(self, c, e):
		nick = nm_to_n(e.source())
		channel = e.target()
		kicked = e.arguments()[0]
		self.log(nick, "* Elĵetas %s de kanalo %s" % (kicked, channel))

	def on_nick(self, c, e):
		before = nm_to_n(e.source())
		after = e.target()
		self.log(before, "* Ŝanĝas nomon al %s" % after)

	def on_dccmsg(self, c, e):
		pass
	
	def on_dccchat(self, c, e):
		pass

	def on_error(self, c, e):
		if config.do_syslog:
			syslog.syslog(syslog.LOG_WARNING, "WARNING: on_error() called, arguments: %s, target: %s" % (e.arguments(), e.target()))
		#self.die(config.die_msg)
	
#	def on_disconnect(self, c, e):
#		server = e.source()
#		msg = e.arguments()[0]
#		if config.do_syslog:
#			syslog.syslog(syslog.LOG_WARNING, "WARNING: Disconnected from server %s: %s" % (server, msg))
#		self._on_disconnect(c, e)

	def on_erroneusnickname(self, c, e):
		nick = e.arguments()[0]
		if config.do_syslog:
			syslog.syslog(syslog.LOG_WARNING, "WARNING: Invalid nickname '%s'" % nick)

	def on_badchanmask(self, c, e):
		channel = event.arguments()[0]
		if config.do_syslog:
			syslog.syslog(syslog.LOG_WARNING, "WARNING: Invalid channel '%s'" % channel)

	def on_welcome(self, c, e):
		c.join(config.channel)
		self.started = datetime.utcnow()
	
	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")

	def cmd(self, nick, msg, to):
		""" Overridden in Bot """

	def url(self, nick, msg, to):
		""" Overridden in Bot """

	def on_pubmsg(self, c, e):
		nick = nm_to_n(e.source())
		msg = e.arguments()[0]
		channel = e.target()
		self.log(nick, msg)
		self.cmd(nick, msg, channel)
		self.url(nick, msg, channel)

	def on_privmsg(self, c, e):
		nick = nm_to_n(e.source())
		msg = e.arguments()[0]
		self.cmd(nick, msg, nick)

	def send(self, to, text):
		for line in text if type(text) == list else text.splitlines():
			self.connection.privmsg(to, line)
			time.sleep(config.send_delay)
