#!/usr/bin/env python
# -*- coding: utf8 -*- 

import os, sys, re, time, atexit, syslog, signal
from pwd import getpwnam
from signal import SIGTERM

WORKDIR = "/"
UMASK = 0

# On some platforms the string "/dev/null" is reported not to work
# correctly, so we will check if our implementation has os.devnull,
# and if it does we use that.
if (hasattr(os, "devnull")):
	REDIRECT_TO = os.devnull
else:
	REDIRECT_TO = "/dev/null"

class Daemon:
	"""
	A generic daemon class. Subclass this class and override the run() method.
	
	Two modes of operation are supported:

	1) Fork a child to do the main daemon work, and leave cleanup to the parent.
	   The parent will simply sit and wait for the child process to exit, at which
	   point the parent will perform cleanup and exit. The parent process will run as
	   whichever user started the script, and the child will run under the user specified
	   in the 'run_as' parameter to the constructor. If the 'run_as' parameter is left
	   empty then the child will run as the user that started the script.

	   Typically in this mode you would start the daemon as the superuser, so the child
	   process may perform any root-only work before changing its UID and GID to that of
	   the unprivileged 'run_as' user. The parent process will remain running as root, so
	   that it can reliably clean up on exit.

	2) Run in a single process. This mode has the small disadvantage that the daemon would
	   not be able to clean up its pidfile in /var/run after changing to the unprivileged
	   user. The alternative is to run as root by starting the daemon as the superuser and
	   leaving the 'run_as' parameter empty (not a good idea!) or to use a subdirectory
	   within /var/run which is chowned to the user.
	"""

	def __init__(self, pidfile, log_app="", log_version="", run_as="", fork_child=False):
		if run_as == "root":
			raise Exception("User root not allowed in run_as parameter.")
		self.pidfile = pidfile
		self.log_app = log_app
		self.log_version = log_version
		self.run_as = run_as
		self.fork_child = fork_child
		self.delpid = True
		if log_app:
			syslog.openlog(log_app, syslog.LOG_PID, syslog.LOG_DAEMON)

	def daemonize(self):
		# Perform double-fork. See Stevens' "Advanced Programming
		# in the UNIX Environment" (ISBN 0201563177)
		# http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		try:
			pid = os.fork()
			if pid > 0:
				# Exit first parent.
				os._exit(0)
		except OSError as e:
			raise Exception("Fork #1 failed: %d (%s)" % (e.errno, e.strerror))

		# To become the session leader of this new session and the process group
		# leader of the new process group, we call os.setsid(). The process is
		# also guaranteed not to have a controlling terminal.
		os.setsid()
		
		# Do second fork.
		try:
			pid = os.fork()
			if pid > 0:
				# Exit second parent
				os._exit(0)
		except OSError as e:
			raise Exception("Fork #2 failed: %d (%s)" % (e.errno, e.strerror))

		# Since the current working directory may be a mounted filesystem, we
		# avoid the issue of not being able to unmount the filesystem at
		# shutdown time by changing it to the root directory.
		os.chdir(WORKDIR)
		
		# We probably don't want the file mode creation mask inherited from
		# the parent, so we give the child complete control over permissions.
		os.umask(UMASK)

		# Redirect standard file descriptors to /dev/null.
		sys.stdout.flush()
		sys.stderr.flush()
		si = open(REDIRECT_TO, 'r')
		so = open(REDIRECT_TO, 'a+')
		se = open(REDIRECT_TO, 'a+', 0)
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())

	def handle_sigterm(self, signum, frame):
		"""
		SIGTERM signal handler for whichever process does the main daemon work.
		Subclass can override this method to perform any custom operations which must
		take place before exit, while the daemon is still in a normal running state.
		"""
		sys.exit(0)
	
	def handle_sigterm_parent(self, signum, frame):
		"""
		SIGTERM signal handler for the parent process.
		"""
		# Kill the child process.
		try:
			os.kill(self.childpid, SIGTERM)
		except OSError as e:
			# if we failed to kill the child process then don't remove the pidfile.
			self.delpid = False
			if self.log_app:
				syslog.syslog(syslog.LOG_ERR, "ERROR: Could not kill child process (%s)" % str(e))
		# Exit, invoking cleanup via the registered atexit function.
		sys.exit(0)
			
	def cleanup(self):
		"""
		Removes the pidfile and closes log. Any other necessary cleanup operations can be put here.
		"""
		if self.delpid:
			os.remove(self.pidfile)
		if self.log_app:
			syslog.closelog()

	def change_user(self, user):
		try:
			pw = getpwnam(user)
			os.setgid(pw.pw_gid)
			os.setuid(pw.pw_uid)
		except OSError as e:
			raise Exception("Failed to change to user %s." % user)
	
	def running(self):
		return self.get_pid() is not None
 
	def get_pid(self):
		try:
			with open(self.pidfile, 'r') as f:				
				pid = int(f.read().strip())
		except IOError:
			pid = None
		return pid		
	
	def write_pid(self, pid):
		with open(self.pidfile, 'w') as f:
			f.write("%s\n" % str(pid))			

	def start(self):
		""" Start the daemon """
		if self.log_app:
			syslog.syslog(syslog.LOG_NOTICE, "%s v%s daemon starting up." % (self.log_app, self.log_version))
		
		# Check for a pidfile to see if the daemon is already running.
		if self.running():
			raise Exception("%s already exists. Daemon already running?" % self.pidfile)

		# Become a daemon
		self.daemonize()
		
		# Fork child to do main daemon work, or continue as a single process.
		if self.fork_child:
			
			# Fork the worker process.
			try:
				self.childpid = os.fork()
			except OSError as e:
				raise Exception("Fork failed: %d (%s)" % (e.errno, e.strerror))		
			
			if self.childpid > 0: # Parent process.						
				
				# Write pidfile.
				self.write_pid(os.getpid())
								
				# Register SIGTERM handler which will kill the child and exit.
				signal.signal(SIGTERM, self.handle_sigterm_parent)
				
				# Register cleanup function which runs on exit.		
				atexit.register(self.cleanup)
								
				# Wait for child to exit.
				os.waitpid(self.childpid, 0)
				
				# Parent process exits.
				sys.exit(0)			
			
			else: # Child process.						

				# Register SIGTERM handler which exits the process.
				signal.signal(SIGTERM, self.handle_sigterm)
				
				if self.log_app:
					syslog.syslog(syslog.LOG_NOTICE, "Startup complete.")
				
				# Do any tasks that require root privileges.
				self.root_work()

				# Change to the run_as user.
				if self.run_as:
					self.change_user(self.run_as)

				# Do daemon work.
				self.run()
				
		else: # Running as a single process.

			# Write pidfile.
			self.write_pid(os.getpid())
			
			# Register SIGTERM handler which exits the process.
			signal.signal(SIGTERM, self.handle_sigterm)

			# Register cleanup function which runs on exit.		
			atexit.register(self.cleanup)
			
			if self.log_app:
				syslog.syslog(syslog.LOG_NOTICE, "Startup complete.")

			# Do any tasks that require root privileges.
			self.root_work()

			# Change to the run_as user.
			if self.run_as:
				self.change_user(self.run_as)

			# Do daemon work.
			self.run()

	def stop(self, raise_error=True):
		""" Stop the daemon """
		if self.log_app:
			syslog.syslog(syslog.LOG_NOTICE, "%s daemon stopping." % self.log_app)
		
		# Get the pid from the pidfile.
		pid = self.get_pid()			
		if not pid:
			if raise_error:
				raise Exception("Could not get PID from %s. Daemon not running?" % self.pidfile)
			else:
				return

		# Try killing the daemon. This will kill the parent process if the daemon was
		# configured to fork a child. The parent's SIGTERM handler will kill the child.
		try:
			while True:
				os.kill(pid, SIGTERM)
				time.sleep(0.1)
		except OSError as e:
			if "No such process" in e.strerror:
				# If we got here then we successfully killed the process,
				# resulting in an exception next time round the loop. We
				# can let the SIGTERM handler clean up the pidfile.
				pass
			elif raise_error: raise
		
		if self.log_app:
			syslog.syslog(syslog.LOG_NOTICE, "Stopped")

	def restart(self):
		""" Restart the daemon """
		# Stop the daemon without raising any errors: pidfile won't be present if
		# restart is being used to start the daemon, but this should not create an error.
		self.stop(raise_error=False)
		self.start()
	
	def root_work(self):
		"""
		Override this method to do any work requiring root privileges, before change
		to the run_as user takes place. Typical tasks may include opening file handles,
		binding to low ports, opening logs etc.
		"""

	def run(self):
		"""
		Override this method when you subclass Daemon. It will be called after daemonization by start().
		"""
		while True:
			time.sleep(1)
