import logging
import datetime
import re
from typing import Set

logger = logging.getLogger(__name__)

ENGLISH_STOPWORDS: Set[str] = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren',
    'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
    'can', 'could', 'did', 'didn', 'do', 'does', 'doesn', 'doing', 'don', 'down', 'during', 'each',
    'few', 'for', 'from', 'further', 'had', 'hadn', 'has', 'hasn', 'have', 'haven', 'having', 'he',
    'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is',
    'isn', 'it', 'its', 'itself', 'just', 'me', 'mightn', 'more', 'most', 'mustn', 'my', 'myself',
    'needn', 'no', 'nor', 'not', 'now', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our',
    'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan', 'she', 'should', 'shouldn', 'so',
    'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there',
    'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was',
    'wasn', 'we', 'were', 'weren', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why',
    'will', 'with', 'won', 'would', 'wouldn', 'you', 'your', 'yours', 'yourself', 'yourselves', 'need'
}

ARABIC_STOPWORDS: Set[str] = {
    'ما', 'هي', 'هى', 'هل', 'كيف'
}

def parse_iso_datetime(date_str: str) -> datetime.datetime:
    """Parses an ISO format datetime string into a UTC-aware datetime object."""
    try:
        clean_str = date_str.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except ValueError as e:
        logger.error(f"Failed to parse datetime '{date_str}': {e}", exc_info=True)
        try:
            dt = datetime.datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
            return dt.replace(tzinfo=datetime.timezone.utc)
        except ValueError as e2:
            logger.error(f"Fallback parsing failed for '{date_str}': {e2}", exc_info=True)
            raise e2
