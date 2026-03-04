# 📚 DSA 30-Day Tutorial - Day 23

## Day 23: Greedy Algorithms

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand greedy choice property
- Identify greedy vs DP problems
- Solve interval scheduling problems

---

### 📖 When to Use Greedy

Greedy works when:
1. **Greedy choice property:** Local optimal leads to global optimal
2. **Optimal substructure:** Optimal solution contains optimal solutions to subproblems

**Greedy fails when:** Local choice affects future options negatively (use DP instead).

---

### 📖 Activity Selection / Meeting Rooms

Maximum number of non-overlapping meetings.

```javascript
function maxMeetings(meetings) {
    // Sort by end time
    meetings.sort((a, b) => a[1] - b[1]);
    
    let count = 1;
    let lastEnd = meetings[0][1];
    
    for (let i = 1; i < meetings.length; i++) {
        if (meetings[i][0] >= lastEnd) {
            count++;
            lastEnd = meetings[i][1];
        }
    }
    
    return count;
}
```

**Why sort by end time?** Finishing early leaves more room for future meetings.

---

### 📖 Jump Game

```javascript
function canJump(nums) {
    let maxReach = 0;
    
    for (let i = 0; i < nums.length; i++) {
        if (i > maxReach) return false;  // Can't reach this position
        maxReach = Math.max(maxReach, i + nums[i]);
    }
    
    return maxReach >= nums.length - 1;
}
```

### Jump Game II (Minimum jumps)
```javascript
function jump(nums) {
    let jumps = 0;
    let currentEnd = 0;
    let farthest = 0;
    
    for (let i = 0; i < nums.length - 1; i++) {
        farthest = Math.max(farthest, i + nums[i]);
        
        if (i === currentEnd) {
            jumps++;
            currentEnd = farthest;
        }
    }
    
    return jumps;
}
```

---

### 📖 Gas Station

```javascript
function canCompleteCircuit(gas, cost) {
    let totalGas = 0, totalCost = 0;
    let tank = 0, start = 0;
    
    for (let i = 0; i < gas.length; i++) {
        totalGas += gas[i];
        totalCost += cost[i];
        tank += gas[i] - cost[i];
        
        if (tank < 0) {
            start = i + 1;  // Reset start
            tank = 0;
        }
    }
    
    return totalGas >= totalCost ? start : -1;
}
```

---

### 📖 Merge Intervals

```javascript
function merge(intervals) {
    intervals.sort((a, b) => a[0] - b[0]);
    const result = [intervals[0]];
    
    for (let i = 1; i < intervals.length; i++) {
        const last = result[result.length - 1];
        
        if (intervals[i][0] <= last[1]) {
            // Overlap - merge
            last[1] = Math.max(last[1], intervals[i][1]);
        } else {
            result.push(intervals[i]);
        }
    }
    
    return result;
}
```

---

### ✅ Day 23 Checklist
- [ ] Understand greedy choice property
- [ ] Complete: Jump Game, Gas Station
- [ ] Practice: Merge Intervals, Meeting Rooms II
- [ ] Compare greedy vs DP approaches

---

