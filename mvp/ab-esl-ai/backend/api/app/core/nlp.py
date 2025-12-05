"""Shared NLP utilities.

This module provides centralized access to NLP models and utilities
to avoid duplicate initialization code across services.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy-loaded spaCy model
_nlp = None


def get_nlp():
    """
    Get the shared spaCy English model.
    
    The model is lazily loaded on first access and cached for reuse.
    Will automatically download the model if not found.
    
    Returns:
        spacy.Language: The loaded spaCy model, or None if unavailable.
    """
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model 'en_core_web_sm' loaded successfully")
        except OSError:
            logger.warning("spaCy model not found, attempting to download...")
            try:
                import spacy.cli
                spacy.cli.download("en_core_web_sm")
                import spacy
                _nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model downloaded and loaded successfully")
            except Exception as e:
                logger.error(f"Failed to download spaCy model: {e}")
                return None
        except ImportError:
            logger.warning("spaCy not installed - NLP features unavailable")
            return None
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            return None
    return _nlp


def get_doc(text: str):
    """
    Process text with spaCy and return the Doc object.
    
    Args:
        text: The text to process.
        
    Returns:
        spacy.Doc or None: The processed document, or None if NLP unavailable.
    """
    nlp = get_nlp()
    if nlp is None:
        return None
    return nlp(text)


def extract_sentences(text: str):
    """
    Extract sentences from text.
    
    Args:
        text: The text to split into sentences.
        
    Returns:
        List of sentence strings, or [text] if NLP unavailable.
    """
    doc = get_doc(text)
    if doc is None:
        # Fallback to simple splitting
        return [s.strip() for s in text.split('.') if s.strip()]
    return [sent.text for sent in doc.sents]


def get_lemma(token_text: str) -> str:
    """
    Get the lemma (base form) of a word.
    
    Args:
        token_text: The word to lemmatize.
        
    Returns:
        The lemma, or the original word if NLP unavailable.
    """
    nlp = get_nlp()
    if nlp is None:
        return token_text.lower()
    doc = nlp(token_text)
    return doc[0].lemma_ if len(doc) > 0 else token_text.lower()
