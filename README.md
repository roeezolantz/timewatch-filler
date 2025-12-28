# TimeWatch Auto-Filler

Automate TimeWatch time reporting - available as a Slack Bot or standalone Docker container.

## Features

- Automatically fills incomplete timewatch entries
- Supports multiple users
- Can run as a Slack Bot or standalone script
- Docker support for Google Cloud Run deployment

---

## Quick Start

### Option 1: Run with Docker

```bash
# Build the image
docker build -t timewatch-filler .

# Run with single user
docker run \
  -e TIMEWATCH_COMPANY=11447 \
  -e TIMEWATCH_USERNAME=5 \
  -e TIMEWATCH_PASSWORD=your_password \
  timewatch-filler

# Run with multiple users
docker run \
  -e 'TIMEWATCH_USERS=[{"company":"11447","username":"5","password":"pass1"},{"company":"11447","username":"6","password":"pass2"}]' \
  timewatch-filler
```

### Option 2: Run locally with Python

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables and run
TIMEWATCH_COMPANY=11447 TIMEWATCH_USERNAME=5 TIMEWATCH_PASSWORD=your_password python main_time.py
```

---

## Configuration

### Environment Variables

**Single user (legacy format):**
```bash
TIMEWATCH_COMPANY=11447
TIMEWATCH_USERNAME=5
TIMEWATCH_PASSWORD=your_password
```

**Multiple users (JSON array):**
```bash
TIMEWATCH_USERS='[
  {"company": "11447", "username": "5", "password": "pass1"},
  {"company": "11447", "username": "6", "password": "pass2"}
]'
```

### Using a `.env` file

Create a `.env` file in the project root:
```
TIMEWATCH_COMPANY=11447
TIMEWATCH_USERNAME=5
TIMEWATCH_PASSWORD=your_password
```

Then run:
```bash
python main_time.py
```

---

## Deploy to Google Cloud Run

### 1. Build and push to Google Container Registry

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/timewatch-filler
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy timewatch-filler \
  --image gcr.io/YOUR_PROJECT_ID/timewatch-filler \
  --platform managed \
  --region us-central1 \
  --no-allow-unauthenticated \
  --set-env-vars 'TIMEWATCH_USERS=[{"company":"11447","username":"5","password":"your_password"}]'
```

### 3. Set up Cloud Scheduler for periodic runs

```bash
# Create a service account
gcloud iam service-accounts create timewatch-scheduler

# Grant permission to invoke Cloud Run
gcloud run services add-iam-policy-binding timewatch-filler \
  --member=serviceAccount:timewatch-scheduler@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.invoker

# Create scheduler job (runs daily at 9 AM)
gcloud scheduler jobs create http timewatch-daily \
  --schedule="0 9 * * *" \
  --uri="YOUR_CLOUD_RUN_URL" \
  --oidc-service-account-email=timewatch-scheduler@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

---

## Deploy to GitHub Container Registry

```bash
# Login to ghcr.io
echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Build and tag
docker build -t ghcr.io/YOUR_GITHUB_USERNAME/timewatch-filler:latest .

# Push
docker push ghcr.io/YOUR_GITHUB_USERNAME/timewatch-filler:latest
```

---

## Slack Bot Setup

If you wish to use the Slack Bot integration:

1. Change the company code in `time_bolt.py`:
   ```python
   tw_return = main_time.some_func('YOUR_COMPANY_CODE', username, password)
   ```

2. Follow the Slack Bolt setup guide:
   https://slack.dev/bolt-python/tutorial/getting-started

---

## Credits

This project is forked from [timewatch_slack_filler](https://github.com/tobenary/timewatch_slack_filler) by [**tobenary**](https://github.com/tobenary).

---

## License

MIT
