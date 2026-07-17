import re
from datetime import datetime, timezone

import logging
from app.utils import ENGLISH_STOPWORDS as STOPWORDS, parse_iso_datetime

_CACHE_TTL_SECONDS = 24 * 3600  # 24 hours

logger = logging.getLogger(__name__)

def extract_keywords(question: str) -> list[str]:
    # Lowercase and split on non-alphanumeric
    words = re.split(r'\W+', question.lower())
    # Remove stopwords and words <= 3 chars
    keywords = [w for w in words if len(w) > 3 and w not in STOPWORDS]
    return sorted(list(set(keywords)))

def keywords_overlap(stored_keywords: list[str], query_keywords: list[str]) -> bool:
    if not query_keywords:
        return True # If there are no meaningful keywords in query, we rely on semantic similarity
    
    stored_set = set(stored_keywords)
    query_set = set(query_keywords)
    
    overlap = len(stored_set.intersection(query_set))
    return (overlap / len(query_set)) >= 0.60

async def lookup_cache(supabase, query_embedding: list[float], query_keywords: list[str]) -> str | None:
    try:
        # Call the RPC with 0.98 similarity threshold
        response = supabase.rpc(
            'search_frequent_questions',
            {'query_embedding': query_embedding, 'similarity_threshold': 0.98, 'match_count': 1}
        ).execute()

        if response.data and len(response.data) > 0:
            match = response.data[0]
            
            # --- Check Expiration (24 hours) ---
            created_at_str = match.get('created_at')
            if created_at_str:
                try:
                    created_at = parse_iso_datetime(created_at_str)
                    age = datetime.now(timezone.utc) - created_at

                    if age.total_seconds() > _CACHE_TTL_SECONDS:
                        # Expired: Delete from DB and ignore
                        try:
                            supabase.table('frequent_questions').delete().eq('id', match['id']).execute()
                        except Exception as delete_err:
                            logger.error(f"Failed to delete expired cache: {delete_err}", exc_info=True)
                        return None
                except Exception as parse_err:
                    logger.error(f"Failed to parse cache date: {parse_err}", exc_info=True)

            stored_keywords = match.get('question_keywords', [])
            
            if keywords_overlap(stored_keywords, query_keywords):
                # Update hit_count and last_accessed_at asynchronously to not block
                row_id = match['id']
                try:
                    # Get current hit count
                    hit_resp = supabase.table('frequent_questions').select('hit_count').eq('id', row_id).execute()
                    current_hits = hit_resp.data[0]['hit_count'] if hit_resp.data else 0
                    
                    supabase.table('frequent_questions').update({
                        'hit_count': current_hits + 1,
                        'last_accessed_at': datetime.now(timezone.utc).isoformat()
                    }).eq('id', row_id).execute()
                except Exception as update_err:
                    logger.warning(f"Cache update error (ignored): {update_err}")
                
                return match.get('cached_answer')
    except Exception as e:
        logger.error(f"Cache lookup error: {e}", exc_info=True)
    
    return None

async def store_in_cache(supabase, question: str, embedding: list[float], answer: str) -> None:
    try:
        keywords = extract_keywords(question)
        data = {
            'question_text': question,
            'question_embedding': embedding,
            'question_keywords': keywords,
            'cached_answer': answer
        }
        supabase.table('frequent_questions').insert(data).execute()
        logger.info(f"Stored question in cache: {question[:50]}...")
    except Exception as e:
        logger.error(f"Cache store error (ignored): {e}", exc_info=True)
