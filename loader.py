import platform
import os
import sys
import ctypes

def load_and_run():
    # Detect architecture
    arch = platform.machine().lower()
    
    # Map architectures to library names
    # Android architectures typically report as aarch64 or x86_64 in Python sys/platform
    lib_name = None
    if arch in ('aarch64', 'armv8', 'arm64'):
        lib_name = 'libdecryptor_aarch64.so'
    elif arch in ('x86_64', 'amd64'):
        lib_name = 'libdecryptor_x86_64.so'
    elif sys.platform == 'win32':
        # Local debugging on Windows fallback
        lib_name = 'decryptor.dll'
    else:
        print(f"Error: Unsupported architecture or platform: {arch}")
        sys.exit(1)
        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(current_dir, lib_name)
    
    # Ensure the library file exists (Flet extracts files into the current temp run directory)
    if not os.path.exists(lib_path):
        print(f"Fatal: Decryption library missing at {lib_path}")
        sys.exit(1)

    # Dynamically load the .so shared library using ctypes
    try:
        decryptor_lib = ctypes.cdll.LoadLibrary(lib_path)
    except Exception as e:
        print(f"Fatal: Failed to load encryption native library {lib_path}: {e}")
        sys.exit(1)

    # Setup C-function arg types and return types
    decryptor_lib.decrypt_payload.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
    decryptor_lib.decrypt_payload.restype = ctypes.c_void_p
    
    decryptor_lib.free_string.argtypes = [ctypes.c_void_p]

    # Read the encrypted Python code (payload.bin)
    payload_path = os.path.join(current_dir, 'payload.bin')
    if not os.path.exists(payload_path):
        print(f"Fatal: Encrypted payload missing at {payload_path}")
        sys.exit(1)
        
    with open(payload_path, 'rb') as f:
        encrypted_data = f.read()

    # Pass the encrypted payload to the Rust native library to decipher
    ptr = decryptor_lib.decrypt_payload(encrypted_data, len(encrypted_data))
    
    if ptr:
        # Convert C pointer to a python utf-8 decoded string
        decrypted_code = ctypes.cast(ptr, ctypes.c_char_p).value.decode('utf-8')
        
        # Free memory back in Rust to avert leaks
        decryptor_lib.free_string(ptr)
        
        if decrypted_code:
            # Execute the plaintext Python code dynamically
            exec(decrypted_code, globals())
        else:
            print("Fatal: Decryption successful but resulted in empty or invalid source string.")
            sys.exit(1)
    else:
        print("Fatal: Rust Native Decryption failed, returned null pointer.")
        sys.exit(1)

if __name__ == '__main__':
    load_and_run()
