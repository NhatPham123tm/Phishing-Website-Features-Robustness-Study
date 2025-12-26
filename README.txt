# Phishing-Website-Features-Robustness-Study

zip file list:  
Documentation.md : appendix table for common features used in the experiment  
Datasets folder:  
    + Cleaned: pre-processed datasets  
        - Common_only: common only features version of three datasets used in the experiment  
        - Full_features: full after preprocessed features version of three datasets used  
    + Original_datasets: raw dataset downloaded  
        - DatasetC_extract.py : script used to extract features for dataset C (need to download html+sql package from dataset mendeley website to run ). (python DatasetC_extract.py --sql [sql map file path] --dataset-root [root html folder] --out [out put name] )  
    + Experiment_notebook  
        - preprocess.ipynb : notebook for preprocess pipeline  
        - Training_Models.ipynb : notebook for experiment pipeline   
    + Output: Output after running Training_Models.ipynb. Note: some output like shap plots were not used in the report  
        - experiment_results_log.csv: full metric table after train and test models  
        - feature_importance.md: result after calculate feature importance  
        - class
        - FeaureRobustness_.png : visual plot for feaure robustness ranking (not used)  
        - Model performance graph.png: visual plot compareing 3 training protocol (not used)  
        - Shap.png: Feature shap value plot (not used)  
