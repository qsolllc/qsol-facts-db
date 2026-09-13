use std::fs;
const ROOT: &str = "cap/objects";
pub fn init() { fs::create_dir_all(ROOT).unwrap(); }
pub fn store(hash: &str, bytes: &[u8]) {
    let path = format!("{}/{}", ROOT, hash);
    fs::write(path, bytes).unwrap();
}
pub fn load(hash: &str) -> Option<Vec<u8>> {
    let path = format!("{}/{}", ROOT, hash);
    fs::read(path).ok()
}
