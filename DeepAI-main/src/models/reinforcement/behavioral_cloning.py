"""
Behavioral Cloning Module
Pre-training RL agent on expert demonstrations
"""

import numpy as np
import logging
from typing import Tuple, List, Dict
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

logger = logging.getLogger(__name__)


class BehavioralClongNetwork(nn.Module):
    """
    Supervised network for behavioral cloning.
    Maps states to action labels for imitation learning.
    """
    
    def __init__(self, state_dim: int = 32, action_dim: int = 10, hidden_dim: int = 128):
        """
        Initialize behavioral cloning network.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Number of discrete actions
            hidden_dim: Hidden layer dimension
        """
        super(BehavioralClongNetwork, self).__init__()
        
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 64)
        self.fc3 = nn.Linear(64, action_dim)
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            state: State tensor (batch_size, state_dim)
            
        Returns:
            Action logits (batch_size, action_dim)
        """
        x = self.relu(self.fc1(state))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        action_logits = self.fc3(x)
        
        return action_logits


class BehavioralCloning:
    """
    Behavioral cloning module for pre-training RL agent.
    
    Learns policy from expert demonstrations using supervised learning.
    Reduces training time and improves initial performance.
    """
    
    def __init__(
        self,
        state_dim: int = 32,
        action_dim: int = 10,
        learning_rate: float = 1e-3,
        device: str = 'cpu'
    ):
        """
        Initialize behavioral cloning module.
        
        Args:
            state_dim: State space dimension
            action_dim: Action space dimension
            learning_rate: Learning rate for supervised training
            device: 'cpu' or 'cuda'
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.device = torch.device(device)
        
        # Network for behavioral cloning
        self.policy_net = BehavioralClongNetwork(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss()
        
        # Training statistics
        self.training_stats = {
            'loss': [],
            'accuracy': [],
            'epoch': []
        }
    
    def collect_expert_demonstrations(self, num_trajectories: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate expert demonstrations using heuristic policy.
        
        This creates synthetic expert trajectories that follow a reasonable
        heuristic: prioritize high-information actions, respect time budget.
        
        Args:
            num_trajectories: Number of expert trajectories to generate
            
        Returns:
            expert_states, expert_actions
        """
        expert_states = []
        expert_actions = []
        
        # Expert heuristic policy
        # Prefers: deep scans (3,4,5) for high gain, respects time
        for traj in range(num_trajectories):
            # Random trajectory length (10-50 steps)
            traj_length = np.random.randint(10, 51)
            
            cumulative_time = 0
            time_budget = 45.0
            action_times = [2, 3, 1.5, 5, 8, 4, 2.5, 6, 3.5, 15]  # From scanning_env
            
            for step in range(traj_length):
                # Random state
                state = np.random.randn(self.state_dim).astype(np.float32)
                state = np.clip(state, -1, 1)  # Normalize
                
                remaining_time = time_budget - cumulative_time
                
                # Expert heuristic: prefer actions with good information/time ratio
                # Deep scans (3,4,5): high gain (0.6-0.8), moderate time (4-8s)
                # Baseline scans (0,1,2): low-moderate gain (0.2-0.3), low time (1.5-3s)
                # Specialized (6,7,8): moderate gain (0.4-0.6), moderate time (2.5-6s)
                # Complete scan (9): high gain (0.95), high time (15s) - use if time permits
                
                # Action selection heuristic
                if remaining_time > 10:
                    # Plenty of time: choose high-gain actions
                    action = np.random.choice([3, 4, 5, 9], p=[0.3, 0.3, 0.2, 0.2])
                elif remaining_time > 5:
                    # Medium time: deep scans
                    action = np.random.choice([3, 4, 5], p=[0.4, 0.4, 0.2])
                elif remaining_time > 3:
                    # Low time: baseline or specialized
                    action = np.random.choice([0, 1, 2, 6], p=[0.3, 0.3, 0.2, 0.2])
                else:
                    # Very low time: fast actions only
                    action = np.random.choice([2, 6], p=[0.6, 0.4])
                
                expert_states.append(state)
                expert_actions.append(action)
                cumulative_time += action_times[action]
                
                # Terminate if time budget exceeded
                if cumulative_time >= time_budget:
                    break
        
        return np.array(expert_states), np.array(expert_actions)
    
    def train(
        self,
        expert_states: np.ndarray,
        expert_actions: np.ndarray,
        num_epochs: int = 10,
        batch_size: int = 32,
        validation_split: float = 0.2
    ) -> Dict[str, List[float]]:
        """
        Train policy network on expert demonstrations.
        
        Args:
            expert_states: Expert state trajectories
            expert_actions: Expert action trajectories
            num_epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Fraction of data for validation
            
        Returns:
            Training statistics
        """
        # Convert to tensors
        states_tensor = torch.FloatTensor(expert_states).to(self.device)
        actions_tensor = torch.LongTensor(expert_actions).to(self.device)
        
        # Split into train/validation
        num_samples = len(expert_states)
        num_train = int(num_samples * (1 - validation_split))
        
        indices = np.random.permutation(num_samples)
        train_indices = indices[:num_train]
        val_indices = indices[num_train:]
        
        train_states = states_tensor[train_indices]
        train_actions = actions_tensor[train_indices]
        val_states = states_tensor[val_indices] if len(val_indices) > 0 else None
        val_actions = actions_tensor[val_indices] if len(val_indices) > 0 else None
        
        # Create data loader
        train_dataset = TensorDataset(train_states, train_actions)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        train_losses = []
        val_losses = []
        train_accuracies = []
        val_accuracies = []
        
        for epoch in range(num_epochs):
            # Training phase
            self.policy_net.train()
            epoch_loss = 0
            epoch_correct = 0
            epoch_total = 0
            
            for batch_states, batch_actions in train_loader:
                # Forward pass
                logits = self.policy_net(batch_states)
                loss = self.criterion(logits, batch_actions)
                
                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
                # Statistics
                epoch_loss += loss.item() * len(batch_states)
                _, predicted = torch.max(logits, 1)
                epoch_correct += (predicted == batch_actions).sum().item()
                epoch_total += len(batch_states)
            
            train_loss = epoch_loss / epoch_total
            train_acc = epoch_correct / epoch_total
            train_losses.append(train_loss)
            train_accuracies.append(train_acc)
            
            # Validation phase
            if val_states is not None:
                self.policy_net.eval()
                with torch.no_grad():
                    val_logits = self.policy_net(val_states)
                    val_loss = self.criterion(val_logits, val_actions)
                    _, val_predicted = torch.max(val_logits, 1)
                    val_correct = (val_predicted == val_actions).sum().item()
                    val_acc = val_correct / len(val_actions)
                
                val_losses.append(val_loss.item())
                val_accuracies.append(val_acc)
                
                logger.info(
                    f"Epoch {epoch + 1}/{num_epochs} - "
                    f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f} - "
                    f"Val Loss: {val_loss.item():.4f}, Val Acc: {val_acc:.4f}"
                )
            else:
                logger.info(
                    f"Epoch {epoch + 1}/{num_epochs} - "
                    f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}"
                )
        
        return {
            'train_loss': train_losses,
            'train_accuracy': train_accuracies,
            'val_loss': val_losses,
            'val_accuracy': val_accuracies
        }
    
    def predict_action(self, state: np.ndarray, use_argmax: bool = True) -> int:
        """
        Predict action for given state using behavioral cloning policy.
        
        Args:
            state: State vector
            use_argmax: If True, use argmax; if False, sample from distribution
            
        Returns:
            Predicted action
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        self.policy_net.eval()
        with torch.no_grad():
            logits = self.policy_net(state_tensor)
            
            if use_argmax:
                action = torch.argmax(logits, dim=1).item()
            else:
                # Sample from softmax distribution
                probs = torch.softmax(logits, dim=1)
                action = torch.multinomial(probs, 1).item()
        
        return action
    
    def transfer_to_rl_agent(self, ppo_agent) -> None:
        """
        Transfer learned policy to RL agent.
        Copies behavioral cloning network weights to PPO actor network.
        
        Args:
            ppo_agent: PPO agent to initialize
        """
        # Initialize actor networks similarly
        ppo_actor_critic = ppo_agent.actor_critic
        
        # Transfer feature extraction layers (fc1, fc2)
        with torch.no_grad():
            ppo_actor_critic.fc1.weight.copy_(self.policy_net.fc1.weight)
            ppo_actor_critic.fc1.bias.copy_(self.policy_net.fc1.bias)
            
            ppo_actor_critic.fc2.weight.copy_(self.policy_net.fc2.weight)
            ppo_actor_critic.fc2.bias.copy_(self.policy_net.fc2.bias)
            
            # Transfer actor head (output layer)
            # Both networks have same action dimension
            ppo_actor_critic.actor_head.weight.copy_(self.policy_net.fc3.weight)
            ppo_actor_critic.actor_head.bias.copy_(self.policy_net.fc3.bias)
        
        logger.info("Behavioral cloning weights transferred to PPO agent")
    
    def save(self, filepath: str) -> None:
        """Save behavioral cloning network."""
        torch.save({
            'policy_net': self.policy_net.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'training_stats': self.training_stats
        }, filepath)
        logger.info(f"Behavioral cloning model saved to {filepath}")
    
    def load(self, filepath: str) -> None:
        """Load behavioral cloning network."""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.policy_net.load_state_dict(checkpoint['policy_net'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.training_stats = checkpoint.get('training_stats', self.training_stats)
        logger.info(f"Behavioral cloning model loaded from {filepath}")
