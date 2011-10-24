#grep "<s>" conf_corpus/en/* | wc
for l in en pt fr; do
    echo "********"
    echo "*  $l  *"
    echo "********"
    docs=`ls conf_corpus/$l/*.xml | wc -l`
    echo "$docs documents"
    #echo "sentenc | word tokens"
    printf "" > vocab
    for f in $( ls conf_corpus/$l/*.xml ); do
        awk 'BEGIN{ start = 0 }\
             /<text>/{ start=1 }\
             /<s>/{ if( start ){ \
                sent=$0; \
                gsub("</?s>","",sent); \
                gsub( "[\.,:!\?;]"," & ", sent); \
                print tolower( sent ); \
                gsub( " ","\n",sent); print tolower(sent) >> "vocab";\
                } }' $f;
    done | wc -l -w | awk '{print $1 " sentences"; print $2 " word tokens";}'
    #echo "vocab (word types)"
    sort vocab | uniq -c | sort -nr > conf_corpus/$l.vocab
    wc -l conf_corpus/$l.vocab | awk '{print $1 " word types"}'
    echo "top 10 words:"
    head -n 11 conf_corpus/$l.vocab | tail -n 10
    rm vocab
done
