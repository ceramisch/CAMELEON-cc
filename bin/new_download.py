#!/usr/bin/python

import sys
import re
import pdb
import subprocess
import threading
import random
import time
import Queue
import urllib2
import datetime
import chardet

################################################################################
# CONSTANTS
################################################################################

XML_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE page SYSTEM "page.dtd">
<page>
  <lang>%(lang)s</lang>
  <url>%(url)s</url>
  <title>%(title)s</title>
  <encoding>%(encoding)s</encoding>
  <encodingsource>%(encoding_source)s</encodingsource>    
  <snippet>
  </snippet>
  <text>"""
XML_FOOTER = """
  </text>
</page>"""
MAX_WIDTH = 1024
NUMBER_OF_THREADS = 50
TIMEOUT = 60 # seconds, for downloading a page
PREFIX = "raw/new2_%(lang)s/"
SEP = "\t" # LOG FILE CSV SEPARATOR
HTTP_CODES = { 0: "SUCCESS", 
			 404: "ERR-NOTFOUND", 
			 403: "ERR-FORBIDDEN", 
			-999: "ERR-READERROR", 
			 400: "ERR-BADREQUEST", 
			 500: "ERR-INTERNALSERVER", 
			 503: "ERR-UNAVAILABLE", 
			 504: "ERR-GATEWAYTIMEOUT" }
WGET_CODES = { 0: "SUCCESS",
			   1: "ERR-GENERIC",			 
			   2: "ERR-PARSE",
			   3: "ERR-IO",
			   4: "ERR-NETWORK",
			   5: "ERR-SSL",
			   6: "ERR-AUTH",
			   7: "ERR-PROTOCOL",
   			   8: "ERR-SERVER" }
#0   No problems occurred.
#1   Generic error code.
#2   Parse error---for instance, when parsing command-line options, the
#    .wgetrc or .netrc...
#3   File I/O error.
#4   Network failure.
#5   SSL verification failure.
#6   Username/password authentication failure.
#7   Protocol errors.
#8   Server issued an error response.			 

################################################################################

class CleanThread( threading.Thread ) :
	"""
		This daemon thread receives an HTML file and cleans it, writing it to a
		file and then logging the action to the log file
	"""
	
################################################################################
	
	def __init__( self, clean_queue, log_file, lang ) :
		"""
			Override constructor so that the object has access to the pages
			queue
		"""
		threading.Thread.__init__( self )
		self.clean_queue = clean_queue
		self.log_file = log_file # Writable open file descriptor
		self.lang = lang		
		
################################################################################
		
	def run( self ) :
		"""
			Override thread run function. This is where the actual code of the
			thread runs. It's a daemon thread, so it will run "forever" until
			the main program ends. THis thread must be unique running. We could
			model it as part of the main program, but since it is called from 
			the other threads it's easier to model it as a parallel single 
			thread
		"""
		while True :
			#grabs downloaded page from queue
			( url, source_text, exit_status, encoding, enc_source ) = self.clean_queue.get()
			
			if exit_status == 0 :		
				( page_title, page_text ) = self.clean_page( source_text, encoding )
				self.write_output( url, page_title, page_text, encoding, enc_source )					
				print >> sys.stderr, "Saved " + url
			else :	
				print >> sys.stderr, "Error" + str( exit_status ) + " " + url
				
			#write log message to file
			log_file.write( self.log_message( url, exit_status ) )
			#signals to queue job is done
			self.clean_queue.task_done()

################################################################################

	def clean_page( self, source_text, encoding ) :
		"""
			XXX
			
			http://ascomtaguatinga.wordpress.com/
			http://bvsms.saude.gov.br/bvs/publicacoes/IV_CONFERENCIA_CIDADE_GRUPO-SAUDE.htm			
		
			@result A tuple (title, output) containing two strings, the first is
			shorter and contains the content of the page <title> head. The 
			second is a long string with line breaks containing the clean text
			extracted from the HTML.
		"""
		global MAX_WIDTH
		#pdb.set_trace()
		CMD_CONVERT = "lynx -force_html -nolist -width %(w)d -dump -stdin \
			                -display_charset UTF-8 -assume_local_charset %(c)s"\
			                % { "w": MAX_WIDTH, "c" : encoding }
		html2txt = subprocess.Popen( CMD_CONVERT, shell=True, \
						             stdout=subprocess.PIPE, \
						             stdin=subprocess.PIPE )
		(output, error) = html2txt.communicate( source_text )
		source_text = source_text.replace( "\r", "\n" )
		title = re.search( "<title>[^<]*</title>", \
						   source_text.replace("\n"," "), \
						   flags=re.IGNORECASE )
		if title :
			title = re.sub( "<[^>]*>", "", title.group() ).strip()
			title = ""		
		else :
			title = ""
		return ( title, output )

################################################################################

	def log_message( self, url, exit_status ) :
		"""
			Create log message and send to logging thread
		"""
		global SEP
		global WGET_CODES
		global HTTP_CODES		
		timestamp = str( datetime.datetime.now() )		
		exit_msg = HTTP_CODES.get( exit_status, "UNKNOWN-" + str(exit_status) )
		return url + SEP + exit_msg + SEP + timestamp + SEP + self.lang + "\n"

################################################################################

	def write_output( self, url, page_title, page_text, encoding, enc_source ) :
		"""
			Writes the contents of a downloaded and cleaned page into a XML file
			
			@param url The complete URL of the page
			@param page_title The content of <title> head as given by `download`
			@param page_text The HTML-extracted page text as given by `download`
		"""
		global XML_HEADER
		global XML_FOOTER
		global PREFIX
		filename = self.filenamize( url )
		fileout = open( PREFIX + filename + ".xml", "w" )
		fileout.write( XML_HEADER % { "lang" : self.lang, \
		                              "url" : url, \
		                              "title" : page_title, \
		                              "encoding" : encoding, \
		                              "encoding_source" : enc_source } )
		text = self.clean_lynx( page_text )		                           
		fileout.write( text )
		fileout.write( XML_FOOTER )
		fileout.close()

################################################################################

	def filenamize( self, url ) :
		"""
			Remove special characters from URL and trim the name
		"""
		#rand_factor = str( random.randint(10000,99999) )
		rand_factor = str(10000) # JUST FOR TESTING
		# Maximal filename size is 120, so we get 115 charcters from the 
		# beginning of the URL (modulo special characters) and concatenate a
		# random 5-digit integer, thus reducing the probability of collisions 
		# for two websites whose URL shares the first 115 characters.
		return url.replace("/","").replace(":","").replace("?","")\
				  .replace("&","").replace(".","")[:115] + rand_factor

################################################################################

	def recreate_paragraphs( self, text ) :
		"""
			This function simply removes the spacing added by lynx's automatic
			word wrapping (which cannot be turned off by any command line 
			option). This function is not guaranteed to work and should be
			evaluated at some point.
			
			@param text The input text generated by lynx
			@return The same text with paragraphs on a single line (no wrapping)
		"""
		out_text = ""
		prev_line = ""
		started = False
		for line in text.split("\n") :
			# Little workaround to ignore lines starting with # at the beginning
			# of the document. This is how Lynx represents some kinds of <link>
			# elements which have no visible counterpart
			if line.startswith( "   #" ) and not started :
				continue
			elif not started :
				started = True
			# Assumes that word wrapping will never find a word longer than 70 
			# chars (which might happen, though, e.g. if it's an URL)				
			if 		re.match( "   [^\* ]", line ) and \
					re.match( "   [^\* ]", prev_line ) and \
					len(prev_line) > MAX_WIDTH - 70 :			
				out_text += " " + line.strip()
			else :
				out_text += "\n" + line
			prev_line = line			
		return out_text

################################################################################

	def strip_xml( self, the_string ) :
		"""
			Replaces the XML/HTML special characters in the text, escaping them 
			with their corresponding entities. This helps generating well-formed 
			XML in the output, regardless of the text in the website.
			
			@param the_string A text that should be escaped
			
			@return The escaped text with special characters replaces by 
			entities
		"""
		return the_string.replace( "&", "&amp;" ).replace( "<", "&lt;" )\
		                 .replace( ">", "&gt;" ).replace( "\"", "&quot;" )
	
################################################################################

	def clean_lynx( self, text ) :
		"""
			Cleans the format output by lynx in order to obtain a more "NLP-
			friendly" version. This includes removing bulltets and numbers in
			lists, removing word wrap from paragraphs and extra indenting 
			indicating headers. This information is then appended to the string
			in the form of an attribute on the XML element <s>
			
			@param text The text generated by lynx
			@param text The same text in a more NLP-friendly format	
		"""
		# First remove word wrapping from paragraphs
		clean_text = self.recreate_paragraphs( text )
		# Remove text fields and horizontal lines, represented by underscore
		clean_text = re.sub( "_+","", clean_text )
		out_text = ""
		# Process the text line by line
		for line in clean_text.split( "\n" ) :
			line = re.sub( "\[.*\] *", "", line )
			# Escape special XML characters
			line = self.strip_xml( line )
			# Any line with no heading space is a header
			if re.match( "^[^ ]", line ) :
				out_text += "    <s source=\"h\">" + line.strip() + "</s>\n"
			# Any line with a heading special bullet symbol is a list item
			elif re.match( "^ +[\*\+o#@] ", line ) :
				nobullet = line.strip()[2:]
				# Remove additional manual numbering added to the list item
				nobullet = re.sub( "^ *[0-9\.]+ ", "", nobullet )
				out_text += "    <s source=\"li\">" + nobullet + "</s>\n"
			# Any line with heading number followed by dot is numbered list item
			elif re.match( "^ *[0-9]+\. ", line ) :
				nobullet = re.sub( "^ *[0-9\.]+ ", "", line )
				out_text += "    <s source=\"li\">" + nobullet + "</s>\n"
			# Other non-empty indented lines are paragraphs
			elif re.match( "^ +[^ ]", line ) and len(line.strip()) > 0 :
				if not line.strip().startswith( "IFRAME:" ) :
					out_text += "    <s source=\"p\">" + line.strip() + "</s>\n"
			# Other lines are ignored, but for debugging you can uncomment the
			# next two code lines
			#elif len( line.strip() ) > 0 :
			#	print >> sys.stderr, "\n\n\n" + line + "\n\n\n"
		return out_text.strip()

################################################################################
################################################################################

class DownloadThread( threading.Thread ) :
	"""
		This thread is responsible for downloading a give URL, cleaning the text
		and writing the output to a file.
	"""
	
################################################################################	
	
	def __init__( self, url_queue, clean_queue ) :
		"""
			Override constructor so that the object has access to the url queue
		"""
		threading.Thread.__init__( self )
		self.url_queue = url_queue
		self.clean_queue = clean_queue
		
################################################################################
	
	def run( self ) :
		"""
			Override thread run function. This is where the actual code of the
			thread runs. It's a daemon thread, so it will run "forever" until
			the main program ends.
		"""
		while True :
			#grabs URL from queue
			url = self.url_queue.get()
			# Download the page title and text body (not HTML! CLEAN TEXT)
			print >> sys.stderr,  "Downloading " + url
			( source_text, exit_status, encoding, enc_source ) = self.download( url )
			self.clean_queue.put( ( url, source_text, exit_status, encoding, enc_source ) )
			#signals to queue job is done
			self.url_queue.task_done()

################################################################################
		
	def download( self, url ) :
		"""
			Downloads the raw HTML source, then uses the same
			program to extract the text from it. It must be done as a 2-step 
			process otherwise we cannot acceed to the page title information.
			@param url The complete URL of the page to download.
			@result A tuple (title, text) containing two strings, the first is
			shorter and contains the content of the page <title> head. The 
			second is a long string with line breaks containing the clean text
			extracted from the HTML.
		"""
		global TIMEOUT # in seconds
		try :
			enc_source = "http-header"
			encoding = None
			page_descr = urllib2.urlopen( url, timeout=TIMEOUT )
			source_text = page_descr.read()
			exit_status = 0
			# First, tries to get the char encoding from the header
			encoding = page_descr.info().getparam("charset")			
			# Second, if the header is not present, tries to get it from the
			# HTML header
			if encoding is None :
				# starts with meta, has charset, finished with >
				pat = "<meta[^>]*charset=([^ >]*)[^>]*>"
				encoding = re.search( pat, source_text, re.DOTALL)
				if encoding is not None :
					encoding = encoding.group(1).replace( "\"", "" )
					print >> sys.stderr, "   DETECTED " + encoding + " " + url
					enc_source = "html-header"
				#pdb.set_trace()
			# Third, it the HTML header is not present, tries to get it from 
			# automatic detection
			if encoding is None :
				encoding = chardet.detect( source_text )[ 'encoding' ]
				enc_source = "detected"
			# If one of the former succeeded, convert the detected encoding to
			# utf-8
			# if encoding is not None :
			#	unicode_obj = unicode( source_text, encoding, errors="ignore" )
			#	source_text = unicode_obj.encode( 'utf-8' )
			#	exit_status = 0
			# Otherwise ignore the page and return error
			if encoding is None :
				print >> sys.stderr, "Char encoding not detected " + url
				exit_status = -999
				source_text = None
		except urllib2.HTTPError, err :
			exit_status = err.code
			title = source_text = None
		except urllib2.URLError, err :
			exit_status = -999
			source_text = None
		except Exception, e :
			ms = "\n\nUNKNOWN EXCEPTION " + str(type(e)) + " " + str(e) + "\n\n"
			print >> sys.stderr, ms	
			print >> sys.stderr, "Char encoding not detected " + url			
			exit_status = -999
			source_text = None
		return ( source_text, exit_status, encoding, enc_source )
		
		#CMD_WGET = "wget --timeout %(to)d -t 1 -q -O - \"%(url)s\"" % { "to": TIMEOUT, "url": url }
		#download = subprocess.Popen( CMD_WGET, shell=True, \
		#				             stdout=subprocess.PIPE )
		#(source_text, error) = download.communicate()
		#exit_status = download.returncode
		#return ( source_text, exit_status )
	
################################################################################	

def read_log( log_filename ) :
	logfile = open( log_filename )
	urls_to_download = {}
	
	for line in logfile.readlines() :
		line = line.strip() 
		url = line.split(" ")[0]
		count = urls_to_download.get( url, 0 )
		urls_to_download[ url ] = count + 1		
	logfile.close()
	
	return urls_to_download
	
################################################################################		

log_filename = sys.argv[ 1 ]
lang = sys.argv[ 2 ]
PREFIX = PREFIX % { "lang": lang }

urls_to_download = read_log( log_filename )
url_queue = Queue.Queue()
clean_queue = Queue.Queue()

try :
	# Create cleaner thread (1 instance)
	log_file = open( PREFIX + "log.txt", "w" )
	clean_thread = CleanThread( clean_queue, log_file, lang )
	clean_thread.setDaemon( True )
	clean_thread.start()

	# Create download threads (several instances)
	for i in range( NUMBER_OF_THREADS ):
		down_thread = DownloadThread( url_queue, clean_queue )
		down_thread.setDaemon( True )
		down_thread.start()

	started = time.time()
	for url in urls_to_download.keys() :
		url_queue.put( url )
	url_queue.join()
	clean_queue.join()
	elapsed = time.time() - started
	print "Time to download %(nb)d URLs: %(time)d" % { "time": elapsed, \
                                                   "nb": len(urls_to_download) }	
except Exception, err :
	print >> sys.stderr, "FATAL ERROR " + str(err)
	
finally:
	log_file.close()	

################################################################################
# UNUSED
# Remove tables from HTML source, avoiding spurious table lines being 
# considered as paragraphs
# NO. What if the whole website is designed as a table?
#def remove_tables( source_text ) :
#	clean_source_text = ""
#	in_table = False
#	for line in source_text.split( "\n" ) :
#		if not in_table :
#			if line.find( "<table" ) >= 0 :
#				#pdb.set_trace()
#				clean_source_text += line[ :line.find( "<table" ): ] + "\n"
#				in_table = True
#			else :
#				clean_source_text += line + "\n"
#		else :
#			if line.find( "</table>" ) >= 0 :
#				#pdb.set_trace()
#				clean_source_text += line[ line.find( "</table>" ) + 8:] + "\n"
#				in_table = False
#	return clean_source_text
################################################################################

