from pathlib import Path
import os
import math
import json
import hashlib
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from collections import defaultdict
from sortedcontainers import SortedDict
import heapq
from bs4 import BeautifulSoup
import warnings
from bs4 import XMLParsedAsHTMLWarning
from bs4 import MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
# Imported data structures/functions comments:
# stem() method of PorterStemmer -> O(m * n), m = # of words, n = # avg length of words
# tokenize() method from RegexpTokenizer -> O(n), where n = # of characters in input string
# defaultdict has the same time complexity as the built in dict() from Python
# Insertion into SortedDict -> O(log n), where n = # of key-value pairs
# Insertion into/popping from heapq -> O(log n), where n = # of elements in the min-heap

def set_up_files():
    json_directory = Path("json")
    txt_directory = Path("txt")
    
    # Creates the json and txt directory if not already created
    json_directory.mkdir(parents=True, exist_ok=True)
    txt_directory.mkdir(parents=True, exist_ok=True)

    # Creates/resets txt files (removes previous writes)
    with open("txt/log.txt", "w") as log_file:
        log_file.write("")
    
    with open("txt/complete_index.txt", "w") as index_file:
       index_file.write("")

    with open("txt/term_offsets.txt", "w") as offset_file:
       offset_file.write("")

def creating_partial_indexes() -> None:
    # Inverted index consists of <term, posting> pairs
    # In partial indexes, posting will consist of <docId, tf> pairs
    # In complete index, posting will consist of <docId, tf-idf> pairs
    # Example structure of inverted index:
    # {
    # "anteater": {1: 4.34393, 45: 1.32323},
    # "bear": {32: 2.23423, 2: 1.32322}
    # }
    # EX: In above index, anteater is given score 4.34393 in doc 1 and score 1.32323 time in doc 45.
    partial_index = defaultdict(dict)
    # Initialize a mapping of doc IDs to urls
    doc_map = dict()
    # Initialize a set to store hashes of page content for duplicate detection
    seen_hashes = set()
    # Declare these as global, since they will be modified in this function
    global indexed_doc_count
    global partial_index_count

    # Get the DEV folder
    dir_path = Path('developer/DEV')
    # Iterate through the domain folders in DEV
    for dir in dir_path.iterdir():
        # Iterate through the individual web pages inside each domain
        for file in dir.iterdir():
            # Open the JSON file representing the web page
            # If encoding error is encountered, the error is caught and program moves onto next file
            try:
                web_page_file_path = 'developer/DEV/'+ dir.name + "/" + file.name
                with open(web_page_file_path, 'r', encoding='utf-8') as webfile:
                    # Parse the JSON file into a dictionary called file_content
                    file_content = json.load(webfile)
                    # Access the content part of the dictionary and parse it using BeautifulSoup
                    soup = BeautifulSoup(file_content['content'], 'html.parser')
                    # Extract only the text content from the web page
                    text_content = soup.get_text(separator=" ", strip=True)

                    # Check for no content and duplicate pages
                    if text_content != "" and not is_duplicate(text_content, seen_hashes):
                        # Get a dictionary of <term, freq> pairs for that web page
                        token_dict = get_token_dict(text_content)

                        # Check if the page has valid tokens (if token dictionary length > 0)
                        # If not, do not add document to doc map or partial index 
                        if len(token_dict) != 0:
                            # Get important tags
                            # Add weight to the text inside those tags in the token dictionary
                            important_tags = soup.find_all(['h1', 'h2', 'h3', 'b', 'strong', 'title'])
                            token_dict = add_weights(important_tags, token_dict)

                            # Increment the count for the number of indexed documents
                            indexed_doc_count += 1

                            # Add a <docId, url> pair to the doc_map
                            doc_map[indexed_doc_count] = file_content['url']

                            # Add to the partial index stored in memory
                            add_to_index(indexed_doc_count, token_dict, partial_index)
                        
                    # Periodically save the partial index to a file if threshold met 
                    if (len(partial_index) >= NUMBER_OF_TERMS_THRESHOLD):
                        write_partial_index(partial_index)
                        # Empty the partial index in memory
                        partial_index.clear()    
            except Exception as e:
                continue
    
    # If partial index isn't empty, save it and the doc_map to a file
    # This is for the case where let's say we are creating a new partial index every 10 webpages
    # If we hit 5 web pages and there's no more files to parse, partial index is never saved to a file b/c...
    # The threshold of 10 web pages wasn't hit. This takes care of that case
    if len(partial_index) != 0:
        write_partial_index(partial_index)
        partial_index.clear()
    
    # Write the doc map to a file
    write_document_mapping(doc_map)
    doc_map.clear()

def is_duplicate(content: str, seen_hashes: set):
    # Assigns a hash to a content string
    # If hash has been seen before --> duplicate detected --> Returns True
    hashed_page = hashlib.md5(content.encode('utf-8')).hexdigest()
    if hashed_page in seen_hashes:
        return True
    else:
        seen_hashes.add(hashed_page)
        return False

def get_token_dict(content: str) -> defaultdict:
    # Get a list of all tokens from a content string (token = alphanumeric sequence)
    tokens = tokenizer.tokenize(content)
    # Use Porter Stemmer for stemming
    stemmed_tokens = [porter_stemmer.stem(token) for token in tokens]
    # Call compute_word_frequencies to get dictionary of <token, frequency> pairs
    return compute_word_frequencies(stemmed_tokens)

def compute_word_frequencies(tokens: list) -> defaultdict:
    # Returns a dictionary that maps the tokens in the list to the number of their occurrences
    word_count = defaultdict(int)
    for t in tokens:
        word_count[t] += 1
    return word_count

def add_weights(important_tags, token_dict: defaultdict) -> defaultdict:
    # Initialize a list of important tokens
    important_tokens = []
    for tag in important_tags:
        # Get content inside those tags
        content = tag.get_text(separator=" ", strip=True)
        # Tokenize and stem the content, adding the tokens to the list of important tokens 
        tokens = tokenizer.tokenize(content)
        important_tokens.extend([porter_stemmer.stem(token) for token in tokens])

    # The important token has already been counted once
    # Iterate through the important tokens, and add 2 to the token dictionary
    # This essentially places 3 times more importance on the tokens between the important tags
    for token in important_tokens:
        token_dict[token] += 2
    return token_dict

def add_to_index(docId: int, token_dict: dict, partial_index: defaultdict) -> None:
    # token identifies the key in the outer dictionary
    # docId identifies the key in the inner dictionary
    # Add a <docId, tf> pair to the inner dictionary of each token

    for token, freq in token_dict.items():
        number_of_terms_in_doc = len(token_dict)
        tf = (1 + math.log10(freq)) / math.log10(number_of_terms_in_doc)
        # Round the tf to 5 decimal places
        partial_index[token][docId] = round(tf, 5)    

def write_partial_index(partial_index: dict) -> None:
    # Declare variable as global b/c it's modified in this function
    global partial_index_count
    # Increment the count of the number of partial index files
    partial_index_count += 1
    # Convert partial_index into a SortedDict to ensure keys are sorted
    sorted_index = SortedDict(partial_index)

    # json.dumps() converts the dictionary into a JSON string
    json_string = json.dumps(sorted_index)
    partial_index_file_name = "json/partial_index" + str(partial_index_count) + ".json"
    # Write the partial inverted index JSON string to a file
    with open(partial_index_file_name, 'w') as index_file:
        index_file.write(json_string)
    
    # Update log file
    write_log_file(f"{indexed_doc_count} docs indexed")
    write_log_file("Finished a write")

def write_log_file(log_text):
     # Write a string to a log file
     with open("txt/log.txt", "a") as log_file:
         log_file.write(f"{log_text}\n")

def write_document_mapping(doc_map: dict) -> None:
    with open("txt/document_mapping.txt", 'w') as map_file:
        for url in doc_map.values():
            map_file.write(f"{url}\n")

def load_chunk(partial_index_id: int, positions: list, chunk_size: int):
    # DISCLAIMER : This method loads only 1 partial index into memory at once
    # It then returns only a chunk of that partial index
    
    # Open the partial index file
    file_name = f"json/partial_index{partial_index_id + 1}.json"
    with open(file_name, 'r') as file:
        # Load the entire partial index into memory
        partial_index = json.load(file)
        # Get a list of terms in that partial index file
        terms = list(partial_index.keys())
        # Get the number of terms in the partial index file
        size_of_partial_index = len(terms)

        # Get the position of where we left off last time in the partial index file
        current_pos = positions[partial_index_id]
        # If the position where we left off = size of the partial index file, file has been exhausted
        # In that case, return empty dictionary
        if current_pos == size_of_partial_index:
            return {}
        
        # Get the position where we want to read up to based on the chunk size
        # If adding the chunk size to the current position exceeds size of file --> cause index out of range
        # In that case, we are on the last chunk of the file --> use the size as the ending position
        end_pos = min(current_pos + chunk_size, size_of_partial_index)

        # Construct the partial index chunk using the terms
        terms = terms[current_pos: end_pos]
        chunk = {term: partial_index[term] for term in terms}
        # Update the current position of the partial index file
        positions[partial_index_id] = end_pos

        # Return the chunk of the partial index
        return chunk

def merging_indexes(partial_index_count: int) -> None:
    # Declare variable as global b/c it's modified in this function
    global unique_term_count
    # Initialize a complete index that will be the result of merging the partial indexes
    complete_index = dict()
    # Initialize a list of all the partial indexes
    partial_indexes = []
    # Initialize a list of iterators for each partial index file
    partial_index_pos_trackers = []
    # Initialize a list of position trackers for each partial index file (used for tracking batches)
    positions = [0] * partial_index_count

    # Iterate through the partial index files
    for partial_index_id in range(0, partial_index_count):
        # For each file, get the first chunk of terms
        partial_index_chunk = load_chunk(partial_index_id, positions, PARTIAL_INDEX_CHUNK_SIZE)
        
        # Add the partial index and iterator object for the keys of that partial index to their respective lists
        partial_indexes.append(partial_index_chunk)
        partial_index_pos_trackers.append(iter(partial_index_chunk))
    
    # Initialize a min_heap that will store (term, partial_index_id) pairs
    # partial_index_id = the particular partial index
    min_heap = []
    for partial_index_id, tracker in enumerate(partial_index_pos_trackers):
        # Populate the heap with the first terms from all the partial indexes
        term = next(tracker, "")
        if term != "":
            heapq.heappush(min_heap, (term, partial_index_id))
    
    # Initialize an inner dictionary for the postings associated w/h each term
    merged_postings = dict()
    # Store the last term that is popped from the heap
    last_term = ""
    # Store the current first character of the terms (begin with "0")
    current_char = "0"
    
    # char_offsets and term_offset dictionaries will be written to files, and used for efficient searching
    # To understand their roles, look at comments inside search.py
    # Initialize a character offset dictionary
    char_offsets = dict()
    # Initialize a term offset dictionary
    term_offsets = {"0": 0}

    # While min heap is not empty (all partial index files haven't been exhausted)
    while len(min_heap) != 0:
        # Pop an entry of the form (term, id of partial index) from the heap
        entry = heapq.heappop(min_heap)
        current_term, partial_index_id = entry

        # Heap pops out the smallest term (alphabetically)
        # If multiple partial indexes have a common term, that term will be popped out consecutively from the heap
        # This is why storing the last term is useful
        # If last term = current term -> posting for last and current term need to be merged
        # Otherwise, all mergings have been completed for the last term, and we move onto the mergings of a new term
        
        # EX: min_heap = [("baby, 3"), ("cold, 2"), ("baby", 1)]
        # In partial index 3: "baby": {1: 4, 2: 1}
        # In partial index 2: "cold": {1: 10}
        # In partial index 1: "baby": {6: 3, 7: 8}
        # 1st iteration | Pop ("baby", 1), Update last_term = "baby", posting = {1: 4, 2: 1}
        # 2nd iteration | Pop ("baby", 3), last_term = current_term, Update posting = {1: 4, 2: 1, 6: 3, 7: 8}
        # 3rd iteration | Pop ("cold", 2), last term != current term, Store posting for "baby" in complete index...
        #               last_term = "cold", posting = {1: 10}

        if last_term != current_term:
            # This check is put in place for the first iteration where there's no last term (empty string)
            # The check stops from putting an empty string into the complete index as a key
            if last_term != "":
                
                # Periodically save the complete index to a file if threshold met
                if len(complete_index) == NUMBER_OF_TERMS_THRESHOLD:
                    write_log_file("Writing complete index to file")

                    with open("txt/complete_index.txt", "a") as index_file:
                        save_prev_term = ""
                        save_prev_pos = 0
                        for term, posting in complete_index.items():
                            # Update the count of unique terms
                            unique_term_count += 1
                            
                            # Every 1000 terms, store the term in a term dictionary
                            # If a new first character is encountered...
                            # Store this character in the term dictionary AND...
                            # Write the term dictionary to a file 
                            if unique_term_count % 1000 == 0 or current_char != term[0]:
                                if current_char != term[0]:
                                    with open("txt/term_offsets.txt", "a") as offset_file:
                                        char_offsets[current_char] = [offset_file.tell()]
                                        # Stores the last term in the char ranges to the term dictionary
                                        # EX: "azotic", "azul", "b", "baby" --> Stores "azul"
                                        term_offsets[save_prev_term] = save_prev_pos
                                        for key, value in term_offsets.items():
                                            offset_file.write(f'{key}:{value}\n')
                                        # Clear term offset dictionary
                                        term_offsets = dict()
                                        char_offsets[current_char].append(offset_file.tell())
                                    
                                    # Reset the current char
                                    current_char = term[0]
                                
                                term_offsets[term] = index_file.tell()
                            
                            save_prev_term = term
                            save_prev_pos = index_file.tell()
                            # Write to complete index
                            index_file.write(f'{term}|{json.dumps(posting)}\n')
                    
                    # Clear complete index dictionary
                    complete_index = dict()

                df = len(merged_postings)
                # Calculate the idf part of tf-idf
                idf = math.log10(indexed_doc_count / df)
                # Update the postings to store tf-idf associated with each doc id
                merged_postings = {int(doc_id): round(tf * idf, 5) for doc_id, tf in merged_postings.items()}
                # Store the document frequency w/h doc id 0 (there's no document w/h id 0)
                merged_postings[0] = df
                sorted_merged_postings = SortedDict(merged_postings)
                # Store the completed merged postings for the last term in the complete index
                complete_index[last_term] = sorted_merged_postings
                # Reset the postings for the current term
                merged_postings = dict()

            # Update the last term (no need to do this if last_term == current_term)
            last_term = current_term
        
        # Update the posting dictionary for the current term (performs merges)
        merged_postings.update(partial_indexes[partial_index_id][current_term])

        # Get the next term in the partial index
        next_term = next(partial_index_pos_trackers[partial_index_id], "")
        # If chunk of partial index file hasn't been exhausted, push the next term in the file to the heap
        if next_term != "":
            heapq.heappush(min_heap, (next_term, partial_index_id))
        # Else chunk has been exhausted
        else:
            # Get a new chunk
            partial_index_chunk = load_chunk(partial_index_id, positions, PARTIAL_INDEX_CHUNK_SIZE)
            # If new chunk is empty dictionary --> reached end of partial index file
            # Otherwise, there's still more terms
            if partial_index_chunk != {}:
                # Re-assign partial_index and pos_tracker lists based off of the new chunk
                partial_indexes[partial_index_id] = partial_index_chunk
                partial_index_pos_trackers[partial_index_id] = iter(partial_index_chunk)
                # Get the first term of the new chunk and add it to the min heap
                term = next(partial_index_pos_trackers[partial_index_id], "")
                if term != "":
                    heapq.heappush(min_heap, (term, partial_index_id))
        
    # Store the posting for the last term
    # Takes care of when heap is exhausted (there's no more current terms, so the current merge_postings are never stored inside the loop)
    sorted_merged_postings = SortedDict(merged_postings)
    complete_index[last_term] = sorted_merged_postings

    # Write the remaining terms in the complete index to a file (just as before)
    write_log_file("Writing complete index to file")
    with open("txt/complete_index.txt", "a") as index_file:
        save_prev_term = ""
        save_prev_pos = 0
        for term, posting in complete_index.items():
            # Update the count of unique terms
            unique_term_count += 1
            if unique_term_count % 1000 == 0 or current_char != term[0]:
                if current_char != term[0]:
                    with open("txt/term_offsets.txt", "a") as offset_file:
                        char_offsets[current_char] = [offset_file.tell()]
                        term_offsets[save_prev_term] = save_prev_pos
                        for key, value in term_offsets.items():
                            offset_file.write(f'{key}:{value}\n')
                        term_offsets = dict()
                        char_offsets[current_char].append(offset_file.tell())
                    
                    current_char = term[0]
                
                term_offsets[term] = index_file.tell()
            
            save_prev_term = term
            save_prev_pos = index_file.tell()
            index_file.write(f'{term}|{json.dumps(posting)}\n')

        # Write the remaining term offsets to a file
        with open("txt/term_offsets.txt", "a") as offset_file:
            char_offsets[current_char] = [offset_file.tell()]
            term_offsets[save_prev_term] = save_prev_pos
            for key, value in term_offsets.items():
                offset_file.write(f'{key}:{value}\n')
            char_offsets[current_char].append(offset_file.tell())

    # Write the char offsets to a file
    with open("json/char_offsets.json", "w") as offset_file:
        json_string = json.dumps(char_offsets)
        offset_file.write(json_string)

def get_file_size_in_kb(file_name):
    # Get the size of the file in bytes
    file_size_bytes = os.path.getsize(file_name)
    # Convert bytes to KB
    file_size_kb = file_size_bytes / 1024  # 1 KB = 1024 Bytes
    return int(file_size_kb)

if __name__ == '__main__':
    porter_stemmer = PorterStemmer()
    tokenizer = RegexpTokenizer(r'[a-zA-Z0-9]+')
    # Initialize a tracker for the number of partial index files
    partial_index_count = 0
    # Initialize a tracker of the number of indexed documents
    indexed_doc_count = 0
    # Initialize a tracker for the number of unique terms
    unique_term_count = 0

    NUMBER_OF_TERMS_THRESHOLD = 300000
    NUMBER_OF_DOCS_THRESHOLD = 10000
    PARTIAL_INDEX_CHUNK_SIZE = 100000

    # Create/reset some necessary directories/files
    set_up_files()

    creating_partial_indexes()
    merging_indexes(partial_index_count)

    # Store analytics in log file
    file_size = get_file_size_in_kb("txt/complete_index.txt")
    write_log_file(f"Total number of documents indexed: {indexed_doc_count}")
    write_log_file(f"Total number of unique terms: {unique_term_count}")
    write_log_file(f"Size of full index: {file_size} KB")
