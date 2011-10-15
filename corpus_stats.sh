echo "English"
grep "<s>" conf_corpus/en/* | wc
echo "Portugues"
grep "<s>" conf_corpus/pt/* | wc
echo "Francais"
grep "<s>" conf_corpus/fr/* | wc
