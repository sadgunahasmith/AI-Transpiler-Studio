// --- C++ Standard Library & Runtime Shim for JavaScript ---
let fs;
try { fs = require("fs"); } catch (e) { fs = null; }
if (typeof Error.prototype.what !== "function") {
  Error.prototype.what = function() { return this.message; };
}
class _CppException extends Error {
  constructor(m = "") {
    const msg = (m && m._s !== undefined) ? m._s : String(m);
    super(msg);
    this.name = "exception";
  }
  what() { return this.message; }
}
class _CppInvalidArgument extends _CppException { constructor(m = "") { super(m); this.name = "invalid_argument"; } }
class _CppOutOfRange extends _CppException { constructor(m = "") { super(m); this.name = "out_of_range"; } }
class _CppRuntimeError extends _CppException { constructor(m = "") { super(m); this.name = "runtime_error"; } }
function invalid_argument(m) { return new _CppInvalidArgument(m); }
invalid_argument.prototype = _CppInvalidArgument.prototype;
function out_of_range(m) { return new _CppOutOfRange(m); }
out_of_range.prototype = _CppOutOfRange.prototype;
function runtime_error(m) { return new _CppRuntimeError(m); }
runtime_error.prototype = _CppRuntimeError.prototype;
function exception(m) { return new _CppException(m); }
exception.prototype = _CppException.prototype;
function isinstance(obj, cls) {
  if (obj == null) return false;
  if (typeof cls === 'function') return obj instanceof cls;
  return true;
}
function assert(cond, msg = "") { if (!cond) throw new Error("Assertion failed: " + msg); }
function _mixin(Derived, Base) {
  if (typeof Base === "undefined" || !Base || !Base.prototype) return;
  let p = Base.prototype;
  while (p && p !== Object.prototype) {
    for (const prop of Object.getOwnPropertyNames(p)) {
      if (prop !== "constructor" && !(prop in Derived.prototype)) {
        try { Derived.prototype[prop] = p[prop]; } catch (e) {}
      }
    }
    p = Object.getPrototypeOf(p);
  }
}
function section(name) {
  console.log(`\n=== ${String(name)} ===\n`);
}
if (typeof Number.prototype.count !== "function") {
  Number.prototype.count = function() { return this.valueOf(); };
}
function milliseconds(n) { return n; }
function __builtin_inff() { return Infinity; }
function __builtin_nanf() { return NaN; }
function _shift(a, b) {
  if (a && a._parts) {
    a._parts.push(String(b));
    if (a.path && fs) {
      try {
        if (a.mode && String(a.mode).includes("app")) fs.appendFileSync(a.path, String(b));
        else fs.writeFileSync(a.path, a._parts.join(""));
      } catch (e) {}
    }
    return a;
  }
  return a << b;
}
function _add(a, b) {
  if (a && typeof a.operator_add === "function") return a.operator_add(b);
  if (a && a._vec && a._idx !== undefined) return new _VecIter(a._vec, a._idx + Number(b));
  if (b && b._vec && b._idx !== undefined) return new _VecIter(b._vec, Number(a) + b._idx);
  return a + b;
}
function _sub(a, b) {
  if (a && typeof a.operator_sub === "function") return a.operator_sub(b);
  if (a && a._vec && a._idx !== undefined && b && b._vec && b._idx !== undefined) return a._idx - b._idx;
  if (a && a._vec && a._idx !== undefined) return new _VecIter(a._vec, a._idx - Number(b));
  return a - b;
}
function _mul(a, b) {
  if (Array.isArray(a) && typeof b === "number") {
    const res = [];
    for (let i = 0; i < b; i++) res.push(...a);
    return res;
  }
  if (a && typeof a.operator_mul === "function") return a.operator_mul(b);
  return a * b;
}
function _eq(a, b) {
  if (a && typeof a.operator_eq === "function") return a.operator_eq(b);
  if (a && typeof a.get === "function" && b == null) return a.get() == null;
  if (b && typeof b.get === "function" && a == null) return b.get() == null;
  if ((a === 18446744073709551615 && b === -1) || (a === -1 && b === 18446744073709551615)) return true;
  return a == b;
}
function _ne(a, b) {
  if (a && typeof a.operator_ne === "function") return a.operator_ne(b);
  if (a && typeof a.get === "function" && b == null) return a.get() != null;
  if (b && typeof b.get === "function" && a == null) return b.get() != null;
  if ((a === 18446744073709551615 && b === -1) || (a === -1 && b === 18446744073709551615)) return false;
  return a != b;
}
function _not(x) {
  if (x == null) return true;
  if (typeof x === "object") {
    if (typeof x.has_value === "function") return !x.has_value();
    if (typeof x.get === "function") return !x.get();
    if ("_obj" in x) return !x._obj;
    if (typeof x[Symbol.toPrimitive] === "function") {
      const p = x[Symbol.toPrimitive]();
      if (typeof p === "boolean" || typeof p === "number") return !p;
    }
  }
  return !x;
}
function _deref(x) {
  if (x && x._vec && x._idx !== undefined) return x._vec[x._idx];
  if (x && typeof x.get === "function") return x.get();
  if (Array.isArray(x) && x.length > 0) return x[0];
  return x;
}
if (typeof Array.prototype.size !== "function") Array.prototype.size = function() { return this.length; };
if (typeof Array.prototype.empty !== "function") Array.prototype.empty = function() { return this.length === 0; };
if (typeof Array.prototype.front !== "function") Array.prototype.front = function() { return this[0]; };
if (typeof Array.prototype.back !== "function") Array.prototype.back = function() { return this[this.length - 1]; };
if (typeof Array.prototype.push_back !== "function") Array.prototype.push_back = function(v) { this.push(v); };
if (typeof Array.prototype.pop_back !== "function") Array.prototype.pop_back = function() { return this.pop(); };
if (typeof Array.prototype.emplace_back !== "function") Array.prototype.emplace_back = function(...args) { this.push(...args); };
if (typeof Array.prototype.push_front !== "function") Array.prototype.push_front = function(v) { this.unshift(v); };
if (typeof Array.prototype.pop_front !== "function") Array.prototype.pop_front = function() { return this.shift(); };
if (!Object.getOwnPropertyDescriptor(Array.prototype, "first")) {
  Object.defineProperty(Array.prototype, "first", { get() { return this[0]; }, configurable: true });
}
if (!Object.getOwnPropertyDescriptor(Array.prototype, "second")) {
  Object.defineProperty(Array.prototype, "second", { get() { return this[1]; }, configurable: true });
}
class _str_iter {
  constructor(owner, idx) { this.owner = owner; this.idx = idx; }
}
class _CppString {
  constructor(val = "") {
    if (val && val._s !== undefined) this._s = val._s;
    else this._s = (val !== null && val !== undefined) ? String(val) : "";
  }
  toString() { return this._s; }
  valueOf() { return this._s; }
  [Symbol.toPrimitive]() { return this._s; }
  [Symbol.for("nodejs.util.inspect.custom")]() { return this._s; }
  get length() { return this._s.length; }
  size() { return this._s.length; }
  substr(pos, len) {
    const p = Number(pos);
    return new _CppString(len !== undefined ? this._s.substr(p, Number(len)) : this._s.substr(p));
  }
  find(sub, pos = 0) {
    const s = typeof sub === "object" ? sub.toString() : String(sub);
    const idx = this._s.indexOf(s, Number(pos));
    return idx === -1 ? 18446744073709551615 : idx;
  }
  rfind(sub, pos) {
    const s = typeof sub === "object" ? sub.toString() : String(sub);
    return pos !== undefined ? this._s.lastIndexOf(s, Number(pos)) : this._s.lastIndexOf(s);
  }
  replace(pos, count, sub) {
    const p = Number(pos), c = Number(count);
    this._s = this._s.substring(0, p) + String(sub) + this._s.substring(p + c);
    return this;
  }
  insert(pos, sub) {
    const p = Number(pos);
    this._s = this._s.substring(0, p) + String(sub) + this._s.substring(p);
    return this;
  }
  erase(pos = 0, count) {
    const p = Number(pos);
    if (count === undefined) this._s = this._s.substring(0, p);
    else this._s = this._s.substring(0, p) + this._s.substring(p + Number(count));
    return this;
  }
  front() { return this._s[0] || ""; }
  back() { return this._s[this._s.length - 1] || ""; }
  compare(other) {
    const o = String(other);
    return this._s > o ? 1 : this._s < o ? -1 : 0;
  }
  append(other) {
    this._s += (other && other._s !== undefined ? other._s : String(other));
    return this;
  }
  push_back(ch) { this._s += String(ch); }
  c_str() { return this._s; }
  data() { return this._s; }
  clear() { this._s = ""; }
  empty() { return this._s.length === 0; }
  begin() { return new _str_iter(this, 0); }
  end() { return new _str_iter(this, this._s.length); }
}
function string(v = "") { return new _CppString(v); }
_CppString.npos = 18446744073709551615;
string.npos = 18446744073709551615;
const string_view = string;
class _char_buf {
  constructor(size = 64) { this._size = size; this._s = ""; }
  toString() { return this._s; }
  valueOf() { return this._s; }
  get length() { return this._size; }
  set(v) { this._s = String(v); }
}
class _ostringstream {
  constructor() { this._parts = []; }
  str(v) { if (v !== undefined) this._parts = [String(v)]; return this._parts.join(""); }
}
function ostringstream(...args) { return new _ostringstream(...args); }
class _istringstream {
  constructor(text = "") {
    this._tokens = String(text).trim().split(/\s+/).filter(Boolean);
    this._idx = 0;
  }
  get() {
    if (this._idx < this._tokens.length) {
      const val = this._tokens[this._idx++];
      const n = Number(val);
      return !isNaN(n) ? n : val;
    }
    return null;
  }
}
function istringstream(...args) { return new _istringstream(...args); }
class _stringstream {
  constructor(text = "") {
    this._text = String(text);
    this._idx = 0;
    this._parts = text ? [String(text)] : [];
  }
  str(v) {
    if (v !== undefined) { this._text = String(v); this._parts = [this._text]; this._idx = 0; }
    return this._parts.join("");
  }
  getline(delim = "\n") {
    if (this._idx >= this._text.length) return null;
    const d = (delim === "\n" || delim === "\\n") ? "\n" : String(delim);
    const end = this._text.indexOf(d, this._idx);
    let res;
    if (end === -1) {
      res = this._text.slice(this._idx);
      this._idx = this._text.length;
    } else {
      res = this._text.slice(this._idx, end);
      this._idx = end + d.length;
    }
    return res;
  }
}
function stringstream(...args) { return new _stringstream(...args); }
function getline(stream, tok, delim = "\n") {
  const line = stream && typeof stream.getline === "function" ? stream.getline(delim) : null;
  if (line !== null) {
    if (tok && typeof tok === "object" && "_s" in tok) tok._s = line;
    return true;
  }
  return false;
}
class _CppVector extends Array {
  constructor(...args) {
    if (args.length === 1 && typeof args[0] === "number") {
      super(args[0]).fill(0);
    } else if (args.length === 2 && typeof args[0] === "number") {
      super(args[0]).fill(args[1]);
    } else if (args.length === 1 && Array.isArray(args[0])) {
      super(...args[0]);
    } else {
      super(...args);
    }
  }
  push_back(v) { this.push(v); }
  emplace_back(v) { this.push(v); }
  pop_back() { return this.pop(); }
  front() { return this[0]; }
  back() { return this[this.length - 1]; }
  size() { return this.length; }
  empty() { return this.length === 0; }
  at(i) {
    if (i < 0 || i >= this.length) throw new _CppOutOfRange("vector::_M_range_check");
    return this[i];
  }
  insert(pos, val) { const idx = typeof pos === "number" ? pos : (pos && pos.idx !== undefined ? pos.idx : Number(pos)); this.splice(idx, 0, val); }
  erase(pos, last) {
    const idx1 = typeof pos === "number" ? pos : (pos && pos.idx !== undefined ? pos.idx : Number(pos));
    if (last !== undefined) {
      const idx2 = typeof last === "number" ? last : (last && last.idx !== undefined ? last.idx : Number(last));
      this.splice(idx1, idx2 - idx1);
    } else {
      this.splice(idx1, 1);
    }
  }
  push_front(v) { this.unshift(v); }
  pop_front() { return this.shift(); }
  sort(comp) { super.sort(comp || ((a, b) => a - b)); return this; }
  reverse() { super.reverse(); return this; }
  begin() { return new _VecIter(this, 0); }
  end() { return new _VecIter(this, this.length); }
}
class _VecIter {
  constructor(vec, idx) { this._vec = vec; this._idx = idx; }
  valueOf() { return this._idx; }
  [Symbol.toPrimitive](hint) { if (hint === "number" || hint === "default") return this._idx; return (this._vec && this._idx < this._vec.length) ? String(this._vec[this._idx]) : String(this._idx); }
  toString() { return String((this._vec && this._idx < this._vec.length) ? this._vec[this._idx] : this._idx); }
  [Symbol.for("nodejs.util.inspect.custom")]() { return (this._vec && this._idx < this._vec.length) ? this._vec[this._idx] : this._idx; }
}
function vector(...args) { return new _CppVector(...args); }
const deque = vector;
const list = vector;
const forward_list = vector;
class _CppStack {
  constructor() { this._items = []; }
  push(x) { this._items.push(x); }
  pop() { return this._items.pop(); }
  top() { return this._items[this._items.length - 1]; }
  size() { return this._items.length; }
  empty() { return this._items.length === 0; }
}
function stack(...args) { return new _CppStack(...args); }
class _CppQueue {
  constructor() { this._items = []; }
  push(x) { this._items.push(x); }
  pop() { return this._items.shift(); }
  front() { return this._items[0]; }
  back() { return this._items[this._items.length - 1]; }
  size() { return this._items.length; }
  empty() { return this._items.length === 0; }
}
function queue(...args) { return new _CppQueue(...args); }
class _CppPriorityQueue {
  constructor(pred = null) {
    this._items = [];
    this._comp = typeof pred === "function" ? pred : (a, b) => b - a;
  }
  push(x) { this._items.push(x); this._items.sort(this._comp); }
  pop() { return this._items.shift(); }
  top() { return this._items[0]; }
  size() { return this._items.length; }
  empty() { return this._items.length === 0; }
}
function priority_queue(...args) { return new _CppPriorityQueue(...args); }
class _CppMap extends Map {
  _k(k) { return (k !== null && k !== undefined && k._s !== undefined) ? k._s : k; }
  *[Symbol.iterator]() {
    for (const [k, v] of super.entries()) {
      yield { first: k, second: v, 0: k, 1: v, length: 2, [Symbol.iterator]: function*() { yield k; yield v; } };
    }
  }
  constructor(init = []) {
    super();
    if (Array.isArray(init)) {
      for (const item of init) {
        if (Array.isArray(item)) this.set(item[0], item[1]);
        else if (item && item.first !== undefined) this.set(item.first, item.second);
      }
    }
    return new Proxy(this, {
      get(target, prop, receiver) {
        if (typeof prop === "string" && !(prop in target) && typeof target[prop] !== "function") {
          let kp = target._k(prop);
          if (/^-?\d+$/.test(prop) && (target.has(Number(prop)) || [...target.keys()].some(x => typeof x === "number"))) kp = Number(prop);
          if (!target.has(kp)) target.set(kp, 0);
          return target.get(kp);
        }
        const val = Reflect.get(target, prop, target);
        return typeof val === "function" ? val.bind(target) : val;
      },
      set(target, prop, value, receiver) {
        if (typeof prop === "string" && !(prop in target)) {
          let kp = target._k(prop);
          if (/^-?\d+$/.test(prop) && (target.has(Number(prop)) || [...target.keys()].some(x => typeof x === "number"))) kp = Number(prop);
          target.set(kp, value);
          return true;
        }
        return Reflect.set(target, prop, value, target);
      }
    });
  }
  has(k) {
    const key = this._k(k);
    if (super.has(key)) return true;
    if (typeof key === "string" && /^-?\d+$/.test(key) && super.has(Number(key))) return true;
    if (typeof key === "number" && super.has(String(key))) return true;
    return false;
  }
  get(k) {
    const key = this._k(k);
    if (super.has(key)) return super.get(key);
    if (typeof key === "string" && /^-?\d+$/.test(key) && super.has(Number(key))) return super.get(Number(key));
    if (typeof key === "number" && super.has(String(key))) return super.get(String(key));
    return super.get(key);
  }
  set(k, v) { return super.set(this._k(k), v); }
  delete(k) {
    const key = this._k(k);
    if (super.has(key)) return super.delete(key);
    if (typeof key === "string" && /^-?\d+$/.test(key) && super.has(Number(key))) return super.delete(Number(key));
    if (typeof key === "number" && super.has(String(key))) return super.delete(String(key));
    return super.delete(key);
  }
  count(k) { return this.has(k) ? 1 : 0; }
  at(k) {
    if (!this.has(k)) throw new Error("map::at");
    return this.get(k);
  }
  find(k) {
    return this.has(k) ? { first: k, second: this.get(k) } : null;
  }
  insert(item) {
    if (Array.isArray(item)) { this.set(item[0], item[1]); }
    else if (item && item.first !== undefined) { this.set(item.first, item.second); }
  }
  emplace(k, v) { this.set(k, v); }
  end() { return null; }
  size() { return super.size; }
}
function map(init) { return new _CppMap(init); }
const unordered_map = map;
const multimap = map;
class _CppSet extends Set {
  _k(k) { return (k !== null && k !== undefined && k._s !== undefined) ? k._s : k; }
  constructor(init = []) {
    super();
    if (Array.isArray(init)) { for (const item of init) this.add(this._k(item)); }
  }
  has(k) {
    const key = this._k(k);
    if (super.has(key)) return true;
    if (typeof key === "string" && /^-?\d+$/.test(key) && super.has(Number(key))) return true;
    if (typeof key === "number" && super.has(String(key))) return true;
    return false;
  }
  add(val) { return super.add(this._k(val)); }
  delete(val) {
    const key = this._k(val);
    if (super.has(key)) return super.delete(key);
    if (typeof key === "string" && /^-?\d+$/.test(key) && super.has(Number(key))) return super.delete(Number(key));
    if (typeof key === "number" && super.has(String(key))) return super.delete(String(key));
    return super.delete(key);
  }
  insert(val) { this.add(val); }
  count(k) { return this.has(k) ? 1 : 0; }
  size() { return super.size; }
}
function set(init) { return new _CppSet(init); }
const unordered_set = set;
const multiset = set;
if (typeof Map.prototype.count !== "function") Map.prototype.count = function(k) { return this.has(k) ? 1 : 0; };
if (typeof Map.prototype.emplace !== "function") Map.prototype.emplace = function(k, v) { this.set(k, v); return this; };
if (typeof Map.prototype.find !== "function") Map.prototype.find = function(k) { return this.has(k) ? { first: k, second: this.get(k), 0: k, 1: this.get(k) } : null; };
if (typeof Map.prototype.end !== "function") Map.prototype.end = function() { return null; };
if (typeof Map.prototype.empty !== "function") Map.prototype.empty = function() { return this.size === 0; };
if (typeof Set.prototype.count !== "function") Set.prototype.count = function(k) { return this.has(k) ? 1 : 0; };
if (typeof Set.prototype.insert !== "function") Set.prototype.insert = function(val) { this.add(val); };
if (typeof Set.prototype.emplace !== "function") Set.prototype.emplace = function(val) { this.add(val); };
if (typeof Set.prototype.find !== "function") Set.prototype.find = function(k) { return this.has(k) ? k : null; };
if (typeof Set.prototype.end !== "function") Set.prototype.end = function() { return null; };
if (typeof Set.prototype.empty !== "function") Set.prototype.empty = function() { return this.size === 0; };
class _CppBitset {
  constructor(val = 0) {
    this._bits = BigInt(val);
  }
  count() {
    let c = 0, n = this._bits;
    while (n > 0n) { if (n & 1n) c++; n >>= 1n; }
    return c;
  }
  test(i) { return Boolean((this._bits >> BigInt(i)) & 1n); }
  to_ulong() { return Number(this._bits); }
  toString() { return this._bits.toString(2); }
}
function bitset(...args) { return new _CppBitset(...args); }
function make_pair(a, b) { return { first: a, second: b }; }
const pair = make_pair;
function make_tuple(...args) { return [...args]; }
const tuple = make_tuple;
function array(...args) {
  const items = (args.length === 1 && Array.isArray(args[0])) ? args[0] : args;
  return new _CppVector(...items);
}
const initializer_list = array;
function get(x, i = 0) {
  if (Array.isArray(x)) return x[i];
  if (i === 0) return (x && x.first !== undefined ? x.first : (x && x.val !== undefined ? x.val : x));
  if (i === 1) return (x && x.second !== undefined ? x.second : x);
  return x[i];
}
function optional(v = null) {
  const has = v !== null && v !== undefined;
  return {
    has_value: () => has,
    value: () => (has ? v : null),
    value_or: (def) => (has ? v : def),
    toString: () => String(v),
    valueOf: () => has,
    [Symbol.toPrimitive]: () => has
  };
}
function variant(v) {
  return {
    val: v,
    index: () => (typeof v === "number" ? 0 : 1),
    toString: () => String(v)
  };
}
function any(v) {
  return { val: v, toString: () => String(v) };
}
class _UniquePtr {
  constructor(obj = null) { this._obj = (obj && obj._obj !== undefined) ? obj._obj : obj; }
  get() { return this._obj; }
  release() { const o = this._obj; this._obj = null; return o; }
  reset(newObj = null) { this._obj = (newObj && newObj._obj !== undefined) ? newObj._obj : newObj; }
  valueOf() { return Boolean(this._obj); }
  [Symbol.toPrimitive]() { return Boolean(this._obj); }
}
function unique_ptr(obj = null) {
  const instance = new _UniquePtr(obj);
  return new Proxy(instance, {
    get(t, p, r) {
      if (p in t) return Reflect.get(t, p, r);
      if (t._obj != null && typeof t._obj === "object") return Reflect.get(t._obj, p);
      return undefined;
    },
    set(t, p, v, r) {
      if (p in t) return Reflect.set(t, p, v, r);
      if (t._obj != null && typeof t._obj === "object") return Reflect.set(t._obj, p, v);
      return false;
    }
  });
}
function shared_ptr(v = null) {
  let inner = (v && typeof v.get === "function") ? v.get() : v;
  return new Proxy({
    get: () => inner,
    use_count: () => (inner ? 2 : 0),
    reset: () => { inner = null; },
    valueOf: () => Boolean(inner)
  }, {
    get(t, p, r) {
      if (p in t) return Reflect.get(t, p, r);
      if (inner != null && typeof inner === "object") return Reflect.get(inner, p);
      return undefined;
    }
  });
}
function weak_ptr(p) {
  return { expired: () => false, lock: () => (p && typeof p.get === "function" ? p.get() : p) };
}
function make_shared(cls, ...args) {
  const obj = typeof cls === "function" ? new cls(...args) : cls;
  return shared_ptr(obj);
}
function make_unique(cls, ...args) {
  if (typeof cls === "function") return unique_ptr(new cls(...args));
  return unique_ptr(cls);
}
class _ofstream {
  constructor(path, mode) { this.path = path; this.mode = mode; this._parts = []; }
  close() {
    if (!fs) return;
    try {
      if (this.mode && String(this.mode).includes("app")) fs.appendFileSync(this.path, this._parts.join(""));
      else fs.writeFileSync(this.path, this._parts.join(""));
    } catch (e) {}
  }
}
function ofstream(path, mode) {
  const f = new _ofstream(path, mode);
  if (typeof process !== "undefined" && process.on) { process.on("beforeExit", () => f.close()); }
  return f;
}
class _ifstream {
  constructor(path) {
    let text = "";
    if (fs) { try { text = fs.readFileSync(path, "utf8"); } catch (e) { text = ""; } }
    this._text = text;
    this._idx = 0;
    this._tokens = text.trim().split(/\s+/).filter(Boolean);
    this._tokIdx = 0;
  }
  getline(delim = "\n") {
    if (this._idx >= this._text.length) return null;
    const d = (delim === "\n" || delim === "\\n") ? "\n" : String(delim);
    const end = this._text.indexOf(d, this._idx);
    let res;
    if (end === -1) { res = this._text.slice(this._idx); this._idx = this._text.length; }
    else { res = this._text.slice(this._idx, end); this._idx = end + d.length; }
    return res.replace(/\r$/, "");
  }
  get() {
    if (this._tokIdx < this._tokens.length) {
      const val = this._tokens[this._tokIdx++];
      const n = Number(val);
      return !isNaN(n) ? n : val;
    }
    return null;
  }
}
function ifstream(path) { return new _ifstream(path); }
function mutex() { return { lock() {}, unlock() {} }; }
function lock_guard(m) { return { m }; }
function unique_lock(m) { return { m, unlock() {}, lock() {} }; }
function condition_variable() { return { wait(l, p) { if (p) p(); }, notify_one() {}, notify_all() {} }; }
function atomic(val = 0) {
  let v = val;
  return {
    get val() { return v; },
    set val(x) { v = x; },
    fetch_add(x) { const old = v; v += x; return old; },
    load() { return v; },
    toString() { return String(v); },
    valueOf() { return v; }
  };
}
function thread(fn, ...args) { if (typeof fn === "function") fn(...args); return { join() {}, detach() {} }; }
function promise() {
  let _v;
  return {
    set_value(v) { _v = v; },
    get_future() { return { get: () => _v }; }
  };
}
function async(policy, fn, ...args) {
  const actualFn = typeof policy === "function" ? policy : fn;
  const actualArgs = typeof policy === "function" ? [fn, ...args] : args;
  const res = typeof actualFn === "function" ? actualFn(...actualArgs) : undefined;
  return { get: () => res };
}
const ios_base = { floatfield: 0, sync_with_stdio() {} };
const numeric_limits = {
  max: () => 2147483647,
  min: () => -2147483648,
  lowest: () => -2147483648,
  epsilon: () => 2.220446049250313e-16
};
const EXIT_SUCCESS = 0;
const EXIT_FAILURE = 1;
const MAX_SIZE = 100;
const __LINE__ = 917;
const __cplusplus = 201703;
let _ = null;
const std = new Proxy({
  numeric_limits: numeric_limits,
  array: array,
  initializer_list: initializer_list,
  make_pair: (...args) => make_pair(...args),
  pair: (...args) => pair(...args),
  make_tuple: (...args) => make_tuple(...args),
  tuple: (...args) => tuple(...args),
  vector: (...args) => vector(...args),
  deque: (...args) => deque(...args),
  list: (...args) => list(...args),
  forward_list: (...args) => forward_list(...args),
  stack: (...args) => stack(...args),
  queue: (...args) => queue(...args),
  priority_queue: (...args) => priority_queue(...args),
  map: (...args) => map(...args),
  unordered_map: (...args) => unordered_map(...args),
  multimap: (...args) => multimap(...args),
  set: (...args) => set(...args),
  unordered_set: (...args) => unordered_set(...args),
  multiset: (...args) => multiset(...args),
  bitset: (...args) => bitset(...args),
  optional: (...args) => optional(...args),
  variant: (...args) => variant(...args),
  any: (...args) => any(...args),
  unique_ptr: (...args) => unique_ptr(...args),
  shared_ptr: (...args) => shared_ptr(...args),
  weak_ptr: (...args) => weak_ptr(...args),
  make_unique: (...args) => make_unique(...args),
  make_shared: (...args) => make_shared(...args),
  ofstream: (...args) => ofstream(...args),
  ifstream: (...args) => ifstream(...args),
  mutex: (...args) => mutex(...args),
  lock_guard: (...args) => lock_guard(...args),
  unique_lock: (...args) => unique_lock(...args),
  condition_variable: (...args) => condition_variable(...args),
  atomic: (...args) => atomic(...args),
  thread: (...args) => thread(...args),
  promise: (...args) => promise(...args),
  async: (...args) => async(...args),
  cout: { unsetf() {}, precision() {}, write(s) { process.stdout.write(String(s)); }, tie() {} },
  clog: { write(s) { process.stdout.write(String(s)); } },
  cerr: { write(s) { process.stderr.write(String(s)); } },
  cin: { tie() {} },
  ios_base: ios_base,
  ios: { app: "app", floatfield: 0 },
  app: "app",
  endl: "\n",
  hex: "", dec: "", fixed: "", scientific: "", boolalpha: "", noboolalpha: "",
  setprecision: (n) => "", setw: (n) => "", setfill: (c) => "",
  to_string: (v) => String(v),
  stoi: (s) => parseInt(s, 10),
  stod: (s) => parseFloat(s),
  malloc: (sz) => new Array(sz).fill(0),
  free: () => {},
  remove: (p) => { if (fs) { try { fs.unlinkSync(p); } catch (e) {} } },
  snprintf: (buf, sz, fmt, ...args) => {
    let idx = 0;
    const res = fmt.replace(/%0?([0-9]*)(\.[0-9]+)?([dfscx%])/g, (match, width, prec, spec) => {
      if (spec === "%") return "%";
      if (idx >= args.length) return match;
      const a = args[idx++];
      let out;
      if (spec === "x") out = Number(a).toString(16);
      else if (prec) out = Number(a).toFixed(parseInt(prec.slice(1)));
      else out = String(a);
      if (width) {
        const padChar = match.startsWith("%0") ? "0" : " ";
        out = out.padStart(parseInt(width), padChar);
      }
      return out;
    });
    if (buf && typeof buf.set === "function") buf.set(res);
    return res.length;
  },
  printf: (fmt, ...args) => {
    let idx = 0;
    const res = fmt.replace(/%[a-z%]/g, (m) => (m === "%%" ? "%" : (idx < args.length ? String(args[idx++]) : m)));
    process.stdout.write(res);
  },
  strcmp: (a, b) => { const s1 = String(a), s2 = String(b); return s1 > s2 ? 1 : s1 < s2 ? -1 : 0; },
  atoi: (s) => parseInt(s, 10),
  strlen: (s) => (s ? String(s).length : 0),
  getline: getline,
  isalpha: (c) => /[a-zA-Z]/.test(c),
  isdigit: (c) => /[0-9]/.test(c),
  toupper: (c) => (typeof c === "number" ? String.fromCharCode(c).toUpperCase().charCodeAt(0) : String(c).toUpperCase()),
  tolower: (c) => (typeof c === "number" ? String.fromCharCode(c).toLowerCase().charCodeAt(0) : String(c).toLowerCase()),
  sqrt: Math.sqrt, pow: Math.pow, abs: Math.abs,
  floor: Math.floor, ceil: Math.ceil, round: Math.round,
  fmod: (a, b) => a % b, sin: Math.sin, cos: Math.cos, tan: Math.tan,
  atan2: Math.atan2, exp: Math.exp, log: Math.log, log10: Math.log10,
  hypot: Math.hypot, isnan: Number.isNaN, isinf: (x) => !isFinite(x), nan: () => NaN,
  gcd: (a, b) => { a = Math.abs(a); b = Math.abs(b); while (b) { [a, b] = [b, a % b]; } return a; },
  lcm: (a, b) => Math.abs(a * b) / (std.gcd(a, b) || 1),
  min: (...args) => Math.min(...args),
  max: (...args) => Math.max(...args),
  move: (x) => x,
  sort: (begin, end, comp) => {
    if (begin && begin._vec) begin._vec.sort(comp || ((a, b) => a - b));
    else if (Array.isArray(begin)) begin.sort(comp || ((a, b) => a - b));
  },
  remove: (begin, end, val) => {
    if (begin && begin._vec) {
      const v = begin._vec;
      for (let i = v.length - 1; i >= 0; i--) {
        if (v[i] === val) v.splice(i, 1);
      }
      return new _VecIter(v, v.length);
    }
    return end;
  },
  accumulate: (begin, end, init, op) => {
    const v = (begin && begin._vec) ? begin._vec : (Array.isArray(begin) ? begin : []);
    let res = init;
    for (const item of v) res = op ? op(res, item) : (res + item);
    return res;
  },
  distance: (begin, it) => (Number(it) - Number(begin)),
  max_element: (b, e) => { const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []); if (!v.length) return b; let mi = 0; for (let i = 1; i < v.length; i++) if (v[i] > v[mi]) mi = i; return new _VecIter(v, mi); },
  min_element: (b, e) => { const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []); if (!v.length) return b; let mi = 0; for (let i = 1; i < v.length; i++) if (v[i] < v[mi]) mi = i; return new _VecIter(v, mi); },
  unique: (begin, end) => { const v = (begin && begin._vec) ? begin._vec : (Array.isArray(begin) ? begin : []); const b = (begin && begin._idx !== undefined) ? begin._idx : 0; const e = (end && end._idx !== undefined) ? end._idx : v.length; let write = b; for (let read = b; read < e; read++) { if (write === b || v[read] !== v[write - 1]) v[write++] = v[read]; } return new _VecIter(v, write); },
  count_if: (b, e, p) => { const v = (b && b._vec) ? b._vec : []; return v.filter(p).length; },
  any_of: (b, e, p) => { const v = (b && b._vec) ? b._vec : []; return v.some(p); },
  all_of: (b, e, p) => { const v = (b && b._vec) ? b._vec : []; return v.every(p); },
  none_of: (b, e, p) => { const v = (b && b._vec) ? b._vec : []; return !v.some(p); },
  find: (b, e, v) => e,
  find_if: (b, e, p) => {
    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);
    const idx = v.findIndex(p);
    return idx !== -1 ? new _VecIter(v, idx) : e;
  },
  iota: (b, e, val) => {
    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);
    for (let i = 0; i < v.length; i++) v[i] = val + i;
  },
  partial_sum: (b, e, out) => {
    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);
    const o = (out && out._vec) ? out._vec : (Array.isArray(out) ? out : []);
    let run = 0;
    for (let i = 0; i < v.length; i++) { run += v[i]; o[i] = run; }
  },
  set_intersection: (b1, e1, b2, e2, out) => {
    const s1 = (b1 && b1._vec) ? b1._vec : (Array.isArray(b1) ? b1 : []);
    const s2 = (b2 && b2._vec) ? b2._vec : (Array.isArray(b2) ? b2 : []);
    const o = (out && out._vec) ? out._vec : (Array.isArray(out) ? out : []);
    for (const x of s1) if (s2.includes(x)) o.push(x);
  },
  back_inserter: (v) => v,
  fill: (b, e, val) => {
    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);
    v.fill(val);
  },
  copy: (b, e, out) => {
    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);
    if (typeof out === "function") { for (const item of v) out(item); }
  },
  partition: (b, e, p) => {
    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);
    const ev = v.filter(p), od = v.filter(x => !p(x));
    v.splice(0, v.length, ...ev, ...od);
  },
  nth_element: (b, nth, e) => {
    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);
    v.sort((x, y) => x - y);
  },
  rotate: (b, m, e) => {
    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);
    const mid = (m && m._idx !== undefined) ? m._idx : (typeof m === "number" ? m : 0);
    const rot = v.splice(0, mid);
    v.push(...rot);
  },
  reverse: (b, e) => {
    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);
    v.reverse();
  },
  for_each: (b, e, fn) => {
    const v = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []);
    for (let i = 0; i < v.length; i++) {
      const res = fn(v[i]);
      if (res !== undefined) v[i] = res;
    }
  },
  next_permutation: (b, e) => false,
  bind: (fn, ...bindArgs) => (...callArgs) => {
    let callIdx = 0;
    const finalArgs = bindArgs.map(a => ((a === std.placeholders._1 || a === std.placeholders._2) ? callArgs[callIdx++] : a));
    return fn(...finalArgs, ...callArgs.slice(callIdx));
  },
  placeholders: { _1: Symbol("_1"), _2: Symbol("_2") },
  shuffle: () => {},
  srand: () => {},
  rand: () => 1,
  time: () => Math.floor(Date.now() / 1000),
  clock: () => Date.now(),
  binary_search: (b, e, v) => { const arr = (b && b._vec) ? b._vec : (Array.isArray(b) ? b : []); return arr.includes(v); },
  lower_bound: (b, e, v) => b,
  ignore: null,
  transform: (first, last, out_first, op) => {
    if (first && first.owner && first.owner._s !== undefined) {
      const s = first.owner._s;
      const end_idx = (last && last.idx !== undefined) ? last.idx : s.length;
      let out_chars = Array.from(out_first.owner._s);
      for (let i = first.idx; i < end_idx; i++) {
        let res = op(s[i]);
        if (typeof res === "number") res = String.fromCharCode(res);
        out_chars[out_first.idx + (i - first.idx)] = String(res);
      }
      out_first.owner._s = out_chars.join("");
      return out_first;
    } else {
      const v = (first && first._vec) ? first._vec : (Array.isArray(first) ? first : []);
      const o = (out_first && out_first._vec) ? out_first._vec : (Array.isArray(out_first) ? out_first : []);
      for (let i = 0; i < v.length; i++) o[i] = op(v[i]);
      return out_first;
    }
  },
  visit: (fn, v) => (v && "val" in v ? fn(v.val) : fn(v)),
  holds_alternative: (v) => true,
  get: (x) => (x && "val" in x ? x.val : x),
  any_cast: (x) => (x && "val" in x ? x.val : x),
  regex_search: (s, m, re) => {
    const str = String(s);
    const pattern = (typeof re === "string") ? new RegExp(re) : re;
    const match = str.match(pattern);
    if (match) {
      if (m && Array.isArray(m)) { m.length = 0; for (const item of match) m.push(item); }
      return true;
    }
    return false;
  },
  regex_replace: (s, re, repl) => {
    const pattern = (typeof re === "string") ? new RegExp(re, "g") : (re.global ? re : new RegExp(re.source, re.flags + "g"));
    return String(s).replace(pattern, repl);
  },
  regex_match: (s, re) => {
    const pattern = (typeof re === "string") ? new RegExp(re) : re;
    return pattern.test(String(s));
  },
  this_thread: { sleep_for() {} },
  chrono: {
    now: () => Date.now(),
    system_clock: { now: () => Date.now() },
    steady_clock: { now: () => Date.now() },
    high_resolution_clock: { now: () => Date.now() },
    milliseconds: (x) => x,
    duration_cast: (d) => 5
  },
  invalid_argument: _CppInvalidArgument,
  out_of_range: _CppOutOfRange,
  runtime_error: _CppRuntimeError,
  exception: _CppException,
  string: _CppString
}, {
  get(target, prop) {
    if (prop in target) return target[prop];
    if (prop === "std") return target;
    return () => {};
  }
});
std.std = std;
function to_string(v) { return String(v); }
function stoi(s) { return parseInt(s, 10); }
function stod(s) { return parseFloat(s); }
function sort(...args) { return std.sort(...args); }
function reverse(...args) { return std.reverse(...args); }
function transform(...args) { return std.transform(...args); }
function count_if(...args) { return std.count_if(...args); }
function accumulate(...args) { return std.accumulate(...args); }
const fixed = "";
function setprecision(n) { return ""; }
function unique(...args) { return std.unique(...args); }
function partial_sum(...args) { return std.partial_sum(...args); }
function max_element(...args) { return std.max_element(...args); }
function min_element(...args) { return std.min_element(...args); }
function find(...args) { return std.find(...args); }
function find_if(...args) { return std.find_if(...args); }
function distance(...args) { return std.distance(...args); }
function any_of(...args) { return std.any_of(...args); }
function all_of(...args) { return std.all_of(...args); }
function none_of(...args) { return std.none_of(...args); }
function iota(...args) { return std.iota(...args); }
function fill(...args) { return std.fill(...args); }
function copy(...args) { return std.copy(...args); }
function for_each(...args) { return std.for_each(...args); }
function partition(...args) { return std.partition(...args); }
function rotate(...args) { return std.rotate(...args); }
function binary_search(...args) { return std.binary_search(...args); }
function lower_bound(...args) { return std.lower_bound(...args); }
function set_intersection(...args) { return std.set_intersection(...args); }
function ostream_iterator(stream, delim = "") {
  return (val) => {
    if (stream && stream.write) stream.write(val + delim);
    else process.stdout.write(val + delim);
  };
}
function regex(pat) { return new RegExp(pat); }
function smatch() { return []; }
function mt19937(seed) { return () => 4; }
function uniform_int_distribution(min, max) { return (gen) => Math.floor(Math.random() * (max - min + 1)) + min; }
function uniform_real_distribution(min, max) { return (gen) => 0.5; }
function normal_distribution(m, s) { return () => 0.5; }
function name() { return "Circle"; }
function multiplies() { return (a, b) => a * b; }
const T = () => 0;
const N = 5;

// Namespace: campus
const MAX_LOANS = 3;
const FINE_PER_DAY = 2.5;
const Category = {
  Science: 0,
  Fiction: 1,
  History: 2,
  Computing: 3,
  Arts: 4,
};
const Science = Category.Science;
const Fiction = Category.Fiction;
const History = Category.History;
const Computing = Category.Computing;
const Arts = Category.Arts;
function categoryName(c) {
  switch (c) {
    case Science:
      return string("Science");
    case Fiction:
      return string("Fiction");
    case History:
      return string("History");
    case Computing:
      return string("Computing");
    default:
      return string("Arts");
  }
}

class Book {
  constructor(i = null, t = null, a = null, c = null, n = null, r = null) {
    this.id = i;
    this.title = t;
    this.author = a;
    this.category = c;
    this.copies = n;
    this.borrowed = 0;
    this.rating = r;
  }
  available() {
    return _sub(this.copies, this.borrowed);
  }
  operator_lt(other) {
    return (this.id < other.id);
  }
  description() {
    let out = ostringstream();
    _shift(_shift(_shift(_shift(_shift(out, this.id), " | "), this.title), " | "), this.author);
    _shift(_shift(_shift(out, " | "), categoryName(this.category)), " | ");
    _shift(_shift(_shift(out, this.available()), "/"), this.copies);
    return out.str();
  }
  get() { return this; }
  destructor_Book() {}
}

class Person {
  constructor(id = null, name = null) {
    this.id_ = id;
    this.name_ = name;
  }
  destructor_Person() {
  }
  id() {
    return this.id_;
  }
  name() {
    return string(this.name_);
  }
  role() {
  }
  print() {
    console.log(this.role(), " #", this.id_, " ", this.name_);
  }
  get() { return this; }
  destructor_Person() {}
}

class Loan {
  constructor(b = null, d = null) {
    this.bookId = b;
    this.days = d;
    this.returned = false;
  }
  get() { return this; }
  destructor_Loan() {}
}

class Member extends Person {
  constructor(id = null, name = null) {
    super(id, name);
    this.points_ = 0;
    this.loans_ = vector();
  }
  role() {
    return string("Member");
  }
  canBorrow() {
    return (this.activeLoans() < MAX_LOANS);
  }
  activeLoans() {
    let count = 0;
    for (const loan of this.loans_) {
      if (_not(loan.returned)) {
        ++count;
      }
    }
    return count;
  }
  borrow(bookId, days) {
    if (_not(this.canBorrow())) {
      throw (runtime_error("Loan limit reached"));
    }
    this.loans_.emplace_back(new Loan(bookId, days));
    if (this.points_ && typeof this.points_.append === 'function') this.points_.append(10); else if (this.points_ && typeof this.points_.operator_add_assign === 'function') this.points_.operator_add_assign(10); else this.points_ += 10;
  }
  giveBack(bookId) {
    for (const loan of this.loans_) {
      if ((_eq(loan.bookId, bookId) && _not(loan.returned))) {
        loan.returned = true;
        return true;
      }
    }
    return false;
  }
  fine() {
    let total = 0;
    for (const loan of this.loans_) {
      if ((_not(loan.returned) && (loan.days > 14))) {
        if (total && typeof total.append === 'function') total.append(_mul(_sub(loan.days, 14), FINE_PER_DAY)); else if (total && typeof total.operator_add_assign === 'function') total.operator_add_assign(_mul(_sub(loan.days, 14), FINE_PER_DAY)); else total += _mul(_sub(loan.days, 14), FINE_PER_DAY);
      }
    }
    return total;
  }
  points() {
    return this.points_;
  }
  loans() {
    return this.loans_;
  }
  print() {
    super.print();
    console.log("  Active loans: ", this.activeLoans());
    console.log(" | Points: ", this.points_);
    console.log(" | Fine: ", fixed, setprecision(2), this.fine());
  }
  get() { return this; }
  destructor_Member() {}
}

class Librarian extends Person {
  constructor(id = null, name = null, shift = null) {
    super(id, name);
    this.shift_ = shift;
  }
  role() {
    return string("Librarian");
  }
  shift() {
    return string(this.shift_);
  }
  print() {
    super.print();
    console.log("  Shift: ", this.shift_);
  }
  get() { return this; }
  destructor_Librarian() {}
}

class Library {
  constructor() {
    this.books_ = map();
    this.members_ = map();
    this.events_ = vector();
  }
  addBook(b) {
    if (this.books_.count(b.id)) {
      throw (invalid_argument("Duplicate book"));
    }
    this.books_.emplace(b.id, b);
    this.events_.push_back(_add("Added book ", to_string(b.id)));
  }
  addMember(m) {
    if (this.members_.count(m.id())) {
      throw (invalid_argument("Duplicate member"));
    }
    this.members_.emplace(m.id(), m);
    this.events_.push_back(_add("Added member ", to_string(m.id())));
  }
  findBook(id) {
    let it = this.books_.find(id);
    return (_eq(it, this.books_.end()) ? null : it.second);
  }
  findMember(id) {
    let it = this.members_.find(id);
    return (_eq(it, this.members_.end()) ? null : it.second);
  }
  findBook(id) {
    let it = this.books_.find(id);
    return (_eq(it, this.books_.end()) ? null : it.second);
  }
  borrowBook(memberId, bookId, days) {
    let member = this.findMember(memberId);
    let book = this.findBook(bookId);
    if ((_not(member) || _not(book))) {
      throw (out_of_range("Unknown ID"));
    }
    if (_eq(book.available(), 0)) {
      throw (runtime_error("Out of stock"));
    }
    member.borrow(bookId, days);
    ++book.borrowed;
    this.events_.push_back(_add("Borrowed ", to_string(bookId)));
  }
  returnBook(memberId, bookId) {
    let member = this.findMember(memberId);
    let book = this.findBook(bookId);
    if ((_not(member) || _not(book))) {
      throw (out_of_range("Unknown ID"));
    }
    if (_not(member.giveBack(bookId))) {
      throw (runtime_error("No active loan"));
    }
    --book.borrowed;
    this.events_.push_back(_add("Returned ", to_string(bookId)));
  }
  allBooks() {
    let result = vector();
    for (const item of this.books_) {
      result.push_back(item.second);
    }
    return vector(result);
  }
  search(text) {
    let result = vector();
    for (const item of this.books_) {
      let b = item.second;
      if ((_ne(b.title.find(text), string.npos) || _ne(b.author.find(text), string.npos))) {
        result.push_back(b);
      }
    }
    return vector(result);
  }
  byCategory(category) {
    let result = vector();
    for (const item of this.books_) {
      if (_eq(item.second.category, category)) {
        result.push_back(item.second);
      }
    }
    return vector(result);
  }
  topRated(limit) {
    let result = this.allBooks();
    sort(result.begin(), result.end(), ((a, b) => (_eq(a.rating, b.rating) ? (a.id < b.id) : (a.rating > b.rating))));
    if ((result.size() > limit)) {
      result.erase(_add(result.begin(), limit), result.end());
    }
    return vector(result);
  }
  totalCopies() {
    let sum = 0;
    for (const item of this.books_) {
      if (sum && typeof sum.append === 'function') sum.append(item.second.copies); else if (sum && typeof sum.operator_add_assign === 'function') sum.operator_add_assign(item.second.copies); else sum += item.second.copies;
    }
    return sum;
  }
  totalBorrowed() {
    let sum = 0;
    for (const item of this.books_) {
      if (sum && typeof sum.append === 'function') sum.append(item.second.borrowed); else if (sum && typeof sum.operator_add_assign === 'function') sum.operator_add_assign(item.second.borrowed); else sum += item.second.borrowed;
    }
    return sum;
  }
  averageRating() {
    if (this.books_.empty()) {
      return 0.0;
    }
    let sum = 0;
    for (const item of this.books_) {
      if (sum && typeof sum.append === 'function') sum.append(item.second.rating); else if (sum && typeof sum.operator_add_assign === 'function') sum.operator_add_assign(item.second.rating); else sum += item.second.rating;
    }
    return (sum / this.books_.size());
  }
  outstandingFines() {
    let sum = 0;
    for (const item of this.members_) {
      if (sum && typeof sum.append === 'function') sum.append(item.second.fine()); else if (sum && typeof sum.operator_add_assign === 'function') sum.operator_add_assign(item.second.fine()); else sum += item.second.fine();
    }
    return sum;
  }
  memberCount() {
    return this.members_.size();
  }
  bookCount() {
    return this.books_.size();
  }
  events() {
    return this.events_;
  }
  printMembers() {
    for (const item of this.members_) {
      item.second.print();
    }
  }
  printBooks() {
    for (const item of this.books_) {
      console.log(item.second.description());
    }
  }
  saveCatalog(filename) {
    let file = ofstream(filename);
    if (_not(file)) {
      throw (runtime_error("Cannot create catalog"));
    }
    for (const item of this.books_) {
      let b = item.second;
      _shift(_shift(_shift(_shift(_shift(_shift(file, b.id), ","), b.title), ","), b.author), ",");
      _shift(_shift(_shift(_shift(file, b.copies), ","), b.borrowed), "\\n");
    }
  }
  saveEvents(filename) {
    let file = ofstream(filename);
    if (_not(file)) {
      throw (runtime_error("Cannot create event log"));
    }
    for (const event of this.events_) {
      _shift(_shift(file, event), "\\n");
    }
  }
  get() { return this; }
  destructor_Library() {}
}

function maximumOf(values) {
  if (values.empty()) {
    throw (invalid_argument("Empty collection"));
  }
  return _deref(max_element(values.begin(), values.end()));
}

function meanOf(values) {
  if (values.empty()) {
    return 0.0;
  }
  return (accumulate(values.begin(), values.end(), 0.0) / values.size());
}

function uniqueSorted(data) {
  sort(data.begin(), data.end());
  data.erase(unique(data.begin(), data.end()), data.end());
  return vector(data);
}

function wordHistogram(text) {
  let input = istringstream(text);
  let counts = map();
  let word = string();
  while (true) {
    const _tok = input.get();
    if (_tok === null || _tok === undefined) break;
    word = _tok;
    ++counts[word];
  }
  return map(counts);
}

function rollingTotals(values) {
  let totals = vector(values.size());
  partial_sum(values.begin(), values.end(), totals.begin());
  return vector(totals);
}

function evenSquares(values) {
  let result = vector();
  for (const x of values) {
    if (_eq((x % 2), 0)) {
      result.push_back(_mul(x, x));
    }
  }
  return vector(result);
}

function printNumbers(values, label) {
  console.log(label, ":");
  for (const value of values) {
    console.log(" ", value);
  }
  console.log();
}

function printBooks(books, label) {
  console.log(label, " (", books.size(), ")\\n");
  for (const b of books) {
    console.log("  ", b.description());
  }
}

function populate(library) {
  library.addBook(new Book(101, string("C++ Fundamentals"), string("Ada"), Computing, 4, 4.8));
  library.addBook(new Book(102, string("Algorithms"), string("Knuth"), Computing, 3, 4.9));
  library.addBook(new Book(103, string("Physics"), string("Feynman"), Science, 5, 4.7));
  library.addBook(new Book(104, string("Astronomy"), string("Carl"), Science, 2, 4.3));
  library.addBook(new Book(105, string("Ancient Worlds"), string("Mira"), History, 3, 4.1));
  library.addBook(new Book(106, string("Modern History"), string("Lena"), History, 2, 4.0));
  library.addBook(new Book(107, string("Stories"), string("Orwell"), Fiction, 6, 4.6));
  library.addBook(new Book(108, string("Poetry"), string("Rita"), Arts, 3, 4.2));
  library.addBook(new Book(109, string("Machine Learning"), string("Ravi"), Computing, 2, 4.5));
  library.addBook(new Book(110, string("Painting"), string("Nora"), Arts, 4, 4.4));
  library.addMember(new Member(1, string("Alice")));
  library.addMember(new Member(2, string("Bob")));
  library.addMember(new Member(3, string("Charlie")));
  library.addMember(new Member(4, string("Diana")));
  library.addMember(new Member(5, string("Ethan")));
}

function runLoans(library) {
  library.borrowBook(1, 101, 5);
  library.borrowBook(1, 102, 18);
  library.borrowBook(2, 103, 21);
  library.borrowBook(3, 107, 7);
  library.borrowBook(4, 109, 15);
  library.borrowBook(5, 108, 3);
  console.log("Borrowed copies: ", library.totalBorrowed());
  library.returnBook(3, 107);
  console.log("After return: ", library.totalBorrowed());
  try {
    library.borrowBook(99, 101, 1);
  } catch (__err) {
    if ((__err instanceof out_of_range || (__err && __err.name === 'out_of_range') || (__err && __err.constructor && __err.constructor.name === 'out_of_range'))) {
      let error = __err;
      console.log("Expected missing member: ", error.what());
    } else {
      throw __err;
    }
  }
  try {
    library.returnBook(3, 107);
  } catch (__err) {
    if ((__err instanceof runtime_error || (__err && __err.name === 'runtime_error') || (__err && __err.constructor && __err.constructor.name === 'runtime_error'))) {
      let error = __err;
      console.log("Expected repeated return: ", error.what());
    } else {
      throw __err;
    }
  }
}

function showAnalytics(library) {
  console.log("=== Library analytics ===\\n");
  console.log("Books: ", library.bookCount());
  console.log("Members: ", library.memberCount());
  console.log("Copies: ", library.totalCopies());
  console.log("Borrowed: ", library.totalBorrowed());
  console.log("Average rating: ", fixed, setprecision(2));
  console.log(library.averageRating());
  console.log("Fines due: ", library.outstandingFines());
  printBooks(library.topRated(3), string("Top rated books"));
  printBooks(library.search(string("History")), string("History title search"));
  printBooks(library.byCategory(Science), string("Science books"));
  console.log("=== Member records ===\\n");
  library.printMembers();
}

function algorithmDemos() {
  console.log("=== STL algorithm demonstrations ===\\n");
  let values = vector([7, 2, 7, 4, 9, 2, 10, 3, 6, 4]);
  printNumbers(values, string("Input"));
  printNumbers(uniqueSorted(vector(values)), string("Unique sorted"));
  printNumbers(rollingTotals(values), string("Running totals"));
  printNumbers(evenSquares(values), string("Even squares"));
  console.log("Maximum: ", maximumOf(values));
  console.log("Mean: ", meanOf(values));
  console.log("Count even: ", count_if(values.begin(), values.end(), ((x) => _eq((x % 2), 0))));
  let copied = vector(values.size());
  transform(values.begin(), values.end(), copied.begin(), ((x) => _mul(x, 3)));
  printNumbers(copied, string("Tripled"));
  reverse(copied.begin(), copied.end());
  printNumbers(copied, string("Reversed"));
  let histogram = wordHistogram(string("red blue red green blue red"));
  for (const item of histogram) {
    console.log(item.first, "=", item.second, " ");
  }
  console.log();
}

function containerDemos() {
  console.log("=== Additional containers ===\\n");
  let doubleEnded = deque([2, 3, 4]);
  doubleEnded.push_front(1);
  doubleEnded.push_back(5);
  console.log("Deque front/back: ", doubleEnded.front());
  console.log("/", doubleEnded.back());
  let pending = queue();
  pending.push(string("request-A"));
  pending.push(string("request-B"));
  while (_not(pending.empty())) {
    console.log("Queue: ", pending.front());
    pending.pop();
  }
  let history = stack();
  for (let i = 1; (i <= 3); ++i) {
    history.push(_mul(i, 10));
  }
  while (_not(history.empty())) {
    console.log("Stack: ", history.top());
    history.pop();
  }
  let ids = set([4, 2, 2, 1, 3]);
  console.log("Unique IDs:");
  for (const id of ids) {
    console.log(" ", id);
  }
  console.log();
}

function pointerAndPolymorphismDemo() {
  console.log("=== Smart pointers and polymorphism ===\\n");
  let people = vector();
  people.push_back(new Member(11, "Nina"));
  people.push_back(new Librarian(20, "Oliver", "Morning"));
  people.push_back(new Member(12, "Priya"));
  for (const person of people) {
    person.print();
  }
  let counter = make_shared(5);
  let alias = counter;
  if (Array.isArray(alias)) alias[0] = 3; else alias = 3;
  console.log("Shared value: ", _deref(counter));
  console.log("Reference count: ", counter.use_count());
}

function exceptionDemo() {
  console.log("=== Exception handling ===\\n");
  let data = vector([10, 20, 30]);
  try {
    console.log("Value at index 1: ", data.at(1));
    console.log(data.at(20));
  } catch (__err) {
    if ((__err instanceof out_of_range || (__err && __err.name === 'out_of_range') || (__err && __err.constructor && __err.constructor.name === 'out_of_range'))) {
      let error = __err;
      console.log("Caught range exception: ", error.what());
    } else {
      throw __err;
    }
  }
  try {
    let empty = vector();
    console.log(maximumOf(empty));
  } catch (__err) {
    if ((__err instanceof invalid_argument || (__err && __err.name === 'invalid_argument') || (__err && __err.constructor && __err.constructor.name === 'invalid_argument'))) {
      let error = __err;
      console.log("Caught invalid argument: ", error.what());
    } else {
      throw __err;
    }
  }
}

function exportReports(library) {
  console.log("=== File output ===\\n");
  try {
    library.saveCatalog(string("library_catalog.csv"));
    library.saveEvents(string("library_events.txt"));
    console.log("Saved catalog and event log\\n");
  } catch (__err) {
    if ((__err instanceof _CppException || __err instanceof Error || __err instanceof exception || (__err && __err.name === 'exception'))) {
      let error = __err;
      console.log("File error: ", error.what());
    } else {
      throw __err;
    }
  }
}

const campus = { MAX_LOANS: MAX_LOANS, FINE_PER_DAY: FINE_PER_DAY, categoryName: categoryName, Book: Book, Person: Person, Loan: Loan, Member: Member, Librarian: Librarian, Library: Library, maximumOf: maximumOf, meanOf: meanOf, uniqueSorted: uniqueSorted, wordHistogram: wordHistogram, rollingTotals: rollingTotals, evenSquares: evenSquares, printNumbers: printNumbers, printBooks: printBooks, populate: populate, runLoans: runLoans, showAnalytics: showAnalytics, algorithmDemos: algorithmDemos, containerDemos: containerDemos, pointerAndPolymorphismDemo: pointerAndPolymorphismDemo, exceptionDemo: exceptionDemo, exportReports: exportReports };

function main() {
  console.log("UNIVERSALTRANSPILER C++17 STRESS TEST\\n");
  let library = new Library();
  populate(library);
  runLoans(library);
  showAnalytics(library);
  algorithmDemos();
  containerDemos();
  pointerAndPolymorphismDemo();
  exceptionDemo();
  exportReports(library);
  console.log("Completed successfully\\n");
  return 0;
}


if (typeof main === "function") {
  try { main(1, ["./program"]); } catch (e) { console.error(e); process.exit(1); }
}
