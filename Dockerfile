FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the cross-encoder reranker model so cold starts don't fetch it
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

COPY . .

# Persistent storage mount point for ChromaDB
RUN mkdir -p /data/chroma_store

EXPOSE 8501

# Copy Streamlit config (sets headless, disables noisy file watcher, error-only logging)
RUN mkdir -p /root/.streamlit
COPY .streamlit/config.toml /root/.streamlit/config.toml

CMD sh -c "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"
