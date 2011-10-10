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
#import os
#import tempfile
import pdb

#from util import usage, read_options, treat_options_simplest, verbose
from googleSearchUniv import GoogleSearchUniv

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s OPTIONS query
    
OPTIONS may be:

-n <results> OR --number <results>
    Number of results used to form the textual base, which is used for the 
    further generation of the language model. Default value is 10.

-l <code> OR --lang <code>
    Language of the result pages. Default value is "en" for English. Use 
    2-letter language codes.
-p <name> OR --prefix <name>
    Prefix of the files where the corpus pages will be stocked. Default value is
    "corpus/page"
"""
nb_results = 10
prefix = "corpus/page"
lang = "en"
__counter = 1

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
    treat_options_simplest( opts, arg, n_arg, usage_string )
    
################################################################################

def writefile( prefix, lang, text ) :
    """
    """
    global nb_results
    global __counter
    text_file = open( prefix + "_" + lang + "_" + str( __counter ) + ".xml" )
    __counter = __counter + 1
    #pdb.set_trace()    
    ok = False
    while not ok :    
        try :
            text_str = text.encode('utf-8', 'ignore')
            ok = True
        except Exception, e :
            #print >> sys.stderr, "ERROR IN ENCODING"
            text = text[:e[2]] + text[e[2]+2:]    
    text_file.writelines( text_str )
    text_file.close()
    
################################################################################  
# MAIN SCRIPT

longopts = [ "verbose", "number=", "lang=" ]
arg = read_options( "vn:l:", longopts, treat_options, 1, usage_string )

try :    
    query = str( arg[ 0 ] ).strip()
    query_spaces = query.replace( "_"," " )
    gs = GoogleSearchUniv()
    pages = gs.get_pages( lang, query_spaces, nb_results )
    for page in pages :
        writefile( prefix, lang, page.to_html() )
        
    
      
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
