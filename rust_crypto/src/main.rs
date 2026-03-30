use aes_gcm::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    Aes256Gcm, Key, Nonce
};
use rand::RngCore;
use std::env;
use std::fs;

// The shared 32-byte secret key for our encryption.
// In a highly advanced setup, this could be injected at build time.
const AES_KEY: &[u8; 32] = b"RUST_FLET_APP_SECRET_KEY_1234567";

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("Usage: {} <input_python_file> <output_bin_file>", args[0]);
        std::process::exit(1);
    }

    let input_path = &args[1];
    let output_path = &args[2];

    let plaintext = fs::read(input_path).expect("Failed to read input Python file");

    let key = Key::<Aes256Gcm>::from_slice(AES_KEY);
    let cipher = Aes256Gcm::new(key);

    let mut nonce_bytes = [0u8; 12];
    rand::thread_rng().fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    let ciphertext = cipher.encrypt(nonce, plaintext.as_ref())
        .expect("Encryption failure!");

    // Final payload format: [12 bytes nonce] + [encrypted data]
    let mut payload = Vec::new();
    payload.extend_from_slice(&nonce_bytes);
    payload.extend_from_slice(&ciphertext);

    fs::write(output_path, payload).expect("Failed to write output binary file");
    println!("Successfully encrypted {} to {}", input_path, output_path);
}
