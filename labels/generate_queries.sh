#!/bin/bash
################################################################################
for f in $(ls original/*fr.txt); do 
    cat $f | 
    awk '{print $1}' | 
    grep "^[A-Z]" | 
    sed 's/\([a-z]\)\([A-Z]\)/\1_\2/g' | 
    sed 's/_/ /g' | 
    awk '{ print tolower($0) }' |
    sed 's/ *$//g' |
    cat
done | 
sort | 
uniq -c | 
sort -n | 
awk '{ if ( $1 > 1 ) { for( i=2;i<=NF;i++) printf("%s ",$i); printf( "\n" ) } }' |
grep -v "^conference $" |
cat > labels_frequent.en
################################################################################
for f in $(ls original/*fr.txt); do 
    cat $f | 
    grep "^[A-Z]" |
    awk 'BEGIN{ FS = "\t" }{print tolower($2) }' | 
    sed 's/ *$//g' |
    cat
done |
sort |
uniq -c |
sort -n |
awk '{ if ( $1 > 1 ) { for( i=2;i<=NF;i++) printf("%s ",$i); printf( "\n" ) } }' |
grep -v "^conférence $" |
cat > labels_frequent.fr
################################################################################
for f in $(ls original/*pt.txt); do 
    cat $f | 
    grep "^[A-Z]" |
    awk 'BEGIN{ FS = "\t" }{print tolower($2) }' | 
    sed 's/ *$//g' |
    cat
done |
sort |
uniq -c |
sort -n |
awk '{ if ( $1 > 1 ) { for( i=2;i<=NF;i++) printf("%s ",$i); printf( "\n" ) } }' |
grep -v "^conferência $" |
cat > labels_frequent.pt
################################################################################

