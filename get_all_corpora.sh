#!/bin/sh

rm -r conf_corpus

python labels/combine_labels.py conference labels/labels_frequent.en en conf_corpus 100 > get_corpus_en.sh
screen -S en sh get_corpus_en.sh

python labels/combine_labels.py conférence labels/labels_frequent.fr fr conf_corpus 100 > get_corpus_fr.sh
screen -S fr sh get_corpus_fr.sh

python labels/combine_labels.py conferência labels/labels_frequent.pt pt conf_corpus 100 > get_corpus_pt.sh
screen -S pt sh get_corpus_pt.sh
