import base64
import zlib
import os
import sys

def obfuscate_file(filepath):
    # 读取原始代码
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    # 移除会引发安卓端版本冲突的 marshal，改用纯高强度文本压缩+Base64加密
    compressed = zlib.compress(source.encode('utf-8'))
    encoded = base64.b64encode(compressed).decode('utf-8')

    # 动态解密加载引擎
    loader = f"""import zlib, base64
# --- EXECUTABLE PAYLOAD ENCRYPTED ---
exec(zlib.decompress(base64.b64decode({repr(encoded)})).decode('utf-8'))
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(loader)
    print(f"File '{filepath}' successfully obfuscated and secured!")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else 'main.py'
    if os.path.exists(target):
        obfuscate_file(target)
    else:
        print(f"Error: {target} not found.")
