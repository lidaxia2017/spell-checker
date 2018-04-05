"""A simple spell checker program"""

import numpy as np
import sys
import re
import string

def init_matrix():
  """only take care of lower letters
    #: empty
  """
  chars = 'abcdefghijklmnopqrstuvwxyz'
  o = {}
  for char1 in chars:
    o['#'+char1] = 0
    for char2 in chars:
      o[char1+char2] = 0
  return o

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

confusion_matrix = {
  'insertion': init_matrix(),
  'deletion': init_matrix(),
  'substitution': init_matrix(),
  'transposition': init_matrix(),
}

def cal_confusion_matrix(case, correct, typo, count):
  if case == 'insertion':
    for idx in range(len(typo)):
      if correct == typo[:idx] + typo[idx+1:]:
        if idx == 0:
          confusion_matrix['insertion']['#'+typo[:1]] += int(count)
        else:
          confusion_matrix['insertion'][typo[idx-1:idx+1]] += int(count)
  elif case == 'deletion':
    for idx in range(len(correct)):
      if correct[:idx] + correct[idx+1:] == typo:
        if idx == 0:
          confusion_matrix['deletion']['#'+correct[:1]] += int(count)
        else:
          confusion_matrix['deletion'][correct[idx-1:idx+1]] += int(count)
  elif case == 'substitution':
    for idx in range(len(typo)):
      for char in 'abcdefghijklmnopqrstuvwxyz':
        if correct == typo[:idx] + char + typo[idx+1:]:
          confusion_matrix['substitution'][char+typo[idx]] += int(count)
  elif case == 'transposition':
    for idx in range(len(correct)-1):
      if correct == typo[:idx] + typo[idx+1] + typo[idx] + typo[idx+2:]:
        confusion_matrix['transposition'][typo[idx+1] + typo[idx]] += int(count)
  # else:
  #   print(case, correct, typo, count)

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
      cal_confusion_matrix('insertion', correct, typo, count)
    elif len(correct) == len(typo) + 1:
      cal_confusion_matrix('deletion', correct, typo, count)
    elif len(correct) == len(typo):
      cal_confusion_matrix('substitution', correct, typo, count)
      cal_confusion_matrix('transposition', correct, typo, count)
    # else:
    #   cal_confusion_matrix('***', correct, typo, count)

print_matrix(confusion_matrix)
