// ============================================================================
// transpiler_test.cpp
// A kitchen-sink C++17 program for stress-testing a C++ transpiler.
// Build:  g++ -std=c++17 -Wall -Wextra -pthread transpiler_test.cpp -o test
// ============================================================================

// ---------- Standard library includes ----------
#include <iostream>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <list>
#include <deque>
#include <forward_list>
#include <map>
#include <unordered_map>
#include <set>
#include <unordered_set>
#include <stack>
#include <queue>
#include <tuple>
#include <utility>
#include <algorithm>
#include <numeric>
#include <functional>
#include <iterator>
#include <memory>
#include <optional>
#include <variant>
#include <any>
#include <bitset>
#include <chrono>
#include <random>
#include <regex>
#include <thread>
#include <mutex>
#include <atomic>
#include <future>
#include <condition_variable>
#include <stdexcept>
#include <exception>
#include <limits>
#include <type_traits>
#include <cmath>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <cassert>
#include <ctime>
#include <cctype>
#include <initializer_list>

// ---------- Macros / preprocessor ----------
#define SQUARE(x) ((x) * (x))
#define MAX_SIZE 100
#define STRINGIFY(x) #x
#define CONCAT(a, b) a##b
#ifndef DEBUG_LEVEL
#define DEBUG_LEVEL 1
#endif

// ---------- Namespaces ----------
namespace math_utils {
    constexpr double PI = 3.14159265358979323846;

    inline int add(int a, int b) { return a + b; }
    inline double add(double a, double b) { return a + b; }   // overload

    namespace nested {
        inline int triple(int x) { return 3 * x; }
    }
}

namespace alias_target = math_utils::nested;

// ---------- Global variables & constants ----------
int g_counter = 0;
const int G_CONST = 42;
constexpr int G_CONSTEXPR = 7;
static int s_static_global = 5;
extern int g_extern_decl;          // declaration
int g_extern_decl = 99;            // definition

// ---------- Enums ----------
enum Color { RED, GREEN = 5, BLUE };
enum class Direction : uint8_t { North = 1, East, South, West };

// ---------- Typedef / using ----------
typedef unsigned long ulong_t;
using IntVec = std::vector<int>;
using StrMap = std::map<std::string, int>;
template <typename T> using Vec = std::vector<T>;

// ---------- Struct & union ----------
struct Point {
    int x = 0;
    int y = 0;
    Point() = default;
    Point(int x_, int y_) : x(x_), y(y_) {}
    bool operator==(const Point& o) const { return x == o.x && y == o.y; }
};

union IntOrFloat {
    int i;
    float f;
};

struct Flags {
    unsigned int a : 1;
    unsigned int b : 3;
    unsigned int c : 4;
};

// ---------- Forward declarations ----------
class Shape;
int factorial(int n);

// ---------- Abstract base class / inheritance / polymorphism ----------
class Shape {
protected:
    std::string name_;
public:
    explicit Shape(std::string n) : name_(std::move(n)) {}
    virtual ~Shape() { }
    virtual double area() const = 0;               // pure virtual
    virtual double perimeter() const = 0;
    virtual std::string describe() const {
        return name_ + " area=" + std::to_string(area());
    }
    const std::string& name() const { return name_; }
};

class Circle : public Shape {
    double r_;
public:
    Circle(double r) : Shape("Circle"), r_(r) {}
    double area() const override { return math_utils::PI * r_ * r_; }
    double perimeter() const override { return 2 * math_utils::PI * r_; }
};

class Rectangle : public Shape {
protected:
    double w_, h_;
public:
    Rectangle(double w, double h) : Shape("Rectangle"), w_(w), h_(h) {}
    double area() const override { return w_ * h_; }
    double perimeter() const override { return 2 * (w_ + h_); }
};

class Square final : public Rectangle {
public:
    explicit Square(double s) : Rectangle(s, s) { name_ = "Square"; }
    std::string describe() const override { return "[Square] " + Rectangle::describe(); }
};

// ---------- Multiple inheritance & virtual inheritance ----------
class Animal { public: virtual std::string sound() const { return "..."; } virtual ~Animal() = default; };
class Walker : virtual public Animal { public: std::string walk() const { return "walking"; } };
class Swimmer : virtual public Animal { public: std::string swim() const { return "swimming"; } };
class Duck : public Walker, public Swimmer {
public:
    std::string sound() const override { return "Quack"; }
};

// ---------- Class with static members, const methods, friend, operator overloads ----------
class Vector2D {
    double x_, y_;
    static int instance_count_;
public:
    Vector2D(double x = 0, double y = 0) : x_(x), y_(y) { ++instance_count_; }
    Vector2D(const Vector2D& o) : x_(o.x_), y_(o.y_) { ++instance_count_; }
    Vector2D(Vector2D&& o) noexcept : x_(o.x_), y_(o.y_) { o.x_ = o.y_ = 0; ++instance_count_; }
    ~Vector2D() { --instance_count_; }

    Vector2D& operator=(const Vector2D& o) { x_ = o.x_; y_ = o.y_; return *this; }
    Vector2D operator+(const Vector2D& o) const { return Vector2D(x_ + o.x_, y_ + o.y_); }
    Vector2D operator-(const Vector2D& o) const { return Vector2D(x_ - o.x_, y_ - o.y_); }
    Vector2D operator*(double s) const { return Vector2D(x_ * s, y_ * s); }
    Vector2D& operator+=(const Vector2D& o) { x_ += o.x_; y_ += o.y_; return *this; }
    Vector2D& operator++() { ++x_; ++y_; return *this; }        // prefix
    Vector2D operator++(int) { Vector2D t(*this); ++(*this); return t; } // postfix
    bool operator==(const Vector2D& o) const { return x_ == o.x_ && y_ == o.y_; }
    bool operator!=(const Vector2D& o) const { return !(*this == o); }
    double& operator[](int i) { return i == 0 ? x_ : y_; }
    double operator()(double k) const { return k * (x_ + y_); }
    explicit operator bool() const { return x_ != 0 || y_ != 0; }

    static int count() { return instance_count_; }
    double length() const { return std::sqrt(x_ * x_ + y_ * y_); }

    friend std::ostream& operator<<(std::ostream& os, const Vector2D& v) {
        return os << "(" << v.x_ << ", " << v.y_ << ")";
    }
    friend double dot(const Vector2D& a, const Vector2D& b);
};
int Vector2D::instance_count_ = 0;
double dot(const Vector2D& a, const Vector2D& b) { return a.x_ * b.x_ + a.y_ * b.y_; }

// ---------- Templates: function, class, specialization, variadic, SFINAE ----------
template <typename T>
T max_of(T a, T b) { return (a > b) ? a : b; }

template <typename T, int N>
class FixedArray {
    T data_[N];
public:
    FixedArray() { for (int i = 0; i < N; ++i) data_[i] = T(); }
    T& operator[](int i) { return data_[i]; }
    constexpr int size() const { return N; }
};

template <typename T>
class Box {
    T value_;
public:
    Box(T v) : value_(v) {}
    T get() const { return value_; }
    std::string type() const { return "generic"; }
};

template <>                                   // full specialization
class Box<bool> {
    bool value_;
public:
    Box(bool v) : value_(v) {}
    bool get() const { return value_; }
    std::string type() const { return "bool-specialized"; }
};

template <typename T>
class Box<T*> {                               // partial specialization
    T* ptr_;
public:
    Box(T* p) : ptr_(p) {}
    T get() const { return *ptr_; }
    std::string type() const { return "pointer-specialized"; }
};

template <typename... Args>
auto sum_all(Args... args) { return (args + ...); }   // fold expression

template <typename T, typename... Rest>
void print_all(const T& first, const Rest&... rest) {
    std::cout << first;
    if constexpr (sizeof...(rest) > 0) {
        std::cout << ", ";
        print_all(rest...);
    }
}

template <typename T>
std::enable_if_t<std::is_integral_v<T>, std::string> describe_type(T) { return "integral"; }
template <typename T>
std::enable_if_t<std::is_floating_point_v<T>, std::string> describe_type(T) { return "floating"; }

template <int N> struct Fact { static constexpr int value = N * Fact<N - 1>::value; };
template <> struct Fact<0> { static constexpr int value = 1; };

// ---------- Functions: recursion, default args, pass by ref/ptr/value, inline, constexpr ----------
int factorial(int n) { return n <= 1 ? 1 : n * factorial(n - 1); }

constexpr int fib(int n) { return n < 2 ? n : fib(n - 1) + fib(n - 2); }

void swap_ref(int& a, int& b) { int t = a; a = b; b = t; }
void swap_ptr(int* a, int* b) { int t = *a; *a = *b; *b = t; }
int with_default(int a, int b = 10, int c = 20) { return a + b + c; }
inline int cube(int x) { return x * x * x; }
static int file_local_fn(int x) { return x + 1; }
[[nodiscard]] int must_use() { return 1; }
int variadic_c_style(int count, ...);  // declared only (skipped by va_list to keep it simple)

int gcd(int a, int b) { return b == 0 ? a : gcd(b, a % b); }
bool is_prime(int n) {
    if (n < 2) return false;
    for (int i = 2; i * i <= n; ++i) if (n % i == 0) return false;
    return true;
}

// Function pointer & typedef
typedef int (*BinaryOp)(int, int);
int apply_op(BinaryOp op, int a, int b) { return op(a, b); }
int op_add(int a, int b) { return a + b; }
int op_mul(int a, int b) { return a * b; }

// Trailing return type & decltype
auto trailing(int a, int b) -> decltype(a + b) { return a + b; }

// ---------- Exceptions ----------
class CustomError : public std::runtime_error {
    int code_;
public:
    CustomError(const std::string& msg, int code) : std::runtime_error(msg), code_(code) {}
    int code() const noexcept { return code_; }
};

int risky(int x) {
    if (x < 0) throw std::invalid_argument("negative value");
    if (x == 0) throw CustomError("zero not allowed", 404);
    if (x > 1000) throw std::out_of_range("too large");
    return x * 2;
}

// ---------- RAII / smart pointers ----------
class Resource {
    std::string id_;
public:
    explicit Resource(std::string id) : id_(std::move(id)) { std::cout << "  [ctor " << id_ << "]\n"; }
    ~Resource() { std::cout << "  [dtor " << id_ << "]\n"; }
    void use() const { std::cout << "  using " << id_ << "\n"; }
};

// ---------- Linked list / manual memory management ----------
struct Node {
    int data;
    Node* next;
    Node(int d) : data(d), next(nullptr) {}
};

Node* push_front(Node* head, int v) { Node* n = new Node(v); n->next = head; return n; }
void free_list(Node* head) { while (head) { Node* t = head->next; delete head; head = t; } }

// ---------- Binary tree with unique_ptr ----------
struct TreeNode {
    int val;
    std::unique_ptr<TreeNode> left, right;
    TreeNode(int v) : val(v) {}
};
void tree_insert(std::unique_ptr<TreeNode>& root, int v) {
    if (!root) { root = std::make_unique<TreeNode>(v); return; }
    if (v < root->val) tree_insert(root->left, v); else tree_insert(root->right, v);
}
void tree_inorder(const std::unique_ptr<TreeNode>& root, std::vector<int>& out) {
    if (!root) return;
    tree_inorder(root->left, out);
    out.push_back(root->val);
    tree_inorder(root->right, out);
}

// ---------- Concurrency helpers ----------
std::mutex g_mutex;
std::atomic<int> g_atomic_counter{0};

void thread_worker(int id, int iterations) {
    for (int i = 0; i < iterations; ++i) {
        g_atomic_counter.fetch_add(1);
        std::lock_guard<std::mutex> lock(g_mutex);
        g_counter += id;
    }
}

// ---------- Section printer ----------
void section(const std::string& title) {
    std::cout << "\n=== " << title << " ===\n";
}

// ============================================================================
// Test sections
// ============================================================================

void test_basic_types_and_operators() {
    section("Basic types & operators");
    char c = 'A'; short s = 100; int i = 42; long l = 1234567L; long long ll = 9876543210LL;
    unsigned int ui = 4000000000U; float f = 3.14f; double d = 2.718281828; long double ld = 1.0L / 3;
    bool b = true; wchar_t wc = L'W'; char16_t c16 = u'x'; char32_t c32 = U'y';
    int8_t i8 = -8; uint16_t u16 = 65535; int64_t i64 = -1LL; size_t sz = sizeof(int);
    std::cout << c << " " << s << " " << i << " " << l << " " << ll << " " << ui << "\n";
    std::cout << f << " " << d << " " << ld << " " << std::boolalpha << b << "\n";
    std::cout << (int)wc << " " << (int)c16 << " " << (int)c32 << " " << (int)i8 << " "
              << u16 << " " << i64 << " " << sz << "\n";

    // arithmetic, bitwise, logical, ternary, compound
    int a = 17, bb = 5;
    std::cout << a + bb << " " << a - bb << " " << a * bb << " " << a / bb << " " << a % bb << "\n";
    std::cout << (a & bb) << " " << (a | bb) << " " << (a ^ bb) << " " << (~a) << " "
              << (a << 2) << " " << (a >> 1) << "\n";
    std::cout << (a > bb && bb > 0) << " " << (a < bb || bb == 5) << " " << !b << "\n";
    int t = (a > bb) ? a : bb;
    t += 3; t -= 1; t *= 2; t /= 3; t %= 7; t <<= 2; t >>= 1; t &= 0xFF; t |= 0x01; t ^= 0x10;
    std::cout << "t=" << t << "\n";
    int x = 5; int y = x++; y += ++x; std::cout << "x=" << x << " y=" << y << "\n";

    // literals
    int hex = 0xFF, oct = 077, bin = 0b1010, big = 1'000'000;
    std::cout << hex << " " << oct << " " << bin << " " << big << "\n";
    std::cout << 1.5e3 << " " << 'a' + 1 << " " << "str" << " " << R"(raw\nstring)" << "\n";

    // casts
    double pi = 3.99;
    int truncated = static_cast<int>(pi);
    const int* cp = &i;
    int* mp = const_cast<int*>(cp);
    void* vp = &i;
    int* ip = static_cast<int*>(vp);
    float fbits = 1.0f;
    uint32_t ubits = reinterpret_cast<uint32_t&>(fbits);
    std::cout << truncated << " " << *mp << " " << *ip << " " << std::hex << ubits << std::dec << "\n";

    // sizeof / limits
    std::cout << sizeof(char) << sizeof(int) << sizeof(double)
              << " " << std::numeric_limits<int>::max() << " "
              << std::numeric_limits<double>::epsilon() << "\n";

    // macros
    std::cout << SQUARE(4) << " " << MAX_SIZE << " " << STRINGIFY(hello) << " ";
    int CONCAT(var, 1) = 10; std::cout << var1 << "\n";
}

void test_control_flow() {
    section("Control flow");
    for (int i = 0; i < 3; ++i) std::cout << i << " ";
    std::cout << "\n";
    int w = 0; while (w < 3) { std::cout << w++ << " "; } std::cout << "\n";
    int dw = 0; do { std::cout << dw << " "; ++dw; } while (dw < 3); std::cout << "\n";

    for (int i = 0; i < 10; ++i) {
        if (i == 2) continue;
        if (i == 6) break;
        std::cout << i << " ";
    }
    std::cout << "\n";

    for (int i = 1; i <= 3; ++i)
        for (int j = 1; j <= 3; ++j) {
            if (j == 3) goto next_i;
            std::cout << i * j << " ";
        next_i:;
        }
    std::cout << "\n";

    for (int v = 0; v < 5; ++v) {
        switch (v) {
            case 0: std::cout << "zero "; break;
            case 1:
            case 2: std::cout << "one-or-two "; break;
            case 3: std::cout << "three "; [[fallthrough]];
            default: std::cout << "default ";
        }
    }
    std::cout << "\n";

    if (int k = 5; k > 3) std::cout << "init-if " << k << "\n";
    else std::cout << "else\n";

    for (int a = 0, b = 10; a < b; a += 3, b -= 3) std::cout << a << ":" << b << " ";
    std::cout << "\n";

    Color col = GREEN;
    switch (col) { case RED: std::cout << "R\n"; break; case GREEN: std::cout << "G\n"; break; default: break; }
    Direction dir = Direction::South;
    std::cout << static_cast<int>(dir) << " " << BLUE << "\n";
}

void test_arrays_pointers_references() {
    section("Arrays / pointers / references");
    int arr[5] = {1, 2, 3, 4, 5};
    int matrix[2][3] = {{1, 2, 3}, {4, 5, 6}};
    char cstr[] = "hello";
    int* p = arr;
    std::cout << *p << " " << *(p + 2) << " " << p[4] << " " << arr[1] << "\n";
    for (int r = 0; r < 2; ++r) { for (int c = 0; c < 3; ++c) std::cout << matrix[r][c] << " "; }
    std::cout << "\n" << cstr << " " << std::strlen(cstr) << "\n";

    int a = 1, b = 2;
    swap_ref(a, b); std::cout << a << b << " ";
    swap_ptr(&a, &b); std::cout << a << b << "\n";

    int** pp = &p; std::cout << **pp << "\n";
    int& ref = arr[3]; ref = 40; std::cout << arr[3] << "\n";
    const int& cref = a; std::cout << cref << "\n";
    int&& rref = 10; std::cout << rref << "\n";

    int* dyn = new int(7);
    int* dyn_arr = new int[4]{1, 2, 3, 4};
    std::cout << *dyn << " " << dyn_arr[3] << "\n";
    delete dyn; delete[] dyn_arr;

    int* np = nullptr;
    std::cout << (np == nullptr) << "\n";

    Point pt(3, 4); Point* ppt = &pt;
    std::cout << ppt->x << " " << (*ppt).y << "\n";

    int* mem = (int*)std::malloc(3 * sizeof(int));
    mem[0] = 9; mem[1] = 8; mem[2] = 7;
    std::cout << mem[0] + mem[1] + mem[2] << "\n";
    std::free(mem);

    // structured bindings
    auto [px, py] = pt;
    std::cout << px << "," << py << "\n";

    // union & bitfield
    IntOrFloat u; u.f = 1.0f; std::cout << std::hex << u.i << std::dec << "\n";
    Flags fl{1, 5, 9}; std::cout << fl.a << fl.b << fl.c << "\n";
}

void test_strings() {
    section("Strings");
    std::string s = "Hello, World";
    s += "!";
    std::cout << s << " len=" << s.length() << " " << s.substr(7, 5) << " " << s.find("World") << "\n";
    s.replace(0, 5, "HELLO"); std::cout << s << "\n";
    s.insert(5, "***"); std::cout << s << "\n";
    s.erase(5, 3); std::cout << s << " " << s.front() << s.back() << "\n";
    std::transform(s.begin(), s.end(), s.begin(), [](unsigned char ch) { return std::tolower(ch); });
    std::cout << s << " " << (s == "hello, world!") << " " << s.compare("abc") << "\n";

    std::string_view sv = "view of text";
    std::cout << sv.substr(0, 4) << " " << sv.size() << "\n";

    std::cout << std::stoi("123") + 1 << " " << std::stod("2.5") * 2 << " " << std::to_string(3.5) << "\n";

    std::ostringstream oss;
    oss << "num=" << 42 << " pi=" << std::fixed << std::setprecision(3) << 3.14159
        << " [" << std::setw(6) << std::setfill('.') << 7 << "]";
    std::cout << oss.str() << "\n";

    std::istringstream iss("10 20 30");
    int n, total = 0; while (iss >> n) total += n;
    std::cout << "total=" << total << "\n";

    std::string csv = "a,b,c"; std::stringstream ss(csv); std::string tok;
    while (std::getline(ss, tok, ',')) std::cout << "<" << tok << ">";
    std::cout << "\n";

    char buf[64];
    std::snprintf(buf, sizeof(buf), "%05d|%.2f|%s|%c|%x", 42, 3.14159, "str", 'z', 255);
    std::cout << buf << "\n";
    std::printf("printf: %d %s\n", 7, "ok");

    std::cout << std::isalpha('a') << std::isdigit('5') << std::toupper('q') << "\n";
    std::cout << std::strcmp("a", "b") << " " << std::atoi("77") << "\n";
    using namespace std::string_literals;
    auto lit = "literal"s; std::cout << lit.size() << "\n";
}

void test_stl_containers() {
    section("STL containers");
    std::vector<int> v = {5, 3, 8, 1, 9, 2};
    v.push_back(7); v.emplace_back(4); v.insert(v.begin() + 1, 100); v.pop_back();
    std::cout << "vec size=" << v.size() << " front=" << v.front() << " back=" << v.back() << "\n";
    std::sort(v.begin(), v.end());
    for (int x : v) std::cout << x << " ";
    std::cout << "\n";
    v.erase(std::remove(v.begin(), v.end(), 100), v.end());
    std::cout << std::binary_search(v.begin(), v.end(), 8) << "\n";

    std::array<int, 4> a = {1, 2, 3, 4};
    std::cout << a.size() << a.at(2) << "\n";

    std::list<int> lst = {3, 1, 2}; lst.push_front(0); lst.sort(); lst.reverse();
    for (auto x : lst) std::cout << x; std::cout << "\n";

    std::deque<int> dq = {1, 2}; dq.push_front(0); dq.push_back(3);
    std::cout << dq.front() << dq.back() << dq[2] << "\n";

    std::forward_list<int> fl = {1, 2, 3}; fl.push_front(0);
    for (int x : fl) std::cout << x; std::cout << "\n";

    std::map<std::string, int> m = {{"one", 1}, {"two", 2}};
    m["three"] = 3; m.insert({"four", 4}); m.emplace("five", 5);
    for (const auto& [k, val] : m) std::cout << k << "=" << val << " ";
    std::cout << "\n";
    if (auto it = m.find("two"); it != m.end()) std::cout << "found " << it->second << "\n";
    std::cout << m.count("zzz") << " " << m.size() << "\n";

    std::unordered_map<int, std::string> um = {{1, "a"}, {2, "b"}};
    um[3] = "c"; std::cout << um.at(3) << um.size() << "\n";

    std::set<int> st = {3, 1, 2, 3, 1}; st.insert(10);
    for (int x : st) std::cout << x << " "; std::cout << st.count(2) << "\n";
    std::unordered_set<std::string> us = {"x", "y"}; us.insert("z");
    std::cout << us.size() << us.count("x") << "\n";
    std::multiset<int> ms = {1, 1, 2}; std::cout << ms.count(1) << "\n";
    std::multimap<int, char> mm = {{1, 'a'}, {1, 'b'}}; std::cout << mm.count(1) << "\n";

    std::stack<int> stk; stk.push(1); stk.push(2); std::cout << stk.top(); stk.pop(); std::cout << stk.size() << "\n";
    std::queue<int> q; q.push(1); q.push(2); std::cout << q.front() << q.back(); q.pop(); std::cout << q.size() << "\n";
    std::priority_queue<int> pq; pq.push(3); pq.push(9); pq.push(1);
    std::cout << pq.top() << "\n";
    std::priority_queue<int, std::vector<int>, std::greater<int>> minpq; minpq.push(3); minpq.push(1);
    std::cout << minpq.top() << "\n";

    std::pair<int, std::string> pr = {1, "pair"}; auto pr2 = std::make_pair(2, 3.5);
    std::cout << pr.first << pr.second << pr2.second << "\n";
    std::tuple<int, double, std::string> tp = {1, 2.5, "tuple"};
    std::cout << std::get<0>(tp) << std::get<1>(tp) << std::get<2>(tp) << "\n";
    auto [t1, t2, t3] = tp; std::cout << t1 << t2 << t3 << "\n";
    int ta; double tb; std::tie(ta, tb, std::ignore) = tp; std::cout << ta << tb << "\n";

    std::bitset<8> bs(0b10110010);
    std::cout << bs << " " << bs.count() << " " << bs.test(1) << " " << bs.to_ulong() << "\n";

    std::vector<std::vector<int>> grid(3, std::vector<int>(3, 0));
    for (int i = 0; i < 3; ++i) grid[i][i] = 1;
    for (auto& row : grid) { for (int x : row) std::cout << x; std::cout << " "; }
    std::cout << "\n";
}

void test_algorithms_and_lambdas() {
    section("Algorithms & lambdas");
    std::vector<int> v = {4, 2, 9, 1, 7, 3};

    auto add = [](int a, int b) { return a + b; };
    int base = 10;
    auto cap_val = [base](int x) { return x + base; };
    auto cap_ref = [&base](int x) { base += x; };
    auto cap_all = [=]() { return base * 2; };
    auto generic = [](auto a, auto b) { return a + b; };
    auto mutable_l = [n = 0]() mutable { return ++n; };
    std::cout << add(1, 2) << cap_val(5) << generic(1.5, 2) << "\n";
    cap_ref(5); std::cout << base << " " << cap_all() << " " << mutable_l() << mutable_l() << "\n";

    std::function<int(int)> fact_fn = [&fact_fn](int n) { return n <= 1 ? 1 : n * fact_fn(n - 1); };
    std::cout << fact_fn(5) << "\n";

    std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });
    for (int x : v) std::cout << x << " "; std::cout << "\n";

    std::cout << std::accumulate(v.begin(), v.end(), 0) << " "
              << std::accumulate(v.begin(), v.end(), 1, std::multiplies<int>()) << "\n";
    std::cout << *std::max_element(v.begin(), v.end()) << *std::min_element(v.begin(), v.end()) << "\n";
    std::cout << std::count_if(v.begin(), v.end(), [](int x) { return x % 2 == 1; }) << "\n";
    std::cout << std::any_of(v.begin(), v.end(), [](int x) { return x > 8; })
              << std::all_of(v.begin(), v.end(), [](int x) { return x > 0; })
              << std::none_of(v.begin(), v.end(), [](int x) { return x > 100; }) << "\n";
    auto it = std::find(v.begin(), v.end(), 7);
    std::cout << (it != v.end() ? std::distance(v.begin(), it) : -1) << "\n";
    auto it2 = std::find_if(v.begin(), v.end(), [](int x) { return x < 3; });
    std::cout << *it2 << "\n";

    std::vector<int> sq(v.size());
    std::transform(v.begin(), v.end(), sq.begin(), [](int x) { return x * x; });
    for (int x : sq) std::cout << x << " "; std::cout << "\n";

    std::for_each(v.begin(), v.end(), [](int& x) { x += 1; });
    std::reverse(v.begin(), v.end());
    std::rotate(v.begin(), v.begin() + 2, v.end());
    for (int x : v) std::cout << x << " "; std::cout << "\n";

    std::vector<int> iota_v(5); std::iota(iota_v.begin(), iota_v.end(), 10);
    std::vector<int> part(5); std::partial_sum(iota_v.begin(), iota_v.end(), part.begin());
    for (int x : part) std::cout << x << " "; std::cout << "\n";

    std::vector<int> a = {1, 2, 3, 4}, b = {3, 4, 5}, out;
    std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(out));
    for (int x : out) std::cout << x; std::cout << "\n";
    auto uq = std::unique(a.begin(), a.end()); (void)uq;
    std::vector<int> fill_v(4); std::fill(fill_v.begin(), fill_v.end(), 7);
    std::copy(fill_v.begin(), fill_v.end(), std::ostream_iterator<int>(std::cout, ","));
    std::cout << "\n";
    std::vector<int> partitioned = {1, 2, 3, 4, 5, 6};
    std::partition(partitioned.begin(), partitioned.end(), [](int x) { return x % 2 == 0; });
    std::nth_element(partitioned.begin(), partitioned.begin() + 2, partitioned.end());
    std::cout << partitioned[2] << "\n";
    std::cout << std::lower_bound(sq.begin(), sq.end(), 0) - sq.begin() << "\n";
    std::next_permutation(a.begin(), a.end());
    std::cout << std::gcd(12, 18) << std::lcm(4, 6) << "\n";

    // std::bind & std::function
    auto bound = std::bind(add, 100, std::placeholders::_1);
    std::cout << bound(5) << "\n";
    std::function<int(int, int)> fn = op_mul; std::cout << fn(3, 4) << "\n";
    std::cout << apply_op(op_add, 2, 3) << apply_op([](int a, int b) { return a - b; }, 9, 4) << "\n";
}

void test_classes_and_polymorphism() {
    section("Classes & polymorphism");
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Circle>(2.0));
    shapes.push_back(std::make_unique<Rectangle>(3, 4));
    shapes.push_back(std::make_unique<Square>(5));
    std::cout << std::fixed << std::setprecision(2);
    for (const auto& sh : shapes)
        std::cout << sh->describe() << " perim=" << sh->perimeter() << "\n";
    Shape* raw = shapes[0].get();
    if (auto* c = dynamic_cast<Circle*>(raw)) std::cout << "is Circle\n";
    if (dynamic_cast<Rectangle*>(raw) == nullptr) std::cout << "not Rectangle\n";
    std::cout << typeid(*raw).name() << "\n";
    std::cout.unsetf(std::ios::floatfield);

    Duck d; std::cout << d.sound() << d.walk() << d.swim() << "\n";

    Vector2D v1(1, 2), v2(3, 4);
    Vector2D v3 = v1 + v2; v3 += Vector2D(1, 1); ++v3; v3++;
    std::cout << v3 << " " << (v1 == v2) << (v1 != v2) << " " << v1[0] << v2(2.0)
              << " " << dot(v1, v2) << " " << Vector2D::count() << " " << (bool)v1 << "\n";
    Vector2D moved(std::move(v3)); std::cout << moved << v3 << "\n";
    std::cout << (v1 * 3.0) << " " << (v2 - v1).length() << "\n";
}

void test_templates() {
    section("Templates");
    std::cout << max_of(3, 7) << max_of(2.5, 1.5) << max_of<std::string>("a", "b") << "\n";
    FixedArray<int, 5> fa; fa[2] = 9; std::cout << fa[2] << fa.size() << "\n";
    Box<int> bi(5); Box<bool> bb(true); int val = 77; Box<int*> bp(&val);
    std::cout << bi.type() << bb.type() << bp.type() << bp.get() << "\n";
    std::cout << sum_all(1, 2, 3, 4) << sum_all(1.5, 2.5) << "\n";
    print_all(1, "two", 3.0, 'c'); std::cout << "\n";
    std::cout << describe_type(5) << describe_type(2.5) << "\n";
    std::cout << Fact<5>::value << " " << fib(10) << "\n";
    constexpr int cx = fib(8); static_assert(cx == 21, "fib check");
    static_assert(sizeof(int) >= 4, "int size");
    Vec<int> vv = {1, 2}; IntVec iv = {3}; StrMap sm = {{"k", 1}};
    std::cout << vv.size() << iv.size() << sm.size() << "\n";
    std::cout << std::is_same_v<int, int> << std::is_pointer_v<int*> << std::is_class_v<Point> << "\n";
}

void test_exceptions() {
    section("Exceptions");
    int inputs[] = {5, -1, 0, 5000};
    for (int in : inputs) {
        try {
            std::cout << "risky(" << in << ")=" << risky(in) << "\n";
        } catch (const CustomError& e) {
            std::cout << "CustomError: " << e.what() << " code=" << e.code() << "\n";
        } catch (const std::invalid_argument& e) {
            std::cout << "invalid_argument: " << e.what() << "\n";
        } catch (const std::exception& e) {
            std::cout << "std::exception: " << e.what() << "\n";
        } catch (...) {
            std::cout << "unknown\n";
        }
    }
    try {
        try { throw std::runtime_error("inner"); }
        catch (const std::exception&) { std::cout << "rethrowing\n"; throw; }
    } catch (const std::runtime_error& e) { std::cout << "outer caught " << e.what() << "\n"; }
    try { std::vector<int> v(2); v.at(10); }
    catch (const std::out_of_range&) { std::cout << "vector out_of_range\n"; }
    try { throw 42; } catch (int x) { std::cout << "int thrown " << x << "\n"; }
    try { throw std::string("string thrown"); } catch (const std::string& s) { std::cout << s << "\n"; }
    auto safe = []() noexcept { return 1; }; std::cout << noexcept(safe()) << "\n";
    assert(1 + 1 == 2);
}

void test_smart_pointers_and_memory() {
    section("Smart pointers & memory");
    {
        std::unique_ptr<Resource> u = std::make_unique<Resource>("unique");
        u->use();
        auto u2 = std::move(u);
        std::cout << (u == nullptr) << "\n";
    }
    {
        std::shared_ptr<Resource> s1 = std::make_shared<Resource>("shared");
        std::shared_ptr<Resource> s2 = s1;
        std::weak_ptr<Resource> w = s1;
        std::cout << "use_count=" << s1.use_count() << " expired=" << w.expired() << "\n";
        s1.reset();
        if (auto locked = w.lock()) locked->use();
    }
    Node* head = nullptr;
    for (int i = 1; i <= 4; ++i) head = push_front(head, i);
    for (Node* n = head; n; n = n->next) std::cout << n->data << " ";
    std::cout << "\n";
    free_list(head);

    std::unique_ptr<TreeNode> root;
    for (int x : {5, 3, 8, 1, 4, 9}) tree_insert(root, x);
    std::vector<int> sorted; tree_inorder(root, sorted);
    for (int x : sorted) std::cout << x << " "; std::cout << "\n";

    auto arr = std::make_unique<int[]>(3); arr[0] = 1; arr[2] = 3;
    std::cout << arr[0] + arr[2] << "\n";

    alignas(16) char buffer[sizeof(Point)];
    Point* placed = new (buffer) Point(8, 9);
    std::cout << placed->x << placed->y << "\n";
    placed->~Point();
}

void test_optional_variant_any() {
    section("optional / variant / any");
    std::optional<int> o1 = 5, o2;
    std::cout << o1.has_value() << o2.has_value() << o1.value_or(0) << o2.value_or(-1) << "\n";
    if (o1) std::cout << *o1 << "\n";

    std::variant<int, double, std::string> var = 3.14;
    std::cout << var.index() << std::get<double>(var) << "\n";
    var = std::string("now string");
    std::visit([](auto&& arg) { std::cout << "visited: " << arg << "\n"; }, var);
    if (std::holds_alternative<std::string>(var)) std::cout << "holds string\n";

    std::any a = 10; std::cout << std::any_cast<int>(a) << "\n";
    a = std::string("any-string"); std::cout << std::any_cast<std::string>(a) << "\n";
}

void test_chrono_random_regex() {
    section("chrono / random / regex");
    auto start = std::chrono::steady_clock::now();
    std::this_thread::sleep_for(std::chrono::milliseconds(5));
    auto end = std::chrono::steady_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    std::cout << "elapsed>=5ms: " << (ms >= 4) << "\n";

    std::mt19937 gen(12345);
    std::uniform_int_distribution<int> dist(1, 6);
    std::uniform_real_distribution<double> rdist(0.0, 1.0);
    std::normal_distribution<double> ndist(0.0, 1.0);
    int roll = dist(gen); double r = rdist(gen); (void)ndist;
    std::cout << (roll >= 1 && roll <= 6) << (r >= 0 && r < 1) << "\n";
    std::vector<int> shuf = {1, 2, 3, 4, 5}; std::shuffle(shuf.begin(), shuf.end(), gen);
    std::srand(1); int rr = std::rand(); (void)rr;

    std::regex re(R"((\w+)@(\w+)\.com)");
    std::smatch m; std::string email = "contact: alice@example.com now";
    if (std::regex_search(email, m, re)) std::cout << m[1] << " at " << m[2] << "\n";
    std::cout << std::regex_replace("a1b22c333", std::regex("[0-9]+"), "#") << "\n";
    std::cout << std::regex_match("abc123", std::regex("[a-z]+[0-9]+")) << "\n";

    std::time_t now = std::time(nullptr); (void)now;
    std::clock_t clk = std::clock(); (void)clk;
}

void test_math() {
    section("cmath");
    std::cout << std::fixed << std::setprecision(4);
    std::cout << std::sqrt(16.0) << " " << std::pow(2, 10) << " " << std::abs(-3.5) << " "
              << std::floor(2.7) << " " << std::ceil(2.1) << " " << std::round(2.5) << " "
              << std::fmod(7.5, 2) << "\n";
    std::cout << std::sin(math_utils::PI / 2) << " " << std::cos(0.0) << " " << std::tan(0.0) << " "
              << std::atan2(1, 1) << " " << std::exp(1.0) << " " << std::log(std::exp(2.0)) << " "
              << std::log10(1000.0) << " " << std::hypot(3, 4) << "\n";
    std::cout.unsetf(std::ios::floatfield);
    std::cout << std::abs(-7) << " " << std::isnan(std::nan("")) << " " << std::isinf(INFINITY) << "\n";
    std::cout << math_utils::add(1, 2) << " " << math_utils::add(1.5, 2.5) << " "
              << alias_target::triple(4) << " " << math_utils::nested::triple(2) << "\n";
    std::cout << factorial(6) << " " << gcd(48, 18) << " " << is_prime(97) << " "
              << with_default(1) << with_default(1, 2) << with_default(1, 2, 3) << " "
              << cube(3) << " " << file_local_fn(1) << " " << trailing(2, 3) << " "
              << must_use() << " " << G_CONST << G_CONSTEXPR << s_static_global << g_extern_decl << "\n";
}

void test_file_io() {
    section("File I/O");
    const char* path = "transpiler_test_tmp.txt";
    {
        std::ofstream out(path);
        out << "line one\nline two\n42 3.14\n";
    }
    {
        std::ifstream in(path);
        std::string line;
        while (std::getline(in, line)) std::cout << "read: " << line << "\n";
    }
    {
        std::ofstream app(path, std::ios::app); app << "appended\n";
    }
    {
        std::ifstream in(path); std::string word; int count = 0;
        while (in >> word) ++count;
        std::cout << "words=" << count << "\n";
    }
    std::remove(path);
    std::cerr << "(this line goes to stderr)\n";
    std::clog << "(this line goes to clog)\n";
}

void test_threads() {
    section("Threads / async / sync");
    g_counter = 0; g_atomic_counter = 0;
    std::vector<std::thread> threads;
    for (int i = 1; i <= 4; ++i) threads.emplace_back(thread_worker, i, 1000);
    for (auto& t : threads) t.join();
    std::cout << "atomic=" << g_atomic_counter << " guarded=" << g_counter << "\n";

    std::future<int> fut = std::async(std::launch::async, [] { return factorial(5); });
    std::cout << "async result=" << fut.get() << "\n";

    std::promise<int> prom; std::future<int> pf = prom.get_future();
    std::thread t([&prom] { prom.set_value(99); });
    std::cout << "promise=" << pf.get() << "\n"; t.join();

    std::mutex m; std::condition_variable cv; bool ready = false;
    std::thread waiter([&] {
        std::unique_lock<std::mutex> lk(m);
        cv.wait(lk, [&] { return ready; });
        std::cout << "cv signaled\n";
    });
    { std::lock_guard<std::mutex> lk(m); ready = true; }
    cv.notify_one(); waiter.join();

    thread_local int tls = 0; ++tls; std::cout << "tls=" << tls << "\n";
}

// ---------- Range-for over custom iterable + iterator class ----------
class Range {
    int lo_, hi_;
public:
    Range(int lo, int hi) : lo_(lo), hi_(hi) {}
    struct Iter {
        int v;
        int operator*() const { return v; }
        Iter& operator++() { ++v; return *this; }
        bool operator!=(const Iter& o) const { return v != o.v; }
    };
    Iter begin() const { return {lo_}; }
    Iter end() const { return {hi_}; }
};

void test_custom_iterables_and_misc() {
    section("Custom iterables & misc");
    for (int x : Range(0, 5)) std::cout << x << " ";
    std::cout << "\n";
    auto init = {1, 2, 3}; std::cout << init.size() << "\n";
    auto lst_sum = [](std::initializer_list<int> il) { int s = 0; for (int x : il) s += x; return s; };
    std::cout << lst_sum({1, 2, 3, 4}) << "\n";
    decltype(auto) dref = g_counter; (void)dref;
    auto fptr = &factorial; std::cout << fptr(4) << "\n";
    int Point::*member_ptr = &Point::x; Point pt(11, 22); std::cout << pt.*member_ptr << "\n";
    std::cout << __LINE__ << " " << (__FILE__ != nullptr) << " " << __func__ << " " << __cplusplus << "\n";
#if DEBUG_LEVEL > 0
    std::cout << "debug on\n";
#else
    std::cout << "debug off\n";
#endif
    volatile int vol = 3; register_hint:; std::cout << vol << "\n";
    Point p1(1, 2), p2(1, 2); std::cout << (p1 == p2) << "\n";
    std::cout << std::boolalpha << (p1 == p2) << std::noboolalpha << "\n";
}

// ============================================================================
// main
// ============================================================================
int main(int argc, char* argv[]) {
    std::ios_base::sync_with_stdio(false);
    std::cout << "argc=" << argc << " argv0_present=" << (argv[0] != nullptr) << "\n";

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

    std::cout << "\nAll sections completed.\n";
    return EXIT_SUCCESS;
}