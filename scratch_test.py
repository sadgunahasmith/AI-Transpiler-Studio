class string:
    npos = -1
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
npos = -1
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
def find(first, last, val=None):
    if hasattr(first, 'find') and not hasattr(first, '_vec'): return first.find(last)
    vec = getattr(first, '_vec', None)
    if vec is not None:
        idx1 = first._idx; idx2 = last._idx if hasattr(last, '_idx') else len(vec)
        for i in range(idx1, idx2):
            if vec[i] == val: return type(first)(vec, i)
        return type(first)(vec, idx2)
    return last
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
fixed = ''
def setprecision(n): return ''

def _deref(x, offset=0):
    if hasattr(x, '_val') and hasattr(x, 'has_value'): return x._val
    if hasattr(x, '__getitem__'): return x[offset]
    return x

def _set_deref(x, val, offset=0):
    if hasattr(x, '__setitem__'): x[offset] = val
    return val

# using namespace 
# Namespace: campus
MAX_LOANS = 3
FINE_PER_DAY = 2.5
class Category:
    Science = 0
    Fiction = 1
    History = 2
    Computing = 3
    Arts = 4
Science = Category.Science
Fiction = Category.Fiction
History = Category.History
Computing = Category.Computing
Arts = Category.Arts

def categoryName(c):
    if c == Science:
        return string('Science')
    elif c == Fiction:
        return string('Fiction')
    elif c == History:
        return string('History')
    elif c == Computing:
        return string('Computing')
    else:
        return string('Arts')

class Book:
    id = None
    title = None
    author = None
    category = None
    copies = None
    borrowed = None
    rating = None
    def __init__(self, i, t, a, c, n, r):
        self.id = i
        self.title = t
        self.author = a
        self.category = c
        self.copies = n
        self.borrowed = 0
        self.rating = r

    def available(self):
        return self.copies - self.borrowed

    def __lt__(self, other):
        return self.id < other.id

    def description(self):
        out = ostringstream()
        out << self.id << ' | ' << self.title << ' | ' << self.author
        out << ' | ' << categoryName(self.category) << ' | '
        out << self.available() << '/' << self.copies
        return out.str()


class Person:
    id_ = None
    name_ = None
    def __init__(self, id, name):
        self.id_ = id
        self.name_ = name

    def __del__(self):
        pass

    def id(self):
        return self.id_

    def name(self):
        return string(self.name_)

    def role(self):
        pass

    def print(self):
        print(self.role(), ' #', self.id_, ' ', self.name_)


class Loan:
    bookId = None
    days = None
    returned = None
    def __init__(self, b, d):
        self.bookId = b
        self.days = d
        self.returned = False


class Member(Person):
    loans_ = None
    points_ = None
    def __init__(self, id, name):
        super().__init__(id, name)
        self.points_ = 0
        self.loans_ = vector()

    def role(self):
        return string('Member')

    def canBorrow(self):
        return self.activeLoans() < MAX_LOANS

    def activeLoans(self):
        count = 0
        for loan in self.loans_:
            if not loan.returned:
                if hasattr(count, 'increment'): count.increment()
                else: count += 1
        return count

    def borrow(self, bookId, days):
        if not self.canBorrow():
            _e = runtime_error('Loan limit reached')
            raise (_e if isinstance(_e, BaseException) else _CppException(_e))
        self.loans_.append(Loan(bookId, days))
        self.points_ += 10

    def giveBack(self, bookId):
        for loan in self.loans_:
            if loan.bookId == bookId and not loan.returned:
                loan.returned = True
                return True
        return False

    def fine(self):
        total = 0
        for loan in self.loans_:
            if not loan.returned and loan.days > 14:
                total += (loan.days - 14) * FINE_PER_DAY
        return total

    def points(self):
        return self.points_

    def loans(self):
        return self.loans_

    def print(self):
        super().print()
        print('  Active loans: ', self.activeLoans(), sep="", end="")
        print(' | Points: ', self.points_, sep="", end="")
        print(' | Fine: ', fixed, setprecision(2), self.fine(), sep="")


class Librarian(Person):
    shift_ = None
    def __init__(self, id, name, shift):
        super().__init__(id, name)
        self.shift_ = shift

    def role(self):
        return string('Librarian')

    def shift(self):
        return string(self.shift_)

    def print(self):
        super().print()
        print('  Shift: ', self.shift_, sep="")


class Library:
    def __init__(self, books_=None, members_=None, events_=None):
        self.books_ = books_ if books_ is not None else map()
        self.members_ = members_ if members_ is not None else map()
        self.events_ = events_ if events_ is not None else []
    books_ = None
    members_ = None
    events_ = None
    def addBook(self, b):
        if self.books_.count(b.id):
            _e = invalid_argument('Duplicate book')
            raise (_e if isinstance(_e, BaseException) else _CppException(_e))
        self.books_.emplace(b.id, b)
        self.events_.append('Added book ' + str(b.id))

    def addMember(self, m):
        if self.members_.count(m.id()):
            _e = invalid_argument('Duplicate member')
            raise (_e if isinstance(_e, BaseException) else _CppException(_e))
        self.members_.emplace(m.id(), m)
        self.events_.append('Added member ' + str(m.id()))

    def findBook(self, id):
        it = self.books_.find(id)
        return (None if it == self.books_.end() else it.second)

    def findMember(self, id):
        it = self.members_.find(id)
        return (None if it == self.members_.end() else it.second)

    def findBook(self, id):
        it = self.books_.find(id)
        return (None if it == self.books_.end() else it.second)

    def borrowBook(self, memberId, bookId, days):
        member = self.findMember(memberId)
        book = self.findBook(bookId)
        if not member or not book:
            _e = out_of_range('Unknown ID')
            raise (_e if isinstance(_e, BaseException) else _CppException(_e))
        if book.available() == 0:
            _e = runtime_error('Out of stock')
            raise (_e if isinstance(_e, BaseException) else _CppException(_e))
        member.borrow(bookId, days)
        if hasattr(book.borrowed, 'increment'): book.borrowed.increment()
        else: book.borrowed += 1
        self.events_.append('Borrowed ' + str(bookId))

    def returnBook(self, memberId, bookId):
        member = self.findMember(memberId)
        book = self.findBook(bookId)
        if not member or not book:
            _e = out_of_range('Unknown ID')
            raise (_e if isinstance(_e, BaseException) else _CppException(_e))
        if not member.giveBack(bookId):
            _e = runtime_error('No active loan')
            raise (_e if isinstance(_e, BaseException) else _CppException(_e))
        if hasattr(book.borrowed, 'decrement'): book.borrowed.decrement()
        else: book.borrowed -= 1
        self.events_.append('Returned ' + str(bookId))

    def allBooks(self):
        result = vector()
        for item in self.books_:
            result.append(item.second)
        return vector(result)

    def search(self, text):
        result = vector()
        for item in self.books_:
            b = item.second
            if b.title.find(text) != string.npos or b.author.find(text) != string.npos:
                result.append(b)
        return vector(result)

    def byCategory(self, category):
        result = vector()
        for item in self.books_:
            if item.second.category == category:
                result.append(item.second)
        return vector(result)

    def topRated(self, limit):
        result = self.allBooks()
        sort(result.begin(), result.end(), (lambda a, b: (a.id < b.id if a.rating == b.rating else a.rating > b.rating)))
        if len(result) > limit:
            result.erase(result.begin() + limit, result.end())
        return vector(result)

    def totalCopies(self):
        sum = 0
        for item in self.books_:
            sum += item.second.copies
        return sum

    def totalBorrowed(self):
        sum = 0
        for item in self.books_:
            sum += item.second.borrowed
        return sum

    def averageRating(self):
        if (len(self.books_) == 0):
            return 0.0
        sum = 0
        for item in self.books_:
            sum += item.second.rating
        return sum / len(self.books_)

    def outstandingFines(self):
        sum = 0
        for item in self.members_:
            sum += item.second.fine()
        return sum

    def memberCount(self):
        return len(self.members_)

    def bookCount(self):
        return len(self.books_)

    def events(self):
        return self.events_

    def printMembers(self):
        for item in self.members_:
            item.second.print()

    def printBooks(self):
        for item in self.books_:
            print(item.second.description())

    def saveCatalog(self, filename):
        file = ofstream(filename)
        if not file:
            _e = runtime_error('Cannot create catalog')
            raise (_e if isinstance(_e, BaseException) else _CppException(_e))
        for item in self.books_:
            b = item.second
            file << b.id << ',' << b.title << ',' << b.author << ','
            file << b.copies << ',' << b.borrowed << '\\n'

    def saveEvents(self, filename):
        file = ofstream(filename)
        if not file:
            _e = runtime_error('Cannot create event log')
            raise (_e if isinstance(_e, BaseException) else _CppException(_e))
        for event in self.events_:
            file << event << '\\n'


def maximumOf(values):
    if (len(values) == 0):
        _e = invalid_argument('Empty collection')
        raise (_e if isinstance(_e, BaseException) else _CppException(_e))
    return _deref(max_element(values.begin(), values.end()))

def meanOf(values):
    if (len(values) == 0):
        return 0.0
    return accumulate(values.begin(), values.end(), 0.0) / len(values)

def uniqueSorted(data):
    sort(data.begin(), data.end())
    data.erase(unique(data.begin(), data.end()), data.end())
    return vector(data)

def wordHistogram(text):
    input = istringstream(text)
    counts = map()
    word = string(string())
    while True:
        _tok = input.get()
        if _tok is None: break
        word = _tok
        if hasattr(counts[word], 'increment'): counts[word].increment()
        else: counts[word] += 1
    return map(counts)

def rollingTotals(values):
    totals = vector(len(values))
    partial_sum(values.begin(), values.end(), totals.begin())
    return vector(totals)

def evenSquares(values):
    result = vector()
    for x in values:
        if x % 2 == 0:
            result.append(x * x)
    return vector(result)

def printNumbers(values, label):
    print(label, ':', end="")
    for value in values:
        print(' ', value, sep="", end="")
    print()

def printBooks(books, label):
    print(label, ' (', len(books), ')\\n', end="")
    for b in books:
        print('  ', b.description(), sep="")

def populate(library):
    library.addBook(Book(101, string('C++ Fundamentals'), string('Ada'), Computing, 4, 4.8))
    library.addBook(Book(102, string('Algorithms'), string('Knuth'), Computing, 3, 4.9))
    library.addBook(Book(103, string('Physics'), string('Feynman'), Science, 5, 4.7))
    library.addBook(Book(104, string('Astronomy'), string('Carl'), Science, 2, 4.3))
    library.addBook(Book(105, string('Ancient Worlds'), string('Mira'), History, 3, 4.1))
    library.addBook(Book(106, string('Modern History'), string('Lena'), History, 2, 4.0))
    library.addBook(Book(107, string('Stories'), string('Orwell'), Fiction, 6, 4.6))
    library.addBook(Book(108, string('Poetry'), string('Rita'), Arts, 3, 4.2))
    library.addBook(Book(109, string('Machine Learning'), string('Ravi'), Computing, 2, 4.5))
    library.addBook(Book(110, string('Painting'), string('Nora'), Arts, 4, 4.4))
    library.addMember(Member(1, string('Alice')))
    library.addMember(Member(2, string('Bob')))
    library.addMember(Member(3, string('Charlie')))
    library.addMember(Member(4, string('Diana')))
    library.addMember(Member(5, string('Ethan')))

def runLoans(library):
    library.borrowBook(1, 101, 5)
    library.borrowBook(1, 102, 18)
    library.borrowBook(2, 103, 21)
    library.borrowBook(3, 107, 7)
    library.borrowBook(4, 109, 15)
    library.borrowBook(5, 108, 3)
    print('Borrowed copies: ', library.totalBorrowed(), sep="")
    library.returnBook(3, 107)
    print('After return: ', library.totalBorrowed(), sep="")
    try:
        library.borrowBook(99, 101, 1)
    except (out_of_range, IndexError) as error:
        print('Expected missing member: ', str(error), sep="")
    try:
        library.returnBook(3, 107)
    except (runtime_error, RuntimeError) as error:
        print('Expected repeated return: ', str(error), sep="")

def showAnalytics(library):
    print('=== Library analytics ===\\n', end="")
    print('Books: ', library.bookCount(), sep="")
    print('Members: ', library.memberCount(), sep="")
    print('Copies: ', library.totalCopies(), sep="")
    print('Borrowed: ', library.totalBorrowed(), sep="")
    print('Average rating: ', fixed, setprecision(2), sep="", end="")
    print(library.averageRating())
    print('Fines due: ', library.outstandingFines(), sep="")
    printBooks(library.topRated(3), string('Top rated books'))
    printBooks(library.search(string('History')), string('History title search'))
    printBooks(library.byCategory(Science), string('Science books'))
    print('=== Member records ===\\n', end="")
    library.printMembers()

def algorithmDemos():
    print('=== STL algorithm demonstrations ===\\n', end="")
    values = vector([7, 2, 7, 4, 9, 2, 10, 3, 6, 4])
    printNumbers(values, string('Input'))
    printNumbers(uniqueSorted(vector(values)), string('Unique sorted'))
    printNumbers(rollingTotals(values), string('Running totals'))
    printNumbers(evenSquares(values), string('Even squares'))
    print('Maximum: ', maximumOf(values), sep="")
    print('Mean: ', meanOf(values), sep="")
    print('Count even: ', count_if(values.begin(), values.end(), (lambda x: x % 2 == 0)), sep="")
    copied = vector(len(values))
    transform(values.begin(), values.end(), copied.begin(), (lambda x: x * 3))
    printNumbers(copied, string('Tripled'))
    reverse(copied.begin(), copied.end())
    printNumbers(copied, string('Reversed'))
    histogram = wordHistogram(string('red blue red green blue red'))
    for item in histogram:
        print(item.first, '=', item.second, ' ', end="")
    print()

def containerDemos():
    print('=== Additional containers ===\\n', end="")
    doubleEnded = deque([2, 3, 4])
    doubleEnded.push_front(1)
    doubleEnded.append(5)
    print('Deque front/back: ', doubleEnded.front(), sep="", end="")
    print('/', doubleEnded.back())
    pending = queue()
    pending.push(string('request-A'))
    pending.push(string('request-B'))
    while not (len(pending) == 0):
        print('Queue: ', pending.front(), sep="")
        pending.pop()
    history = stack()
    for i in range(1, 3 + 1):
        history.push(i * 10)
    while not (len(history) == 0):
        print('Stack: ', history.top(), sep="")
        history.pop()
    ids = set([4, 2, 2, 1, 3])
    print('Unique IDs:', end="")
    for id in ids:
        print(' ', id, sep="", end="")
    print()

def pointerAndPolymorphismDemo():
    print('=== Smart pointers and polymorphism ===\\n', end="")
    people = vector()
    people.append(Member(11, 'Nina'))
    people.append(Librarian(20, 'Oliver', 'Morning'))
    people.append(Member(12, 'Priya'))
    for person in people:
        person.print()
    counter = make_shared(5)
    alias = shared_ptr(counter)
    _set_deref(alias, 3)
    print('Shared value: ', _deref(counter), sep="")
    print('Reference count: ', counter.use_count(), sep="")

def exceptionDemo():
    print('=== Exception handling ===\\n', end="")
    data = vector([10, 20, 30])
    try:
        print('Value at index 1: ', data.at(1), sep="")
        print(data.at(20))
    except (out_of_range, IndexError) as error:
        print('Caught range exception: ', str(error), sep="")
    try:
        empty = vector()
        print(maximumOf(empty))
    except (invalid_argument, ValueError) as error:
        print('Caught invalid argument: ', str(error), sep="")

def exportReports(library):
    print('=== File output ===\\n', end="")
    try:
        library.saveCatalog(string('library_catalog.csv'))
        library.saveEvents(string('library_events.txt'))
        print('Saved catalog and event log\\n', end="")
    except (exception, Exception) as error:
        print('File error: ', str(error), sep="")

class campus:
    MAX_LOANS = MAX_LOANS
    FINE_PER_DAY = FINE_PER_DAY
    Category = Category
    categoryName = categoryName
    Book = Book
    Person = Person
    Loan = Loan
    Member = Member
    Librarian = Librarian
    Library = Library
    maximumOf = maximumOf
    meanOf = meanOf
    uniqueSorted = uniqueSorted
    wordHistogram = wordHistogram
    rollingTotals = rollingTotals
    evenSquares = evenSquares
    printNumbers = printNumbers
    printBooks = printBooks
    populate = populate
    runLoans = runLoans
    showAnalytics = showAnalytics
    algorithmDemos = algorithmDemos
    containerDemos = containerDemos
    pointerAndPolymorphismDemo = pointerAndPolymorphismDemo
    exceptionDemo = exceptionDemo
    exportReports = exportReports

def main():
    print('UNIVERSALTRANSPILER C++17 STRESS TEST\\n', end="")
    library = Library()
    populate(library)
    runLoans(library)
    showAnalytics(library)
    algorithmDemos()
    containerDemos()
    pointerAndPolymorphismDemo()
    exceptionDemo()
    exportReports(library)
    print('Completed successfully\\n', end="")
    return 0


if __name__ == "__main__":
    main()
