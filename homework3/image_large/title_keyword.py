import json
import re
import spacy
from collections import defaultdict, Counter
import os

# 加载spaCy英文模型
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    print("请安装spaCy英文模型: python -m spacy download en_core_web_lg")
    exit(1)

def load_jsonl(file_path):
    """加载JSONL文件"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line.strip()))
    return data

def save_jsonl(data, file_path):
    """保存JSONL文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def load_keywords(file_path):
    """加载关键词库"""
    keywords = set()
    data = load_jsonl(file_path)
    for item in data:
        keywords.add(item['name'].lower())
    return keywords

def extract_internet_slang(text, slang_keywords):
    """提取网络流行语"""
    slangs = []
    text_lower = text.lower()
    
    for slang in slang_keywords:
        # 网络流行语匹配，保持原格式
        pattern = r'\b' + re.escape(slang) + r'\b'
        if re.search(pattern, text_lower, re.IGNORECASE):
            # 查找原文中的实际格式
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                slangs.append(match.group())
    
    return list(set(slangs))

def extract_green_sustainability(text):
    """提取环境和社会可持续发展相关信息"""
    green_keywords = []
    text_lower = text.lower()
    
    # 环境关键词库
    environmental_keywords = {
        # 环境保护
        'sustainability', 'sustainable', 'environmentally friendly', 'eco-friendly', 'green',
        'renewable energy', 'solar power', 'wind power', 'clean energy', 'carbon neutral',
        'carbon footprint', 'greenhouse gas', 'emissions', 'pollution', 'contamination',
        'recycling', 'renewable', 'biodegradable', 'organic', 'natural',
        
        # 气候变化
        'climate change', 'global warming', 'carbon dioxide', 'co2', 'methane',
        'deforestation', 'forest conservation', 'reforestation', 'afforestation',
        'ocean acidification', 'sea level rise', 'extreme weather',
        
        # 社会可持续性
        'social responsibility', 'corporate social responsibility', 'csr', 'fair trade',
        'ethical sourcing', 'labor rights', 'human rights', 'social justice',
        'community development', 'social impact', 'stakeholder', 'transparency',
        'accountability', 'governance', 'diversity', 'inclusion', 'equity',
        
        # 循环经济
        'circular economy', 'waste reduction', 'zero waste', 'upcycling', 'downcycling',
        'life cycle assessment', 'cradle to cradle', 'reduce reuse recycle',
        
        # 可持续发展目标
        'sdg', 'sustainable development goals', 'un goals', 'millennium development goals',
        'poverty reduction', 'hunger', 'health and wellbeing', 'quality education',
        'gender equality', 'clean water', 'sanitation', 'affordable energy',
        
        # 生物多样性和生态
        'biodiversity', 'ecosystem', 'conservation', 'endangered species', 'wildlife protection',
        'habitat destruction', 'ecological footprint', 'natural resources', 'overfishing',
        'plastic pollution', 'microplastics',
        
        # 绿色技术和创新
        'green technology', 'cleantech', 'electric vehicle', 'ev', 'hybrid',
        'energy efficiency', 'smart grid', 'green building', 'leed certification',
        'carbon capture', 'green chemistry', 'biomimicry',
        
        # 可持续商业
        'b corporation', 'benefit corporation', 'triple bottom line', 'esg',
        'environmental social governance', 'impact investing', 'green finance',
        'sustainable supply chain', 'ethical consumption', 'conscious consumerism'
    }
    
    # 多词短语的特殊处理
    multi_word_phrases = [
        'climate change', 'global warming', 'renewable energy', 'solar power', 'wind power',
        'clean energy', 'carbon neutral', 'carbon footprint', 'greenhouse gas',
        'environmentally friendly', 'eco-friendly', 'social responsibility',
        'corporate social responsibility', 'fair trade', 'ethical sourcing',
        'labor rights', 'human rights', 'social justice', 'community development',
        'social impact', 'circular economy', 'waste reduction', 'zero waste',
        'life cycle assessment', 'cradle to cradle', 'reduce reuse recycle',
        'sustainable development goals', 'millennium development goals',
        'poverty reduction', 'health and wellbeing', 'quality education',
        'gender equality', 'clean water', 'affordable energy', 'endangered species',
        'wildlife protection', 'habitat destruction', 'ecological footprint',
        'natural resources', 'plastic pollution', 'green technology',
        'electric vehicle', 'energy efficiency', 'smart grid', 'green building',
        'leed certification', 'carbon capture', 'green chemistry',
        'b corporation', 'benefit corporation', 'triple bottom line',
        'environmental social governance', 'impact investing', 'green finance',
        'sustainable supply chain', 'ethical consumption', 'conscious consumerism',
        'sea level rise', 'extreme weather', 'ocean acidification', 'forest conservation'
    ]
    
    # 首先检查多词短语
    for phrase in multi_word_phrases:
        pattern = r'\b' + re.escape(phrase) + r'\b'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            green_keywords.append(match.group())
    
    # 然后检查单词关键词（避免重复）
    words = re.findall(r'\b\w+\b', text_lower)
    for word in words:
        if word in environmental_keywords:
            # 检查是否已经被多词短语包含
            already_found = False
            for existing in green_keywords:
                if word in existing.lower():
                    already_found = True
                    break
            if not already_found:
                # 查找原文中的实际格式
                pattern = r'\b' + re.escape(word) + r'\b'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    green_keywords.append(match.group())
                    break  # 只添加第一个匹配
    
    return list(set(green_keywords))

def extract_green_sustainability(text):
    """提取环境和社会可持续发展相关信息"""
    green_keywords = []
    text_lower = text.lower()
    
    # 环境关键词库
    environmental_keywords = {
        # 环境保护
        'sustainability', 'sustainable', 'environmentally friendly', 'eco-friendly', 'green',
        'renewable energy', 'solar power', 'wind power', 'clean energy', 'carbon neutral',
        'carbon footprint', 'greenhouse gas', 'emissions', 'pollution', 'contamination',
        'recycling', 'renewable', 'biodegradable', 'organic', 'natural',
        
        # 气候变化
        'climate change', 'global warming', 'carbon dioxide', 'co2', 'methane',
        'deforestation', 'forest conservation', 'reforestation', 'afforestation',
        'ocean acidification', 'sea level rise', 'extreme weather',
        
        # 社会可持续性
        'social responsibility', 'corporate social responsibility', 'csr', 'fair trade',
        'ethical sourcing', 'labor rights', 'human rights', 'social justice',
        'community development', 'social impact', 'stakeholder', 'transparency',
        'accountability', 'governance', 'diversity', 'inclusion', 'equity',
        
        # 循环经济
        'circular economy', 'waste reduction', 'zero waste', 'upcycling', 'downcycling',
        'life cycle assessment', 'cradle to cradle', 'reduce reuse recycle',
        
        # 可持续发展目标
        'sdg', 'sustainable development goals', 'un goals', 'millennium development goals',
        'poverty reduction', 'hunger', 'health and wellbeing', 'quality education',
        'gender equality', 'clean water', 'sanitation', 'affordable energy',
        
        # 生物多样性和生态
        'biodiversity', 'ecosystem', 'conservation', 'endangered species', 'wildlife protection',
        'habitat destruction', 'ecological footprint', 'natural resources', 'overfishing',
        'plastic pollution', 'microplastics',
        
        # 绿色技术和创新
        'green technology', 'cleantech', 'electric vehicle', 'ev', 'hybrid',
        'energy efficiency', 'smart grid', 'green building', 'leed certification',
        'carbon capture', 'green chemistry', 'biomimicry',
        
        # 可持续商业
        'b corporation', 'benefit corporation', 'triple bottom line', 'esg',
        'environmental social governance', 'impact investing', 'green finance',
        'sustainable supply chain', 'ethical consumption', 'conscious consumerism'
    }
    
    # 多词短语的特殊处理
    multi_word_phrases = [
        'climate change', 'global warming', 'renewable energy', 'solar power', 'wind power',
        'clean energy', 'carbon neutral', 'carbon footprint', 'greenhouse gas',
        'environmentally friendly', 'eco-friendly', 'social responsibility',
        'corporate social responsibility', 'fair trade', 'ethical sourcing',
        'labor rights', 'human rights', 'social justice', 'community development',
        'social impact', 'circular economy', 'waste reduction', 'zero waste',
        'life cycle assessment', 'cradle to cradle', 'reduce reuse recycle',
        'sustainable development goals', 'millennium development goals',
        'poverty reduction', 'health and wellbeing', 'quality education',
        'gender equality', 'clean water', 'affordable energy', 'endangered species',
        'wildlife protection', 'habitat destruction', 'ecological footprint',
        'natural resources', 'plastic pollution', 'green technology',
        'electric vehicle', 'energy efficiency', 'smart grid', 'green building',
        'leed certification', 'carbon capture', 'green chemistry',
        'b corporation', 'benefit corporation', 'triple bottom line',
        'environmental social governance', 'impact investing', 'green finance',
        'sustainable supply chain', 'ethical consumption', 'conscious consumerism',
        'sea level rise', 'extreme weather', 'ocean acidification', 'forest conservation'
    ]
    
    # 首先检查多词短语
    for phrase in multi_word_phrases:
        pattern = r'\b' + re.escape(phrase) + r'\b'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            green_keywords.append(match.group())
    
    # 然后检查单词关键词（避免重复）
    words = re.findall(r'\b\w+\b', text_lower)
    for word in words:
        if word in environmental_keywords:
            # 检查是否已经被多词短语包含
            already_found = False
            for existing in green_keywords:
                if word in existing.lower():
                    already_found = True
                    break
            if not already_found:
                # 查找原文中的实际格式
                pattern = r'\b' + re.escape(word) + r'\b'
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    green_keywords.append(match.group())
                    break  # 只添加第一个匹配
    
    return list(set(green_keywords))

def is_url_related(text):
    """检查是否包含URL相关内容"""
    return 'https://' in text or 'http://' in text or 'www.' in text or '.com' in text

def extract_nlp_entities(text):
    """使用NLP提取实体信息"""
    doc = nlp(text)
    
    organizations = []
    persons = []
    locations = []
    
    for ent in doc.ents:
        # 过滤掉包含URL的实体
        if is_url_related(ent.text):
            continue
        
        # 过滤掉过短或过长的实体
        if len(ent.text.strip()) < 2 or len(ent.text.strip()) > 50:
            continue
            
        # 过滤掉纯数字或特殊字符
        if re.match(r'^[\d\W]+$', ent.text.strip()):
            continue
            
        if ent.label_ == "ORG":
            organizations.append(ent.text.strip())
        elif ent.label_ == "PERSON":
            persons.append(ent.text.strip())
        elif ent.label_ in ["GPE", "LOC"] :  # GPE: 地缘政治实体, LOC: 地点
            locations.append(ent.text.strip())
    
    return list(set(organizations)), list(set(persons)), list(set(locations))

def analyze_sentiment(text):
    """情感分析"""
    # 积极词汇（扩展词汇表）
    positive_words = {
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 
        'love', 'like', 'happy', 'glad', 'pleased', 'satisfied', 'perfect', 'best',
        'brilliant', 'outstanding', 'superb', 'magnificent', 'incredible', 'marvelous',
        'delighted', 'thrilled', 'excited', 'positive', 'optimistic', 'hopeful',
        'beautiful', 'nice', 'cool', 'fun', 'enjoy', 'impressive', 'remarkable',
        'successful', 'victory', 'win', 'winner', 'celebrate', 'congratulations'
    }
    
    # 消极词汇（扩展词汇表）
    negative_words = {
        'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate', 'dislike',
        'sad', 'angry', 'upset', 'disappointed', 'frustrated', 'annoyed', 'worst',
        'pathetic', 'useless', 'stupid', 'ridiculous', 'annoying', 'irritating',
        'depressed', 'worried', 'concerned', 'negative', 'pessimistic', 'hopeless',
        'fail', 'failure', 'lose', 'loser', 'problem', 'issue', 'trouble', 'crisis',
        'disaster', 'nightmare', 'boring', 'suck', 'sucks', 'wrong', 'mistake'
    }
    
    # 预处理文本，转为小写并提取单词
    words = re.findall(r'\b\w+\b', text.lower())
    
    # 计算积极和消极词汇的数量
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    # 考虑感叹号和问号的影响
    exclamation_count = text.count('!')
    question_count = text.count('?')
    
    # 调整权重
    positive_score = positive_count + exclamation_count * 0.1
    negative_score = negative_count
    
    # 判断情感
    threshold = 0.5  # 设置阈值
    if positive_score > negative_score + threshold:
        return "积极"
    elif negative_score > positive_score + threshold:
        return "消极"
    else:
        return "中立"

def filter_organizations(organizations, locations, persons):
    """过滤组织名称，剔除地区名和人名"""
    filtered_orgs = []
    
    # 将地区名和人名转为小写集合以便比较
    location_set = {loc.lower() for loc in locations}
    person_set = {person.lower() for person in persons}
    
    for org in organizations:
        org_lower = org.lower()
        # 如果组织名不在地区名和人名中，则保留
        if org_lower not in location_set and org_lower not in person_set:
            filtered_orgs.append(org)
    
    return filtered_orgs

def process_articles():
    """处理文章数据"""
    # 加载数据
    print("加载数据...")
    articles = load_jsonl('image_large/final_detailed.jsonl')
    slang_keywords = load_keywords('InternetSlang/Internet_slang.jsonl')  # 网络流行语关键词
    
    print(f"共加载 {len(articles)} 篇文章")
    print(f"网络流行语关键词: {len(slang_keywords)} 个")
    
    # 统计信息 - 使用字典记录计数和ID列表
    statistics = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'ids': []}))
    
    # 处理每篇文章
    for i, article in enumerate(articles):
        if i % 100 == 0:
            print(f"处理进度: {i}/{len(articles)}")
        
        # 获取文章ID，如果没有则使用索引
        article_id = article.get('id', str(i))
        
        text = article.get('title', '')
        if not text:
            # 如果没有文章内容，设置空字段
            article['key_area'] = []
            article['key_organization'] = []
            article['key_name'] = []
            article['key_internet_slang'] = []
            article['key_Green'] = []
            article['key_feeling'] = "中立"
            article['Good'] = 0
            article['Bad'] = 0
            
            # 记录中立情感的ID
            statistics['key_feeling']["中立"]['count'] += 1
            statistics['key_feeling']["中立"]['ids'].append(article_id)
            continue
        
        # 1. 使用NLP提取组织、人名和地点
        nlp_orgs, nlp_persons, nlp_locations = extract_nlp_entities(text)
        
        # 2. 过滤组织名称，剔除地区名和人名
        filtered_organizations = filter_organizations(nlp_orgs, nlp_locations, nlp_persons)
        
        # 3. 提取网络流行语
        internet_slangs = extract_internet_slang(text, slang_keywords)
        
        # 4. 提取环境和社会可持续发展相关信息
        green_sustainability = extract_green_sustainability(text)
        
        # 5. 情感分析
        sentiment = analyze_sentiment(text)
        
        # 更新文章信息
        article['key_area'] = nlp_locations  # 直接使用NLP提取的地理位置
        article['key_organization'] = filtered_organizations
        article['key_name'] = nlp_persons
        article['key_internet_slang'] = internet_slangs
        article['key_Green'] = green_sustainability
        article['key_feeling'] = sentiment
        article['Good'] = 0
        article['Bad'] = 0
        
        # 更新统计信息，同时记录ID
        for area in nlp_locations:
            statistics['key_area'][area]['count'] += 1
            statistics['key_area'][area]['ids'].append(article_id)
        
        for org in filtered_organizations:
            statistics['key_organization'][org]['count'] += 1
            statistics['key_organization'][org]['ids'].append(article_id)
        
        for person in nlp_persons:
            statistics['key_name'][person]['count'] += 1
            statistics['key_name'][person]['ids'].append(article_id)
        
        for slang in internet_slangs:
            statistics['key_internet_slang'][slang]['count'] += 1
            statistics['key_internet_slang'][slang]['ids'].append(article_id)
        
        for green_item in green_sustainability:
            statistics['key_Green'][green_item]['count'] += 1
            statistics['key_Green'][green_item]['ids'].append(article_id)
        
        statistics['key_feeling'][sentiment]['count'] += 1
        statistics['key_feeling'][sentiment]['ids'].append(article_id)
    
    return articles, statistics

def save_statistics(statistics):
    """保存统计信息"""
    stats_list = []
    
    for category, items in statistics.items():
        for item, data in items.items():
            stats_list.append({
                "信息点类名": category,
                "信息点具体名称": item,
                "具体数目": data['count'],
                "包含文章ID列表": data['ids']
            })
    
    # 按类别和数量排序
    stats_list.sort(key=lambda x: (x["信息点类名"], -x["具体数目"]))
    
    save_jsonl(stats_list, 'image_large/title_statistics_report.jsonl')
    
    # 打印详细统计报告
    print("\n=== 详细统计报告 ===")
    
    category_names = {
        'key_area': '地理位置',
        'key_organization': '组织机构',
        'key_name': '人名',
        'key_internet_slang': '网络流行语',
        'key_Green': '环境和社会可持续发展',
        'key_feeling': '情感分析'
    }
    
    for category in ['key_area', 'key_organization', 'key_name', 'key_internet_slang', 'key_Green', 'key_feeling']:
        if category in statistics:
            total = sum(data['count'] for data in statistics[category].values())
            unique = len(statistics[category])
            print(f"\n{category_names.get(category, category)}:")
            print(f"  总实例数: {total}")
            print(f"  唯一项数: {unique}")
            
            # 显示前10个最常见的项目
            top_items = sorted(statistics[category].items(), 
                             key=lambda x: x[1]['count'], reverse=True)[:10]
            print("  Top 10:")
            for j, (item, data) in enumerate(top_items, 1):
                # 显示前5个ID作为示例
                id_sample = data['ids'][:5]
                if len(data['ids']) > 5:
                    id_display = f"{id_sample}... (共{len(data['ids'])}个)"
                else:
                    id_display = str(data['ids'])
                print(f"    {j:2d}. {item}: {data['count']} 次 - ID示例: {id_display}")

def main():
    """主函数"""
    print("开始处理Reddit信息抽取...")
    
    # 检查输入文件是否存在
    required_files = [
        'image_large/final_detailed.jsonl',
        'InternetSlang/Internet_slang.jsonl'  # 网络流行语关键词文件
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"错误: 找不到文件 {file_path}")
            return
    
    try:
        # 处理文章
        processed_articles, statistics = process_articles()
        
        # 保存处理后的文章
        print("\n保存处理后的文章...")
        save_jsonl(processed_articles, 'image_large/title_keyword.jsonl')
        
        # 保存统计信息
        print("保存统计信息...")
        save_statistics(statistics)
        
        print("\n处理完成!")
        print(f"处理结果保存在: image_large/title_keyword.jsonl")
        print(f"统计报告保存在: image_large/title_statistics_report.jsonl")
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()