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

### :hammer: CONFIGURATION PART I: BUILDING THE INVERTED INDEX
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
```

**3. Run the program that builds the inverted index**
```bash
python3 invertedindex.py
```

**4. Once the program has terminated, directories titled ```json``` and ```txt```, each with their own set of files, should exist in the root project directory**
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

### :rocket: CONFIGURATION PART II: RUN THE SEARCH ENGINE
**1. Install the necessary libraries**
```bash
pip install nltk
pip install ujson
```

**2. Launch a local Flask web server**
```bash
python3 app.py
```

**3. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser to use the search engine**

### :wrench: TRY IT OUT
