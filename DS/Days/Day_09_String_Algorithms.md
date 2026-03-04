# 📚 DSA 30-Day Tutorial - Day 9

## Day 9: String Algorithms

### 🎯 Learning Objectives
By the end of this day, you will:
- Implement KMP pattern matching
- Understand Z-algorithm
- Know when to use which string algorithm

---

### 📖 Why String Algorithms Matter?

**Naive string search:** O(n × m)
```javascript
function naiveSearch(text, pattern) {
    for (let i = 0; i <= text.length - pattern.length; i++) {
        let match = true;
        for (let j = 0; j < pattern.length; j++) {
            if (text[i + j] !== pattern[j]) {
                match = false;
                break;
            }
        }
        if (match) return i;
    }
    return -1;
}
```

**KMP/Z-algorithm:** O(n + m)

---

### 📖 KMP Algorithm (Knuth-Morris-Pratt)

KMP avoids re-comparing characters by using a **failure function (LPS array)**.

#### What is LPS (Longest Proper Prefix Suffix)?

LPS[i] = length of longest proper prefix of pattern[0..i] that is also a suffix.

```
Pattern: "ABABC"

Index:   0   1   2   3   4
Char:    A   B   A   B   C
LPS:     0   0   1   2   0

Explanation:
LPS[0] = 0 (single char, no proper prefix)
LPS[1] = 0 ("AB" - no match)
LPS[2] = 1 ("ABA" - "A" is both prefix and suffix)
LPS[3] = 2 ("ABAB" - "AB" is both prefix and suffix)
LPS[4] = 0 ("ABABC" - no match)
```

#### Building LPS Array

```javascript
function buildLPS(pattern) {
    const lps = [0];       // LPS[0] is always 0
    let len = 0;           // Length of previous longest prefix suffix
    let i = 1;
    
    while (i < pattern.length) {
        if (pattern[i] === pattern[len]) {
            len++;
            lps.push(len);
            i++;
        } else if (len > 0) {
            // Try shorter prefix
            len = lps[len - 1];
        } else {
            lps.push(0);
            i++;
        }
    }
    
    return lps;
}
```

#### KMP Search

```javascript
function kmpSearch(text, pattern) {
    const lps = buildLPS(pattern);
    const results = [];
    
    let i = 0;  // Index for text
    let j = 0;  // Index for pattern
    
    while (i < text.length) {
        if (text[i] === pattern[j]) {
            i++;
            j++;
            
            if (j === pattern.length) {
                results.push(i - j);  // Found match!
                j = lps[j - 1];       // Continue searching
            }
        } else if (j > 0) {
            // Mismatch: use LPS to skip
            j = lps[j - 1];
        } else {
            i++;
        }
    }
    
    return results;
}
```

**Visual Walkthrough:**
```
Text:    "ABABDABABC"
Pattern: "ABABC"
LPS:     [0, 0, 1, 2, 0]

i=0, j=0: A=A ✓, i=1, j=1
i=1, j=1: B=B ✓, i=2, j=2
i=2, j=2: A=A ✓, i=3, j=3
i=3, j=3: B=B ✓, i=4, j=4
i=4, j=4: D≠C ✗
          j = lps[3] = 2 (skip to position 2)
          
i=4, j=2: D≠A ✗
          j = lps[1] = 0
          
i=4, j=0: D≠A ✗, j=0, so i++

i=5, j=0: A=A ✓, i=6, j=1
... continues until match at index 5
```

**Why it works:**
When mismatch at position j, LPS tells us the longest prefix that's also a suffix. We don't need to re-compare that part!

---

### 📖 Z-Algorithm

Z[i] = length of longest substring starting at i that matches a prefix of the string.

```
String: "aabxaab"

Index:   0   1   2   3   4   5   6
Char:    a   a   b   x   a   a   b
Z:       -   1   0   0   3   1   0

Z[4] = 3 because "aab" (starting at 4) matches prefix "aab"
```

```javascript
function zFunction(s) {
    const n = s.length;
    const z = new Array(n).fill(0);
    let l = 0, r = 0;  // [l, r] is the rightmost matched segment
    
    for (let i = 1; i < n; i++) {
        if (i < r) {
            // We're inside a known matching segment
            z[i] = Math.min(r - i, z[i - l]);
        }
        
        // Try to extend
        while (i + z[i] < n && s[z[i]] === s[i + z[i]]) {
            z[i]++;
        }
        
        // Update rightmost segment
        if (i + z[i] > r) {
            l = i;
            r = i + z[i];
        }
    }
    
    return z;
}

// Pattern matching using Z
function zSearch(text, pattern) {
    const combined = pattern + '$' + text;
    const z = zFunction(combined);
    const results = [];
    
    for (let i = pattern.length + 1; i < combined.length; i++) {
        if (z[i] === pattern.length) {
            results.push(i - pattern.length - 1);
        }
    }
    
    return results;
}
```

---

### 📖 When to Use Which Algorithm?

| Algorithm | Use Case | Time | Space |
|-----------|----------|------|-------|
| KMP | Single pattern search | O(n+m) | O(m) |
| Z-Algorithm | Pattern search, longest palindromic prefix | O(n+m) | O(n+m) |
| Rabin-Karp | Multiple pattern search, plagiarism detection | O(n+m) avg | O(1) |
| Trie | Dictionary matching, autocomplete | O(m) per query | O(alphabet × total chars) |

---

### ✅ Day 9 Checklist
- [ ] Understand LPS array construction
- [ ] Implement KMP search
- [ ] Understand Z-algorithm
- [ ] Practice: Implement strStr, Repeated Substring Pattern

---

