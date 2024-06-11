import os
import json
import re
from nltk.corpus import stopwords
from spellchecker import SpellChecker
import contractions
from tqdm import tqdm
from datetime import datetime

def clean_comment(comment, custom_stopwords, spell_checker):
    """Clean and tokenize the comment string."""
    if comment is None:
        return ""
    # Ensure comment is not an empty string
    if not comment.strip():
        return ""

    cleaning_rules = [
        # Remove usernames or user handles
        (r'@[^\s]+', ''),
        # Remove timestamps (e.g., "12:34 PM")
        (r'\b(?:[01]\d|2[0-3]):(?:[0-5]\d)\s*(?:[ap]\.?m\.?)?\b', ''),
        # Remove emojis and emoticons
        (r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F700-\U0001F77F]|[\U0001F780-\U0001F7FF]|[\U0001F800-\U0001F8FF]|[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FA6F]|[\U0001FA70-\U0001FAFF]|[\U00002702-\U000027B0]|[\U000024C2-\U0001F251]', ''),
        # Remove repeated messages
        (r'(^\s*(?:re:|fwd:)?\s*){2,}', ''),
        # Filter special characters (excluding apostrophes and hyphens)
        (r'[^\w\s\'-]', ''),
        # Remove unnecessary whitespace
        (r'\s+', ' '),
        # Remove specific patterns (websites with .com)
        (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ''),
        # Remove words with . in the phrasing
        (r'\b\w*\.\w+\b', ''),
        # Remove words with hyphens
        (r'\b\w*-\w+\b', ''),
        # Remove words that have punctuation attached to them
        (r'\b\w*[\.,;\'"!?]+\w+\b', ''),
        # Remove minimal replies
        (r'^\s*Reply-To [^\w\s]+\s*$', ''),
        # Basic email removal
        (r'\S+@\S+', ''),
    ]
    
    # Apply the cleaning rules to the comment
    for pattern, replacement in cleaning_rules:
        comment = re.sub(pattern, replacement, comment)

    # Expand contractions
    comment = contractions.fix(comment)

    # Correct spelling
    comment = spell_checker.correction(comment)
    
    # Ensure comment is not an empty string after cleaning
    if comment is None or not comment.strip():
        return ""
    
    return comment

def get_stopwords():
    """Create a set of stopwords, including custom ones."""
    custom_stopwords = [
        # List custom stopwords here if needed
    ]
    return set(stopwords.words("english")) | set(custom_stopwords)

def get_spell_checker():
    """Create a spell checker instance."""
    return SpellChecker()

class DatasetCleaner:
    def __init__(self, input_folder):
        self.input_folder = input_folder

    def clean_comments(self, comments, custom_stopwords, spell_checker):
        """Clean the comments section of each entry."""
        unique_comments = set()  # To store unique comments
        cleaned_comments = []    # To store cleaned comments
        
        for entry in tqdm(comments, desc="Cleaning comments", unit="comment"):
            if 'comment' in entry and entry['comment']:
                cleaned_comment = clean_comment(entry['comment'], custom_stopwords, spell_checker)
                if cleaned_comment and cleaned_comment not in unique_comments:
                    unique_comments.add(cleaned_comment)
                    cleaned_comments.append(entry)
        return cleaned_comments

    def _clean_json_file(self, file_path, custom_stopwords, spell_checker):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            cleaned_data = self._clean_json_data(data, custom_stopwords, spell_checker)
        return cleaned_data

    def _clean_json_data(self, data, custom_stopwords, spell_checker):
        if isinstance(data, list):
            cleaned_data = []
            for entry in tqdm(data, desc="Processing entries", unit="entry"):
                if 'created_utc' in entry and entry['created_utc']:  # Check if 'created_utc' key exists
                    # Convert Unix timestamp to formatted date
                    entry_date = datetime.utcfromtimestamp(int(entry['created_utc'])).strftime('%d %b %Y')
                else:
                    entry_date = None

                # Apply cleaning rules to the 'body' field
                cleaned_comment = clean_comment(entry.get('body', ''), custom_stopwords, spell_checker)

                # Change 'body' to 'comment' and include the formatted date
                cleaned_entry = {
                    'date': entry_date,
                    'comment': cleaned_comment
                }
                cleaned_data.append(cleaned_entry)

            return cleaned_data

    def clean_dataset(self):
        """Clean the entire dataset."""
        custom_stopwords = get_stopwords()
        spell_checker = get_spell_checker()
        json_files = [file for file in os.listdir(self.input_folder) if file.endswith(".json")]
        
        for file_name in tqdm(json_files, desc="Processing files", unit="file"):
            file_path = os.path.join(self.input_folder, file_name)
            print(f"Cleaning file: {file_name}")
            cleaned_data = self._clean_json_file(file_path, custom_stopwords, spell_checker)

            # Remove empty comments
            non_empty_comments = [entry for entry in cleaned_data if 'comment' in entry and entry['comment'].strip() != '']

            # Write cleaned data to a new file
            if non_empty_comments:
                new_file_name = "clean_" + file_name
                new_file_path = os.path.join(self.input_folder, new_file_name)
                with open(new_file_path, 'w', encoding='utf-8') as file:
                    json.dump(non_empty_comments, file, indent=2)
                print(f"Processed file: {file_name} - Cleaned data saved to: {new_file_name}")
            else:
                print(f"Processed file: {file_name} - No non-empty comments found")

            # Remove original file
            os.remove(file_path)
            print(f"Removed original file: {file_name}")

if __name__ == "__main__":
    folder_path = input("Enter the folder path containing JSON files: ")
    cleaner = DatasetCleaner(folder_path)
    cleaner.clean_dataset()

