"""
Script pour promouvoir un modèle de 'Staging' vers 'Production' dans MLflow
"""
import os
import sys
from datetime import datetime
from mlflow.tracking import MlflowClient

# Configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = "luxury_demand_forecast"

# Seuils de qualité
MIN_R2_SCORE = 0.80
MAX_MAPE = 15.0

def promote_to_production(run_id: str = None, model_name: str = MODEL_NAME):
    """
    Promouvoir un modèle de 'Staging' vers 'Production'
    
    Args:
        run_id: ID de la run à promouvoir (optionnel, utilise le dernier modèle en Staging si non fourni)
        model_name: Nom du modèle dans MLflow Registry
    """
    client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
    
    try:
        # 1. Récupérer la version du modèle
        if run_id:
            model_versions = client.search_model_versions(f"run_id='{run_id}'")
            if not model_versions:
                print(f"❌ Aucun modèle trouvé pour le run_id: {run_id}")
                return False
            version_info = model_versions[0]
        else:
            # Récupérer le dernier modèle en Staging
            staging_versions = client.get_latest_versions(model_name, stages=["Staging"])
            if not staging_versions:
                print(f"❌ Aucun modèle en Staging pour {model_name}")
                print("💡 Utilisez l'UI MLflow pour mettre un modèle en Staging d'abord")
                return False
            version_info = staging_versions[0]
            run_id = version_info.run_id
        
        version = version_info.version
        
        # 2. Vérifier les métriques avant promotion
        run = client.get_run(run_id)
        mape = run.data.metrics.get('mape', float('inf'))
        r2 = run.data.metrics.get('r2_score', 0.0)
        mae = run.data.metrics.get('mae', float('inf'))
        rmse = run.data.metrics.get('rmse', float('inf'))
        
        print(f"📊 Métriques du modèle v{version}:")
        print(f"   - MAPE: {mape:.1f}%")
        print(f"   - R²: {r2:.3f}")
        print(f"   - MAE: {mae:.2f}")
        print(f"   - RMSE: {rmse:.2f}")
        print(f"   - Run ID: {run_id}")
        
        # Vérification des seuils de qualité
        if mape > MAX_MAPE:
            print(f"❌ Le modèle ne respecte pas les seuils de qualité")
            print(f"   MAPE ({mape:.1f}%) > seuil ({MAX_MAPE}%)")
            return False
        
        if r2 < MIN_R2_SCORE:
            print(f"❌ Le modèle ne respecte pas les seuils de qualité")
            print(f"   R² ({r2:.3f}) < seuil ({MIN_R2_SCORE})")
            return False
        
        print(f"✅ Le modèle respecte les seuils de qualité")
        print(f"   Seuils: MAPE < {MAX_MAPE}%, R² > {MIN_R2_SCORE}")
        
        # 3. Archiver l'ancien modèle en production
        current_prod_versions = client.get_latest_versions(
            model_name, 
            stages=["Production"]
        )
        
        for prod_version in current_prod_versions:
            client.transition_model_version_stage(
                name=model_name,
                version=prod_version.version,
                stage="Archived",
                archive_existing_versions=False
            )
            print(f"📦 Modèle v{prod_version.version} archivé")
        
        # 4. Promouvoir le nouveau modèle
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Production"
        )
        
        print(f"✅ Modèle v{version} promu en PRODUCTION")
        
        # 5. Ajouter une description
        description = (
            f"Promoted on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. "
            f"MAPE: {mape:.1f}%, R²: {r2:.3f}, MAE: {mae:.2f}, RMSE: {rmse:.2f}"
        )
        client.update_model_version(
            name=model_name,
            version=version,
            description=description
        )
        
        print(f"📝 Description mise à jour")
        print(f"\n🎉 Promotion réussie!")
        print(f"   Modèle: {model_name}")
        print(f"   Version: {version}")
        print(f"   Stage: Production")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la promotion: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_models(model_name: str = MODEL_NAME):
    """
    Lister tous les modèles et leurs versions
    """
    client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
    
    try:
        versions = client.search_model_versions(f"name='{model_name}'")
        
        if not versions:
            print(f"❌ Aucun modèle trouvé: {model_name}")
            return
        
        print(f"\n📦 Modèles pour '{model_name}':")
        print("-" * 80)
        
        for version in sorted(versions, key=lambda v: int(v.version), reverse=True):
            stage = version.current_stage
            run_id = version.run_id
            
            # Récupérer les métriques
            try:
                run = client.get_run(run_id)
                mape = run.data.metrics.get('mape', 'N/A')
                r2 = run.data.metrics.get('r2_score', 'N/A')
                metrics_str = f"MAPE: {mape:.1f}%" if isinstance(mape, float) else "N/A"
                metrics_str += f", R²: {r2:.3f}" if isinstance(r2, float) else ""
            except:
                metrics_str = "N/A"
            
            print(f"Version {version.version} ({stage})")
            print(f"  Run ID: {run_id}")
            print(f"  Métriques: {metrics_str}")
            print(f"  Créé: {version.creation_timestamp}")
            print()

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Promouvoir un modèle MLflow en Production")
    parser.add_argument("--run-id", type=str, help="Run ID du modèle à promouvoir")
    parser.add_argument("--list", action="store_true", help="Lister tous les modèles")
    parser.add_argument("--model-name", type=str, default=MODEL_NAME, help="Nom du modèle")
    
    args = parser.parse_args()
    
    if args.list:
        list_models(args.model_name)
    else:
        success = promote_to_production(args.run_id, args.model_name)
        sys.exit(0 if success else 1)
