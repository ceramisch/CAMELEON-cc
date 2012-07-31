#!/usr/bin/python

import sys
import os
import re
import pdb

url = sys.argv[1]
MAX_WIDTH = 1024

################################################################################

def download( url ) :
	"""
	"""
	cmd = os.popen( "lynx -nolist -width " + str(MAX_WIDTH) + " -dump %s" % url )
	output = cmd.read()
	cmd.close()
	return output
	
################################################################################

def recreate_paragraphs( text ) :
	"""
	"""
	out_text = ""
	prev_line = ""
	for line in text.split("\n") :
		# Assumes that a word wrapping will never find a word longer than 100 
		# chars long (which might happen, though, if it's an URL)
		if 		re.match( "   [^\* ]", line ) and \
				re.match( "   [^\* ]", prev_line ) and \
				len(prev_line) > MAX_WIDTH - 100 :			
			out_text += " " + line.strip()
		else :
			out_text += "\n" + line
		prev_line = line			
		
	return out_text

################################################################################

def clean( text ) :
	"""
	"""
	clean_text = recreate_paragraphs( text )
	clean_text = re.sub( "_*","", clean_text )
	out_text = ""
	for line in clean_text.split( "\n" ) :
		if re.match( "^[^ ]", line ) :
			out_text += "<s source=\"h\">" + line.strip() + "</s>\n"
		elif re.match( "^ *[\*\+] ", line ) :
			out_text += "<s source=\"li\">" + line.strip()[2:] + "</s>\n"
		elif re.match( "^ *[0-9]+\. ", line ) :
			out_text += "<s source=\"li\">" + line[line.find(".")+2:].strip() + "</s>\n"
		elif re.match( "^   [^\*\+]", line ) :
			out_text += "<s source=\"p\">" + line.strip() + "</s>\n"
		elif len( line ) > 0 :
			print "\n\n\n" + line + "\n\n\n"

	#clean_text = re.sub( "\n   ", " ", clean_text )
	return out_text
	
text = download( url )
print clean( text )



