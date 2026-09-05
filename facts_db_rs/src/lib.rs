use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(tag = "type", content = "value")]
pub enum AstNode {
    Var(String),
    Not(Box<AstNode>),
    And(Vec<AstNode>),
    Or(Vec<AstNode>),
}

pub fn evaluate_ast(node: &AstNode, env: &HashMap<String, bool>) -> bool {
    match node {
        AstNode::Var(name) => *env.get(name).unwrap_or(&false),
        AstNode::Not(inner) => !evaluate_ast(inner, env),
        AstNode::And(nodes) => nodes.iter().all(|n| evaluate_ast(n, env)),
        AstNode::Or(nodes) => nodes.iter().any(|n| evaluate_ast(n, env)),
    }
}
