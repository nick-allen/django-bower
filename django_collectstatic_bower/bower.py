import json
import os

import subprocess

import sys
from django.conf import settings


def which(cmd, mode=os.F_OK | os.X_OK, path=None):
	"""Given a command, mode, and a PATH string, return the path which
	conforms to the given mode on the PATH, or None if there is no such
	file.

	`mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
	of os.environ.get("PATH"), or can be overridden with a custom search
	path.

	"""
	# Check that a given file can be accessed with the correct mode.
	# Additionally check that `file` is not a directory, as on Windows
	# directories pass the os.access check.
	def _access_check(fn, mode):
		return (os.path.exists(fn) and os.access(fn, mode)
				and not os.path.isdir(fn))

	# If we're given a path with a directory part, look it up directly rather
	# than referring to PATH directories. This includes checking relative to the
	# current directory, e.g. ./script
	if os.path.dirname(cmd):
		if _access_check(cmd, mode):
			return cmd
		return None

	if path is None:
		path = os.environ.get("PATH", os.defpath)
	if not path:
		return None
	path = path.split(os.pathsep)

	if sys.platform == "win32":
		# The current directory takes precedence on Windows.
		if not os.curdir in path:
			path.insert(0, os.curdir)

		# PATHEXT is necessary to check on Windows.
		pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
		# See if the given file matches any of the expected path extensions.
		# This will allow us to short circuit when given "python.exe".
		# If it does match, only test that one, otherwise we have to try
		# others.
		if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
			files = [cmd]
		else:
			files = [cmd + ext for ext in pathext]
	else:
		# On other platforms you don't have things like PATHEXT to tell you
		# what file suffixes are executable, so just pass on cmd as-is.
		files = [cmd]

	seen = set()
	for dir in path:
		normdir = os.path.normcase(dir)
		if not normdir in seen:
			seen.add(normdir)
			for thefile in files:
				name = os.path.join(dir, thefile)
				if _access_check(name, mode):
					return name
	return None


def get_bower_executable_path():
	"""Find bower executable"""
	try:
		return getattr(settings, 'BOWER_CMD')
	except AttributeError:
		return which('bower')


def get_bower_rc_path():
	"""Find .bowerrc file"""
	return getattr(settings, 'BOWER_RC_FILE', os.path.join(
		os.getcwd(),
		'.bowerrc'
	))


def get_bower_components_path():
	"""Returns bower components path"""
	rc = load_bower_rc()

	if rc:
		path = os.path.abspath(rc.get('directory', 'bower_components/'))
	else:
		path = os.path.join(
			os.getcwd(),
			'bower_components/'
		)

	return os.path.abspath(path)


def load_bower_rc():
	"""Returns parsed .bowerrc file"""
	try:
		with open(get_bower_rc_path()) as rc:
			return json.load(rc)
	except Exception:
		return None


def bower(*args):
	"""Runs bower with provided args"""
	cwd = os.getcwd()

	proc = subprocess.Popen(
		(get_bower_executable_path(),) + args + ('--allow-root',),
		cwd=cwd
	)
	proc.wait()

	if proc.returncode:
		raise RuntimeError('Bower command failed')

	return proc
