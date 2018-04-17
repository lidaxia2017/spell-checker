"""This project is used to compute given string's probability using bigram"""
import sys
import string
from collections import OrderedDict
from copy import deepcopy

def read_file(fileName):
  text = open(fileName, 'r', encoding='utf-8-sig').read()
  table = str.maketrans({key: None for key in string.punctuation})
  corpus = text.translate(table).split()
  for item in corpus:
    DICT[item] = DICT.get(item, 0) + 1
  return corpus

def create_counts(new_str):
  strLen = len(new_str)
  counts = [0 for i in range(strLen)]
  for idx in range(strLen):
    counts[idx] = DICT.get(new_str[idx])
  return counts

def create_bigram_counts_table(new_str, corpus):
  strLen = len(new_str)
  bigramCounts = [[0 for x in range(strLen)] for y in range(strLen)]
  for idx in range(len(corpus) - 1):
    word = corpus[idx]
    try:
      idx0 = new_str.index(word)
      idx1 = new_str.index(corpus[idx + 1])
      bigramCounts[idx0][idx1] += 1
    except ValueError:
      continue
  # print_table(bigramCounts, new_str, 'd')
  return bigramCounts

def create_bigram_prob_table(mode, new_str, counts, bigramCounts, corpus):
  strLen = len(new_str)
  bigramProb = [[0 for x in range(strLen)] for y in range(strLen)]
  v = len(set(corpus))
  for r in range(strLen):
    for c in range(strLen):
      bigramProb[r][c] = bigramCounts[r][c] / counts[r] if mode is 0 else ((bigramCounts[r][c] + 1) / (v + counts[r]))
  # print_table(bigramProb, new_str, 'e')
  return bigramProb

def compute_probability(str1, new_str, bigramProb):
  prob = 1
  for idx in range(len(str1) - 1):
    idx0 = new_str.index(str1[idx])
    idx1 = new_str.index(str1[idx + 1])
    prob *= bigramProb[idx0][idx1]
  print('{:>16}'.format('{:.4e}'.format(prob)), end='')
  return prob

def reconsitituta_table(new_str, counts, oldBigramCounts, corpus):
  bigramCounts = deepcopy(oldBigramCounts)
  v = len(set(corpus))
  for r in range(len(counts)):
    for c in range(len(counts)):
      bigramCounts[r][c] = (bigramCounts[r][c] + 1) * counts[r] / (counts[r] + v)
  # print_table(bigramCounts, new_str, 'f')
  return bigramCounts

def print_table(table, new_str, mode):
  tableName = "# Prob #" if mode is 'e' else "# Count #"
  print('{:>16}'.format(tableName), end='')
  for idx in range(len(new_str)):
    print('{:>16}'.format(new_str[idx]), end='')
  print()
  for r in range(len(table)):
    print('{:>16}'.format(new_str[r]), end='')
    for c in range(len(table[r])):
      if mode is 'e':
        print('{:>16}'.format('{:.2e}'.format(table[r][c])), end='')
      elif mode is 'd':
        print('{:>16}'.format('{:d}'.format(table[r][c])), end='')
      elif mode is 'f':
        print('{:>16}'.format('{:.2f}'.format(table[r][c])), end='')
    print ('')
  print()
  return

def compute_bigram(new_str, corpus):
  # print("###  This is a new sentence.  ###")
  # print(new_str)

  str_set = list(OrderedDict.fromkeys(new_str.split()))
  counts = create_counts(str_set)

  bigramCounts = create_bigram_counts_table(str_set, corpus)

  # print("###  Bigram tables with Add-one smoothing. ###")
  reconsitituta_table(str_set, counts, bigramCounts, corpus)
  bigramProb1 = create_bigram_prob_table(1, str_set, counts, bigramCounts, corpus)
  # print("The probability is: ", end='')
  return compute_probability(new_str.split(), str_set, bigramProb1)

def bb(str):
  fileName = "corpus.txt"
  corpus = read_file(fileName)
  return compute_bigram(str, corpus)

DICT = {}
def main():
  str1 = sys.argv[1]
  fileName = "corpus.txt"
  corpus = read_file(fileName)
  compute_bigram(str1, corpus)

if __name__ == "__main__":
  main()
