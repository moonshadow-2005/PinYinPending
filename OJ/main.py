# -*- coding: utf-8 -*-
import json
import sys
import math
import os

if sys.platform.startswith('win'):
    # Windows系统需要设置控制台编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 添加文件校验
if not os.path.isfile('./1_word.txt'):
    print("错误：1_word.txt 文件未找到", file=sys.stderr)
    sys.exit(1)

# 预处理一元词频表为字典结构
with open('./1_word.txt', 'r', encoding='utf-8') as f:
    one_gram = json.load(f)
one_gram_dict = {
    pinyin: dict(zip(data['words'], data['counts']))
    for pinyin, data in one_gram.items()
}

# 预处理二元词频表为嵌套字典结构
with open('./2_word.txt', 'r', encoding='utf-8') as f:
    two_gram = json.load(f)
two_gram_dict = {}
for bigram_key, data in two_gram.items():
    inner_dict = {}
    for pair, count in zip(data['words'], data['counts']):
        w1, w2 = pair.split()
        inner_dict.setdefault(w1, {})[w2] = count
    two_gram_dict[bigram_key] = inner_dict

# 在文件开头添加常量定义
MIN_PROB = -1e20  # 极小值代替负无穷
LM_WEIGHT = 1.5  # 语言模型权重
BEAM_WIDTH = 50  # 根据实际情况调整

def process_pinyin(pinyin_list):
    if not pinyin_list:
        return ""
    
    # 初始化动态规划表
    dp = [{} for _ in range(len(pinyin_list))]
    
    # 每个位置存储格式：{汉字: (累计对数概率, 前驱汉字)}
    
    # 处理第一个拼音时添加默认候选
    first_pinyin = pinyin_list[0]
    candidates = one_gram_dict.get(first_pinyin, {})
    if not candidates:
        # 添加拼音对应的常见字（示例数据，需完善）
        default_candidates = {'ni': '你', 'hao': '好', 'de': '的'}  # 应扩展为完整列表
        candidates = {default_candidates.get(first_pinyin, '?'): 1}
    
    for word, count in candidates.items():
        dp[0][word] = (math.log(count), None)
    
    # 处理后续拼音
    for i in range(1, len(pinyin_list)):
        current_pinyin = pinyin_list[i]
        prev_pinyin = pinyin_list[i-1]
        bigram_key = f"{prev_pinyin} {current_pinyin}"
        bigram_data = two_gram_dict.get(bigram_key, {})
        
        for current_word, one_count in one_gram_dict.get(current_pinyin, {}).items():
            max_prob = -math.inf
            best_prev = None
            
            # 遍历前一个状态的所有可能
            for prev_word, (prev_log_prob, _) in dp[i-1].items():
                # 计算转移概率（核心公式）
                transition = bigram_data.get(prev_word, {}).get(current_word, 0)
                
                # 改进后的平滑处理：加入拉普拉斯平滑
                alpha = 0.1  # 平滑系数
                if transition:
                    current_prob = prev_log_prob + LM_WEIGHT * math.log(transition)
                else:
                    # 回退机制改进：考虑前词的一元概率
                    prev_word_count = sum(one_gram_dict.get(prev_pinyin, {}).values()) or 1
                    current_prob = prev_log_prob + math.log((one_count + alpha) / (prev_word_count + alpha * len(one_gram_dict)))
                
                # 加入权重平衡（可调整参数）
                lambda_factor = 0.7  # 二元模型权重
                current_prob = lambda_factor * current_prob + (1 - lambda_factor) * math.log(one_count)
                
                # 确保概率不低于下限
                current_prob = max(current_prob, MIN_PROB)
                
                if current_prob > max_prob:
                    max_prob = current_prob
                    best_prev = prev_word
            
            dp[i][current_word] = (max_prob, best_prev)
        
        # 添加剪枝逻辑
        dp[i] = dict(sorted(dp[i].items(), key=lambda x: x[1][0], reverse=True)[:BEAM_WIDTH])
    
    # 回溯构建最优路径
    if not dp[-1]:
        return ""
    
    path = []
    current_word = max(dp[-1].items(), key=lambda x: x[1][0])[0]
    for i in reversed(range(len(dp))):
        path.append(current_word)
        current_word = dp[i].get(current_word, (0, None))[1]
        # 处理中间断链情况
        if current_word is None and i > 0:
            # 选择前一个位置的最大概率词
            current_word = max(dp[i-1].items(), key=lambda x: x[1][0])[0] if dp[i-1] else '?'
    
    return ''.join(reversed(path))

# 主程序
for line in sys.stdin:
    pinyin_line = line.strip().split()
    print(process_pinyin(pinyin_line))

