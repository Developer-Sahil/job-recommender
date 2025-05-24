from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define the base path relative to this file
CURRENT_DIR = Path(__file__).resolve().parent
job_data_path = CURRENT_DIR.parent / 'job_data_sampled.csv'

# Load the CSV
jobs_df = pd.read_csv(job_data_path)

# Keep only the required columns
jobs_df = jobs_df[[
    "Qualifications", "Work Type", "Job Title", "Role", 
    "Job Description", "skills", "Responsibilities", "Company"
]]

# Fill NaNs
jobs_df.fillna("", inplace=True)

# Combine relevant fields into a single text column
jobs_df["combined_text"] = jobs_df["Qualifications"] + " " + jobs_df["Work Type"] + " " + \
                           jobs_df["Job Title"] + " " + jobs_df["Role"] + " " + \
                           jobs_df["Job Description"] + " " + jobs_df["skills"] + " " + \
                           jobs_df["Responsibilities"] + " " + jobs_df["Company"]

# Vectorize the job descriptions
vectorizer = TfidfVectorizer(stop_words="english")
job_vectors = vectorizer.fit_transform(jobs_df["combined_text"])

def match_jobs(resume_text, top_n=10):
    resume_vector = vectorizer.transform([resume_text])
    similarities = cosine_similarity(resume_vector, job_vectors).flatten()

    # Get top N matches
    top_indices = similarities.argsort()[::-1][:top_n]
    top_scores = similarities[top_indices]

    matched_jobs = []
    for idx, score in zip(top_indices, top_scores):
        job = jobs_df.iloc[idx].to_dict()
        job["similarity"] = float(score)
        matched_jobs.append(job)

    return matched_jobs
