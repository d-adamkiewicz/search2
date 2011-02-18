#!/usr/bin/python
'''
v.13, status: alpha - USE IT AT YOUR OWN RISK!!! 
IT COULD POTENTIALLY CAUSE DAMAGE OR DATA LOSS
changes:
- '-a' | '--append' option added
- fixing "<driveletter>:"  bug
v.12
changes:
- now it uses modified version of fnmatch.translate function instead of fnmatch module
this allows file multi-patterns i.e. patterns separated by semicolon e.g.
*.zip;*.py
v.11
changes:
- now when in scan mode it creates 'dirinfo.txt' file 
which contains directory paths and summarized size of all files (of given pattern) 
in each of them
'''

import os, sys, getopt, shutil, re

def usage():
	print(
	"usage:",
	" search2 --move --search-dir=c:\\tym --dest-dir=f:\\tymczas --pattern=*.odt",
	"or",
	" search2.py -p*.odt -sc:\\tym -de:\\tu -c",
	"multi-pattern case:",
	" search2.py -p*.odt;*.ods -sc:\\tym -de:\\tu -c",
	"options:",
	" -s [or --search-dir=]",
	" -d [or --dest-folder=]",
	" -p [or --pattern=]",
	" -c [or --copy] OR -m [or --move] OR -n [or --scan or none of]",
	" -o [or --output=] OR if not specified output file is 'output.txt'",
	" -a [or --append]",
	"notes:",
	" when specify whole disk drive use -s\"c:\" not -s\"c:\\\"",
	" - output file (by default 'output.txt') contains list of full pathnames", 
	" that match the pattern",
	" - 'error.log' file contains list of non-critical errors that occured", 
	" during scan",
	" - when '-d' script creates output file (and 'error.log' and/or 'dirinfo.txt')",
	" in specified directory",
	" - when in scan mode ie '-n' [or '--scan' or none] it produces 'dirinfo.txt'",
	" which contains directory paths and summarized size of all files",
	" (of given pattern) in each of them",
	" '--append' option makes data to be appended at the end of existing file(s)",
	" not creating new ones",
	sep="\n")
	
def failsafe_makedirs(dir):
	try: 
		os.makedirs(dir)
	except: 
		return False
	else: 
		return True
		
'''
origin: fnmatch module
'''
def translate(pat):
	"""Translate a shell PATTERN to a regular expression.

	There is no way to quote meta-characters.
	"""

	i, n = 0, len(pat)
	res = ''
	while i < n:
		c = pat[i]
		i = i+1
		if c == '*':
			res = res + '.*'
		elif c == '?':
			res = res + '.'
		elif c == '[':
			j = i
			if j < n and pat[j] == '!':
				j = j+1
			if j < n and pat[j] == ']':
				j = j+1
			while j < n and pat[j] != ']':
				j = j+1
			if j >= n:
				res = res + '\\['
			else:
				stuff = pat[i:j].replace('\\','\\\\')
				i = j+1
				if stuff[0] == '!':
					stuff = '^' + stuff[1:]
				elif stuff[0] == '^':
					stuff = '\\' + stuff
				res = '%s[%s]' % (res, stuff)
		# added
		elif c == ';':
			res = res + '\Z|'
		else:
			res = res + re.escape(c)
	return res + '\Z(?ms)'

def main():
	search_dir = ''
	dest_dir = ''
	pattern = ''
	copy = False
	move = False
	scan = False
	default_output = 'output.txt'
	output = ''
	work = False
	append = False
	try:
		opts, args = getopt.getopt(sys.argv[1:], "s:d:p:cmno:ha", ["search-dir=","dest-dir=","pattern=","copy","move","scan","output=","help","append"])
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(2)
	
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-s", "--search-dir"):
			if a[-1] == ':':
				a = a + '\\'
			search_dir = a
			print(o, a)
		elif o in ("-d", "--dest-dir"):
			dest_dir = a
			print(o, a)
		elif o in ("-p", "--pattern"):
			pattern = a
			print(o, a)
		elif o in ("-c", "--copy"):
			copy = True
			print(o, a)
		elif o in ("-m", "--move"):
			move = True
			print(o, a)
		elif o in ("-n", "--scan"):
			scan = True
			print(o, a)
		elif o in ("-o", "--output"):
			output = a
			print(o, a)
		elif o in ("-a", "--append"):
			append = True
			print(o, a)
	if not move and not copy:
		scan = True
		work = 'scan'
	elif move and copy:
		sys.exit("you provided both --copy and --move paramters!, quit")
	elif move:
		work = 'move'
	elif copy:
		work = 'copy'
	if pattern == '':
		sys.exit("you didn't provide -p or --pattern parameter, use --help for help")
	if work in ('scan', 'move', 'copy'):
		if search_dir == '':
			sys.exit("you should have provided -s or --search-dir parameter!")
		elif not os.path.isdir(search_dir):
			sys.exit("--search-dir parameter '" + search_dir +"' you provided is not valid path!")
	if work in ('move', 'copy'):
		if dest_dir == '':
			sys.exit("you should have provided -d or --dest-dir parameter!")
		elif not os.path.isdir(dest_dir):
			if not failsafe_makedirs(dest_dir):
				sys.exit("1: error creating dir: " + dest_dir)
	if work == 'scan' and dest_dir != '':
		if not os.path.isdir(dest_dir):
			if not failsafe_makedirs(dest_dir):
				sys.exit("1: error creating dir: " + dest_dir)
	'''
	when -o is not specified then default_output ('output.txt')
	'''
	output = output or default_output
	errlog = 'error.log'
	dirinfo = ''
	if work == 'scan':
		dirinfo = 'dirinfo.txt'
		
	'''
	when -d	then output file
	is located inside --dest_dir
	'''
	if dest_dir != '':
			output = dest_dir + '/' + output
			errlog = dest_dir + '/' + errlog
			if dirinfo:
				dirinfo = dest_dir + '/' + dirinfo
			
	try:
		out = open(output, 'a' if append else 'w')
	except IOError as err:
		print(err)
		sys.exit(2)
		
	try:
		log = open(errlog, 'a' if append else 'w')
	except IOError as err:
		print(err)
		sys.exit(2)
		
	if dirinfo:
		try: 
			idir = open(dirinfo, 'a' if append else 'w')
		except IOError as err:
			print(err)
			sys.exit(2)
		
	fullpath = ''
	stores = {}
	pattern = translate(pattern)
	print(pattern)
	regex = re.compile(pattern)
	for root, dirs, files in os.walk(search_dir):
		for file in files:
			if regex.match(file):
				fullpath = os.path.join(root, file)
				size = os.path.getsize(fullpath)
				if work in ('scan', 'copy', 'move'):
					try: 
						print(fullpath, size, sep=';', file=out)
					except: 
						print(ascii(fullpath), size, sep=';', file=log)
				
				if work in ('copy', 'move'):
					extpath = os.path.splitdrive(fullpath)[1]
					head = os.path.split(extpath)[0]
					if not os.path.isdir(dest_dir + '/' + head):
						if not failsafe_makedirs(dest_dir + '/' + head):
							sys.exit("2: error creating dir: " + dest_dir + '/' + head)
					if work == 'copy':
						try:
							shutil.copy(fullpath, dest_dir + '/' + extpath)
						except WindowsError:
							print(fullpath, "- can't copy file!!!", sep=';', file=log)
					elif work == 'move':
						try: 
							shutil.move(fullpath, dest_dir + '/' + extpath)
						except WindowsError:
							print(fullpath, "- can't move file!!!", sep=';', file=log)
				
				if work == 'scan':
					try:
						stores[root] += size
					except KeyError:
						stores[root] = size
				
	if work == 'scan':
		for k in stores.keys():
			print(k, stores[k], sep=';', file=idir)
		
			
	
if __name__ == "__main__":
	main()
