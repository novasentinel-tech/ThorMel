"""
Phase D RL Inference Script
Use trained PPO agent for scanning strategy optimization
"""

import argparse
import logging
import sys
from pathlib import Path
import numpy as np
import torch

# Configure import paths
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from models.reinforcement.scanning_env import ScanningEnvironment
from models.reinforcement.ppo_agent_impl import PPOAgent
from models.reinforcement.rl_trainer import RLTrainingPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScanningStrategyOptimizer:
    """
    Use trained RL agent to optimize scanning strategies.
    Provides interface for selecting optimal scanning actions.
    """
    
    def __init__(self, agent_path: str, device: str = 'cpu'):
        """
        Initialize optimizer with trained agent.
        
        Args:
            agent_path: Path to saved agent checkpoint
            device: 'cpu' or 'cuda'
        """
        self.device = torch.device(device)
        
        # Create and load agent
        self.agent = PPOAgent(device=device)
        self.agent.load(agent_path)
        
        logger.info(f"Loaded agent from {agent_path}")
    
    def optimize_strategy(
        self,
        initial_state: np.ndarray,
        time_budget: float = 45.0,
        greedy: bool = True
    ) -> dict:
        """
        Generate optimized scanning strategy for a domain.
        
        Args:
            initial_state: Domain state vector (32-dimensional)
            time_budget: Time budget in seconds
            greedy: Use greedy action selection (True) or stochastic (False)
            
        Returns:
            Dictionary with strategy details
        """
        action_names = {
            0: 'baseline_http',
            1: 'baseline_tls',
            2: 'baseline_dns',
            3: 'deep_http',
            4: 'deep_tls',
            5: 'deep_dns',
            6: 'whois_registry',
            7: 'port_scanning',
            8: 'tech_detection',
            9: 'complete_scan'
        }
        
        action_times = [2, 3, 1.5, 5, 8, 4, 2.5, 6, 3.5, 15]
        action_gains = [0.3, 0.3, 0.2, 0.7, 0.8, 0.6, 0.4, 0.6, 0.5, 0.95]
        
        state = initial_state.copy()
        strategy = []
        cumulative_time = 0
        cumulative_gain = 0
        
        self.agent.actor_critic.eval()
        
        with torch.no_grad():
            for step in range(100):  # Max 100 steps
                # Get action
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                action_logits, value = self.agent.actor_critic(state_tensor)
                
                if greedy:
                    action = torch.argmax(action_logits, dim=1).item()
                else:
                    probs = torch.softmax(action_logits, dim=1)
                    action = torch.multinomial(probs, 1).item()
                
                # Check time budget
                action_time = action_times[action]
                if cumulative_time + action_time > time_budget:
                    logger.info(f"Time budget exceeded at step {step + 1}")
                    break
                
                # Record action
                cumulative_time += action_time
                cumulative_gain += action_gains[action]
                
                strategy.append({
                    'step': step + 1,
                    'action': action,
                    'action_name': action_names[action],
                    'time_cost': action_time,
                    'cumulative_time': cumulative_time,
                    'information_gain': action_gains[action],
                    'cumulative_gain': min(cumulative_gain, 1.0),  # Capped at 1.0
                    'value_estimate': value.item(),
                    'time_remaining': time_budget - cumulative_time
                })
                
                # Simulate state update (simplified)
                state = np.random.randn(len(initial_state)) * 0.1 + initial_state * 0.9
        
        return {
            'strategy': strategy,
            'total_steps': len(strategy),
            'total_time': cumulative_time,
            'total_gain': min(cumulative_gain, 1.0),
            'efficiency': cumulative_gain / cumulative_time if cumulative_time > 0 else 0,
            'time_remaining': time_budget - cumulative_time
        }


def evaluate_trained_agent(
    checkpoint_path: str,
    num_episodes: int = 100,
    device: str = 'cpu'
):
    """Evaluate trained agent on environment."""
    logger.info("=" * 80)
    logger.info("Agent Evaluation")
    logger.info("=" * 80)
    
    # Load agent
    env = ScanningEnvironment()
    agent = PPOAgent(device=device)
    agent.load(checkpoint_path)
    
    # Evaluation loop
    agent.actor_critic.eval()
    rewards = []
    lengths = []
    coverage_values = []
    
    with torch.no_grad():
        for episode in range(num_episodes):
            state = env.reset()
            episode_reward = 0
            episode_length = 0
            
            for step in range(100):
                # Greedy action
                action_logits, _ = agent.actor_critic(
                    torch.FloatTensor(state).unsqueeze(0).to(agent.device)
                )
                action = torch.argmax(action_logits, dim=1).item()
                
                state, reward, done, info = env.step(action)
                episode_reward += reward
                episode_length += 1
                
                if done:
                    break
            
            rewards.append(episode_reward)
            lengths.append(episode_length)
            coverage_values.append(info.get('coverage', 0))
            
            if (episode + 1) % 20 == 0:
                logger.info(f"Episode {episode + 1}/{num_episodes}")
    
    # Statistics
    eval_stats = {
        'mean_reward': np.mean(rewards),
        'std_reward': np.std(rewards),
        'max_reward': np.max(rewards),
        'min_reward': np.min(rewards),
        'mean_length': np.mean(lengths),
        'mean_coverage': np.mean(coverage_values)
    }
    
    logger.info("\n" + "=" * 80)
    logger.info("Evaluation Results")
    logger.info("=" * 80)
    logger.info(f"Mean Reward:       {eval_stats['mean_reward']:8.2f} ± {eval_stats['std_reward']:8.2f}")
    logger.info(f"Max Reward:        {eval_stats['max_reward']:8.2f}")
    logger.info(f"Min Reward:        {eval_stats['min_reward']:8.2f}")
    logger.info(f"Mean Episode Len:  {eval_stats['mean_length']:8.1f}")
    logger.info(f"Mean Coverage:     {eval_stats['mean_coverage']:8.2%}")
    
    return eval_stats


def interactive_strategy_planning(
    checkpoint_path: str,
    device: str = 'cpu'
):
    """Interactive strategy planning session."""
    logger.info("=" * 80)
    logger.info("Interactive Scanning Strategy Optimizer")
    logger.info("=" * 80)
    logger.info("Enter domain state characteristics (12 dimensions)")
    logger.info("Type 'quit' to exit")
    logger.info()
    
    optimizer = ScanningStrategyOptimizer(checkpoint_path, device=device)
    
    while True:
        try:
            # Get user input
            print("\n" + "-" * 80)
            domain = input("Domain: ").strip()
            
            if domain.lower() == 'quit':
                break
            
            time_budget = 45.0
            try:
                time_input = input(f"Time budget (default {time_budget}s): ").strip()
                if time_input:
                    time_budget = float(time_input)
            except ValueError:
                logger.warning("Invalid time input, using default")
            
            # Create random state for demo (in reality, would extract from domain data)
            state = np.random.randn(32) * 0.5
            
            # Generate strategy
            result = optimizer.optimize_strategy(state, time_budget=time_budget, greedy=True)
            
            # Display results
            logger.info(f"\nOptimized Strategy for {domain}:")
            logger.info("-" * 80)
            
            for action_info in result['strategy']:
                logger.info(
                    f"Step {action_info['step']:2d}: {action_info['action_name']:18} "
                    f"({action_info['time_cost']:4.1f}s) "
                    f"→ Time: {action_info['cumulative_time']:5.1f}s, "
                    f"Gain: {action_info['cumulative_gain']:5.1%}, "
                    f"Value: {action_info['value_estimate']:6.3f}"
                )
            
            logger.info("-" * 80)
            logger.info(f"Total Steps: {result['total_steps']}")
            logger.info(f"Total Time: {result['total_time']:.1f}s / {time_budget}s")
            logger.info(f"Total Gain: {result['total_gain']:.1%}")
            logger.info(f"Efficiency: {result['efficiency']:.3f} gain/second")
            
        except KeyboardInterrupt:
            logger.info("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


def main(args):
    """Main function."""
    device = 'cuda' if torch.cuda.is_available() and args.cuda else 'cpu'
    logger.info(f"Using device: {device}")
    
    if args.evaluate:
        evaluate_trained_agent(
            args.checkpoint,
            num_episodes=args.eval_episodes,
            device=device
        )
    
    elif args.interactive:
        interactive_strategy_planning(args.checkpoint, device=device)
    
    else:
        logger.error("Please specify --evaluate or --interactive")
        return 1
    
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Inference and evaluation for trained RL agent"
    )
    
    parser.add_argument(
        'checkpoint',
        type=str,
        help='Path to trained agent checkpoint'
    )
    
    parser.add_argument(
        '--evaluate',
        action='store_true',
        help='Evaluate agent on environment'
    )
    
    parser.add_argument(
        '--eval-episodes',
        type=int,
        default=100,
        help='Number of evaluation episodes'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive strategy planning mode'
    )
    
    parser.add_argument(
        '--cuda',
        action='store_true',
        help='Use CUDA if available'
    )
    
    args = parser.parse_args()
    
    sys.exit(main(args))
