"""
PPO Agent Implementation
Proximal Policy Optimization for scanning strategy optimization
"""

import numpy as np
import logging
from typing import Tuple, Dict, Optional, List
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical

logger = logging.getLogger(__name__)


class ActorCritic(nn.Module):
    """
    Actor-Critic network for PPO.
    
    Architecture:
    - Shared layers: 2 hidden layers (128 → 64)
    - Actor head: 64 → 10 (action logits)
    - Critic head: 64 → 1 (value estimate)
    """
    
    def __init__(self, state_dim: int = 32, action_dim: int = 10, hidden_dim: int = 128):
        """
        Initialize Actor-Critic network.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Number of discrete actions
            hidden_dim: Hidden layer dimension
        """
        super(ActorCritic, self).__init__()
        
        # Shared feature extraction
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 64)
        
        # Actor (policy) head
        self.actor_head = nn.Linear(64, action_dim)
        
        # Critic (value) head
        self.critic_head = nn.Linear(64, 1)
        
        # Activation function
        self.relu = nn.ReLU()
        
    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.
        
        Args:
            state: State tensor (batch_size, state_dim)
            
        Returns:
            action_logits, value
        """
        x = self.relu(self.fc1(state))
        x = self.relu(self.fc2(x))
        
        action_logits = self.actor_head(x)
        value = self.critic_head(x)
        
        return action_logits, value


class PPOAgent:
    """
    Proximal Policy Optimization agent for scanning strategy.
    
    Features:
    - Actor-Critic neural network
    - Clipped objective function
    - Advantage estimation (GAE - Generalized Advantage Estimation)
    - Experience replay buffer
    """
    
    def __init__(
        self,
        state_dim: int = 32,
        action_dim: int = 10,
        learning_rate: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_ratio: float = 0.2,
        entropy_coef: float = 0.01,
        value_coef: float = 0.5,
        max_grad_norm: float = 0.5,
        device: str = 'cpu'
    ):
        """
        Initialize PPO agent.
        
        Args:
            state_dim: State space dimension
            action_dim: Action space dimension (10 actions)
            learning_rate: Optimizer learning rate
            gamma: Discount factor for rewards
            gae_lambda: GAE lambda for advantage estimation
            clip_ratio: PPO clipping ratio (epsilon)
            entropy_coef: Entropy loss coefficient
            value_coef: Value loss coefficient
            max_grad_norm: Maximum gradient norm
            device: 'cpu' or 'cuda'
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_ratio = clip_ratio
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.max_grad_norm = max_grad_norm
        self.device = torch.device(device)
        
        # Network
        self.actor_critic = ActorCritic(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.actor_critic.parameters(), lr=learning_rate)
        
        # Experience buffer
        self.clear_buffer()
        
        # Training statistics
        self.training_stats = {
            'episode_rewards': [],
            'policy_loss': [],
            'value_loss': [],
            'entropy': [],
            'clip_fraction': []
        }
        
    def clear_buffer(self) -> None:
        """Clear experience buffer."""
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.log_probs = []
        self.dones = []
    
    def select_action(self, state: np.ndarray) -> Tuple[int, float]:
        """
        Select action using current policy.
        
        Args:
            state: Current state (32-dimensional)
            
        Returns:
            action, log_probability
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            action_logits, value = self.actor_critic(state_tensor)
        
        # Sample action from policy
        probs = torch.softmax(action_logits, dim=-1)
        dist = Categorical(probs)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        
        return action.item(), log_prob.item()
    
    def store_transition(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        value: float,
        log_prob: float,
        done: bool
    ) -> None:
        """
        Store transition in experience buffer.
        
        Args:
            state: State
            action: Action taken
            reward: Reward received
            value: Value estimate
            log_prob: Log probability of action
            done: Episode termination flag
        """
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
        self.dones.append(done)
    
    def compute_advantages(self, last_value: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute advantages using Generalized Advantage Estimation (GAE).
        
        Args:
            last_value: Value of last state (0 if terminal)
            
        Returns:
            advantages, returns (target values)
        """
        advantages = []
        gae = 0
        
        values = self.values + [last_value]
        rewards = self.rewards
        dones = self.dones
        
        # Compute TD residuals and GAE backward
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = last_value
            else:
                next_value = values[t + 1]
            
            # TD residual
            delta = rewards[t] + self.gamma * next_value * (1 - dones[t]) - values[t]
            
            # GAE
            gae = delta + self.gamma * self.gae_lambda * (1 - dones[t]) * gae
            advantages.insert(0, gae)
        
        advantages = np.array(advantages, dtype=np.float32)
        returns = advantages + np.array(self.values, dtype=np.float32)
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        return advantages, returns
    
    def update(
        self,
        advantages: np.ndarray,
        returns: np.ndarray,
        num_epochs: int = 4,
        batch_size: int = 64
    ) -> Dict[str, float]:
        """
        Update policy and value function using PPO loss.
        
        Args:
            advantages: Computed advantages
            returns: Target returns
            num_epochs: Number of training epochs
            batch_size: Batch size for updates
            
        Returns:
            Dictionary with loss statistics
        """
        states = torch.FloatTensor(np.array(self.states)).to(self.device)
        actions = torch.LongTensor(self.actions).to(self.device)
        old_log_probs = torch.FloatTensor(self.log_probs).to(self.device)
        advantages_t = torch.FloatTensor(advantages).to(self.device)
        returns_t = torch.FloatTensor(returns).to(self.device)
        
        # Store old policy for KL divergence check
        with torch.no_grad():
            old_action_logits, _ = self.actor_critic(states)
            old_probs = torch.softmax(old_action_logits, dim=-1)
        
        policy_losses = []
        value_losses = []
        entropies = []
        clip_fractions = []
        
        num_samples = len(self.states)
        indices = np.arange(num_samples)
        
        for epoch in range(num_epochs):
            np.random.shuffle(indices)
            
            for start in range(0, num_samples, batch_size):
                end = min(start + batch_size, num_samples)
                batch_indices = indices[start:end]
                
                # Get batch
                batch_states = states[batch_indices]
                batch_actions = actions[batch_indices]
                batch_old_log_probs = old_log_probs[batch_indices]
                batch_advantages = advantages_t[batch_indices]
                batch_returns = returns_t[batch_indices]
                
                # Forward pass
                action_logits, values = self.actor_critic(batch_states)
                probs = torch.softmax(action_logits, dim=-1)
                dist = Categorical(probs)
                
                # Log probabilities for batch actions
                new_log_probs = dist.log_prob(batch_actions)
                
                # Policy loss (PPO clipped objective)
                ratio = torch.exp(new_log_probs - batch_old_log_probs)
                clipped_ratio = torch.clamp(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                policy_loss = -torch.min(ratio * batch_advantages, clipped_ratio * batch_advantages).mean()
                
                # Value loss
                value_loss = nn.MSELoss()(values.squeeze(-1), batch_returns)
                
                # Entropy loss (encourage exploration)
                entropy = dist.entropy().mean()
                
                # Total loss
                loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy
                
                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.actor_critic.parameters(), self.max_grad_norm)
                self.optimizer.step()
                
                # Statistics
                policy_losses.append(policy_loss.item())
                value_losses.append(value_loss.item())
                entropies.append(entropy.item())
                
                # Clip fraction (for debugging)
                clip_fraction = (ratio > 1 + self.clip_ratio).float().mean()
                clip_fraction += ((1 - self.clip_ratio) > ratio).float().mean()
                clip_fractions.append(clip_fraction.item())
        
        # Clear buffer
        self.clear_buffer()
        
        return {
            'policy_loss': np.mean(policy_losses),
            'value_loss': np.mean(value_losses),
            'entropy': np.mean(entropies),
            'clip_fraction': np.mean(clip_fractions)
        }
    
    def save(self, filepath: str) -> None:
        """Save agent to file."""
        torch.save({
            'actor_critic': self.actor_critic.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'training_stats': self.training_stats
        }, filepath)
        logger.info(f"Agent saved to {filepath}")
    
    def load(self, filepath: str) -> None:
        """Load agent from file."""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.actor_critic.load_state_dict(checkpoint['actor_critic'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.training_stats = checkpoint.get('training_stats', self.training_stats)
        logger.info(f"Agent loaded from {filepath}")
    
    def get_value(self, state: np.ndarray) -> float:
        """
        Get value estimate for a state.
        
        Args:
            state: State vector
            
        Returns:
            Value estimate
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            _, value = self.actor_critic(state_tensor)
        
        return value.item()
    
    def get_training_stats(self) -> Dict:
        """Get training statistics."""
        return {
            'avg_reward': np.mean(self.training_stats['episode_rewards']) if self.training_stats['episode_rewards'] else 0,
            'avg_policy_loss': np.mean(self.training_stats['policy_loss']) if self.training_stats['policy_loss'] else 0,
            'avg_value_loss': np.mean(self.training_stats['value_loss']) if self.training_stats['value_loss'] else 0,
            'avg_entropy': np.mean(self.training_stats['entropy']) if self.training_stats['entropy'] else 0,
        }
