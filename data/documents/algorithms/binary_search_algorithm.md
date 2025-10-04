# Binary Search Algorithm

## Overview

Binary search is a search algorithm that finds the position of a target value within a sorted array. Binary search compares the target value to the middle element of the array. If they are not equal, the half in which the target cannot lie is eliminated and the search continues on the remaining half, again taking the middle element to compare to the target value, and repeating this until the target value is found.

## How Binary Search Works

Binary search works by repeatedly dividing the search interval in half. If the value of the search key is less than the item in the middle of the interval, narrow the interval to the lower half. Otherwise, narrow it to the upper half. Repeatedly check until the value is found or the interval is empty.

## Algorithm Steps

1. Compare the target value with the middle element of the array
2. If the target value matches the middle element, return the index
3. If the target value is less than the middle element, search the left half
4. If the target value is greater than the middle element, search the right half
5. Repeat the process until the target is found or the search space is exhausted

## Time Complexity

The time complexity of binary search is **O(log n)**, where n is the number of elements in the array. This is because with each comparison, the search space is reduced by half.

## Space Complexity

The space complexity of binary search is **O(1)** for the iterative implementation and **O(log n)** for the recursive implementation due to the call stack.

## Implementation

### Iterative Implementation

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # Target not found
```

### Recursive Implementation

```python
def binary_search_recursive(arr, target, left, right):
    if left > right:
        return -1  # Target not found
    
    mid = (left + right) // 2
    
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)
```

## Binary Search Variations

1. **First Occurrence** - Find the first occurrence of a target value in a sorted array with duplicates
2. **Last Occurrence** - Find the last occurrence of a target value in a sorted array with duplicates
3. **Count Occurrences** - Count the number of occurrences of a target value in a sorted array
4. **Search Insert Position** - Find the position where a target value should be inserted to maintain sorted order
5. **Search in Rotated Array** - Search for a target value in a rotated sorted array

## Applications

1. **Searching in Databases** - Binary search is used in database systems to quickly locate records
2. **Computer Graphics** - Used in computer graphics for efficient spatial data structures
3. **Numerical Analysis** - Used in numerical analysis for finding roots of equations
4. **Game Development** - Used in game development for efficient collision detection
5. **Machine Learning** - Used in machine learning algorithms for efficient data processing

## Advantages

1. **Efficient Time Complexity** - O(log n) time complexity, making it very efficient for large datasets
2. **Simple Implementation** - The algorithm is relatively simple to understand and implement
3. **Memory Efficient** - The iterative version uses constant space
4. **Predictable Performance** - The performance is predictable and consistent

## Disadvantages

1. **Requires Sorted Array** - The array must be sorted for binary search to work
2. **Not Suitable for Linked Lists** - Binary search is not efficient for linked lists due to the inability to access elements by index
3. **Static Data** - Binary search is not suitable for frequently changing data
4. **Memory Access Pattern** - Binary search may not be cache-friendly due to its memory access pattern

## Binary Search vs Linear Search

| Feature | Linear Search | Binary Search |
|---------|---------------|---------------|
| Time Complexity | O(n) | O(log n) |
| Array Requirement | Works on unsorted arrays | Requires sorted array |
| Implementation | Simple | More complex |
| Access Pattern | Sequential | Random |

## When to Use Binary Search

**Use binary search when:**
- The data is sorted
- You need to search frequently
- The dataset is large
- You need predictable performance

**Don't use binary search when:**
- The data is not sorted
- The data changes frequently
- The dataset is small
- You're working with linked lists

## Multi-Language Examples

### Java
```java
public static int binarySearch(int[] arr, int target) {
    int left = 0, right = arr.length - 1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    
    return -1;
}
```

### C++
```cpp
int binarySearch(int arr[], int size, int target) {
    int left = 0, right = size - 1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    
    return -1;
}
```

### JavaScript
```javascript
function binarySearch(arr, target) {
    let left = 0, right = arr.length - 1;
    
    while (left <= right) {
        let mid = Math.floor((left + right) / 2);
        
        if (arr[mid] === target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    
    return -1;
}
```

## Common Mistakes

1. **Integer Overflow** - Using `(left + right) / 2` can cause integer overflow. Use `left + (right - left) / 2` instead
2. **Off-by-One Errors** - Be careful with the boundary conditions and loop termination
3. **Incorrect Mid Calculation** - Make sure the mid calculation is correct for the given data type
4. **Forgetting to Update Boundaries** - Always update the left and right boundaries correctly
5. **Not Handling Edge Cases** - Handle cases where the array is empty or has one element

## Real-World Applications

1. **Dictionary Lookup** - Binary search is used in dictionary implementations for fast word lookup
2. **Phone Book Search** - Used in phone book applications for quick contact search
3. **Library Catalog** - Used in library systems for book search
4. **Stock Market Data** - Used in financial applications for price lookup
5. **Geographic Data** - Used in mapping applications for location search

## Performance Analysis

- **Best Case**: O(1) - Target is found at the middle
- **Average Case**: O(log n) - Target is found after log n comparisons
- **Worst Case**: O(log n) - Target is not found or found at the end

The algorithm is very efficient for large datasets and is widely used in computer science applications.
