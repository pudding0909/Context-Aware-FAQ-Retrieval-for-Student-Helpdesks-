# CampusConnect — Context-Aware FAQ Student Helpdesk

A Streamlit helpdesk that follows the supplied four-level architecture and uses **Sentence Transformers `all-MiniLM-L6-v2`** to create 384-dimensional FAQ and query embeddings, followed by cosine-similarity ranking. The acceptance threshold is set to **0.42** to match the architecture diagram; calibrate it on validated test data before making accuracy claims.

## Included data
- `data/faq_dataset_1.csv`: 500 FAQ records
- `data/faq_dataset_2.csv`: 500 FAQ records
- `data/faq_dataset_3.csv`: 500 FAQ records
- `data/test_queries.csv`: 120 labelled evaluation queries

The FAQ records are demonstration data based on common student-helpdesk topics and generated variations. They are not independently verified college policies; replace or validate answers with approved institutional information before deployment.

## Model and index
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Embedding size: 384 dimensions
- Embeddings: L2-normalized
- Retrieval: cosine similarity, Top-k ranking, threshold 0.42, fallback when below threshold
- On first run, the model is downloaded from Hugging Face and FAQ embeddings are generated. The embeddings and FAQ metadata are saved under `saved_index/` for reuse. If the dataset questions change, the index is rebuilt.

## Input methods
1. Type one or many questions, one per line.
2. Upload TXT or CSV question lists (CSV column: `question`, `query`, or `questions`).
3. Upload text-based PDF or DOCX documents containing questions.
4. Upload PNG/JPG/JPEG images; Tesseract OCR is required and must be installed separately.
5. Record audio in the Streamlit UI or upload WAV audio; online speech recognition requires internet.

## Install and run (Windows)
```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```
Open the local URL printed in the terminal, usually `http://localhost:8501`.

## Evaluate
```bash
python evaluate.py
```
Reports Top-1 accuracy, Top-3 accuracy and Mean Reciprocal Rank (MRR) using the included sample labelled queries. Results are demonstration measurements, not a guarantee of production accuracy. Validate the labels and tune the threshold on a held-out validation set before reporting final results.

## Notes
- Python 3.10 or 3.11 is recommended for a smoother setup with ML dependencies.
- The first model load needs an internet connection; later runs may use the cached model.
- Scanned PDFs may need OCR separately. Voice/audio compatibility depends on your system and speech-recognition setup.
