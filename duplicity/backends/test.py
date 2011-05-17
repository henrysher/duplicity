#!/usr/bin/python

_login_success = False
def login():
	from gobject import MainLoop
	from dbus.mainloop.glib import DBusGMainLoop
	from ubuntuone.platform.credentials import CredentialsManagementTool

	global _login_success
	_login_success = False

	DBusGMainLoop(set_as_default=True)
	loop = MainLoop()

	def quit(result):
		global _login_success
		loop.quit()
		if result:
			_login_success = True

	cd = CredentialsManagementTool()
	d = cd.login()
	d.addCallbacks(quit)
	loop.run()
	return _login_success

import urllib
import ubuntuone.couch.auth as auth
import json

def list(path):
	base = "https://one.ubuntu.com/api/file_storage/v1"
	answer = auth.request(base + "/~/" + urllib.quote(path))# + "?include_children=true")
	if len(answer) < 2:
		return False
	node = json.loads(answer[1])
	return True

def delete(path):
	base = "https://one.ubuntu.com/api/file_storage/v1"
	answer = auth.request(base + "/~/" + urllib.quote(path), http_method="DELETE")
	if len(answer) < 2:
		return False
	return True

def get(path, target):
	base = "https://one.ubuntu.com/api/file_storage/v1"
	answer = auth.request(base + "/~/" + urllib.quote(path))
	if len(answer) < 2:
		return False
	node = json.loads(answer[1])
	base = "https://files.one.ubuntu.com"
	content_url = base + urllib.quote(node['content_path'], safe="/~")
	answer = auth.request(content_url)
	if len(answer) < 2:
		return False
	f = open(target, 'wb')
	f.write(answer[1])
	return True

def put(source, path):
	base = "https://one.ubuntu.com/api/file_storage/v1"
	print base + "/~/" + urllib.quote(path)
	answer = auth.request(base + "/~/" + urllib.quote(path), http_method="PUT",
	                      request_body='{"kind":"file"}')
	if len(answer) < 2:
		return False
	node = json.loads(answer[1])
	base = "https://files.one.ubuntu.com"
	content_url = base + urllib.quote(node['content_path'], safe="/~")
	#f = open(source, 'rb')
	#data = f.read()
	data = "hello!"
	print content_url
	answer = auth.request(content_url, http_method="PUT", request_body=data)
	if len(answer) < 2:
		return False
	#print answer[1][:500]
	print answer[0]
	return True

def create_volume(root):
	base = "https://one.ubuntu.com/api/file_storage/v1/volumes/~/"
	answer = auth.request(base + urllib.quote(root), http_method="PUT")
	if len(answer) < 2:
		return False
	return True

def start(root):
	if not login():
		print "Could not obtain Ubuntu One credentials"
		import sys
		sys.exit(1)

	create_volume(root)


root = "deja-dup"
start(root)

#get("Ubuntu One/MIR.log", "/tmp/test")
put("/tmp/test", "deja-dup/blarg.txt")
