# Environment Setup

In order to work with this repository in your local machine, follow the next steps:

## Step 1: Clone repository

```python
git clone https://github.com/MarianaPerezG/final_project_iebs.git
cd final_project_iebs
```

## Step 2: Create conda environment

```python
conda env create -f environment.yml
```

## Step 3: Activate environment

```python
conda activate proyecto_final_iebs
```

## Step 4: Update dependencies (opcional)

```python
conda env update -f environment.yml --prune
```


# Obtain and setup Kaggle credentials

In order to download the datasets from kaggle is neccesary that you create an API KEY in your kaggle account. 

Go to Settings -> Create Legacy API Key. It will download a kaggle.json file. 

With those credentials, and using the file .env.example as reference, create a .env file on the project level and add the credencials. 

VERY IMPORTANTE:Make sure .env is NOT being commited to the repo

# Datasets being used 

- IBM HR Attrition (Snapshot)

Source:
https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset


- LinkedIn Job Postings (2023 - 2024) (Snapshot)

Source:
https://www.kaggle.com/datasets/marianaprezgonzlez/linkedin-job-postings-2023-2024


- Multi-Platform Online Courses Dataset (Snapshot)

Source:
https://www.kaggle.com/datasets/marianaprezgonzlez/multi-platform-online-courses-dataset/data?select=Udemy.csv


# Next Steps

- Regression model with KNN for aggregation in roles and scoring rules


## Web app 

Run the app:

```bash
conda env update --file environment.yml --prune   # si no has creado o quieres actualizar
conda activate proyecto_final_iebs
streamlit run src/web/app.py
```

