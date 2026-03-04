# 📚 DSA 30-Day Tutorial - Day 25

## Day 25: Tries (Prefix Trees)

### 🎯 Learning Objectives
By the end of this day, you will:
- Implement Trie data structure
- Use Tries for prefix matching
- Build autocomplete system

---

### 📖 What is a Trie?

Tree structure for storing strings, where each node represents a character.

```
Words: ["cat", "car", "card", "dog"]

         root
        /    \
       c      d
       |      |
       a      o
      / \     |
     t   r    g*
     *   |
         d*

* = end of word
```

---

### 📖 Trie Implementation

```javascript
class TrieNode {
    constructor() {
        this.children = {};
        this.isEndOfWord = false;
    }
}

class Trie {
    constructor() {
        this.root = new TrieNode();
    }
    
    insert(word) {
        let node = this.root;
        for (let char of word) {
            if (!node.children[char]) {
                node.children[char] = new TrieNode();
            }
            node = node.children[char];
        }
        node.isEndOfWord = true;
    }
    
    search(word) {
        let node = this._findNode(word);
        return node !== null && node.isEndOfWord;
    }
    
    startsWith(prefix) {
        return this._findNode(prefix) !== null;
    }
    
    _findNode(str) {
        let node = this.root;
        for (let char of str) {
            if (!node.children[char]) {
                return null;
            }
            node = node.children[char];
        }
        return node;
    }
}
```

---

### 📖 Word Search II (Trie + Backtracking)

```javascript
function findWords(board, words) {
    const trie = new Trie();
    for (let word of words) {
        trie.insert(word);
    }
    
    const result = new Set();
    const rows = board.length, cols = board[0].length;
    
    function dfs(r, c, node, path) {
        if (r < 0 || r >= rows || c < 0 || c >= cols) return;
        
        const char = board[r][c];
        if (char === '#' || !node.children[char]) return;
        
        path += char;
        node = node.children[char];
        
        if (node.isEndOfWord) {
            result.add(path);
        }
        
        board[r][c] = '#';  // Mark visited
        
        dfs(r + 1, c, node, path);
        dfs(r - 1, c, node, path);
        dfs(r, c + 1, node, path);
        dfs(r, c - 1, node, path);
        
        board[r][c] = char;  // Restore
    }
    
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            dfs(r, c, trie.root, '');
        }
    }
    
    return [...result];
}
```

---

### 📖 Autocomplete System

```javascript
class AutocompleteSystem {
    constructor(sentences, times) {
        this.trie = new Trie();
        this.frequency = new Map();
        this.currentInput = '';
        
        for (let i = 0; i < sentences.length; i++) {
            this.trie.insert(sentences[i]);
            this.frequency.set(sentences[i], times[i]);
        }
    }
    
    input(c) {
        if (c === '#') {
            // End of sentence - store it
            this.trie.insert(this.currentInput);
            this.frequency.set(
                this.currentInput,
                (this.frequency.get(this.currentInput) || 0) + 1
            );
            this.currentInput = '';
            return [];
        }
        
        this.currentInput += c;
        return this._getSuggestions(this.currentInput);
    }
    
    _getSuggestions(prefix) {
        const matches = [];
        const node = this.trie._findNode(prefix);
        
        if (!node) return [];
        
        this._collectWords(node, prefix, matches);
        
        // Sort by frequency (desc), then alphabetically
        matches.sort((a, b) => {
            const freqDiff = this.frequency.get(b) - this.frequency.get(a);
            if (freqDiff !== 0) return freqDiff;
            return a.localeCompare(b);
        });
        
        return matches.slice(0, 3);
    }
    
    _collectWords(node, prefix, matches) {
        if (node.isEndOfWord) {
            matches.push(prefix);
        }
        for (let char in node.children) {
            this._collectWords(node.children[char], prefix + char, matches);
        }
    }
}
```

---

### ✅ Day 25 Checklist
- [ ] Implement Trie with insert, search, startsWith
- [ ] Complete: Implement Trie, Word Search II
- [ ] Practice: Design Add and Search Words
- [ ] Build autocomplete system

---

