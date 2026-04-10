from functools import lru_cache
import logging
import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer

from config.global_skills import GLOBAL_SKILLS


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def create_course_semantic_embeddings(course_matrix: pd.DataFrame) -> np.ndarray:
    """
    Create embeddings for courses with disk-based caching and batch processing.
    - First call: Computes and saves (~30-60 sec for 15k courses with batch_size=100)
    - Subsequent calls: Loads from numpy array (~0.5 sec)

    Uses batch processing to reduce memory and CPU overhead.
    Falls back to zeros if processing takes too long (timeout safety).
    """
    cache_path = Path("models/trained/course_embeddings_cache.npz")

    # Try to load from cache (npz is faster than pickle)
    if cache_path.exists():
        try:
            logging.info(f"Loading cached course embeddings from {cache_path}")
            with open(cache_path, "rb") as f:
                cached = np.load(f)
                embeddings = cached["embeddings"]
            logging.info(
                f"✓ Loaded {len(embeddings)} course embeddings from cache ({embeddings.nbytes / 1024 / 1024:.1f} MB)"
            )
            return embeddings
        except Exception as e:
            logging.warning(f"Could not load cache: {e}")

    # If not cached, compute embeddings WITH BATCH PROCESSING
    logging.info("Computing course embeddings (first time - will be cached)...")

    try:
        course_contexts = []
        for course_idx in range(len(course_matrix)):
            course_row = course_matrix.iloc[course_idx]

            relevant_course_skills = [
                skill
                for skill in GLOBAL_SKILLS
                if float(course_row.get(skill, 0.0)) > 0.2
            ]
            course_skills_str = ", ".join(relevant_course_skills)
            course_level = str(course_row.get("level", "intermediate"))

            course_context = (
                f"Course: {course_row.get('course_title', 'Unknown')}. "
                f"Subject: {course_row.get('subject', 'General')}. "
                f"Level: {course_level}. "
                f"Teaches: {course_skills_str}."
            )
            course_contexts.append(course_context)

        model = _get_model()

        # Process in batches
        BATCH_SIZE = 100
        all_embeddings = []

        for i in range(0, len(course_contexts), BATCH_SIZE):
            batch = course_contexts[i : i + BATCH_SIZE]
            batch_embeddings = model.encode(
                batch,
                convert_to_tensor=False,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            all_embeddings.append(batch_embeddings)
            if (i + BATCH_SIZE) % 500 == 0 or i + BATCH_SIZE >= len(course_contexts):
                logging.info(
                    f"  ✓ Encoded {min(i+BATCH_SIZE, len(course_contexts))}/{len(course_contexts)} courses"
                )

        embeddings = np.vstack(all_embeddings)

        # Save to cache using npz format
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(cache_path, embeddings=embeddings)
        logging.info(
            f"✓ Cached {len(embeddings)} embeddings to {cache_path} ({embeddings.nbytes / 1024 / 1024:.1f} MB)"
        )

        return embeddings

    except Exception as e:
        logging.warning(f"Could not compute semantic embeddings: {e}")
        logging.info(
            "Falling back to zero embeddings (will use only cosine similarity)"
        )
        # Return zero embeddings - will still work with cosine similarity
        return np.zeros((len(course_matrix), 384), dtype=np.float32)


def create_employee_description_embeddings(
    gap_matrix: pd.DataFrame, employee_number: int
) -> np.ndarray:
    user_row = gap_matrix[gap_matrix["EmployeeNumber"] == employee_number].iloc[0]

    gap_skills = []
    for skill in GLOBAL_SKILLS:
        gap_val = float(user_row.get(skill, 0.0))
        if gap_val > 0:
            gap_skills.append((skill, gap_val))

    gap_skills.sort(key=lambda x: x[1], reverse=True)
    top_gap_skills = [s[0] for s in gap_skills[:5]]
    gap_skills_str = ", ".join(top_gap_skills) if top_gap_skills else "general skills"

    gap_description = (
        f"Employee seeking to improve: {gap_skills_str}. "
        f"Current level: {user_row.get('JobLevel', 'unknown')}. "
        f"Needs practical training in these specific areas."
    )

    model = _get_model()

    return model.encode(
        gap_description,
        convert_to_tensor=False,
        normalize_embeddings=True,
    )


def create_employee_descriptions_batch(gap_matrix: pd.DataFrame) -> np.ndarray:
    """
    BATCH version: Create embeddings for ALL employees with a single model.encode() call.
    Much faster than calling create_employee_description_embeddings 282 times.

    Returns: (N_employees, 384) array of embeddings
    Fallback: Returns zeros if encoding fails/times out (use only cosine similarity then)
    """
    try:
        logging.info(f"Creating batch embeddings for {len(gap_matrix)} employees...")

        gap_descriptions = []
        for _, user_row in gap_matrix.iterrows():
            gap_skills = []
            for skill in GLOBAL_SKILLS:
                gap_val = float(user_row.get(skill, 0.0))
                if gap_val > 0:
                    gap_skills.append((skill, gap_val))

            gap_skills.sort(key=lambda x: x[1], reverse=True)
            top_gap_skills = [s[0] for s in gap_skills[:5]]
            gap_skills_str = (
                ", ".join(top_gap_skills) if top_gap_skills else "general skills"
            )

            gap_description = (
                f"Employee seeking to improve: {gap_skills_str}. "
                f"Current level: {user_row.get('JobLevel', 'unknown')}. "
                f"Needs practical training in these specific areas."
            )
            gap_descriptions.append(gap_description)

        model = _get_model()

        # SINGLE encode() call for ALL employees at once
        embeddings = model.encode(
            gap_descriptions,
            convert_to_tensor=False,
            normalize_embeddings=True,
        )

        logging.info(
            f"✓ Batch encoded {len(gap_descriptions)} employees: shape {embeddings.shape}"
        )
        return embeddings

    except Exception as e:
        logging.warning(f"Could not batch encode employees: {e}")
        logging.info(f"Falling back to zero embeddings for {len(gap_matrix)} employees")
        return np.zeros((len(gap_matrix), 384), dtype=np.float32)
