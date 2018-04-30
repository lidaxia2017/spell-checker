"""A simple spell checker program"""

import numpy as np
import sys
import re
import string
import bigram
from collections import Counter

def init_matrix():
  """only take care of lower letters
    #: empty char
  """
  chars = 'abcdefghijklmnopqrstuvwxyz'
  o = {}
  for char1 in chars:
    o['#'+char1] = 0
    for char2 in chars:
      o[char1+char2] = 0
  return o

def words(text):
  return re.findall(r'[a-zA-Z,.\'\-]+', text)

CORPUS = open('./corpus.txt').read()
WORDS = Counter(words(CORPUS))
N=sum(WORDS.values())
CONFUSION_MATRIX = {
  'ins': init_matrix(),
  'del': init_matrix(),
  'subs': init_matrix(),
  'trans': init_matrix(),
}

def print_matrix(matrix):
  chars = 'abcdefghijklmnopqrstuvwxyz'
  for key in matrix.keys():
    print(key)
    print('{:>4}'.format('//'), end='')
    for char in chars:
      print('{:>4}'.format(char), end='')
    print()
    for row in '#'+chars:
      print('{:>4}'.format(row), end='')
      for col in chars:
        print('{:>4}'.format(matrix[key][row+col]), end='')
      print()

def cal_confusion_matrix(case, correct, typo, count):
  if case == 'ins':
    for idx in range(len(typo)):
      if correct == typo[:idx] + typo[idx+1:]:
        xy = '#'+typo[:1] if idx == 0 else typo[idx-1:idx+1]
        CONFUSION_MATRIX['ins'][xy] += int(count)
  elif case == 'del':
    for idx in range(len(correct)):
      if correct == typo[:idx] + correct[idx] + typo[idx:]:
        xy = '#'+correct[:1] if idx == 0 else correct[idx-1:idx+1]
        CONFUSION_MATRIX['del'][xy] += int(count)
  elif case == 'subs':
    for idx in range(len(typo)):
      for char in 'abcdefghijklmnopqrstuvwxyz':
        if correct == typo[:idx] + char + typo[idx+1:]:
          xy = char+typo[idx]
          CONFUSION_MATRIX['subs'][xy] += int(count)
  elif case == 'trans':
    for idx in range(len(correct)-1):
      if correct == typo[:idx] + typo[idx+1] + typo[idx] + typo[idx+2:]:
        xy = typo[idx+1] + typo[idx]
        CONFUSION_MATRIX['trans'][xy] += int(count)

def init_confusion_matrix():
  fname = './spellerror.txt'
  with open(fname) as f:
    lines = f.readlines()
  lines = [x.strip() for x in lines]
  for line in lines:
    correct, typos = [word.strip().lower() for word in line.split(':')]
    if not re.match("^[a-z]*$", correct):
      continue
    for typo in [typo.strip() for typo in typos.split(',')]:
      if not re.match("^[a-z]*$", typo):
        continue
      count = 1
      if '*' in typo:
        typo, count = typo.split('*')
      if len(correct) == len(typo) - 1:
        cal_confusion_matrix('ins', correct, typo, count)
      elif len(correct) == len(typo) + 1:
        cal_confusion_matrix('del', correct, typo, count)
      elif len(correct) == len(typo):
        cal_confusion_matrix('subs', correct, typo, count)
        cal_confusion_matrix('trans', correct, typo, count)

def cal_candidates(word):
    "All edits that are one edit away from `word`."
    o = {}
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    o['ins'] = [L + R[1:] for L, R in splits if R]
    o['del'] = [L + c + R for L, R in splits for c in letters]
    o['subs'] = [L + c + R[1:] for L, R in splits if R for c in letters]
    o['trans'] = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    return o

def valid(words):
  return set(w for w in words if w in WORDS)

def compare(candidates, typo, words):
  o = {}
  s = {}
  h = {}
  for key in candidates.keys():
    for c in candidates[key]:
      if key == 'ins':
        for idx in range(len(typo)):
          if c == typo[:idx] + typo[idx+1:]:
            xy = '#' + typo[idx] if idx == 0 else typo[idx-1:idx+1]
            print_candidate(o, c, key, xy, xy[0], typo, words, s, h)
      elif key == 'del':
        for idx in range(len(c)):
          if c[:idx] + c[idx+1:] == typo:
            xy = '#'+c[idx] if idx == 0 else c[idx-1:idx+1]
            print_candidate(o, c, key, xy, xy.replace('#', ''), typo, words, s, h)
      elif key == 'subs':
        for idx in range(len(typo)):
          for char in 'abcdefghijklmnopqrstuvwxyz':
            if c == typo[:idx] + char + typo[idx+1:]:
              xy = char+typo[idx]
              print_candidate(o, c, key, xy, xy[1], typo, words, s, h)
      elif key == 'trans':
        for idx in range(len(c)-1):
          if c == typo[:idx] + typo[idx+1] + typo[idx] + typo[idx+2:]:
            xy = typo[idx+1] + typo[idx]
            print_candidate(o, c, key, xy, xy, typo, words, s, h)
  print('The most possible correct word is: ', max(o, key=o.get))
  print('The most possible correct sentence is: ', max(s, key=s.get))
  print('The most possible correct sentence is: ', max(h, key=h.get))

def print_table_title():
  print('{:>10}'.format('Method'), end='')
  print('{:>16}'.format('Candidate'), end='')
  print('{:>10}'.format('Freq(c)'), end='')
  print('{:>16}'.format('P(c)'), end='')
  print('{:>10}'.format('C[XY]'), end='')
  print('{:>10}'.format('Total'), end='')
  print('{:>16}'.format('P(t|c)'), end='')
  print('{:>16}'.format('P(t|c)*P(c)'), end='')
  print('{:>16}'.format('P(bigram(S))'), end='')
  print('{:>16}'.format('Hybrid'), end='')
  print('')

def print_candidate(o, c, key, numerator, denominator, typo, words, s, h):
  sentence = words.replace(typo, c)
  if denominator == '#': denominator = ''
  print('{:>10}'.format(key+'['+numerator+']'), end='')
  print('{:>16}'.format(c), end='')
  print('{:>10}'.format(WORDS[c]), end='')
  pc = WORDS[c] / N
  print('{:>16}'.format('{:.4e}'.format(pc)), end='')
  ptc = CONFUSION_MATRIX[key][numerator]/CORPUS.count(denominator)
  print('{:>10}'.format(CONFUSION_MATRIX[key][numerator]), end='')
  print('{:>10}'.format(CORPUS.count(denominator)), end='')
  print('{:>16}'.format('{:.4e}'.format(ptc)), end='')
  print('{:>16}'.format('{:.4e}'.format(pc * ptc)), end='')
  ps = bigram.bb(sentence)
  print('{:>16}'.format('{:.4e}'.format(pc * ptc * ps)), end='')
  print('')
  o[c] = o.get(c, 0) + pc * ptc
  s[sentence] = s.get(sentence, 0) + ps
  h[sentence] = h.get(sentence, 0) + pc * ptc * ps

def main():
  init_confusion_matrix()
  words = sys.argv[1]
  typo = ''
  for word in words.split(' '):
    if word not in WORDS:
      typo = word
      break
  if typo == '':
    print('There is no spell error.')
  else:
    candidates = cal_candidates(typo)
    valid_candidates = {}
    for key in list(candidates.keys()):
      valid_candidates[key] = valid(candidates[key])
    print_table_title()
    compare(valid_candidates, typo, words)

if __name__ == "__main__":
    main()
