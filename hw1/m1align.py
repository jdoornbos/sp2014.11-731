# -*- coding: utf-8 -*-
'''
Created on Jan 30, 2014

@author: Jeremy Doornbos
@author: Mario Piergallini
'''

from collections import defaultdict

if __name__ == '__main__':

  def getbest(w1, other_sent, p_dist):
    maxprob = 0
    aligned = len(other_sent) - 1
    for w2 in other_sent:
      if p_dist[(w2,w1)] > maxprob:
        maxprob = p_dist[(w2,w1)]
        aligned = other_sent.index(w2)
    return aligned

  def train(bisents):
    for (source, target) in bisents:
      source.append("")

    # Create word lists
    print "*** Word lists"
    source_words = set()
    target_words = set()
    
    iteration = 1
    for (source, target) in bisents:
      if iteration % (size / 10) == 0:
        print "sentence:", iteration
      for word in source:
        source_words.add(word)
      for word in target:
        target_words.add(word)
      iteration += 1
    
    source_len = len(source_words)
    target_len = len(target_words)
    
    cooccur = defaultdict(int)
    p = defaultdict(lambda:1 / float(source_len))
    count = defaultdict(float)
    total = defaultdict(float)
    subtotal = defaultdict(float)
    
    print source_len - 1, "German words"
    print target_len, "English words"
    
    # Create co-occurrance counts
    print "*** Co-occurrance counts"
    sentnum = 0
    for (source, target) in bitext:
      if sentnum % (size / 10) == 0:
          print "sentence:", sentnum
      sentnum += 1
      for s in source:
        for t in target:
          cooccur[(s, t)] += 1
          p[(s, t)] = 1 / float(source_len)
        
    for iteration in range(5):
      print "iteration = " + str(iteration + 1) + ":"
      
      # initialize
      for (s_word, t_word) in p:
        count[(s_word, t_word)] = 0
        total[t_word] = 0
      
      # apply model
      # compute normalization
      for (s, t) in p:
        subtotal[s] += p[(s, t)] * cooccur[(s, t)]
      # collect counts
      sentnum = 0
      for (source, target) in bisents:
        if sentnum % (size / 10) == 0:
          print "   sentence:", sentnum
        sentnum += 1
        for s_word in source:
          for t_word in target:
            count[(s_word, t_word)] += p[(s_word, t_word)] / subtotal[s_word]
            total[t_word] += p[(s_word, t_word)] / subtotal[s_word]
            
      # estimate probabilities
      for (s_word, t_word) in p:
        p[(s_word, t_word)] = count[(s_word, t_word)] / total[t_word]
        
    return p
  
  
  
  
  numtoprint = 10
  goldData = 'data//dev.align'
  gold = [aligns.strip() for aligns in open(goldData)][:numtoprint]
  
  size = 20000
  data = 'data//dev-test-train.de-en'
#   data = 'data//tiny.de-en'
  bitext = [[sentence.strip().lower().split() for sentence in pair.split(' ||| ')] for pair in open(data)][:size]
  bisents = bitext
  
  # Reverse the SOURCE and TARGET
#   for sent in bisents:
#     sent.reverse()
    
  prob_dist = train(bisents)
  
  # print to console
  for (n, (source, target)) in enumerate(bisents):
    if n >= numtoprint:
      break
    print " ".join(source)
    print gold[n]
    print " ".join(target)
    for word in target:
      best_align = getbest(word, source, prob_dist)
      if best_align < len(source) - 1:
        sentOutput = str(best_align) + '-' + str(target.index(word))
      else:
        sentOutput = str(best_align) + '-$'
      print sentOutput,
      
    print
    for word in target:
      print source[getbest(word, source)] + '-' + word,
    print
    print
  
  # print to output file
  output = open("output.txt", 'w')
  for (source, target) in bisents:
    sentOutput = ""
    for word in target:
      best_align = getbest(word, source, prob_dist)
      if best_align < len(source) - 1:
        # non-reversed
        sentOutput += str(best_align) + '-' + str(target.index(word)) + ' '
        # reversed
#         sentOutput += str(target.index(word)) + '-' + str(getbest(word, source)) + ' ' 
    output.write(sentOutput.strip() + "\n")
