from flask import Flask, render_template, request
from search import perform_search

app = Flask(__name__)
results_per_page = 10

@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    results = []
    
    if request.method == "POST":
        query = request.form["query"]
        query_tokens = query.split()
        results = perform_search(query_tokens)
        page = 1
    else:
        query = request.args.get("query", "")
        page = int(request.args.get("page", 1))
        
        if query:
            query_tokens = query.split()
            results = perform_search(query_tokens)

    start = (page - 1) * results_per_page
    end = min(start + results_per_page, len(results))
    paginated_results = results[start:end]

    total_pages = len(results) // results_per_page
    if len(results) % results_per_page != 0:
        total_pages += 1

    return render_template("interface.html", query=query, results=paginated_results, page=page, total_pages=total_pages)

if __name__ == "__main__":
    app.run(debug=False)
