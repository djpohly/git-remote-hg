"""Interface to Mercurial APIs

Uses 40-character hex nodeids consistently
"""

from mercurial import hg, node, revlog, filelog

from mercurial.ui import ui as Ui
from mercurial.mdiff import textdiff

NULLID = "0" * 40

def hash(text, p1, p2):
	return node.hex(revlog.hash(text, node.bin(p1), node.bin(p2)))

class Peer(object):
	def __init__(self, hgui, url):
		self.p = hg.peer(hgui, {}, url)

	def branchmap(self):
		return {name: [node.hex(h) for h in heads]
		        for name, heads in self.p.branchmap().viewitems()}

	def bookmarks(self):
		return self.p.listkeys("bookmarks")

def buildfile(text, extra=None):
	if not (extra or text.startswith("\1\n")):
		return text
	return "\1\n%s\1\n%s" % (filelog._packmeta(extra), text)

def buildmf(tree, files):
	def modeflags(num):
		mode = int(num, 8)
		fl = ""
		if mode & 0170000 == 0160000:
			raise NotImplementedError, "Gitlink/submodule"
		if mode & 0111 > 0:
			fl += "x"
		if mode & 0170000 == 0120000:
			fl += "l"
		return fl
	s = ""
	for ent in tree:
		s += "%s\0%s%s\n" % (ent[3], files[ent[3]], modeflags(ent[0]))
	return s

def makebundle(clog, mlog, flog):
	def tochunk(rev):
		chunk = ""
		for i in (rev.nodeid, rev.p1, rev.p2, rev.cs):
			if i is None:
				chunk += node.bin(rev.nodeid)
			else:
				chunk += node.bin(i)
		chunk += delta
		return struct.pack(">l", len(chunk)) + chunk
	def togroup(log):
		group = ""
		for rev in log.log:
			group += tochunk(rev)
		return group + struct.pack(">l", 0)
	bundle = togroup(clog) + togroup(mlog)
	for path, log in flog.viewitems():
		bundle += len(path) + path + togroup(log)
	return bundle
