#!/usr/bin/python
# -*- coding:UTF-8 -*-

import sys
import pdb

# constant_part variable_file lang prefix n

constant_part = sys.argv[1]
variable_file = open( sys.argv[ 2 ], "r" )
lang = sys.argv[ 3 ]
prefix = sys.argv[ 4 ]
n = sys.argv[ 5 ]
variables = []
combinations = []

#pdb.set_trace()

for line in variable_file.readlines() :
    variables.append( line.strip() )
    
for v1 in variables :
    for v2 in variables :
        if v1 != v2 :
            combinations.append( "_".join( [constant_part,v1,v2] ) )

for c in combinations :
    print "python crawler.py -k webascorpus-inf.ufrgs.br -l " + lang + " -p " + prefix + " -n " + n + " -v " + c
