import json
import re
from collections import defaultdict
from typing import Dict, Set, Union
from nltk.stem import PorterStemmer
import math

class InvertedIndex:
    def __init__(self,using_stem=True):
        self.use_stem = using_stem
        self.stemmer=PorterStemmer() if using_stem else None
        self.inverted_index = defaultdict(set)
        self.tot_docs=0

    def _tokenize(self, text):
        words=re.findall(r'\w+',text.lower())
        if self.use_stem:
            return [self.stemmer.stem(word) for word in words]
        return words
    
    def process_doc(self,doc_id,text):
        #文档中的词添加到倒排文件中
        terms=self._tokenize(text)
        for term in terms:
            self.inverted_index[term].add(doc_id)

    def build_from_file(self,file_path):
        with open(file_path,'r',encoding='utf-8') as f:
            for line_num,line in enumerate(f):
                try:
                    data=json.loads(line.strip())
                    doc_id=data['id']
                    text=data['title']
                    self.process_doc(doc_id,text)
                    self.tot_docs+=1
                except (KeyError,json.JSONDecodeError)as e:
                    print(f"error processing in line {line_num}: {e}")
                    continue
                except Exception as e:
                    print(f"unexpected error in line {line_num}: {e}")
                    continue
    
    def get_index(self):
        #拿到某个词干的文件集合
        return {term:sorted(doc_ids) for term,doc_ids in self.inverted_index.items()}
  
    def save_to_path(self,file_path):
        sorted_index=self.get_index()
        with open(file_path,'w',encoding='utf-8') as f:
            json.dump(sorted_index,f,ensure_ascii=False,indent=2)
    
    def query_process(self,query):
        stems=self._tokenize(query)
        processed_stems=[]
        for stem in stems:
            if stem in self.inverted_index:
                processed_stems.append(stem)
        postings=[self.inverted_index[stem] for stem in processed_stems]
        if not postings:
            return []
        result=set(postings[0])
        for lst in postings[1:]:
            result.intersection_update(lst)
            if not result:
                break
            return sorted(result)
    
    def compute_idf(self,base=math.e):
        if self.tot_docs==0:
            raise ValueError("no document yet")
        idf_values={}
        for term,doc_ids in self.inverted_index.items():
            df=len(doc_ids)
            idf=math.log(self.tot_docs/df)/math.log(base)
            idf_values[term]=idf
        return idf_values
    
    def save_idf_to_path(self,base=math.e,file_path=None):
        idf_data={
            "meta":{
                "total_docs":self.tot_docs,
                "idf_base":base
            },
            "idf_values":self.compute_idf(base)
        }
        with open(file_path,'w',encoding='utf-8') as f:
            json.dump(idf_data,f,ensure_ascii=False,indent=2)
                

if __name__ == '__main__':
    index_builder = InvertedIndex(using_stem=True)
    index_builder.build_from_file('text_data/reddit_detailed_id.jsonl')
    index_builder.save_to_path('static_data/inverted_index.json')
    print("success in building index.")
    index_builder.save_idf_to_path(file_path='static_data/idf_values.json')
    print("success in computing idf values.")
    # index_builder.build_from_file(r'C:\Users\admin\Desktop\信息检索系统\mess_search_system\version_data_large\tmp-1\final_detailed.jsonl')
    # index_builder.save_to_path('static_data/inverted_index_version_large.json')
    # print("success in building index.")
    # index_builder.save_idf_to_path(file_path='static_data/idf_values_version_large.json')
    # print("success in computing idf values.")