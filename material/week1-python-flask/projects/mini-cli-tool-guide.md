# Week 1 Mini Project: Build a CLI Tool in Python

## Project: Document Processing CLI

Build a command-line tool that processes text documents — this directly prepares you for RAG pipeline work in Week 2.

### Features:
1. Read text/JSON files from a directory
2. Clean and normalize text
3. Split into chunks with overlap
4. Generate metadata (word count, chunk count, etc.)
5. Export as JSON (ready for embedding)

---

## Implementation

```python
#!/usr/bin/env python3
"""
Document Processing CLI - Prepares documents for AI embedding pipeline.

Usage:
    python doc_processor.py process --input ./docs --output ./processed --chunk-size 500
    python doc_processor.py stats --input ./docs
    python doc_processor.py search --input ./processed --query "machine learning"
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
from datetime import datetime


@dataclass
class Chunk:
    """A chunk of text from a document."""
    id: str
    text: str
    document_id: str
    chunk_index: int
    word_count: int
    char_count: int
    metadata: dict = field(default_factory=dict)


@dataclass
class ProcessedDocument:
    """A processed document ready for embedding."""
    id: str
    source_file: str
    title: str
    total_chunks: int
    total_words: int
    total_chars: int
    chunks: list[Chunk] = field(default_factory=list)
    processed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class TextCleaner:
    """Clean and normalize text."""
    
    @staticmethod
    def clean(text: str) -> str:
        """Clean text for processing."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s.,!?;:\-\'\"()\n]', '', text)
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        return text.strip()
    
    @staticmethod
    def normalize(text: str) -> str:
        """Normalize text for better embedding quality."""
        text = TextCleaner.clean(text)
        # Collapse multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text


class TextChunker:
    """Split text into overlapping chunks."""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, text: str) -> list[str]:
        """Split text into chunks with overlap."""
        if not text:
            return []
        
        chunks = []
        words = text.split()
        
        if len(words) <= self.chunk_size:
            return [text]
        
        # Split by words to avoid cutting mid-word
        chunk_words = self.chunk_size
        overlap_words = self.overlap
        
        start = 0
        while start < len(words):
            end = start + chunk_words
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            start += chunk_words - overlap_words
        
        return chunks
    
    def chunk_by_sentence(self, text: str) -> list[str]:
        """Split by sentences, respecting chunk size."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence.split())
            if current_size + sentence_size > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                # Keep last sentence for overlap
                current_chunk = current_chunk[-1:] if self.overlap > 0 else []
                current_size = len(' '.join(current_chunk).split())
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks


class DocumentProcessor:
    """Main document processing engine."""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.json', '.csv'}
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.cleaner = TextCleaner()
        self.chunker = TextChunker(chunk_size, overlap)
    
    def read_file(self, filepath: Path) -> str:
        """Read content from a file."""
        try:
            if filepath.suffix == '.json':
                with open(filepath) as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data.get('content', json.dumps(data))
                    return json.dumps(data)
            else:
                return filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return ""
    
    def process_file(self, filepath: Path) -> Optional[ProcessedDocument]:
        """Process a single file into chunks."""
        if filepath.suffix not in self.SUPPORTED_EXTENSIONS:
            return None
        
        content = self.read_file(filepath)
        if not content:
            return None
        
        # Clean text
        cleaned = self.cleaner.normalize(content)
        
        # Create chunks
        text_chunks = self.chunker.chunk_by_sentence(cleaned)
        
        # Build document ID
        doc_id = filepath.stem.replace(' ', '_').lower()
        
        # Create chunk objects
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            words = chunk_text.split()
            chunk = Chunk(
                id=f"{doc_id}_chunk_{i}",
                text=chunk_text,
                document_id=doc_id,
                chunk_index=i,
                word_count=len(words),
                char_count=len(chunk_text),
                metadata={
                    "source_file": str(filepath.name),
                    "position": f"{i+1}/{len(text_chunks)}"
                }
            )
            chunks.append(chunk)
        
        total_words = sum(c.word_count for c in chunks)
        
        return ProcessedDocument(
            id=doc_id,
            source_file=str(filepath),
            title=filepath.stem.replace('_', ' ').title(),
            total_chunks=len(chunks),
            total_words=total_words,
            total_chars=len(cleaned),
            chunks=chunks,
        )
    
    def process_directory(self, input_dir: Path) -> list[ProcessedDocument]:
        """Process all supported files in a directory."""
        documents = []
        
        for filepath in sorted(input_dir.rglob('*')):
            if filepath.is_file() and filepath.suffix in self.SUPPORTED_EXTENSIONS:
                print(f"Processing: {filepath.name}...")
                doc = self.process_file(filepath)
                if doc:
                    documents.append(doc)
                    print(f"  → {doc.total_chunks} chunks, {doc.total_words} words")
        
        return documents
    
    def export_json(self, documents: list[ProcessedDocument], output_dir: Path):
        """Export processed documents as JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for doc in documents:
            output_file = output_dir / f"{doc.id}.json"
            with open(output_file, 'w') as f:
                json.dump(asdict(doc), f, indent=2)
            print(f"Exported: {output_file}")
        
        # Also create a manifest
        manifest = {
            "total_documents": len(documents),
            "total_chunks": sum(d.total_chunks for d in documents),
            "total_words": sum(d.total_words for d in documents),
            "documents": [
                {
                    "id": d.id,
                    "title": d.title,
                    "chunks": d.total_chunks,
                    "words": d.total_words,
                }
                for d in documents
            ],
            "processed_at": datetime.utcnow().isoformat(),
        }
        
        manifest_file = output_dir / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"\nManifest: {manifest_file}")


def simple_search(processed_dir: Path, query: str) -> list[dict]:
    """Simple keyword search across processed documents."""
    results = []
    query_lower = query.lower()
    
    for filepath in processed_dir.glob('*.json'):
        if filepath.name == 'manifest.json':
            continue
        
        with open(filepath) as f:
            doc = json.load(f)
        
        for chunk in doc.get('chunks', []):
            if query_lower in chunk['text'].lower():
                results.append({
                    'document': doc['title'],
                    'chunk_id': chunk['id'],
                    'text': chunk['text'][:200] + '...',
                    'score': chunk['text'].lower().count(query_lower),
                })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def main():
    parser = argparse.ArgumentParser(description='Document Processing CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process documents')
    process_parser.add_argument('--input', '-i', required=True, help='Input directory')
    process_parser.add_argument('--output', '-o', required=True, help='Output directory')
    process_parser.add_argument('--chunk-size', type=int, default=500, help='Chunk size in words')
    process_parser.add_argument('--overlap', type=int, default=50, help='Overlap in words')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show document stats')
    stats_parser.add_argument('--input', '-i', required=True, help='Input directory')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search processed documents')
    search_parser.add_argument('--input', '-i', required=True, help='Processed directory')
    search_parser.add_argument('--query', '-q', required=True, help='Search query')
    
    args = parser.parse_args()
    
    if args.command == 'process':
        processor = DocumentProcessor(args.chunk_size, args.overlap)
        docs = processor.process_directory(Path(args.input))
        processor.export_json(docs, Path(args.output))
        print(f"\n✅ Processed {len(docs)} documents")
    
    elif args.command == 'stats':
        processor = DocumentProcessor()
        for filepath in Path(args.input).rglob('*'):
            if filepath.is_file():
                content = filepath.read_text(encoding='utf-8', errors='ignore')
                words = len(content.split())
                print(f"{filepath.name}: {words} words, {len(content)} chars")
    
    elif args.command == 'search':
        results = simple_search(Path(args.input), args.query)
        if results:
            for r in results[:5]:
                print(f"\n📄 {r['document']} (score: {r['score']})")
                print(f"   {r['text']}")
        else:
            print("No results found.")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
```

---

## How to Test

```bash
# Create sample documents
mkdir -p sample_docs
echo "Machine learning is a subset of artificial intelligence. It enables systems to learn from data. Deep learning is a further subset that uses neural networks." > sample_docs/ml_basics.txt
echo "RAG stands for Retrieval Augmented Generation. It combines search with language models to provide accurate answers." > sample_docs/rag_intro.txt

# Process documents
python doc_processor.py process --input ./sample_docs --output ./processed --chunk-size 50

# View stats
python doc_processor.py stats --input ./sample_docs

# Search
python doc_processor.py search --input ./processed --query "neural networks"
```

---

## What This Teaches You
1. **argparse** — CLI argument parsing (used in AI tools)
2. **dataclasses** — structured data (used everywhere)
3. **pathlib** — modern file handling
4. **Text chunking** — CORE RAG skill
5. **JSON export** — data pipeline output
6. **Clean architecture** — separate concerns
7. **Type hints** — production Python
