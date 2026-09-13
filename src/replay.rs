use serde_json::Value;
use crate::{hash::hash, storage};
pub fn verify(id: &str) -> bool {
    let data = match storage::load(id) {
        Some(v) => v,
        None => return false,
    };
    let parsed: Value = serde_json::from_slice(&data).unwrap();
    let recomputed = serde_json::to_vec(&parsed).unwrap();
    hash(&recomputed) == id
}
pub fn replay_chain(_id: &str) -> Vec<String> {
    vec!["replay-not-implemented-yet".to_string()]
}
