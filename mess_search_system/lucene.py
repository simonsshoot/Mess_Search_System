import json
import re
import math
from nltk.stem import PorterStemmer
from buildindex import InvertedIndex

class LuceneScorer:
  def __init__(self, index_path,idf_path,docs_path,using_stem=True,top_K=5):
    self.using_stem = using_stem
    self.stemmer = PorterStemmer() if using_stem else None
    self.top_K = top_K
    self.docs_meta=self._load_docs_meta(docs_path)
    # self.inverted_index = InvertedIndex(using_stem=using_stem)

    with open(index_path, 'r', encoding='utf-8') as f:
      self.index = json.load(f)

    with open(idf_path, 'r', encoding='utf-8') as f:
      idf_data=json.load(f)
      self.idf = idf_data['idf_values']

  def _load_docs_meta(self,docs_path):
    meta_dict={}
    with open(docs_path, 'r', encoding='utf-8') as f:
      for line in f:
        doc=json.loads(line)
        doc_id=doc['id']
        meta_dict[doc_id]={
          'title':doc.get('title','untitled'),
          'url':doc.get('url','none'),
          'time':doc.get('time','none'),
          'article':doc.get('article','none'),
          'length':len(re.findall(r'\w+', doc['article']))
        }
    return meta_dict

  def query_process(self, query):
    words=re.findall(r'\w+',query.lower())
    stems=[]
    if self.using_stem:
      stems = [self.stemmer.stem(word) for word in words]
    else:
      stems = words
    processed_stems=[]
    for stem in stems:
      if stem in self.index:
        processed_stems.append(stem)  
    postings=[self.index[stem] for stem in processed_stems]
    if not postings:
      print("no postings found")
      return []
    result=set(postings[0])
    if len(postings)==1:
      return sorted(result)
    for lst in postings[1:]:
      result.intersection_update(lst)
    if not result:
      print("no intersection found")
      return []
    return sorted(result)

    
  def compute_score(self,query):
    '''
    评分基于LUCENE实现：输入query，对于某篇文档
    score(q,d) = coord(q,d) × queryNorm(q) × ∑[tf(t in d) × idf(t)² × t.getBoost() × norm(t,d)]

    词频tf、逆文档频率idf、getboost查询加权（可为某些词增加权重）、norm字段长度与加权、queryNorm(q)归一化、coord协调因子，奖励匹配更多查询词项的文档，例如，查询"信息 检索算法"，某文档匹配前两个词，则coord = 2/3 ≈ 0.667。
    '''
    words = re.findall(r'\w+', query.lower())
    stems = [self.stemmer.stem(word) for word in words] if self.using_stem else words
    valid_terms = [term for term in stems if term in self.index]
    
    if not valid_terms:
        print("no valid terms found")
        return []
    sum_squared = sum((self.idf.get(term, 0.0) ** 2) for term in valid_terms)
    query_norm = 1.0 / math.sqrt(sum_squared) if sum_squared > 0 else 1.0

    contained_docs=self.query_process(query)
    doc_scores=[]
    for doc_id in contained_docs:
      tot_score=0
      matched_terms=0
      # print(self.docs_meta)
      meta=self.docs_meta.get(doc_id,{}) 
      length_norm = 1.0 / math.sqrt(meta.get('length', 1))
      #在候选的文档下遍历query并计算
      for term in valid_terms:
        if doc_id in self.index[term]:
          tf=1
          idf=self.idf.get(term, 0.0)

          boost=1.0 #TODO: 增加权重，这里默认每个词权重相同
          #score(q,d) = coord(q,d) × queryNorm(q) × ∑[tf(t in d) × idf(t)² × t.getBoost() × norm(t,d)]
          term_contrib=tf*idf*idf*boost*length_norm
          tot_score+=term_contrib
          matched_terms+=1
      #计算协调因子
      coord=matched_terms/len(valid_terms) if len(valid_terms)>0 else 0.0

      final_score=coord*query_norm*tot_score
      doc_scores.append((doc_id,final_score))
      top_k=min(self.top_K,len(doc_scores))
    return sorted(doc_scores,key=lambda x:x[1],reverse=True)[:top_k]

class ImageScorer:
  def __init__(self, index_path,idf_path,images_path,using_stem=True,top_K=5):
    self.using_stem = using_stem
    self.stemmer = PorterStemmer() if using_stem else None
    self.top_K = top_K
    self.images_meta=self._load_images_meta(images_path)

    with open(index_path, 'r', encoding='utf-8') as f:
      self.index = json.load(f)

    with open(idf_path, 'r', encoding='utf-8') as f:
      idf_data=json.load(f)
      self.idf = idf_data['idf_values']

  def _load_images_meta(self,images_path):
    meta_dict={}
    with open(images_path, 'r', encoding='utf-8') as f:
      for line in f:
        image=json.loads(line)
        image_id=image['id']
        meta_dict[image_id]={
          'title':image.get('title','untitled'),
          'url':image.get('url','none'),
          'time':image.get('time','none'),
          'relative_path':image.get('relative_path','none')
        }
    return meta_dict
  
  def query_process(self, query):
    words=re.findall(r'\w+',query.lower())
    stems=[]
    if self.using_stem:
      stems = [self.stemmer.stem(word) for word in words]
    else:
      stems = words
    processed_stems=[]
    for stem in stems:
      if stem in self.index:
        processed_stems.append(stem)  
    postings=[self.index[stem] for stem in processed_stems]
    if not postings:
      print("no postings found")
      return []
    result=set(postings[0])
    if len(postings)==1:
      return sorted(result)
    for lst in postings[1:]:
      result.intersection_update(lst)
    if not result:
      print("no intersection found")
      return []
    return sorted(result)
  
  def compute_score(self,query):
    words = re.findall(r'\w+', query.lower())
    stems = [self.stemmer.stem(word) for word in words] if self.using_stem else words
    valid_terms = [term for term in stems if term in self.index]
    
    if not valid_terms:
        print("no valid terms found")
        return []
    sum_squared = sum((self.idf.get(term, 0.0) ** 2) for term in valid_terms)
    query_norm = 1.0 / math.sqrt(sum_squared) if sum_squared > 0 else 1.0

    contained_docs=self.query_process(query)
    doc_scores=[]
    for doc_id in contained_docs:
      tot_score=0
      matched_terms=0
      meta=self.images_meta.get(doc_id,{}) 
      length_norm = 1.0 / math.sqrt(meta.get('length', 1))
      for term in valid_terms:
        if doc_id in self.index[term]:
          tf=1
          idf=self.idf.get(term, 0.0)

          boost=1.0
          term_contrib=tf*idf*idf*boost*length_norm
          tot_score+=term_contrib
          matched_terms+=1
      coord=matched_terms/len(valid_terms) if len(valid_terms)>0 else 0.0

      final_score=coord*query_norm*tot_score
      doc_scores.append((doc_id,final_score))
      top_k=min(self.top_K,len(doc_scores))
    return sorted(doc_scores,key=lambda x:x[1],reverse=True)[:top_k]