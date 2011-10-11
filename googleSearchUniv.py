#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2011 Carlos Ramisch
#
# CAMELEON-cc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CAMELEON-cc is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mwetoolkit.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
    This module provides the `GoogleFreqUniv` class. This class represents an 
    abstract gateway that allows you to access the Google search index and look 
    up for the number of Web pages that contain a certain word or ngram.
"""

import pdb
import urllib2
import urllib
import re
import html2text
import sys
import xml.dom.minidom
import datetime

from googlePage import GooglePage
from util import verbose

################################################################################         

class GoogleSearchUniv() :
    """
        The `GoogleFreqUniv` class is an abstraction that allows you to call 
        Google Web Service search to estimate the frequency of a certain search 
        term in the Web, in terms of pages that contain that term (a term not in 
        the sense of Terminology, but in the sense of word or ngram, i.e. an 
        Information Retrieval term). After instanciated, you should call the
        `search_frequency` function to obtain these estimators for a given
        term. 
        
        This class only works with a valid registered Google Research University
        Program ID and when the script is called from the computer whose IP 
        address is assigned to the ID. If you do not have this ID, use regular
        Google search class `GoogleFreq` bounded by a daily usage quota.
    """

################################################################################          

    def __init__( self, google_id ) :
        """
            Instanciates a connection to the Google Web Search service. This
            object is a gate through which you can estimate the number of time
            a given element (word or ngram) appears in the Web. 
            
            @param google_id This is the ID you receive from Google when you 
            register to the Google Search University Research Program. More
            information about it can be found at :
            http://research.google.com/university/search/
            Please remind that the ID only works with the registered IP address.
            
            @return A new instance of the `GoogleSearchUniv` service abstraction
        """ 
        self.url = ('https://research.google.com/university/search/service?' +\
                        urllib.urlencode({"rsz"     : "large",
                                          "q"       : "QUERYPLACEHOLDER",
                                          "lr"      : "LANGPLACEHOLDER",
                                          "start"   : "0",
                                          "clid"    : google_id ,
                                          "snippets": "true" } ) )
        self.post_data = {'Referer': 'https://github.com/ceramisch/CAMELEON-cc'}
        self.MIN_WORDS = 1
            
################################################################################  

    def get_field( self, element, name ) :
        """
            Blah
        """
        nodelist = element.getElementsByTagName( name )[ 0 ].childNodes
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

################################################################################  

    def get_pages( self, lang, search_term, nb_results ):
        """
        """
        pages = []
        result_count = 0 # Counts only pages that go to the final results
        page_count = 0 # Counts all pages processed, despite of ignored
        result_xml = self.send_query( lang, search_term )        
        result_dom = xml.dom.minidom.parseString( result_xml )
        while result_count < nb_results :
            try :
                for r in result_dom.getElementsByTagName( 'RES' )[ 0 ].getElementsByTagName( 'R' ) :
                    if result_count < nb_results :
                        url = self.get_field( r, "U" )
                        title = self.get_field( r, "TNB" )
                        date = str( datetime.date.today() )
                        snippet = self.split_sentences( self.clean( self.get_field( r, "SNB" ) ) )
                        text = self.split_sentences( self.clean( self.get_text_from_html( self.get_field( r, "U" ) ) ) )
                        if len(text) > 1 :
                            page = GooglePage( search_term, result_count, lang, \
                                               date, url, title, snippet, text )                                           
                            pages.append( page )
                            verbose( "Downloaded page number " + str( result_count ) )
                            result_count = result_count + 1
                        page_count = page_count + 1
                    else :
                        break
            except TypeError, e :
                pdb.set_trace()
                print e
            if result_count < nb_results :
                result_xml = self.send_query( lang, search_term, page_count )        
                result_dom = xml.dom.minidom.parseString( result_xml )
        return pages
        
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
            page_text = re.sub( '\&', '&amp;', page_text )
            page_text = re.sub( '<', '&lt;', page_text )
            page_text = re.sub( '>', '&gt;', page_text )
            page_text = re.sub( '"', '&quot;', page_text )
            page_text = re.sub( '_', ' ', page_text )
            for line in page_text.split( "\n" ) :
                line = line.strip()
                if len( line.split( " " ) ) > self.MIN_WORDS :
                    text = text + line + "\n"
        except Exception, e :
            print >> sys.stderr, "Warning, URL " + url + " ignored"
            print >> sys.stderr, e
        return text

################################################################################    

    def clean( self, text ) :
        """
        """
        clean_text = text
        clean_text = clean_text.replace( "...", " " )
        clean_text = re.sub( "</?b>", "", clean_text )
        clean_text = re.sub( "\&[^;];", " ", clean_text )
        clean_text = re.sub( "  *", " ", clean_text )        
        ok = False
        while not ok :    
            try :
                out_text = clean_text.encode('utf-8', 'ignore')
                ok = True
            except Exception, e :
                #print >> sys.stderr, "ERROR IN ENCODING"
                clean_text = clean_text[:e[2]] + clean_text[e[2]+2:]    
        return out_text

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
            return response.read()
        except urllib2.HTTPError, e:
            print >> sys.stderr, "Error processing query \"" + search_term + "\"\n" + url
            return None

################################################################################  

    def split_sentences( self, text ) :
        """
            Given an input text, returns a list of strings containing the 
            sentences of the original text separated, one string per sentence.
            
            TODO: Implement a real sentence splitter
        """
        return text.split( "\n" )
        
################################################################################        
