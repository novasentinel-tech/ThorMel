#!/usr/bin/env python
"""
Phase C: Demonstration ML Training Script (Fast Version)
Completes quickly for demonstration purposes while showing all steps
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import logging
from datetime import datetime

from src.data.dataset_generator import DatasetGenerator
from src.models.supervised.lgbm_trainer import LightGBMTrainer
from src.models.supervised.model_evaluator import ModelEvaluator
from config.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)


def main():
    """Run complete Phase C ML training pipeline (fast demonstration)."""
    
    logger.info("="*80)
    logger.info("PHASE C: MACHINE LEARNING MODEL TRAINING (FAST DEMO)")
    logger.info("="*80)
    
    # Paths
    data_dir = Path("data/phase_c")
    data_dir.mkdir(parents=True, exist_ok=True)
    model_dir = Path("data/models")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # ===== STEP 1: Generate Dataset =====
    logger.info("\n[STEP 1] Generating training dataset...")
    gen = DatasetGenerator(n_features=87, random_state=42)
    
    # Generate 5k samples for faster demo (still solid validation)
    logger.info("Creating 5,000 sample dataset with class imbalance...")
    X_train, X_test, y_train, y_test = gen.generate_train_test_split(
        n_samples=5000,
        test_size=0.2,
        class_distribution={0: 0.40, 1: 0.25, 2: 0.20, 3: 0.15}
    )
    
    # Get statistics
    stats = gen.get_dataset_statistics(X_train, y_train)
    logger.info(f"Training samples: {X_train.shape[0]}, Test samples: {X_test.shape[0]}")
    logger.info(f"Class distribution: {stats['class_distribution']}")
    
    # ===== STEP 2: Train Baseline Model =====
    logger.info("\n[STEP 2] Training baseline LightGBM model...")
    trainer = LightGBMTrainer(random_state=42, n_jobs=-1)
    
    # Train with optimized parameters
    model, history = trainer.train(
        X_train, y_train,
        n_estimators=150,
        num_leaves=31,
        learning_rate=0.1,
        max_depth=7
    )
    logger.info("Baseline model trained successfully")
    
    # ===== STEP 3: Quick Hyperparameter Tuning (Reduced) =====  logger.info("\n[STEP 3] Tuning hyperparameters (simplified grid)...")
    
    # Reduced parameter grid for faster tuning
    param_grid = {
        'num_leaves': [31, 50],
        'learning_rate': [0.05, 0.1],
        'max_depth': [7, 10],
    }
    
    tuning_results = trainer.tune_hyperparameters(
        X_train, y_train,
        param_grid=param_grid,
        cv=3,  # 3 folds instead of 5 for speed
        scoring='f1_weighted'
    )
    logger.info(f"Best parameters: {trainer.best_params}")
    logger.info(f"Best CV score: {tuning_results['best_score']:.4f}")
    
    # ===== STEP 4: Cross-Validation =====
    logger.info("\n[STEP 4] Running 3-fold cross-validation...")
    cv_results = trainer.cross_validate(X_train, y_train, cv=3, scoring='f1_weighted')
    logger.info(f"CV mean score: {cv_results['mean_score']:.4f} (+/- {cv_results['std_score']:.4f})")
    
    # ===== STEP 5: Evaluate on Test Set =====
    logger.info("\n[STEP 5] Evaluating on test set...")
    eval_results = trainer.evaluate(X_test, y_test)
    metrics = eval_results['metrics']
    targets_met = eval_results['targets_met']
    
    # Log detailed results
    logger.info(f"\nTest Set Performance:")
    logger.info(f"  • Accuracy: {metrics['accuracy']:.4f} (Target: 85%)")
    logger.info(f"  • Weighted F1: {metrics['weighted_f1']:.4f} (Target: 83%)")
    logger.info(f"  • Critical Class Recall: {metrics['critical_recall']:.4f} (Target: 95%)")
    logger.info(f"\nTarget Achievement:")
    logger.info(f"  • Accuracy 85%+: {targets_met['accuracy_85_percent']}")
    logger.info(f"  • Critical Recall 95%+: {targets_met['critical_recall_95_percent']}")
    logger.info(f"  • F1 Score 83%+: {targets_met['weighted_f1_83_percent']}")
    
    # ===== STEP 6: Feature Importance =====
    logger.info("\n[STEP 6] Extracting feature importance...")
    
    feature_names = [
        'http_response_time', 'http_redirect_count', 'http_hsts', 'http_hsts_max_age',
        'http_csp', 'http_csp_directives', 'http_x_frame_options', 'http_x_content_type',
        'http_referrer_policy', 'http_security_headers', 'http_cookie_count',
        'http_secure_cookies', 'http_httponly_cookies', 'http_server_exposed', 'http_honeypot',
        'tls_protocol_score', 'tls_deprecated', 'tls_tls13', 'tls_cipher_strength',
        'tls_forward_secrecy', 'tls_self_signed', 'tls_cert_expired', 'tls_days_to_expiry',
        'tls_vulnerabilities', 'tls_poodle', 'tls_chain_length', 'tls_ocsp', 'tls_sct',
        'tls_protocols', 'tls_weak_ciphers', 'tls_pfs_ratio', 'tls_valid', 'tls_security_score',
        'dns_a_record', 'dns_aaaa_record', 'dns_mx_record', 'dns_mx_count', 'dns_ns_count',
        'dns_spf', 'dns_dmarc', 'dns_dnssec', 'dns_caa', 'dns_tlsa', 'dns_vulnerabilities',
        'dns_email_security_score',
        'whois_days_to_expiry', 'whois_expiration_risk', 'whois_domain_age', 'whois_privacy',
        'whois_registrar_reputation', 'whois_tech_contact', 'whois_country_risk',
        'whois_organization', 'whois_nameserver_count', 'whois_trustworthiness',
        'ports_open_count', 'ports_ssh', 'ports_http', 'ports_https', 'ports_db_port',
        'ports_ssh_version', 'ports_web_services', 'ports_db_services', 'ports_unusual',
        'ports_banner_rate', 'ports_fingerprint_accuracy', 'ports_unknown_services',
        'ports_mail_service', 'ports_rdp', 'ports_exposure_score',
        'tech_count', 'tech_apache', 'tech_nginx', 'tech_iis', 'tech_wordpress',
        'tech_drupal', 'tech_php', 'tech_python', 'tech_nodejs', 'tech_java',
        'tech_cms', 'tech_modern_framework', 'tech_server_exposed', 'tech_vulnerabilities',
        'tech_outdated', 'tech_diversity', 'tech_security_score'
    ]
    
    importance_dict = trainer.get_feature_importance(top_k=20, feature_names=feature_names)
    
    logger.info("\nTop 20 Most Important Features:")
    for item in importance_dict['top_k_features']:
        logger.info(f"  {item['rank']:2d}. {item['name']:30s} | "
                   f"Importance: {item['importance']:8.4f} | "
                   f"Relative: {item['importance_relative']*100:6.2f}%")
    
    # ===== STEP 7: Save Models and Results =====
    logger.info("\n[STEP 7] Saving models and results...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save trained model
    model_path = model_dir / f"lgbm_model_{timestamp}.pkl"
    trainer.save_model(str(model_path))
    logger.info(f"Model saved to {model_path}")
    
    # Save training summary
    summary_path = model_dir / f"lgbm_summary_{timestamp}.json"
    trainer.save_summary(str(summary_path))
    logger.info(f"Summary saved to {summary_path}")
    
    # Save evaluation metrics
    eval_path = model_dir / f"lgbm_evaluation_{timestamp}.json"
    trainer.evaluator.save_metrics(str(eval_path))
    logger.info(f"Evaluation metrics saved to {eval_path}")
    
    # ===== FINAL SUMMARY =====
    logger.info("\n" + "="*80)
    logger.info("PHASE C COMPLETION SUMMARY")
    logger.info("="*80)
    
    logger.info(f"✓ Dataset generated: {X_train.shape[0]} training + {X_test.shape[0]} test samples")
    logger.info(f"✓ Baseline model trained with {trainer.model.n_estimators} estimators")
    logger.info(f"✓ Hyperparameters tuned via GridSearchCV (8 configurations tested)")
    logger.info(f"✓ Cross-validation completed (3-fold)")
    logger.info(f"\nTest Set Metrics:")
    logger.info(f"  • Accuracy: {metrics['accuracy']:.4f} {'✓' if targets_met['accuracy_85_percent'] else '✗'}")
    logger.info(f"  • F1 Score: {metrics['weighted_f1']:.4f} {'✓' if targets_met['weighted_f1_83_percent'] else '✗'}")
    logger.info(f"  • Critical Recall: {metrics['critical_recall']:.4f} {'✓' if targets_met['critical_recall_95_percent'] else '✗'}")
    
    logger.info(f"\n✓ Feature importance extracted (top 20 features identified)")
    logger.info(f"✓ Model saved to {model_path}")
    logger.info(f"✓ Results saved to {model_dir}")
    
    # Per-class breakdown
    logger.info(f"\nPer-Class Performance:")
    for class_name in ['secure', 'warning', 'vulnerable', 'critical']:
        class_metrics = metrics['per_class'][class_name]
        logger.info(f"  {class_name}:")
        logger.info(f"    Precision: {class_metrics['precision']:.4f}")
        logger.info(f"    Recall: {class_metrics['recall']:.4f}")
        logger.info(f"    F1: {class_metrics['f1']:.4f}")
    
    logger.info("\n" + "="*80)
    logger.info("PHASE C: COMPLETE ✓")
    logger.info("="*80)
    
    return trainer, metrics, importance_dict


if __name__ == "__main__":
    trainer, metrics, importance = main()
