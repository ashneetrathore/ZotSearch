# :mag: ZOT SEARCH

## :open_book: OVERVIEW
Date: March 2025\
Developer(s): Ashneet Rathore, Nura Ahmed Nasir Abdalla

Zot Search is a domain-specific search engine for UCI ICS (University of California, Irvine Information and Computer Sciences), supporting fast search across 55,000+ departmental pages. The system consists of two components found in most modern search engines: an indexer, which processes and stores page content, and a retrieval system, which fetches results from the index and scores them for relevancy. Users can enter query terms and receive a ranked list of relevant results, with response times under 300 ms.

## :film_strip: DEMO
![Demo](demo.gif)

## :gear: HOW IT WORKS
Built in **Python**, the search engine's architecture prioritizes memory efficiency and fast query response times.\

The indexer component of the search engine builds a complete **inverted index** from the downloaded corpus. It uses **BeautifulSoup** to parse raw HTML and extract text, and then processes terms using **tokenization** and **lemmatization** via **NLTK**. Partial inverted indexes are created on disk, and finally these indexes are merged into a single index.

Real-world search engines are designed to handle data far larger than what can fit in memory. Designed with **scalability** in mind, this search engine is implemented under the assumption that the entire inverted index cannot be held in memory at once. During index construction, the indexer periodically offloads the in-memory hash map to disk as partial indexes. Even when building the complete index, the indexer writes the hash map to a file whenever a specified memory threshold is reached.

The indexer is also responsible for computing and storing the relevancy score of each page for every term. This search engine uses a **TF-IDF-based ranking algorithm**, applying higher weights to text considered more important based off of HTML tags. For context, the completed inverted index is structured as a map of `(term → posting)` pairs, where each posting is itself a map of `(document id → relevancy score)` pairs.

The ranking and retrieval component relies on a **multi-level index** structure, created during indexing, to achieve fast lookups. Alongside the complete index, the indexer also generated...
- An index of  `(character, [start position, end position])` pairs
- An index of `(term, position)` pairs

Positions represent offsets in the next level of the index, allowing the system to jump directly to the relevant range of entries rather than scanning the complete index from the beginning. Conceptually, this algorithm is similar to binary search in that it significantly reduces the **search space** by eliminating irrelevant regions.

To illustrate how retrieval works, consider the query "career":
1. The retrieval system looks at the first character of the term "career" -"c" - and uses the character offset index to retrieve its start and end positions, representing the range of terms starting with "c" in the term offset index. Let's say the start and end positions for "c" are [100, 150].
2. The algorithm jumps to the position 100 in the term offset index and scans until it finds the two terms "career" falls between - say, "cantral" and "carridin". Once these bounding terms are found, scanning terminates because the end position 150 only indicates the maximum possible range to consider. The positions associated with the bounding terms - say 4000 and 4300 - become the lower and upper bounds for searching the completed inverted index.
3. The algorithm jumps to the lower bound position 4000 in the complete index and scans until it finds the exact match for the term "career" or reaches the upper bound position 4300.

The retrieval system uses **OR query logic**, fetching a broad set of documents to maximize **recall**, while the relevancy scores computed by the indexer maximize **precision**. Retrieved documents are then ranked by relevance, with the most relevant pages appearing at the top. Finally, the results are served to the frontend via a lightweight **Flask** backend for display.

## :open_file_folder: PROJECT FILE STRUCTURE
```bash
zot-search/
│── app.py               # Flask app entry point
│── search.py            # Search, ranking, and result logic
│── inverted_index.py    # Inverted index construction logic
│── templates/          
│   └── interface.html   # Flask frontend interface
│── README.md            # Project documentation
│── .gitignore           # Ignored files
└── demo.gif             # Demo GIF
```

## :hammer: CONFIGURATION
**1. Clone the repository**
```bash
git clone https://github.com/ashneetrathore/zot-search.git
```

**2. Install the necessary libraries**
```bash
pip install nltk
pip install sortedcontainers
pip install beautifulsoup4
pip install ujson
```

<a name="anchor-point"></a>

**3. Download `developer.zip` from this [link](https://drive.google.com/file/d/1VDKl8NkZjRGGToOhHLVgtUEckZUxetwX/view?usp=sharing) to the project root directory and unzip it. This archive contains the full web page corpus for the search engine**
```bash
cd zot-search
unzip developer.zip
```

**4. Run the program that builds the inverted index**
```bash
python3 invertedindex.py
```

> [!TIP]
> `invertedindex.py` can take a couple hours to complete. To avoid interruptions, consider running it in the background using [`tmux`](https://linuxize.com/post/getting-started-with-tmux/) or another terminal multiplexer

**5. Once the program terminates, the following ```json``` and ```txt``` directories should exist in the project root, containing their respective files**

```bash
zot-search/
├── json/
│   ├── char_offsets.json      # Character offset data for fast searching
│   ├── partial_index1.json    # Partial index of terms
│   ├── partial_index2.json    # Partial index of terms
│   └── ...                    # Additional partial index files
├── txt/
│   ├── complete_index.txt     # Merged index of all partial indices
│   ├── log.txt                # Program execution logs
│   ├── document_mapping.txt   # Document ids to URL mappings
│   └── term_offsets.txt       # Term offset data for fast searching
└── ...
```

## :rocket: EXECUTION
```bash
python3 app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) to use the search engine.

## :wrench: TRY IT OUT
1. Enter a query into the search bar and click `Search`.
2. The top 10 results will be displayed. Click any of the links to view the page, or click `Next` to load more results. 
3. To access the full list of results without interface pagination, open `search_results.txt` located in the `txt` directory.
4. To check the query response time, open `time.txt` located in the `txt` directory.

> [!IMPORTANT]
> Some of the links may return 403/404 errors because the content provided in `developer.zip` may be outdated compared to the current version of those web pages.

Sample query terms to input:
- Architecture
- Artificial intelligence
- Bayesian model
- Capstone projects
- Career fair
- Compiler programming
- Constraint networks course
- Database systems
- Neuroscience
- Pythagorean theorem
- Probabilistic reasoning
- Reinforcement learning
- Security
- Software engineering degree