"""One frozen tokenizer for indexing, queries and lexical evidence coverage."""
from functools import lru_cache
from importlib.metadata import version
from pathlib import Path
import hashlib
import logging
import re
import jieba
from .documents import STANDARD, standards

RESOURCES = Path(__file__).with_name('resources')
ALGORITHM = 'jieba-precise-hmm-false-v1'

@lru_cache(maxsize=1)
def segmenter():
    jieba.setLogLevel(logging.WARNING)
    tokenizer = jieba.Tokenizer()
    tokenizer.load_userdict(str(RESOURCES/'domain_words.txt'))
    return tokenizer

@lru_cache(maxsize=1)
def stopwords():
    return frozenset((RESOURCES/'stopwords.txt').read_text(encoding='utf-8').split())

def preprocessing_identity():
    h=hashlib.sha256()
    for name in ['domain_words.txt','stopwords.txt']:
        h.update(name.encode());h.update((RESOURCES/name).read_bytes())
    return f'{ALGORITHM}|jieba={version("jieba")}|resources={h.hexdigest()}'

def _ordinary_tokens(text):
    for part in re.findall(r'[\u4e00-\u9fff]+|[a-z]+(?:[/-][a-z]+)*|\d+(?:\.\d+)?',text.lower()):
        if re.fullmatch(r'[\u4e00-\u9fff]+',part):
            yield from (t for t in segmenter().cut(part,cut_all=False,HMM=False) if t.strip())
        else:yield part

def tokens(text):
    result=[];cursor=0
    for match in STANDARD.finditer(text):
        result.extend(_ordinary_tokens(text[cursor:match.start()]))
        identifier,year=standards(match.group())[0]
        result.append(identifier.lower())
        if year:result.append(year)
        cursor=match.end()
    result.extend(_ordinary_tokens(text[cursor:]))
    return result

def content_terms(query):
    return set(tokens(STANDARD.sub(' ',query)))-stopwords()

def lexical_coverage(query,passage):
    terms=content_terms(query)
    return len(terms.intersection(tokens(passage)))/len(terms) if terms else 0.
