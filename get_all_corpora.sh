#!/bin/sh

python labels/combine_labels.py conference labels/labels_frequent.en en conf_corpus 100 > get_corpus_en.sh
sh get_corpus_en.sh
rm get_corpus_en.sh

python labels/combine_labels.py conférence labels/labels_frequent.fr fr conf_corpus 100 > get_corpus_fr.sh
sh get_corpus_fr.sh
rm get_corpus_fr.sh

python labels/combine_labels.py conferência labels/labels_frequent.pt pt conf_corpus 100 > get_corpus_pt.sh
sh get_corpus_pt.sh
rm get_corpus_pt.sh
