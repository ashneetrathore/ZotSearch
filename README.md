# :mag: ZOT SEARCH

## :open_book: OVERVIEW
Date: March 2025\
Developer(s): Ashneet Rathore, Nura Ahmed Nasir Abdalla\
Based on assignment instructions from Prof. Iftekhar Ahmed and Prof. Cristina Lopes


## :gear: HOW IT WORKS

## :open_file_folder: PROJECT FILE STRUCTURE
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

## :rocket: CONFIGURATION
### :hammer: BUILD THE INVERTED INDEX
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
**2. Run the program**
```bash
g++ -std=c++17 app/main.cpp app/convert.cpp -o app
./app
```

## :wrench: TRY IT OUT
