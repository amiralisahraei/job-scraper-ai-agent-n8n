# 🛠️ Telegram Job Scraper Bot with n8n AI Agent & Selenium

This project is a **Python-based job scraper** exposed as a Flask API, designed for integration with a Telegram bot via n8n workflows. It uses **Selenium** and **BeautifulSoup** to collect and filter job postings, and can be deployed locally or in the cloud using Docker.

---

## 📦 Features

- **Scrapes latest Python-related job offers**
- **Filters out saved/starred and already applied offers**
- **Returns structured data**: title, company, location, technologies, and link
- **REST API**: `/` endpoint returns job offers as JSON, `/health` for health checks
- **Ready for n8n integration**: Easily connect to Telegram bots and automation workflows
- **Dockerized**: Easily deployable anywhere Docker is supported

---

## 🔧 Technologies Used

- **Python**: `selenium`, `beautifulsoup4`, `flask`, `python-dotenv`
- **Chrome WebDriver** (headless, via Docker)
- **Docker** (for containerization)
- **n8n** (for workflow automation and Telegram bot integration)

---

## 🧠 Project Architecture

### 1. Python Web Scraper (`src/scraper.py`)

- Logs into a job portal using credentials from environment variables
- Navigates to the job search page
- Scrapes and filters job offers
- Returns results as a list of dictionaries

### 2. Flask API (`src/app.py`)

- **`/`**: Triggers the scraper and returns job offers as JSON
- **`/health`**: Simple health check endpoint

### 3. n8n Workflows (external, not included)

- **Workflow 1**: Triggered by Telegram messages, uses an AI Agent to process requests and fetch job data via the Flask API
- **Workflow 2**: Fetches job data from the Flask API and returns the top 20 offers

---

## ▶️ How to Run

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd job_offers_scrapy
```

### 2. Setup Python Environment (for local development)

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
EMAIL=your_email_here
PASSWORD=your_password_here
```

### 3. Run the Scraper API Locally

```bash
cd src
python app.py
```

- The API will be available at `http://localhost:5000/`
- Test with: `curl http://localhost:5000/health`

### 4. Build and Run with Docker

```bash
docker build -t flask_scraper_app .
docker run -p 5000:5000 --env EMAIL=your_email --env PASSWORD=your_password flask_scraper_app
```

### 5. Cloud Hosting (Optional)

You can host the scraper API on any cloud platform (such as AWS ECS, EC2, or similar).  
Once hosted, simply send HTTP requests from your n8n workflow to the API endpoint.

---

## 🧩 n8n Integration

- Set up a Telegram bot and connect it to n8n
- Import your n8n workflows (see screenshots below)
- Configure HTTP Request nodes to call your deployed Flask API

---

## 📷 Screenshots

![Workflow 1](/workflow_screenshots/workflow_1.png)

---

## 📄 License

MIT License

---

## 📝 File Structure

```
job_offers_scrapy/
├── Dockerfile
├── requirements.txt
├── README.md
├── deploy_aws_ecs.sh
├── src/
│   ├── app.py
│   └── scraper.py
└── workflow_screenshots/
    ├── workflow1.png
```

---

## ❗ Notes

- **Credentials:** Never commit real credentials to version control. Use `.env` for local, and environment variables or a secrets manager for production.
- **Cloud Hosting:** Ensure your API is accessible from n8n (public IP or proper networking).
- **Telegram/n8n:** n8n workflows are not included in this repo, but screenshots and integration instructions are provided.
