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
		        for name, heads in self.p.branchmap()}

	def bookmarks(self):
		return self.p.listkeys("bookmarks")

def buildfile(text, extra=None):
	if not (extra or text.startswith("\1\n")):
		return text
	return "\1\n%s\1\n%s" % (filelog._packmeta(extra), text)

def makebundle(clog, mlog, flog):
	# XXX implement once we decide how to store deltified logs
	raise NotImplementedError
