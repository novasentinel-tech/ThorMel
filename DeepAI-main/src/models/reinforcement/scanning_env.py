"""
Scanning Strategy Environment
Gym-compatible environment for RL-based scanning optimization
"""

import numpy as np
import logging
from typing import Tuple, Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScanAction:
    """Represents a scanning action."""
    action_id: int
    action_name: str
    time_cost: float  # Time cost in seconds
    information_gain: float  # Information gained [0-1]
    target_modules: list  # Which modules to scan (HTTP, TLS, DNS, etc.)


class ScanningEnvironment:
    """
    Custom environment for optimizing scanning strategy.
    
    Goal: Learn to maximize security information gathering while minimizing time.
    
    Action Space: 10 discrete scanning actions
    State Space: 32-dimensional (derived from Phase B features)
    """
    
    # Action definitions: 10 different scanning strategies
    ACTIONS = {
        0: ScanAction(0, 'baseline_http', 2.0, 0.3, ['http']),
        1: ScanAction(1, 'baseline_tls', 3.0, 0.3, ['tls']),
        2: ScanAction(2, 'baseline_dns', 1.5, 0.2, ['dns']),
        3: ScanAction(3, 'deep_http', 5.0, 0.7, ['http']),
        4: ScanAction(4, 'deep_tls', 8.0, 0.8, ['tls']),
        5: ScanAction(5, 'deep_dns', 4.0, 0.6, ['dns']),
        6: ScanAction(6, 'whois_registry', 2.5, 0.4, ['whois']),
        7: ScanAction(7, 'port_scanning', 6.0, 0.6, ['ports']),
        8: ScanAction(8, 'tech_detection', 3.5, 0.5, ['tech']),
        9: ScanAction(9, 'complete_scan', 15.0, 0.95, ['http', 'tls', 'dns', 'whois', 'ports', 'tech'])
    }
    
    # Module coverage: how much each action covers
    MODULE_COVERAGE = {
        'http': [0, 3],      # Actions 0, 3 focus on HTTP
        'tls': [1, 4],       # Actions 1, 4 focus on TLS
        'dns': [2, 5],       # Actions 2, 5 focus on DNS
        'whois': [6],        # Action 6 focuses on WHOIS
        'ports': [7],        # Action 7 focuses on ports
        'tech': [8],         # Action 8 focuses on tech stack
        'complete': [9]      # Action 9 does everything
    }
    
    def __init__(
        self,
        max_time: float = 45.0,
        state_dim: int = 32,
        episode_length: int = 100,
        reward_mode: str = 'balanced'
    ):
        """
        Initialize scanning environment.
        
        Args:
            max_time: Maximum time budget per episode (seconds)
            state_dim: State space dimensionality
            episode_length: Maximum episode length
            reward_mode: 'coverage', 'speed', or 'balanced'
        """
        self.max_time = max_time
        self.state_dim = state_dim
        self.episode_length = episode_length
        self.reward_mode = reward_mode
        
        # Episode state
        self.current_step = 0
        self.time_spent = 0.0
        self.coverage = {module: 0.0 for module in ['http', 'tls', 'dns', 'whois', 'ports', 'tech']}
        self.state = None
        self._initialize_domain()
        
    def _initialize_domain(self):
        """Initialize random domain properties."""
        # Simulate a domain's initial state (before scanning)
        self.domain_properties = {
            'complexity': np.random.uniform(0.3, 1.0),  # Scan complexity
            'coverage_needed': np.random.uniform(0.7, 1.0),  # Required coverage
            'has_security_headers': np.random.choice([True, False], p=[0.6, 0.4]),
            'is_production': np.random.choice([True, False], p=[0.8, 0.2]),
        }
        
    def reset(self) -> np.ndarray:
        """
        Reset environment to initial state.
        
        Returns:
            Initial state vector (32-dimensional)
        """
        self.current_step = 0
        self.time_spent = 0.0
        self.coverage = {module: 0.0 for module in ['http', 'tls', 'dns', 'whois', 'ports', 'tech']}
        self._initialize_domain()
        
        self.state = self._get_state()
        logger.debug(f"Environment reset. Initial state shape: {self.state.shape}")
        
        return self.state
    
    def _get_state(self) -> np.ndarray:
        """
        Get current state vector (32-dimensional).
        
        Returns:
            State vector combining:
            - Time progress (1)
            - Coverage per module (6)
            - Domain properties (4)
            - Previous action effect (10)
            - Step count normalized (1)
            - Time budget remaining (1)
            - Coverage average (1)
            - Remaining gap (1)
            - Quality metrics (6)
        """
        state_parts = []
        
        # 1. Time progress (1)
        state_parts.append(self.time_spent / self.max_time)
        
        # 2. Coverage per module (6)
        for module in ['http', 'tls', 'dns', 'whois', 'ports', 'tech']:
            state_parts.append(self.coverage[module])
        
        # 3. Domain properties (4)
        state_parts.append(self.domain_properties['complexity'])
        state_parts.append(float(self.domain_properties['has_security_headers']))
        state_parts.append(float(self.domain_properties['is_production']))
        state_parts.append(self.domain_properties['coverage_needed'])
        
        # 4. Step count normalized (1)
        state_parts.append(self.current_step / self.episode_length)
        
        # 5. Time budget remaining (1)
        state_parts.append(max(0, self.max_time - self.time_spent) / self.max_time)
        
        # 6. Coverage statistics (6)
        coverage_vals = list(self.coverage.values())
        state_parts.append(np.mean(coverage_vals))  # Average coverage
        state_parts.append(np.std(coverage_vals))   # Coverage std
        state_parts.append(max(coverage_vals))      # Max coverage
        state_parts.append(min(coverage_vals))      # Min coverage
        state_parts.append(np.sum(coverage_vals) / 6)  # Total coverage ratio
        state_parts.append(max(0, self.domain_properties['coverage_needed'] - np.mean(coverage_vals)))  # Gap
        
        # 7. Quality indicators (4)
        state_parts.append(0.5)  # Last action success (placeholder)
        state_parts.append(0.5)  # Cumulative efficiency
        state_parts.append(0.5)  # Risk detected
        state_parts.append(0.5)  # Time efficiency
        
        #Fill to 32 dimensions with padding
        while len(state_parts) < 32:
            state_parts.append(0.0)
        
        # Truncate if over 32
        state_parts = state_parts[:32]
        
        return np.array(state_parts, dtype=np.float32)
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """
        Execute one environment step.
        
        Args:
            action: Action index (0-9)
            
        Returns:
            state, reward, done, info
        """
        if action < 0 or action >= 10:
            raise ValueError(f"Invalid action: {action}. Must be 0-9")
        
        scan_action = self.ACTIONS[action]
        
        # Update time spent
        time_added = scan_action.time_cost
        self.time_spent += time_added
        
        # Update coverage for targeted modules
        for module in scan_action.target_modules:
            # Gaussian update to coverage based on information gain
            current = self.coverage[module]
            gain = scan_action.information_gain * (1.0 - current)  # Diminishing returns
            self.coverage[module] = min(1.0, current + gain * np.random.uniform(0.8, 1.0))
        
        # Calculate reward
        reward = self._calculate_reward(scan_action, time_added)
        
        # Check termination
        self.current_step += 1
        done = (self.time_spent >= self.max_time) or (self.current_step >= self.episode_length)
        
        # Bonus reward for completing within budget
        if done and self.time_spent < self.max_time:
            reward += 5.0  # Bonus for completing early
        
        # Penalty for exceeding time budget
        if self.time_spent > self.max_time:
            reward -= 10.0
        
        # Get next state
        next_state = self._get_state()
        
        # Info dict
        info = {
            'action_name': scan_action.action_name,
            'time_spent': self.time_spent,
            'coverage': self.coverage.copy(),
            'total_coverage': np.mean(list(self.coverage.values())),
            'step': self.current_step,
            'individual_reward': reward
        }
        
        return next_state, reward, done, info
    
    def _calculate_reward(self, action: ScanAction, time_cost: float) -> float:
        """
        Calculate reward based on coverage and time.
        
        Reward components:
        1. Coverage gained: Higher coverage increase = higher reward
        2. Time efficiency: Lower time cost = higher reward
        3. Module balance: Evenly covered modules = higher reward
        """
        # Calculate coverage gain from this action
        coverage_before = np.mean(list(self.coverage.values()))
        
        # Simulate coverage after action (without actually applying it yet)
        temp_coverage = self.coverage.copy()
        for module in action.target_modules:
            current = temp_coverage[module]
            gain = action.information_gain * (1.0 - current)
            temp_coverage[module] = min(1.0, current + gain)
        coverage_after = np.mean(list(temp_coverage.values()))
        
        coverage_gain = coverage_after - coverage_before
        
        # Base reward from coverage
        if self.reward_mode == 'coverage':
            reward = coverage_gain * 20.0
        elif self.reward_mode == 'speed':
            reward = (1.0 - time_cost / 15.0) * 10.0
        else:  # balanced
            # Trade-off between coverage and speed
            coverage_component = coverage_gain * 15.0
            speed_component = (1.0 - time_cost / 15.0) * 5.0
            reward = coverage_component + speed_component
        
        # Balance bonus: encourage covering all modules
        coverage_vals = list(self.coverage.values())
        coverage_std = np.std(coverage_vals)
        balance_bonus = max(0, 2.0 - coverage_std) * 0.5  # Reward uniform coverage
        reward += balance_bonus
        
        # Efficiency bonus: complete high coverage quickly
        time_efficiency = max(0, 1.0 - self.time_spent / self.max_time)
        reward += time_efficiency * 0.5
        
        return reward
    
    def render(self, mode: str = 'human') -> None:
        """Render environment state."""
        if mode == 'human':
            logger.info(f"Step: {self.current_step}/{self.episode_length}")
            logger.info(f"Time: {self.time_spent:.1f}s / {self.max_time:.1f}s")
            logger.info(f"Coverage: {self.coverage}")
            logger.info(f"Avg Coverage: {np.mean(list(self.coverage.values())):.2%}")
    
    def seed(self, seed: int = None) -> None:
        """Set random seed."""
        if seed is not None:
            np.random.seed(seed)
            logger.debug(f"Random seed set to {seed}")
    
    def close(self) -> None:
        """Close environment."""
        logger.debug("Environment closed")
