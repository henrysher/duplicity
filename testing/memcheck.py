"""Check for memory leak in tarfile.py.

Before somehow reading from a _FileObject as returned by extractfile()
would cause a memory leak.

"""

import sys, gzip, os, random
sys.path.insert(0, "../src")
import tarfile

def main():
	#gzipfile = gzip.GzipFile("/root/.duplicity/full/duplicity-signatures.2002-08-06T22:07:07-07:00.sigtar.gz", "rb")
	#gzipfile = os.popen("zcat /root/.duplicity/full/duplicity-signatures.2002-08-06T22:07:07-07:00.sigtar.gz")
	gzipfile = gzip.GzipFile(None, "r", 9,
							 open("/root/.duplicity/full/duplicity-signatures.2002-08-06T22:07:07-07:00.sigtar.gz", "rb"))
	tf =  tarfile.TarFile("none", "r", gzipfile)
	i = 0
	for tarinfo in tf:
		print tarinfo.name, i, tarinfo.size
		i += 1
		if tarinfo.isreg():
			fileobj = tf.extractfile(tarinfo)
			#buf = fileobj.read()
			buf = tf.fileobj.read(tarinfo.size)
			tf.offset += tarinfo.size

def main2():
	gzipfile  = gzip.GzipFile("/root/.duplicity/full/duplicity-signatures.2002-08-06T22:07:07-07:00.sigtar.gz", "rb")

	while 1:
		buf = gzipfile.read(random.randrange(0, 500000))
		#buf = gzipfile.read(500000)
		if not buf: break


main2()
