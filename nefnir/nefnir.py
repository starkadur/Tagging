#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import codecs
import json
import logging
import time
from collections import Counter

FORMAT = '%(asctime)s - %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)


class Nefnir(object):
    """
    A rule-based lemmatizer
    """
    def __init__(self, rules, tagmap):
        """
        Initialize an instance of the Nefnir lemmatizer.
        """
        self.rules = rules
        self.tagmap = tagmap

        self.proper_nouns = {t: t[:-2] for t in self.tagmap.values() if t.startswith('no') and t.endswith('-s')}
        self.uninflected = {t for t in tagmap.values() if t.startswith('ób')} | {'no-x'}

    def lemmatize(self, form, tag):
        """
        Lemmatize a word form given its part-of-speech tag.

        :param form: A word form.
        :param tag: The word form's part-of-speech tag.
        :return: The word form's lemma.
        """
        try:
            nefnir_tag = self.tagmap[tag]
        except KeyError:
            logger.warning("Unknown tag: {}".format((form, tag)))
            return form

        # Assume that lemmas for abbreviations and unanalyzed/foreign words are identically cased
        if nefnir_tag in {'ób-x', 'ób-e', 'ób-sk'}:
            return form

        # Assume that lemmas for other uninflected words (conjunctions, interjections, etc.) are lowercase
        if nefnir_tag in self.uninflected:
            return form.lower()

        # Don't bother finding matching rules for word forms with no alphabetical characters
        if not any(c for c in form if c.isalpha()):
            return form

        # Proper nouns with no gender analysis and word forms ending with a hyphen
        if nefnir_tag == 'no-x-s' or form[-1] == '-':
            return self.recase(form, nefnir_tag, form)

        # Words ending with a nonalphabetic character (other than a hyphen)
        if not form[-1].isalpha():
            return form

        if nefnir_tag not in self.rules:
            logger.warning("No rules for this tag: {} {} {}".format(form, tag, nefnir_tag))
            return self.recase(form, tag, form)

        form_lower = form.lower()

        # For proper nouns, first apply the corresponding rules for common nouns
        if nefnir_tag in self.proper_nouns:
            baseline_tf = self.get_tf(form_lower, self.proper_nouns[nefnir_tag])
            tf = self.get_tf(form_lower, nefnir_tag) or baseline_tf
        else:
            tf = self.get_tf(form_lower, nefnir_tag)

        if tf is None:
            logger.debug("No rules for this word form: {} {}".format(form, tag))
            tf = ('', '')

        suffix_from, suffix_to = tf

        form_prefix = form_lower[:-len(suffix_from)] if suffix_from else form_lower
        lemma = form_prefix + suffix_to

        if not lemma:
            logger.debug("Rule produced an empty lemma: ({}, {}, {}) ('{}' -> '{}')".format(form, tag, nefnir_tag,
                                                                                            suffix_from, suffix_to))
            lemma = form_lower

        return self.recase(form, nefnir_tag, lemma)

    def get_tf(self, form, tag):
        if form in self.rules[tag]['form']:
            return self.rules[tag]['form'][form]

        suffixes = get_suffixes(form)

        try:
            target = next(s for s in suffixes if s in self.rules[tag]['suffix'])
            return self.rules[tag]['suffix'][target]
        except StopIteration:
            return None

    def recase(self, form, tag, lemma):
        """
        Determine how to properly case a lemma given the word form and part of speech tag it was derived from.

        Nefnir transforms words into lowercase prior to lemmatization. Some words, such as proper nouns, abbreviations
        and foreign words therefore need to be re-capitalized or changed back into uppercase.

        :param form: A word form, cased as it was written.
        :param tag: The word form's part-of-speech tag.
        :param lemma: The word form's lemma, in lowercase.
        :return: A properly cased lemma.
        """
        # Hyphenated words: try to maintain original casing in each part
        #   1) (DNA-þræðinum, nþeþg) -> dna-þráður -> DNA-þráður
        #   2) (Vestur-Íslendingum, nkfþ-s) -> vestur-íslendingur -> Vestur-Íslendingur
        #   3) (Stoke-on-Trent, e) -> stoke-on-trent -> Stoke-on-Trent
        if '-' in form[1:-1]:
            fparts = form.split('-')
            lparts = lemma.split('-')

            result = []
            for fpart, lpart in zip(fparts, lparts):
                if fpart.lower() == lpart.lower():
                    # part was not transformed by lemmatization
                    result.append(fpart)
                elif fpart.isupper():
                    # part was transformed and was uppercase
                    result.append(lpart.upper())
                elif fpart.istitle():
                    # part was transformed and was title cased
                    result.append(lpart.title())
                else:
                    # part was transformed and not uppercase or title cased
                    result.append(lpart.lower())

            if tag in self.proper_nouns and not result[0].isupper():
                result[0] = result[0].title()

            return "-".join(result)

        # Proper nouns: capitalize the lemma
        #   1) (Halldórs, nken-s) -> halldór -> Halldór
        #   2) (HALLDÓRS, nken-s) -> halldór -> Halldór
        if tag in self.proper_nouns:
            if form.isupper() and 1 < len(form) < 5:
                return lemma.upper()
            return lemma.title()

        # If none of the above applies, return lemma in lowercase
        return lemma.lower()


def get_suffixes(s):
    """
    Return an iterator yielding a string's suffixes, from the largest to the smallest.

    :param s: A text string.
    :return: An iterator for the string's suffixes.
    """
    return (s[pos:] for pos in range(len(s) + 1))


def main():
    # Command line interface
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rules", help="the path to a JSON document with transformation rules", required=True)
    parser.add_argument("-t", "--tagset", help="the path to a JSON document with tagset mappings", required=True)
    parser.add_argument("-i", "--input-file", help="read input from specified file", required=True)
    parser.add_argument("-o", "--output-file", help="write output to specified file (otherwise, write to stdout)")
    parser.add_argument("--from-encoding", help="character encoding of input file (default: utf-8)",
                        default="utf-8")
    parser.add_argument("--to-encoding", help="character encoding of output file (default: utf-8)",
                        default="utf-8")
    parser.add_argument("-s", "--separator", help="the string separating word forms, tags and lemmas (default: '\\t')",
                        default='\t')
    args = parser.parse_args()

    args.separator = codecs.decode(args.separator, 'unicode_escape')

    # Lemmatize input
    time_start = time.time()

    with open(args.rules, encoding='utf-8') as f:
        rules = json.load(f)

    with open(args.tagset, encoding='utf-8') as f:
        tagset = json.load(f)

    nefnir = Nefnir(rules, tagset)

    logger.info("Reading input from {} ({})".format(args.input_file, args.from_encoding))
    logger.debug("Separator set to {}".format(repr(args.separator)))

    with open(args.input_file, encoding=args.from_encoding) as f:
        lines = f.read().splitlines()

    lemmas = {}
    for line in set(lines) - {''}:
        try:
            form, tag = line.split(args.separator)
            lemma = nefnir.lemmatize(form, tag)
            lemmas[line] = args.separator.join((form, tag, lemma))
        except ValueError:
            if line.strip():
                logger.warning('Ignoring line: {}'.format(line))

    # Statistics
    time_elapsed = time.time() - time_start

    line_counts = Counter(lines)
    num_tokens = sum(line_counts.values()) - line_counts['']
    lines_per_second = num_tokens / time_elapsed
    stats = "{:,} tokens processed in {:.2f} s ({:,.0f} tokens/s)".format(num_tokens, time_elapsed, lines_per_second)
    logger.info(stats)

    # Write output
    if args.output_file:
        logger.info("Writing output to {} ({})".format(args.output_file, args.to_encoding))
        with open(args.output_file, 'w', newline='\n', encoding=args.to_encoding) as f:
            for line in lines:
                output = lemmas.get(line.strip(), '')
                f.write(output + '\n')
    else:
        for line in lines:
            output = lemmas.get(line.strip(), '')
            print(output)


if __name__ == '__main__':
    main()
