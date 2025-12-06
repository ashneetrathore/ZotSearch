from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import time
import heapq
import ujson
from collections import defaultdict
import sys
# Imported data structures/functions comments:
# stem() method of PorterStemmer -> O(m * n), m = # of words, n = # avg length of words
# tokenize() method from RegexpTokenizer -> O(n), where n = # of characters in input string
# defaultdict has the same time complexity as the built in dict() from Python
# Insertion into/popping from heapq -> O(log n), where n = # of elements in the min-heap

def perform_search(query: list) -> list:
    # Start timer
    start_time = time.perf_counter() * 1000
    
    # Tokenize the query, get the associated posting list for each term, intersect those lists
    term_dict = get_token_dict(query)
    postings = get_postings(term_dict)
    
    doc_ids = union(postings)
    # If there's no doc that has all the terms in the query -> no matched results -> return []
    if len(doc_ids) == 0:
        return []
    
    # At this point, the response has been retrieved -> record end time
    # Ranking time IS NOT included in the total time
    end_time = time.perf_counter() * 1000
    elapsed_time1 = end_time - start_time
    
    # Rank the documents based on the tf-idf score
    ranked_docs = rank_docs(postings, doc_ids)

    start_time = time.perf_counter() * 1000
    # Get the associated urls for the ranked documents (include in total time)
    result_urls = get_urls(ranked_docs)
    end_time = time.perf_counter() * 1000
    elapsed_time2 = end_time - start_time

    # Log the time for reference
    with open("txt/time.txt", "w") as time_file:
        time_file.write(f"Response time: {elapsed_time1 + elapsed_time2} ms\n")
    
    return result_urls

def get_token_dict(query: list) -> defaultdict:
    tokenizer = RegexpTokenizer(r'[a-zA-Z0-9]+')
    porter_stemmer = PorterStemmer()
    
    # Tokenize and stem each term in the query
    stemmed_tokens = []
    for term in query:
        terms = tokenizer.tokenize(term)
        for token in terms:
            stemmed_tokens.append(porter_stemmer.stem(token))

    # Call compute_word_frequencies to get dictionary of <token, frequency> pairs
    return compute_word_frequencies(stemmed_tokens)

def compute_word_frequencies(tokens: list) -> defaultdict:
    # Returns a dictionary that maps the tokens in the list to the number of their occurrences
    word_count = defaultdict(int)
    for t in tokens:
        word_count[t] += 1
    return word_count

def get_postings(term_dict: defaultdict) -> list:
    postings = []

    # Load the char_offsets file into a dictionary
    with open("json/char_offsets.json", "r") as offset_file:
        char_offsets = ujson.load(offset_file)
    
    # Open the complete index and term_offsets txt files
    with open('txt/complete_index.txt', 'rb') as index_file, open('txt/term_offsets.txt', 'rb') as offset_file:
        # Iterate through each unique term in the query
        for term in term_dict.keys():
            # Get the first char of the term and its associated start & end position in the offset file
            start_pos, end_pos = char_offsets[term[0]]

            # Jump to the start position in the offset file
            offset_file.seek(start_pos)
            bounds = [0, 0]
            # Continue while the current position in the offset file is <= end position
            while offset_file.tell() <= end_pos:
                # Get the line in the offset file, split into a list with two elements
                line = offset_file.readline().decode('utf-8').strip().split(":")
                # 1st element = word, 2nd element = associated position in the complete index
                word = line[0]
                pos = int(line[1])
        
                # If word comes before term lexicographically, set/reset lower bound
                # If word comes after term lexicographically, set upper bound --> break out of loop
                # If word is the term, the lower and upper bound are the same --> break out of loop
                if word < term:
                    bounds[0] = pos
                elif term < word:
                    bounds[1] = pos
                    break
                else:
                    bounds = [pos, pos]
                    break
            
            # Jump to the start position in the complete index using the lower bound
            index_file.seek(bounds[0])
            # Continue while the current position in the complete index file is <= upper bound
            while index_file.tell() <= bounds[1]:
                line = index_file.readline().decode('utf-8').strip().split("|")
                word = line[0]
                
                # If match found in the complete index, append that term's posting to the list of postings
                if word == term:
                    postings.append(ujson.loads(line[1]))
                    break
    
    # Each posting list in postings corresponds to a term, as it appears in the query
    # A posting list is a dictionary of <doc_id, tf-idf> pairs
    # EX: If query is "Antartica global warming", the postings will look like this:
    # [posting list for "Antartica", posting list for "global", posting list for "warming"]
    return postings

def union(postings: list) -> set:
    # Get the union of all the doc ids --> Boolean OR retrieval
    all_doc_ids = set()
    
    for posting in postings:
        current_doc_ids = set(posting.keys())
        all_doc_ids |= current_doc_ids

    # Remove the doc id "0" (b/c this isn't an actual document)
    # "0" just stored the length of the posting list
    all_doc_ids.remove("0")
    return all_doc_ids

def rank_docs(postings: list, doc_ids: set) -> list:
    # Initialize a dictionary that will store <doc_id, total score> pairs
    doc_scores = dict()
    # Sums the tf-idf scores of ALL query terms for each document (each term has an associated posting list)
    # EX: If doc_ids = {"2", "4", "7"}, and postings look like this...
    # postings = [{"2": 1, "3": 7, "4": 4, "7": 3, "9": 2},
    #              {"2": 2, "4": 10, "7": 12},
    #               {"2": 1, "4": 1, "5": 4, 7": 9, "9": 1, "12": 9}]
    # Then, the scores for doc_ids 
    # "2" = 1 + 2 + 1 = 4,
    # "3" = 7,
    # "4" = 4 + 10 + 1 = 15,
    # "5" = 4,
    # "7": 3 + 12 + 9 = 24,
    # "9": 2 + 1 = 3,
    # "12": 9
    for doc_id in doc_ids:
        doc_scores[int(doc_id)] = round(sum(posting.get(doc_id, 0) for posting in postings), 5)

    # Sort the doc ids by score, descending
    sorted_by_scores = [key for key, _ in sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)]
    return sorted_by_scores

def get_urls(doc_ids: list) -> list:
    result_urls = []
    with open("txt/document_mapping.txt", 'r') as map_file:
        content = map_file.read().strip()
        # Split the urls by newline -> Index of content list == doc_id - 1
        content = content.split("\n")
        for doc_id in doc_ids:
            result_urls.append(content[doc_id - 1])
    return result_urls


def show_results(result_urls: list) -> None:
    if len(result_urls) == 0:
        print("No matched results\n")
    else:
        # Print the top 10 results (or less if there's not 10) to the console
        top_10 = ""
        num_results = min(10, len(result_urls))
        for i, result in enumerate(result_urls[:num_results], start=1):
            top_10 += f"{i} | {result}\n"
        print(top_10)

    # Store the remaining results inside a file
    with open("txt/search_results.txt", "w") as result_file:
        for i, url in enumerate(result_urls, start=1):
            result_file.write(f"{i} | {url}\n")

if __name__ == '__main__':
    query = sys.argv[1:]
    print(f"?{query}?")
    result_urls = perform_search(query)
    show_results(result_urls)
