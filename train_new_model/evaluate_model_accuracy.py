import os
import csv

from detectron2.evaluation import COCOEvaluator, inference_on_dataset
from detectron2.data import build_detection_test_loader
from detectron2.config import get_cfg
from detectron2.engine import DefaultTrainer

from detectron2.data.datasets import register_coco_instances

# Register your datasets (example)
register_coco_instances("my_dataset_train", {}, "/dataset_roboflow/train/_annotations.coco.json", "/dataset_roboflow/train")
register_coco_instances("my_dataset_val", {}, "/dataset_roboflow/valid/_annotations.coco.json", "dataset_roboflow/valid/images")


def evaluate_model(cfg, model_path):
    # Load model weights of selected model to evaluate
    cfg.MODEL.WEIGHTS = model_path
    cfg.MODEL.DEVICE = "cuda"  # Change to "cpu" if not using GPU
    
    # Initialize model with weights
    trainer = DefaultTrainer(cfg)
    trainer.resume_or_load(resume=True)
    
    evaluator = COCOEvaluator(cfg.DATASETS.TEST[0], cfg, False, output_dir=cfg.OUTPUT_DIR)
    val_loader = build_detection_test_loader(cfg, cfg.DATASETS.TEST[0])
    
    # Run evaluation
    metrics = inference_on_dataset(trainer.model, val_loader, evaluator)
    print(f"Metrics for {model_path}: {metrics}")
    return metrics

def evaluate_models(model_paths, cfg):
    results = []
    
    for path in model_paths:
        metrics = evaluate_model(cfg, path)
        results.append({
            'model_path': path,
            'AP': metrics['bbox']['AP'],  # Average Precision
            'AP50': metrics['bbox']['AP50'],  # AP at IoU=0.5
            'AP75': metrics['bbox']['AP75'],  # AP at IoU=0.75
            'APs': metrics['bbox']['APs'],  # AP for small objects
            'APm': metrics['bbox']['APm'],  # AP for medium objects
            'APl': metrics['bbox']['APl']   # AP for large objects
        })
    
    return results

def save_results_to_csv(results, output_file):
    keys = results[0].keys() if results else []
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

if __name__ == "__main__":
    # Define paths to trained models
    model_paths = [
        "./built_models/model_default_dataset_2k_iterations/default_2k_model.pth",
        #"./built_models/model_default_dataset_10k_iterations/default_10k_model.pth",
        #"./built_models/model_boston_dataset/boston_model.pth",
        #"./built_models/model_dubai_dataset/dubai_model.pth"
    ]
    
    # Load config
    cfg = get_cfg()
    
    CONFIG_FILE_PATH = f"COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml"
    cfg.MODEL.DEVICE = "cuda"  # or "cpu" if GPU is unavailable
    
    # Create output directory for logs
    output_dir = "./evaluation_logs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Evaluate models and save results
    results = evaluate_models(model_paths, cfg)
    save_results_to_csv(results, os.path.join(output_dir, 'evaluation_results.csv'))
    
    print("Evaluation complete. Results saved to evaluation_logs/evaluation_results.csv")
      
