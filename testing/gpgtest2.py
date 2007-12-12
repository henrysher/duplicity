import config
import sys, os, time

config.setup()

import GnuPGInterface, thread

def main():
	gnupg = GnuPGInterface.GnuPG()
	gnupg.options.meta_interactive = 0
	gnupg.passphrase = "foobar"

	p1 = gnupg.run(['--symmetric'], create_fhs=['stdin', 'stdout'])
	
	if os.fork() == 0: # child
		p1.handles['stdin'].write("hello, world!")
		p1.handles['stdin'].close()
		os._exit(0)
	else: # parent
		p1.handles['stdin'].close()
		s = p1.handles['stdout'].read()
		p1.handles['stdout'].close()
		p1.wait()


def main2():
	a = range(500000)
	thread.start_new_thread(tmp, (a,))
	tmp(a)

def tmp(a):
	for i in range(10):
		for i in a: pass


main2()
