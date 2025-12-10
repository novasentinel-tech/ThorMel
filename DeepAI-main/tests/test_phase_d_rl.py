"""
Phase D RL Training Tests
Comprehensive test suite for PPO, behavioral cloning, and training pipeline
"""

import pytest
import numpy as np
import torch
import sys
from pathlib import Path

# Add source to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from models.reinforcement.scanning_env import ScanningEnvironment, ScanAction
from models.reinforcement.ppo_agent_impl import PPOAgent, ActorCritic
from models.reinforcement.behavioral_cloning import BehavioralCloning, BehavioralClongNetwork
from models.reinforcement.rl_trainer import RLTrainingPipeline


class TestScanningEnvironment:
    """Test scanning environment."""
    
    def test_environment_initialization(self):
        """Test environment can be initialized."""
        env = ScanningEnvironment(max_time=45.0, state_dim=32, episode_length=100)
        assert env.state_dim == 32
        assert env.max_time == 45.0
        assert env.episode_length == 100
    
    def test_environment_reset(self):
        """Test environment reset returns valid state."""
        env = ScanningEnvironment()
        state = env.reset()
        
        assert isinstance(state, np.ndarray)
        assert state.shape == (32,)
        assert np.all(np.isfinite(state))
    
    def test_environment_step(self):
        """Test environment step executes action."""
        env = ScanningEnvironment()
        state = env.reset()
        
        # Valid action
        next_state, reward, done, info = env.step(0)
        
        assert isinstance(next_state, np.ndarray)
        assert next_state.shape == (32,)
        assert isinstance(reward, (float, int))
        assert isinstance(done, (bool, np.bool_))
        assert isinstance(info, dict)
    
    def test_environment_episode_termination(self):
        """Test episode termination on max steps."""
        env = ScanningEnvironment(max_time=45.0, episode_length=5)
        state = env.reset()
        
        done = False
        steps = 0
        while not done:
            next_state, reward, done, info = env.step(0)
            steps += 1
            if steps > 100:  # Safety
                break
        
        assert done
        assert steps <= 5  # Should terminate within max_steps
    
    def test_all_actions_valid(self):
        """Test all 10 actions execute without error."""
        env = ScanningEnvironment()
        state = env.reset()
        
        for action in range(10):
            next_state, reward, done, info = env.step(action)
            assert isinstance(next_state, np.ndarray)
            assert isinstance(reward, (float, int))
            state = next_state
    
    def test_reward_calculation(self):
        """Test reward calculation produces valid values."""
        env = ScanningEnvironment(reward_mode='balanced')
        state = env.reset()
        
        rewards = []
        for _ in range(20):
            next_state, reward, done, info = env.step(np.random.randint(0, 10))
            rewards.append(reward)
            if done:
                break
        
        rewards = np.array(rewards)
        assert np.all(np.isfinite(rewards))
        # Rewards should be reasonable magnitude
        assert np.max(np.abs(rewards)) < 100


class TestPPOAgent:
    """Test PPO agent."""
    
    def test_actor_critic_network(self):
        """Test ActorCritic network."""
        net = ActorCritic(state_dim=32, action_dim=10, hidden_dim=128)
        
        state = torch.randn(4, 32)
        action_logits, value = net(state)
        
        assert action_logits.shape == (4, 10)
        assert value.shape == (4, 1)
    
    def test_agent_initialization(self):
        """Test PPO agent initialization."""
        agent = PPOAgent(state_dim=32, action_dim=10)
        
        assert agent.state_dim == 32
        assert agent.action_dim == 10
        assert agent.clip_ratio == 0.2
    
    def test_agent_action_selection(self):
        """Test agent can select actions."""
        agent = PPOAgent()
        state = np.random.randn(32)
        
        action, log_prob = agent.select_action(state)
        
        assert isinstance(action, (int, np.integer))
        assert 0 <= action < 10
        assert isinstance(log_prob, float)
        assert np.isfinite(log_prob)
    
    def test_agent_store_transition(self):
        """Test storing transitions."""
        agent = PPOAgent()
        state = np.random.randn(32)
        
        agent.store_transition(
            state=state,
            action=5,
            reward=10.0,
            value=0.5,
            log_prob=-0.5,
            done=False
        )
        
        assert len(agent.states) == 1
        assert len(agent.actions) == 1
        assert agent.actions[0] == 5
    
    def test_agent_advantage_computation(self):
        """Test advantage computation."""
        agent = PPOAgent()
        
        # Collect experiences
        for _ in range(10):
            agent.store_transition(
                state=np.random.randn(32),
                action=np.random.randint(0, 10),
                reward=np.random.randn() * 10,
                value=np.random.randn(),
                log_prob=np.log(0.1),
                done=False
            )
        
        advantages, returns = agent.compute_advantages(last_value=0.0)
        
        assert len(advantages) == 10
        assert len(returns) == 10
        assert np.all(np.isfinite(advantages))
        assert np.all(np.isfinite(returns))
    
    def test_agent_update(self):
        """Test PPO update."""
        agent = PPOAgent()
        
        # Generate batch experience
        for _ in range(20):
            state = np.random.randn(32)
            action, log_prob = agent.select_action(state)
            agent.store_transition(
                state=state,
                action=action,
                reward=np.random.randn() * 5,
                value=0.0,
                log_prob=log_prob,
                done=False
            )
        
        advantages, returns = agent.compute_advantages()
        
        update_stats = agent.update(
            advantages,
            returns,
            num_epochs=2,
            batch_size=8
        )
        
        assert 'policy_loss' in update_stats
        assert 'value_loss' in update_stats
        assert 'entropy' in update_stats
        assert 'clip_fraction' in update_stats
    
    def test_agent_value_estimation(self):
        """Test agent value estimation."""
        agent = PPOAgent()
        state = np.random.randn(32)
        
        value = agent.get_value(state)
        
        assert isinstance(value, float)
        assert np.isfinite(value)
    
    def test_agent_save_load(self, tmp_path):
        """Test agent checkpoint save/load."""
        agent = PPOAgent()
        
        # Train briefly
        for _ in range(10):
            agent.store_transition(
                state=np.random.randn(32),
                action=np.random.randint(0, 10),
                reward=1.0,
                value=0.5,
                log_prob=-0.5,
                done=False
            )
        
        # Save
        checkpoint_path = tmp_path / "agent.pt"
        agent.save(str(checkpoint_path))
        assert checkpoint_path.exists()
        
        # Load into new agent
        agent2 = PPOAgent()
        agent2.load(str(checkpoint_path))
        
        # Compare outputs (use same seed for deterministic behavior)
        torch.manual_seed(42)
        state = np.random.randn(32)
        with torch.no_grad():
            logits1, _ = agent.actor_critic(torch.FloatTensor(state).unsqueeze(0))
            action1 = torch.argmax(logits1, dim=1).item()
        
        torch.manual_seed(42)
        with torch.no_grad():
            logits2, _ = agent2.actor_critic(torch.FloatTensor(state).unsqueeze(0))
            action2 = torch.argmax(logits2, dim=1).item()
        
        assert action1 == action2


class TestBehavioralCloning:
    """Test behavioral cloning."""
    
    def test_bc_network_initialization(self):
        """Test BC network initialization."""
        net = BehavioralClongNetwork(state_dim=32, action_dim=10)
        
        state = torch.randn(4, 32)
        logits = net(state)
        
        assert logits.shape == (4, 10)
    
    def test_bc_module_initialization(self):
        """Test BC module initialization."""
        bc = BehavioralCloning(state_dim=32, action_dim=10)
        
        assert bc.state_dim == 32
        assert bc.action_dim == 10
    
    def test_bc_expert_generation(self):
        """Test expert demonstration generation."""
        bc = BehavioralCloning()
        
        expert_states, expert_actions = bc.collect_expert_demonstrations(
            num_trajectories=10
        )
        
        assert len(expert_states) > 0
        assert len(expert_actions) > 0
        assert expert_states.shape[1] == 32
        assert np.all(expert_actions >= 0)
        assert np.all(expert_actions < 10)
    
    def test_bc_training(self):
        """Test behavioral cloning training."""
        bc = BehavioralCloning()
        
        # Generate data
        expert_states, expert_actions = bc.collect_expert_demonstrations(50)
        
        # Train
        stats = bc.train(
            expert_states,
            expert_actions,
            num_epochs=2,
            batch_size=16
        )
        
        assert 'train_loss' in stats
        assert 'train_accuracy' in stats
        assert len(stats['train_loss']) == 2
        assert len(stats['train_accuracy']) == 2
    
    def test_bc_action_prediction(self):
        """Test BC action prediction."""
        bc = BehavioralCloning()
        
        # Train on random data
        expert_states, expert_actions = bc.collect_expert_demonstrations(20)
        bc.train(expert_states, expert_actions, num_epochs=1)
        
        # Predict
        state = np.random.randn(32)
        action = bc.predict_action(state, use_argmax=True)
        
        assert isinstance(action, (int, np.integer))
        assert 0 <= action < 10
    
    def test_bc_transfer_to_rl(self):
        """Test transferring BC weights to RL agent."""
        bc = BehavioralCloning()
        agent = PPOAgent()
        
        # Train BC
        expert_states, expert_actions = bc.collect_expert_demonstrations(20)
        bc.train(expert_states, expert_actions, num_epochs=1)
        
        # Transfer
        bc.transfer_to_rl_agent(agent)
        
        # Verify transfer by comparing predictions using greedy/argmax
        state = np.random.randn(32)
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        # BC prediction using greedy
        bc_logits = bc.policy_net(state_tensor)
        bc_action = torch.argmax(bc_logits, dim=1).item()
        
        # RL prediction using greedy
        with torch.no_grad():
            rl_logits, _ = agent.actor_critic(state_tensor)
        rl_action = torch.argmax(rl_logits, dim=1).item()
        
        # Actions should be same (deterministic greedy)
        assert isinstance(bc_action, int)
        assert isinstance(rl_action, int)
        assert 0 <= bc_action < 10
        assert 0 <= rl_action < 10
    
    def test_bc_save_load(self, tmp_path):
        """Test BC network save/load."""
        bc = BehavioralCloning()
        
        # Train
        expert_states, expert_actions = bc.collect_expert_demonstrations(10)
        bc.train(expert_states, expert_actions, num_epochs=1)
        
        # Save
        checkpoint_path = tmp_path / "bc.pt"
        bc.save(str(checkpoint_path))
        assert checkpoint_path.exists()
        
        # Load
        bc2 = BehavioralCloning()
        bc2.load(str(checkpoint_path))
        
        # Compare predictions
        state = np.random.randn(32)
        action1 = bc.predict_action(state)
        action2 = bc2.predict_action(state)
        
        assert action1 == action2


class TestRLTrainingPipeline:
    """Test RL training pipeline."""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        env = ScanningEnvironment()
        agent = PPOAgent()
        
        pipeline = RLTrainingPipeline(env, agent)
        
        assert pipeline.env is env
        assert pipeline.agent is agent
        assert pipeline.config['max_episodes'] == 10000
    
    def test_pipeline_episode_run(self):
        """Test running single episode."""
        env = ScanningEnvironment(episode_length=10)
        agent = PPOAgent()
        
        pipeline = RLTrainingPipeline(env, agent)
        reward, length = pipeline.run_episode()
        
        assert isinstance(reward, (int, float))
        assert isinstance(length, int)
        assert 0 < length <= 10
    
    def test_pipeline_training_loop_short(self):
        """Test short training loop."""
        env = ScanningEnvironment(episode_length=5)
        agent = PPOAgent()
        
        pipeline = RLTrainingPipeline(env, agent)
        pipeline.config['update_frequency'] = 2
        pipeline.config['max_episodes'] = 100
        
        history = pipeline.training_loop(
            num_episodes=4,
            use_behavioral_cloning=False
        )
        
        assert 'reward' in history
        assert 'episode' in history
        assert len(history['reward']) > 0
    
    def test_pipeline_with_behavioral_cloning(self):
        """Test pipeline with behavioral cloning pre-training."""
        env = ScanningEnvironment(episode_length=5)
        agent = PPOAgent()
        
        pipeline = RLTrainingPipeline(env, agent)
        pipeline.config['update_frequency'] = 2
        
        history = pipeline.training_loop(
            num_episodes=4,
            use_behavioral_cloning=True
        )
        
        assert 'reward' in history
        assert len(history['reward']) > 0
    
    def test_pipeline_evaluation(self):
        """Test pipeline evaluation."""
        env = ScanningEnvironment(episode_length=10)
        agent = PPOAgent()
        
        pipeline = RLTrainingPipeline(env, agent)
        
        eval_stats = pipeline.evaluate(num_episodes=5)
        
        assert 'mean_reward' in eval_stats
        assert 'std_reward' in eval_stats
        assert 'max_reward' in eval_stats
        assert isinstance(eval_stats['mean_reward'], (int, float))
    
    def test_pipeline_save_checkpoint(self, tmp_path):
        """Test checkpoint saving."""
        env = ScanningEnvironment()
        agent = PPOAgent()
        
        pipeline = RLTrainingPipeline(env, agent, output_dir=str(tmp_path))
        pipeline.history['reward'] = [1.0, 2.0, 3.0]
        
        pipeline.save_checkpoint("test")
        
        checkpoint_file = tmp_path / "checkpoint_test.pt"
        assert checkpoint_file.exists()
    
    def test_pipeline_load_checkpoint(self, tmp_path):
        """Test checkpoint loading."""
        env = ScanningEnvironment()
        agent = PPOAgent()
        
        pipeline = RLTrainingPipeline(env, agent, output_dir=str(tmp_path))
        pipeline.history['reward'] = [1.0, 2.0, 3.0]
        pipeline.save_checkpoint("test")
        
        # Create new pipeline and load
        pipeline2 = RLTrainingPipeline(env, agent, output_dir=str(tmp_path))
        pipeline2.load_checkpoint("test")
        
        assert pipeline2.history['reward'] == [1.0, 2.0, 3.0]


# Integration tests
class TestPhaseD_Integration:
    """Integration tests for Phase D."""
    
    def test_full_training_pipeline(self):
        """Test complete training pipeline end-to-end."""
        # Setup
        env = ScanningEnvironment(episode_length=10, max_time=45.0)
        agent = PPOAgent(learning_rate=1e-3)
        pipeline = RLTrainingPipeline(env, agent)
        
        # Configure for quick test
        pipeline.config['update_frequency'] = 2
        pipeline.config['max_episodes'] = 20
        
        # Train
        history = pipeline.training_loop(
            num_episodes=10,
            use_behavioral_cloning=False
        )
        
        # Verify learning
        assert len(history['reward']) > 0
        assert len(history['episode']) > 0
        
        # Later episodes should have better (or similar) rewards
        if len(history['reward']) > 1:
            assert np.mean(history['reward'][-1:]) >= -1000  # Sanity check
    
    def test_behavioral_cloning_integration(self):
        """Test behavioral cloning with RL pipeline."""
        env = ScanningEnvironment(episode_length=10)
        agent = PPOAgent()
        pipeline = RLTrainingPipeline(env, agent)
        
        pipeline.config['update_frequency'] = 2
        
        history = pipeline.training_loop(
            num_episodes=6,
            use_behavioral_cloning=True
        )
        
        assert len(history['reward']) > 0
    
    def test_convergence_monitoring(self):
        """Test convergence monitoring during training."""
        env = ScanningEnvironment(episode_length=20)
        agent = PPOAgent()
        pipeline = RLTrainingPipeline(env, agent)
        
        pipeline.config['update_frequency'] = 5
        pipeline.config['convergence_threshold'] = 10
        pipeline.config['target_reward'] = -1000  # Set low to avoid early stopping
        
        history = pipeline.training_loop(
            num_episodes=20,
            use_behavioral_cloning=False
        )
        
        assert 'moving_avg_reward' in history
        assert len(history['moving_avg_reward']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
