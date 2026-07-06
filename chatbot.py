import numpy as np
import pandas as pd
from typing import Tuple
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocess import load_dataset, preprocess_dataset, clean_text

# -------------------------------------------------------------------------
# CONSTANTS
# -------------------------------------------------------------------------

DEFAULT_DATASET_PATH = "faq.csv"
DEFAULT_SIMILARITY_THRESHOLD = 0.35


# -------------------------------------------------------------------------
# DATA PREPARATION ENGINE
# -------------------------------------------------------------------------

def load_and_prepare_data(
    file_path: str = DEFAULT_DATASET_PATH
) -> pd.DataFrame:
    """
    Load the FAQ dataset and preprocess all questions.

    Parameters:
        file_path (str): Path to the FAQ dataset.

    Returns:
        pd.DataFrame: Preprocessed FAQ dataset.
    """

    # Load raw dataset
    dataframe = load_dataset(file_path)

    # Preprocess questions
    processed_dataframe = preprocess_dataset(dataframe)

    return processed_dataframe


# -------------------------------------------------------------------------
# TF-IDF VECTORIZATION ENGINE
# -------------------------------------------------------------------------

def create_tfidf_vectorizer(
    dataframe: pd.DataFrame,
) -> Tuple[TfidfVectorizer, csr_matrix]:
    """
    Create and train the TF-IDF vectorizer.

    Parameters:
        dataframe (pd.DataFrame):
            Dataset containing the Clean_Question column.

    Returns:
        Tuple[TfidfVectorizer, csr_matrix]
            - Trained TF-IDF Vectorizer
            - TF-IDF Matrix
    """

    # Create TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()

    # Learn vocabulary and create TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform(
        dataframe["Clean_Question"]
    )

    return vectorizer, tfidf_matrix


# -------------------------------------------------------------------------
# CHATBOT INITIALIZATION
# -------------------------------------------------------------------------

def initialize_chatbot(
    file_path: str = DEFAULT_DATASET_PATH,
) -> Tuple[pd.DataFrame, TfidfVectorizer, csr_matrix]:
    """
    Initialize the complete TF-IDF engine.

    Parameters:
        file_path (str): Path to FAQ dataset.

    Returns:
        Tuple containing:

        - Processed DataFrame
        - Trained TF-IDF Vectorizer
        - TF-IDF Matrix
    """

    processed_dataframe = load_and_prepare_data(file_path)

    vectorizer, tfidf_matrix = create_tfidf_vectorizer(
        processed_dataframe
    )

    return (
        processed_dataframe,
        vectorizer,
        tfidf_matrix,
    )


# -------------------------------------------------------------------------
# USER QUERY PREPROCESSING
# -------------------------------------------------------------------------

def preprocess_user_query(user_query: str) -> str:
    """
    Validates, cleans, and preprocesses the user's input query.

    Parameters:
         user_query (str): The raw input question from the user.

    Returns:
         str: The preprocessed, lemmatized query string, or "" if invalid.
    """
    # Validate that the input is a string
    if not isinstance(user_query, str):
        return ""

    # Strip leading and trailing whitespace
    user_query = user_query.strip()

    # Return empty string if the query is empty
    if not user_query:
        return ""

    # Call the existing clean_text function from preprocess.py
    return clean_text(user_query)


# -------------------------------------------------------------------------
# USER QUERY VECTORIZATION
# -------------------------------------------------------------------------

def query_to_vector(
    user_query: str,
    vectorizer: TfidfVectorizer
) -> csr_matrix:
    """
    Converts a cleaned user query into a TF-IDF vector using the trained vectorizer.

    Parameters:
        user_query (str): The raw input query from the user.
        vectorizer (TfidfVectorizer): The trained TF-IDF vectorizer.

    Returns:
        csr_matrix: The sparse TF-IDF vector representation of the query, or None if invalid.
    """
    # 1. Clean the raw query using the existing preprocessor
    cleaned_query = preprocess_user_query(user_query)

    # 2. Return None if the query is invalid or empty
    if not cleaned_query:
        return None

    # 3. Transform the cleaned query using the trained vectorizer (no fitting)
    query_vector = vectorizer.transform([cleaned_query])

    return query_vector


# -------------------------------------------------------------------------
# SIMILARITY ENGINE
# -------------------------------------------------------------------------

def calculate_similarity(
    query_vector: csr_matrix,
    tfidf_matrix: csr_matrix
):
    """
    Calculates cosine similarity scores between user query vector and the FAQ matrix.

    Parameters:
        query_vector (csr_matrix): The TF-IDF vector of the user query.
        tfidf_matrix (csr_matrix): The trained FAQ TF-IDF matrix.

    Returns:
        numpy.ndarray: 1D array of similarity scores, or None if query_vector is invalid.
    """
    # 1. Return None if the query vector is missing/invalid
    if query_vector is None:
        return None

    # 2. Calculate cosine similarity (returns 2D array of shape [1, num_questions])
    similarity_scores = cosine_similarity(query_vector, tfidf_matrix)

    # 3. Flatten the array into 1D (shape [num_questions,]) and return
    return similarity_scores.flatten()


# -------------------------------------------------------------------------
# MATCHING ENGINE
# -------------------------------------------------------------------------

def find_best_match(
    similarity_scores,
    dataframe: pd.DataFrame
):
    """
    Finds the best matching FAQ by identifying the highest similarity score.

    Parameters:
        similarity_scores (numpy.ndarray): 1D array of cosine similarity scores.
        dataframe (pd.DataFrame): The preprocessed FAQ DataFrame.

    Returns:
        dict: A dictionary containing the matching details (best_index, similarity_score, question, answer),
              or None if similarity_scores is invalid.
    """
    # 1. Return None if similarity_scores is None
    if similarity_scores is None:
        return None

    # 2. Find the index of the highest similarity score using numpy.argmax()
    best_index = int(np.argmax(similarity_scores))
    highest_score = float(similarity_scores[best_index])

    # 3. Extract the question and answer at the matched index
    question = dataframe.iloc[best_index]["Question"]
    answer = dataframe.iloc[best_index]["Answer"]

    # 4. Return as dictionary
    return {
        "best_index": best_index,
        "similarity_score": highest_score,
        "question": question,
        "answer": answer
    }


def get_chatbot_response(
    user_query: str,
    dataframe: pd.DataFrame,
    vectorizer: TfidfVectorizer,
    tfidf_matrix: csr_matrix
):
    """
    Calculates the best matched FAQ response for a given user query.

    Parameters:
        user_query (str): The raw input query from the user.
        dataframe (pd.DataFrame): The preprocessed FAQ DataFrame.
        vectorizer (TfidfVectorizer): The trained TF-IDF vectorizer.
        tfidf_matrix (csr_matrix): The trained FAQ TF-IDF matrix.

    Returns:
        dict: The best matching details dictionary, or None if the query is invalid.
    """
    # 1. Convert user query to vector
    query_vector = query_to_vector(user_query, vectorizer)

    # 2. Calculate similarity scores
    similarity_scores = calculate_similarity(query_vector, tfidf_matrix)

    # 3. Find the best match
    best_match = find_best_match(similarity_scores, dataframe)

    # 4. Return None if best_match is invalid/empty
    if best_match is None:
        return None

    # 5. Apply threshold filter to prevent incorrect answers
    if best_match["similarity_score"] >= DEFAULT_SIMILARITY_THRESHOLD:
        return best_match
    else:
        return {
            "best_index": None,
            "similarity_score": best_match["similarity_score"],
            "question": None,
            "answer": "Sorry, I couldn't find a relevant answer to your question."
        }


# -------------------------------------------------------------------------
# TESTING
# -------------------------------------------------------------------------

def test_tfidf_engine() -> None:
    """
    Test the TF-IDF engine and display useful statistics.
    """

    (
        processed_dataframe,
        vectorizer,
        tfidf_matrix,
    ) = initialize_chatbot()

    vocabulary = vectorizer.get_feature_names_out()

    print("\n" + "=" * 55)
    print("             TF-IDF ENGINE TEST")
    print("=" * 55)

    print(f"\nDataset Status      : Loaded Successfully")
    print(f"Total Questions     : {len(processed_dataframe)}")
    print(f"Vocabulary Size     : {len(vocabulary)}")
    print(f"TF-IDF Matrix Shape : {tfidf_matrix.shape}")

    print("\nFirst 10 Vocabulary Words")
    print("-" * 30)

    for index, word in enumerate(vocabulary[:10], start=1):
        print(f"{index:>2}. {word}")

    print("\n" + "=" * 55)


def test_query_preprocessing() -> None:
    """
    Test the query preprocessing function with sample inputs.
    """
    sample_queries = [
        "Where is my order?",
        "Can I return my product?",
        "HELLO",
        "   ",
        None
    ]

    print("\n" + "=" * 55)
    print("          QUERY PREPROCESSING TEST")
    print("=" * 55)

    for query in sample_queries:
        cleaned = preprocess_user_query(query)
        print(f"Original : {query!r}")
        print(f"Cleaned  : {cleaned!r}")
        print("-" * 30)

    print("=" * 55)


def test_query_vectorization() -> None:
    """
    Test and verify that user queries are correctly converted into TF-IDF vectors.
    """
    # 1. Initialize chatbot engine
    processed_dataframe, vectorizer, tfidf_matrix = initialize_chatbot()

    # 2. Set up sample queries
    sample_queries = [
        "Where is my order?",
        "How can I cancel my order?",
        "HELLO",
        "",
        None
    ]

    print("\n" + "=" * 55)
    print("          QUERY VECTORIZATION TEST")
    print("=" * 55)

    # 3. Iterate and evaluate vectors
    for query in sample_queries:
        cleaned = preprocess_user_query(query)
        query_vector = query_to_vector(query, vectorizer)

        print(f"Original : {query!r}")
        print(f"Cleaned  : {cleaned!r}")

        if query_vector is not None:
            print(f"Vector   : Shape={query_vector.shape}, Non-Zero Features={query_vector.nnz}")
        else:
            print("Vector   : Invalid Query")
        print("-" * 30)

    print("=" * 55)


def test_similarity_engine() -> None:
    """
    Test and verify that cosine similarity scores are computed correctly for sample queries.
    """
    # 1. Initialize chatbot engine
    processed_dataframe, vectorizer, tfidf_matrix = initialize_chatbot()

    # 2. Set up sample queries
    sample_queries = [
        "Where is my order?",
        "Can I return my product?",
        "HELLO",
        "",
        None
    ]

    print("\n" + "=" * 55)
    print("             SIMILARITY ENGINE TEST")
    print("=" * 55)

    # 3. Iterate and evaluate similarity scores
    for query in sample_queries:
        cleaned = preprocess_user_query(query)
        query_vector = query_to_vector(query, vectorizer)
        similarity_scores = calculate_similarity(query_vector, tfidf_matrix)

        print(f"Original : {query!r}")
        print(f"Cleaned  : {cleaned!r}")

        if similarity_scores is not None:
            highest_score = similarity_scores.max()
            lowest_score = similarity_scores.min()
            print(f"Scores   : Shape={similarity_scores.shape}, Max={highest_score:.4f}, Min={lowest_score:.4f}")
        else:
            print("Scores   : Invalid Query (No similarity computed)")
        print("-" * 30)

    print("=" * 55)


def test_chatbot_response() -> None:
    """
    Test and verify the complete chatbot response pipeline with sample queries.
    """
    # 1. Initialize chatbot engine
    processed_dataframe, vectorizer, tfidf_matrix = initialize_chatbot()

    # 2. Set up sample queries
    sample_queries = [
        "Where is my order?",
        "How can I cancel my order?",
        "What payment methods are accepted?",
        "Can I return my product?"
    ]

    print("\n" + "=" * 55)
    print("             CHATBOT RESPONSE TEST")
    print("=" * 55)

    # 3. Test and print results
    for query in sample_queries:
        response = get_chatbot_response(query, processed_dataframe, vectorizer, tfidf_matrix)

        print(f"Original Query   : {query!r}")
        if response is not None:
            print(f"Matched Question : {response['question']}")
            print(f"Similarity Score : {response['similarity_score']:.4f}")
            print(f"Answer           : {response['answer']}")
        else:
            print("Response         : Invalid Query")
        print("-" * 30)

    print("=" * 55)


def test_threshold_engine() -> None:
    """
    Test and verify the threshold engine using relevant and irrelevant queries.
    """
    # 1. Initialize chatbot engine
    processed_dataframe, vectorizer, tfidf_matrix = initialize_chatbot()

    # 2. Set up relevant and irrelevant queries
    sample_queries = [
        "Where is my order?",
        "What payment methods are accepted?",
        "How to cook biryani?",
        "What is the capital of France?",
        "Tell me a movie."
    ]

    print("\n" + "=" * 55)
    print("             THRESHOLD ENGINE TEST")
    print("=" * 55)

    # 3. Evaluate results against the threshold
    for query in sample_queries:
        response = get_chatbot_response(query, processed_dataframe, vectorizer, tfidf_matrix)

        print(f"Original Query   : {query!r}")
        if response is not None:
            score = response["similarity_score"]
            print(f"Similarity Score : {score:.4f}")
            print(f"Answer           : {response['answer']}")
            if response["best_index"] is not None:
                print("Response Type    : [Matched FAQ]")
            else:
                print("Response Type    : [Fallback Response]")
        else:
            print("Response         : Invalid Query")
        print("-" * 30)

    print("=" * 55)


# -------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------

if __name__ == "__main__":
    test_tfidf_engine()
    test_query_preprocessing()
    test_query_vectorization()
    test_similarity_engine()
    test_chatbot_response()
    test_threshold_engine()