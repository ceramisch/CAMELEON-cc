#!/usr/bin/python
# -*- coding:UTF-8 -*-

"""
    This class represents an abstract gateway that allows you to access the 
    Google search index and get either snippets or URLs for the result pages.
"""

import pdb
import urllib2
import urllib
import simplejson
import re
import html2text
import sys

################################################################################         

class GoogleSearch() :
    """
        The `GoogleSearch` class is an abstraction that allows you to call 
        Google Web Service search to retrieve text snippets or URLs for a given
        query
    """

################################################################################          

    def __init__( self ) :
        """
            Instanciates a connection to the Google Web Search service. 
                       
            @return A new instance of the `GoogleSearch` service abstraction.
        """
  

  
        url = ('https://www.googleapis.com/customsearch/v1?' +\
                        urllib.urlencode({"num": "10", 
                                          "key": "AIzaSyBTwv6_ewQtzkG5ojM6kh9lruHDwF6WR44",
                                          "q": "QUERYPLACEHOLDER",
                                          "lr": "lang_LANGPLACEHOLDER",
                                          "cx": "013036536707430787589:_pqjad5hr1a",
                                          "start" : "STARTPLACEHOLDER" } ) )                                          
                                          
        post_data = {'Referer': 'sourceforge.net/projects/mwetoolkit'}
        self.url = url
        self.post_data = post_data
        self.MIN_WORDS = 2 # Minimum number of words for a line
                        
################################################################################  

    def clean( self, text ) :
        """
        """
        clean_text = text
        clean_text = clean_text.replace( "...", " " )
        clean_text = re.sub( "</?b>", "", clean_text )
        clean_text = re.sub( "\&[^;];", " ", clean_text )
        clean_text = re.sub( "  *", " ", clean_text )
        return clean_text

################################################################################  

    def send_query( self, lang, search_term, start=0 ) :
        """
        """
        #pdb.set_trace()
        url = self.url.replace( "LANGPLACEHOLDER",lang )
        url = url.replace( "QUERYPLACEHOLDER", urllib.quote_plus( search_term ))
        url = url.replace( "STARTPLACEHOLDER", str( start + 1 ) )
        request = urllib2.Request( url, None, self.post_data )
        try :
            response = urllib2.urlopen( request )
        except urllib2.HTTPError, e:
            pass
        response_string = response.read()
        results = simplejson.loads( response_string, encoding="UTF-8" )
        return results

################################################################################  

    def get_snippets( self, lang, search_term, nb_results ):
        """
        """
        result_count = 0
        results = self.send_query( lang, search_term )        
        text = ""
        while result_count < nb_results :
            try :
                for r in results[ "items" ] :
                    if result_count < nb_results :
                        text = text + "<s> " + r[ 'title' ] + " </s>\n"
                        text = text + "<s> " + r[ 'snippet' ] + " </s>\n"                                               
                        result_count = result_count + 1
                    else :
                        break
            except TypeError :
                pdb.set_trace()
            if result_count < nb_results :
                results = self.send_query( lang, search_term, start=result_count )        
        return self.clean( text )

################################################################################  

    def get_snippets_pages( self, lang, search_term, nb_results ):
        """
        """
        result_count = 0
        results = self.send_query( lang, search_term )        
        text = ""
        text_page = ""
        while result_count < nb_results :
            try :
                for r in results[ "items" ] :
                    if result_count < nb_results :
                        text = text + "<s> " + r[ 'title' ] + " </s>\n"
                        text = text + "<s> " + r[ 'snippet' ] + " </s>\n"                        
                        text_page = text_page + self.get_text_from_html( r[ "link" ] )
                        result_count = result_count + 1
                    else :
                        break
            except TypeError :
                pdb.set_trace()
            if result_count < nb_results :
                results = self.send_query( lang, search_term, start=result_count )        
        return self.clean( text ), self.clean( text_page )
        
################################################################################          

    def get_text_from_html( self, url ) :
        """
        """
        try :
            text = ""
            page_text = html2text.html2text_all( url )
            page_text = re.sub( ' *\[[0-9]*\]:.*', '', page_text )
            page_text = re.sub( '\[[0-9]*\]', '', page_text )
            page_text = re.sub( '\[([^\]]*)\]','\\1',page_text )
            page_text = re.sub( '\*\*([^\*]*)\*\*',"\\1", page_text)
            page_text = re.sub( ' *\* ','',page_text)
            page_text = re.sub( ' *! ','',page_text)            
            page_text = re.sub( '#*','',page_text)                  
            page_text = re.sub( '!\[[^\]]\]', '', page_text )
            page_text = re.sub( '!\[[^\]]*\]', '', page_text )
            page_text = re.sub( '_', ' ', page_text )            
            for line in page_text.split( "\n" ) :
                line = line.strip()
                if len( line.split( " " ) ) > self.MIN_WORDS :
                    text = text + "<s> " + line + " </s>\n"
        except Exception, e :
            print >> sys.stderr, "Warning, URL " + url + " ignored"
            print >> sys.stderr, e
        return text

################################################################################          
        
    def get_pages( self, lang, search_term, nb_results ):
        """
        """
        result_count = 0
        results = self.send_query( lang, search_term )        
        text = ""
        pdb.set_trace()
        while result_count < nb_results :
            for r in results[ "items" ] :
                if result_count < nb_results :
                    text = text + self.get_text_from_html( r[ "link" ] )
                    result_count = result_count + 1                        
                else :
                    break
            #pdb.set_trace()
            if result_count < nb_results :
                results = self.send_query( lang, search_term, start=result_count )        
        return self.clean( text )        
        
