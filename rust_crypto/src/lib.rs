use aes_gcm::{aead::Aead, Aes256Gcm, Key, KeyInit, Nonce};
use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use std::str;

const AES_KEY: &[u8; 32] = b"RUST_FLET_APP_SECRET_KEY_1234567"; // must match main.rs

#[no_mangle]
pub extern "C" fn decrypt_payload(
    encrypted_data: *const u8,
    data_len: usize,
) -> *mut c_char {
    let payload = unsafe { std::slice::from_raw_parts(encrypted_data, data_len) };

    if payload.len() < 12 {
        return CString::new("").unwrap().into_raw();
    }

    let (nonce_bytes, ciphertext) = payload.split_at(12);

    let key = Key::<Aes256Gcm>::from_slice(AES_KEY);
    let cipher = Aes256Gcm::new(key);
    let nonce = Nonce::from_slice(nonce_bytes);

    match cipher.decrypt(nonce, ciphertext) {
        Ok(plaintext) => {
            if let Ok(s) = str::from_utf8(&plaintext) {
                CString::new(s).unwrap().into_raw()
            } else {
                CString::new("").unwrap().into_raw()
            }
        }
        Err(_) => CString::new("").unwrap().into_raw(),
    }
}

// Function to free the memory allocated by CString
#[no_mangle]
pub extern "C" fn free_string(s: *mut c_char) {
    if s.is_null() {
        return;
    }
    unsafe {
        let _ = CString::from_raw(s);
    }
}
