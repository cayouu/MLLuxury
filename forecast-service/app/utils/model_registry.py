"""
MLflow model registry utilities
"""
import mlflow
import mlflow.xgboost
from pathlib import Path

def log_model_to_registry(model, model_name: str, run_name: str = None):
    """Enregistrer un modèle dans MLflow"""
    try:
        mlflow.set_experiment("luxury_forecast")
        
        with mlflow.start_run(run_name=run_name):
            # Log du modèle
            mlflow.xgboost.log_model(model, "model")
            
            # Transiter vers staging puis production
            # mlflow.register_model(f"runs:/{run.info.run_id}/model", model_name)
            
        return True
    except Exception as e:
        print(f"Error logging model to MLflow: {e}")
        return False

def load_model_from_registry(model_name: str, stage: str = "production"):
    """Charger un modèle depuis MLflow"""
    try:
        model_uri = f"models:/{model_name}/{stage}"
        model = mlflow.xgboost.load_model(model_uri)
        return model
    except Exception as e:
        print(f"Error loading model from MLflow: {e}")
        return None
