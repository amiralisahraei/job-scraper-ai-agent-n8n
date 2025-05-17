from flask import Flask, jsonify
from scraper import scrape_jobs

app = Flask(__name__)


@app.route("/")
def index():
    result = scrape_jobs()
    return jsonify(result)

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)