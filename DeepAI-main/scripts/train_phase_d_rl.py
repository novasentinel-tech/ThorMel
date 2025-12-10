"""
Phase D RL Training Script
Main training entry point for PPO-based scanning strategy optimization
"""

import argparse
import logging
import sys
from pathlib import Path

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


def main(args):
    """Main training function."""
    
    # Setup device
    import torch
    device = 'cuda' if torch.cuda.is_available() and args.cuda else 'cpu'
    logger.info(f"Using device: {device}")
    
    # Create environment
    logger.info("Initializing scanning environment...")
    env = ScanningEnvironment(
        max_time=args.max_time,
        state_dim=32,
        episode_length=args.episode_length,
        reward_mode=args.reward_mode
    )
    logger.info(f"Environment initialized: {args.reward_mode} reward mode, max_time={args.max_time}s")
    
    # Create PPO agent
    logger.info("Initializing PPO agent...")
    agent = PPOAgent(
        state_dim=32,
        action_dim=10,
        learning_rate=args.learning_rate,
        gamma=args.gamma,
        gae_lambda=args.gae_lambda,
        clip_ratio=args.clip_ratio,
        entropy_coef=args.entropy_coef,
        value_coef=args.value_coef,
        device=device
    )
    logger.info(f"PPO agent initialized (lr={args.learning_rate})")
    
    # Create training pipeline
    logger.info("Initializing training pipeline...")
    pipeline = RLTrainingPipeline(env, agent, output_dir=args.output_dir)
    
    # Configure pipeline
    pipeline.config['max_episodes'] = args.max_episodes
    pipeline.config['update_frequency'] = args.update_frequency
    pipeline.config['max_episode_steps'] = args.episode_length
    pipeline.config['ppo_epochs'] = args.ppo_epochs
    pipeline.config['batch_size'] = args.batch_size
    pipeline.config['convergence_threshold'] = args.convergence_threshold
    pipeline.config['target_reward'] = args.target_reward
    
    logger.info(f"Training config: {pipeline.config}")
    
    # Run training
    logger.info("\n" + "=" * 80)
    logger.info("Starting RL training...")
    logger.info("=" * 80)
    
    try:
        history = pipeline.training_loop(
            num_episodes=args.max_episodes,
            use_behavioral_cloning=args.use_behavioral_cloning
        )
        
        # Save checkpoint
        pipeline.save_checkpoint("final")
        
        # Run evaluation
        if args.evaluate:
            logger.info("\n" + "=" * 80)
            logger.info("Running evaluation...")
            logger.info("=" * 80)
            
            eval_stats = pipeline.evaluate(num_episodes=args.eval_episodes)
            logger.info(f"Evaluation complete:")
            logger.info(f"  Mean reward: {eval_stats['mean_reward']:.2f}")
            logger.info(f"  Max reward: {eval_stats['max_reward']:.2f}")
            logger.info(f"  Mean length: {eval_stats['mean_length']:.1f}")
        
        # Plot training curves if matplotlib available
        try:
            pipeline.plot_training_curves()
            logger.info("Training curves saved")
        except Exception as e:
            logger.warning(f"Could not save training curves: {e}")
        
        logger.info("\n✓ Training completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n✗ Training interrupted by user")
        pipeline.save_checkpoint("interrupted")
        return 1
    except Exception as e:
        logger.error(f"\n✗ Training failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Train PPO agent for scanning strategy optimization"
    )
    
    # Environment settings
    parser.add_argument(
        '--max-time',
        type=float,
        default=45.0,
        help='Maximum time budget per episode (seconds)'
    )
    parser.add_argument(
        '--episode-length',
        type=int,
        default=100,
        help='Maximum steps per episode'
    )
    parser.add_argument(
        '--reward-mode',
        type=str,
        choices=['coverage', 'speed', 'balanced'],
        default='balanced',
        help='Reward function mode'
    )
    
    # Training settings
    parser.add_argument(
        '--max-episodes',
        type=int,
        default=10000,
        help='Total training episodes'
    )
    parser.add_argument(
        '--update-frequency',
        type=int,
        default=20,
        help='Update policy every N episodes'
    )
    parser.add_argument(
        '--ppo-epochs',
        type=int,
        default=4,
        help='PPO training epochs per update'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=64,
        help='Batch size for PPO updates'
    )
    
    # Agent settings
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=3e-4,
        help='PPO learning rate'
    )
    parser.add_argument(
        '--gamma',
        type=float,
        default=0.99,
        help='Discount factor'
    )
    parser.add_argument(
        '--gae-lambda',
        type=float,
        default=0.95,
        help='GAE lambda parameter'
    )
    parser.add_argument(
        '--clip-ratio',
        type=float,
        default=0.2,
        help='PPO clipping ratio'
    )
    parser.add_argument(
        '--entropy-coef',
        type=float,
        default=0.01,
        help='Entropy loss coefficient'
    )
    parser.add_argument(
        '--value-coef',
        type=float,
        default=0.5,
        help='Value loss coefficient'
    )
    
    # Convergence settings
    parser.add_argument(
        '--convergence-threshold',
        type=int,
        default=50,
        help='Episodes for moving average convergence check'
    )
    parser.add_argument(
        '--target-reward',
        type=float,
        default=50,
        help='Target average reward for convergence'
    )
    
    # Behavioral cloning
    parser.add_argument(
        '--use-behavioral-cloning',
        action='store_true',
        help='Use behavioral cloning pre-training'
    )
    
    # Output and evaluation
    parser.add_argument(
        '--output-dir',
        type=str,
        default='checkpoints/rl',
        help='Output directory for checkpoints'
    )
    parser.add_argument(
        '--evaluate',
        action='store_true',
        help='Run evaluation after training'
    )
    parser.add_argument(
        '--eval-episodes',
        type=int,
        default=100,
        help='Number of evaluation episodes'
    )
    
    # Device
    parser.add_argument(
        '--cuda',
        action='store_true',
        help='Use CUDA if available'
    )
    
    args = parser.parse_args()
    
    sys.exit(main(args))
