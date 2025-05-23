'''
要求：
英文可以直接通过空格分隔。构建基本的倒排索引文件。实现基本的向量空间检索模型的匹配算法。用户查询输入为自然语言字串，查询结果输出按相关度从大到小排序，列出相关度、文档题目、主要匹配内容、URL、文档日期等信息。最好能对检索结果的准确率进行人工评价。界面不做强制要求

'''

'''
TF-IDF(Term Frequency-Inverse Document Frequency, 词频-逆文件频率)是一种用于资讯检索与资讯探勘的常用加权技术。TF-IDF是一种统计方法，用以评估一字词对于一个文件集或一个语料库中的其中一份文件的重要程度。字词的重要性随着它在文件中出现的次数成正比增加，但同时会随着它在语料库中出现的频率成反比下降。

上述引用总结就是, 一个词语在一篇文章中出现次数越多, 同时在所有文档中出现次数越少, 越能够代表该文章。这也就是TF-IDF的含义。

'''
'''
TODO:
后端读入jsonl文件，

评分基于LUCENE实现：输入query，对于某篇文档
score(q,d) = coord(q,d) × queryNorm(q) × ∑[tf(t in d) × idf(t)² × t.getBoost() × norm(t,d)]

使用堆排的TOP-K，需要词频tf、逆文档频率idf、getboost查询加权（可为某些词增加权重）、norm字段长度与加权、queryNorm(q)归一化、coord协调因子，奖励匹配更多查询词项的文档，例如，查询"信息 检索算法"，某文档匹配前两个词，则coord = 2/3 ≈ 0.667。

即拿到一个query，对于每篇文档，计算其score，然后将其加入堆中，取出前K个。这里应该需要维护一个map，存文档id到文档本身的映射，拿到这个id就能在原始数据集中找到标题，url，日期等信息。
还需要一个map维护文档id与标题的映射
主要匹配内容如何获得？——确定文档后，tokenizer+滑动窗口找相似？KMP算法？或者单纯找到相似的部分给他拼一起？

完事之后还可以加一个鲁棒性：对输入先进行纠错再进入

所以需要的模块：
倒排模块：
倒排索引文件，所有文档的全部词都对应一个列表（哪些文档里有这个词），在后面用户输入为多个的时候，把所有用户的词的倒排索引文件拿过来做一个交运算，得到哪些文档是含了所有这些词的（考虑为空的情况，做一个关于索引文件长度的排序，去掉最小的）

TF-IDF模块，计算每个词的tf-idf值，存到文件中（一个字典）

lucene模块：
拿到上面的相关文档集合后，对每个文档计算其score，然后加入堆中，取出前K个。
输出模块：
print

工具模块：
pass
先做后端print，在做前端
'''

import argparse
from outputs import SearchResult
from lucene import LuceneScorer

def main():
  parser = argparse.ArgumentParser(description='Search Engine')
  parser.add_argument('--index_path', type=str, help='path to the index file',default="static_data/inverted_index.json")
  parser.add_argument('--idf_path', type=str, help='path to the idf file',default="static_data/idf_values.json")
  parser.add_argument('--docs_path', type=str, help='path to the documents file',default="text_data/reddit_detailed_id.jsonl")
  parser.add_argument('--top_K',type=int,default=3,help='top K results')
  parser.add_argument('--stem',action='store_true',help='using stemming')
  args = parser.parse_args()

  scorer=LuceneScorer(args.index_path,args.idf_path,args.docs_path,args.stem,args.top_K)
  print("欢迎使用Lucene搜索引擎（输入:q退出）")
  while True:
    try:
      query=input("请输入查询词: ").strip()
      if query=='q':
        break
      results=scorer.compute_score(query)
      print(f"\n找到 {len(results)} 条相关结果：")
      #这里meta_data要在lucene中进一步改
      print(results)
      for rank,(doc_id,score) in enumerate(results,1):
        meta=scorer.docs_meta.get(doc_id,{})

        result=SearchResult(doc_id,score,meta,args.stem)
        print(f"{rank}. {result.get_title()}")
        print(f"  URL: {result.get_url()}")
        print(f"  日期: {result.get_time()}")
        print(f"  相关度: {score:.4f}")
        print(f"  匹配内容: {result.get_article(query)}")

    except KeyboardInterrupt:
      break
    except Exception as e:
      print(f"Error: {e}")

if __name__ == '__main__':
  main()