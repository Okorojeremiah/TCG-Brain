import nltk
import os

def download_nltk():
    """
    Downloads necessary NLTK resources to a custom directory.
    """
    nltk_data_dir = os.path.join(os.getcwd(), 'data/nltk_data')
    os.makedirs(nltk_data_dir, exist_ok=True)
    nltk.data.path.append(nltk_data_dir)

    try:
        nltk.download('punkt', download_dir=nltk_data_dir)
        nltk.download('punkt_tab', download_dir=nltk_data_dir)
        nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_dir)
        nltk.download('averaged_perceptron_tagger_eng', download_dir=nltk_data_dir)
        print(f"NLTK resources downloaded to {nltk_data_dir}")
    except Exception as e:
        print(f"Error downloading NLTK resources: {e}")
        raise
