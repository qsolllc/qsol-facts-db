use serde_json::json;
use crate::{hash::hash, storage};
pub fn write(cap: &str, tree: &str) -> String {
    let obj = json!({ "type": "snapshot", "capfile": cap, "tree": tree });
    let bytes = serde_json::to_vec(&obj).unwrap();
    let h = hash(&bytes);
    storage::store(&h, &bytes);
    h
}
