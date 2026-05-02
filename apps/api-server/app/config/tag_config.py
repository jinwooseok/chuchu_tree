"""
TAG_CONFIG: solved.ac 태그 코드 → 레벨/목표/부모 태그 매핑

db_initializer.py의 초기 마이그레이션과 ProblemMetadataSyncService의
주간 동기화 모두에서 참조한다.
"""

TAG_CONFIG = {
    # 쌩기초 (BEGINNER)
    "math": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "sorting": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "geometry": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "arithmetic": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "number_theory": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "combinatorics": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "primality_test": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},

    # 기초알고리즘 (BEGINNER)
    "implementation": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "greedy": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "string": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "bruteforcing": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "trees": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "set": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "simulation": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": ["implementation"]},
    "prefix_sum": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "bfs": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "dfs": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "hash_set": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": ["set"]},
    "backtracking": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "stack": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "recursion": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "arbitrary_precision": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "sieve": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "deque": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "queue": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},

    # 필수알고리즘 (REQUIREMENT)
    "dp": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "ad_hoc": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "binary_search": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["set"]},
    "shortest_path": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["dfs", "bfs"]},
    "bitmask": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "disjoint_set": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "tree_set": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["set", "trees"]},
    "priority_queue": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["stack", "queue"]},
    "divide_and_conquer": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "two_pointer": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "euclidean": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "grid_graph": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "sliding_window": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["two_pointer"]},

    # 세부알고리즘 (DETAIL)
    "segtree": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["trees", "stack"]},
    "dijkstra": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["shortest_path"]},
    "flow": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": []},
    "trie": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["string"]},
    "mst": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["priority_queue"]},
    "topological_sorting": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["trees"]},
    "lca": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["trees"]},
    "floyd_warshall": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["shortest_path"]},
    "lazyprop": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["segtree"]},
    "dp_tree": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["dp", "trees"]},
    "dp_bitfield": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["dp", "bitmask"]},
    "knapsack": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["dp"]},
    "traceback": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["dp"]},
    "lis": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["dp"]},

    # 도전알고리즘 (CHALLENGE)
    "mcmf": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["flow"]},
    "kmp": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["string"]},
    "tsp": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["dp_bitfield"]},
    "bipartite_matching": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["flow"]},
    "scc": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["dfs", "stack"]},
    "convex_hull": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["geometry"]},
}
