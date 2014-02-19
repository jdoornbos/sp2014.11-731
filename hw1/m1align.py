# -*- coding: utf-8 -*-
'''
Created on Jan 30, 2014

@author: Jeremy Doornbos
@author: Mario Piergallini
'''

from collections import defaultdict

if __name__ == '__main__':

  def getbest(w1, other_sent, p_dist, exactMatches):
    maxprob = 0
    aligned = len(other_sent) - 1
    for w2 in other_sent:
      if (w1 == w2) and (w1 in exactMatches):
        aligned = other_sent.index(w2)
        return aligned
      if p_dist[(w2,w1)] > maxprob:
        maxprob = p_dist[(w2,w1)]
        aligned = other_sent.index(w2)
    return aligned

  def train(bisents):
    for (source, target) in bisents:
      source.append("$null$")
 
    # Create word lists
    print "*** Word lists"
    source_words = set()
    target_words = set()
    matchCounts = defaultdict(lambda: [0,0])
    iteration = 1
    for (source, target) in bisents:
      s_set = set(source)
      t_set = set(target)
      source_words.update(s_set)
      target_words.update(t_set)
      if iteration % (trainsize / 10) == 0:
        print "sentence:", iteration
      for t in target:
        if t in s_set:
          matchCounts[t][0] += 1
          matchCounts[t][1] += 1
        else:
          matchCounts[t][1] += 1
      for s in source:
        if s not in t_set:
          matchCounts[s][1] += 1
      iteration += 1
      
    exactMatches = set()
    for word in matchCounts:
      matchRate = float(matchCounts[word][0])/float(matchCounts[word][1])*100
      if matchRate >= 1 and (matchRate + len(word)) >= 15:
        exactMatches.add(word)
    
    source_len = len(source_words)
    target_len = len(target_words)
    
    cooccur = defaultdict(int)
    p = defaultdict(lambda:1 / float(source_len))
    count = defaultdict(float)
    total = defaultdict(float)
    subtotal = defaultdict(float)
    
    print source_len - 1, "Source words"
    print target_len, "Target words"
    
    # Create co-occurrance counts
    print "*** Co-occurrance counts"
    sentnum = 0
    for (source, target) in bisents:
      if sentnum % (trainsize / 10) == 0:
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
        if sentnum % (trainsize / 10) == 0:
          print "   sentence:", sentnum
        sentnum += 1
        for s_word in source:
          for t_word in target:
            count[(s_word, t_word)] += p[(s_word, t_word)] / subtotal[s_word]
            total[t_word] += p[(s_word, t_word)] / subtotal[s_word]
            
      # estimate probabilities
      for (s_word, t_word) in p:
        p[(s_word, t_word)] = count[(s_word, t_word)] / total[t_word]
    
    print    
    return p, exactMatches
  
  
  
  
  numtoprint = 2
  goldData = 'data//dev.align'
  gold = [aligns.strip() for aligns in open(goldData)][:numtoprint]
  
  trainsize = 10000
  testsize = 50000
  data = 'data//dev-test-train.de-en'
#   data = 'data//tiny.de-en'
  bitext =  [[sentence.strip().lower().split() for sentence in pair.split(' ||| ')] for pair in open(data)][:testsize]
  bitext_st = [[sentence.strip().lower().split() for sentence in pair.split(' ||| ')] for pair in open(data)][:trainsize]
  bitext_ts = [[sentence.strip().lower().split() for sentence in pair.split(' ||| ')] for pair in open(data)][:trainsize]
  
  for sent in bitext_ts:
    sent.reverse()
    
  (prob_dist, exacts)  = train(bitext_st)

  (prob_dist2, exacts)  = train(bitext_ts)
  

  output = open("output.txt", 'w')
  
  
  print "*** Write alignments"
  sentnum = 0
  for (source, target) in bitext:
    if sentnum % (testsize / 10) == 0:
      print "   sentence:", sentnum
    sentnum += 1
        
#     if n >= numtoprint:
#       break
#     print " ".join(source)
#     print gold[n]
#     print " ".join(target)
    
    aligns1 = set()
    for word in target:
      best_align = getbest(word, source, prob_dist, exacts)
      if best_align < len(source):
        sentOutput = str(best_align) + '-' + str(target.index(word))
        aligns1.add((best_align, target.index(word)))
      else:
        sentOutput = str(best_align) + '-$'
#       print sentOutput,
#     print
#     print aligns1
    
    aligns2 = set()
    for word in source:
      best_align = getbest(word, target, prob_dist2, exacts)
      if best_align < len(target):
        sentOutput = str(source.index(word)) + '-' +  str(best_align)
        aligns2.add((source.index(word), best_align))
      else:
        sentOutput = '$-' + str(best_align)
#       print sentOutput,
#     print
#     print aligns2
    
#     print
    sure_aligns = set.intersection(aligns1, aligns2)
#     print sure_aligns
#     poss_aligns = set.union(aligns1, aligns2) - sure_aligns
#     print poss_aligns
    
    sentOutput = ''
    for (s, t) in sure_aligns:
      sentOutput += str(s) + '-' + str(t) + ' '
#     for (s, t) in poss_aligns:
#       sentOutput += str(s) + '-' + str(t) + ' '
      
#     print sentOutput
    output.write(sentOutput.strip() + "\n")
#     for word in target:
#       print source[getbest(word, source)] + '-' + word,
#     print
#     print
  print 'Done!'
  # print to output file
#   for (source, target) in bitext:
#     sentOutput = ""
#     for word in target:
#       best_align = getbest(word, source, prob_dist, exacts)
#       if best_align < len(source) - 1:
#         # non-reversed
#         sentOutput += str(best_align) + '-' + str(target.index(word)) + ' '
#         # reversed
# #         sentOutput += str(target.index(word)) + '-' + str(getbest(word, source)) + ' ' 
#     output.write(sentOutput.strip() + "\n")
