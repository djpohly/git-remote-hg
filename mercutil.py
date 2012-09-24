"""Interface to Mercurial APIs

Uses 40-character hex nodeids consistently
"""

from mercurial import hg, ui, node, revlog, filelog

nullid = "0" * 40

ui = ui.ui

def hash(text, p1, p2):
	return node.hex(revlog.hash(text, node.bin(p1), node.bin(p2)))

class peer(object):
	def __init__(self, ui, url):
		self.p = hg.peer(ui, {}, url)

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
