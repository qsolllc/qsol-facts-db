package factsdb

import (
"encoding/json"
"fmt"
)

type AstNode struct {
Type  string          `json:"type"`
Value json.RawMessage `json:"value,string"`
}

func EvaluateMap(node map[string]interface{}, env map[string]bool) (bool, error) {
nodeType, ok := node["type"].(string)
if !ok {
return false, fmt.Errorf("missing node type")
}

switch nodeType {
case "Var":
vName, ok := node["value"].(string)
if !ok {
return false, fmt.Errorf("invalid Var value")
}
return env[vName], nil
case "Not":
innerMap, ok := node["value"].(map[string]interface{})
if !ok {
return false, fmt.Errorf("invalid Not inner expression")
}
val, err := EvaluateMap(innerMap, env)
return !val, err
case "And":
list, ok := node["value"].([]interface{})
if !ok {
return false, fmt.Errorf("invalid And list")
}
for _, item := range list {
m, ok := item.(map[string]interface{})
if !ok {
return false, fmt.Errorf("invalid subnode in And")
}
res, err := EvaluateMap(m, env)
if err != nil || !res {
return false, err
}
}
return true, nil
case "Or":
list, ok := node["value"].([]interface{})
if !ok {
return false, fmt.Errorf("invalid Or list")
}
for _, item := range list {
m, ok := item.(map[string]interface{})
if !ok {
return false, fmt.Errorf("invalid subnode in Or")
}
res, err := EvaluateMap(m, env)
if err == nil && res {
return true, nil
}
}
return false, nil
default:
return false, fmt.Errorf("unknown node type: %s", nodeType)
}
}
