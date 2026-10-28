FROM python:3.12-slim

WORKDIR /opt/business-mindset

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY features/business-idea-from-news/FeatureArtifacts/business-idea-from-news.smoke.md ./features/business-idea-from-news/FeatureArtifacts/business-idea-from-news.smoke.md

CMD ["python", "-m", "app.main"]
