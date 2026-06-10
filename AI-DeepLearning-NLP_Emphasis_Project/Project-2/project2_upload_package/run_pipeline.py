#!/usr/bin/env python
"""
Main Pipeline Script for Turkish Stress Detection
Runs the complete workflow: data loading → training → evaluation → visualization
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def run_data_loading():
    """Step 1: Load and process data"""
    print_header("STEP 1: DATA LOADING AND PROCESSING")

    try:
        subprocess.run([sys.executable, "data_loader.py"], check=True)

        print("\n✅ Data processing complete!")
        return True

    except Exception as e:
        print(f"\n❌ Error during data loading: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_training():
    """Step 2: Train the model"""
    print_header("STEP 2: MODEL TRAINING")

    try:
        print("\nStarting model training...")
        print("Note: This may take a while depending on your hardware.")
        print("GPU is recommended for faster training.\n")
        subprocess.run([sys.executable, "train_v2.py"], check=True)

        print("\n✅ Training complete!")
        return True

    except FileNotFoundError as e:
        print(f"\n❌ Data files not found: {e}")
        print("Please run data loading first.")
        return False
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_baseline_training():
    """Step 2b: Train the legacy baseline model"""
    print_header("STEP 2B: BASELINE TRAINING")

    try:
        print("\nStarting baseline cross-entropy training...\n")
        subprocess.run([sys.executable, "baseline_train.py"], check=True)

        print("\n✅ Baseline training complete!")
        return True

    except FileNotFoundError as e:
        print(f"\n❌ Data files not found: {e}")
        print("Please run data loading first.")
        return False
    except Exception as e:
        print(f"\n❌ Error during baseline training: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_evaluation():
    """Step 3: Evaluate the model"""
    print_header("STEP 3: MODEL EVALUATION")

    try:
        subprocess.run([sys.executable, "evaluation.py"], check=True)

        print("\n✅ Evaluation complete!")
        return True

    except FileNotFoundError as e:
        print(f"\n❌ Model or data files not found: {e}")
        print("Please run training first.")
        return False
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_visualization():
    """Step 4: Generate visualizations"""
    print_header("STEP 4: GENERATING VISUALIZATIONS")

    try:
        import visualize

        visualize.main()

        print("\n✅ Visualization complete!")
        return True

    except Exception as e:
        print(f"\n❌ Error during visualization: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_comparison():
    """Step 5: Generate model comparison artifacts"""
    print_header("STEP 5: MODEL COMPARISON")

    try:
        subprocess.run([sys.executable, "compare_models.py"], check=True)

        print("\n✅ Comparison complete!")
        return True

    except Exception as e:
        print(f"\n❌ Error during comparison: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the complete pipeline"""
    print("\n" + "🇹🇷 " * 20)
    print_header("TURKISH STRESS DETECTION - COMPLETE PIPELINE")
    print("LLM-Based Token Classification Approach")
    print("=" * 70)

    # Parse command line arguments
    if len(sys.argv) > 1:
        step = sys.argv[1]

        if step == "data":
            run_data_loading()
        elif step == "train":
            run_training()
        elif step == "baseline":
            run_baseline_training()
        elif step == "eval":
            run_evaluation()
        elif step == "visualize":
            run_visualization()
        elif step == "compare":
            run_comparison()
        else:
            print(f"❌ Unknown step: {step}")
            print("\nUsage:")
            print("  python run_pipeline.py [step]")
            print("\nSteps:")
            print("  data       - Load and process data only")
            print("  train      - Train model only")
            print("  baseline   - Train baseline model only")
            print("  eval       - Evaluate model only")
            print("  visualize  - Generate visualizations only")
            print("  compare    - Generate comparison artifacts only")
            print("  (no args)  - Run complete pipeline")
    else:
        # Run complete pipeline
        success = True

        # Step 1: Data Loading
        if not run_data_loading():
            success = False

        # Step 2: Training (only if data loading succeeded)
        if success:
            if not run_training():
                success = False

        # Step 2b: Baseline training (best-effort, needed for comparisons)
        baseline_success = False
        if success:
            baseline_success = run_baseline_training()

        # Step 3: Evaluation (only if training succeeded)
        if success:
            if not run_evaluation():
                success = False

        # Step 4: Visualization (only if evaluation succeeded)
        if success:
            run_visualization()

        # Step 5: Comparison artifacts (best-effort)
        if success:
            run_comparison()

        # Final summary
        print_header("PIPELINE EXECUTION SUMMARY")

        if success:
            print("\n🎉 ✅ ALL STEPS COMPLETED SUCCESSFULLY!")
            print("\nGenerated outputs:")
            print("  📁 data/processed/       - Processed datasets (JSON)")
            print("  📁 outputs/checkpoints/  - Trained CRF+SCL model")
            print("  📁 outputs/results/      - Evaluation results")
            print("  📁 outputs/figures/      - Visualizations")
            print("  📁 outputs/results/comparisons/ - Section 5 tables")
            print("\nNext steps:")
            print("  1. Review evaluation metrics in outputs/results/")
            print("  2. View visualizations in outputs/figures/")
            print("  3. Check sample predictions HTML file")
            print("  4. Use trained model for inference:")
            print("     python train_v2.py --epochs 1")
            if not baseline_success:
                print("\nNote: baseline artifacts were not generated in this run.")
        else:
            print("\n⚠️ Pipeline completed with errors.")
            print("Please check the error messages above and fix any issues.")


if __name__ == "__main__":
    main()
