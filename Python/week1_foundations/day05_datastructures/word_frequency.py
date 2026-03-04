#!/usr/bin/env python3
"""
Word Frequency Counter

Features:
- Count word occurrences in text
- Filter stop words
- Show top N most common words
- Support for file input
"""

import re
from collections import Counter
from typing import Dict, List, Tuple


# Common English stop words
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "over", "after",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "must", "shall", "can", "that", "this", "these", "those", "i", "you",
    "he", "she", "it", "we", "they", "what", "which", "who", "whom",
    "me", "him", "her", "us", "them", "my", "your", "his", "its", "our", "their",
    "as", "if", "when", "than", "because", "while", "where", "so", "not", "no"
}


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters, keep only alphanumeric and spaces
    text = re.sub(r"[^a-z0-9\s]", "", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    """Split text into words"""
    return clean_text(text).split()


def count_words(text: str, remove_stop_words: bool = True) -> Counter:
    """
    Count word frequencies in text.
    
    Args:
        text: Input text to analyze
        remove_stop_words: Whether to filter out common stop words
        
    Returns:
        Counter object with word frequencies
    """
    words = tokenize(text)
    
    if remove_stop_words:
        words = [w for w in words if w not in STOP_WORDS]
    
    return Counter(words)


def get_top_words(counter: Counter, n: int = 10) -> List[Tuple[str, int]]:
    """Get top N most common words"""
    return counter.most_common(n)


def print_frequency_chart(top_words: List[Tuple[str, int]], max_bar_length: int = 40):
    """Print a horizontal bar chart of word frequencies"""
    if not top_words:
        print("No words to display")
        return
    
    max_count = top_words[0][1]
    max_word_len = max(len(word) for word, _ in top_words)
    
    print("\n" + "=" * 60)
    print("WORD FREQUENCY CHART")
    print("=" * 60)
    
    for word, count in top_words:
        bar_length = int((count / max_count) * max_bar_length)
        bar = "█" * bar_length
        print(f"{word:>{max_word_len}} | {bar} {count}")


def analyze_text(text: str, top_n: int = 10, show_stats: bool = True):
    """
    Comprehensive text analysis.
    
    Args:
        text: Text to analyze
        top_n: Number of top words to show
        show_stats: Whether to show detailed statistics
    """
    # Basic stats
    words_raw = tokenize(text)
    words_filtered = [w for w in words_raw if w not in STOP_WORDS]
    
    counter = Counter(words_filtered)
    
    if show_stats:
        print("\n" + "=" * 60)
        print("TEXT STATISTICS")
        print("=" * 60)
        print(f"Total words: {len(words_raw)}")
        print(f"Unique words (all): {len(set(words_raw))}")
        print(f"Words after filtering: {len(words_filtered)}")
        print(f"Unique words (filtered): {len(counter)}")
        print(f"Stop words removed: {len(words_raw) - len(words_filtered)}")
    
    top_words = get_top_words(counter, top_n)
    print_frequency_chart(top_words)
    
    return counter


def read_file(filepath: str) -> str:
    """Read text from file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return ""
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""


# Sample text for testing
SAMPLE_TEXT = """
Python is an amazing programming language. Python is easy to learn and 
Python is very powerful. Many developers love Python because of its 
simplicity and readability. The Python community is very supportive.

Python can be used for web development, data science, machine learning,
automation, and much more. Python has many libraries and frameworks that
make development faster and easier.

When you learn Python, you join millions of developers worldwide who use
Python every day. Python continues to grow in popularity and remains one
of the most loved programming languages.
"""


def main():
    print("=" * 60)
    print("WORD FREQUENCY COUNTER")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("1. Analyze sample text")
        print("2. Enter custom text")
        print("3. Read from file")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            analyze_text(SAMPLE_TEXT)
            
        elif choice == "2":
            print("\nEnter text (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            
            if lines:
                text = "\n".join(lines)
                analyze_text(text)
            else:
                print("No text entered")
                
        elif choice == "3":
            filepath = input("Enter file path: ").strip()
            text = read_file(filepath)
            if text:
                analyze_text(text)
                
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("Invalid option. Please choose 1-4.")


if __name__ == "__main__":
    main()
