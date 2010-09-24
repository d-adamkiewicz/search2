#!/usr/bin/python
'''
v.09, status: alpha - USE IT AT YOUR OWN RISK!!! 
IT COULD POTENTIALLY CAUSE DAMAGE OR DATA LOSS
'''

import os, sys, getopt, fnmatch, shutil

def usage():
	print(
	"usage:",
	" search2 --move --search-dir=c:\\tym --dest-dir=f:\\tymczas --pattern=*.odt",
	"or",
	" search2.py -p*.odt -sc:\\tym -de:\\tu -c",
	"options:",
	" -s [or --search-dir=]",
	" -d [or --dest-folder=]",
	" -p [or --pattern=]",
	" -c [or --copy] OR -m [or --move] OR -n [or --scan or none of]",
	" -o [or --output=] OR if not specified output file is 'output.txt'",
	"notes:",
	" output file contains list of full pathnames that matches the pattern",
	" 'error.log' file contains list of non-critical errors that occured during scan",
	" when -d script creates output file (and 'error.log') in specified directory",
	sep="\n")
	
def failsafe_makedirs(dir):
	try: 
		os.makedirs(dir)
	except: 
		return False
	else: 
		return True

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
	try:
		opts, args = getopt.getopt(sys.argv[1:], "s:d:p:cmno:h", ["search-dir=","dest-dir=","pattern=","copy","move","scan","output=","help"])
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(2)
	
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-s", "--search-dir"):
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
	'''
	when -d	then output file
	is located inside --dest_dir
	'''
	if dest_dir != '':
			output = dest_dir + '/' + output
			errlog = dest_dir + '/' + errlog
			
	try:
		out = open(output, 'a+')
	except IOError as err:
		print(err)
		sys.exit(2)
		
	try:
		log = open(errlog, 'a+')
	except IOError as err:
		print(err)
		sys.exit(2)
		
	fullpath = ''
	for root, dirs, files in os.walk(search_dir):
		for file in fnmatch.filter(files, pattern):
			fullpath = os.path.join(root, file)
			if work in ('scan', 'copy', 'move'):
				try: 
					print(fullpath, os.path.getsize(fullpath), sep=';', file=out)
				except: 
					print(ascii(fullpath), os.path.getsize(fullpath), sep=';', file=log)
			
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
	
if __name__ == "__main__":
	main()
