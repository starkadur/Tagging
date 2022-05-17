#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from collections import defaultdict
import json
import os
import sys
import time


class NefnirLive(object):
	
    def __init__(self, rules_path=None, tag_path=None):
        nefnir_dir = os.path.dirname(sys.argv[0])

        if rules_path is None:
            rules_path = os.path.join(nefnir_dir, 'rules.json')

        if tag_path is None:
            tag_path = os.path.join(nefnir_dir, 'tags.json')

        with open(rules_path, encoding='utf-8') as f:
            self.rules = json.load(f)

        with open(tag_path, encoding='utf-8') as f:
            self.tagmap = json.load(f)
            
        
        self.tagmap['<paragraph>'] = '<paragraph>'

        self.proper = {t for t in self.tagmap if t[0] == 'n' and t[-1] in {'m', 'ö', 's'}}
        self.unanalyzed = {t for t in self.tagmap if t[:2] == 'nx'} | {'x', 'e', 'as'}

    def lemmatize(self, form, tag):
        try:
            ntag = self.tagmap[tag]
        except KeyError:
            if any((c for c in tag if c.isalpha())):
                if form!="<paragraph>":
                    print("Unknown tag: {} {}".format(form, tag))
            return form

        if tag in {'v', 'au'}:
            return form.lower()

        if tag in self.unanalyzed:
            return form

        try:
            if form[-1] == '-':
                if tag in self.proper:
                    return self.recase(form, tag, form)
                return form.lower()
        except Exception as e:
            print(e)
            print(form,tag)
            sys.exit(1) 
        if not form[-1].isalpha():
            return form

        form_lower = form.lower()

        if ntag not in self.rules:
            # print("No rule for tag:", tag, ntag, form, tag)
            return self.recase(form, tag, form)

        if form_lower in self.rules[ntag]['form']:
            suffix_from, suffix_to = self.rules[ntag]['form'][form_lower]
            # print("Form match:", form_lower, suffix_from, suffix_to)
        else:
            suffixes = get_suffixes(form_lower)

            try:
                target = next(s for s in suffixes if s in self.rules[ntag]['suffix'])
                suffix_from, suffix_to = self.rules[ntag]['suffix'][target]
                # print("Suffix match:", form, tag, target, suffix_from, suffix_to)
            except StopIteration:
                # print("No match:", form, tag, ntag)
                return self.recase(form, tag, form)

        form_prefix = form_lower[:-len(suffix_from)] if suffix_from else form_lower
        lemma = form_prefix + suffix_to

        if not lemma:
            # print("Empty lemma:", form, tag, ntag, suffix_from, suffix_to, form_prefix)
            lemma = form_lower

        return self.recase(form, tag, lemma)

    def recase(self, form, tag, lemma):
        if '-' in form:
            fparts = form.split('-')
            lparts = lemma.split('-')

            result = []
            for fpart, lpart in zip(fparts, lparts):
                if fpart.isupper():
                    result.append(lpart.upper())
                elif fpart.istitle():
                    result.append(lpart.title())
                else:
                    result.append(lpart.lower())

            if tag in self.proper and not result[0].isupper():
                result[0] = result[0].title()

            return "-".join(result)

        if tag in self.proper:
            if len(form) > 1 and form.isupper():
                return lemma.upper()
            return lemma.title()
        return lemma


def get_suffixes(s):
    return (s[pos:] for pos in range(len(s) + 1))


def main():

    time_start = time.time()
    nefnir = Nefnir()

    with open(args.input_file, encoding=args.from_encoding) as f:
        input_lines = f.read().splitlines()

    length = len(input_lines)
    output_lines = [None] * length

    entries = defaultdict(list)
    num_tokens = length
    for pos, line in enumerate(input_lines):
        try:
            form, tag = line.split(args.separator)
            entries[(form, tag)].append(pos)
        except ValueError:
            num_tokens -= 1
            output_lines[pos] = line

    for (form, tag), poss in entries.items():
        lemma = nefnir.lemmatize(form, tag)
        outp = args.separator.join((form, tag, lemma))
        for pos in poss:
            output_lines[pos] = outp

    time_elapsed = time.time() - time_start
    print("{:,} tokens lemmatized in {:.2f} s ({:,.1f} tokens/s)".format(num_tokens, time_elapsed,
                                                                         num_tokens / time_elapsed))

    with open(args.output_file, 'w', encoding=args.to_encoding) as f:
        f.write("\n".join(output_lines))


if __name__ == '__main__':
    main()
