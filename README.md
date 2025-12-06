## :mag: ZOT SEARCH

### :open_book: OVERVIEW
Date: March 2025\
Developer(s): Ashneet Rathore, Nura Ahmed Nasir Abdalla\
Based on assignment instructions from Prof. Iftekhar Ahmed and Prof. Cristina Lopes


### :gear: HOW IT WORKS

### :open_file_folder: PROJECT FILE STRUCTURE
```bash
ZotSearch/
│── app.py               # Launches Flask frontend and accepts queries
│── search.py            # Performs search, and ranks and returns results
│── inverted_index.py    # Builds the inverted index (preprocessing step)
│── templates/          
│   └── interface.html   # Renders the Flask frontend 
│── README.md            # Project documentation
└── .gitignore           # Specifies files and folders that shouldn't be included in the repo
```

### :hammer: CONFIGURATION
**1. Clone the repository**
```bash
git clone https://github.com/ashneetrathore/ZotSearch.git
cd ZotSearch
```

**2. Install the necessary libraries**
```bash
pip install nltk
pip install sortedcontainers
pip install beautifulsoup4
pip install ujson
```

**3. Run the program that builds the inverted index**
```bash
python3 invertedindex.py
```

> [!TIP]
> `invertedindex.py` can take a couple hours to complete. To avoid interruptions, consider running it in the background using [`tmux`](https://linuxize.com/post/getting-started-with-tmux/) or another terminal multiplexer

**4. Once the program terminates, ```json``` and ```txt``` directories should exist in the project root, containing their respective files**

```bash
ZotSearch/
├── json/
│   ├── char_offsets.json      # Stores character offsets for fast searching
│   ├── partial_index1.json    # Stores partial index of terms
│   ├── partial_index2.json    # Stores partial index of terms
│   └── ...                    # Additional partial index files
├── txt/
│   ├── complete_index.txt     # Stores a merged index of all partial indices
│   ├── log.txt                # Records program execution details
│   ├── document_mapping.txt   # Maps document ids to urls
│   └── term_offsets.txt       # Stores term offsets for fast searching
└── ...
```

### :rocket: EXECUTION
Launch a local Flask web server
```bash
python3 app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser to use the search engine

### :wrench: TRY IT OUT
1. After opening the application in your browser, enter a query into the search bar and click `Search`.
2. The top 10 results will be displayed. Click on any of the links to view the page.
    
    > [!NOTE]
    > Some of the links may return 403/404 errors because the content provided in developer.zip may be outdated compared to the current version of those web pages 
3. To view additional pages beyond the top 10, click `Next` to load the next set of results. 
4. To access the full list of results without interface pagination, open `search_results.txt` located in the `txt` directory.
5. To check the query response time, open `time.txt` located in the `txt`directory.

Here are some sample query terms you can input:
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