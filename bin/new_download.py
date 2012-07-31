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

def strip_xml( the_string ) :
    """
    """
    cleanContent = the_string
    cleanContent = cleanContent.replace( "&", "&amp;" ) # Escape sequence
    cleanContent = cleanContent.replace( "<", "&lt;" ) # Escape sequence
    cleanContent = cleanContent.replace( ">", "&gt;" ) # Escape sequence
    cleanContent = cleanContent.replace( "\"", "&quot;" ) # Escape sequence
    #cleanContent = cleanContent.replace( "*", "&lowast;" ) # Escape WILDCARD (TODO: better generic handling of WILDCARD, since it might be changed in config file)
    return cleanContent
	
################################################################################

def clean( text ) :
	"""
	"""
	clean_text = recreate_paragraphs( text )
	clean_text = re.sub( "_+","", clean_text )
	out_text = ""
	for line in clean_text.split( "\n" ) :
		line = re.sub( "\[.*\] *", "", line )
		line = strip_xml( line )
		if re.match( "^ *#", line ) :
			continue
		if re.match( "^[^ ]", line ) :
			out_text += "<s source=\"h\">" + line.strip() + "</s>\n"
		elif re.match( "^ *[\*\+] ", line ) :
			nobullet = line.strip()[2:]
			out_text += "<s source=\"li\">" + re.sub( "^ *[0-9\.]+ ", "", nobullet ) + "</s>\n"
		elif re.match( "^ *[0-9]+\. ", line ) :
			out_text += "<s source=\"li\">" + re.sub( "^ *[0-9\.]+ ", "", line ) + "</s>\n"
		elif re.match( "^   [^\*\+]", line ) and len(line.strip()) > 0 :
			out_text += "<s source=\"p\">" + line.strip() + "</s>\n"
		elif len( line.strip() ) > 0 :
			print "\n\n\n" + line + "\n\n\n"
	#clean_text = re.sub( "\n   ", " ", clean_text )	
	return out_text
	
text = download( url )
print clean( text )



