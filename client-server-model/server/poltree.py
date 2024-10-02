import json
import math
from hashlib import sha256


class NPolTreeNode:
    def __init__(
        self, attr_type, attribute, branches=None, decision=None, is_leaf=False
    ):
        self._id = str(id(self))
        self.attr_type = attr_type
        self.attribute = attribute
        self.branches = branches if branches else {}
        self.decision = decision
        self.is_leaf = is_leaf
    
    def __repr__(self):
        return f"Node: ({self.attribute}, {self.decision}), IsLeaf: {self.is_leaf}, Branches: {list(self.branches.keys())}"

    def to_dict(self):
        """Serialize the node into a dictionary."""
        return {
            "id": self._id,
            "attr_type": self.attr_type,
            "attribute": self.attribute,
            "branches": {key: branch.to_dict() for key, branch in self.branches.items()},
            "decision": self.decision,
            "is_leaf": self.is_leaf,
        }

    @staticmethod
    def from_dict(data):
        """Deserialize a node from a dictionary."""
        node = NPolTreeNode(
            attr_type=data["attr_type"],
            attribute=data["attribute"],
            decision=data["decision"],
            is_leaf=data["is_leaf"]
        )
        node.branches = {
            key: NPolTreeNode.from_dict(branch_data)
            for key, branch_data in data.get("branches", {}).items()
        }
        return node

class NPolTree:
    def __init__(self, policy: str | dict = None):
        self.update_policy(policy)

    def update_policy(self, policy):
        self.policy = {}
        if type(policy) == str:
            self.policy: dict = json.loads(policy)
        elif type(policy) == dict:
            self.policy: dict = policy
        if len(self.policy) == 0:
            self.root = NPolTreeNode(None, None, decision="Deny", is_leaf=True)
            return
        self.stats = self.calculate_stats(self.policy)
        self.attributes = self.gather_attributes()
        self.attr_vals = self.gather_attr_vals()
        self.node_count = 0
        self.leaf_count = 0
        self.root = self.build_tree(self.policy, self.attributes)

    def gather_attributes(self):
        attr_type_attrs = []
        for attr_type, attrs in self.stats.items():
            for attr in attrs:
                attr_type_attrs.append((attr_type, attr))
        return attr_type_attrs

    def gather_attr_vals(self):
        attr_vals = {}
        for attr_type, attrs in self.stats.items():
            for attr, values in attrs.items():
                if attr_type not in attr_vals:
                    attr_vals[attr_type] = {}
                attr_vals[attr_type][attr] = values.keys() 
        return attr_vals

    def calculate_stats(self, policy_rules):
        stats = {"sub": {}, "obj": {}, "op": {"op": {}}}
        for rule_name, rule in policy_rules.items():
            subj_attrs = rule.get("sub", {})
            obj_attrs = rule.get("obj", {})
            op_values = rule.get("op", [])
            for attr, values in subj_attrs.items():
                if attr not in stats["sub"]:
                    stats["sub"][attr] = {}
                for value in values:
                    if value not in stats["sub"][attr]:
                        stats["sub"][attr][value] = 0
                    stats["sub"][attr][value] += 1
            for attr, values in obj_attrs.items():
                if attr not in stats["obj"]:
                    stats["obj"][attr] = {}
                for value in values:
                    if value not in stats["obj"][attr]:
                        stats["obj"][attr][value] = 0
                    stats["obj"][attr][value] += 1
            if op_values not in stats["op"]["op"]:
                stats["op"]["op"][op_values] = 0
            stats["op"]["op"][op_values] += 1
        return stats

    def entropy(self, attr_type, attribute, rules: dict[str, dict]) -> float:
        values = self.attr_vals[attr_type][attribute]
        counts = {value: 0 for value in values}
        total = 0
        for rule_name, rule in rules.items():
            rule_values = (
                rule.get(attr_type, {}).get(attribute, [])
                if attr_type != "op"
                else [rule.get(attr_type, None)]
            )
            if "*" in rule_values:
                continue  # Skip rules with wildcard in entropy calculation
            total += 1
            for value in rule_values:
                counts[value] += 1
        entropy = 0
        for value, count in counts.items():
            probability = count / total if total > 0 else 0
            entropy -= probability * math.log2(probability) if probability > 0 else 0
        return entropy

    def select_attribute(self, attributes, rules: dict[str, dict]) -> tuple:
        max_entropy = float("-inf")
        selected_attribute = (None, None)
        for attr_type, attribute in attributes:
            entropy = self.entropy(attr_type, attribute, rules)
            if entropy > max_entropy:
                max_entropy = entropy
                selected_attribute = (attr_type, attribute)
        return selected_attribute

    def build_tree(self, policy_rules, attributes):
        self.node_count += 1
        if not policy_rules:
            self.leaf_count += 1
            return NPolTreeNode(None, None, decision="Deny", is_leaf=True)
        if len(attributes) == 0:
            self.leaf_count += 1
            return NPolTreeNode(None, None, decision="Allow", is_leaf=True)
        attr_type, attribute = self.select_attribute(attributes, policy_rules)
        if attr_type is None:
            self.leaf_count += 1
            return NPolTreeNode(None, None, decision="Allow", is_leaf=True)
        node = NPolTreeNode(attr_type, attribute)
        for value in self.attr_vals[attr_type][attribute]:
            new_attributes = [
                attr for attr in attributes if attr != (attr_type, attribute)
            ]
            if attr_type == "op":
                new_policy_rules = {
                    rule_name: rule
                    for rule_name, rule in policy_rules.items()
                    if value == rule.get(attr_type, None) or rule.get(attr_type, None) == "*"
                }
            else:
                new_policy_rules = {
                    rule_name: rule
                    for rule_name, rule in policy_rules.items()
                    if value in rule.get(attr_type, {}).get(attribute, []) or "*" in rule.get(attr_type, {}).get(attribute, [])
                }
            if len(new_policy_rules) == 0: # Skip empty branches
                continue
            node.branches[value] = self.build_tree(new_policy_rules, new_attributes)
        return node
        
    def _print_tree(self, node, depth=0):
        if node.is_leaf:
            print(f"{'  ' * depth}Decision: {node.decision}")
        else:
            print(f"{'  ' * depth}Attribute: {node.attribute}")
            for value, branch in node.branches.items():
                print(f"{'  ' * depth}Value: {value}")
                self._print_tree(branch, depth + 1)
    
    def print_tree(self):
        self._print_tree(self.root)
    
    def _resolve(self, node, request, depth=0):
        if node.is_leaf:
            return (node.decision == "Allow")
        attr_type = node.attr_type
        attribute = node.attribute
        access = False
        
        for value in (request.get(attr_type, {}).get(attribute, []) if attr_type != "op" else [request.get(attr_type, None)]):
            if value in node.branches:
                access |= self._resolve(node.branches[value], request, depth + 1)
                if access:
                    break
        if len(value) and "*" not in value:
            if "*" in node.branches:
                access |= self._resolve(node.branches["*"], request, depth + 1)
        return access
    
    def resolve(self, request):
        return "Allow" if self._resolve(self.root, request) else "Deny"
    
    def insert_rule(self, rule_name, rule):
        # print(f"Inserting rule: {rule_name}: {rule}")
        # print(f"Prev policy size: {len(self.policy)}")
        self.policy[rule_name] = rule
        self.update_policy(self.policy)
    
    def store_tree(self, file_path):
        """Store the tree structure to a JSON file."""
        with open(file_path, 'w') as file:
            json.dump(self.root.to_dict(), file)
    
    def load_tree(self, file_path):
        """Load the tree structure from a JSON file."""
        with open(file_path, 'r') as file:
            data = json.load(file)
        self.root = NPolTreeNode.from_dict(data)
    
    @staticmethod
    def store_hash(file_path, policy: dict):
        with open(file_path, 'w') as file:
            file.write(HashPolicy(policy))

    @staticmethod
    def load_hash(file_path):
        with open(file_path, 'r') as file:
            return (file.read())
    

# def make_hashable(obj):
#     """Recursively convert a dictionary into a hashable tuple."""
#     if isinstance(obj, dict):
#         return tuple((key, make_hashable(value)) for key, value in sorted(obj.items()))
#     elif isinstance(obj, list):
#         return tuple(make_hashable(item) for item in obj)
#     elif isinstance(obj, set):
#         return frozenset(make_hashable(item) for item in obj)
#     return obj


def HashPolicy(policy):
    """Hash a policy dictionary."""
    return sha256(json.dumps(policy).encode()).hexdigest()