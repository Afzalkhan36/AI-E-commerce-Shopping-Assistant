import re
import string
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# -------------------------------------------------------------------------
# NLTK RESOURCE DOWNLOADS
# -------------------------------------------------------------------------
# Define the required NLTK resources and their lookup paths to prevent
# redundant downloads if they are already present on the system.
nltk_resources = {
    "punkt": "tokenizers/punkt",
    "stopwords": "corpora/stopwords",
    "wordnet": "corpora/wordnet",
    "omw-1.4": "corpora/omw-1.4"
}

for resource, path in nltk_resources.items():
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(resource)

# -------------------------------------------------------------------------
# GLOBAL PREPROCESSING OBJECTS
# -------------------------------------------------------------------------
# Reusable objects initialized once at import time for optimal performance.
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


# -------------------------------------------------------------------------
# TEXT PREPROCESSING FUNCTION
# -------------------------------------------------------------------------
def clean_text(text):
    """
    Cleans and preprocesses input text for the chatbot.

    Parameters:
        text (str): Raw user query or FAQ question.

    Returns:
        str: Cleaned and preprocessed text.
    """

    # Handle empty or invalid input
    if not isinstance(text, str) or not text.strip():
        return ""

    # Convert text to lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Remove extra whitespace
    text = " ".join(text.split())

    # Tokenize
    tokens = word_tokenize(text)

    # Remove stopwords
    tokens = [token for token in tokens if token not in stop_words]

    # Lemmatization
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Return cleaned text
    return " ".join(tokens)


# -------------------------------------------------------------------------
# LOAD DATASET
# -------------------------------------------------------------------------
def load_dataset(file_path="faq.csv"):
    """
    Loads the FAQ dataset and validates required columns.

    Parameters:
        file_path (str): Path of the CSV file.

    Returns:
        pd.DataFrame
    """

    df = pd.read_csv(file_path)

    required_columns = ["Question", "Answer"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Dataset is missing required column: {column}")

    return df


# -------------------------------------------------------------------------
# PREPROCESS COMPLETE DATASET
# -------------------------------------------------------------------------
def preprocess_dataset(df):
    """
    Creates a new dataframe with a Clean_Question column.

    Parameters:
        df (pd.DataFrame)

    Returns:
        pd.DataFrame
    """

    processed_df = df.copy()

    processed_df["Clean_Question"] = processed_df["Question"].apply(clean_text)

    return processed_df


# -------------------------------------------------------------------------
# TEST PREPROCESSING PIPELINE
# -------------------------------------------------------------------------
def test_preprocessing():
    """
    Loads the dataset, preprocesses it,
    and prints sample results for verification.
    """

    print("Loading dataset...")

    df = load_dataset()

    print("Preprocessing dataset...")

    processed_df = preprocess_dataset(df)

    print("\n========== DATASET INFORMATION ==========")

    print(f"Total Rows : {len(processed_df)}")
    print(f"Columns    : {list(processed_df.columns)}")

    print("\nFirst 5 Original Questions\n")

    for i, question in enumerate(processed_df["Question"].head(5), start=1):
        print(f"{i}. {question}")

    print("\nFirst 5 Cleaned Questions\n")

    for i, question in enumerate(processed_df["Clean_Question"].head(5), start=1):
        print(f"{i}. {question}")


# -------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------
if __name__ == "__main__":
    test_preprocessing()