import json
from poltree import NPolTree, HashPolicy
from poltree import resolveAccessRequestfromPolicy  # Assuming your slow function is in a separate file
from time import perf_counter as pf
from time import perf_counter_ns as pfn

print("Reading policy.json")
with open('policy.json', 'r') as f:
    policy_str = f.read()

print("Converting policy to dictionary")
policy: dict = json.loads(policy_str)

# policy_hash = NPolTree.load_hash("policy_hash.txt")
policy_hash = None
pol_tree = None
if policy_hash != HashPolicy(policy):
    print("Initializing faster policy tree")
    pol_tree = NPolTree(policy_str)

    # print("Storing policy tree")
    # pol_tree.store_tree("policy_tree.json")
    # print("Storing policy hash")
    # pol_tree.store_hash("policy_hash.txt", policy)
else:
    print("Loading policy tree")
    pol_tree = NPolTree()
    pol_tree.load_tree("policy_tree.json")

print("Reading access_request.txt")
access_requests = []
with open('access_request.txt', 'r') as f:
    for line in f:
        if line.strip():
            access_requests.append(eval(line.strip()))


def test_access_resolution():
    passed = 0
    failed = 0
    fast_access_resolution_times = []
    slow_access_resolution_times = []
    allowed = 0
    denied = 0
    
    for i, access_request in enumerate(access_requests):
        slow_time = pfn()
        slow_result = resolveAccessRequestfromPolicy(access_request, policy)
        slow_time = pfn() - slow_time
        
        slow_access_resolution_times.append(slow_time)
        
        fast_time = pfn()
        fast_result = pol_tree.resolve(access_request)
        fast_time = pfn() - fast_time
        
        fast_access_resolution_times.append(fast_time)
        
        # print(f"Test {i+1}")
        # print(f"Access Resolution Time - Slow: {slow_time} ns, Fast: {fast_time} ns")
        
        # Normalize fast_result for comparison (Allow/Deny to 1/0)
        fast_result_normalized = 1 if fast_result == "Allow" else 0
        
        allowed += 1 if slow_result == 1 else 0
        denied += 1 if slow_result == 0 else 0
        
        if slow_result == fast_result_normalized:
            passed += 1
        else:
            failed += 1
            
            print(f"Test {i+1} failed")
            print(f"Access Request: {access_request}")
            print(f"Expected: {slow_result}")
            print(f"Got: {fast_result_normalized}")
            print()
    
    print(f"Total Passed: {passed}")
    print(f"Total Failed: {failed}")
    
    print("Average Access Resolution Time - Slow: ", sum(slow_access_resolution_times)/len(slow_access_resolution_times), "ns")
    print("Average Access Resolution Time - Fast: ", sum(fast_access_resolution_times)/len(fast_access_resolution_times), "ns")
    print(f"No. of Access Requests Allowed: {allowed}")
    print(f"No. of Access Requests Denied: {denied}")
    exit(0)

if __name__ == "__main__":
    test_access_resolution()