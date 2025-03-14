import json
import os
import re
from collections import Counter
from pypinyin import lazy_pinyin, Style
import sys


# 设置控制台输出编码（解决中文输出乱码问题）
if sys.platform.startswith('win'):
    # Windows系统需要设置控制台编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def build_frequency_tables(input_dir, output_1word, output_2word):
    # 初始化计数器
    char_counter = Counter()
    bigram_counter = Counter()
    hanzi_pattern = re.compile(r'[\u4e00-\u9fa5]')  # 汉字正则匹配

    # 获取所有txt文件
    txt_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    news_count = 0  # 新闻条数计数器
    
    for file_name in txt_files:
        file_path = os.path.join(input_dir, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    text = data['title'] + data['html']
                    chars = hanzi_pattern.findall(text)  # 提取汉字
                    
                    # 更新单字计数
                    char_counter.update(chars)
                    
                    # 更新二元组计数
                    for i in range(len(chars)-1):
                        bigram = chars[i] + chars[i+1]
                        bigram_counter[bigram] += 1
                    
                    news_count += 1  # 处理成功时计数
                    if news_count % 20 == 0:  # 每20条报告一次
                        print(f"已处理 {news_count} 条新闻")
                except:
                    continue

    # 构建一元词频表
    print("开始构建一元词频表...")
    total_chars = len(char_counter)
    processed_chars = 0
    pinyin_1word = {}
    for char, count in char_counter.items():
        try:
            py = lazy_pinyin(char, style=Style.NORMAL)[0]  # 取第一个读音
        except IndexError:
            continue
        
        if py not in pinyin_1word:
            pinyin_1word[py] = {"words": [], "counts": []}
        
        # 插入并保持排序（按出现频率降序）
        inserted = False
        for i in range(len(pinyin_1word[py]["counts"])):
            if count > pinyin_1word[py]["counts"][i]:
                pinyin_1word[py]["words"].insert(i, char)
                pinyin_1word[py]["counts"].insert(i, count)
                inserted = True
                break
        if not inserted:
            pinyin_1word[py]["words"].append(char)
            pinyin_1word[py]["counts"].append(count)
        
        processed_chars += 1
        if processed_chars % 1000 == 0:  # 每处理1000个字符报告一次
            progress = processed_chars / total_chars * 100
            print(f"一元表构建进度: {progress:.1f}% ({processed_chars}/{total_chars})")

    # 构建二元词频表
    print("\n开始构建二元词频表...")
    total_bigrams = len(bigram_counter)
    processed_bigrams = 0
    pinyin_2word = {}
    for bigram, count in bigram_counter.items():
        char1, char2 = bigram[0], bigram[1]
        try:
            py1 = lazy_pinyin(char1, style=Style.NORMAL)[0]
            py2 = lazy_pinyin(char2, style=Style.NORMAL)[0]
        except IndexError:
            continue
        
        py_key = f"{py1} {py2}"
        chars_key = f"{char1} {char2}"
        
        if py_key not in pinyin_2word:
            pinyin_2word[py_key] = {"words": [], "counts": []}
        
        # 插入并保持排序
        inserted = False
        for i in range(len(pinyin_2word[py_key]["counts"])):
            if count > pinyin_2word[py_key]["counts"][i]:
                pinyin_2word[py_key]["words"].insert(i, chars_key)
                pinyin_2word[py_key]["counts"].insert(i, count)
                inserted = True
                break
        if not inserted:
            pinyin_2word[py_key]["words"].append(chars_key)
            pinyin_2word[py_key]["counts"].append(count)
        
        processed_bigrams += 1
        if processed_bigrams % 1000 == 0:  # 每处理1000个二元组报告一次
            progress = processed_bigrams / total_bigrams * 100
            print(f"二元表构建进度: {progress:.1f}% ({processed_bigrams}/{total_bigrams})")

    print("\n开始写入文件...")

    # 写入文件
    with open(output_1word, 'w', encoding='utf-8') as f1, \
         open(output_2word, 'w', encoding='utf-8') as f2:
        
        json.dump(pinyin_1word, f1, ensure_ascii=False, indent=2)
        json.dump(pinyin_2word, f2, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    build_frequency_tables(
        input_dir='Training/sina_news_gbk',
        output_1word='1_word.txt',
        output_2word='2_word.txt'
    )

