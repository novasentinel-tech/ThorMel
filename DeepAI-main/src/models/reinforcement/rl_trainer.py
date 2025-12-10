"""
RL Training Pipeline
Orchestrates training of PPO agent with behavioral cloning pre-training
"""

import numpy as np
import logging
from typing import Dict, Tuple, Optional
import torch
from datetime import datetime
from pathlib import Path

from src.models.reinforcement.scanning_env import ScanningEnvironment
from src.models.reinforcement.ppo_agent_impl import PPOAgent
from src.models.reinforcement.behavioral_cloning import BehavioralCloning

logger = logging.getLogger(__name__)


class RLTrainingPipeline:
    """
    Complete RL training pipeline.
    
    Process:
    1. Generate expert demonstrations
    2. Pre-train using behavioral cloning
    3. Fine-tune with PPO on environment
    4. Monitor convergence
    5. Evaluate performance
    """
    
    def __init__(
        self,
        env: ScanningEnvironment,
        ppo_agent: PPOAgent,
        output_dir: str = "checkpoints/rl"
    ):
        """
        Initialize training pipeline.
        
        Args:
            env: Scanning environment
            ppo_agent: PPO agent to train
            output_dir: Directory for checkpoints
        """
        self.env = env
        self.agent = ppo_agent
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Training configuration
        self.config = {
            'max_episodes': 10000,
            'update_frequency': 20,  # Update after 20 episodes
            'max_episode_steps': 100,
            'ppo_epochs': 4,
            'batch_size': 64,
            'convergence_threshold': 50,  # Episodes for moving average
            'target_reward': 50  # Target average reward
        }
        
        # Training history
        self.history = {
            'episode': [],
            'reward': [],
            'episode_length': [],
            'policy_loss': [],
            'value_loss': [],
            'entropy': [],
            'moving_avg_reward': []
        }
        
        self.behavioral_cloning = BehavioralCloning(
            state_dim=env.state_dim,
            action_dim=10,
            device=ppo_agent.device
        )
    
    def run_episode(self) -> Tuple[float, int]:
        """
        Run single episode with current policy.
        
        Returns:
            episode_reward, episode_length
        """
        state = self.env.reset()
        episode_reward = 0
        episode_length = 0
        
        for step in range(self.config['max_episode_steps']):
            # Select action
            action, log_prob = self.agent.select_action(state)
            
            # Get value estimate
            value = self.agent.get_value(state)
            
            # Environment step
            next_state, reward, done, info = self.env.step(action)
            
            # Store transition
            self.agent.store_transition(state, action, reward, value, log_prob, done)
            
            episode_reward += reward
            episode_length += 1
            state = next_state
            
            if done:
                break
        
        return episode_reward, episode_length
    
    def training_loop(
        self,
        num_episodes: Optional[int] = None,
        use_behavioral_cloning: bool = True
    ) -> Dict:
        """
        Main training loop.
        
        Args:
            num_episodes: Number of episodes to train (uses config if None)
            use_behavioral_cloning: Whether to pre-train with behavioral cloning
            
        Returns:
            Training history
        """
        if num_episodes is None:
            num_episodes = self.config['max_episodes']
        
        logger.info("=" * 80)
        logger.info("Starting RL Training Pipeline")
        logger.info(f"Max episodes: {num_episodes}")
        logger.info(f"Behavioral cloning pre-training: {use_behavioral_cloning}")
        logger.info("=" * 80)
        
        # Phase 1: Behavioral cloning pre-training
        if use_behavioral_cloning:
            logger.info("\n" + "=" * 80)
            logger.info("Phase 1: Behavioral Cloning Pre-training")
            logger.info("=" * 80)
            
            # Collect expert demonstrations
            logger.info("Collecting expert demonstrations...")
            expert_states, expert_actions = self.behavioral_cloning.collect_expert_demonstrations(
                num_trajectories=100
            )
            logger.info(f"Generated {len(expert_states)} expert transitions")
            
            # Train behavioral cloning
            logger.info("Training behavioral cloning network...")
            bc_stats = self.behavioral_cloning.train(
                expert_states,
                expert_actions,
                num_epochs=10,
                batch_size=32,
                validation_split=0.2
            )
            
            # Transfer weights to PPO agent
            logger.info("Transferring behavioral cloning weights to PPO agent...")
            self.behavioral_cloning.transfer_to_rl_agent(self.agent)
            
            logger.info(f"Behavioral cloning final train accuracy: {bc_stats['train_accuracy'][-1]:.4f}")
            if bc_stats['val_accuracy']:
                logger.info(f"Behavioral cloning final val accuracy: {bc_stats['val_accuracy'][-1]:.4f}")
        
        # Phase 2: PPO fine-tuning
        logger.info("\n" + "=" * 80)
        logger.info("Phase 2: PPO Fine-tuning")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        episode_rewards = []
        
        for episode in range(num_episodes):
            # Run episode
            episode_reward, episode_length = self.run_episode()
            episode_rewards.append(episode_reward)
            
            # Update policy every N episodes
            if (episode + 1) % self.config['update_frequency'] == 0:
                # Get last state value
                state = self.env.reset()
                last_value = self.agent.get_value(state)
                
                # Compute advantages
                advantages, returns = self.agent.compute_advantages(last_value)
                
                # Update
                update_stats = self.agent.update(
                    advantages,
                    returns,
                    num_epochs=self.config['ppo_epochs'],
                    batch_size=self.config['batch_size']
                )
                
                # Record history
                self.history['episode'].append(episode + 1)
                self.history['reward'].append(np.mean(episode_rewards[-self.config['update_frequency']:]))
                self.history['policy_loss'].append(update_stats['policy_loss'])
                self.history['value_loss'].append(update_stats['value_loss'])
                self.history['entropy'].append(update_stats['entropy'])
                
                # Moving average reward
                moving_avg = np.mean(episode_rewards[-self.config['convergence_threshold']:])
                self.history['moving_avg_reward'].append(moving_avg)
                
                # Logging
                elapsed = (datetime.now() - start_time).total_seconds()
                eps_per_sec = (episode + 1) / elapsed if elapsed > 0 else 0
                
                logger.info(
                    f"Episode {episode + 1:5d} | "
                    f"Avg Reward: {self.history['reward'][-1]:8.2f} | "
                    f"Moving Avg: {moving_avg:8.2f} | "
                    f"Policy Loss: {update_stats['policy_loss']:8.4f} | "
                    f"Value Loss: {update_stats['value_loss']:8.4f} | "
                    f"Entropy: {update_stats['entropy']:8.4f} | "
                    f"Speed: {eps_per_sec:.1f} eps/s"
                )
                
                # Early stopping
                if len(self.history['moving_avg_reward']) > 1:
                    if moving_avg >= self.config['target_reward']:
                        logger.info(f"\n✓ Convergence achieved! Moving average: {moving_avg:.2f}")
                        break
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"\nTraining completed in {elapsed:.1f} seconds")
        
        return self.history
    
    def evaluate(self, num_episodes: int = 100) -> Dict:
        """
        Evaluate trained agent.
        
        Args:
            num_episodes: Number of evaluation episodes
            
        Returns:
            Evaluation statistics
        """
        logger.info(f"\nEvaluating agent for {num_episodes} episodes...")
        
        self.agent.actor_critic.eval()
        rewards = []
        lengths = []
        
        with torch.no_grad():
            for _ in range(num_episodes):
                state = self.env.reset()
                episode_reward = 0
                episode_length = 0
                
                for step in range(self.config['max_episode_steps']):
                    # Greedy action selection (no sampling)
                    action_logits, _ = self.agent.actor_critic(
                        torch.FloatTensor(state).unsqueeze(0).to(self.agent.device)
                    )
                    action = torch.argmax(action_logits, dim=1).item()
                    
                    state, reward, done, info = self.env.step(action)
                    episode_reward += reward
                    episode_length += 1
                    
                    if done:
                        break
                
                rewards.append(episode_reward)
                lengths.append(episode_length)
        
        self.agent.actor_critic.train()
        
        eval_stats = {
            'mean_reward': np.mean(rewards),
            'std_reward': np.std(rewards),
            'max_reward': np.max(rewards),
            'min_reward': np.min(rewards),
            'mean_length': np.mean(lengths),
            'std_length': np.std(lengths)
        }
        
        logger.info(f"Evaluation Results:")
        logger.info(f"  Mean Reward: {eval_stats['mean_reward']:.2f} ± {eval_stats['std_reward']:.2f}")
        logger.info(f"  Max Reward: {eval_stats['max_reward']:.2f}")
        logger.info(f"  Mean Episode Length: {eval_stats['mean_length']:.1f}")
        
        return eval_stats
    
    def save_checkpoint(self, name: str = "final") -> None:
        """Save training checkpoint."""
        checkpoint_path = self.output_dir / f"checkpoint_{name}.pt"
        
        torch.save({
            'agent_state': self.agent.actor_critic.state_dict(),
            'optimizer_state': self.agent.optimizer.state_dict(),
            'history': self.history,
            'config': self.config
        }, checkpoint_path)
        
        logger.info(f"Checkpoint saved to {checkpoint_path}")
    
    def load_checkpoint(self, name: str = "final") -> None:
        """Load training checkpoint."""
        checkpoint_path = self.output_dir / f"checkpoint_{name}.pt"
        checkpoint = torch.load(checkpoint_path, map_location=self.agent.device)
        
        self.agent.actor_critic.load_state_dict(checkpoint['agent_state'])
        self.agent.optimizer.load_state_dict(checkpoint['optimizer_state'])
        self.history = checkpoint['history']
        self.config = checkpoint['config']
        
        logger.info(f"Checkpoint loaded from {checkpoint_path}")
    
    def plot_training_curves(self, save_path: Optional[str] = None) -> None:
        """Plot training curves."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.warning("matplotlib not installed, skipping plot generation")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Reward
        axes[0, 0].plot(self.history['episode'], self.history['reward'], label='Avg Reward')
        axes[0, 0].plot(self.history['episode'], self.history['moving_avg_reward'], label='Moving Avg')
        axes[0, 0].axhline(y=self.config['target_reward'], color='r', linestyle='--', label='Target')
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Reward')
        axes[0, 0].set_title('Episode Rewards')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Policy Loss
        axes[0, 1].plot(self.history['episode'], self.history['policy_loss'])
        axes[0, 1].set_xlabel('Episode')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].set_title('Policy Loss')
        axes[0, 1].grid(True)
        
        # Value Loss
        axes[1, 0].plot(self.history['episode'], self.history['value_loss'])
        axes[1, 0].set_xlabel('Episode')
        axes[1, 0].set_ylabel('Loss')
        axes[1, 0].set_title('Value Loss')
        axes[1, 0].grid(True)
        
        # Entropy
        axes[1, 1].plot(self.history['episode'], self.history['entropy'])
        axes[1, 1].set_xlabel('Episode')
        axes[1, 1].set_ylabel('Entropy')
        axes[1, 1].set_title('Policy Entropy')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Training curves saved to {save_path}")
        else:
            plt.savefig(self.output_dir / "training_curves.png")
            logger.info(f"Training curves saved to {self.output_dir / 'training_curves.png'}")
        
        plt.close()
