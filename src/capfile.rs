use serde_json::json;
use crate::{hash::hash, storage};
pub fn write(tree: &str) -> String {
    let obj = json!({ "type": "capfile", "tree": tree });
    let bytes = serde_json::to_vec(&obj).unwrap();
    let h = hash(&bytes);
    storage::store(&h, &bytes);
    h
}
