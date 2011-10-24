#!/bin/sh

sh bin/generate_labels_frequent.sh
rm -r conf_corpus

python bin/combine_labels.py conference labels/labels_frequent.en en conf_corpus 10 webascorpus-inf.ufrgs.br > get_corpus_en.sh
screen -S en sh get_corpus_en.sh

python bin/combine_labels.py conférence labels/labels_frequent.fr fr conf_corpus 10 webascorpus-inf.ufrgs.br > get_corpus_fr.sh
screen -S fr sh get_corpus_fr.sh

python bin/combine_labels.py conferência labels/labels_frequent.pt pt conf_corpus 10 webascorpus-inf.ufrgs.br > get_corpus_pt.sh
screen -S pt sh get_corpus_pt.sh
