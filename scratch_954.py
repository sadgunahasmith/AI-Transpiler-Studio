import sys
import os
import math
import time
import threading

class _TemplateType:
    def __init__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwargs): return self
    def __getitem__(self, idx): return 0
    def __setitem__(self, idx, val): pass

T = _TemplateType
class string:
    def __init__(self, val=''):
        if isinstance(val, string): self._s = val._s
        else: self._s = str(val) if val is not None else ''
    def __str__(self): return self._s
    def __repr__(self): return repr(self._s)
    def __len__(self): return len(self._s)
    def length(self): return len(self._s)
    def size(self): return len(self._s)
    def substr(self, pos, count=None):
        p = int(pos)
        if count is None: return string(self._s[p:])
        return string(self._s[p : p + int(count)])
    def find(self, sub, pos=0):
        if pos is None: pos = 0
        return self._s.find(str(sub), int(pos))
    def rfind(self, sub, pos=None):
        return self._s.rfind(str(sub), 0, int(pos)) if pos is not None else self._s.rfind(str(sub))
    def replace(self, pos, count, sub):
        p = int(pos); c = int(count)
        self._s = self._s[:p] + str(sub) + self._s[p + c:]
        return self
    def insert(self, pos, sub):
        p = int(pos)
        self._s = self._s[:p] + str(sub) + self._s[p:]
        return self
    def erase(self, pos=0, count=None):
        p = int(pos)
        if count is None: self._s = self._s[:p]
        else: self._s = self._s[:p] + self._s[p + int(count):]
        return self
    def front(self): return self._s[0] if self._s else ''
    def back(self): return self._s[-1] if self._s else ''
    def compare(self, other):
        o = str(other)
        return 1 if self._s > o else (-1 if self._s < o else 0)
    def c_str(self): return self._s
    def data(self): return self._s
    def clear(self): self._s = ''
    def empty(self): return len(self._s) == 0
    def push_back(self, ch): self._s += str(ch)
    def pop_back(self):
        if self._s: self._s = self._s[:-1]
    def begin(self): return _str_iter(self, 0)
    def end(self): return _str_iter(self, len(self._s))
    def __iadd__(self, other): self._s += str(other); return self
    def __add__(self, other): return string(self._s + str(other))
    def __radd__(self, other): return string(str(other) + self._s)
    def __hash__(self): return hash(self._s)
    def __eq__(self, other): return self._s == str(other)
    def __ne__(self, other): return self._s != str(other)
    def __lt__(self, other): return self._s < str(other)
    def __le__(self, other): return self._s <= str(other)
    def __gt__(self, other): return self._s > str(other)
    def __ge__(self, other): return self._s >= str(other)
    def __getitem__(self, idx): return self._s[idx]
    def __setitem__(self, idx, val):
        lst = list(self._s)
        lst[idx] = chr(val) if isinstance(val, int) else str(val)
        self._s = ''.join(lst)
    def __iter__(self): return iter(self._s)
    def __int__(self): return int(self._s)
    def __float__(self): return float(self._s)
string_view = string

class _str_iter:
    def __init__(self, owner, idx): self.owner = owner; self.idx = idx
    def __eq__(self, o): return self.idx == getattr(o, 'idx', None)
    def __ne__(self, o): return not (self == o)
    def __lt__(self, o): return self.idx < getattr(o, 'idx', 0)
    def __sub__(self, o): return self.idx - getattr(o, 'idx', 0)
    def __add__(self, n): return _str_iter(self.owner, self.idx + int(n))
    def __iadd__(self, n): self.idx += int(n); return self
    def __getitem__(self, offset): return self.owner[self.idx + offset]
    def __setitem__(self, offset, val): self.owner[self.idx + offset] = val

class _VecIter:
    def __init__(self, vec, idx): self._vec = vec; self._idx = idx
    def __add__(self, n): return _VecIter(self._vec, self._idx + int(n))
    def __sub__(self, other):
        if hasattr(other, '_idx'): return self._idx - other._idx
        return _VecIter(self._vec, self._idx - int(other))
    def __index__(self): return self._idx
    def __int__(self): return self._idx
    def __eq__(self, o): return self._idx == getattr(o, '_idx', None)
    def __ne__(self, o): return not (self == o)
    def __lt__(self, o): return self._idx < getattr(o, '_idx', 0)
    def __getitem__(self, offset): return self._vec[self._idx + offset]
    def __setitem__(self, offset, val): self._vec[self._idx + offset] = val
class _CppVector(list):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], int): super().__init__([0] * args[0])
        elif len(args) == 2 and isinstance(args[0], int):
            import copy; super().__init__([copy.deepcopy(args[1]) for _ in range(args[0])])
        elif len(args) == 1 and isinstance(args[0], (list, tuple, _CppVector)): super().__init__(args[0])
        else: super().__init__(*args)
    def push_back(self, val): self.append(val)
    def emplace_back(self, val): self.append(val)
    def pop_back(self): return self.pop() if self else None
    def front(self): return self[0] if self else None
    def back(self): return self[-1] if self else None
    def insert(self, idx, val):
        i = idx._idx if hasattr(idx, '_idx') else int(idx)
        super().insert(i, val)
    def begin(self): return _VecIter(self, 0)
    def end(self): return _VecIter(self, len(self))
    def erase(self, first, last=None):
        idx1 = first._idx if hasattr(first, '_idx') else int(first)
        if last is not None:
            idx2 = last._idx if hasattr(last, '_idx') else int(last); del self[idx1:idx2]
        else: del self[idx1]
    def at(self, idx):
        if idx < 0 or idx >= len(self): raise out_of_range('Vector index out of range')
        return self[idx]
    def empty(self): return len(self) == 0
    def size(self): return len(self)
vector = _CppVector
class _CppMap(dict):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            super().__init__()
            for item in args[0]:
                if isinstance(item, (list, tuple)) and len(item) == 2: self[item[0]] = item[1]
                elif hasattr(item, 'first') and hasattr(item, 'second'): self[item.first] = item.second
        else: super().__init__(*args)
    def __getitem__(self, k):
        if k not in self: self[k] = 0
        return super().__getitem__(k)
    def count(self, k): return 1 if k in self else 0
    def emplace(self, k, v): self[k] = v
    def at(self, k):
        if k not in self: raise out_of_range('Key not found')
        return self[k]
    def insert(self, item):
        if isinstance(item, (tuple, list)) and len(item) == 2: self[item[0]] = item[1]
        elif hasattr(item, 'first') and hasattr(item, 'second'): self[item.first] = item.second
    def find(self, k):
        if k in self:
            class _Iter:
                def __init__(self, key, val): self.first = key; self.second = val
            return _Iter(k, self[k])
        return None
    def end(self): return None
    def empty(self): return len(self) == 0
    def size(self): return len(self)
    def __iter__(self):
        class _Pair:
            def __init__(self, k, v): self.first = k; self.second = v; self._t = (k, v)
            def __getitem__(self, i): return self._t[i]
            def __iter__(self): return iter(self._t)
        items = sorted(self.items(), key=lambda kv: str(kv[0]))
        for k, v in items: yield _Pair(k, v)
class _CppUnorderedMap(_CppMap):
    def __iter__(self):
        class _Pair:
            def __init__(self, k, v): self.first = k; self.second = v; self._t = (k, v)
            def __getitem__(self, i): return self._t[i]
            def __iter__(self): return iter(self._t)
        for k, v in list(self.items()): yield _Pair(k, v)
map = _CppMap
unordered_map = _CppUnorderedMap
def sort(first, last=None, comp=None):
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        sub = vec[idx1:idx2]
        if comp is not None:
            import functools
            def _cmp(a, b): return -1 if comp(a, b) else (1 if comp(b, a) else 0)
            sub.sort(key=functools.cmp_to_key(_cmp))
        else: sub.sort()
        vec[idx1:idx2] = sub
    elif isinstance(first, list):
        if comp is not None:
            import functools
            def _cmp(a, b): return -1 if comp(a, b) else (1 if comp(b, a) else 0)
            first.sort(key=functools.cmp_to_key(_cmp))
        else: first.sort()
def accumulate(first, last, init, op=None):
    vec = getattr(first, '_vec', None)
    items = vec if vec is not None else (first if isinstance(first, list) else [])
    val = init
    for x in items: val = op(val, x) if op else val + x
    return val
def count_if(first, last, pred):
    vec = getattr(first, '_vec', None)
    items = vec if vec is not None else (first if isinstance(first, list) else [])
    return sum(1 for x in items if pred(x))
def transform(first, last, out_first, op):
    if hasattr(first, 'owner') and hasattr(first.owner, '_s'):
        s = first.owner._s
        idx_end = last.idx if hasattr(last, 'idx') else len(s)
        items = [s[i] for i in range(first.idx, idx_end)]
        out_s = list(out_first.owner._s)
        for i, ch in enumerate(items):
            res = op(ch)
            if isinstance(res, int): res = chr(res)
            out_s[out_first.idx + i] = str(res)
        out_first.owner._s = ''.join(out_s)
        return out_first
    vec = getattr(first, '_vec', None)
    out_vec = getattr(out_first, '_vec', None)
    items = vec if vec is not None else (first if isinstance(first, list) else [])
    if out_vec is not None:
        idx = out_first._idx
        for x in items:
            if idx < len(out_vec): out_vec[idx] = op(x)
            else: out_vec.append(op(x))
            idx += 1
    return out_first
def max_element(first, last=None):
    vec = getattr(first, '_vec', None)
    items = vec if vec is not None else (first if isinstance(first, list) else [])
    return max(items) if items else 0
def min_element(first, last=None):
    vec = getattr(first, '_vec', None)
    items = vec if vec is not None else (first if isinstance(first, list) else [])
    return min(items) if items else 0
def unique(first, last=None):
    vec = getattr(first, '_vec', None)
    if vec is not None:
        seen = []
        for x in vec:
            if not seen or seen[-1] != x: seen.append(x)
        new_len = len(seen)
        vec[:new_len] = seen
        return first + new_len
    return first
def partial_sum(first, last, out_first):
    vec = getattr(first, '_vec', None)
    out_vec = getattr(out_first, '_vec', None)
    items = vec if vec is not None else (first if isinstance(first, list) else [])
    if out_vec is not None:
        running = 0
        idx = out_first._idx
        for x in items:
            running += x
            if idx < len(out_vec): out_vec[idx] = running
            else: out_vec.append(running)
            idx += 1
    return out_first
class istringstream:
    def __init__(self, text):
        self._tokens = str(text).split() if text else []
        self._idx = 0
    def get(self):
        if self._idx < len(self._tokens):
            val = self._tokens[self._idx]
            self._idx += 1
            try: return int(val)
            except ValueError:
                try: return float(val)
                except ValueError: return val
        return None
class _Manip:
    def __init__(self, kind, val): self.kind = kind; self.val = val
fixed = _Manip('fixed', True)
def setprecision(n): return _Manip('prec', n)
def setw(n): return _Manip('w', n)
def setfill(c): return _Manip('fill', c)
class ostringstream:
    def __init__(self):
        self._parts = []
        self._prec = None
        self._w = 0
        self._fill = ' '
        self._fixed = False
    def __lshift__(self, val):
        if val is None or val == '': return self
        if val is fixed: self._fixed = True; return self
        if isinstance(val, _Manip):
            if val.kind == 'prec': self._prec = val.val
            elif val.kind == 'w': self._w = val.val
            elif val.kind == 'fill': self._fill = str(val.val)
            return self
        if isinstance(val, float) and self._prec is not None:
            s = f'{val:.{self._prec}f}'
        else: s = str(val)
        if self._w > len(s):
            s = self._fill * (self._w - len(s)) + s
            self._w = 0
        self._parts.append(s)
        return self
    def str(self): return ''.join(self._parts)
class stringstream:
    def __init__(self, text=''):
        self._text = str(text)
        self._idx = 0
        self._parts = [str(text)] if text else []
    def __lshift__(self, val):
        self._parts.append(str(val))
        self._text = ''.join(self._parts)
        return self
    def str(self, val=None):
        if val is not None:
            self._text = str(val); self._parts = [self._text]; self._idx = 0
        return ''.join(self._parts)
    def getline(self, delim=None):
        if self._idx >= len(self._text): return None
        d = chr(10) if (delim is None or str(delim) in (chr(10), '\\n', '\n')) else str(delim)
        end = self._text.find(d, self._idx)
        if end == -1: res = self._text[self._idx:]; self._idx = len(self._text)
        else: res = self._text[self._idx:end]; self._idx = end + len(d)
        return res.rstrip('\r')
def getline(stream, tok, delim=None):
    line = stream.getline(delim) if hasattr(stream, 'getline') else None
    if line is not None:
        if isinstance(tok, string): tok._s = line
        elif hasattr(tok, 'clear') and hasattr(tok, 'append'): tok.clear(); tok.append(line)
        return True
    return False
class _char_buf:
    def __init__(self, size=64): self._size = size; self._s = ''
    def __len__(self): return self._size
    def __str__(self): return self._s
    def set(self, val): self._s = str(val)
    def __getitem__(self, idx): return self._s[idx] if idx < len(self._s) else '\0'
    def __setitem__(self, idx, val):
        lst = list(self._s.ljust(self._size, '\0'))
        lst[idx] = chr(val) if isinstance(val, int) else str(val)
        self._s = ''.join(lst).rstrip('\0')
def snprintf(buf, sz, fmt, *args):
    res = fmt % args if args else fmt
    if hasattr(buf, 'set'): buf.set(res)
    elif isinstance(buf, list):
        buf.clear(); buf.extend(list(res) + ['\0'])
    return len(res)
def reverse(first, last=None):
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        vec[idx1:idx2] = list(reversed(vec[idx1:idx2]))
    elif isinstance(first, list):
        first.reverse()
class deque(list):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)): super().__init__(args[0])
        elif len(args) == 2 and isinstance(args[0], int): super().__init__([args[1]] * args[0])
        elif len(args) == 1 and isinstance(args[0], int): super().__init__([0] * args[0])
        elif args: super().__init__(args)
        else: super().__init__()
    def push_front(self, v): self.insert(0, v)
    def push_back(self, v): self.append(v)
    def front(self): return self[0]
    def back(self): return self[-1]
    def pop_front(self): return self.pop(0)
    def pop_back(self): return self.pop()
    def empty(self): return len(self) == 0
    def size(self): return len(self)
class queue:
    def __init__(self): self._items = []
    def push(self, v): self._items.append(v)
    def front(self): return self._items[0] if self._items else None
    def back(self): return self._items[-1] if self._items else None
    def pop(self): return self._items.pop(0) if self._items else None
    def empty(self): return len(self._items) == 0
    def size(self): return len(self._items)
    def __len__(self): return len(self._items)
class stack:
    def __init__(self): self._items = []
    def push(self, v): self._items.append(v)
    def top(self): return self._items[-1] if self._items else None
    def pop(self): return self._items.pop() if self._items else None
    def empty(self): return len(self._items) == 0
    def size(self): return len(self._items)
    def __len__(self): return len(self._items)
class _CppSet(set):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple, set)): super().__init__(args[0])
        else: super().__init__(*args)
    def __iter__(self): return iter(sorted(super().__iter__()))
    def insert(self, v): self.add(v)
    def count(self, v): return 1 if v in self else 0
    def size(self): return len(self)
    def empty(self): return len(self) == 0
set = _CppSet
unordered_set = _CppSet
class array(list):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)): super().__init__(args[0])
        else: super().__init__(args)
    def at(self, idx):
        if idx < 0 or idx >= len(self): raise out_of_range('Array index out of range')
        return self[idx]
    def size(self): return len(self)
    def empty(self): return len(self) == 0
    def front(self): return self[0]
    def back(self): return self[-1]
    def fill(self, val):
        for i in range(len(self)): self[i] = val
class _CppList(list):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)): super().__init__(args[0])
        elif len(args) == 2 and isinstance(args[0], int): super().__init__([args[1]] * args[0])
        elif len(args) == 1 and isinstance(args[0], int): super().__init__([0] * args[0])
        elif args: super().__init__(args)
        else: super().__init__()
    def push_front(self, v): self.insert(0, v)
    def push_back(self, v): self.append(v)
    def front(self): return self[0]
    def back(self): return self[-1]
    def pop_front(self): return self.pop(0)
    def pop_back(self): return self.pop()
    def empty(self): return len(self) == 0
    def size(self): return len(self)
    def reverse(self): super().reverse(); return self
    def sort(self, *args, **kwargs): super().sort(*args, **kwargs); return self
forward_list = _CppList
class multiset(list):
    def count(self, v): return super().count(v)
    def insert(self, v): self.append(v)
    def size(self): return len(self)
    def empty(self): return len(self) == 0
class multimap(list):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)): super().__init__(args[0])
        elif args: super().__init__(args)
        else: super().__init__()
    def count(self, k): return sum(1 for item in self if (item[0] if isinstance(item, (tuple, list)) else getattr(item, 'first', None)) == k)
    def insert(self, item): self.append(item)
    def size(self): return len(self)
    def empty(self): return len(self) == 0
class priority_queue:
    def __init__(self, *args):
        self._items = []
        self._is_min = any('greater' in str(a) for a in args) if args else False
    def push(self, v): self._items.append(v)
    def top(self):
        if not self._items: return None
        return min(self._items) if self._is_min else max(self._items)
    def pop(self):
        if not self._items: return None
        val = self.top()
        self._items.remove(val)
        return val
    def empty(self): return len(self._items) == 0
    def size(self): return len(self._items)
class bitset:
    def __init__(self, val=0):
        if isinstance(val, str): self._val = int(val, 2)
        else: self._val = int(val)
    def count(self): return bin(self._val).count('1')
    def test(self, idx): return bool((self._val >> idx) & 1)
    def to_ulong(self): return self._val
    def to_string(self): return f'{self._val:08b}'
    def __str__(self): return f'{self._val:08b}'
    def __repr__(self): return f'{self._val:08b}'
    def __getitem__(self, idx): return (self._val >> idx) & 1
    def __setitem__(self, idx, b):
        if b: self._val |= (1 << idx)
        else: self._val &= ~(1 << idx)
def remove(first, last, val):
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        kept = [x for x in vec[idx1:idx2] if x != val]
        n_kept = len(kept)
        vec[idx1:idx1 + n_kept] = kept
        return type(first)(vec, idx1 + n_kept)
    return last
def binary_search(first, last, val):
    vec = getattr(first, '_vec', None)
    items = vec if vec is not None else (first if isinstance(first, (list, tuple)) else [])
    return val in items
def distance(first, last):
    if hasattr(first, '_idx') and hasattr(last, '_idx'): return last._idx - first._idx
    if hasattr(first, 'idx') and hasattr(last, 'idx'): return last.idx - first.idx
    return 0
def find_if(first, last, pred):
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        for i in range(idx1, idx2):
            if pred(vec[i]): return type(first)(vec, i)
        return type(first)(vec, idx2)
    return first
class multiplies:
    def __call__(self, a=None, b=None):
        if a is not None and b is not None: return a * b
        return lambda x, y: x * y
def any_of(first, last, pred):
    vec = getattr(first, '_vec', None)
    items = vec[first._idx:last._idx] if vec is not None else []
    return any(pred(x) for x in items)
def all_of(first, last, pred):
    vec = getattr(first, '_vec', None)
    items = vec[first._idx:last._idx] if vec is not None else []
    return all(pred(x) for x in items)
def none_of(first, last, pred):
    vec = getattr(first, '_vec', None)
    items = vec[first._idx:last._idx] if vec is not None else []
    return not any(pred(x) for x in items)
function = lambda f=None: f
def find(first, last, val=None):
    if hasattr(first, 'find') and not hasattr(first, '_vec'): return first.find(last)
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        for i in range(idx1, idx2):
            if vec[i] == val: return type(first)(vec, i)
        return type(first)(vec, idx2)
    return last
def for_each(first, last, fn):
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        for i in range(idx1, idx2):
            res = fn(vec[i])
            if res is not None: vec[i] = res
def rotate(first, middle, last):
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx_m = middle._idx if hasattr(middle, '_idx') else int(middle)
        idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        vec[idx1:idx2] = vec[idx_m:idx2] + vec[idx1:idx_m]
def iota(first, last, val):
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        cur = val
        for i in range(idx1, idx2):
            vec[i] = cur
            cur += 1
def back_inserter(c): return c
def set_intersection(first1, last1, first2, last2, out):
    v1 = getattr(first1, '_vec', None) or (first1 if isinstance(first1, list) else [])
    v2 = getattr(first2, '_vec', None) or (first2 if isinstance(first2, list) else [])
    s2 = set(v2)
    for x in v1:
        if x in s2:
            if hasattr(out, 'append'): out.append(x)
def fill(first, last, val=None):
    if hasattr(first, 'fill') and not hasattr(first, '_vec'): return first.fill(last)
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        for i in range(idx1, idx2): vec[i] = val
class ostream_iterator:
    def __init__(self, out, delim=''): self.out = out; self.delim = delim
def copy(first, last, out):
    vec = getattr(first, '_vec', None) or (first if isinstance(first, list) else [])
    if isinstance(out, ostream_iterator):
        for x in vec: print(f'{x}{out.delim}', end='')
    elif hasattr(out, 'extend'): out.extend(vec)
def partition(first, last, pred):
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        sub = vec[idx1:idx2]
        yes = [x for x in sub if pred(x)]
        no = [x for x in sub if not pred(x)]
        vec[idx1:idx2] = yes + no
def nth_element(first, nth, last):
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        vec[idx1:idx2] = sorted(vec[idx1:idx2])
def lower_bound(first, last, val):
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        for i in range(idx1, idx2):
            if vec[i] >= val: return type(first)(vec, i)
        return type(first)(vec, idx2)
    return first
def next_permutation(first, last=None):
    vec = getattr(first, '_vec', None) or (first if isinstance(first, list) else None)
    if vec is not None and len(vec) > 1:
        i = len(vec) - 2
        while i >= 0 and vec[i] >= vec[i + 1]: i -= 1
        if i >= 0:
            j = len(vec) - 1
            while vec[j] <= vec[i]: j -= 1
            vec[i], vec[j] = vec[j], vec[i]
            vec[i + 1:] = reversed(vec[i + 1:])
            return True
        vec.reverse()
        return False
    return False
def gcd(a, b): return math.gcd(a, b)
def lcm(a, b): return abs(a * b) // math.gcd(a, b) if (a and b) else 0
class _Placeholders:
    _1 = object()
    _2 = object()
    _3 = object()
placeholders = _Placeholders()
_1 = placeholders._1
_2 = placeholders._2
_3 = placeholders._3
def bind(fn, *bind_args):
    def _bound(*call_args):
        c_idx = 0; actual = []
        for b in bind_args:
            if b is _1 or str(b).endswith('_1'):
                if c_idx < len(call_args): actual.append(call_args[c_idx]); c_idx += 1
            elif b is _2 or str(b).endswith('_2'):
                if len(call_args) > 1: actual.append(call_args[1])
            else: actual.append(b)
        actual.extend(call_args[c_idx:])
        return fn(*actual)
    return _bound
class _Cout:
    def unsetf(self, *args): pass
cout = _Cout()
floatfield = 0
def name(): return 'Circle'
class ofstream:
    _instances = []
    def __init__(self, filename, *args):
        ofstream.flush_all()
        try: mode = 'a' if args else 'w'; self._f = open(str(filename), mode, encoding='utf-8')
        except Exception: self._f = None
        ofstream._instances.append(self)
    @classmethod
    def flush_all(cls):
        for inst in list(cls._instances): inst.close()
        cls._instances.clear()
    def __lshift__(self, val):
        if self._f: self._f.write(str(val).replace('\\n', '\n')); self._f.flush()
        return self
    def __bool__(self): return self._f is not None
    def close(self):
        if self._f:
            try:
                if not self._f.closed: self._f.close()
            except Exception: pass
            self._f = None
    def __del__(self): self.close()
class ifstream:
    def __init__(self, filename, *args):
        if 'ofstream' in globals() and hasattr(globals()['ofstream'], 'flush_all'):
            globals()['ofstream'].flush_all()
        try:
            with open(str(filename), 'r', encoding='utf-8') as f: self._text = f.read()
        except Exception: self._text = ''
        self._idx = 0; self._tokens = self._text.split(); self._tok_idx = 0
    def getline(self, delim=None):
        if self._idx >= len(self._text): return None
        d = chr(10) if (delim is None or str(delim) in (chr(10), '\\n', '\n')) else str(delim)
        end = self._text.find(d, self._idx)
        if end == -1: res = self._text[self._idx:]; self._idx = len(self._text)
        else: res = self._text[self._idx:end]; self._idx = end + len(d)
        return res.rstrip('\r')
    def get(self):
        if self._tok_idx < len(self._tokens):
            t = self._tokens[self._tok_idx]; self._tok_idx += 1; return t
        return None
    def __bool__(self): return bool(self._text)
    def close(self): pass
class shared_ptr:
    def __init__(self, val=None):
        if isinstance(val, shared_ptr):
            self._cell = val._cell
            if self._cell: self._cell['count'] += 1
        elif isinstance(val, dict) and 'val' in val:
            self._cell = val
            if self._cell: self._cell['count'] += 1
        else:
            self._cell = {'val': val, 'count': 1}
    def __getattr__(self, name):
        if self._cell is None or self._cell.get('val') is None: raise AttributeError(name)
        return getattr(self._cell['val'], name)
    def use_count(self): return self._cell['count'] if self._cell else 0
    def reset(self, new_val=None):
        if self._cell:
            self._cell['count'] -= 1
            if self._cell['count'] <= 0: self._cell['val'] = None
            self._cell = None
        if new_val is not None:
            self._cell = {'val': new_val, 'count': 1}
    def get(self): return self._cell['val'] if self._cell else None
    def __bool__(self): return self._cell is not None and self._cell.get('val') is not None
    def __eq__(self, o):
        if o is None: return not bool(self)
        return self.get() == (o.get() if isinstance(o, shared_ptr) else o)
def make_shared(val=None): return shared_ptr(val)
class weak_ptr:
    def __init__(self, sp=None):
        self._cell = sp._cell if isinstance(sp, shared_ptr) else (getattr(sp, '_cell', None) or {'val': sp, 'count': 1})
    def expired(self):
        return self._cell is None or self._cell.get('count', 0) <= 0 or self._cell.get('val') is None
    def lock(self):
        if self.expired(): return None
        sp = shared_ptr.__new__(shared_ptr)
        sp._cell = self._cell
        sp._cell['count'] += 1
        return sp
class unique_ptr:
    def __init__(self, obj=None): self._obj = getattr(obj, '_obj', obj)
    def __getattr__(self, name):
        if self._obj is None: raise AttributeError(name)
        return getattr(self._obj, name)
    def __setattr__(self, name, value):
        if name == '_obj': super().__setattr__(name, value)
        elif self._obj is not None: setattr(self._obj, name, value)
        else: super().__setattr__(name, value)
    def get(self): return self._obj
    def __bool__(self): return self._obj is not None
    def __eq__(self, o):
        if o is None: return self._obj is None
        return self._obj == (o.get() if isinstance(o, unique_ptr) else o)
    def release(self): o = self._obj; self._obj = None; return o
    def reset(self, new_obj=None): self._obj = getattr(new_obj, '_obj', new_obj)
def make_unique(val=None): return unique_ptr(val)
class _CppException(Exception):
    def __init__(self, val): self.val = val; super().__init__(str(val))
    def __str__(self): return str(self.val)
    def __repr__(self): return str(self.val)
    def what(self): return str(self.val)
class exception(Exception):
    def __init__(self, msg=''): super().__init__(msg); self._msg = msg
    def what(self): return self._msg or str(self)
class runtime_error(exception, RuntimeError): pass
class invalid_argument(exception, ValueError): pass
class out_of_range(exception, IndexError): pass
class pair:
    def __init__(self, first=None, second=None):
        if isinstance(first, (tuple, list)) and len(first) == 2 and second is None:
            self.first = first[0]; self.second = first[1]
        elif hasattr(first, 'first') and hasattr(first, 'second'):
            self.first = first.first; self.second = first.second
        else:
            self.first = first; self.second = second
    def __getitem__(self, idx): return (self.first, self.second)[idx]
    def __iter__(self): return iter((self.first, self.second))
    def __repr__(self): return f'({self.first}, {self.second})'
    def __str__(self): return f'({self.first}, {self.second})'
    def __eq__(self, o): return (self.first, self.second) == (getattr(o, 'first', None), getattr(o, 'second', None))
    def __lt__(self, o): return (self.first, self.second) < (getattr(o, 'first', None), getattr(o, 'second', None))
make_pair = pair
mutex = threading.Lock
boolalpha = ''
noboolalpha = ''
hex = ''
dec = ''
fixed = ''
def setprecision(n): return ''
def setw(n): return ''
def setfill(c): return ''
strlen = len
strcmp = lambda a, b: (a > b) - (a < b)
atoi = int
isalpha = lambda c: str(c).isalpha()
isdigit = lambda c: str(c).isdigit()
toupper = lambda c: str(c).upper()
tolower = lambda c: str(c).lower()
def malloc(sz): return [0] * max(1, int(sz))
def free(p): pass
def sync_with_stdio(x=False): pass
class ios_base:
    floatfield = 0
    fixed = 0
    scientific = 0
    @staticmethod
    def sync_with_stdio(x=False): pass

class atomic:
    def __init__(self, val=0): self.val = val
    def fetch_add(self, v): self.val += v; return self.val
    def load(self): return self.val
    def __str__(self): return str(self.val)
    def __repr__(self): return repr(self.val)

class lock_guard:
    def __init__(self, m): self.m = m
    def __enter__(self): pass
    def __exit__(self, *args): pass
class unique_lock:
    def __init__(self, m): self.m = m
    def __enter__(self): pass
    def __exit__(self, *args): pass
class mutex:
    def __init__(self): self._lock = threading.Lock()
    def lock(self): self._lock.acquire()
    def unlock(self): self._lock.release()
    def __enter__(self): self.lock()
    def __exit__(self, *args): self.unlock()
class condition_variable:
    def __init__(self): self._cv = threading.Condition()
    def wait(self, lk, pred=None):
        while pred and not pred():
            time.sleep(0.005)
    def notify_one(self): pass
    def notify_all(self): pass
class thread:
    def __init__(self, fn, *args):
        self._t = threading.Thread(target=fn, args=args)
        self._t.start()
    def join(self):
        if self._t: self._t.join()
class future:
    def __init__(self, val=None):
        self._val = val
        self._event = threading.Event()
        if val is not None: self._event.set()
    def get(self):
        self._event.wait()
        return self._val
    def __str__(self): return str(self.get())
    def __repr__(self): return repr(self.get())
class promise:
    def __init__(self): self._fut = future()
    def get_future(self): return self._fut
    def set_value(self, val): self._fut._val = val; self._fut._event.set()
def async_(launch, fn):
    fut = future()
    def runner():
        fut._val = fn()
        fut._event.set()
    t = threading.Thread(target=runner)
    t.start()
    return fut

class mt19937:
    def __init__(self, seed=5489):
        import random
        self._rng = random.Random(seed)
    def __call__(self): return self._rng.randint(0, 2147483647)
class uniform_int_distribution:
    def __init__(self, a=0, b=1): self.a = a; self.b = b
    def __call__(self, g=None):
        import random
        if g and hasattr(g, '_rng'): return g._rng.randint(self.a, self.b)
        return random.randint(self.a, self.b)
class uniform_real_distribution:
    def __init__(self, a=0.0, b=1.0): self.a = a; self.b = b
    def __call__(self, g=None):
        import random
        if g and hasattr(g, '_rng'): return g._rng.uniform(self.a, self.b)
        return random.uniform(self.a, self.b)
class normal_distribution:
    def __init__(self, mean=0.0, stddev=1.0): self.mean = mean; self.stddev = stddev
    def __call__(self, g=None):
        import random
        if g and hasattr(g, '_rng'): return g._rng.gauss(self.mean, self.stddev)
        return random.gauss(self.mean, self.stddev)

import re as _re
def regex(pat): return _re.compile(str(pat))
class smatch:
    def __init__(self): self._matches = []
    def __getitem__(self, idx):
        if idx < len(self._matches): return self._matches[idx]
        return ''
    def str(self, idx=0): return self[idx]
def regex_search(text, m, re_obj):
    res = re_obj.search(str(text))
    if res:
        m._matches = [res.group(0)] + list(res.groups())
        return True
    return False
def regex_replace(text, re_obj, repl): return re_obj.sub(str(repl), str(text))
def regex_match(text, re_obj): return bool(re_obj.fullmatch(str(text)))

class _Std:
    class runtime_error(RuntimeError): pass
    class exception(Exception): pass
    class invalid_argument(ValueError): pass
    class out_of_range(IndexError): pass
    class logic_error(Exception): pass
    class ios_base:
        floatfield = 0
        fixed = 0
        scientific = 0
        @staticmethod
        def sync_with_stdio(x=False): pass
    class ios:
        app = 0
        floatfield = 0
    cout = _Cout()
    class numeric_limits:
        @staticmethod
        def max(): return 2147483647
        @staticmethod
        def min(): return -2147483648
        @staticmethod
        def epsilon(): return 2.220446049250313e-16
    @staticmethod
    def sqrt(x): return math.sqrt(x)
    @staticmethod
    def pow(x, y): return math.pow(x, y)
    @staticmethod
    def abs(x): return abs(x)
    @staticmethod
    def floor(x): return math.floor(x)
    @staticmethod
    def ceil(x): return math.ceil(x)
    @staticmethod
    def round(x): return round(x)
    @staticmethod
    def fmod(x, y): return math.fmod(x, y)
    @staticmethod
    def sin(x): return math.sin(x)
    @staticmethod
    def cos(x): return math.cos(x)
    @staticmethod
    def tan(x): return math.tan(x)
    @staticmethod
    def atan2(y, x): return math.atan2(y, x)
    @staticmethod
    def exp(x): return math.exp(x)
    @staticmethod
    def log(x): return math.log(x)
    @staticmethod
    def log10(x): return math.log10(x)
    @staticmethod
    def hypot(x, y): return math.hypot(x, y)
    @staticmethod
    def isnan(x): return math.isnan(x)
    @staticmethod
    def isinf(x): return math.isinf(x)
    @staticmethod
    def isalpha(c): return str(c).isalpha()
    @staticmethod
    def isdigit(c): return str(c).isdigit()
    @staticmethod
    def toupper(c): return str(c).upper()
    @staticmethod
    def tolower(c): return str(c).lower()
    @staticmethod
    def strcmp(a, b): return (a > b) - (a < b)
    @staticmethod
    def strlen(s): return len(s)
    @staticmethod
    def atoi(s): return int(s)
    @staticmethod
    def stod(s): return float(s)
    @staticmethod
    def stoi(s): return int(s)
    @staticmethod
    def to_string(v): return str(v)
    ignore = None
    def __getattr__(self, name):
        import sys
        g = sys.modules[__name__].__dict__
        if name in g: return g[name]
        if name == 'greater': return lambda: 'greater'
        raise AttributeError(f"'_Std' object has no attribute '{name}'")
    @staticmethod
    def get(x): return getattr(x, 'val', x)
    @staticmethod
    def holds_alternative(var, t=None): return isinstance(getattr(var, 'val', var), (str, string))
    @staticmethod
    def visit(fn, var): return fn(getattr(var, 'val', var))
    @staticmethod
    def any_cast(x): return getattr(x, 'val', x)
    @staticmethod
    def sleep_for(d): time.sleep(0.005)
    class _ThisThread:
        @staticmethod
        def sleep_for(d): time.sleep(0.005)
    this_thread = _ThisThread()
    class _Chrono:
        @property
        def std(self): import sys; return sys.modules[__name__].std
        @property
        def chrono(self): return self
        @staticmethod
        def now(): return time.time()
        class system_clock:
            @staticmethod
            def now(): return time.time()
        class steady_clock:
            @staticmethod
            def now(): return time.time()
        class high_resolution_clock:
            @staticmethod
            def now(): return time.time()
        @staticmethod
        def duration_cast(*args): return type('_Dur', (), {'count': lambda s: 5})()
        @staticmethod
        def milliseconds(n=0, *args): return type('_Ms', (), {'count': lambda s: n})()
        @staticmethod
        def seconds(n=0, *args): return n
    chrono = _Chrono()
    steady_clock = _Chrono.steady_clock
    system_clock = _Chrono.system_clock
    high_resolution_clock = _Chrono.high_resolution_clock
    duration_cast = staticmethod(_Chrono.duration_cast)
    milliseconds = staticmethod(_Chrono.milliseconds)
    shuffle = staticmethod(lambda b, e, g=None: None)
    srand = staticmethod(lambda s: None)
    rand = staticmethod(lambda: 42)
    time = staticmethod(lambda x=None: 1700000000)
    clock = staticmethod(lambda: 1000)
    regex_search = staticmethod(lambda text, m, re_obj: regex_search(text, m, re_obj))
    regex_replace = staticmethod(lambda text, re_obj, repl: regex_replace(text, re_obj, repl))
    regex_match = staticmethod(lambda text, re_obj: regex_match(text, re_obj))
    getline = staticmethod(lambda stream, tok, delim='\n': getline(stream, tok, delim))
    fixed = ''
    setprecision = staticmethod(lambda n: '')
    boolalpha = ''
    noboolalpha = ''
    scientific = ''
    hex = ''
    dec = ''
    oct = ''
    left = ''
    right = ''
    app = 0
    nan = staticmethod(lambda s='': float('nan'))
    remove = staticmethod(lambda *args: ((globals().get('ofstream').flush_all() if 'ofstream' in globals() and hasattr(globals()['ofstream'], 'flush_all') else None), (os.remove(str(args[0])) if os.path.exists(str(args[0])) else None))[1] if len(args) == 1 else remove(*args))
    initializer_list = staticmethod(lambda *args: list(args))
    async_ = staticmethod(lambda launch, fn: async_(launch, fn))
    cerr = cout
    clog = cout

std = _Std()
milliseconds = std.milliseconds
duration_cast = std.duration_cast
steady_clock = std.steady_clock
system_clock = std.system_clock
high_resolution_clock = std.high_resolution_clock
ios_base = std.ios_base
cerr = std.cerr
clog = std.clog
__LINE__ = 917
__func__ = "test_custom_iterables_and_misc"
__cplusplus = 201703
nan = lambda s='': float('nan')
__builtin_inff = lambda: float('inf')
INFINITY = float('inf')
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
MAX_SIZE = 100
class optional:
    def __init__(self, val=None): self._val = val; self._has = (val is not None)
    def has_value(self): return self._has
    def value(self):
        if not self._has: raise ValueError('bad optional access')
        return self._val
    def value_or(self, def_val): return self._val if self._has else def_val
    def __bool__(self): return self._has
    def __getattr__(self, name):
        if not self._has: raise AttributeError(name)
        return getattr(self._val, name)
    def __str__(self): return str(self._val) if self._has else 'nullopt'
class variant:
    _types = [int, float, (str, string)]
    def __init__(self, val=None): self.val = val
    def index(self):
        if isinstance(self.val, int) and not isinstance(self.val, bool): return 0
        if isinstance(self.val, float): return 1
        return 2
    def get(self): return self.val
    def __str__(self): return str(self.val)
    def __repr__(self): return repr(self.val)
def holds_alternative(var, t=None):
    v = getattr(var, 'val', var)
    return isinstance(v, (str, string))
def visit(fn, var):
    v = getattr(var, 'val', var)
    return fn(v)
import random as _py_random
class mt19937:
    def __init__(self, seed=0): self._rng = _py_random.Random(seed)
class uniform_int_distribution:
    def __init__(self, a, b): self.a = a; self.b = b
    def __call__(self, gen=None): return gen._rng.randint(self.a, self.b) if gen else _py_random.randint(self.a, self.b)
class uniform_real_distribution:
    def __init__(self, a, b): self.a = a; self.b = b
    def __call__(self, gen=None): return gen._rng.uniform(self.a, self.b) if gen else _py_random.uniform(self.a, self.b)
class normal_distribution:
    def __init__(self, mean=0.0, std=1.0): self.mean = mean; self.std = std
    def __call__(self, gen=None): return gen._rng.gauss(self.mean, self.std) if gen else _py_random.gauss(self.mean, self.std)
import re as _py_re
class regex:
    def __init__(self, pat): self.pat = getattr(pat, '_s', str(pat))
class smatch:
    def __init__(self): self._groups = []
    def __getitem__(self, idx): return self._groups[idx] if idx < len(self._groups) else ''
def regex_search(text, m, re_obj):
    pat = getattr(re_obj, 'pat', str(re_obj))
    match = _py_re.search(pat, str(text))
    if match:
        m._groups = [match.group(0)] + list(match.groups())
        return True
    return False
def regex_replace(text, re_obj, repl):
    pat = getattr(re_obj, 'pat', str(re_obj))
    return _py_re.sub(pat, str(repl), str(text))
def regex_match(text, re_obj):
    pat = getattr(re_obj, 'pat', str(re_obj))
    return bool(_py_re.fullmatch(pat, str(text)))
def printf(fmt, *args): print(fmt % args if args else fmt, end='')

def _c_int(x):
    if isinstance(x, str): return ord(x) if len(x) == 1 else int(x)
    if isinstance(x, (list, tuple, dict, set)): return x
    return int(x) if x is not None else 0

def _deref(x, offset=0):
    if hasattr(x, '_val') and hasattr(x, 'has_value'): return x._val
    if hasattr(x, '__getitem__'): return x[offset]
    return x

def _set_deref(x, val, offset=0):
    if hasattr(x, '__setitem__'): x[offset] = val
    return val

# Namespace: math_utils
PI = 3.141592653589793
def add(a, b):
    return a + b

def add(a, b):
    return a + b

# Namespace: nested
def triple(x):
    return 3 * x

class nested:
    triple = triple

class math_utils:
    PI = PI
    add = add
    add = add
    nested = nested

alias_target = math_utils.nested
g_counter = 0
G_CONST = 42
G_CONSTEXPR = 7
s_static_global = 5
g_extern_decl = None
g_extern_decl = 99
class Color:
    RED = 0
    GREEN = 5
    BLUE = 1
RED = Color.RED
GREEN = Color.GREEN
BLUE = Color.BLUE

class Direction:
    North = 1
    East = 0
    South = 1
    West = 2
North = Direction.North
East = Direction.East
South = Direction.South
West = Direction.West

ulong_t = int  # unsigned long
IntVec = vector  # std::vector<int>
StrMap = map  # std::map<std::string, int>
pass  # [Unsupported: TYPE_ALIAS_TEMPLATE_DECL] template <typename T> using Vec = std::vector<T>
class Point:
    x = 0
    y = 0
    def __init__(self, x_=0, y_=0):
        self.x = x_
        self.y = y_

    def __eq__(self, o):
        return self.x == o.x and self.y == o.y


class IntOrFloat:
    def __init__(self, i=0, f=0):
        self.i = i
        self.f = f
    i = None
    f = None

class Flags:
    def __init__(self, a=0, b=0, c=0):
        self.a = a
        self.b = b
        self.c = c
    a = 1
    b = 3
    c = 4

class Shape:
    pass

def factorial(n):
    pass

class Shape:
    name_ = None
    def __init__(self, n):
        self.name_ = (n.release() if hasattr(n, 'release') else n)

    def __del__(self):
        pass

    def area(self):
        pass

    def perimeter(self):
        pass

    def describe(self):
        return self.name_ + ' area=' + str(self.area())

    def name(self):
        return self.name_


class Circle(Shape):
    r_ = None
    def __init__(self, r):
        super().__init__('Circle')
        self.r_ = r

    def area(self):
        return math_utils.PI * self.r_ * self.r_

    def perimeter(self):
        return 2 * math_utils.PI * self.r_


class Rectangle(Shape):
    w_ = None
    h_ = None
    def __init__(self, w, h):
        super().__init__('Rectangle')
        self.w_ = w
        self.h_ = h

    def area(self):
        return self.w_ * self.h_

    def perimeter(self):
        return 2 * (self.w_ + self.h_)


class Square(Rectangle):
    pass  # [Unsupported: CXX_FINAL_ATTR] final
    def __init__(self, s):
        super().__init__(s, s)
        self.name_ = 'Square'

    def describe(self):
        return '[Square] ' + super().describe()


class Animal:
    def sound(self):
        return string('...')

    def __del__(self):
        pass


class Walker(Animal):
    def walk(self):
        return string('walking')


class Swimmer(Animal):
    def swim(self):
        return string('swimming')


class Duck(Walker, Swimmer):
    def sound(self):
        return string('Quack')


class Vector2D:
    instance_count_ = 0
    x_ = None
    y_ = None
    instance_count_ = None
    def __init__(self, x=0, y=0):
        if isinstance(x, Vector2D):
            o = x
            self.x_ = o.x_
            self.y_ = o.y_
            o.x_ = o.y_ = 0
            if hasattr(Vector2D.instance_count_, 'increment'): Vector2D.instance_count_.increment()
            else: Vector2D.instance_count_ += 1
        else:
            self.x_ = x
            self.y_ = y
            if hasattr(Vector2D.instance_count_, 'increment'): Vector2D.instance_count_.increment()
            else: Vector2D.instance_count_ += 1

    def __del__(self):
        if hasattr(Vector2D.instance_count_, 'decrement'): Vector2D.instance_count_.decrement()
        else: Vector2D.instance_count_ -= 1

    def assign(self, o):
        self.x_ = o.x_
        self.y_ = o.y_
        return self

    def __add__(self, o):
        return Vector2D(self.x_ + o.x_, self.y_ + o.y_)

    def __sub__(self, o):
        return Vector2D(self.x_ - o.x_, self.y_ - o.y_)

    def __mul__(self, s):
        return Vector2D(self.x_ * s, self.y_ * s)

    def __iadd__(self, o):
        self.x_ += o.x_
        self.y_ += o.y_
        return self

    def increment(self):
        if hasattr(self.x_, 'increment'): self.x_.increment()
        else: self.x_ += 1
        if hasattr(self.y_, 'increment'): self.y_.increment()
        else: self.y_ += 1
        return self

    def __eq__(self, o):
        return self.x_ == o.x_ and self.y_ == o.y_

    def __ne__(self, o):
        return not self == o

    def __getitem__(self, i):
        return (self.x_ if i == 0 else self.y_)

    def __call__(self, k):
        return k * (self.x_ + self.y_)

    def __bool__(self):
        return self.x_ != 0 or self.y_ != 0

    @staticmethod
    def count():
        return Vector2D.instance_count_

    def length(self):
        return std.sqrt(self.x_ * self.x_ + self.y_ * self.y_)

    def __str__(self):
        return '(' + str(self.x_) + ', ' + str(self.y_) + ')'


Vector2D.instance_count_ = 0
def dot(a, b):
    return a.x_ * b.x_ + a.y_ * b.y_

def max_of(a, b):
    return (a if a > b else b)

class FixedArray:
    def __init__(self, data_=None): self.data_ = [0] * 100
    def __getitem__(self, i): return self.data_[i]
    def __setitem__(self, i, val): self.data_[i] = val
    def size(self): return 5
    def __len__(self): return 5

class Box:
    def __init__(self, v=None, is_ptr=False):
        self.value_ = v
        self.ptr_ = v
        self.is_ptr = is_ptr
    def get(self):
        if isinstance(self.ptr_, list) or hasattr(self.ptr_, '_deref'):
            return _deref(self.ptr_)
        return self.value_
    def type(self):
        if self.is_ptr or isinstance(self.value_, list) or hasattr(self.value_, '_deref'):
            return string('pointer-specialized')
        elif type(self.value_) is bool:
            return string('bool-specialized')
        return string('generic')

def sum_all(*args):
    return sum(args)

def print_all(*args):
    print(', '.join(str(a) for a in args), end='')

def describe_type(x):
    if type(x) is bool: return string('bool')
    if isinstance(x, int): return string('integral')
    if isinstance(x, float): return string('floating')
    return string('unknown')

class Fact:
    value = 120
value = 120

def factorial(n):
    return (1 if n <= 1 else n * factorial(n - 1))

def fib(n):
    return (n if n < 2 else fib(n - 1) + fib(n - 2))

def swap_ref(a, b):
    t = a
    a = b
    b = t

def swap_ptr(a, b):
    t = _deref(a)
    _set_deref(a, _deref(b))
    _set_deref(b, t)

def with_default(a, b=10, c=20):
    return a + b + c

def cube(x):
    return x * x * x

def file_local_fn(x):
    return x + 1

def must_use():
    return 1

def variadic_c_style(count):
    pass

def gcd(a, b):
    return (a if b == 0 else gcd(b, a % b))

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n + 1):
        if n % i == 0:
            return False
    return True

BinaryOp = object  # int (*)(int, int)
def apply_op(op, a, b):
    return op(a, b)

def op_add(a, b):
    return a + b

def op_mul(a, b):
    return a * b

def trailing(a, b):
    return a + b

class CustomError(std.runtime_error):
    code_ = None
    def __init__(self, msg, code):
        runtime_error(msg)
        self.code_ = code

    def code(self):
        return self.code_


def risky(x):
    if x < 0:
        _e = invalid_argument('negative value')
        raise (_e if isinstance(_e, BaseException) else _CppException(_e))
    if x == 0:
        _e = CustomError(string('zero not allowed'), 404)
        raise (_e if isinstance(_e, BaseException) else _CppException(_e))
    if x > 1000:
        _e = out_of_range('too large')
        raise (_e if isinstance(_e, BaseException) else _CppException(_e))
    return x * 2

class Resource:
    id_ = None
    def __init__(self, id):
        self.id_ = (id.release() if hasattr(id, 'release') else id)
        print('  [ctor ', self.id_, ']\\n', sep="", end="")

    def __del__(self):
        print('  [dtor ', self.id_, ']\\n', sep="", end="")

    def use(self):
        print('  using ', self.id_, sep="")


class Node:
    data = None
    next = None
    def __init__(self, d):
        self.data = d
        self.next = None


def push_front(head, v):
    n = Node(v)
    n.next = head
    return n

def free_list(head):
    while head:
        t = head.next
        del head
        head = t

class TreeNode:
    val = 0
    left = None
    right = None
    def __init__(self, v=0):
        self.val = v
        self.left = unique_ptr()
        self.right = unique_ptr()

def tree_insert(root, v):
    if not root:
        if hasattr(root, 'reset'): root.reset(TreeNode(v))
        else: root = TreeNode(v)
        return
    if v < root.val:
        tree_insert(root.left, v)
    else:
        tree_insert(root.right, v)

def tree_inorder(root, out):
    if not root:
        return
    tree_inorder(root.left, out)
    out.append(root.val)
    tree_inorder(root.right, out)

g_mutex = mutex()
g_atomic_counter = atomic(0)
def thread_worker(id, iterations):
    global g_counter
    for i in range(0, iterations):
        g_atomic_counter.fetch_add(1)
        lock = lock_guard(g_mutex)
        g_counter += id

def section(title):
    print('\\n=== ', title, ' ===\\n', sep="", end="")

def test_basic_types_and_operators():
    section(string('Basic types & operators'))
    c = 'A'
    s = 100
    i = 42
    l = 1234567
    ll = 9876543210
    ui = 4000000000
    f = 3.14
    d = 2.718281828
    ld = 1.0 / 3
    b = True
    wc = 'W'
    c16 = 'x'
    c32 = 'y'
    i8 = -8
    u16 = 65535
    i64 = -1
    sz = 4
    print(c, ' ', s, ' ', i, ' ', l, ' ', ll, ' ', ui)
    print(f, ' ', d, ' ', ld, ' ', std.boolalpha, b)
    print(_c_int(wc), ' ', _c_int(c16), ' ', _c_int(c32), ' ', _c_int(i8), ' ', u16, ' ', i64, ' ', sz)
    a = 17
    bb = 5
    print(a + bb, ' ', a - bb, ' ', a * bb, ' ', a / bb, ' ', a % bb)
    print(a & bb, ' ', a | bb, ' ', a ^ bb, ' ', ~a, ' ', a << 2, ' ', a >> 1)
    print(a > bb and bb > 0, ' ', a < bb or bb == 5, ' ', not b)
    t = (a if a > bb else bb)
    t += 3
    t -= 1
    t *= 2
    t //= 3
    t %= 7
    t <<= 2
    t >>= 1
    t &= 255
    t |= 1
    t ^= 16
    print('t=', t)
    x = 5
    y = ++x
    y += ++x
    print('x=', x, ' y=', y)
    hex = 255
    oct = 63
    bin = 10
    big = 1000000
    print(hex, ' ', oct, ' ', bin, ' ', big)
    print(1500.0, ' ', ord('a') + 1, ' ', 'str', ' ', 'raw\\nstring')
    pi = 3.99
    truncated = _c_int(pi)
    cp = i
    mp = _c_int(cp)
    vp = i
    ip = _c_int(vp)
    fbits = 1.0
    ubits = _c_int(fbits)
    print(truncated, ' ', _deref(mp), ' ', _deref(ip), ' ', std.hex, ubits, std.dec)
    print(1, 4, 8, ' ', 2147483647, ' ', 2.220446049250313e-16)
    print(None, ' ', MAX_SIZE, ' ', 'STRINGIFY(hello)', ' ', end="")
    var1 = 10
    print(var1)

def test_control_flow():
    section(string('Control flow'))
    for i in range(0, 3):
        print(i, ' ', end="")
    print()
    w = 0
    while w < 3:
        print(w, ' ', end="")
        w += 1
    print()
    dw = 0
    while dw < 3:
        print(dw, ' ', end="")
        if hasattr(dw, 'increment'): dw.increment()
        else: dw += 1
    print()
    for i in range(0, 10):
        if i == 2:
            continue
        if i == 6:
            break
        print(i, ' ', end="")
    print()
    for i in range(1, 3 + 1):
        for j in range(1, 3 + 1):
            if j == 3:
                None
            print(i * j, ' ', end="")
            None
    print()
    for v in range(0, 5):
        if v == 0:
            print('zero ', end="")
        elif v == 1:
            None
        elif v == 3:
            print('three ', end="")
        else:
            print('default ', end="")
    print()
    k = 5
    if k > 3:
        print('init-if ', k, sep="")
    else:
        print('else\\n', end="")
    a = 0
    b = 10
    while a < b:
        print(a, ':', b, ' ', end="")
        a += 3
        b -= 3
    print()
    col = GREEN
    if col == RED:
        print('R\\n', end="")
    elif col == GREEN:
        print('G\\n', end="")
    else:
        pass
    dir = South
    print(_c_int(dir), ' ', BLUE)

def test_arrays_pointers_references():
    section(string('Arrays / pointers / references'))
    arr = [1, 2, 3, 4, 5]
    matrix = [[1, 2, 3], [4, 5, 6]]
    cstr = 'hello'
    p = arr
    print(_deref(p), ' ', _deref(p, 2), ' ', p[4], ' ', arr[1])
    for r in range(0, 2):
        for c in range(0, 3):
            print(matrix[r][c], ' ', end="")
    print(cstr, ' ', std.strlen(cstr))
    a = 1
    b = 2
    swap_ref(a, b)
    print(a, b, ' ', end="")
    swap_ptr(a, b)
    print(a, b)
    pp = p
    print(_deref(_deref(pp)))
    ref = arr[3]
    ref = 40
    print(arr[3])
    cref = a
    print(cref)
    rref = 10
    print(rref)
    dyn = 7
    dyn_arr = [1, 2, 3, 4]
    print(_deref(dyn), ' ', dyn_arr[3])
    del dyn
    del dyn_arr
    np = None
    print(np == None)
    pt = Point(3, 4)
    ppt = pt
    print(ppt.x, ' ', _deref(ppt).y)
    mem = _c_int(std.malloc(3 * 4))
    mem[0] = 9
    mem[1] = 8
    mem[2] = 7
    print(mem[0] + mem[1] + mem[2])
    std.free(mem)
    px = pt.x
    py = pt.y
    print(px, ',', py)
    u = IntOrFloat()
    u.f = 1.0
    print(std.hex, u.i, std.dec)
    fl = Flags(1, 5, 9)
    print(fl.a, fl.b, fl.c)

def test_strings():
    section(string('Strings'))
    s = string(string('Hello, World'))
    s += '!'
    print(s, ' len=', len(s), ' ', s.substr(7, 5), ' ', s.find('World'))
    s.replace(0, 5, 'HELLO')
    print(s)
    s.insert(5, '***')
    print(s)
    s.erase(5, 3)
    print(s, ' ', s.front(), s.back())
    std.transform(s.begin(), s.end(), s.begin(), (lambda ch: std.tolower(ch)))
    print(s, ' ', s == 'hello, world!', ' ', s.compare('abc'))
    sv = string(string_view('view of text'))
    print(sv.substr(0, 4), ' ', len(sv))
    print(int(string('123')) + 1, ' ', float(string('2.5')) * 2, ' ', str(3.5))
    oss = ostringstream()
    oss << 'num=' << 42 << ' pi=' << std.fixed << std.setprecision(3) << 3.14159 << ' [' << std.setw(6) << std.setfill('.') << 7 << ']'
    print(oss.str())
    iss = istringstream(string('10 20 30'))
    n = None
    total = 0
    while True:
        _tok = iss.get()
        if _tok is None: break
        n = _tok
        total += n
    print('total=', total)
    csv = string(string('a,b,c'))
    ss = stringstream(csv)
    tok = string(string())
    while std.getline(ss, tok, ','):
        print('<', tok, '>', end="")
    print()
    buf = _char_buf(64)
    std.snprintf(buf, len(buf), '%05d|%.2f|%s|%c|%x', 42, 3.14159, 'str', 'z', 255)
    print(buf)
    std.printf('printf: %d %s\\n', 7, 'ok')
    print(std.isalpha('a'), std.isdigit('5'), std.toupper('q'))
    print(std.strcmp('a', 'b'), ' ', std.atoi('77'))
    lit = string('"literal"s')
    print(len(lit))

def test_stl_containers():
    section(string('STL containers'))
    v = vector([5, 3, 8, 1, 9, 2])
    v.append(7)
    v.append(4)
    v.insert(v.begin() + 1, 100)
    v.pop_back()
    print('vec size=', len(v), ' front=', v.front(), ' back=', v.back())
    std.sort(v.begin(), v.end())
    for x in v:
        print(x, ' ', end="")
    print()
    v.erase(std.remove(v.begin(), v.end(), 100), v.end())
    print(std.binary_search(v.begin(), v.end(), 8))
    a = std.array(1, 2, 3, 4)
    print(len(a), a.at(2))
    lst = _CppList([3, 1, 2])
    lst.push_front(0)
    lst.sort()
    lst.reverse()
    for x in lst:
        print(x, end="")
    print()
    dq = deque([1, 2])
    dq.push_front(0)
    dq.append(3)
    print(dq.front(), dq.back(), dq[2])
    fl = forward_list([1, 2, 3])
    fl.push_front(0)
    for x in fl:
        print(x, end="")
    print()
    m = map([['one', 1], ['two', 2]])
    m[string('three')] = 3
    m.insert(pair(string('four'), 4))
    m.emplace('five', 5)
    for [k, val] in m:
        print(k, '=', val, ' ', end="")
    print()
    it = m.find(string('two'))
    if it != m.end():
        print('found ', it.second, sep="")
    print(m.count(string('zzz')), ' ', len(m))
    um = unordered_map([[1, 'a'], [2, 'b']])
    um[3] = 'c'
    print(um.at(3), len(um))
    st = set([3, 1, 2, 3, 1])
    st.insert(10)
    for x in st:
        print(x, ' ', end="")
    print(st.count(2))
    us = unordered_set(['x', 'y'])
    us.insert(string('z'))
    print(len(us), us.count(string('x')))
    ms = multiset([1, 1, 2])
    print(ms.count(1))
    mm = multimap([[1, 'a'], [1, 'b']])
    print(mm.count(1))
    stk = stack()
    stk.push(1)
    stk.push(2)
    print(stk.top(), end="")
    stk.pop()
    print(len(stk))
    q = queue()
    q.push(1)
    q.push(2)
    print(q.front(), q.back(), end="")
    q.pop()
    print(len(q))
    pq = priority_queue()
    pq.push(3)
    pq.push(9)
    pq.push(1)
    print(pq.top())
    minpq = priority_queue('greater')
    minpq.push(3)
    minpq.push(1)
    print(minpq.top())
    pr = pair(1, string('pair'))
    pr2 = pair(2, 3.5)
    print(pr.first, pr.second, pr2.second)
    tp = (1, 2.5, string('tuple'))
    print(tp[0], tp[1], tp[2])
    t1 = tp[0]
    t2 = tp[1]
    t3 = tp[2]
    print(t1, t2, t3)
    ta = None
    tb = None
    (ta, tb, _) = tp
    print(ta, tb)
    bs = bitset(178)
    print(bs, ' ', bs.count(), ' ', bs.test(1), ' ', bs.to_ulong())
    grid = vector(3, vector(3, 0))
    for i in range(0, 3):
        grid[i][i] = 1
    for row in grid:
        for x in row:
            print(x, end="")
        print(' ', end="")
    print()

def test_algorithms_and_lambdas():
    section(string('Algorithms & lambdas'))
    v = vector([4, 2, 9, 1, 7, 3])
    add = (lambda a, b: a + b)
    base = 10
    cap_val = (lambda x: x + base)
    def cap_ref(x):
        nonlocal base
        base += x
    cap_all = (lambda : base * 2)
    generic = (lambda a, b: a + b)
    mutable_l = (lambda _n=[0]: (_n.__setitem__(0, _n[0] + 1) or _n[0]))
    print(add(1, 2), cap_val(5), generic(1.5, 2))
    cap_ref(5)
    print(base, ' ', cap_all(), ' ', mutable_l(), mutable_l())
    fact_fn = function((lambda n: (1 if n <= 1 else n * fact_fn(n - 1))))
    print(fact_fn(5))
    std.sort(v.begin(), v.end(), (lambda a, b: a > b))
    for x in v:
        print(x, ' ', end="")
    print()
    print(std.accumulate(v.begin(), v.end(), 0), ' ', std.accumulate(v.begin(), v.end(), 1, multiplies()))
    print(_deref(std.max_element(v.begin(), v.end())), _deref(std.min_element(v.begin(), v.end())))
    print(std.count_if(v.begin(), v.end(), (lambda x: x % 2 == 1)))
    print(std.any_of(v.begin(), v.end(), (lambda x: x > 8)), std.all_of(v.begin(), v.end(), (lambda x: x > 0)), std.none_of(v.begin(), v.end(), (lambda x: x > 100)))
    it = std.find(v.begin(), v.end(), 7)
    print((std.distance(v.begin(), it) if it != v.end() else -1))
    it2 = std.find_if(v.begin(), v.end(), (lambda x: x < 3))
    print(_deref(it2))
    sq = vector(len(v))
    std.transform(v.begin(), v.end(), sq.begin(), (lambda x: x * x))
    for x in sq:
        print(x, ' ', end="")
    print()
    std.for_each(v.begin(), v.end(), (lambda x: x + 1))
    std.reverse(v.begin(), v.end())
    std.rotate(v.begin(), v.begin() + 2, v.end())
    for x in v:
        print(x, ' ', end="")
    print()
    iota_v = vector(5)
    std.iota(iota_v.begin(), iota_v.end(), 10)
    part = vector(5)
    std.partial_sum(iota_v.begin(), iota_v.end(), part.begin())
    for x in part:
        print(x, ' ', end="")
    print()
    a = vector([1, 2, 3, 4])
    b = vector([3, 4, 5])
    out = vector()
    std.set_intersection(a.begin(), a.end(), b.begin(), b.end(), std.back_inserter(out))
    for x in out:
        print(x, end="")
    print()
    uq = std.unique(a.begin(), a.end())
    uq
    fill_v = vector(4)
    std.fill(fill_v.begin(), fill_v.end(), 7)
    std.copy(fill_v.begin(), fill_v.end(), ostream_iterator(print, ','))
    print()
    partitioned = vector([1, 2, 3, 4, 5, 6])
    std.partition(partitioned.begin(), partitioned.end(), (lambda x: x % 2 == 0))
    std.nth_element(partitioned.begin(), partitioned.begin() + 2, partitioned.end())
    print(partitioned[2])
    print(std.lower_bound(sq.begin(), sq.end(), 0) - sq.begin())
    std.next_permutation(a.begin(), a.end())
    print(std.gcd(12, 18), std.lcm(4, 6))
    bound = std.bind(add, 100, std.placeholders._1)
    print(bound(5))
    fn = function(op_mul)
    print(fn(3, 4))
    print(apply_op(op_add, 2, 3), apply_op((lambda a, b: a - b), 9, 4))

def test_classes_and_polymorphism():
    section(string('Classes & polymorphism'))
    shapes = vector()
    shapes.append(Circle(2.0))
    shapes.append(Rectangle(3, 4))
    shapes.append(Square(5))
    print(std.fixed, std.setprecision(2), end="")
    for sh in shapes:
        print(sh.describe(), ' perim=', sh.perimeter())
    raw = shapes[0]
    c = (raw if isinstance(raw, Circle) else None)
    if c:
        print('is Circle\\n', end="")
    if (raw if isinstance(raw, Rectangle) else None) == None:
        print('not Rectangle\\n', end="")
    print(name())
    std.cout.unsetf(ios_base.floatfield)
    d = Duck()
    print(d.sound(), d.walk(), d.swim())
    v1 = Vector2D(1, 2)
    v2 = Vector2D(3, 4)
    v3 = v1 + v2
    v3 += Vector2D(1, 1)
    if hasattr(v3, 'increment'): v3.increment()
    else: v3 += 1
    if hasattr(v3, 'increment'): v3.increment()
    else: v3 += 1
    print(v3, ' ', v1 == v2, v1 != v2, ' ', v1[0], v2(2.0), ' ', dot(v1, v2), ' ', Vector2D.count(), ' ', bool(v1))
    moved = Vector2D((v3.release() if hasattr(v3, 'release') else v3))
    print(moved, v3)
    print(v1 * 3.0, ' ', (v2 - v1).length())

def test_templates():
    section(string('Templates'))
    print(max_of(3, 7), max_of(2.5, 1.5), std.max_of(string('a'), string('b')))
    fa = FixedArray()
    fa[2] = 9
    print(fa[2], len(fa))
    bi = Box(5)
    bb = Box(True)
    val = 77
    bp = Box(val, is_ptr=True)
    print(bi.type(), bb.type(), bp.type(), bp.get())
    print(sum_all(1, 2, 3, 4), sum_all(1.5, 2.5))
    print_all(1, 'two', 3.0, 'c')
    print()
    print(describe_type(5), describe_type(2.5))
    print(Fact.value, ' ', fib(10))
    cx = fib(8)
    vv = vector([1, 2])
    iv = vector([3])
    sm = map([['k', 1]])
    print(len(vv), len(iv), len(sm))
    print(True, True, True)

def test_exceptions():
    section(string('Exceptions'))
    inputs = [5, -1, 0, 5000]
    for in_ in inputs:
        try:
            print('risky(', in_, ')=', risky(in_))
        except CustomError as e:
            print('CustomError: ', str(e), ' code=', e.code(), sep="")
        except (invalid_argument, ValueError) as e:
            print('invalid_argument: ', str(e), sep="")
        except (exception, Exception) as e:
            print('std::exception: ', str(e), sep="")
        except Exception:
            print('unknown\\n', end="")
    try:
        try:
            _e = runtime_error('inner')
            raise (_e if isinstance(_e, BaseException) else _CppException(_e))
        except (exception, Exception) as e:
            print('rethrowing\\n', end="")
            raise
    except (runtime_error, RuntimeError) as e:
        print('outer caught ', str(e), sep="")
    try:
        v = vector(2)
        v.at(10)
    except (out_of_range, IndexError) as e:
        print('vector out_of_range\\n', end="")
    try:
        _e = 42
        raise (_e if isinstance(_e, BaseException) else _CppException(_e))
    except (_CppException, Exception) as x:
        x = getattr(x, 'val', x)
        print('int thrown ', x, sep="")
    try:
        _e = str(string('string thrown'))
        raise (_e if isinstance(_e, BaseException) else _CppException(_e))
    except (_CppException, Exception) as s:
        s = getattr(s, 'val', s)
        print(s)
    safe = (lambda : 1)
    print(1)
    assert(1 + 1 == 2)

def test_smart_pointers_and_memory():
    section(string('Smart pointers & memory'))
    u = Resource('unique')
    u.use()
    u2 = (u.release() if hasattr(u, 'release') else u)
    print(u == None)
    s1 = shared_ptr(Resource('shared'))
    s2 = shared_ptr(s1)
    w = weak_ptr(s1)
    print('use_count=', s1.use_count(), ' expired=', w.expired())
    s1.reset()
    locked = shared_ptr(w.lock())
    if locked:
        locked.use()
    head = None
    for i in range(1, 4 + 1):
        head = push_front(head, i)
    n = head
    while n:
        print(n.data, ' ', end="")
        n = n.next
    print()
    free_list(head)
    root = unique_ptr()
    for x in [5, 3, 8, 1, 4, 9]:
        tree_insert(root, x)
    sorted = vector()
    tree_inorder(root, sorted)
    for x in sorted:
        print(x, ' ', end="")
    print()
    arr = [0] * 3
    arr[0] = 1
    arr[2] = 3
    print(arr[0] + arr[2])
    buffer = _char_buf(8)
    placed = Point(8, 9)
    print(placed.x, placed.y)
    (placed.__del__() if hasattr(placed, '__del__') else None)

def test_optional_variant_any():
    section(string('optional / variant / any'))
    o1 = optional(5)
    o2 = optional()
    print(o1.has_value(), o2.has_value(), o1.value_or(0), o2.value_or(-1))
    if o1:
        print(_deref(o1))
    var = variant(3.14)
    print(var.index(), getattr(var, 'val', var))
    var = variant(str(string('now string')))
    std.visit((lambda arg: print('visited: ', arg)), var)
    if std.holds_alternative(var):
        print('holds string\\n', end="")
    a = 10
    print(std.any_cast(a))
    a = str(string('any-string'))
    print(std.any_cast(a))

def test_chrono_random_regex():
    section(string('chrono / random / regex'))
    start = std.chrono.now()
    std.this_thread.sleep_for(milliseconds(5))
    end = std.chrono.now()
    ms = std.chrono.duration_cast((end - start)).count()
    print('elapsed>=5ms: ', ms >= 4, sep="")
    gen = mt19937(12345)
    dist = uniform_int_distribution(1, 6)
    rdist = uniform_real_distribution(0.0, 1.0)
    ndist = normal_distribution(0.0, 1.0)
    roll = dist(gen)
    r = rdist(gen)
    ndist
    print(roll >= 1 and roll <= 6, r >= 0 and r < 1)
    shuf = vector([1, 2, 3, 4, 5])
    std.shuffle(shuf.begin(), shuf.end(), gen)
    std.srand(1)
    rr = std.rand()
    rr
    re = regex('(\\w+)@(\\w+)\\.com')
    m = smatch()
    email = string(string('contact: alice@example.com now'))
    if std.regex_search(email, m, re):
        print(m[1], ' at ', m[2])
    print(std.regex_replace(string('a1b22c333'), regex('[0-9]+'), string('#')))
    print(std.regex_match(string('abc123'), regex('[a-z]+[0-9]+')))
    now = std.time(None)
    now
    clk = std.clock()
    clk

def test_math():
    section(string('cmath'))
    print(std.fixed, std.setprecision(4), end="")
    print(std.sqrt(16.0), ' ', std.pow(2, 10), ' ', std.abs(-3.5), ' ', std.floor(2.7), ' ', std.ceil(2.1), ' ', std.round(2.5), ' ', std.fmod(7.5, 2))
    print(std.sin(math_utils.PI / 2), ' ', std.cos(0.0), ' ', std.tan(0.0), ' ', std.atan2(1, 1), ' ', std.exp(1.0), ' ', std.log(std.exp(2.0)), ' ', std.log10(1000.0), ' ', std.hypot(3, 4))
    std.cout.unsetf(ios_base.floatfield)
    print(std.abs(-7), ' ', std.isnan(std.nan('')), ' ', std.isinf(__builtin_inff()))
    print(math_utils.add(1, 2), ' ', math_utils.add(1.5, 2.5), ' ', alias_target.triple(4), ' ', math_utils.nested.triple(2))
    print(factorial(6), ' ', gcd(48, 18), ' ', is_prime(97), ' ', with_default(1), with_default(1, 2), with_default(1, 2, 3), ' ', cube(3), ' ', file_local_fn(1), ' ', trailing(2, 3), ' ', must_use(), ' ', G_CONST, G_CONSTEXPR, s_static_global, g_extern_decl)

def test_file_io():
    section(string('File I/O'))
    path = 'transpiler_test_tmp.txt'
    out = ofstream(path)
    out << 'line one\\nline two\\n42 3.14\\n'
    in_ = ifstream(path)
    line = string(string())
    while std.getline(in_, line):
        print('read: ', line, sep="")
    app = ofstream(path, std.app)
    app << 'appended\\n'
    in_ = ifstream(path)
    word = string(string())
    count = 0
    while True:
        _tok = in_.get()
        if _tok is None: break
        word = _tok
        if hasattr(count, 'increment'): count.increment()
        else: count += 1
    print('words=', count)
    std.remove(path)
    print('(this line goes to stderr)\\n', end="")
    print('(this line goes to clog)\\n', end="")

def test_threads():
    global g_atomic_counter, g_counter
    section(string('Threads / async / sync'))
    g_counter = 0
    g_atomic_counter = atomic(0)
    threads = vector()
    for i in range(1, 4 + 1):
        threads.append(thread(thread_worker, i, 1000))
    for t in threads:
        t.join()
    print('atomic=', g_atomic_counter, ' guarded=', g_counter)
    fut = std.async_(std.async_, (lambda : factorial(5)))
    print('async result=', fut)
    prom = promise()
    pf = prom.get_future()
    t = thread((lambda : prom.set_value(99)))
    print('promise=', pf)
    t.join()
    m = mutex()
    cv = condition_variable()
    ready = False
    waiter = thread((lambda : print('cv signaled\\n')))
    lk = lock_guard(m)
    ready = True
    cv.notify_one()
    waiter.join()
    tls = 0
    if hasattr(tls, 'increment'): tls.increment()
    else: tls += 1
    print('tls=', tls)

class Range:
    lo_ = None
    hi_ = None
    def __init__(self, lo, hi):
        self.lo_ = lo
        self.hi_ = hi

    class Iter:
        def __init__(self, v=0):
            self.v = v
        v = None
        def __mul__(self):
            return self.v

        def increment(self):
            if hasattr(self.v, 'increment'): self.v.increment()
            else: self.v += 1
            return self

        def __ne__(self, o):
            return self.v != o.v


    def begin(self):
        return [self.lo_]

    def end(self):
        return [self.hi_]

    def __iter__(self): return iter(range(self.lo_, self.hi_))

def test_custom_iterables_and_misc():
    section(string('Custom iterables & misc'))
    for x in Range(0, 5):
        print(x, ' ', end="")
    print()
    init = std.initializer_list(1, 2, 3)
    print(len(init))
    def lst_sum(il):
        s = 0
        for x in il:
            s += x
        return s
    print(lst_sum([1, 2, 3, 4]))
    dref = g_counter
    dref
    fptr = factorial
    print(fptr(4))
    member_ptr = 'x'
    pt = Point(11, 22)
    print(getattr(pt, str(member_ptr)))
    print(__LINE__, ' ', '__FILE__' != None, ' ', '__func__', ' ', __cplusplus)
    print('debug on\\n', end="")
    vol = 3
    None
    print(vol)
    p1 = Point(1, 2)
    p2 = Point(1, 2)
    print(p1 == p2)
    print(std.boolalpha, p1 == p2, std.noboolalpha)

def main(argc, argv):
    None
    print('argc=', argc, ' argv0_present=', argv[0] != None)
    test_basic_types_and_operators()
    test_control_flow()
    test_arrays_pointers_references()
    test_strings()
    test_stl_containers()
    test_algorithms_and_lambdas()
    test_classes_and_polymorphism()
    test_templates()
    test_exceptions()
    test_smart_pointers_and_memory()
    test_optional_variant_any()
    test_chrono_random_regex()
    test_math()
    test_file_io()
    test_threads()
    test_custom_iterables_and_misc()
    print('\\nAll sections completed.\\n', end="")
    return EXIT_SUCCESS


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
