# dataset-cleaner

# Extraction Script
Setup:

Place your JSON files containing Reddit data in a folder.
Using the Extraction Script:

Run the extraction script (extract_reddit_data.py).
Ensure the input_folder_path and output_folder_path variables point to the correct locations.
The script will extract relevant data from each zst file and save the extracted data to new JSON files suffixed with "_extracted".
It skips lines that cannot be decoded as JSON.
Example:
Suppose you have a folder named reddit_data containing zst files with Reddit data. To clean the data, run the cleaning script. Then, to extract specific fields from the cleaned data, run the extraction script. Ensure you update the file paths in the scripts accordingly.

# Cleaning Script
Requirements:

Ensure you have the necessary Python libraries installed. You can install them using pip install:
Copy code
nltk
spellchecker
contractions
tqdm
Setup:

Place your JSON files containing Reddit data in a folder.
Ensure that your JSON files have the structure where each line represents a JSON object containing Reddit data, typically with fields like created_utc and body.
Using the Cleaning Script:

Run the cleaning script (clean_reddit_data.py).
When prompted, enter the path to the folder containing your JSON files.
The script will process each JSON file, clean the comments, and save the cleaned data to new JSON files prefixed with "clean_".
Original files will be removed after processing.
