import hashlib

class MerkleTree:
    def __init__(self, leaves: list[str]):
        self.leaves = [self._hash(leaf) for leaf in leaves]
        self.tree = self._build_tree(self.leaves)

    def _hash(self, data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def _build_tree(self, leaves: list[str]) -> list[list[str]]:
        if not leaves:
            return [[""]]
        
        tree = [leaves]
        while len(tree[-1]) > 1:
            current_level = tree[-1]
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = self._hash(left + right)
                next_level.append(combined)
            tree.append(next_level)
        return tree

    @property
    def root(self) -> str:
        return self.tree[-1][0] if self.tree and self.tree[-1] else ""

    def generate_proof(self, index: int) -> list[tuple[str, str]]:
        """Generate inclusion proof for leaf at given index: list of (hash, 'left'/'right')"""
        proof = []
        if index < 0 or index >= len(self.leaves):
            return proof

        current_index = index
        for level in range(len(self.tree) - 1):
            level_nodes = self.tree[level]
            is_right_node = current_index % 2 == 1
            sibling_index = current_index - 1 if is_right_node else current_index + 1

            if sibling_index < len(level_nodes):
                direction = 'left' if is_right_node else 'right'
                proof.append((level_nodes[sibling_index], direction))
            else:
                proof.append((level_nodes[current_index], 'left'))
            
            current_index //= 2
        return proof

    def verify_proof(self, leaf: str, proof: list[tuple[str, str]], root: str) -> bool:
        current_hash = self._hash(leaf)
        for sibling_hash, direction in proof:
            if direction == 'left':
                current_hash = self._hash(sibling_hash + current_hash)
            else:
                current_hash = self._hash(current_hash + sibling_hash)
        return current_hash == root
