#!/usr/bin/env python3

import itertools
import nltk
import re
import statistics
from collections import defaultdict, Counter

COL_SEP = "\t"
PHRASE_COL_NAME = "PHRASE"
DA_LABEL_COL_NAME = "DA"
USERNAME_PLACEHOLDER_TOKEN = "<user>"

WHITESPACE_PATTERN = re.compile("\\s+")

class DialogueActTargets(object):
	def __init__(self, target_da_label_counts, usernames):
		self.target_da_label_counts = target_da_label_counts
		self.total_label_count = total_embedded_dict_values(target_da_label_counts)
		self.target_da_label_likelihoods = create_da_label_likelihood_dict(target_da_label_counts, float(self.total_label_count))
		self.usernames = usernames

	def __repr__(self):
		return self.__class__.__name__ + str(self.__dict__)

class PhraseDALabeller(object):
	def __init__(self, phrase_da_labels, usernames, ngram_factory=nltk.bigrams):
		self.phrase_da_labels = phrase_da_labels
		self.ngram_da_labels = create_ngram_da_label_dict(phrase_da_labels, ngram_factory)
		self.usernames = usernames
		self.ngram_factory = ngram_factory

	def find_phrase_da_labels(self, phrase_tokens):
		result = {}
		user_placeholder_phrases = dict((username, tuple(USERNAME_PLACEHOLDER_TOKEN if token == username else token for token in phrase_tokens)) for username in usernames)
		for username in usernames:
			phrase_tokens_with_placeholder = user_placeholder_phrases[username]
			da_labels = self._find_exact_phrase_da_labels(phrase_tokens_with_placeholder)
			if len(da_labels) > 0:
				result[username] = da_labels

		if len(result) == 0:
			for username in usernames:
				phrase_tokens_with_placeholder = user_placeholder_phrases[username]
				da_labels = self._find_ngram_da_labels(phrase_tokens_with_placeholder)
				if len(da_labels) > 0:
					result[username] = da_labels

		return result

	def _find_exact_phrase_da_labels(self, phrase_tokens_with_placeholder):
		result = defaultdict(Counter)
		# TODO: Replace this with a suffix tree to improve performance
		for subseq_length in range(len(phrase_tokens_with_placeholder), 0, -1):
			subseqs = nltk.ngrams(phrase_tokens_with_placeholder, subseq_length)
			for subseq in subseqs:
				subseq_labels = self.phrase_da_labels.get(subseq)
				if subseq_labels is not None:
					result[subseq].update(subseq_labels)
		return result

	def _find_ngram_da_labels(self, phrase_tokens):
		result = defaultdict(Counter)
		phrase_ngrams = self.ngram_factory(phrase_tokens)
		for ngram in phrase_ngrams:
			ngram_labels = self.ngram_da_labels.get(ngram)
			if ngram_labels is not None:
				result[ngram].update(ngram_labels)
		return result

def create_da_label_likelihood_dict(target_da_label_counts, total_label_count):
	user_label_total_counts = defaultdict(Counter)
	for username, label_counts in target_da_label_counts.items():
		label_total_counts = user_label_total_counts[username]
		for phrase, da_counts in label_counts.items():
			label_total_counts.update(da_counts)

	result = {}
	for username, da_label_counts in user_label_total_counts.items():
		da_label_likelihoods = dict((da_label, count / total_label_count) for da_label, count in da_label_counts.items())
		result[username] = da_label_likelihoods
	return result

def create_ngram_da_label_dict(phrase_da_labels, ngram_factory):
	result = {}
	for phrase, da_label in phrase_da_labels.items():
		phrase_bigrams = ngram_factory(phrase)
		for bigram in phrase_bigrams:
			result[bigram] = da_label
	return result

def create_phrase_da_label_dict(rows):
	result = defaultdict(Counter)
	col_name_idxs = dict((col_name, idx) for (idx, col_name) in enumerate(next(rows)))
	for row in rows:
		phrase = row[col_name_idxs[PHRASE_COL_NAME]]
		phrase_tokens = tuple(WHITESPACE_PATTERN.split(phrase))
		da_label = row[col_name_idxs[DA_LABEL_COL_NAME]]
		result[phrase_tokens][da_label] += 1

	return result

def total_embedded_dict_values(d):
	result = 0
	for embedded_dict in d.values():
		for embedded_counter in embedded_dict.values():
			result += sum(embedded_counter.values())
	return result

if __name__ == "__main__":
	import sys
#	if len(sys.argv != 1):
#		raise ValueError("Usage: %s INPUT > OUTPUT" % sys.argv[0])
#	else:

	input = "I accuse Zofia because she has been talking a lot but Patrik is a villager"
	dialogue_category_inpath = "phrase_da_labels.tsv"
	usernames = frozenset(("Zofia", "Todd", "Patrik"))

	phrase_da_labels = defaultdict(Counter)
	with open(dialogue_category_inpath, 'r') as lines:
		rows = (line.strip().split(COL_SEP) for line in lines)
		phrase_da_labels = create_phrase_da_label_dict(rows)
	print("Read phrase label dict of size %d." % len(phrase_da_labels), file=sys.stderr)

	phrase_da_labeller = PhraseDALabeller(phrase_da_labels, usernames)

	input_tokens = WHITESPACE_PATTERN.split(input)
	da_labels = phrase_da_labeller.find_phrase_da_labels(input_tokens)
	print(da_labels)
	da_targets = DialogueActTargets(da_labels, usernames)
	print(da_targets)


