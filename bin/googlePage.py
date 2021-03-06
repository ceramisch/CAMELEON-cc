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
    This module provides the `GooglePage` class. This class represents an 
    abstract web page downloaded by the GoogleSearchUniv class. The attributes 
    represented are: keywords, position, language, date, url, title, snippet,
    text and total results.
"""

import pdb

################################################################################

class GooglePage() :

################################################################################

    def __init__( self, keywords, pos1, pos2, lang, date, url, title, snippet, \
                  text, total ) :
        """
            Instanciates a new GooglePage.
            
            @param keywords The query keywords that originated the search where 
            this page was retrieved.
            
            @param pos1 Index of this page in the resulting output.
            
            @param pos2 Index of this page in Google ranking.
            
            @param lang Language used in the request.
            
            @param date The date in which the website was retrieved.
            
            @param url The address of the website.            
            
            @param title Title of the website.
            
            @param snippet The Google snippet that describes (summarises) the 
            page content. It contains a list of string sentences.
            
            @param text The text extracted from the website. Contains a list of 
            string sentences.

            @param total The approximate total number of resutls returned by
            Google for this query.
        """
        self.keywords = keywords
        self.pos1     = pos1
        self.pos2     = pos2
        self.lang     = lang
        self.date     = date
        self.url      = url
        self.title    = title
        self.snippet  = snippet # list of string sentences
        self.text     = text # list of string sentences    
        self.total    = total
    
################################################################################

    def to_html( self ) :
        """
            Returns a string containing an HTML version of the page.
        """
        #print type(self.url)
        #print type(self.title)
        #print type(self.snippet[0])
        #print type(self.text[0])
        page = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        page += "<!DOCTYPE page SYSTEM \"page.dtd\">\n"
        page += "<page>\n"
        #page += "  <query keywords=\"" + self.keywords + \
        #              "\" position=\"" + str( self.position ) + \
        #              "\" lang=\""     + self.lang + \
        #              "\" date=\""     + self.date + "\"/>\n"
        page += "  <lang>" + self.lang + "</lang>\n"
        page += "  <url>" + self.url.encode('utf-8') + "</url>\n"
        page += "  <title>" + self.title.encode('utf-8') + "</title>\n"
        page += "  <snippet>\n"
        for s in self.snippet :
            #try :
            page += "    <s>" + s.encode('utf-8','ignore') + "</s>\n"        
            #except UnicodeError, e :
            #    pdb.set_trace()
            #    print e
        page += "  </snippet>\n"
        page += "  <text>\n"
        for s in self.text :
            page += "    <s>" + s.encode('utf-8','ignore') + "</s>\n"
        page += "  </text>\n"
        page += "</page>\n"

        return page
        
################################################################################

    def get_metadata( self ) :
        """
            Returns a string containing metadata about how this page was 
            retrieved. The information is in the following format:
            url date keywords position lang total

            url: The URL address of the page retrieved and downloaded
            date: The date when this page was retrieved and downloaded
            keywords: The keywords of the query sent to Google
            pos1: The position in which this page appears in result list
            pos2: The position in which this page was retrieved in Google
            lang: The language used as filter in Google request
            total: The approximate number of results returned by Google query
            
            @return A line containing the fields described above separated by
            spaces and terminated by carriage return
        """

        
        return self.url.encode( 'utf-8' ) + " " + self.date + " " + \
               self.keywords.replace( " ", "_" ) + " " + \
               str( self.pos1 ) + " " + str( self.pos2 ) + " " + \
               self.lang + " " + str( self.total ) + "\n"
