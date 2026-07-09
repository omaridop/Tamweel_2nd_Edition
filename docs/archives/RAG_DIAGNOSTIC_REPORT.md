# RAG Diagnostic Report

## 1. Executive Summary
The Tamweel RAG pipeline is currently experiencing critical failures in factual grounding and quantitative data retrieval (the "Qualitative Hallucination / Quantitative Omission" syndrome). While the system successfully retrieves broad themes, it consistently drops hard numerical targets from financial documents and fails to accurately process tabular user data (e.g., transaction histories). 

Our read-only diagnostic audit of the backend codebase has pinpointed the root causes:
1. **LLM-as-a-Chunker Strategy:** Relying on an LLM to generate synthetic Q&A from raw PDFs strips dense tabular data and specific numerical targets.
2. **Data Fetcher Omissions:** The transaction retrieval query explicitly drops the transaction `type` (Income vs. Expense), leading the LLM to improperly sum instead of aggregate.
3. **Broken Recency Weighting:** The retrieval logic attempts to apply a recency score using missing metadata (`doc_date`), which silently corrupts the retrieval ranking.

## 2. Root Cause Analysis (The "Why")

### Why Hard Numerical Targets are Dropped
The ingestion pipeline (`backend/app/knowledge_ingester.py` and `backend/app/pipeline/doc_to_qa.py`) does not use standard structural chunking (e.g., semantic or markdown splitting). Instead, it uses an LLM to read chunks of PDF pages and generate "exhaustive bilingual Q&A". 
- **Tabular Data Destruction:** PyMuPDF raw text extraction (`_pages_text`) destroys table structures. When passed to the LLM for Q&A generation, the LLM hallucinates or summarizes qualitative themes, completely missing the hard numerical targets. 
- **Zero-Shot Loss:** Despite prompt instructions to "copy exact numbers," LLMs natively summarize and lose dense metrics (like "75% MSME accounts") when processing unstructured PDF text chunks.

### Why User Transaction Data Fails (Summing vs. Averaging)
In `backend/app/services/data_fetcher.py`, the SQL query explicitly omits the `type` column:
```python
tx_query = supabase.table("transactions").select("amount, category, description, created_at")
```
Because the `type` (Expense vs. Income) is missing, the LLM receives a flat array of amounts. It cannot differentiate between money entering or leaving the account. Additionally, the minified JSON injection in `context_assembler.py` provides dates (`created_at[:10]`) but lacks strict temporal instruction in the `system_prompt`, causing the LLM to naively sum all amounts rather than average them by month.

### Why Retrieval is Weak
In `backend/app/main.py`, the code applies a recency penalty:
```python
doc_date = doc['metadata'].get('doc_date') if doc.get('metadata') else None
rec = recency_score(doc_date, settings.RECENCY_HALFLIFE_DAYS)
```
However, `backend/app/knowledge_ingester.py` **never injects `doc_date` into the metadata dictionary.** This means `doc_date` is always `None`, causing the `recency_score` to return a default weight that distorts the RRF (Reciprocal Rank Fusion) similarity scores from `hybrid_search_policy_chunks`.

## 3. Component Breakdown

| Component | Grade | Diagnosis |
| :--- | :--- | :--- |
| **Parser & Splitter** | **D-** | The LLM Q&A generation approach is actively destructive to tables and numerical data. PyMuPDF raw text extraction is insufficient for structured financial documents. |
| **Embedding Model** | **B+** | Gemini Embedding 2 via OpenRouter is solid. However, `embed.py` uses aggressive character truncation (`[:limit]`) which may prematurely truncate large Q&A blocks. |
| **Vector Search** | **A-** | Excellent use of Hybrid Search (BM25 + Dense Vectors) with Reciprocal Rank Fusion (RRF) in Supabase Postgres (`hybrid_search_schema.sql`). |
| **Context Injection** | **C** | Minified JSON `<FP>` injection is efficient for tokens, but `data_fetcher.py` drops critical SQL columns (e.g., `type`), and the LLM prompt lacks strict tabular/temporal reasoning constraints. |

## 4. The Prescription (Action Plan)

To fix the pipeline's accuracy, I recommend executing the following prioritized action plan:

### Phase 1: Fix Transaction Data (Immediate Win)
1. **Update `data_fetcher.py`:** Modify the Supabase `.select()` clause to include the `type` column so the LLM knows if a transaction is an Income or Expense.
2. **Update `context_assembler.py`:** Add strict temporal reasoning instructions to the system prompt (e.g., "To calculate monthly averages, group transactions by the YYYY-MM prefix of the date field").

### Phase 2: Fix RAG Retrieval Logic
1. **Fix Recency Weighting in `main.py`:** Either remove the `doc_date` recency penalty or update `knowledge_ingester.py` to correctly extract and inject the document date into the vector metadata payload.

### Phase 3: Replace the Chunker (Strategic Fix)
1. **Adopt Markdown Parsing:** Replace PyMuPDF raw text extraction with a robust structured parser (e.g., LlamaParse or Unstructured) to retain table structures in Markdown format.
2. **Implement Semantic Chunking:** Ditch the pure "LLM Q&A generation" as the primary ingestion method. Instead, use MarkdownHeaderTextSplitter or Semantic Chunking to preserve context and hard numbers. 
3. *(Optional)* **Parent-Document Retrieval:** Store the full Markdown table in the database and embed smaller sub-chunks. When a sub-chunk matches, retrieve the parent table to ensure the LLM has all numerical targets.
