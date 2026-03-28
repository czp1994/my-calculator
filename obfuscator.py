import base64
import zlib
import marshal
import os
import sys

def obfuscate_file(filepath):
    # Read original python code
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    # Compile into bytecode and serialize using marshal
    compiled = compile(source, '<obfuscated>', 'exec')
    marshaled = marshal.dumps(compiled)

    # Compress and Base64 encode
    compressed = zlib.compress(marshaled)
    encoded = base64.b64encode(compressed).decode('utf-8')

    # The loader snippet that decrypts and executes the payload at runtime
    loader = f"""import marshal, zlib, base64
# --- EXECUTABLE PAYLOAD ENCRYPTED ---
exec(marshal.loads(zlib.decompress(base64.b64decode({repr(encoded)}))))
"""

    # Overwrite the file with the obfuscated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(loader)
    print(f"File '{filepath}' successfully obfuscated and secured!")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else 'main.py'
    if os.path.exists(target):
        obfuscate_file(target)
    else:
        print(f"Error: {target} not found.")
