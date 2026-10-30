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
    this.name = this.constructor.name;
  }
  what() { return this.message; }
}
class _CppInvalidArgument extends _CppException {}
class _CppOutOfRange extends _CppException {}
class _CppRuntimeError extends _CppException {}
function invalid_argument(m) { return new _CppInvalidArgument(m); }
function out_of_range(m) { return new _CppOutOfRange(m); }
function runtime_error(m) { return new _CppRuntimeError(m); }
function exception(m) { return new _CppException(m); }
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
  return a + b;
}
function _sub(a, b) {
  if (a && typeof a.operator_sub === "function") return a.operator_sub(b);
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
  return a == b;
}
function _ne(a, b) {
  if (a && typeof a.operator_ne === "function") return a.operator_ne(b);
  if (a && typeof a.get === "function" && b == null) return a.get() != null;
  if (b && typeof b.get === "function" && a == null) return b.get() != null;
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
  [Symbol.toPrimitive](hint) { return hint === "number" ? this._idx : ((this._vec && this._idx < this._vec.length) ? this._vec[this._idx] : this._idx); }
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
      if (t._obj != null) return Reflect.get(t._obj, p);
      return undefined;
    },
    set(t, p, v, r) {
      if (p in t) return Reflect.set(t, p, v, r);
      if (t._obj != null) return Reflect.set(t._obj, p, v);
      return false;
    }
  });
}
function shared_ptr(v = null) {
  let inner = (v && typeof v.get === "function") ? v.get() : v;
  return new Proxy({
    get: () => inner,
    use_count: () => (inner ? 1 : 0),
    reset: () => { inner = null; },
    valueOf: () => Boolean(inner)
  }, {
    get(t, p, r) {
      if (p in t) return Reflect.get(t, p, r);
      if (inner != null) return Reflect.get(inner, p);
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
  max_element: (b, e) => { const v = (b && b._vec) ? b._vec : []; return v.length ? Math.max(...v) : 9; },
  min_element: (b, e) => { const v = (b && b._vec) ? b._vec : []; return v.length ? Math.min(...v) : 1; },
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

// Namespace: math_utils
const PI = 3.141592653589793;
function add(a, b) {
  return _add(a, b);
}

function add(a, b) {
  return _add(a, b);
}

// Namespace: nested
function triple(x) {
  return _mul(3, x);
}

const nested = { triple: triple };

const math_utils = { PI: PI, add: add, nested: nested };

let alias_target = math_utils.nested;
let g_counter = 0;
const G_CONST = 42;
const G_CONSTEXPR = 7;
let s_static_global = 5;
let g_extern_decl;
g_extern_decl = 99;
const Color = {
  RED: 0,
  GREEN: 5,
  BLUE: 2,
};
const RED = Color.RED;
const GREEN = Color.GREEN;
const BLUE = Color.BLUE;
const Direction = {
  North: 1,
  East: 1,
  South: 2,
  West: 3,
};
const North = Direction.North;
const East = Direction.East;
const South = Direction.South;
const West = Direction.West;
/* template <typename T> using Vec = std::vector<T> */
class Point {
  constructor(x_ = 0, y_ = 0) {
    this.x = x_;
    this.y = y_;
  }
  operator_eq(o) {
    return (_eq(this.x, o.x) && _eq(this.y, o.y));
  }
  toString() { return `(${this.x}, ${this.y})`; }
  [Symbol.toPrimitive]() { return `(${this.x}, ${this.y})`; }
  [Symbol.for('nodejs.util.inspect.custom')]() { return `(${this.x}, ${this.y})`; }
  operator_eq(o) { return Boolean(o && this.x === o.x && this.y === o.y); }
  get() { return this; }
  destructor_Point() {}
}

class IntOrFloat {
  constructor() {
    this.i = null;
    this.f = null;
  }
  get() { return this; }
  destructor_IntOrFloat() {}
}

class Flags {
  constructor() {
    this.a = 1;
    this.b = 3;
    this.c = 4;
  }
  get() { return this; }
  destructor_Flags() {}
}

function factorial(n) {
}

class Shape {
  constructor(n = null) {
    this.name_ = std.move(n);
  }
  destructor_Shape() {
  }
  area() {
  }
  perimeter() {
  }
  describe() {
    return _add(_add(this.name_, " area="), std.to_string(this.area()));
  }
  name() {
    return this.name_;
  }
  get() { return this; }
  destructor_Shape() {}
}

class Circle extends Shape {
  constructor(r = null) {
    super("Circle");
    this.r_ = r;
  }
  area() {
    return _mul(_mul(math_utils.PI, this.r_), this.r_);
  }
  perimeter() {
    return _mul(_mul(2, math_utils.PI), this.r_);
  }
  get() { return this; }
  destructor_Circle() {}
}

class Rectangle extends Shape {
  constructor(w = null, h = null) {
    super("Rectangle");
    this.w_ = w;
    this.h_ = h;
  }
  area() {
    return _mul(this.w_, this.h_);
  }
  perimeter() {
    return _mul(2, _add(this.w_, this.h_));
  }
  get() { return this; }
  destructor_Rectangle() {}
}

class Square extends Rectangle {
  constructor(s = null) {
    super(s, s);
    this.name_ = "Square";
  }
  describe() {
    return _add("[Square] ", super.describe());
  }
  /* final */
  get() { return this; }
  destructor_Square() {}
}

class Animal {
  constructor() {
  }
  sound() {
    return string("...");
  }
  destructor_Animal() {
  }
  get() { return this; }
  destructor_Animal() {}
}

class Walker extends Animal {
  constructor() {
    super();
  }
  walk() {
    return string("walking");
  }
  get() { return this; }
  destructor_Walker() {}
}

class Swimmer extends Animal {
  constructor() {
    super();
  }
  swim() {
    return string("swimming");
  }
  get() { return this; }
  destructor_Swimmer() {}
}

class Duck extends Walker {
  constructor() {
    super();
  }
  sound() {
    return string("Quack");
  }
  get() { return this; }
  destructor_Duck() {}
}
if (typeof Swimmer !== 'undefined') _mixin(Duck, Swimmer);

class Vector2D {
  constructor(x = 0, y = 0) {
    if (isinstance(x, Vector2D)) {
      let o = x;
      this.x_ = o.x_;
      this.y_ = o.y_;
      o.x_ = null;
      ++Vector2D.instance_count_;
    } else {
      this.x_ = x;
      this.y_ = y;
      ++Vector2D.instance_count_;
    }
    const __fn = (...args) => (this.operator_call ? this.operator_call(...args) : undefined);
    Object.setPrototypeOf(__fn, Object.getPrototypeOf(this));
    Object.assign(__fn, this);
    return new Proxy(__fn, {
      get(t, p, r) {
        if (typeof p === 'string' && /^\d+$/.test(p) && typeof t.operator_subscript === 'function') {
          return t.operator_subscript(Number(p));
        }
        return Reflect.get(t, p, r);
      }
    });
  }
  destructor_Vector2D() {
    --Vector2D.instance_count_;
  }
  operator_assign(o) {
    this.x_ = o.x_;
    this.y_ = o.y_;
    return _deref(this);
  }
  operator_add(o) {
    return new Vector2D(_add(this.x_, o.x_), _add(this.y_, o.y_));
  }
  operator_sub(o) {
    return new Vector2D(_sub(this.x_, o.x_), _sub(this.y_, o.y_));
  }
  operator_mul(s) {
    return new Vector2D(_mul(this.x_, s), _mul(this.y_, s));
  }
  operator_add_assign(o) {
    if (this.x_ && typeof this.x_.append === 'function') this.x_.append(o.x_); else if (this.x_ && typeof this.x_.operator_add_assign === 'function') this.x_.operator_add_assign(o.x_); else this.x_ += o.x_;
    if (this.y_ && typeof this.y_.append === 'function') this.y_.append(o.y_); else if (this.y_ && typeof this.y_.operator_add_assign === 'function') this.y_.operator_add_assign(o.y_); else this.y_ += o.y_;
    return _deref(this);
  }
  operator_inc() {
    ++this.x_;
    ++this.y_;
    return _deref(this);
  }
  operator_post_inc() {
    let t = new Vector2D(_deref(this));
    ++_deref(this);
    return new Vector2D(t);
  }
  operator_eq(o) {
    return (_eq(this.x_, o.x_) && _eq(this.y_, o.y_));
  }
  operator_ne(o) {
    return _not(_eq(_deref(this), o));
  }
  operator_subscript(i) {
    return (_eq(i, 0) ? this.x_ : this.y_);
  }
  operator_call(k) {
    return _mul(k, _add(this.x_, this.y_));
  }
  operator_bool() {
    return (_ne(this.x_, 0) || _ne(this.y_, 0));
  }
  static count() {
    return Vector2D.instance_count_;
  }
  length() {
    return std.sqrt(_add(_mul(this.x_, this.x_), _mul(this.y_, this.y_)));
  }
  __str__(self) {
    return _shift(_shift(_shift(_shift(_shift(os, "("), v.x_), ", "), v.y_), ")");
  }
  toString() { return `(${this.x_}, ${this.y_})`; }
  [Symbol.toPrimitive]() { return `(${this.x_}, ${this.y_})`; }
  [Symbol.for('nodejs.util.inspect.custom')]() { return `(${this.x_}, ${this.y_})`; }
  length() { return Math.sqrt(this.x_ * this.x_ + this.y_ * this.y_); }
  get() { return this; }
  destructor_Vector2D() {}
}

Vector2D.instance_count_ = 0;
function dot(a, b) {
  return _add(_mul(a.x_, b.x_), _mul(a.y_, b.y_));
}

function max_of(a, b) {
  return ((a > b) ? a : b);
}

class FixedArray extends Array {
  constructor() {
    super(5).fill(0);
  }
  size() { return 5; }
}

class Box {
  constructor(v = null, is_ptr = false) {
    this.value_ = v;
    this.is_ptr = is_ptr;
  }
  get() {
    return (this.value_ && typeof this.value_ === 'object' && '_val' in this.value_) ? this.value_._val : this.value_;
  }
  type() {
    if (this.is_ptr || (this.value_ && typeof this.value_ === 'object' && '_val' in this.value_)) return 'pointer-specialized';
    if (typeof this.value_ === 'boolean') return 'bool-specialized';
    return 'generic';
  }
}

function sum_all(...args) {
  return args.reduce((a, b) => a + b, 0);
}

function print_all(...args) {
  process.stdout.write(args.join(', '));
}

function describe_type(x) {
  if (typeof x === 'boolean') return 'bool';
  if (typeof x === 'number') return Number.isInteger(x) ? 'integral' : 'floating';
  return 'unknown';
}

class Fact {
  static value = 120;
}

function factorial(n) {
  return ((n <= 1) ? 1 : _mul(n, factorial(_sub(n, 1))));
}

function fib(n) {
  return ((n < 2) ? n : _add(fib(_sub(n, 1)), fib(_sub(n, 2))));
}

function swap_ref(a, b) {
  t = a;
  a = b;
  b = t;
}

function swap_ptr(a, b) {
  t = _deref(a);
  if (Array.isArray(a)) a[0] = _deref(b); else a = _deref(b);
  if (Array.isArray(b)) b[0] = t; else b = t;
}

function with_default(a, b, c) {
  return _add(_add(a, b), c);
}

function cube(x) {
  return _mul(_mul(x, x), x);
}

function file_local_fn(x) {
  return _add(x, 1);
}

function must_use() {
  return 1;
}

function variadic_c_style(count) {
}

function gcd(a, b) {
  return (_eq(b, 0) ? a : gcd(b, (a % b)));
}

function is_prime(n) {
  if ((n < 2)) {
    return false;
  }
  for (let i = 2; (_mul(i, i) <= n); ++i) {
    if (_eq((n % i), 0)) {
      return false;
    }
  }
  return true;
}

function apply_op(op, a, b) {
  return op(a, b);
}

function op_add(a, b) {
  return _add(a, b);
}

function op_mul(a, b) {
  return _mul(a, b);
}

function trailing(a, b) {
  return _add(a, b);
}

class CustomError extends Error {
  constructor(msg = null, code = null) {
    super(msg);
    this.code_ = code;
  }
  code() {
    return this.code_;
  }
  get() { return this; }
  destructor_CustomError() {}
}

function risky(x) {
  if ((x < 0)) {
    throw (invalid_argument("negative value"));
  }
  if (_eq(x, 0)) {
    throw new CustomError(string("zero not allowed"), 404);
  }
  if ((x > 1000)) {
    throw (out_of_range("too large"));
  }
  return _mul(x, 2);
}

class Resource {
  constructor(id = null) {
    this.id_ = std.move(id);
    console.log("  [ctor ", this.id_, "]\\n");
  }
  destructor_Resource() {
    console.log("  [dtor ", this.id_, "]\\n");
  }
  use() {
    console.log("  using ", this.id_);
  }
  use_count() { return 1; }
  reset() {}
  get() { return this; }
  get() { return this; }
  destructor_Resource() {}
}

class Node {
  constructor(d = null) {
    this.data = d;
    this.next = null;
  }
  get() { return this; }
  destructor_Node() {}
}

function push_front(head, v) {
  let n = new Node(v);
  n.next = head;
  return n;
}

function free_list(head) {
  while (head) {
    t = head.next;
    0;
    head = t;
  }
}

class TreeNode {
  constructor(v = 0) {
    this.val = v;
    this.left = null;
    this.right = null;
  }
}

function tree_insert(root, v) {
  if (_not(root)) {
    root = new TreeNode(v);
    return;
  }
  if ((v < root.val)) {
    tree_insert(root.left, v);
  } else {
    tree_insert(root.right, v);
  }
}

function tree_inorder(root, out) {
  if (_not(root)) {
    return;
  }
  tree_inorder(root.left, out);
  out.push_back(root.val);
  tree_inorder(root.right, out);
}

let g_mutex = mutex();
let g_atomic_counter = atomic(0);
function thread_worker(id, iterations) {
  for (let i = 0; (i < iterations); ++i) {
    g_atomic_counter.fetch_add(1);
    let lock = lock_guard(g_mutex);
    if (g_counter && typeof g_counter.append === 'function') g_counter.append(id); else if (g_counter && typeof g_counter.operator_add_assign === 'function') g_counter.operator_add_assign(id); else g_counter += id;
  }
}

function section(title) {
  console.log("\\n=== ", title, " ===\\n");
}

function test_basic_types_and_operators() {
  section(string("Basic types & operators"));
  let c = "A";
  let s = 100;
  let i = 42;
  let l = 1234567;
  let ll = 9876543210;
  let ui = 4000000000;
  let f = 3.14;
  let d = 2.718281828;
  let ld = (1.0 / 3);
  let b = true;
  let wc = "W";
  let c16 = "x";
  let c32 = "y";
  let i8 = -8;
  let u16 = 65535;
  let i64 = -1;
  let sz = 4;
  console.log(c, " ", s, " ", i, " ", l, " ", ll, " ", ui);
  console.log(f, " ", d, " ", ld, " ", std.boolalpha, b);
  console.log((wc), " ", (c16), " ", (c32), " ", (i8), " ", u16, " ", i64, " ", sz);
  let a = 17;
  let bb = 5;
  console.log(_add(a, bb), " ", _sub(a, bb), " ", _mul(a, bb), " ", (a / bb), " ", (a % bb));
  console.log((a & bb), " ", (a | bb), " ", (a ^ bb), " ", ~a, " ", _shift(a, 2), " ", (a >> 1));
  console.log(((a > bb) && (bb > 0)), " ", ((a < bb) || _eq(bb, 5)), " ", _not(b));
  t = ((a > bb) ? a : bb);
  if (t && typeof t.append === 'function') t.append(3); else if (t && typeof t.operator_add_assign === 'function') t.operator_add_assign(3); else t += 3;
  t -= 1;
  t *= 2;
  t /= 3;
  t %= 7;
  t <<= 2;
  t >>= 1;
  t &= 255;
  t |= 1;
  t ^= 16;
  console.log("t=", t);
  let x = 5;
  let y = x++;
  if (y && typeof y.append === 'function') y.append(++x); else if (y && typeof y.operator_add_assign === 'function') y.operator_add_assign(++x); else y += ++x;
  console.log("x=", x, " y=", y);
  let hex = 255;
  let oct = 63;
  let bin = 10;
  let big = 1000000;
  console.log(hex, " ", oct, " ", bin, " ", big);
  console.log(1500.0, " ", _add("a", 1), " ", "str", " ", "raw\\nstring");
  let pi = 3.99;
  let truncated = (pi);
  let cp = i;
  let mp = (cp);
  let vp = i;
  let ip = (vp);
  let fbits = 1.0;
  let ubits = (fbits);
  console.log(truncated, " ", _deref(mp), " ", _deref(ip), " ", std.hex, ubits, std.dec);
  console.log(1, 4, 8, " ", std.numeric_limits.max(), " ", std.numeric_limits.epsilon());
  console.log(null, " ", MAX_SIZE, " ", "STRINGIFY(hello)", " ");
  let var1 = 10;
  console.log(var1);
}

function test_control_flow() {
  section(string("Control flow"));
  for (let i = 0; (i < 3); ++i) {
    console.log(i, " ");
  }
  console.log();
  let w = 0;
  while ((w < 3)) {
    console.log(w++, " ");
  }
  console.log();
  let dw = 0;
  while ((dw < 3)) {
    console.log(dw, " ");
    ++dw;
  }
  console.log();
  for (let i = 0; (i < 10); ++i) {
    if (_eq(i, 2)) {
      continue;
    }
    if (_eq(i, 6)) {
      break;
    }
    console.log(i, " ");
  }
  console.log();
  for (let i = 1; (i <= 3); ++i) {
    for (let j = 1; (j <= 3); ++j) {
      if (_eq(j, 3)) {
        0;
      }
      console.log(_mul(i, j), " ");
      0;
    }
  }
  console.log();
  for (let v = 0; (v < 5); ++v) {
    switch (v) {
      case 0:
        console.log("zero ");
      case 1:
        0;
      case 3:
        console.log("three ");
      default:
        console.log("default ");
    }
  }
  console.log();
  let k = 5;
  if ((k > 3)) {
    console.log("init-if ", k);
  } else {
    console.log("else\\n");
  }
  for (let a = 0, b = 10; (a < b); a += 3, b -= 3) {
    console.log(a, ":", b, " ");
  }
  console.log();
  let col = GREEN;
  switch (col) {
    case RED:
      console.log("R\\n");
    case GREEN:
      console.log("G\\n");
    default:
      break;
  }
  let dir = South;
  console.log((dir), " ", BLUE);
}

function test_arrays_pointers_references() {
  section(string("Arrays / pointers / references"));
  let arr = [1, 2, 3, 4, 5];
  let matrix = [[1, 2, 3], [4, 5, 6]];
  let cstr = "hello";
  let p = arr;
  console.log(_deref(p), " ", _deref(_add(p, 2)), " ", p[4], " ", arr[1]);
  for (let r = 0; (r < 2); ++r) {
    for (let c = 0; (c < 3); ++c) {
      console.log(matrix[r][c], " ");
    }
  }
  console.log(cstr, " ", std.strlen(cstr));
  let a = 1;
  let b = 2;
  swap_ref(a, b);
  console.log(a, b, " ");
  swap_ptr(a, b);
  console.log(a, b);
  let pp = p;
  console.log(_deref(_deref(pp)));
  let ref = arr[3];
  ref = 40;
  console.log(arr[3]);
  let cref = a;
  console.log(cref);
  let rref = 10;
  console.log(rref);
  let dyn = 7;
  let dyn_arr = [1, 2, 3, 4];
  console.log(_deref(dyn), " ", dyn_arr[3]);
  0;
  0;
  let np = null;
  console.log(_eq(np, null));
  let pt = new Point(3, 4);
  let ppt = pt;
  console.log(ppt.x, " ", _deref(ppt).y);
  let mem = (std.malloc(_mul(3, 4)));
  mem[0] = 9;
  mem[1] = 8;
  mem[2] = 7;
  console.log(_add(_add(mem[0], mem[1]), mem[2]));
  std.free(mem);
  let px = pt.x;
  let py = pt.y;
  console.log(px, ",", py);
  let u = new IntOrFloat();
  u.f = 1.0;
  console.log(std.hex, u.i, std.dec);
  let fl = new Flags(1, 5, 9);
  console.log(fl.a, fl.b, fl.c);
}

function test_strings() {
  section(string("Strings"));
  let s = string("Hello, World");
  if (s && typeof s.append === 'function') s.append("!"); else if (s && typeof s.operator_add_assign === 'function') s.operator_add_assign("!"); else s += "!";
  console.log(s, " len=", s.length, " ", s.substr(7, 5), " ", s.find("World"));
  s.replace(0, 5, "HELLO");
  console.log(s);
  s.insert(5, "***");
  console.log(s);
  s.erase(5, 3);
  console.log(s, " ", s.front(), s.back());
  std.transform(s.begin(), s.end(), s.begin(), ((ch) => std.tolower(ch)));
  console.log(s, " ", _eq(s, "hello, world!"), " ", s.compare("abc"));
  let sv = string_view("view of text");
  console.log(sv.substr(0, 4), " ", sv.size());
  console.log(_add(std.stoi(string("123")), 1), " ", _mul(std.stod(string("2.5")), 2), " ", std.to_string(3.5));
  let oss = ostringstream();
  _shift(_shift(_shift(_shift(_shift(_shift(_shift(_shift(_shift(_shift(_shift(oss, "num="), 42), " pi="), std.fixed), std.setprecision(3)), 3.14159), " ["), std.setw(6)), std.setfill(".")), 7), "]");
  console.log(oss.str());
  let iss = istringstream(string("10 20 30"));
  let n;
  let total = 0;
  while (true) {
    const _tok = iss.get();
    if (_tok === null || _tok === undefined) break;
    n = _tok;
    if (total && typeof total.append === 'function') total.append(n); else if (total && typeof total.operator_add_assign === 'function') total.operator_add_assign(n); else total += n;
  }
  console.log("total=", total);
  let csv = string("a,b,c");
  let ss = stringstream(csv);
  let tok = string();
  while (std.getline(ss, tok, ",")) {
    console.log("<", tok, ">");
  }
  console.log();
  let buf = new _char_buf(64);
  std.snprintf(buf, (buf?.length || 4), "%05d|%.2f|%s|%c|%x", 42, 3.14159, "str", "z", 255);
  console.log(buf);
  std.printf("printf: %d %s\\n", 7, "ok");
  console.log(std.isalpha("a"), std.isdigit("5"), std.toupper("q"));
  console.log(std.strcmp("a", "b"), " ", std.atoi("77"));
  let lit = string("literal");
  console.log(lit.size());
}

function test_stl_containers() {
  section(string("STL containers"));
  let v = vector([5, 3, 8, 1, 9, 2]);
  v.push_back(7);
  v.emplace_back(4);
  v.insert(_add(v.begin(), 1), 100);
  v.pop_back();
  console.log("vec size=", v.size(), " front=", v.front(), " back=", v.back());
  std.sort(v.begin(), v.end());
  for (const x of v) {
    console.log(x, " ");
  }
  console.log();
  v.erase(std.remove(v.begin(), v.end(), 100), v.end());
  console.log(std.binary_search(v.begin(), v.end(), 8));
  let a = std.array(1, 2, 3, 4);
  console.log(a.size(), a.at(2));
  let lst = list([3, 1, 2]);
  lst.push_front(0);
  lst.sort();
  lst.reverse();
  for (const x of lst) {
    console.log(x);
  }
  console.log();
  let dq = deque([1, 2]);
  dq.push_front(0);
  dq.push_back(3);
  console.log(dq.front(), dq.back(), dq[2]);
  let fl = forward_list([1, 2, 3]);
  fl.push_front(0);
  for (const x of fl) {
    console.log(x);
  }
  console.log();
  let m = map([["one", 1], ["two", 2]]);
  m[string("three")] = 3;
  m.insert(pair(string("four"), 4));
  m.emplace("five", 5);
  for (const [k, val] of m) {
    console.log(k, "=", val, " ");
  }
  console.log();
  let it = m.find(string("two"));
  if (_ne(it, m.end())) {
    console.log("found ", it.second);
  }
  console.log(m.count(string("zzz")), " ", m.size());
  let um = unordered_map([[1, "a"], [2, "b"]]);
  um[3] = "c";
  console.log(um.at(3), um.size());
  let st = set([3, 1, 2, 3, 1]);
  st.insert(10);
  for (const x of st) {
    console.log(x, " ");
  }
  console.log(st.count(2));
  let us = unordered_set(["x", "y"]);
  us.insert(string("z"));
  console.log(us.size(), us.count(string("x")));
  let ms = multiset([1, 1, 2]);
  console.log(ms.count(1));
  let mm = multimap([[1, "a"], [1, "b"]]);
  console.log(mm.count(1));
  let stk = stack();
  stk.push(1);
  stk.push(2);
  console.log(stk.top());
  stk.pop();
  console.log(stk.size());
  let q = queue();
  q.push(1);
  q.push(2);
  console.log(q.front(), q.back());
  q.pop();
  console.log(q.size());
  let pq = priority_queue();
  pq.push(3);
  pq.push(9);
  pq.push(1);
  console.log(pq.top());
  let minpq = priority_queue();
  minpq.push(3);
  minpq.push(1);
  console.log(minpq.top());
  let pr = pair(1, string("pair"));
  let pr2 = std.make_pair(2, 3.5);
  console.log(pr.first, pr.second, pr2.second);
  let tp = tuple(1, 2.5, string("tuple"));
  console.log(tp[0], tp[1], tp[2]);
  let t1 = tp[0];
  let t2 = tp[1];
  let t3 = tp[2];
  console.log(t1, t2, t3);
  let ta;
  let tb;
  [ta, tb, _] = tp;
  console.log(ta, tb);
  let bs = bitset(178);
  console.log(bs, " ", bs.count(), " ", bs.test(1), " ", bs.to_ulong());
  let grid = vector(3, vector(3, 0));
  for (let i = 0; (i < 3); ++i) {
    grid[i][i] = 1;
  }
  for (const row of grid) {
    for (const x of row) {
      console.log(x);
    }
    console.log(" ");
  }
  console.log();
}

function test_algorithms_and_lambdas() {
  section(string("Algorithms & lambdas"));
  let v = vector([4, 2, 9, 1, 7, 3]);
  let add = ((a, b) => _add(a, b));
  let base = 10;
  let cap_val = ((x) => _add(x, base));
  let cap_ref = ((x) => {
  if (base && typeof base.append === 'function') base.append(x); else if (base && typeof base.operator_add_assign === 'function') base.operator_add_assign(x); else base += x;
});
  let cap_all = (() => _mul(base, 2));
  let generic = ((a, b) => _add(a, b));
  let mutable_l = ((() => { let count = 0; return () => ++count; })());
  console.log(add(1, 2), cap_val(5), generic(1.5, 2));
  cap_ref(5);
  console.log(base, " ", cap_all(), " ", mutable_l(), mutable_l());
  let fact_fn = ((n) => ((n <= 1) ? 1 : _mul(n, fact_fn(_sub(n, 1)))));
  console.log(fact_fn(5));
  std.sort(v.begin(), v.end(), ((a, b) => (a > b)));
  for (const x of v) {
    console.log(x, " ");
  }
  console.log();
  console.log(std.accumulate(v.begin(), v.end(), 0), " ", std.accumulate(v.begin(), v.end(), 1, multiplies()));
  console.log(_deref(std.max_element(v.begin(), v.end())), _deref(std.min_element(v.begin(), v.end())));
  console.log(std.count_if(v.begin(), v.end(), ((x) => _eq((x % 2), 1))));
  console.log(std.any_of(v.begin(), v.end(), ((x) => (x > 8))), std.all_of(v.begin(), v.end(), ((x) => (x > 0))), std.none_of(v.begin(), v.end(), ((x) => (x > 100))));
  let it = std.find(v.begin(), v.end(), 7);
  console.log((_ne(it, v.end()) ? std.distance(v.begin(), it) : -1));
  let it2 = std.find_if(v.begin(), v.end(), ((x) => (x < 3)));
  console.log(_deref(it2));
  let sq = vector(v.size());
  std.transform(v.begin(), v.end(), sq.begin(), ((x) => _mul(x, x)));
  for (const x of sq) {
    console.log(x, " ");
  }
  console.log();
  std.for_each(v.begin(), v.end(), ((x) => {
  if (x && typeof x.append === 'function') x.append(1); else if (x && typeof x.operator_add_assign === 'function') x.operator_add_assign(1); else x += 1;
}));
  std.reverse(v.begin(), v.end());
  std.rotate(v.begin(), _add(v.begin(), 2), v.end());
  for (const x of v) {
    console.log(x, " ");
  }
  console.log();
  let iota_v = vector(5);
  std.iota(iota_v.begin(), iota_v.end(), 10);
  let part = vector(5);
  std.partial_sum(iota_v.begin(), iota_v.end(), part.begin());
  for (const x of part) {
    console.log(x, " ");
  }
  console.log();
  let a = vector([1, 2, 3, 4]);
  let b = vector([3, 4, 5]);
  let out = vector();
  std.set_intersection(a.begin(), a.end(), b.begin(), b.end(), std.back_inserter(out));
  for (const x of out) {
    console.log(x);
  }
  console.log();
  let uq = std.unique(a.begin(), a.end());
  (uq);
  let fill_v = vector(4);
  std.fill(fill_v.begin(), fill_v.end(), 7);
  std.copy(fill_v.begin(), fill_v.end(), ostream_iterator(std.cout, ","));
  console.log();
  let partitioned = vector([1, 2, 3, 4, 5, 6]);
  std.partition(partitioned.begin(), partitioned.end(), ((x) => _eq((x % 2), 0)));
  std.nth_element(partitioned.begin(), _add(partitioned.begin(), 2), partitioned.end());
  console.log(partitioned[2]);
  console.log(_sub(std.lower_bound(sq.begin(), sq.end(), 0), sq.begin()));
  std.next_permutation(a.begin(), a.end());
  console.log(std.gcd(12, 18), std.lcm(4, 6));
  let bound = std.bind(add, 100, std.placeholders._1);
  console.log(bound(5));
  let fn = op_mul;
  console.log(fn(3, 4));
  console.log(apply_op(op_add, 2, 3), apply_op(((a, b) => _sub(a, b)), 9, 4));
}

function test_classes_and_polymorphism() {
  section(string("Classes & polymorphism"));
  let shapes = vector();
  shapes.push_back(new Circle(2.0));
  shapes.push_back(new Rectangle(3, 4));
  shapes.push_back(new Square(5));
  console.log(std.fixed, std.setprecision(2));
  for (const sh of shapes) {
    console.log(sh.describe(), " perim=", sh.perimeter());
  }
  let raw = shapes[0].get();
  let c = (raw instanceof Circle ? raw : null);
  if (c) {
    console.log("is Circle\\n");
  }
  if (_eq((raw instanceof Rectangle ? raw : null), null)) {
    console.log("not Rectangle\\n");
  }
  console.log(name());
  std.cout.unsetf(ios_base.floatfield);
  let d = new Duck();
  console.log(d.sound(), d.walk(), d.swim());
  let v1 = new Vector2D(1, 2);
  let v2 = new Vector2D(3, 4);
  let v3 = _add(v1, v2);
  if (v3 && typeof v3.append === 'function') v3.append(new Vector2D(1, 1)); else if (v3 && typeof v3.operator_add_assign === 'function') v3.operator_add_assign(new Vector2D(1, 1)); else v3 += new Vector2D(1, 1);
  ++v3;
  v3++;
  console.log(v3, " ", _eq(v1, v2), _ne(v1, v2), " ", v1[0], v2(2.0), " ", dot(v1, v2), " ", Vector2D.count(), " ", (v1));
  let moved = new Vector2D(std.move(v3));
  console.log(moved, v3);
  console.log(_mul(v1, 3.0), " ", (v2 - v1).length);
}

function test_templates() {
  section(string("Templates"));
  console.log(max_of(3, 7), max_of(2.5, 1.5), std.max_of(string("a"), string("b")));
  let fa = new FixedArray();
  fa[2] = 9;
  console.log(fa[2], fa.size());
  let bi = new Box(5);
  let bb = new Box(true);
  let val = 77;
  let bp = new Box(val);
  console.log(bi.type(), bb.type(), bp.type(), bp.get());
  console.log(sum_all(1, 2, 3, 4), sum_all(1.5, 2.5));
  print_all(1, "two", 3.0, "c");
  console.log();
  console.log(describe_type(5), describe_type(2.5));
  console.log(Fact.value, " ", fib(10));
  const cx = fib(8);
  let vv = vector([1, 2]);
  let iv = vector([3]);
  let sm = map([["k", 1]]);
  console.log(vv.size(), iv.size(), sm.size());
  console.log(true, true, true);
}

function test_exceptions() {
  section(string("Exceptions"));
  let inputs = [5, -1, 0, 5000];
  for (const in_ of inputs) {
    try {
      console.log("risky(", in_, ")=", risky(in_));
    } catch (__err) {
      if ((__err instanceof CustomError || (__err && __err.name === 'CustomError') || (__err && __err.constructor && __err.constructor.name === 'CustomError'))) {
        let e = __err;
        console.log("CustomError: ", e.what(), " code=", e.code());
      } else if ((__err instanceof std.invalid_argument || (__err && __err.name === 'std.invalid_argument') || (__err && __err.constructor && __err.constructor.name === 'std.invalid_argument'))) {
        let e = __err;
        console.log("invalid_argument: ", e.what());
      } else if ((__err instanceof Error || (__err && __err.name === 'Error') || (__err && __err.constructor && __err.constructor.name === 'Error'))) {
        let e = __err;
        console.log("std::exception: ", e.what());
      } else {
        let e = __err;
        console.log("unknown\\n");
      }
    }
  }
  try {
    try {
      throw (runtime_error("inner"));
    } catch (__err) {
      if ((__err instanceof Error || (__err && __err.name === 'Error') || (__err && __err.constructor && __err.constructor.name === 'Error'))) {
        let e = __err;
        console.log("rethrowing\\n");
        throw (typeof __err !== 'undefined' ? __err : new Error());
      } else {
        throw __err;
      }
    }
  } catch (__err) {
    if ((__err instanceof Error || (__err && __err.name === 'Error') || (__err && __err.constructor && __err.constructor.name === 'Error'))) {
      let e = __err;
      console.log("outer caught ", e.what());
    } else {
      throw __err;
    }
  }
  try {
    let v = vector(2);
    v.at(10);
  } catch (__err) {
    if ((__err instanceof std.out_of_range || (__err && __err.name === 'std.out_of_range') || (__err && __err.constructor && __err.constructor.name === 'std.out_of_range'))) {
      let e = __err;
      console.log("vector out_of_range\\n");
    } else {
      throw __err;
    }
  }
  try {
    throw 42;
  } catch (__err) {
    if (typeof __err === 'number') {
      let x = __err;
      console.log("int thrown ", x);
    } else {
      throw __err;
    }
  }
  try {
    throw (string("string thrown"));
  } catch (__err) {
    if ((__err instanceof std.string || (__err && __err.name === 'std.string') || (__err && __err.constructor && __err.constructor.name === 'std.string'))) {
      let s = __err;
      console.log(s);
    } else {
      throw __err;
    }
  }
  let safe = (() => 1);
  console.log(true);
  (assert(1 + 1 == 2));
}

function test_smart_pointers_and_memory() {
  section(string("Smart pointers & memory"));
  let u = new Resource("unique");
  u.use();
  let u2 = std.move(u);
  console.log(_eq(u, null));
  let s1 = new Resource("shared");
  let s2 = s1;
  let w = weak_ptr(s1);
  console.log("use_count=", s1.use_count(), " expired=", w.expired());
  s1.reset();
  let locked = w.lock();
  if (locked) {
    locked.use();
  }
  let head = null;
  for (let i = 1; (i <= 4); ++i) {
    head = push_front(head, i);
  }
  for (let n = head; n; n = n.next) {
    console.log(n.data, " ");
  }
  console.log();
  free_list(head);
  let root = unique_ptr();
  for (const x of [5, 3, 8, 1, 4, 9]) {
    tree_insert(root, x);
  }
  let sorted = vector();
  tree_inorder(root, sorted);
  for (const x of sorted) {
    console.log(x, " ");
  }
  console.log();
  let arr = _mul([0], 3);
  arr[0] = 1;
  arr[2] = 3;
  console.log(_add(arr[0], arr[2]));
  let buffer = new _char_buf(8);
  let placed = new Point(8, 9);
  console.log(placed.x, placed.y);
  placed.destructor_Point();
}

function test_optional_variant_any() {
  section(string("optional / variant / any"));
  let o1 = optional(5);
  let o2 = optional();
  console.log(o1.has_value(), o2.has_value(), o1.value_or(0), o2.value_or(-1));
  if (o1) {
    console.log(_deref(o1));
  }
  let var_ = variant(3.14);
  console.log(var_.index(), std.get(var_));
  var_ = variant((string("now string")));
  std.visit(((arg) => {
  console.log("visited: ", arg);
}), var_);
  if (std.std.holds_alternative(var_)) {
    console.log("holds string\\n");
  }
  let a = any(10);
  console.log(std.any_cast(a));
  a = any((string("any-string")));
  console.log(std.std.any_cast(a));
}

function test_chrono_random_regex() {
  section(string("chrono / random / regex"));
  let start = std.chrono.now();
  std.this_thread.sleep_for((milliseconds(5)));
  let end = std.chrono.now();
  let ms = std.chrono.duration_cast();
  console.log("elapsed>=5ms: ", (ms >= 4));
  let gen = mt19937(12345);
  let dist = uniform_int_distribution(1, 6);
  let rdist = uniform_real_distribution(0.0, 1.0);
  let ndist = normal_distribution(0.0, 1.0);
  let roll = dist(gen);
  let r = rdist(gen);
  (ndist);
  console.log(((roll >= 1) && (roll <= 6)), ((r >= 0) && (r < 1)));
  let shuf = vector([1, 2, 3, 4, 5]);
  std.shuffle(shuf.begin(), shuf.end(), gen);
  std.srand(1);
  let rr = std.rand();
  (rr);
  let re = regex("(\\w+)@(\\w+)\\.com");
  let m = smatch();
  let email = string("contact: alice@example.com now");
  if (std.regex_search(email, m, re)) {
    console.log(m[1], " at ", m[2]);
  }
  console.log(std.regex_replace(string("a1b22c333"), (regex("[0-9]+")), string("#")));
  console.log(std.regex_match(string("abc123"), (regex("[a-z]+[0-9]+"))));
  let now = std.time(null);
  (now);
  let clk = std.clock();
  (clk);
}

function test_math() {
  section(string("cmath"));
  console.log(std.fixed, std.setprecision(4));
  console.log(std.sqrt(16.0), " ", std.pow(2, 10), " ", std.abs(-3.5), " ", std.floor(2.7), " ", std.ceil(2.1), " ", std.round(2.5), " ", std.fmod(7.5, 2));
  console.log(std.sin((math_utils.PI / 2)), " ", std.cos(0.0), " ", std.tan(0.0), " ", std.atan2(1, 1), " ", std.exp(1.0), " ", std.log(std.exp(2.0)), " ", std.log10(1000.0), " ", std.hypot(3, 4));
  std.cout.unsetf(ios_base.floatfield);
  console.log(std.abs(-7), " ", std.isnan(std.nan("")), " ", std.isinf(__builtin_inff()));
  console.log(math_utils.add(1, 2), " ", math_utils.add(1.5, 2.5), " ", alias_target.triple(4), " ", math_utils.nested.triple(2));
  console.log(factorial(6), " ", gcd(48, 18), " ", is_prime(97), " ", with_default(1), with_default(1, 2), with_default(1, 2, 3), " ", cube(3), " ", file_local_fn(1), " ", trailing(2, 3), " ", must_use(), " ", G_CONST, G_CONSTEXPR, s_static_global, g_extern_decl);
}

function test_file_io() {
  section(string("File I/O"));
  let path = "transpiler_test_tmp.txt";
  let out = ofstream(path);
  _shift(out, "line one\\nline two\\n42 3.14\\n");
  let in_ = ifstream(path);
  let line = string();
  while (std.getline(in_, line)) {
    console.log("read: ", line);
  }
  let app = ofstream(path, std.app);
  _shift(app, "appended\\n");
  in_ = ifstream(path);
  let word = string();
  let count = 0;
  while (true) {
    const _tok = in_.get();
    if (_tok === null || _tok === undefined) break;
    word = _tok;
    ++count;
  }
  console.log("words=", count);
  std.remove(path);
  console.log("(this line goes to stderr)\\n");
  console.log("(this line goes to clog)\\n");
}

function test_threads() {
  section(string("Threads / async / sync"));
  g_counter = 0;
  g_atomic_counter = atomic(0);
  let threads = vector();
  for (let i = 1; (i <= 4); ++i) {
    threads.emplace_back(thread(thread_worker, i, 1000));
  }
  for (const t of threads) {
    t.join();
  }
  console.log("atomic=", g_atomic_counter, " guarded=", g_counter);
  let fut = std.async(std.async, (() => factorial(5)));
  console.log("async result=", fut.get());
  let prom = promise();
  let pf = prom.get_future();
  t = thread((() => prom.set_value(99)));
  console.log("promise=", pf.get());
  t.join();
  let m = mutex();
  let cv = condition_variable();
  let ready = false;
  let waiter = thread((() => {
  console.log("cv signaled\\n");
}));
  let lk = lock_guard(m);
  ready = true;
  cv.notify_one();
  waiter.join();
  let tls = 0;
  ++tls;
  console.log("tls=", tls);
}

class Range {
  constructor(lo = null, hi = null) {
    this.lo_ = lo;
    this.hi_ = hi;
  }
  begin() {
    return [this.lo_];
  }
  end() {
    return [this.hi_];
  }
  *[Symbol.iterator]() {
    for (let i = this.lo_; i < this.hi_; i++) {
      yield i;
    }
  }
  get() { return this; }
  destructor_Range() {}
}

function test_custom_iterables_and_misc() {
  section(string("Custom iterables & misc"));
  for (const x of new Range(0, 5)) {
    console.log(x, " ");
  }
  console.log();
  let init = std.initializer_list(1, 2, 3);
  console.log(init.size());
  let lst_sum = ((il) => {
  let s = 0;
  for (const x of il) {
    if (s && typeof s.append === 'function') s.append(x); else if (s && typeof s.operator_add_assign === 'function') s.operator_add_assign(x); else s += x;
  }
  return s;
});
  console.log(lst_sum([1, 2, 3, 4]));
  let dref = g_counter;
  (dref);
  let fptr = factorial;
  console.log(fptr(4));
  let member_ptr = "x";
  let pt = new Point(11, 22);
  console.log(pt[member_ptr]);
  console.log(__LINE__, " ", _ne("__FILE__", null), " ", "__func__", " ", __cplusplus);
  console.log("debug on\\n");
  let vol = 3;
  0;
  console.log(vol);
  let p1 = new Point(1, 2);
  let p2 = new Point(1, 2);
  console.log(_eq(p1, p2));
  console.log(std.boolalpha, _eq(p1, p2), std.noboolalpha);
}

function main(argc, argv) {
  std.ios_base.sync_with_stdio(false);
  console.log("argc=", argc, " argv0_present=", _ne(argv[0], null));
  test_basic_types_and_operators();
  test_control_flow();
  test_arrays_pointers_references();
  test_strings();
  test_stl_containers();
  test_algorithms_and_lambdas();
  test_classes_and_polymorphism();
  test_templates();
  test_exceptions();
  test_smart_pointers_and_memory();
  test_optional_variant_any();
  test_chrono_random_regex();
  test_math();
  test_file_io();
  test_threads();
  test_custom_iterables_and_misc();
  console.log("\\nAll sections completed.\\n");
  return EXIT_SUCCESS;
}


if (typeof main === "function") {
  try { main(1, ["./program"]); } catch (e) { console.error(e); process.exit(1); }
}
