from collections import deque, defaultdict
import time
import klotski.solver
from klotski import board # this must work from repo root


def build_graph():
    """
    BFS from initial board to get full graph of reachable configs.
    Returns: graph dict[node_key -> set(neighbor_keys)], all_nodes set
    """
    graph = defaultdict(set)
    visited = set()

    start = board.initial_board()
    start_key = start.hash_key()
    queue = deque([start])
    visited.add(start_key)

    while queue:
        cur = queue.popleft()
        cur_key = cur.hash_key()

        for nxt in cur.next_boards():
            nxt_key = nxt.hash_key()
            graph[cur_key].add(nxt_key)
            graph[nxt_key].add(cur_key) # undirected

            if nxt_key not in visited:
                visited.add(nxt_key)
                queue.append(nxt)

    return graph, visited

def find_farthest_from_solution(graph, all_node_keys):
    """
    Multi-source BFS starting from all solved nodes.
    Returns: farthest_node_key, max_distance, distance_map
    """
    # We need Board objects to test if solved, but we only have keys.
    # So rebuild minimal Boards from keys using Solver's approach: BFS again but store one Board per key.
    # Faster: do one BFS to map key -> Board while building graph.
    # For simplicity here, we'll redo a light BFS to recover Boards.

    # Map key -> Board instance
    key_to_board = {}
    start = board.initial_board()
    q = deque([start])
    key_to_board[start.hash_key()] = start

    while q:
        b = q.popleft()
        for nb in b.next_boards():
            k = nb.hash_key()
            if k not in key_to_board and k in all_node_keys:
                key_to_board[k] = nb
                q.append(nb)

    # Find all solved nodes
    solved_keys = [k for k, b in key_to_board.items() if board.solved(b)]
    if not solved_keys:
        raise RuntimeError("No solved states found")

    # Multi-source BFS on keys
    dist = {}
    queue = deque()
    for s in solved_keys:
        dist[s] = 0
        queue.append(s)

    farthest_key = None
    max_dist = -1

    while queue:
        cur = queue.popleft()
        if dist[cur] > max_dist:
            max_dist = dist[cur]
            farthest_key = cur

        for nbr in graph[cur]:
            if nbr not in dist:
                dist[nbr] = dist[cur] + 1
                queue.append(nbr)

    return farthest_key, max_dist, dist, key_to_board

def reconstruct_path(farthest_key, key_to_board, dist):
    """Optional: rebuild one shortest path from farthest node to a solution"""
    path = []
    cur_key = farthest_key
    while dist[cur_key]!= 0:
        path.append(key_to_board[cur_key])
        # find a neighbor 1 step closer to solution
        for nbr in key_to_board[cur_key].next_boards():
            nbr_key = nbr.hash_key()
            if nbr_key in dist and dist[nbr_key] == dist[cur_key] - 1:
                cur_key = nbr_key

def main():
    print("Building graph...")
    t0 = time.time()
    graph, nodes = build_graph()
    print(f"Graph: {len(nodes)} nodes, {sum(len(v) for v in graph.values())//2} edges")
    print(f"Took {time.time() - t0:.2f}s")

    print("\nFinding node farthest from any solution...")
    t0 = time.time()
    farthest_key, max_dist, dist, key_to_board = find_farthest_from_solution(graph, nodes)
    print(f"Done in {time.time() - t0:.2f}s")

    print(f"\nFarthest node is {max_dist} moves from a solution.")
    print("Board layout:")
    print(key_to_board[farthest_key]) # uses Board.__str__

if __name__ == "__main__":
    main()