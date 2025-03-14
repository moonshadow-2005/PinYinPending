import os
import re
import random
import subprocess
from pypinyin import pinyin, Style
import sys

if sys.platform.startswith('win'):
    # Windows系统需要设置控制台编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 添加文件校验

def extract_sentences(directory):
    sentences = []
    punc_pattern = re.compile(r'[，。！？；、]')
    chinese_pattern = re.compile(r'^[\u4e00-\u9fa5]+$')
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    segments = punc_pattern.split(content)
                    for seg in segments:
                        seg = seg.strip()
                        if len(seg) >= 4 and chinese_pattern.match(seg):
                            sentences.append(seg)
    return sentences

def convert_to_pinyin(sentence):
    return ' '.join([p[0] for p in pinyin(sentence, style=Style.NORMAL)])

def calculate_accuracy(ans_path, output_path):
    with open(ans_path, 'r', encoding='utf-8') as f_ans, \
         open(output_path, 'r', encoding='utf-8') as f_out:
        ans_lines = f_ans.readlines()
        out_lines = f_out.readlines()
        
        total_sentences = len(ans_lines)
        correct_sentences = 0
        total_chars = 0
        correct_chars = 0
        
        for ans, out in zip(ans_lines, out_lines):
            ans = ans.strip()
            out = out.strip()
            if ans == out:
                correct_sentences += 1
            min_len = min(len(ans), len(out))
            total_chars += min_len
            correct_chars += sum(a == o for a, o in zip(ans[:min_len], out[:min_len]))
        
        sentence_acc = correct_sentences / total_sentences * 100
        char_acc = correct_chars / total_chars * 100 if total_chars > 0 else 0
        
        return sentence_acc, char_acc

def main():
    # 步骤1：提取训练数据中的句子
    sentences = extract_sentences('Training/sina_news_gbk')
    selected = random.sample(sentences, 1000)
    
    # 步骤2：生成答案文件
    with open('output_ans.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(selected))
    
    # 步骤3：生成拼音输入文件
    with open('input.txt', 'w', encoding='utf-8') as f:
        for s in selected:
            f.write(convert_to_pinyin(s) + '\n')
    
    # 步骤4：运行被测程序
    with open('input.txt', 'r', encoding='utf-8') as fin, \
         open('output.txt', 'w', encoding='utf-8') as fout:
        subprocess.run(['python', 'OJ/main.py'], stdin=fin, stdout=fout)
    
    # 步骤5：计算准确率
    sentence_acc, char_acc = calculate_accuracy('output_ans.txt', 'output.txt')
    
    print(f'句准确率：{sentence_acc:.2f}%')
    print(f'字准确率：{char_acc:.2f}%')

if __name__ == '__main__':
    main() 