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

from util import usage, read_options, treat_options_simplest, verbose
from googleSearchUniv import GoogleSearch

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s OPTIONS query
    
OPTIONS may be:

-n OR --number
    Number of results used to form the textual base, which is used for the 
    further generation of the language model. Default value is 10.
    
-s OR --snippets
    Use ONLY page snippets provided by Google search interface instead of the
    text from the webpages. This is likely to run much faster than the default
    mode. On the other side, you should increase the amount of results 
    considered (e.g. 50 instead of 5). Default is False, so both snippet and 
    page model will be built.
    
-p OR --pages
    Use ONLY text from the webpages instead of page snippets provided by Google 
    search interface. Default is False, so both snippet and page model will be
    built.

"""
nb_results = 10
snippets_only = False
pages_only = False
prefix = "pages"

################################################################################  

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global nb_results
    global snippets_only
    global pages_only
    for ( o, a ) in opts:
        if o in ("-n", "--number") : 
            try :
                nb_results = int( a )
            except ValueError :
                print >> sys.stderr, "Parameter -n must be integer"
                usage( usage_string )
                sys.exit( -1 )
        if o in ( "-s", "--snippets" ) :
            snippets_only = True
        if o in ( "-p", "--pages" ) :
            pages_only = True
            
            
    treat_options_simplest( opts, arg, n_arg, usage_string )
    
################################################################################

def writefile( prefix, query, text ) :
    """
    """
    global nb_results
    text_file = open( "tmp/" + prefix + "_" + str( nb_results ) + "_" + query + ".tmp", "w" )
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

longopts = [ "verbose", "number=", "snippets", "pages" ]
arg = read_options( "vn:sp", longopts, treat_options, 1, usage_string )

try :    
    query = str( arg[ 0 ] ).strip()
    query_spaces = query.replace( "_"," " )
    # print "Query: >>>>> " + query
    gs = GoogleSearch()
    if snippets_only :
        text_snippets = gs.get_snippets( "en", query_spaces, nb_results )
    elif pages_only :
        text_pages = gs.get_pages( "en", query_spaces, nb_results )    
    else :
        (text_snippets, text_pages) = gs.get_snippets_pages( "en", query_spaces, nb_results )
        
    if text_snippets :
        writefile( "snippets", query, text_snippets )
    if text_pages :
        writefile( "pages", query, text_pages )
      
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
