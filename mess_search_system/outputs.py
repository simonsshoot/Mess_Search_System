import json
import re
from collections import namedtuple
from lucene import LuceneScorer, ImageScorer
from typing import Optional
from nltk.stem import PorterStemmer

class SearchResult:
  def __init__(self,doc_id,score,meta_data,using_stem=True):
    self.doc_id = doc_id
    self.score = score
    self.meta_data = meta_data
    self.using_stem = using_stem
    self.stemmer = PorterStemmer() if using_stem else None
    self._query_terms = set()
    self._original_query = set()
  
  def get_time(self):
    return self.meta_data['time']
  
  def get_title(self):
    return self.meta_data['title']
  
  def get_url(self):
    return self.meta_data['url']
  
  def _process_query(self, query):
    words = re.findall(r'\w+', query.lower())
    if self.using_stem:
      return [self.stemmer.stem(w) for w in words]
    return words
  
  def set_original_query(self, query):
    words = re.findall(r'\w+', query.lower())
    self._original_query = set(words)
  
  def set_query_terms(self, query):
    self._query_terms = set(self._process_query(query))

  # def _highlight_terms(self,text):
  #   #用**包裹关键词，服务于后续前端
  #   if not self._query_terms:
  #     return text
  #   pattern=r'(\b{}\b)'.format('|'.join(map(re.escape, self._query_terms)))
  #   return re.sub(pattern, r'**\1**', text, flags=re.IGNORECASE)
  def _highlight_terms(self, text: str) -> str:
    """使用HTML标签标记关键词"""
    if not self._query_terms:
        return text
        
    #用正则表达式匹配词边界，添加HTML标签
    #这里也可以用词干来高亮，不过感觉效果有点奇怪，比如football会被词干为footbal
    # pattern = r'\b({})\b'.format('|'.join(map(re.escape, self._query_terms)))
    # return re.sub(pattern, 
    #             r'<span style="font-weight: bold; color: #e74c3c;">\1</span>', 
    #             text, 
    #             flags=re.IGNORECASE)
    pattern = r'\b({})\b'.format('|'.join(map(re.escape, self._original_query)))
    return re.sub(pattern, 
                r'<span style="font-weight: bold; color: #e74c3c;">\1</span>', 
                text, 
                flags=re.IGNORECASE)
  
  def get_article(self,query,max_snippet=3,snippet_len=50):
    full_text = self.meta_data['article']
    if not query:
      return (full_text[:snippet_len] + '...') if len(full_text) > snippet_len else full_text
    
    self.set_query_terms(query)
    self.set_original_query(query)
    if not self._query_terms:
      return (full_text[:snippet_len] + '...') if len(full_text) > snippet_len else full_text
    #正则将全文分为句子
    sentences=re.split(r'(?<=[.!?])\s+', full_text)
    relevant_sentences = []
    for sent in sentences:
      sent=sent.lower()
      if any(term in sent for term in self._query_terms):
        highlighted=self._highlight_terms(sent)
        relevant_sentences.append(highlighted)
        if len(relevant_sentences)>=max_snippet:
          break

    if relevant_sentences:
      snippet=[]
      for sent in relevant_sentences:
        # if len(sent)>snippet_len:
          snippet.append(sent)
          print(sent)
      return '+++'.join(snippet)
    else:
      print('No relevant sentences found.')
      return (full_text[:snippet_len] + '...') if len(full_text) > 500 else full_text
  
  def to_dict(self) -> dict:
    """转换为字典格式（用于API响应）"""
    return {
            'doc_id': self.doc_id,
            'score': self.score,
            'title': self.get_title(),
            'time': self.get_time(),
            'url': self.get_url(),
            'snippet': self.get_article()
        }

  def __repr__(self) -> str:
    return f"<SearchResult doc_id={self.doc_id} score={self.score:.3f}>"
  
class ImageResult:
  def __init__(self,image_id,score,meta_data,using_stem=True):
    self.image_id = image_id
    self.score = score
    self.meta_data = meta_data
    self.using_stem = using_stem
    self.stemmer = PorterStemmer() if using_stem else None
    self._query_terms = set()
    self._original_query = set()
  
  def get_title(self,query,max_len=500):
    self.set_query_terms(query)
    self.set_original_query(query)
    full_title = self.meta_data['title']
    if not query:
      return full_title[:max_len]
    highlighted=self._highlight_terms(full_title)
    if(len(highlighted)>max_len):
      highlighted=highlighted[:max_len]+"..."
    return highlighted

  
  def get_url(self):
    return self.meta_data['url']
  
  def get_time(self):
    return self.meta_data['time']
  
  def get_image(self):
    return self.meta_data['relative_path']
  
  def _process_query(self, query):
    words = re.findall(r'\w+', query.lower())
    if self.using_stem:
      return [self.stemmer.stem(w) for w in words]
    return words
  
  def set_original_query(self, query):
    words = re.findall(r'\w+', query.lower())
    self._original_query = set(words)
  
  def set_query_terms(self, query):
    self._query_terms = set(self._process_query(query))

  def _highlight_terms(self, text: str) -> str:
    if not self._query_terms:
        return text
    print(self._original_query)
    pattern = r'\b({})\b'.format('|'.join(map(re.escape, self._original_query)))
    return re.sub(pattern, 
                r'<span style="font-weight: bold; color: #e74c3c;">\1</span>', 
                text, 
                flags=re.IGNORECASE)
  
  def to_dict(self) -> dict:
    return{
        'image_id': self.image_id,
        'score': self.score,
        'title': self.get_title(),
        'url': self.get_url(),
    }
  
  def __repr__(self) -> str:
    return f"<ImageResult image_id={self.image_id} score={self.score:.3f}>"