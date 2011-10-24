#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
    Set of utility functions that are common to several scripts.
"""

import getopt
import sys

################################################################################

verbose_on = False

################################################################################

def set_verbose( value ) :
    """
    """
    global verbose_on
    verbose_on = value

################################################################################

def verbose( message ) :
    """
    """
    global verbose_on
    if verbose_on :
        print >> sys.stderr, message

################################################################################

def usage( usage_string ) :
    """
        Print detailed instructions about the use of this program. Each script
        that uses this function should provide a variable containing the
        usage string.
    """
    print >> sys.stderr, usage_string % {"program": sys.argv[ 0 ]}
    
################################################################################

def treat_options_simplest( opts, arg, n_arg, usage_string ) :
    """
        Verifies that the number of arguments given to the script is correct.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.
    """
    for ( o, a ) in opts:      
        if o in ("-v", "--verbose") :
            set_verbose( True )
            verbose( "Verbose mode on" )            
    
    if n_arg >= 0 and len( arg ) != n_arg :
        print >> sys.stderr, "You must provide %(n)s arguments to this script" \
                             % { "n" : n_arg }
        usage( usage_string )
        sys.exit( 2 )

################################################################################     

def read_options( shortopts, longopts, treat_options, n_args, usage_string ) :
    """
        Generic function that parses the input options using the getopt module.
        The options are then treated through the `treat_options` callback.
        
        @param shortopts Short options as defined by getopts, i.e. a sequence of
        letters and colons to indicate arguments.
        
        @param longopts Long options as defined by getopts, i.e. a list of 
        strings ending with "=" to indicate arguments.
        
        @param treat_options Callback function, receives a list of strings to
        indicate parsed options, a list of strings to indicate the parsed 
        arguments and an integer that expresses the expected number of arguments
        of this script.
    """
    try:
        opts, arg = getopt.getopt( sys.argv[ 1: ], shortopts, longopts )
    except getopt.GetoptError, err:
        # will print something like "option -a not recognized"
        print >> sys.stderr, str( err ) 
        usage( usage_string )
        sys.exit( -1 )

    treat_options( opts, arg, n_args, usage_string ) 
    return arg
        
################################################################################             

def strip_xml( the_string ) :
    """
    """
    cleanContent = the_string
    cleanContent = cleanContent.replace( "&", "&amp;" ) # Escape sequence
    cleanContent = cleanContent.replace( "<", "&lt;" ) # Escape sequence
    cleanContent = cleanContent.replace( ">", "&gt;" ) # Escape sequence
    cleanContent = cleanContent.replace( "\"", "&quot;" ) # Escape sequence
    cleanContent = cleanContent.replace( "*", "&lowast;" ) # Escape WILDCARD (TODO: better generic handling of WILDCARD, since it might be changed in config file)
    return cleanContent
        
################################################################################
