#pragma once
#ifndef __STD_DEFS_H__
#define __STD_DEFS_H__

typedef unsigned long long size_t;
typedef long long int64_t;
typedef unsigned long long uint64_t;
typedef int int32_t;
typedef unsigned int uint32_t;
typedef short int16_t;
typedef unsigned short uint16_t;
typedef signed char int8_t;
typedef unsigned char uint8_t;
#ifdef __cplusplus
typedef decltype(nullptr) nullptr_t;
#endif

#ifndef INFINITY
#define INFINITY (__builtin_inff())
#endif

#ifndef EXIT_SUCCESS
#define EXIT_SUCCESS 0
#endif
#ifndef EXIT_FAILURE
#define EXIT_FAILURE 1
#endif

#ifdef __cplusplus
inline void* operator new(size_t, void* ptr) noexcept { return ptr; }
inline void operator delete(void*, void*) noexcept {}

namespace std {
    using ::size_t;
    using ::int64_t;
    using ::uint64_t;
    using ::int32_t;
    using ::uint32_t;
    using ::int16_t;
    using ::uint16_t;
    using ::int8_t;
    using ::uint8_t;

    template<typename T> struct remove_reference { typedef T type; };
    template<typename T> struct remove_reference<T&> { typedef T type; };
    template<typename T> struct remove_reference<T&&> { typedef T type; };

    template<bool B, typename T = void> struct enable_if {};
    template<typename T> struct enable_if<true, T> { typedef T type; };
    template<bool B, typename T = void> using enable_if_t = typename enable_if<B, T>::type;

    template<typename T> struct is_integral { static constexpr bool value = false; };
    template<> struct is_integral<bool> { static constexpr bool value = true; };
    template<> struct is_integral<char> { static constexpr bool value = true; };
    template<> struct is_integral<signed char> { static constexpr bool value = true; };
    template<> struct is_integral<unsigned char> { static constexpr bool value = true; };
    template<> struct is_integral<short> { static constexpr bool value = true; };
    template<> struct is_integral<unsigned short> { static constexpr bool value = true; };
    template<> struct is_integral<int> { static constexpr bool value = true; };
    template<> struct is_integral<unsigned int> { static constexpr bool value = true; };
    template<> struct is_integral<long> { static constexpr bool value = true; };
    template<> struct is_integral<unsigned long> { static constexpr bool value = true; };
    template<> struct is_integral<long long> { static constexpr bool value = true; };
    template<> struct is_integral<unsigned long long> { static constexpr bool value = true; };
    template<typename T> inline constexpr bool is_integral_v = is_integral<T>::value;

    template<typename T> struct is_floating_point { static constexpr bool value = false; };
    template<> struct is_floating_point<float> { static constexpr bool value = true; };
    template<> struct is_floating_point<double> { static constexpr bool value = true; };
    template<> struct is_floating_point<long double> { static constexpr bool value = true; };
    template<typename T> inline constexpr bool is_floating_point_v = is_floating_point<T>::value;

    template<typename T> struct is_pointer { static constexpr bool value = false; };
    template<typename T> struct is_pointer<T*> { static constexpr bool value = true; };
    template<typename T> inline constexpr bool is_pointer_v = is_pointer<T>::value;

    template<typename T> struct is_class { static constexpr bool value = true; };
    template<typename T> inline constexpr bool is_class_v = is_class<T>::value;

    struct type_info {
        const char* name() const { return "type"; }
    };

    template<typename T, typename U> struct is_same { static constexpr bool value = false; };
    template<typename T> struct is_same<T, T> { static constexpr bool value = true; };
    template<typename T, typename U> inline constexpr bool is_same_v = is_same<T, U>::value;

    template<typename T> struct numeric_limits {
        static constexpr T max() { return T(); }
        static constexpr T min() { return T(); }
        static constexpr T lowest() { return T(); }
        static constexpr T epsilon() { return T(); }
    };

    // Math functions
    inline double sqrt(double) { return 0.0; }
    inline float sqrt(float) { return 0.0f; }
    inline double pow(double, double) { return 0.0; }
    inline int abs(int) { return 0; }
    inline double abs(double) { return 0.0; }
    inline double sin(double) { return 0.0; }
    inline double cos(double) { return 0.0; }
    inline double tan(double) { return 0.0; }
    inline double log(double) { return 0.0; }
    inline double log10(double) { return 0.0; }
    inline double exp(double) { return 0.0; }
    inline double ceil(double) { return 0.0; }
    inline double floor(double) { return 0.0; }
    inline double round(double) { return 0.0; }
    inline double fmod(double, double) { return 0.0; }
    inline double atan2(double, double) { return 0.0; }
    inline double hypot(double, double) { return 0.0; }
    inline bool isnan(double) { return false; }
    inline bool isinf(double) { return false; }
    inline double nan(const char*) { return 0.0; }

    // Time
    typedef long long time_t;
    typedef long long clock_t;
    inline time_t time(time_t* = nullptr) { return 0; }
    inline clock_t clock() { return 0; }

    // C-string, file and memory
    inline size_t strlen(const char*) { return 0; }
    inline int strcmp(const char*, const char*) { return 0; }
    inline char* strcpy(char* d, const char*) { return d; }
    inline void* memcpy(void* d, const void*, size_t) { return d; }
    inline void* memset(void* d, int, size_t) { return d; }
    inline int remove(const char*) { return 0; }

    // Forward declarations and early templates
    template<typename T> struct initializer_list {
        const T* begin() const { return nullptr; }
        const T* end() const { return nullptr; }
        size_t size() const { return 0; }
    };

    // C functions and memory
    inline void* malloc(size_t) { return nullptr; }
    inline void free(void*) {}
    inline int snprintf(char*, size_t, const char*, ...) { return 0; }
    inline int printf(const char*, ...) { return 0; }
    inline int tolower(int c) { return c; }
    inline int toupper(int c) { return c; }
    inline int isalpha(int c) { return 0; }
    inline int isdigit(int c) { return 0; }
    inline int isalnum(int c) { return 0; }
    inline int isspace(int c) { return 0; }
    inline int atoi(const char*) { return 0; }
    inline double atof(const char*) { return 0.0; }
    inline long atol(const char*) { return 0; }

    // Basic types
    struct string {
        string() {}
        string(const char*) {}
        string(const string&) {}
        string(string&&) {}
        string(size_t, char) {}
        ~string() {}
        string& operator=(const char*) { return *this; }
        string& operator=(const string&) { return *this; }
        string& operator+=(const char*) { return *this; }
        string& operator+=(const string&) { return *this; }
        string& operator+=(char) { return *this; }
        const char* c_str() const { return ""; }
        const char* data() const { return ""; }
        size_t size() const { return 0; }
        size_t length() const { return 0; }
        bool empty() const { return true; }
        char& operator[](size_t) { static char c; return c; }
        const char& operator[](size_t) const { static char c; return c; }
        char& front() { static char c; return c; }
        char& back() { static char c; return c; }
        char* begin() { return nullptr; }
        char* end() { return nullptr; }
        const char* begin() const { return nullptr; }
        const char* end() const { return nullptr; }
        string substr(size_t = 0, size_t = 0) const { return string(); }
        size_t find(const string&, size_t = 0) const { return 0; }
        size_t find(const char*, size_t = 0) const { return 0; }
        string& replace(size_t, size_t, const char*) { return *this; }
        string& replace(size_t, size_t, const string&) { return *this; }
        string& insert(size_t, const char*) { return *this; }
        string& insert(size_t, const string&) { return *this; }
        string& erase(size_t = 0, size_t = 0) { return *this; }
        int compare(const string&) const { return 0; }
        int compare(const char*) const { return 0; }
        static const size_t npos = -1;
    };

    inline namespace literals {
        inline namespace string_literals {
            inline string operator""s(const char*, size_t) { return string(); }
        }
    }

    inline bool operator==(const string&, const string&) { return true; }
    inline bool operator==(const string&, const char*) { return true; }
    inline bool operator==(const char*, const string&) { return true; }
    inline bool operator!=(const string&, const string&) { return false; }
    inline bool operator!=(const string&, const char*) { return false; }
    inline bool operator!=(const char*, const string&) { return false; }
    inline bool operator<(const string&, const string&) { return false; }
    inline bool operator<(const string&, const char*) { return false; }
    inline bool operator<(const char*, const string&) { return false; }
    inline bool operator<=(const string&, const string&) { return true; }
    inline bool operator<=(const string&, const char*) { return true; }
    inline bool operator<=(const char*, const string&) { return true; }
    inline bool operator>(const string&, const string&) { return false; }
    inline bool operator>(const string&, const char*) { return false; }
    inline bool operator>(const char*, const string&) { return false; }
    inline bool operator>=(const string&, const string&) { return true; }
    inline bool operator>=(const string&, const char*) { return true; }
    inline bool operator>=(const char*, const string&) { return true; }

    struct string_view {
        string_view() {}
        string_view(const char*) {}
        string_view(const string&) {}
        const char* data() const { return ""; }
        size_t size() const { return 0; }
        size_t length() const { return 0; }
        bool empty() const { return true; }
        string_view substr(size_t = 0, size_t = 0) const { return string_view(); }
    };

    inline string operator+(const string& a, const string& b) { return a; }
    inline string operator+(const string& a, const char* b) { return a; }
    inline string operator+(const char* a, const string& b) { return b; }

    template<typename T1, typename T2>
    struct pair {
        T1 first;
        T2 second;
        pair() : first(), second() {}
        pair(const T1& a, const T2& b) : first(a), second(b) {}
    };

    template<typename T1, typename T2>
    pair<T1, T2> make_pair(T1 a, T2 b) { return pair<T1, T2>(a, b); }

    template<typename... Types>
    struct tuple {
        tuple() {}
        tuple(Types...) {}
        template<typename... Other>
        tuple& operator=(const tuple<Other...>&) { return *this; }
        template<typename... Other>
        tuple& operator=(tuple<Other...>&&) { return *this; }
    };

    template<typename... Types>
    tuple<Types...> make_tuple(Types... args) { return tuple<Types...>(args...); }

    template<typename... Types>
    tuple<Types&...> tie(Types&... args) { return tuple<Types&...>(args...); }

    template<typename T> struct tuple_size;
    template<typename... Types> struct tuple_size<tuple<Types...>> { static constexpr size_t value = sizeof...(Types); };
    template<typename T1, typename T2> struct tuple_size<pair<T1, T2>> { static constexpr size_t value = 2; };
    template<typename T> struct tuple_size<const T> : tuple_size<T> {};

    template<size_t I, typename T> struct tuple_element;
    template<size_t I, typename Head, typename... Tail>
    struct tuple_element<I, tuple<Head, Tail...>> : tuple_element<I - 1, tuple<Tail...>> {};
    template<typename Head, typename... Tail>
    struct tuple_element<0, tuple<Head, Tail...>> { typedef Head type; };
    template<typename T1, typename T2> struct tuple_element<0, pair<T1, T2>> { typedef T1 type; };
    template<typename T1, typename T2> struct tuple_element<1, pair<T1, T2>> { typedef T2 type; };
    template<size_t I, typename T>
    struct tuple_element<I, const T> {
        typedef const typename tuple_element<I, T>::type type;
    };

    struct __ignore_t {
        template<typename T> const __ignore_t& operator=(const T&) const { return *this; }
    };
    static const __ignore_t ignore;

    template<size_t I, typename... Types>
    typename tuple_element<I, tuple<Types...>>::type& get(tuple<Types...>&) {
        static typename tuple_element<I, tuple<Types...>>::type dummy;
        return dummy;
    }
    template<size_t I, typename... Types>
    typename tuple_element<I, tuple<Types...>>::type& get(tuple<Types...>&&) {
        static typename tuple_element<I, tuple<Types...>>::type dummy;
        return dummy;
    }
    template<size_t I, typename... Types>
    const typename tuple_element<I, tuple<Types...>>::type& get(const tuple<Types...>&) {
        static typename tuple_element<I, tuple<Types...>>::type dummy;
        return dummy;
    }
    template<size_t I, typename T1, typename T2>
    typename tuple_element<I, pair<T1, T2>>::type& get(pair<T1, T2>&) {
        static typename tuple_element<I, pair<T1, T2>>::type dummy;
        return dummy;
    }
    template<size_t I, typename T1, typename T2>
    typename tuple_element<I, pair<T1, T2>>::type& get(pair<T1, T2>&&) {
        static typename tuple_element<I, pair<T1, T2>>::type dummy;
        return dummy;
    }
    template<size_t I, typename T1, typename T2>
    const typename tuple_element<I, pair<T1, T2>>::type& get(const pair<T1, T2>&) {
        static typename tuple_element<I, pair<T1, T2>>::type dummy;
        return dummy;
    }

    // Containers
    template<typename T, typename Alloc = void>
    struct vector {
        vector() {}
        vector(size_t, const T& = T()) {}
        vector(const vector&) {}
        vector(vector&&) {}
        vector(std::initializer_list<T>) {}
        ~vector() {}
        void push_back(const T&) {}
        template<typename... Args> void emplace_back(Args&&...) {}
        void pop_back() {}
        size_t size() const { return 0; }
        bool empty() const { return true; }
        void clear() {}
        void resize(size_t) {}
        void reserve(size_t) {}
        T& operator[](size_t) { static T dummy; return dummy; }
        const T& operator[](size_t) const { static T dummy; return dummy; }
        T& at(size_t i) { return (*this)[i]; }
        const T& at(size_t i) const { return (*this)[i]; }
        T& front() { static T dummy; return dummy; }
        T& back() { static T dummy; return dummy; }
        T* begin() { return nullptr; }
        T* end() { return nullptr; }
        const T* begin() const { return nullptr; }
        const T* end() const { return nullptr; }
        T* insert(T* pos, const T&) { return pos; }
        T* erase(T* pos) { return pos; }
        T* erase(T* first, T*) { return first; }
    };

    template<typename T, size_t N>
    struct array {
        T elems[N > 0 ? N : 1];
        size_t size() const { return N; }
        bool empty() const { return N == 0; }
        T& operator[](size_t i) { return elems[i]; }
        const T& operator[](size_t i) const { return elems[i]; }
        T& at(size_t i) { return elems[i]; }
        const T& at(size_t i) const { return elems[i]; }
        T* begin() { return elems; }
        T* end() { return elems + N; }
        const T* begin() const { return elems; }
        const T* end() const { return elems + N; }
        const T* cbegin() const { return elems; }
        const T* cend() const { return elems + N; }
    };

    template<typename K, typename V, typename C = void, typename A = void>
    struct map {
        map() {}
        map(std::initializer_list<pair<K, V>>) {}
        V& operator[](const K&) { static V dummy; return dummy; }
        V& at(const K&) { static V dummy; return dummy; }
        const V& at(const K&) const { static V dummy; return dummy; }
        size_t count(const K&) const { return 0; }
        size_t size() const { return 0; }
        bool empty() const { return true; }
        void insert(const pair<K, V>&) {}
        template<typename... Args> void emplace(Args&&...) {}
        pair<K, V>* begin() { return nullptr; }
        pair<K, V>* end() { return nullptr; }
        pair<K, V>* find(const K&) { return nullptr; }
        const pair<K, V>* begin() const { return nullptr; }
        const pair<K, V>* end() const { return nullptr; }
        const pair<K, V>* find(const K&) const { return nullptr; }
        const pair<K, V>* cbegin() const { return nullptr; }
        const pair<K, V>* cend() const { return nullptr; }
    };

    template<typename K, typename V, typename H = void, typename E = void, typename A = void>
    struct unordered_map {
        unordered_map() {}
        unordered_map(std::initializer_list<pair<K, V>>) {}
        V& operator[](const K&) { static V dummy; return dummy; }
        V& at(const K&) { static V dummy; return dummy; }
        const V& at(const K&) const { static V dummy; return dummy; }
        size_t count(const K&) const { return 0; }
        size_t size() const { return 0; }
        bool empty() const { return true; }
        void insert(const pair<K, V>&) {}
        template<typename... Args> void emplace(Args&&...) {}
        pair<K, V>* begin() { return nullptr; }
        pair<K, V>* end() { return nullptr; }
        pair<K, V>* find(const K&) { return nullptr; }
        const pair<K, V>* begin() const { return nullptr; }
        const pair<K, V>* end() const { return nullptr; }
        const pair<K, V>* find(const K&) const { return nullptr; }
        const pair<K, V>* cbegin() const { return nullptr; }
        const pair<K, V>* cend() const { return nullptr; }
    };

    template<typename T, typename C = void, typename A = void>
    struct set {
        set() {}
        set(std::initializer_list<T>) {}
        void insert(const T&) {}
        size_t count(const T&) const { return 0; }
        size_t size() const { return 0; }
        bool empty() const { return true; }
        T* begin() { return nullptr; }
        T* end() { return nullptr; }
        T* find(const T&) { return nullptr; }
        const T* begin() const { return nullptr; }
        const T* end() const { return nullptr; }
        const T* find(const T&) const { return nullptr; }
        const T* cbegin() const { return nullptr; }
        const T* cend() const { return nullptr; }
    };

    template<typename T, typename H = void, typename E = void, typename A = void>
    struct unordered_set {
        unordered_set() {}
        unordered_set(std::initializer_list<T>) {}
        void insert(const T&) {}
        size_t count(const T&) const { return 0; }
        size_t size() const { return 0; }
        bool empty() const { return true; }
        T* begin() { return nullptr; }
        T* end() { return nullptr; }
        T* find(const T&) { return nullptr; }
        const T* begin() const { return nullptr; }
        const T* end() const { return nullptr; }
        const T* find(const T&) const { return nullptr; }
        const T* cbegin() const { return nullptr; }
        const T* cend() const { return nullptr; }
    };

    template<typename T, typename C = void, typename A = void>
    struct multiset {
        multiset() {}
        multiset(std::initializer_list<T>) {}
        void insert(const T&) {}
        size_t count(const T&) const { return 0; }
        size_t size() const { return 0; }
        bool empty() const { return true; }
        T* begin() { return nullptr; }
        T* end() { return nullptr; }
        T* find(const T&) { return nullptr; }
        const T* begin() const { return nullptr; }
        const T* end() const { return nullptr; }
        const T* find(const T&) const { return nullptr; }
        const T* cbegin() const { return nullptr; }
        const T* cend() const { return nullptr; }
    };

    template<typename K, typename V, typename C = void, typename A = void>
    struct multimap {
        multimap() {}
        multimap(std::initializer_list<pair<K, V>>) {}
        size_t count(const K&) const { return 0; }
        size_t size() const { return 0; }
        bool empty() const { return true; }
        pair<K, V>* begin() { return nullptr; }
        pair<K, V>* end() { return nullptr; }
        pair<K, V>* find(const K&) { return nullptr; }
        const pair<K, V>* begin() const { return nullptr; }
        const pair<K, V>* end() const { return nullptr; }
        const pair<K, V>* find(const K&) const { return nullptr; }
        const pair<K, V>* cbegin() const { return nullptr; }
        const pair<K, V>* cend() const { return nullptr; }
    };

    template<typename T> struct list {
        list() {}
        list(std::initializer_list<T>) {}
        void push_back(const T&) {}
        void push_front(const T&) {}
        void sort() {}
        template<typename Comp> void sort(Comp) {}
        void reverse() {}
        T& front() { static T dummy; return dummy; }
        T& back() { static T dummy; return dummy; }
        T* begin() { return nullptr; }
        T* end() { return nullptr; }
        const T* begin() const { return nullptr; }
        const T* end() const { return nullptr; }
        const T* cbegin() const { return nullptr; }
        const T* cend() const { return nullptr; }
        size_t size() const { return 0; }
        bool empty() const { return true; }
    };
    template<typename T> struct deque {
        deque() {}
        deque(std::initializer_list<T>) {}
        void push_back(const T&) {}
        void push_front(const T&) {}
        void pop_back() {}
        void pop_front() {}
        T& front() { static T dummy; return dummy; }
        T& back() { static T dummy; return dummy; }
        T& operator[](size_t) { static T dummy; return dummy; }
        const T& operator[](size_t) const { static T dummy; return dummy; }
        T* begin() { return nullptr; }
        T* end() { return nullptr; }
        const T* begin() const { return nullptr; }
        const T* end() const { return nullptr; }
        const T* cbegin() const { return nullptr; }
        const T* cend() const { return nullptr; }
        size_t size() const { return 0; }
        bool empty() const { return true; }
    };
    template<typename T> struct forward_list {
        forward_list() {}
        forward_list(std::initializer_list<T>) {}
        void push_front(const T&) {}
        T& front() { static T dummy; return dummy; }
        T* begin() { return nullptr; }
        T* end() { return nullptr; }
        const T* begin() const { return nullptr; }
        const T* end() const { return nullptr; }
        const T* cbegin() const { return nullptr; }
        const T* cend() const { return nullptr; }
        size_t size() const { return 0; }
        bool empty() const { return true; }
    };
    template<typename T> struct stack {
        void push(const T&) {}
        void pop() {}
        T& top() { static T dummy; return dummy; }
        bool empty() const { return true; }
        size_t size() const { return 0; }
    };
    template<typename T> struct queue {
        void push(const T&) {}
        void pop() {}
        T& front() { static T dummy; return dummy; }
        T& back() { static T dummy; return dummy; }
        bool empty() const { return true; }
        size_t size() const { return 0; }
    };
    template<typename T = void> struct less { bool operator()(const T&, const T&) const { return true; } };
    template<typename T = void> struct greater { bool operator()(const T&, const T&) const { return true; } };

    template<typename T, typename Container = vector<T>, typename Compare = less<T>>
    struct priority_queue {
        priority_queue() {}
        void push(const T&) {}
        void pop() {}
        const T& top() const { static T dummy; return dummy; }
        bool empty() const { return true; }
        size_t size() const { return 0; }
    };
    template<typename T = void> struct multiplies { T operator()(const T& a, const T& b) const { return a * b; } };
    template<typename T = void> struct plus { T operator()(const T& a, const T& b) const { return a + b; } };
    template<typename T = void> struct minus { T operator()(const T& a, const T& b) const { return a - b; } };

    template<size_t N> struct bitset {
        bitset() {}
        bitset(unsigned long long) {}
        bitset(const string&) {}
        bitset(const char*) {}
        bool test(size_t) const { return false; }
        void set(size_t) {}
        void reset(size_t) {}
        size_t count() const { return 0; }
        size_t size() const { return N; }
        unsigned long to_ulong() const { return 0; }
        unsigned long long to_ullong() const { return 0; }
        string to_string() const { return string(); }
    };

    // Streams & I/O
    struct ios_base {
        enum fmtflags { dec = 1, hex = 2, oct = 4, fixed = 8, scientific = 16, right = 32, left = 64, boolalpha = 128, app = 256, in = 512, out = 1024, binary = 2048, trunc = 4096, ate = 8192 };
        typedef fmtflags openmode;
        static const fmtflags floatfield = fixed;
        static bool sync_with_stdio(bool = true) { return true; }
    };
    inline ios_base::fmtflags operator|(ios_base::fmtflags a, ios_base::fmtflags b) {
        return static_cast<ios_base::fmtflags>(static_cast<int>(a) | static_cast<int>(b));
    }
    typedef ios_base ios;
    struct istream {
        template<typename T> istream& operator>>(T&) { return *this; }
        bool good() const { return true; }
        bool fail() const { return false; }
        bool bad() const { return false; }
        bool eof() const { return false; }
        explicit operator bool() const { return true; }
        bool operator!() const { return false; }
        void clear() {}
    };
    struct ostream {
        template<typename T> ostream& operator<<(const T&) { return *this; }
        ostream& operator<<(ostream& (*pf)(ostream&)) { return pf(*this); }
        void unsetf(ios_base::fmtflags) {}
        void setf(ios_base::fmtflags) {}
        void setf(ios_base::fmtflags, ios_base::fmtflags) {}
        char fill() const { return ' '; }
        char fill(char c) { return c; }
        int precision() const { return 6; }
        int precision(int p) { return p; }
        int width() const { return 0; }
        int width(int w) { return w; }
        bool good() const { return true; }
        bool fail() const { return false; }
        bool bad() const { return false; }
        bool eof() const { return false; }
        explicit operator bool() const { return true; }
        bool operator!() const { return false; }
        void clear() {}
    };
    inline ostream& endl(ostream& os) { return os; }
    inline ostream& flush(ostream& os) { return os; }
    inline ostream& boolalpha(ostream& os) { return os; }
    inline ostream& noboolalpha(ostream& os) { return os; }

    extern istream cin;
    extern ostream cout;
    extern ostream cerr;
    extern ostream clog;

    struct stringstream : ostream, istream {
        stringstream() {}
        stringstream(const string&) {}
        string str() const { return string(); }
        void str(const string&) {}
        explicit operator bool() const { return true; }
        bool operator!() const { return false; }
    };
    struct istringstream : istream {
        istringstream(const string&) {}
        string str() const { return string(); }
        explicit operator bool() const { return true; }
        bool operator!() const { return false; }
    };
    struct ostringstream : ostream {
        ostringstream() {}
        string str() const { return string(); }
        explicit operator bool() const { return true; }
        bool operator!() const { return false; }
    };

    struct ifstream : istream {
        ifstream() {}
        ifstream(const char*, ios_base::fmtflags = (ios_base::fmtflags)0) {}
        ifstream(const string&, ios_base::fmtflags = (ios_base::fmtflags)0) {}
        void open(const char*, ios_base::fmtflags = (ios_base::fmtflags)0) {}
        void open(const string&, ios_base::fmtflags = (ios_base::fmtflags)0) {}
        void close() {}
        bool is_open() const { return true; }
        explicit operator bool() const { return true; }
        bool operator!() const { return false; }
    };
    struct ofstream : ostream {
        ofstream() {}
        ofstream(const char*, ios_base::fmtflags = (ios_base::fmtflags)0) {}
        ofstream(const string&, ios_base::fmtflags = (ios_base::fmtflags)0) {}
        void open(const char*, ios_base::fmtflags = (ios_base::fmtflags)0) {}
        void open(const string&, ios_base::fmtflags = (ios_base::fmtflags)0) {}
        void close() {}
        bool is_open() const { return true; }
        explicit operator bool() const { return true; }
        bool operator!() const { return false; }
    };

    // Smart Pointers
    template<typename T>
    struct default_delete {
        void operator()(T* p) const { delete p; }
    };

    template<typename T, typename D = default_delete<T>>
    struct unique_ptr {
        T* ptr;
        unique_ptr() : ptr(nullptr) {}
        explicit unique_ptr(T* p) : ptr(p) {}
        unique_ptr(unique_ptr&& u) : ptr(u.ptr) { u.ptr = nullptr; }
        template<typename U, typename D2>
        unique_ptr(unique_ptr<U, D2>&& u) : ptr(u.release()) {}
        ~unique_ptr() {}
        unique_ptr& operator=(unique_ptr&& u) { ptr = u.ptr; u.ptr = nullptr; return *this; }
        template<typename U, typename D2>
        unique_ptr& operator=(unique_ptr<U, D2>&& u) { ptr = u.release(); return *this; }
        T* get() const { return ptr; }
        T* release() { T* p = ptr; ptr = nullptr; return p; }
        void reset(T* p = nullptr) { ptr = p; }
        T& operator*() const { return *ptr; }
        T* operator->() const { return ptr; }
        T& operator[](size_t) const { static T dummy; return dummy; }
        explicit operator bool() const { return ptr != nullptr; }
        bool operator==(nullptr_t) const { return ptr == nullptr; }
        bool operator!=(nullptr_t) const { return ptr != nullptr; }
    };

    template<typename U, typename D>
    struct unique_ptr<U[], D> {
        U* ptr;
        unique_ptr() : ptr(nullptr) {}
        explicit unique_ptr(U* p) : ptr(p) {}
        unique_ptr(unique_ptr&& u) : ptr(u.ptr) { u.ptr = nullptr; }
        ~unique_ptr() {}
        unique_ptr& operator=(unique_ptr&& u) { ptr = u.ptr; u.ptr = nullptr; return *this; }
        U* get() const { return ptr; }
        U* release() { U* p = ptr; ptr = nullptr; return p; }
        void reset(U* p = nullptr) { ptr = p; }
        U& operator[](size_t) const { static U dummy; return dummy; }
        explicit operator bool() const { return ptr != nullptr; }
        bool operator==(nullptr_t) const { return ptr == nullptr; }
        bool operator!=(nullptr_t) const { return ptr != nullptr; }
    };

    template<typename T, typename... Args>
    unique_ptr<T> make_unique(Args&&... args) { return unique_ptr<T>(); }

    template<typename T>
    struct shared_ptr {
        T* ptr;
        shared_ptr() : ptr(nullptr) {}
        explicit shared_ptr(T* p) : ptr(p) {}
        shared_ptr(const shared_ptr& s) : ptr(s.ptr) {}
        shared_ptr(shared_ptr&& s) : ptr(s.ptr) { s.ptr = nullptr; }
        template<typename U>
        shared_ptr(const shared_ptr<U>& s) : ptr(s.get()) {}
        template<typename U>
        shared_ptr(shared_ptr<U>&& s) : ptr(s.get()) {}
        template<typename U>
        shared_ptr(unique_ptr<U>&& u) : ptr(u.release()) {}
        ~shared_ptr() {}
        shared_ptr& operator=(const shared_ptr& s) { ptr = s.ptr; return *this; }
        template<typename U>
        shared_ptr& operator=(const shared_ptr<U>& s) { ptr = s.get(); return *this; }
        T* get() const { return ptr; }
        void reset(T* p = nullptr) { ptr = p; }
        T& operator*() const { return *ptr; }
        T* operator->() const { return ptr; }
        T& operator[](size_t) const { static T dummy; return dummy; }
        explicit operator bool() const { return ptr != nullptr; }
        bool operator==(nullptr_t) const { return ptr == nullptr; }
        bool operator!=(nullptr_t) const { return ptr != nullptr; }
        long use_count() const { return 1; }
    };

    template<typename T, typename... Args>
    shared_ptr<T> make_shared(Args&&... args) { return shared_ptr<T>(new T(args...)); }

    template<typename T>
    struct weak_ptr {
        weak_ptr() {}
        weak_ptr(const shared_ptr<T>&) {}
        shared_ptr<T> lock() const { return shared_ptr<T>(); }
        bool expired() const { return false; }
    };

    // Exceptions
    struct exception {
        virtual ~exception() {}
        virtual const char* what() const noexcept { return "std::exception"; }
    };
    struct runtime_error : exception {
        string msg;
        runtime_error(const char* m) : msg(m) {}
        runtime_error(const string& m) : msg(m) {}
        virtual const char* what() const noexcept override { return msg.c_str(); }
    };
    struct logic_error : exception {
        logic_error(const char*) {}
        logic_error(const string&) {}
    };
    struct out_of_range : logic_error {
        out_of_range(const char* m) : logic_error(m) {}
        out_of_range(const string& m) : logic_error(m) {}
    };
    struct invalid_argument : logic_error {
        invalid_argument(const char* m) : logic_error(m) {}
        invalid_argument(const string& m) : logic_error(m) {}
    };

    // Modern C++ Utilities
    template<typename T>
    struct optional {
        bool has;
        T val;
        optional() : has(false) {}
        optional(const T& v) : has(true), val(v) {}
        bool has_value() const { return has; }
        explicit operator bool() const { return has; }
        T& value() { return val; }
        const T& value() const { return val; }
        T value_or(const T& def) const { return has ? val : def; }
        T& operator*() { return val; }
        const T& operator*() const { return val; }
        T* operator->() { return &val; }
    };

    template<typename... Types>
    struct variant {
        variant() {}
        template<typename T> variant(const T&) {}
        size_t index() const { return 0; }
    };

    template<typename T, typename... Types>
    T& get(variant<Types...>&) { static T dummy; return dummy; }

    template<typename T, typename... Types>
    bool holds_alternative(const variant<Types...>&) { return true; }

    template<typename Visitor, typename... Variants>
    auto visit(Visitor&&, Variants&&...) { return 0; }

    struct any {
        any() {}
        template<typename T> any(const T&) {}
        bool has_value() const { return true; }
    };

    template<typename T>
    T any_cast(const any&) { static T dummy; return dummy; }

    // Concurrency
    struct mutex {
        void lock() {}
        bool try_lock() { return true; }
        void unlock() {}
    };
    struct recursive_mutex {
        void lock() {}
        void unlock() {}
    };
    template<typename M>
    struct lock_guard {
        lock_guard(M&) {}
    };
    template<typename M>
    struct unique_lock {
        unique_lock(M&) {}
        void lock() {}
        void unlock() {}
    };
    struct condition_variable {
        void notify_one() {}
        void notify_all() {}
        template<typename L> void wait(L&) {}
        template<typename L, typename P> void wait(L&, P) {}
    };
    struct thread {
        template<typename F, typename... Args>
        explicit thread(F, Args...) {}
        thread() {}
        ~thread() {}
        bool joinable() const { return true; }
        void join() {}
        void detach() {}
    };
    namespace this_thread {
        inline void yield() {}
        template<typename D>
        void sleep_for(const D&) {}
    }
    template<typename T>
    struct atomic {
        atomic() {}
        atomic(T) {}
        T load() const { return T(); }
        void store(T) {}
        T exchange(T) { return T(); }
        T operator++() { return T(); }
        T operator++(int) { return T(); }
        T operator--() { return T(); }
        T operator--(int) { return T(); }
        T fetch_add(T) { return T(); }
        T fetch_sub(T) { return T(); }
    };
    enum class launch { async = 1, deferred = 2 };

    template<typename T>
    struct future {
        T get() { return T(); }
        void wait() {}
    };

    template<typename T>
    struct promise {
        promise() {}
        future<T> get_future() { return future<T>(); }
        void set_value(const T&) {}
        void set_value() {}
    };

    template<typename F, typename... Args>
    auto async(F f, Args... args) -> future<decltype(f(args...))> {
        return future<decltype(f(args...))>();
    }
    template<typename F, typename... Args>
    auto async(launch, F f, Args... args) -> future<decltype(f(args...))> {
        return future<decltype(f(args...))>();
    }

    // Chrono
    namespace chrono {
        struct nanoseconds {};
        struct microseconds {};
        struct milliseconds {
            milliseconds(long long = 0) {}
            long long count() const { return 0; }
        };
        struct seconds {};
        struct minutes {};
        struct hours {};
        struct time_point {
            time_point() {}
            milliseconds operator-(const time_point&) const { return milliseconds(); }
        };
        struct system_clock {
            typedef chrono::time_point time_point;
            static time_point now() { return time_point(); }
        };
        struct steady_clock {
            typedef chrono::time_point time_point;
            static time_point now() { return time_point(); }
        };
        template<typename D, typename T>
        D duration_cast(const T&) { return D(); }
    }

    // Random
    struct random_device {
        unsigned operator()() { return 0; }
    };
    struct mt19937 {
        mt19937(unsigned = 0) {}
    };
    template<typename T = int>
    struct uniform_int_distribution {
        uniform_int_distribution(T, T) {}
        template<typename G> T operator()(G&) { return T(); }
    };
    template<typename T = double>
    struct uniform_real_distribution {
        uniform_real_distribution(T, T) {}
        template<typename G> T operator()(G&) { return T(); }
    };
    template<typename T = double>
    struct normal_distribution {
        normal_distribution(T = 0.0, T = 1.0) {}
        template<typename G> T operator()(G&) { return T(); }
    };
    template<typename It, typename G> void shuffle(It, It, G&&) {}
    inline void srand(unsigned) {}
    inline int rand() { return 0; }

    // Regex
    struct regex {
        regex(const char*) {}
        regex(const string&) {}
    };
    struct smatch {
        string operator[](size_t) const { return string(); }
        size_t size() const { return 0; }
        bool empty() const { return true; }
        string str(size_t = 0) const { return string(); }
    };
    inline bool regex_search(const string&, smatch&, const regex&) { return true; }
    inline bool regex_search(const string&, const regex&) { return true; }
    inline bool regex_match(const string&, smatch&, const regex&) { return true; }
    inline bool regex_match(const string&, const regex&) { return true; }
    inline string regex_replace(const string&, const regex&, const string&) { return string(); }

    // Algorithms & Functions
    template<typename It> void sort(It, It) {}
    template<typename It, typename Comp> void sort(It, It, Comp) {}
    template<typename It, typename T> It find(It first, It last, const T&) { return first; }
    template<typename It, typename Pred> It find_if(It first, It last, Pred) { return first; }
    template<typename It, typename T> T accumulate(It, It, T init) { return init; }
    template<typename It, typename T, typename Op> T accumulate(It, It, T init, Op) { return init; }
    template<typename It, typename F> F for_each(It, It, F f) { return f; }
    template<typename In, typename Out, typename Op> Out transform(In, In, Out res, Op) { return res; }
    template<typename In, typename Out> Out copy(In, In, Out res) { return res; }
    template<typename It, typename T> It remove(It first, It last, const T&) { return first; }
    template<typename It, typename T> bool binary_search(It first, It last, const T&) { return true; }
    template<typename It, typename Pred> bool all_of(It first, It last, Pred) { return true; }
    template<typename It, typename Pred> bool any_of(It first, It last, Pred) { return true; }
    template<typename It, typename Pred> bool none_of(It first, It last, Pred) { return true; }
    template<typename It> void reverse(It, It) {}
    template<typename It> It max_element(It first, It last) { return first; }
    template<typename It> It min_element(It first, It last) { return first; }
    template<typename It, typename Pred> size_t count_if(It first, It last, Pred) { return 0; }
    template<typename It, typename T> void iota(It first, It last, T) {}
    template<typename In, typename Out> Out partial_sum(In first, In last, Out res) { return res; }
    template<typename In1, typename In2, typename Out> Out set_intersection(In1, In1, In2, In2, Out res) { return res; }
    template<typename C> auto back_inserter(C&) { static int dummy; return &dummy; }
    template<typename It> size_t distance(It, It) { return 0; }
    template<typename It> void rotate(It, It, It) {}
    template<typename It> It unique(It first, It last) { return first; }
    template<typename It, typename T> void fill(It, It, const T&) {}
    template<typename T> struct ostream_iterator {
        ostream_iterator(ostream&, const char* = "") {}
    };
    template<typename It, typename Pred> It partition(It first, It last, Pred) { return first; }
    template<typename It> void nth_element(It first, It nth, It last) {}
    template<typename It, typename T> It lower_bound(It first, It last, const T&) { return first; }
    template<typename It> bool next_permutation(It first, It last) { return true; }
    inline int gcd(int a, int b) { return 1; }
    inline int lcm(int a, int b) { return 1; }
    template<typename F, typename... BindArgs>
    struct __binder {
        template<typename... CallArgs>
        auto operator()(CallArgs&&...) const { return 0; }
    };
    template<typename F, typename... Args> auto bind(F&&, Args&&...) { return __binder<F, Args...>{}; }
    namespace placeholders {
        struct __ph {};
        static const __ph _1, _2, _3;
    }
    template<typename T> const T& min(const T& a, const T& b) { return (a < b) ? a : b; }
    template<typename T> const T& max(const T& a, const T& b) { return (a > b) ? a : b; }

    template<typename T> struct function;
    template<typename R, typename... Args>
    struct function<R(Args...)> {
        function() {}
        template<typename F> function(F) {}
        R operator()(Args... args) const { return R(); }
    };

    // Conversions
    inline int stoi(const string&, size_t* = nullptr, int = 10) { return 0; }
    inline double stod(const string&, size_t* = nullptr) { return 0.0; }
    inline float stof(const string&, size_t* = nullptr) { return 0.0f; }
    inline long stol(const string&, size_t* = nullptr, int = 10) { return 0; }
    inline long long stoll(const string&, size_t* = nullptr, int = 10) { return 0; }
    inline string to_string(int) { return string(); }
    inline string to_string(long) { return string(); }
    inline string to_string(long long) { return string(); }
    inline string to_string(unsigned) { return string(); }
    inline string to_string(double) { return string(); }
    inline string to_string(float) { return string(); }

    template<typename T>
    constexpr typename std::remove_reference<T>::type&& move(T&& t) noexcept {
        return static_cast<typename std::remove_reference<T>::type&&>(t);
    }
    template<typename T>
    constexpr T&& forward(typename std::remove_reference<T>::type& t) noexcept {
        return static_cast<T&&>(t);
    }
}

// Manipulators
namespace std {
    inline ostream& setprecision(int) { static ostream os; return os; }
    inline ostream& setw(int) { static ostream os; return os; }
    inline ostream& setfill(char) { static ostream os; return os; }
    inline ostream& fixed(ostream& os) { return os; }
    inline ostream& scientific(ostream& os) { return os; }
    inline ostream& hex(ostream& os) { return os; }
    inline ostream& dec(ostream& os) { return os; }
}
#else
int printf(const char* format, ...);
int scanf(const char* format, ...);
int puts(const char* s);
int sprintf(char* str, const char* format, ...);
int snprintf(char* str, size_t size, const char* format, ...);
void* malloc(size_t size);
void* calloc(size_t num, size_t size);
void* realloc(void* ptr, size_t size);
void free(void* ptr);
void exit(int status);
void abort(void);
int atoi(const char* str);
long atol(const char* str);
double atof(const char* str);
int abs(int n);
int rand(void);
void srand(unsigned int seed);
char* strcpy(char* dest, const char* src);
char* strncpy(char* dest, const char* src, size_t n);
char* strcat(char* dest, const char* src);
char* strncat(char* dest, const char* src, size_t n);
int strcmp(const char* s1, const char* s2);
int strncmp(const char* s1, const char* s2, size_t n);
size_t strlen(const char* s);
void* memset(void* s, int c, size_t n);
void* memcpy(void* dest, const void* src, size_t n);
void* memmove(void* dest, const void* src, size_t n);
int memcmp(const void* s1, const void* s2, size_t n);
#endif // __cplusplus

#endif // __STD_DEFS_H__
