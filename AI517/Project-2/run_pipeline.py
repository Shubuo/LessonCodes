#!/usr/bin/env python
"""
Main Pipeline Script for Turkish Stress Detection
Runs the complete workflow: data loading → training → evaluation → visualization
"""
import sys
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def run_data_loading():
    """Step 1: Load and process data"""
    print_header("STEP 1: DATA LOADING AND PROCESSING")
    
    try:
        import data_loader
        loader = data_loader.TurkishStressDataLoader()
        all_examples = loader.load_all_data()
        
        if len(all_examples) == 0:
            print("\n❌ No data loaded! Please check if CSV files exist.")
            return False
        
        loader.split_data(all_examples)
        loader.print_sample_examples(n=3)
        loader.save_processed_data()
        
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
        # Import here to avoid loading before data is ready
        from token_classification import train_model
        
        print("\nStarting model training...")
        print("Note: This may take a while depending on your hardware.")
        print("GPU is recommended for faster training.\n")
        
        trainer, results = train_model()
        
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

def run_evaluation():
    """Step 3: Evaluate the model"""
    print_header("STEP 3: MODEL EVALUATION")
    
    try:
        import evaluation
        evaluation.main()
        
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

def main():
    """Run the complete pipeline"""
    print("\n" + "🇹🇷 " * 20)
    print_header("TURKISH STRESS DETECTION - COMPLETE PIPELINE")
    print("LLM-Based Token Classification Approach")
    print("="*70)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        step = sys.argv[1]
        
        if step == "data":
            run_data_loading()
        elif step == "train":
            run_training()
        elif step == "eval":
            run_evaluation()
        elif step == "visualize":
            run_visualization()
        else:
            print(f"❌ Unknown step: {step}")
            print("\nUsage:")
            print("  python run_pipeline.py [step]")
            print("\nSteps:")
            print("  data       - Load and process data only")
            print("  train      - Train model only")
            print("  eval       - Evaluate model only")
            print("  visualize  - Generate visualizations only")
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
        
        # Step 3: Evaluation (only if training succeeded)
        if success:
            if not run_evaluation():
                success = False
        
        # Step 4: Visualization (only if evaluation succeeded)
        if success:
            run_visualization()
        
        # Final summary
        print_header("PIPELINE EXECUTION SUMMARY")
        
        if success:
            print("\n🎉 ✅ ALL STEPS COMPLETED SUCCESSFULLY!")
            print("\nGenerated outputs:")
            print("  📁 data/processed/       - Processed datasets (JSON)")
            print("  📁 outputs/checkpoints/  - Trained model")
            print("  📁 outputs/results/      - Evaluation results")
            print("  📁 outputs/figures/      - Visualizations")
            print("\nNext steps:")
            print("  1. Review evaluation metrics in outputs/results/")
            print("  2. View visualizations in outputs/figures/")
            print("  3. Check sample predictions HTML file")
            print("  4. Use trained model for inference:")
            print("     python token-classification.py --predict 'Yarın okula gideceğim'")
        else:
            print("\n⚠️ Pipeline completed with errors.")
            print("Please check the error messages above and fix any issues.")

if __name__ == "__main__":
    main()
