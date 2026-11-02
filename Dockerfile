FROM python:3.12-slim

WORKDIR /opt/business-mindset

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY web ./web
COPY features/business-idea-from-news/FeatureArtifacts/ ./features/business-idea-from-news/FeatureArtifacts/

CMD ["python", "-m", "app.main"]
