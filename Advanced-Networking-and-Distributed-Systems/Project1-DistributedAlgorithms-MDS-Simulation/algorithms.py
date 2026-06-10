"""
Algorithm implementations for MDS Project
Contains Seq_MDS (Algorithm 11.1) and Span_MDS (Algorithm 11.2)
Uses distsim framework for distributed simulation
"""

import networkx as nx
import time
import logging
from typing import Tuple, Set, List, Dict, Optional
from distsim import Node, System

# Constants
logger = logging.getLogger(__name__)
MAX_SIMULATION_ROUNDS = 50
ROUND_INTERVAL = 1.0


def run_seq_mds(G: nx.Graph) -> Tuple[Set[int], float, int]:
    """
    Algorithm 11.1: Greedy Sequential MDS (Centralized)
    
    Time Complexity: O(N*Delta) or O(N^2) depending on implementation.
    
    Args:
        G: NetworkX graph
        
    Returns:
        Tuple of (dominating_set, execution_time, message_count)
        Note: Sequential algorithm sends 0 messages (centralized)
    """
    if len(G) == 0:
        logger.warning("Empty graph provided to run_seq_mds")
        return set(), 0.0, 0
    
    start_time = time.time()
    
    dominating_set = set()
    covered_nodes = set()
    all_nodes = set(G.nodes())
    
    # Track 'span' dynamically: number of WHITE neighbors
    max_iterations = len(all_nodes)  # Safety limit
    iterations = 0
    
    while len(covered_nodes) < len(all_nodes) and iterations < max_iterations:
        iterations += 1
        best_candidate = -1
        max_span = -1
        
        # Calculate span for all nodes not in DS
        candidates = all_nodes - dominating_set
        
        for u in candidates:
            # Span = Yourself (if not covered) + Uncovered Neighbors
            white_neighbors = [v for v in G.neighbors(u) if v not in covered_nodes]
            current_span = len(white_neighbors)
            if u not in covered_nodes:
                current_span += 1
            
            # Greedy Criterion: Max Span
            # Tie-Breaking: Lowest ID
            if current_span > max_span:
                max_span = current_span
                best_candidate = u
            elif current_span == max_span:
                # Tie-breaker (Lowest ID favors deterministic behavior)
                if best_candidate == -1 or u < best_candidate:
                    best_candidate = u
        
        if best_candidate == -1:
            logger.warning("No candidate found, graph may be disconnected")
            break
            
        # Add to DS and Update Coverage
        dominating_set.add(best_candidate)
        covered_nodes.add(best_candidate)
        for v in G.neighbors(best_candidate):
            covered_nodes.add(v)
    
    if iterations >= max_iterations:
        logger.warning(f"Maximum iterations reached in seq_mds")
            
    exec_time = time.time() - start_time
    # Sequential algorithm is centralized, no messages sent (0 messages)
    return dominating_set, exec_time, 0


class MDSNode(Node):
    """
    Represents a single node in the distributed MDS algorithm.
    Implements Algorithm 11.2 logic using distsim framework.
    Extends distsim.Node base class.
    """
    
    def __init__(self, id, env, msgManager):
        """Initialize a distributed MDS node."""
        super().__init__(id, env, msgManager)
        
        # State
        self.state: str = 'WHITE'  # WHITE, BLACK (Dominator), GRAY (Dominated)
        self.span: int = 0
        self.round_num: int = 0
        self.finished: bool = False
        
        # Neighbor information storage
        self.neighbor_info: Dict[int, Dict] = {}  # {neighbor_id: {'state': ..., 'span': ...}}
        
        # Stats
        self.msgs_sent: int = 0
        
    def run(self):
        """Main Distributed Algorithm Loop (Algorithm 11.2) using distsim framework."""
        max_rounds = MAX_SIMULATION_ROUNDS
        waiting_for_info = False  # Flag to track if we're waiting for neighbor INFO messages
        
        while not self.finished and self.round_num < max_rounds:
            # Wait for message from mailbox (distsim pattern)
            yield self.mailbox.get(1)
            
            if len(self.messages) == 0:
                continue
                
            msg = self.receiveMessage()
            
            # Process ROUND messages
            if msg['type'] == 'ROUND':
                self.round_num = msg['round']
                self.neighbor_info = {}  # Reset neighbor info for new round
                
                # Handle isolated nodes
                if len(self.neighbors) == 0:
                    self.state = 'BLACK'
                    self.finished = True
                    break
                
                # Phase 1: Calculate and send INFO message
                # Calculate current span: number of WHITE neighbors + self (if WHITE)
                # For first round, assume all neighbors are WHITE
                if self.round_num == 1:
                    # First round: span = all neighbors + self
                    self.span = len(self.neighbors) + 1
                else:
                    # Subsequent rounds: count WHITE neighbors from previous round info
                    white_neighbor_count = sum(
                        1 for nid in self.neighbors.keys() 
                        if self.neighbor_info.get(nid, {}).get('state') == 'WHITE'
                    )
                    if self.state == 'WHITE':
                        self.span = white_neighbor_count + 1
                    else:
                        self.span = white_neighbor_count
                
                # Send INFO message to all neighbors
                info_msg = {
                    'type': 'INFO',
                    'state': self.state,
                    'span': self.span,
                    'round': self.round_num
                }
                self.sendMessage(info_msg)  # Broadcast to all neighbors (receiver=255)
                self.msgs_sent += 1
                waiting_for_info = True
            
            # Process INFO messages (from neighbors)
            elif msg['type'] == 'INFO':
                # Store neighbor info if it's for current round
                if msg.get('round') == self.round_num:
                    sender_id = msg['sender']
                    if sender_id in self.neighbors:
                        self.neighbor_info[sender_id] = {
                            'state': msg['state'],
                            'span': msg['span']
                        }
                        
                        # Check if we have all neighbor info and can make decision
                        if waiting_for_info and len(self.neighbor_info) == len(self.neighbors):
                            waiting_for_info = False
                            
                            # Update span based on received neighbor info
                            if self.state == 'WHITE':
                                white_neighbors = [
                                    nid for nid, info in self.neighbor_info.items()
                                    if info.get('state') == 'WHITE'
                                ]
                                self.span = len(white_neighbors) + 1
                            
                            # DECISION LOGIC
                            if self.state == 'WHITE':
                                # Check if I am the local maxima
                                is_local_max = True
                                for nid, info in self.neighbor_info.items():
                                    n_state = info.get('state', 'WHITE')
                                    n_span = info.get('span', 0)
                                    
                                    if n_state == 'WHITE':
                                        if n_span > self.span:
                                            is_local_max = False
                                            break
                                        elif n_span == self.span and nid > self.id:
                                            is_local_max = False
                                            break
                                
                                if is_local_max:
                                    self.state = 'BLACK'
                                    # Announce that I am a dominator
                                    dominator_msg = {
                                        'type': 'DOMINATOR',
                                        'round': self.round_num
                                    }
                                    self.sendMessage(dominator_msg)
                                    self.msgs_sent += 1
                                    self.finished = True
                                    break
                            
                            # Phase 2: Check for Dominators
                            for nid, info in self.neighbor_info.items():
                                if info.get('state') == 'BLACK':
                                    if self.state == 'WHITE':
                                        self.state = 'GRAY'
                                        self.finished = True
                                        break
                            
                            if self.finished:
                                break
            
            # Process DOMINATOR messages
            elif msg['type'] == 'DOMINATOR':
                sender_id = msg['sender']
                if sender_id in self.neighbors and self.state == 'WHITE':
                    self.state = 'GRAY'
                    self.finished = True
            
            # Process other message types (TIMEOUT, etc.)
            elif msg['type'] == 'TIMEOUT':
                # Handle timer events if needed
                pass
        
        if self.round_num >= max_rounds:
            # Force finish if max rounds reached - mark as BLACK if still WHITE
            if self.state == 'WHITE':
                self.state = 'BLACK'  # Force to be dominator if timeout
            self.finished = True


def run_span_mds_simulation(G: nx.Graph) -> Tuple[Set[int], float, int, int]:
    """
    Sets up and runs the distsim simulation for Algorithm 11.2.
    
    Args:
        G: NetworkX graph to simulate
        
    Returns:
        Tuple of (dominating_set, execution_time, total_messages, rounds)
    """
    if len(G) == 0:
        logger.warning("Empty graph provided to run_span_mds_simulation")
        return set(), 0.0, 0, 0
    
    try:
        # Create System using distsim with NetworkX graph
        system = System(
            NodeObject=MDSNode,
            nxGraph=G,
            roundInterval=ROUND_INTERVAL
        )
        
        start_time = time.time()
        
        # Run round by round until convergence
        for round_num in range(MAX_SIMULATION_ROUNDS):
            # Run until next round (System automatically sends ROUND messages)
            system.env.run(until=system.env.now + ROUND_INTERVAL)
            
            # Check if all WHITE nodes are finished (converted to BLACK or GRAY)
            white_nodes = [
                node_id for node_id, node in system.nodes.items()
                if node.state == 'WHITE' and not node.finished
            ]
            
            if len(white_nodes) == 0:
                break
        
        # Force any remaining WHITE nodes to become BLACK (safety measure)
        # This ensures we always have a valid dominating set
        for node_id, node in system.nodes.items():
            if node.state == 'WHITE' and not node.finished:
                node.state = 'BLACK'  # Force to be dominator
                node.finished = True
        
        exec_time = time.time() - start_time
        
        # PRUNING PHASE: Rule-k pruning (conservative approach)
        # Only prune if a BLACK node's neighbors are ALL covered by OTHER BLACK nodes
        black_nodes = [node_id for node_id, node in system.nodes.items() if node.state == 'BLACK']
        if len(black_nodes) > 1:  # Only prune if there are multiple BLACK nodes
            nodes_to_prune = []
            
            for node_id in black_nodes:
                node = system.nodes[node_id]
                neighbors = list(node.neighbors.keys())
                if len(neighbors) == 0:
                    continue  # Isolated node, keep it
                
                # Check if all neighbors are covered by OTHER BLACK nodes (not this one)
                all_covered_by_others = True
                for neighbor_id in neighbors:
                    neighbor = system.nodes[neighbor_id]
                    # Neighbor is covered if:
                    # 1. It's GRAY (dominated by another BLACK), OR
                    # 2. It's BLACK itself (covers itself), OR  
                    # 3. It has at least one OTHER BLACK neighbor (besides current node)
                    if neighbor.state == 'GRAY':
                        continue  # Covered by another BLACK
                    if neighbor.state == 'BLACK':
                        continue  # Covers itself
                    # Check if neighbor has another BLACK neighbor (not current node)
                    has_other_black = any(
                        system.nodes[nid].state == 'BLACK' 
                        for nid in neighbor.neighbors.keys() 
                        if nid != node_id
                    )
                    if not has_other_black:
                        all_covered_by_others = False
                        break
                
                # Only prune if ALL neighbors are covered by OTHER nodes
                if all_covered_by_others:
                    nodes_to_prune.append(node_id)
            
            # Apply pruning conservatively - only if we have enough BLACK nodes left
            if len(black_nodes) - len(nodes_to_prune) > 0:
                for node_id in nodes_to_prune:
                    system.nodes[node_id].state = 'GRAY'  # Prune: change from BLACK to GRAY
        
        # Collect final results (after pruning)
        dominating_set = [
            node_id for node_id, node in system.nodes.items()
            if node.state == 'BLACK'
        ]
        total_messages = sum(node.msgs_sent for node in system.nodes.values())
        rounds = max(node.round_num for node in system.nodes.values()) if system.nodes else 0
        
        return set(dominating_set), exec_time, total_messages, rounds
    
    except Exception as e:
        logger.error(f"Error in span_mds_simulation: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return set(), 0.0, 0, 0
