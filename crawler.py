#!/usr/bin/python
# -*- coding:UTF-8 -*-

'''
    This script receives a query (string of keywords) and builds a textual 
    corpus for that query, based on the documents retrieved by the 
    keywords from Google search.
'''

import sys
#import re
#import shelve
#import xml.sax
import os
import pdb

from util import read_options, treat_options_simplest, verbose
from googleSearchUniv import GoogleSearchUniv

###############################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s OPTIONS query
    
OPTIONS may be:

-n OR --number
    Number of results used to form the textual base, which is used for the 
    further generation of the language model. Default value is 10.

-l OR --lang
    Language of the result pages. Default value is "en" for English. Use 
    only the 2-letter language code, do not add "lang_" as a prefix. Available
    languages are at this website :
    http://www.google.com/cse/docs/resultsxml.html#languageCollections
    
-p OR --prefix
    Prefix of the files where the corpus pages will be stocked. Default value is
    the current folder ".". If the folder does not exist, it will be created. 
    All the corpus files are organized in a folder named after the language code
    of the retrieved pages. All files are prefixed by the query keywords and the
    position of the page in the result rank.
    
-k OR --key
    The Google University Research Program key. Default value is empty. Although
    this is not a required argument, the program won't work if you do not have
    an account at the research program, run the script from the static IP 
    registered in the program and specifying the related key.
"""
nb_results = 10
prefix = "."
lang = "en"
__counter = 1
key = ""

################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global nb_results 
    global lang
    global prefix
    global key
    for ( o, a ) in opts:
        if o in ("-n", "--number") : 
            try :
                nb_results = int( a )
            except ValueError :
                print >> sys.stderr, "Parameter -n must be integer"
                usage( usage_string )
                sys.exit( -1 )  
        elif o in ("-l", "--lang") :
            lang = a
        elif o in ("-p", "--prefix") :
            prefix = a    
        elif o in ("-k", "--key") :
            key = a
    treat_options_simplest( opts, arg, n_arg, usage_string )
    
################################################################################

def filenamize( url ) :
    """
    """
    filename = url
    filename = filename.replace("/","")
    filename = filename.replace(":","")
    filename = filename.replace("?","")
    filename = filename.replace("&","")
    filename = filename.replace(".","")
    return filename[:120] # Maximal file name size

################################################################################

def writefile( prefix, lang, query, text, metadata, url ) :
    """
    """
    global nb_results
    global __counter
    folder_name = prefix + "/" + lang + "/"
    file_name = "%(u)s.xml" % { "u":filenamize(url) }
    os.system( "mkdir -p " + folder_name )
    text_file = open( folder_name + file_name, "w" )
    __counter = __counter + 1
    #pdb.set_trace()    
    text_file.writelines( [ text ] )
    text_file.close()
    log_file = open( folder_name + "log.txt", "a" )
    log_file.writelines( [ metadata ] )
    log_file.close()
    
################################################################################  
# MAIN SCRIPT

longopts = [ "verbose", "number=", "lang=", "prefix=", "key=" ]
arg = read_options( "vn:l:p:k:", longopts, treat_options, 1, usage_string )

try :    
    query = str( arg[ 0 ] ).strip()
    query_spaces = query.replace( "_"," " )
    gs = GoogleSearchUniv( key )
    pages = gs.get_pages( lang, query_spaces, nb_results ) 
    for page in pages :
        writefile( prefix, lang, query, page.to_html(), page.get_metadata(), page.url )
        
    
      
except IOError, err :  
    print >> sys.stderr, err
    print >> sys.stderr, "Error reading corpus file. Please verify " + \
                         "__common.py configuration"        
    sys.exit( 2 )      
#except Exception, err :
#    print >> sys.stderr, err
#    print >> sys.stderr, "You probably provided an invalid corpus file, " + \
#                         "please validate it against the DTD " + \
#                         "(dtd/mwetoolkit-corpus.dtd)"
