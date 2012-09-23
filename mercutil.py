"""Interface to Mercurial APIs
"""

import struct, collections, subprocess
from mercurial import hg, ui, node, revlog, filelog

nullid = "0" * 40

ui = ui.ui

Ftree = collections.namedtuple("Ftree", ["sha", "extra"])
Mtree = collections.namedtuple("Mtree", ["sha", "file"])
Ctree = collections.namedtuple("Ctree", ["sha", "mf", "extra"])

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

class revmap(object):
	def __init__(self, ref):
		args = ["git", "ls-tree", ref]
		# XXX rewrite to read incrementally
		# XXX CalledProcessError here means ref not found/valid
		tree = [l.split("\t") for l in
		        subprocess.check_output(args).splitlines()]
		self.rmap = {sha: info.split()[2] for info, sha in tree}
	# Currently raises KeyError if nodeid not in revmap, and
	# CalledProcessError if Ftree or its components not in repo
	def readftree(self, nodeid):
		# XXX KeyError here means node not in revmap
		args = ["git", "ls-tree", self.rmap[nodeid]]
		# XXX CalledProcessError here means entry deleted since revmap
		# was initialized
		tree = [l.split("\t") for l in
		        subprocess.check_output(args).splitlines()]
		sha = None
		extra = {}
		for ent in tree:
			# XXX CalledProcessError here means git repo corrupted
			# (sub-objects lost)
			if ent[1] == "sha":
				args = ["git", "cat-file", "blob",
				        ent[0].split()[2]]
				sha = subprocess.check_output(args)
			elif ent[1].startswith("extra."):
				name = ent[1][6:].replace(": ", "/")
				args = ["git", "cat-file", "blob",
				        ent[0].split()[2]]
				extra[name] = subprocess.check_output(args)
		return Ftree(sha, extra)
	def buildfile(self, nodeid):
		ftree = self.readftree(nodeid)
		args = ["git", "cat-file", "blob", ftree.sha]
		text = subprocess.check_output(args)
		if not (ftree.extra or text.startswith("\1\n")):
			return text
		return "\1\n%s\1\n%s" % (filelog._packmeta(ftree.extra), text)
