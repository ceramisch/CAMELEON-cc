#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# googleFreq.py is part of mwetoolkit
#
# mwetoolkit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mwetoolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mwetoolkit.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
    This module provides the `GoogleFreq` class. This class represents an 
    abstract gateway that allows you to access the Google search index and look 
    up for the number of Web pages that contain a certain word or ngram.
"""

import pdb
import urllib
import simplejson

from __common import GOOGLE_CACHE_FILENAME
from webFreq import WebFreq

################################################################################         

class GoogleFreq( WebFreq ) :
    """
        The `GoogleFreq` class is an abstraction that allows you to call Google
        Web Service search to estimate the frequency of a certain search term
        in the Web, in terms of pages that contain that term (a term not in the
        sense of Terminology, but in the sense of word or ngram, i.e. an 
        Information Retrieval term). After instanciated, you should call the
        `search_frequency` function to obtain these estimators for a given
        term.
    """

################################################################################          

    def __init__( self, cache_filename=None ) :
        """
            Instanciates a connection to the Google Web Search service. This
            object is a gate through which you can estimate the number of time
            a given element (word or ngram) appears in the Web. A cache 
            mechanism does automatically manage repeated queries.
            
            @param cache_file The string corresonding to the name of the cache 
            file in/from which you would like to store/retrieve recent queries. 
            If you do not provide a file name, it will be automatically chosen 
            by the class (google_cache.dat or something like this). You should 
            have write permission in the current directory in order to create
            and update the cache file.
            
            @return A new instance of the `GoogleFreq` service abstraction.
        """
  
        #### CACHE MECHANISM ####
        url = ('http://ajax.googleapis.com/ajax/services/search/web?' +\
                        urllib.urlencode({"rsz": "small", "v": "1.0",
                                          "q": "QUERYPLACEHOLDER",
                                          "lr": "LANGPLACEHOLDER",
                                          "hl": "LANGPLACEHOLDER" } ) )
        post_data = {'Referer': 'sourceforge.net/projects/mwetoolkit'}
        if not cache_filename :
            cache_filename = GOOGLE_CACHE_FILENAME
        super( GoogleFreq, self ).__init__( cache_filename, url, post_data, self.treat_result )
            
################################################################################           

    def treat_result( self, response_string ) :
        """
            
        """                
        results = simplejson.loads( response_string, encoding="UTF-8" )        
        if results[ "responseData" ] :
            if results[ "responseData" ][ "results" ] :
                return int( results[ "responseData" ][ "cursor" ] \
                                   [ "estimatedResultCount" ] )
            else :
                return 0
        else :
            return None       
            
################################################################################                   
    
    def corpus_size( self ) :
        """
            Returns the approximate size of the World Wide Web in number of 
            pages. This estimation considers data available from 
            www.worldwidewebsize.com. It was of ~14 billion pages at Jan. 20, 
            2010
            
            @return An integer corresponding to an estimation of the number of
            pages in the World Wide Web.
        """
        return 14000000000 # AROUND 14 BILLION PAGES 20/Jan/2010
             
################################################################################
 


