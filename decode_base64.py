import base64
import zlib
import re
import io
import sys
from itertools import product
import binascii

# 这是我的第一次修改
# 这时我的第二次修改


def try_decode_base64(encoded_str):
    """尝试多种方式解码base64字符串"""
    results = []
    encodings = ['utf-8', 'ascii', 'latin-1', 'gbk', 'gb18030']
    
    # 确保有正确的填充
    padding_fixed = encoded_str + "=" * ((4 - len(encoded_str) % 4) % 4)
    
    # 1. 尝试标准base64解码
    try:
        decoded = base64.b64decode(padding_fixed)
        
        # 尝试不同编码解析
        for enc in encodings:
            try:
                text = decoded.decode(enc)
                if any(c.isprintable() and not c.isspace() for c in text):
                    results.append((f'标准Base64 + {enc}', text[:200]))
            except:
                pass
        
        # 尝试zlib解压缩
        try:
            decompressed = zlib.decompress(decoded)
            for enc in encodings:
                try:
                    text = decompressed.decode(enc)
                    if any(c.isprintable() and not c.isspace() for c in text):
                        results.append((f'Base64 + zlib + {enc}', text[:200]))
                except:
                    pass
        except:
            pass
    except:
        pass
        
    # 2. 尝试URL安全的base64变体
    try:
        url_safe = padding_fixed.replace('-', '+').replace('_', '/')
        decoded = base64.b64decode(url_safe)
        
        for enc in encodings:
            try:
                text = decoded.decode(enc)
                if any(c.isprintable() and not c.isspace() for c in text):
                    results.append((f'URL安全Base64 + {enc}', text[:200]))
            except:
                pass
    except:
        pass
    
    # 3. 尝试去除可能干扰的字符
    try:
        cleaned = re.sub(r'[^A-Za-z0-9+/=]', '', encoded_str)
        cleaned = cleaned + "=" * ((4 - len(cleaned) % 4) % 4)
        if cleaned != padding_fixed:
            decoded = base64.b64decode(cleaned)
            for enc in encodings:
                try:
                    text = decoded.decode(enc)
                    if any(c.isprintable() and not c.isspace() for c in text):
                        results.append((f'清理后Base64 + {enc}', text[:200]))
                except:
                    pass
    except:
        pass
    
    # 4. 尝试处理可能的XOR加密
    try:
        # 尝试简单的XOR解密 (常用密钥)
        common_xor_keys = [1, 2, 13, 42, 0xFF]
        decoded = base64.b64decode(padding_fixed)
        
        for key in common_xor_keys:
            xor_decoded = bytes(b ^ key for b in decoded)
            for enc in encodings:
                try:
                    text = xor_decoded.decode(enc)
                    if any(c.isprintable() and not c.isspace() for c in text):
                        results.append((f'Base64 + XOR({key}) + {enc}', text[:200]))
                except:
                    pass
    except:
        pass
    
    # 5. 尝试处理特殊分隔符情况 - 有时base64编码会被分割成块
    try:
        # 去除所有空白字符
        no_spaces = re.sub(r'\s', '', encoded_str)
        if no_spaces != encoded_str:
            no_spaces = no_spaces + "=" * ((4 - len(no_spaces) % 4) % 4)
            decoded = base64.b64decode(no_spaces)
            
            for enc in encodings:
                try:
                    text = decoded.decode(enc)
                    if any(c.isprintable() and not c.isspace() for c in text):
                        results.append((f'去空格Base64 + {enc}', text[:200]))
                except:
                    pass
    except:
        pass
    
    # 6. 尝试反转base64字符串 (有时编码是反向的)
    try:
        reversed_str = encoded_str[::-1]
        reversed_str = reversed_str + "=" * ((4 - len(reversed_str) % 4) % 4)
        decoded = base64.b64decode(reversed_str)
        
        for enc in encodings:
            try:
                text = decoded.decode(enc)
                if any(c.isprintable() and not c.isspace() for c in text):
                    results.append((f'反向Base64 + {enc}', text[:200]))
            except:
                pass
    except:
        pass
    
    # 7. 尝试双重base64解码
    try:
        decoded = base64.b64decode(padding_fixed)
        # 检查解码结果是否还是base64
        if re.match(r'^[A-Za-z0-9+/=\s]+$', decoded.decode('ascii', errors='ignore')):
            inner_decoded = base64.b64decode(decoded)
            for enc in encodings:
                try:
                    text = inner_decoded.decode(enc)
                    if any(c.isprintable() and not c.isspace() for c in text):
                        results.append((f'双重Base64 + {enc}', text[:200]))
                except:
                    pass
    except:
        pass
    
    return results

def try_split_and_decode(encoded_str):
    """尝试按不同的分隔方式解码"""
    results = []
    
    # 尝试按特定长度切分字符串
    chunk_sizes = [4, 8, 16, 32, 64]
    encodings = ['utf-8', 'ascii', 'latin-1', 'gbk', 'gb18030']
    
    for size in chunk_sizes:
        if len(encoded_str) % size == 0:
            chunks = [encoded_str[i:i+size] for i in range(0, len(encoded_str), size)]
            
            # 尝试解码每一块
            decoded_chunks = []
            valid = True
            
            for chunk in chunks:
                try:
                    # 确保填充正确
                    padded_chunk = chunk + "=" * ((4 - len(chunk) % 4) % 4)
                    decoded = base64.b64decode(padded_chunk)
                    decoded_chunks.append(decoded)
                except:
                    valid = False
                    break
            
            if valid and decoded_chunks:
                # 尝试连接解码后的块
                combined = b''.join(decoded_chunks)
                for enc in encodings:
                    try:
                        text = combined.decode(enc)
                        if any(c.isprintable() and not c.isspace() for c in text):
                            results.append((f'分块({size})解码 + {enc}', text[:200]))
                    except:
                        pass
    
    return results

def main():
    print("开始解析base64编码内容...")
    
    # 读取文件
    with open('示例.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        parts = line.strip().split('----')
        if len(parts) >= 2:
            number = parts[0]
            encoded = parts[1]
            
            print(f"\n=== 处理第{i+1}行，编号: {number} ===")
            print(f"编码内容长度: {len(encoded)} 字符")
            
            # 基本解码尝试
            results = try_decode_base64(encoded)
            
            # 尝试分割后解码
            split_results = try_split_and_decode(encoded)
            if split_results:
                results.extend(split_results)
            
            if results:
                print(f"找到 {len(results)} 种可能的解码方式:")
                for j, (method, result) in enumerate(results, 1):
                    # 检查结果是否包含有意义的内容
                    meaningful_chars = sum(1 for c in result if c.isprintable() and not c.isspace())
                    total_chars = len(result)
                    quality = meaningful_chars / total_chars if total_chars > 0 else 0
                    
                    if quality > 0.5:
                        print(f"\n{j}. 使用 {method}:")
                        print(f"解码质量: {quality:.2f}")
                        print(result)
            else:
                print("未找到有意义的解码结果")
                
                # 尝试检查是否是有效的base64格式
                valid_base64 = re.match(r'^[A-Za-z0-9+/=]+$', encoded) is not None
                if not valid_base64:
                    invalid_chars = set(c for c in encoded if not re.match(r'[A-Za-z0-9+/=]', c))
                    print(f"注意: 包含非标准base64字符: {invalid_chars}")

    print("\n分析完成。")

if __name__ == "__main__":
    main() 