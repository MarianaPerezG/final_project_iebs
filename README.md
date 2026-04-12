# Talent Growth Hub

Talent Growth Hub is an intelligent course recommendation system designed to bridge skill gaps in your workforce. It analyzes employee competencies against role requirements, market demand, and company strategic goals to suggest personalized, high-quality online courses from e-learning platforms. Currently integrated with edx.

The system uses a hybrid recommendation engine that combines:

- Semantic similarity (embeddings of course descriptions vs. employee skill gaps)
- Skill alignment (cosine similarity between gap profiles and course content)
- Level compatibility (ensuring courses match employee experience level)

This results in personalized recommendations achieving 100% coverage across the organization.

## Environment Setup

In order to work with this repository in your local machine, follow the next steps:

### Step 1: Clone repository

```python
git clone https://github.com/MarianaPerezG/final_project_iebs.git
cd final_project_iebs
```

### Step 2: Create conda environment

```python
conda env create -f environment.yml
```

### Step 3: Activate environment

```python
conda activate proyecto_final_iebs
```

### Step 4: Update dependencies

```python
conda env update -f environment.yml --prune
```


## Obtain and setup Kaggle credentials

In order to download the datasets from kaggle is neccesary that you create an API KEY in your kaggle account. 

Go to Settings -> Create Legacy API Key. It will download a kaggle.json file. 

With those credentials, and using the file .env.example as reference, create a .env file on the project level and add the credencials. 

VERY IMPORTANTE:Make sure .env is NOT being commited to the repo

## How to run the pipeline 

In order to run the batch process where everything is processed and setup, you need to run the pipeline.

```python
python src/main.py
```

## Run Web App 

### Run the Flask application:

Make sure you have run the pipeline at least once before running the app. 

```bash
python src/web_flask/app.py
```

### Access the app:

- **Home (Company Goals):** http://localhost:5000/
- **Employee Directory:** http://localhost:5000/employees
- **Employee Detail:** http://localhost:5000/employee/{employee_id}

## Datasets being used 

- IBM HR Attrition (Snapshot)

Source:
https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset


- LinkedIn Job Postings (2023 - 2024) (Snapshot)

Source:
https://www.kaggle.com/datasets/marianaprezgonzlez/linkedin-job-postings-2023-2024


- Multi-Platform Online Courses Dataset (Snapshot)

Source:
https://www.kaggle.com/datasets/marianaprezgonzlez/multi-platform-online-courses-dataset/data?select=Udemy.csv


