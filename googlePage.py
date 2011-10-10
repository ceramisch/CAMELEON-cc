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
    represented are: language, query, position, title, snippet and text.
"""

################################################################################

class GooglePage() :

################################################################################

    def __init__( self, keywords, position, lang, title, snippet, text ) :
        """
            Instanciates a new GooglePage.
            
            @param keywords The query keywords that originated the search where 
            this page was retrieved.
            
            @param position Index of this page in the result list.
            
            @param lang Language used in the request.
            
            @param title Title of the website.
            
            @param snippet The Google snippet that describes (summarises) the 
            page content. It contains a list of string sentences.
            
            @param text The text extracted from the website. Contains a list of 
            string sentences.
        """
        self.keywords    = keywords
        self.position = position
        self.lang     = lang
        self.title    = title
        self.snippet  = snippet # list of string sentences
        self.text     = text # list of string sentences    
    
################################################################################

    def to_html( self ) :
        """
            Returns a string containing an HTML version of the page.
        """
        page = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        page += "<!DOCTYPE page SYSTEM \"page.dtd\">"
        page += "<page>"
        page += "  <query keywords=\"" + self.keywords + \
                      "\" position=\"" + str( self.position ) + \
                      "\" lang=\""     + self.lang + "\"/>"
        page += "  <title>" + self.title + "</title>"
        page += "  <snippet>"
        for s in self.snippet :
            page += "    <s>" + s.encode("utf-8","ignore") + "</s>"        
        page += "  </snippet>"
        page += "  <text>"
        for s in self.text :
            page += "    <s>" + s + "</s>"
        page += "  </text>"
        page += "</page>"
        return page
