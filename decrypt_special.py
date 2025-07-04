import base64
import zlib
import re
import binascii
import os
import sys
from itertools import product

def try_xor_keys(data, start=0, end=256):
    """尝试不同的XOR密钥解密数据"""
    results = []
    encodings = ['utf-8', 'ascii', 'latin-1', 'gbk', 'gb18030']
    
    for key in range(start, end):
        # 应用XOR解密
        xor_decoded = bytes(b ^ key for b in data)
        
        # 尝试不同编码解析结果
        for enc in encodings:
            try:
                text = xor_decoded.decode(enc)
                # 检查可读字符比例
                readable_chars = sum(1 for c in text if c.isprintable())
                if readable_chars > len(text) * 0.7:
                    results.append((key, enc, text[:200]))
            except:
                pass
    
    return results

def try_key_combinations(data, key_length=1):
    """尝试使用重复模式密钥解密"""
    results = []
    
    if key_length > 4:
        return []  # 限制密钥长度，避免过度计算
    
    encodings = ['utf-8', 'ascii', 'latin-1', 'gbk']
    
    # 生成所有可能的密钥模式
    common_bytes = [1, 2, 13, 42, 97, 65, 48, 255, 127, 128, 129]
    key_patterns = product(common_bytes, repeat=key_length)
    
    for pattern in key_patterns:
        # 创建一个与数据长度匹配的重复模式密钥
        full_key = pattern * (len(data) // len(pattern) + 1)
        full_key = full_key[:len(data)]
        
        # 应用XOR
        xor_result = bytes(data[i] ^ key for i, key in enumerate(full_key))
        
        # 检查结果
        for enc in encodings:
            try:
                text = xor_result.decode(enc)
                readable_chars = sum(1 for c in text if c.isprintable())
                if readable_chars > len(text) * 0.7:
                    results.append((pattern, enc, text[:200]))
            except:
                pass
    
    return results

def process_file(filepath):
    """处理文件中的base64编码内容"""
    print(f"读取文件: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        parts = line.strip().split('----')
        if len(parts) >= 2:
            number = parts[0]
            encoded = parts[1]
            
            print(f"\n===== 处理第{i+1}行，编号: {number} =====")
            print(f"编码内容长度: {len(encoded)} 字符")
            
            # 标准base64解码
            try:
                # 确保有正确的填充
                padding_fixed = encoded + "=" * ((4 - len(encoded) % 4) % 4)
                decoded = base64.b64decode(padding_fixed)
                
                print("解码成功，尝试XOR解密...")
                print(f"数据长度: {len(decoded)} 字节")
                
                # 显示前20个字节的十六进制
                print(f"前20字节: {decoded[:20].hex()}")
                
                # 1. 尝试常见XOR密钥
                print("1. 测试单字节XOR密钥 (0-255):")
                xor_results = try_xor_keys(decoded)
                
                if xor_results:
                    for key, enc, text in xor_results:
                        print(f"\n使用密钥 {key} (0x{key:02X}) + {enc} 解码:")
                        print(f"解码结果: {text}")
                else:
                    print("单字节密钥未找到有效结果")
                
                # 2. 尝试双字节和三字节模式密钥
                for length in [2, 3]:
                    print(f"\n2. 测试{length}字节模式密钥:")
                    pattern_results = try_key_combinations(decoded, length)
                    
                    if pattern_results:
                        for pattern, enc, text in pattern_results:
                            pattern_hex = ', '.join([f"0x{k:02X}" for k in pattern])
                            print(f"\n使用密钥模式 [{pattern_hex}] + {enc} 解码:")
                            print(f"解码结果: {text}")
                    else:
                        print(f"{length}字节模式密钥未找到有效结果")
            except Exception as e:
                print(f"解码或处理失败: {str(e)}")
    
    print("\n处理完成!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_file(sys.argv[1])
    else:
        process_file("示例.txt") 



        