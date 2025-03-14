import os

def convert_encoding(folder_path):
    """转换目录下所有txt文件编码格式（GBK -> UTF-8）"""
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                try:
                    # 使用GBK编码读取文件
                    with open(file_path, 'r', encoding='gbk', errors='ignore') as f:
                        content = f.read()
                    
                    # 使用UTF-8编码覆盖写入原文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"成功转换：{file_path}")
                except Exception as e:
                    print(f"处理 {file_path} 时出错：{str(e)}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    convert_encoding(current_dir)
