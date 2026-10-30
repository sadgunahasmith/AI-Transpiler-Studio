import java.util.*;
import java.io.*;

public class Main {
    public static class math_utils {
        final double PI = 3.141592653589793;
        public static int add(int a, int b) {
            return (a + b);
        }

        public static double add(double a, double b) {
            return (a + b);
        }

        public static class nested {
            public static int triple(int x) {
                return (3 * x);
            }

        }
    }

    /* alias: alias_target = math_utils.nested; */
    public static int g_counter = 0;
    public static final int G_CONST = 42;
    public static final int G_CONSTEXPR = 7;
    public static int s_static_global = 5;
    public static int g_extern_decl;
    public static int g_extern_decl = 99;
    public enum Color {
        RED, GREEN, BLUE;
    }

    public enum Direction {
        North, East, South, West;
    }

    /* template <typename T> using Vec = std::vector<T> */
    public static class Point {
        public int x;
        public int y;
        public Point() {
        }

        public Point(int x_, int y_) {
            this.x = x_;
            this.y = y_;
        }

        public boolean op_equals(Point o) {
            return ((this.x == o.x) && (this.y == o.y));
        }

    }

    public static class IntOrFloat {
        public int i;
        public float f;
    }

    public static class Flags {
        public long a;
        public long b;
        public long c;
    }

    public static class Shape {
    }

    public static int factorial(int n) {
    }


    public static class Shape {
        public String name_;
        public Shape(String n) {
            this.name_ = n;
        }

        /* destructor: ~Shape */
        public double area() {
        }

        public double perimeter() {
        }

        public String describe() {
            return ((this.name_ + " area=") + String.valueOf(this.area()));
        }

        public String name() {
            return this.name_;
        }

    }

    public static class Circle extends Shape {
        public double r_;
        public Circle(double r) {
            Shape("Circle");
            this.r_ = r;
        }

        public double area() {
            return ((math_utils.PI * this.r_) * this.r_);
        }

        public double perimeter() {
            return ((2 * math_utils.PI) * this.r_);
        }

    }

    public static class Rectangle extends Shape {
        public double w_;
        public double h_;
        public Rectangle(double w, double h) {
            Shape("Rectangle");
            this.w_ = w;
            this.h_ = h;
        }

        public double area() {
            return (this.w_ * this.h_);
        }

        public double perimeter() {
            return (2 * (this.w_ + this.h_));
        }

    }

    public static class Square extends Rectangle {
        public Square(double s) {
            Rectangle(s, s);
            this.name_ = "Square";
        }

        public String describe() {
            return ("[Square] " + class Rectangle.describe());
        }

        /* final */
    }

    public static class Animal {
        public String sound() {
            return string("...");
        }

        /* destructor: ~Animal */
    }

    public static class Walker extends Animal {
        public String walk() {
            return string("walking");
        }

    }

    public static class Swimmer extends Animal {
        public String swim() {
            return string("swimming");
        }

    }

    public static class Duck extends Walker {
        public String sound() {
            return string("Quack");
        }

    }

    public static class Vector2D {
        public double x_;
        public double y_;
        public int instance_count_;
        public Vector2D(double x, double y) {
            this.x_ = x;
            this.y_ = y;
            ++Vector2D.instance_count_;
        }

        public Vector2D(Vector2D o) {
            this.x_ = o.x_;
            this.y_ = o.y_;
            ++Vector2D.instance_count_;
        }

        public Vector2D(Vector2D o) {
            this.x_ = o.x_;
            this.y_ = o.y_;
            o.x_ = 0;
            ++Vector2D.instance_count_;
        }

        /* destructor: ~Vector2D */
        public Vector2D op_=(Vector2D o) {
            this.x_ = o.x_;
            this.y_ = o.y_;
            return *this;
        }

        public Vector2D op_+(Vector2D o) {
            return Vector2D((this.x_ + o.x_), (this.y_ + o.y_));
        }

        public Vector2D op_-(Vector2D o) {
            return Vector2D((this.x_ - o.x_), (this.y_ - o.y_));
        }

        public Vector2D op_*(double s) {
            return Vector2D((this.x_ * s), (this.y_ * s));
        }

        public Vector2D op_+=(Vector2D o) {
            this.x_ += o.x_;
            this.y_ += o.y_;
            return *this;
        }

        public Vector2D op_++() {
            ++this.x_;
            ++this.y_;
            return *this;
        }

        public Vector2D op_++(int ) {
            Vector2D t = Vector2D(*this);
            ++*this;
            return Vector2D(t);
        }

        public boolean op_equals(Vector2D o) {
            return ((this.x_ == o.x_) && (this.y_ == o.y_));
        }

        public boolean op_notEquals(Vector2D o) {
            return !(*this == o);
        }

        public double op_[](int i) {
            return ((i == 0) ? this.x_ : this.y_);
        }

        public double op_()(double k) {
            return (k * (this.x_ + this.y_));
        }

        public boolean op_ bool() {
            return ((this.x_ != 0) || (this.y_ != 0));
        }

        public static int count() {
            return Vector2D.instance_count_;
        }

        public double length() {
            return sqrt(((this.x_ * this.x_) + (this.y_ * this.y_)));
        }

        public std::ostream __str__(var self) {
            return (((((os << "(") << v.x_) << ", ") << v.y_) << ")");
        }

    }

    /* alias: Vector2D.instance_count_ = 0; */
    public static double dot(Vector2D a, Vector2D b) {
        return ((a.x_ * b.x_) + (a.y_ * b.y_));
    }


    public static T max_of(T a, T b) {
        return ((a > b) ? a : b);
    }


    public static class FixedArray {
        public T[N] data_;
        public void FixedArray<T, N>() {
            for (int i = 0; (i < N); ++i) {
                this.data_[i] = T();
            }
        }

        public T op_[](int i) {
            return this.data_[i];
        }

        public int size() {
            return N;
        }

    }
    public static class Box {
        public T value_;
        public void Box<T>(T v) {
            this.value_ = v;
        }

        public T get() {
            return this.value_;
        }

        public String type() {
            return string("generic");
        }

    }
    public static class Box {
        public boolean value_;
        public Box(boolean v) {
            this.value_ = v;
        }

        public boolean get() {
            return this.value_;
        }

        public String type() {
            return string("bool-specialized");
        }

    }

    public static class Box {
        public T ptr_;
        public void Box<type-parameter-0-0 *>(T p) {
            this.ptr_ = p;
        }

        public T get() {
            return *this.ptr_;
        }

        public String type() {
            return string("pointer-specialized");
        }

        /* T */
    }
    public static void sum_all(Args... args) {
        return args;
    }


    public static void print_all(T first, Rest ... rest) {
        (cout << first);
        if ((/* sizeof...(rest) */ > 0)) {
            System.out.print(", ");
            /* rest... */;
        }
    }


    public static std::enable_if_t<std::is_integral_v<T>, String> describe_type(T ) {
        return "integral";
    }


    public static std::enable_if_t<std::is_floating_point_v<T>, String> describe_type(T ) {
        return "floating";
    }


    public static class Fact {
        public int value;
    }
    public static class Fact {
        public int value;
        /* 0 */
    }

    public static int factorial(int n) {
        return ((n <= 1) ? 1 : (n * factorial((n - 1))));
    }


    public static int fib(int n) {
        return ((n < 2) ? n : (fib((n - 1)) + fib((n - 2))));
    }


    public static void swap_ref(int a, int b) {
        int t = a;
        a = b;
        b = t;
    }


    public static void swap_ptr(int a, int b) {
        int t = *a;
        *a = *b;
        *b = t;
    }


    public static int with_default(int a, int b, int c) {
        return ((a + b) + c);
    }


    public static int cube(int x) {
        return ((x * x) * x);
    }


    public static int file_local_fn(int x) {
        return (x + 1);
    }


    public static int must_use() {
        return 1;
    }


    public static int variadic_c_style(int count) {
    }


    public static int gcd(int a, int b) {
        return ((b == 0) ? a : gcd(b, (a % b)));
    }


    public static boolean is_prime(int n) {
        if ((n < 2)) {
            return false;
        }
        for (int i = 2; ((i * i) <= n); ++i) {
            if (((n % i) == 0)) {
                return false;
            }
        }
        return true;
    }


    public static int apply_op(BinaryOp op, int a, int b) {
        return op(a, b);
    }


    public static int op_add(int a, int b) {
        return (a + b);
    }


    public static int op_mul(int a, int b) {
        return (a * b);
    }


    public static decltype(a + b) trailing(int a, int b) {
        return (a + b);
    }


    public static class CustomError extends std::runtime_error {
        public int code_;
        public CustomError(String msg, int code) {
            runtime_error(msg);
            this.code_ = code;
        }

        public int code() {
            return this.code_;
        }

    }

    public static int risky(int x) {
        if ((x < 0)) {
            0;
        }
        if ((x == 0)) {
            0;
        }
        if ((x > 1000)) {
            0;
        }
        return (x * 2);
    }


    public static class Resource {
        public String id_;
        public Resource(String id) {
            this.id_ = id;
            System.out.print("  [ctor " + " " + this.id_ + " " + "]\n");
        }

        /* destructor: ~Resource */
        public void use() {
            System.out.println("  using " + " " + this.id_);
        }

    }

    public static class Node {
        public int data;
        public Node next;
        public Node(int d) {
            this.data = d;
            this.next = null;
        }

    }

    public static Node push_front(Node head, int v) {
        Node n = Node(v);
        n.next = head;
        return n;
    }


    public static void free_list(Node head) {
        while (head) {
            Node t = head.next;
            deletehead;
            head = t;
        }
    }


    public static class TreeNode {
        public int val;
        public std::unique_ptr<TreeNode> left;
        public std::unique_ptr<TreeNode> right;
        public TreeNode(int v) {
            this.val = v;
        }

    }

    public static void tree_insert(std::unique_ptr<TreeNode> root, int v) {
        if (!root) {
            root = TreeNode(v);
            return;
        }
        if ((v < root.val)) {
            tree_insert(root.left, v);
        } else {
            tree_insert(root.right, v);
        }
    }


    public static void tree_inorder(std::unique_ptr<TreeNode> root, List<int> out) {
        if (!root) {
            return;
        }
        tree_inorder(root.left, out);
        out.push_back(root.val);
        tree_inorder(root.right, out);
    }


    public static std::mutex g_mutex = mutex();
    public static std::atomic<int> g_atomic_counter = atomic(0);
    public static void thread_worker(int id, int iterations) {
        for (int i = 0; (i < iterations); ++i) {
            g_atomic_counter.fetch_add(1);
            std::lock_guard<std::mutex> lock = lock_guard(g_mutex);
            g_counter += id;
        }
    }


    public static void section(String title) {
        System.out.print("\n=== " + " " + title + " " + " ===\n");
    }


    public static void test_basic_types_and_operators() {
        section(string("Basic types & operators"));
        char c = "A";
        int s = 100;
        int i = 42;
        long l = 1234567;
        long long ll = 9876543210;
        long ui = 4000000000;
        float f = 3.14;
        double d = 2.718281828;
        long double ld = 0.3333333333333333;
        boolean b = true;
        wchar_t wc = "W";
        char16_t c16 = "x";
        char32_t c32 = "y";
        int i8 = -8;
        uint16_t u16 = 65535;
        long i64 = -1;
        long sz = sizeofint;
        System.out.println(c + " " + " " + " " + 100 + " " + " " + " " + 42 + " " + " " + " " + 1234567 + " " + " " + " " + 9876543210 + " " + " " + " " + 4000000000);
        System.out.println(3.14 + " " + " " + " " + 2.718281828 + " " + " " + " " + 0.3333333333333333 + " " + " " + " " + boolalpha + " " + b);
        System.out.println(((int)(wc)) + " " + " " + " " + ((int)(c16)) + " " + " " + " " + ((int)(c32)) + " " + " " + " " + ((int)(i8)) + " " + " " + " " + 65535 + " " + " " + " " + i64 + " " + " " + " " + sz);
        int a = 17;
        int bb = 5;
        System.out.println(22 + " " + " " + " " + 12 + " " + " " + " " + 85 + " " + " " + " " + 3 + " " + " " + " " + 2);
        System.out.println((17 & 5) + " " + " " + " " + (17 | 5) + " " + " " + " " + (17 ^ 5) + " " + " " + " " + ~a + " " + " " + " " + (17 << 2) + " " + " " + " " + (17 >> 1));
        System.out.println((true && true) + " " + " " + " " + (false || true) + " " + " " + " " + !b);
        int t = ((a > bb) ? a : bb);
        t += 3;
        t -= 1;
        t *= 2;
        t /= 3;
        t %= 7;
        t <<= 2;
        t >>= 1;
        t &= 255;
        t |= 1;
        t ^= 16;
        System.out.println("t=" + " " + t);
        int x = 5;
        int y = x++;
        y += ++x;
        System.out.println("x=" + " " + 5 + " " + " y=" + " " + y);
        int hex = 255;
        int oct = 63;
        int bin = 10;
        int big = 1000000;
        System.out.println(255 + " " + " " + " " + 63 + " " + " " + " " + 10 + " " + " " + " " + 1000000);
        System.out.println(1500.0 + " " + " " + " " + ("a" + 1) + " " + " " + " " + "str" + " " + " " + " " + "raw\nstring");
        double pi = 3.99;
        int truncated = ((int)(pi));
        int cp = &i;
        int mp = ((int)(cp));
        void vp = &i;
        int ip = ((int)(vp));
        float fbits = 1.0;
        int ubits = ((int)(fbits));
        System.out.println(truncated + " " + " " + " " + *mp + " " + " " + " " + *ip + " " + " " + " " + hex + " " + ubits + " " + dec);
        System.out.println(sizeofchar + " " + sizeofint + " " + sizeofdouble + " " + " " + " " + numeric_limits.max() + " " + " " + " " + numeric_limits.epsilon());
        System.out.print(0 + " " + " " + " " + MAX_SIZE + " " + " " + " " + "STRINGIFY(hello)" + " " + " ");
        int var1 = 10;
        System.out.println(10);
    }


    public static void test_control_flow() {
        section(string("Control flow"));
        for (int i = 0; (i < 3); ++i) {
            System.out.print(i + " " + " ");
        }
        System.out.println("");
        int w = 0;
        while ((w < 3)) {
            System.out.print(w++ + " " + " ");
        }
        System.out.println("");
        int dw = 0;
        while ((dw < 3)) {
            System.out.print(dw + " " + " ");
            ++dw;
        }
        System.out.println("");
        for (int i = 0; (i < 10); ++i) {
            if ((i == 2)) {
                continue;
            }
            if ((i == 6)) {
                break;
            }
            System.out.print(i + " " + " ");
        }
        System.out.println("");
        for (int i = 1; (i <= 3); ++i) {
            for (int j = 1; (j <= 3); ++j) {
                if ((j == 3)) {
                    /* goto next_i */;
                }
                System.out.print((i * j) + " " + " ");
                /* next_i:; */;
            }
        }
        System.out.println("");
        for (int v = 0; (v < 5); ++v) {
            switch (v) {
                case 0:
                    System.out.print("zero ");
                case 1:
                    /* case 2: std::cout << "one-or-two " */;
                case 3:
                    System.out.print("three ");
                default:
                    System.out.print("default ");
            }
        }
        System.out.println("");
        int k = 5;
        if (true) {
            System.out.println("init-if " + " " + 5);
        }
        for (int i = 0; (a < b); i++) {
            System.out.print(a + " " + ":" + " " + b + " " + " ");
        }
        System.out.println("");
        Color col = GREEN;
        switch (col) {
            case RED:
                System.out.print("R\n");
            case GREEN:
                System.out.print("G\n");
            default:
                break;
        }
        Direction dir = South;
        System.out.println(((int)(dir)) + " " + " " + " " + BLUE);
    }


    public static void test_arrays_pointers_references() {
        section(string("Arrays / pointers / references"));
        int[5][] arr = new Object[]{1, 2, 3, 4, 5};
        int[2][3][] matrix = new Object[]{new Object[]{1, 2, 3}, new Object[]{4, 5, 6}};
        char[6][] cstr = "hello";
        int p = arr;
        System.out.println(*p + " " + " " + " " + *(p + 2) + " " + " " + " " + p[4] + " " + " " + " " + arr[1]);
        for (int r = 0; (r < 2); ++r) {
            for (int c = 0; (c < 3); ++c) {
                System.out.print(matrix[r][c] + " " + " ");
            }
        }
        System.out.println(cstr + " " + " " + " " + strlen(cstr));
        int a = 1;
        int b = 2;
        swap_ref(a, b);
        System.out.print(1 + " " + 2 + " " + " ");
        swap_ptr(&a, &b);
        System.out.println(1 + " " + 2);
        int pp = &p;
        System.out.println(**pp);
        int ref = arr[3];
        ref = 40;
        System.out.println(arr[3]);
        int cref = 1;
        System.out.println(1);
        int rref = 10;
        System.out.println(10);
        int dyn = 7;
        int dyn_arr = new Object[]{1, 2, 3, 4};
        System.out.println(*dyn + " " + " " + " " + dyn_arr[3]);
        deletedyn;
        deletedyn_arr;
        int np = null;
        System.out.println((np == null));
        Point pt = Point(3, 4);
        Point ppt = &pt;
        System.out.println(ppt.x + " " + " " + " " + *ppt.y);
        int mem = ((int)(malloc((3 * sizeofint))));
        mem[0] = 9;
        mem[1] = 8;
        mem[2] = 7;
        System.out.println(((mem[0] + mem[1]) + mem[2]));
        free(mem);
        var px = pt.x;
        var py = pt.y;
        System.out.println(px + " " + "," + " " + py);
        IntOrFloat u = IntOrFloat();
        u.f = 1.0;
        System.out.println(hex + " " + u.i + " " + dec);
        Flags fl = Flags(1, 5, 9);
        System.out.println(fl.a + " " + fl.b + " " + fl.c);
    }


    public static void test_strings() {
        section(string("Strings"));
        String s = string("Hello, World");
        s += "!";
        System.out.println(s + " " + " len=" + " " + s.length() + " " + " " + " " + s.substr(7, 5) + " " + " " + " " + s.find("World"));
        s.replace(0, 5, "HELLO");
        System.out.println(s);
        s.insert(5, "***");
        System.out.println(s);
        s.erase(5, 3);
        System.out.println(s + " " + " " + " " + s.front() + " " + s.back());
        transform(s.begin(), s.end(), s.begin(), 0);
        System.out.println(s + " " + " " + " " + (s == "hello, world!") + " " + " " + " " + s.compare("abc"));
        String_view sv = string_view("view of text");
        System.out.println(sv.substr(0, 4) + " " + " " + " " + sv.size());
        System.out.println((stoi(string("123")) + 1) + " " + " " + " " + (stod(string("2.5")) * 2) + " " + " " + " " + String.valueOf(3.5));
        std::oStringstream oss = ostringstream();
        (((((((((((oss << "num=") << 42) << " pi=") << fixed) << setprecision(3)) << 3.14159) << " [") << setw(6)) << setfill(".")) << 7) << "]");
        System.out.println(oss.str());
        std::iStringstream iss = istringstream(string("10 20 30"));
        int n;
        int total = 0;
        while ((iss >> n)) {
            total += n;
        }
        System.out.println("total=" + " " + total);
        String csv = string("a,b,c");
        Stringstream ss = stringstream(csv);
        String tok = string();
        while (getline(ss, tok, ',')) {
            System.out.print("<" + " " + tok + " " + ">");
        }
        System.out.println("");
        char[64][] buf;
        snprintf(buf, sizeofbuf, "%05d|%.2f|%s|%c|%x", 42, 3.14159, "str", "z", 255);
        System.out.println(buf);
        printf("printf: %d %s\n", 7, "ok");
        System.out.println(isalpha("a") + " " + isdigit("5") + " " + toupper("q"));
        System.out.println(strcmp("a", "b") + " " + " " + " " + atoi("77"));
        String lit = ""literal"s";
        System.out.println(lit.size());
    }


    public static void test_stl_containers() {
        section(string("STL containers"));
        List<int> v = vector(new Object[]{5, 3, 8, 1, 9, 2});
        v.push_back(7);
        v.emplace_back(4);
        v.insert((v.begin() + 1), 100);
        v.pop_back();
        System.out.println("vec size=" + " " + v.size() + " " + " front=" + " " + v.front() + " " + " back=" + " " + v.back());
        sort(v.begin(), v.end());
        for (int x : v) {
            System.out.print(x + " " + " ");
        }
        System.out.println("");
        v.erase(remove(v.begin(), v.end(), 100), v.end());
        System.out.println(binary_search(v.begin(), v.end(), 8));
        std::array<int, 4> a = array<int, 4>(1, 2, 3, 4);
        System.out.println(a.size() + " " + a.at(2));
        std::list<int> lst = list(new Object[]{3, 1, 2});
        lst.push_front(0);
        lst.sort();
        lst.reverse();
        for (int x : lst) {
            System.out.print(x);
        }
        System.out.println("");
        std::deque<int> dq = deque(new Object[]{1, 2});
        dq.push_front(0);
        dq.push_back(3);
        System.out.println(dq.front() + " " + dq.back() + " " + dq[2]);
        std::forward_list<int> fl = forward_list(new Object[]{1, 2, 3});
        fl.push_front(0);
        for (int x : fl) {
            System.out.print(x);
        }
        System.out.println("");
        Map<String, int> m = map(new Object[]{new Object[]{"one", 1}, new Object[]{"two", 2}});
        m[string("three")] = 3;
        m.insert(pair(string("four"), 4));
        m.emplace("five", 5);
        for (pair<String, int> [k, val] : m) {
            System.out.print(k + " " + "=" + " " + val + " " + " ");
        }
        System.out.println("");
        pair<String, int> it = m.find(string("two"));
        if ((it != m.end())) {
            System.out.println("found " + " " + it.second);
        }
        System.out.println(m.count(string("zzz")) + " " + " " + " " + m.size());
        std::unordered_Map<int, String> um = unordered_map(new Object[]{new Object[]{1, "a"}, new Object[]{2, "b"}});
        um[3] = "c";
        System.out.println(um.at(3) + " " + um.size());
        std::set<int> st = set(new Object[]{3, 1, 2, 3, 1});
        st.insert(10);
        for (int x : st) {
            System.out.print(x + " " + " ");
        }
        System.out.println(st.count(2));
        std::unordered_set<String> us = unordered_set(new Object[]{"x", "y"});
        us.insert(string("z"));
        System.out.println(us.size() + " " + us.count(string("x")));
        std::multiset<int> ms = multiset(new Object[]{1, 1, 2});
        System.out.println(ms.count(1));
        std::multiMap<int, char> mm = multimap(new Object[]{new Object[]{1, "a"}, new Object[]{1, "b"}});
        System.out.println(mm.count(1));
        std::stack<int> stk = stack();
        stk.push(1);
        stk.push(2);
        System.out.print(stk.top());
        stk.pop();
        System.out.println(stk.size());
        std::queue<int> q = queue();
        q.push(1);
        q.push(2);
        System.out.print(q.front() + " " + q.back());
        q.pop();
        System.out.println(q.size());
        std::priority_queue<int> pq = priority_queue();
        pq.push(3);
        pq.push(9);
        pq.push(1);
        System.out.println(pq.top());
        std::priority_queue<int, List<int>, std::greater<int>> minpq = priority_queue();
        minpq.push(3);
        minpq.push(1);
        System.out.println(minpq.top());
        Map.Entry<int, String> pr = pair(1, string("pair"));
        pair<int, double> pr2 = make_pair(2, 3.5);
        System.out.println(pr.first + " " + pr.second + " " + pr2.second);
        std::tuple<int, double, String> tp = tuple(1, 2.5, string("tuple"));
        System.out.println(get<0>(tp) + " " + get<1>(tp) + " " + get<2>(tp));
        var t1 = tp[0];
        var t2 = tp[1];
        var t3 = tp[2];
        System.out.println(t1 + " " + t2 + " " + t3);
        int ta;
        double tb;
        tie(ta, tb, ignore) = tp;
        System.out.println(ta + " " + tb);
        std::bitset<8> bs = bitset(178);
        System.out.println(bs + " " + " " + " " + bs.count() + " " + " " + " " + bs.test(1) + " " + " " + " " + bs.to_ulong());
        List<std::List<int>> grid = vector(3, vector(3, 0));
        for (int i = 0; (i < 3); ++i) {
            grid[i][i] = 1;
        }
        for (List<int> row : grid) {
            for (int x : row) {
                System.out.print(x);
            }
            System.out.print(" ");
        }
        System.out.println("");
    }


    public static void test_algorithms_and_lambdas() {
        section(string("Algorithms & lambdas"));
        List<int> v = vector(new Object[]{4, 2, 9, 1, 7, 3});
        (lambda at main.cpp:609:16) add = 0;
        int base = 10;
        (lambda at main.cpp:611:20) cap_val = 0;
        (lambda at main.cpp:612:20) cap_ref = 0;
        (lambda at main.cpp:613:20) cap_all = 0;
        (lambda at main.cpp:614:20) generic = 0;
        (lambda at main.cpp:615:22) mutable_l = 0;
        System.out.println(add(1, 2) + " " + cap_val(5) + " " + generic(1.5, 2));
        cap_ref(5);
        System.out.println(10 + " " + " " + " " + cap_all() + " " + " " + " " + mutable_l() + " " + mutable_l());
        std::function<int (int)> fact_fn = function(0);
        System.out.println(fact_fn(5));
        sort(v.begin(), v.end(), 0);
        for (int x : v) {
            System.out.print(x + " " + " ");
        }
        System.out.println("");
        System.out.println(accumulate(v.begin(), v.end(), 0) + " " + " " + " " + accumulate(v.begin(), v.end(), 1, multiplies()));
        System.out.println(*max_element(v.begin(), v.end()) + " " + *min_element(v.begin(), v.end()));
        System.out.println(count_if(v.begin(), v.end(), 0));
        System.out.println(any_of(v.begin(), v.end(), 0) + " " + all_of(v.begin(), v.end(), 0) + " " + none_of(v.begin(), v.end(), 0));
        int it = find(v.begin(), v.end(), 7);
        System.out.println(((it != v.end()) ? distance(v.begin(), it) : -1));
        int it2 = find_if(v.begin(), v.end(), 0);
        System.out.println(*it2);
        List<int> sq = vector(v.size());
        transform(v.begin(), v.end(), sq.begin(), 0);
        for (int x : sq) {
            System.out.print(x + " " + " ");
        }
        System.out.println("");
        for_each(v.begin(), v.end(), 0);
        reverse(v.begin(), v.end());
        rotate(v.begin(), (v.begin() + 2), v.end());
        for (int x : v) {
            System.out.print(x + " " + " ");
        }
        System.out.println("");
        List<int> iota_v = vector(5);
        iota(iota_v.begin(), iota_v.end(), 10);
        List<int> part = vector(5);
        partial_sum(iota_v.begin(), iota_v.end(), part.begin());
        for (int x : part) {
            System.out.print(x + " " + " ");
        }
        System.out.println("");
        List<int> a = vector(new Object[]{1, 2, 3, 4});
        List<int> b = vector(new Object[]{3, 4, 5});
        List<int> out = vector();
        set_intersection(a.begin(), a.end(), b.begin(), b.end(), back_inserter(out));
        for (int x : out) {
            System.out.print(x);
        }
        System.out.println("");
        int uq = unique(a.begin(), a.end());
        ((void)(uq));
        List<int> fill_v = vector(4);
        fill(fill_v.begin(), fill_v.end(), 7);
        copy(fill_v.begin(), fill_v.end(), ostream_iterator(cout, ","));
        System.out.println("");
        List<int> partitioned = vector(new Object[]{1, 2, 3, 4, 5, 6});
        partition(partitioned.begin(), partitioned.end(), 0);
        nth_element(partitioned.begin(), (partitioned.begin() + 2), partitioned.end());
        System.out.println(partitioned[2]);
        System.out.println((lower_bound(sq.begin(), sq.end(), 0) - sq.begin()));
        next_permutation(a.begin(), a.end());
        System.out.println(gcd(12, 18) + " " + lcm(4, 6));
        __binder<(lambda at main.cpp:609:16) , int, __ph > bound = bind(add, 100, placeholders._1);
        System.out.println(bound(5));
        std::function<int (int, int)> fn = function(op_mul);
        System.out.println(fn(3, 4));
        System.out.println(apply_op(op_add, 2, 3) + " " + apply_op(0, 9, 4));
    }


    public static void test_classes_and_polymorphism() {
        section(string("Classes & polymorphism"));
        List<std::unique_ptr<Shape>> shapes = vector();
        shapes.push_back(Circle(2.0));
        shapes.push_back(Rectangle(3, 4));
        shapes.push_back(Square(5));
        System.out.print(fixed + " " + setprecision(2));
        for (std::unique_ptr<Shape> sh : shapes) {
            System.out.println(sh.describe() + " " + " perim=" + " " + sh.perimeter());
        }
        Shape raw = shapes[0].get();
        Circle c = ((Circle)(raw));
        if (c) {
            System.out.print("is Circle\n");
        }
        if ((((Rectangle)(raw)) == null)) {
            System.out.print("not Rectangle\n");
        }
        System.out.println(name());
        cout.unsetf(ios_base.floatfield);
        Duck d = Duck();
        System.out.println(d.sound() + " " + d.walk() + " " + d.swim());
        Vector2D v1 = Vector2D(1, 2);
        Vector2D v2 = Vector2D(3, 4);
        Vector2D v3 = (v1 + v2);
        v3 += Vector2D(1, 1);
        ++v3;
        v3++;
        System.out.println(v3 + " " + " " + " " + (v1 == v2) + " " + (v1 != v2) + " " + " " + " " + v1[0] + " " + v2(2.0) + " " + " " + " " + dot(v1, v2) + " " + " " + " " + Vector2D.count() + " " + " " + " " + ((boolean)(v1)));
        Vector2D moved = Vector2D(v3);
        System.out.println(moved + " " + v3);
        System.out.println((v1 * 3.0) + " " + " " + " " + (v2 - v1).length());
    }


    public static void test_templates() {
        section(string("Templates"));
        System.out.println(max_of(3, 7) + " " + max_of(2.5, 1.5) + " " + max_of(string("a"), string("b")));
        FixedArray<int, 5> fa = FixedArray();
        fa[2] = 9;
        System.out.println(fa[2] + " " + fa.size());
        Box<int> bi = Box(5);
        Box<boolean> bb = Box(true);
        int val = 77;
        Box<int > bp = Box(&val);
        System.out.println(bi.type() + " " + bb.type() + " " + bp.type() + " " + bp.get());
        System.out.println(sum_all(1, 2, 3, 4) + " " + sum_all(1.5, 2.5));
        print_all(1, "two", 3.0, "c");
        System.out.println("");
        System.out.println(describe_type(5) + " " + describe_type(2.5));
        System.out.println(Fact.value + " " + " " + " " + fib(10));
        final int cx = fib(8);
        Vec<int> vv = vector(new Object[]{1, 2});
        IntVec iv = vector(new Object[]{3});
        StrMap sm = map(new Object[]{new Object[]{"k", 1}});
        System.out.println(vv.size() + " " + iv.size() + " " + sm.size());
        System.out.println(is_same_v + " " + is_pointer_v + " " + is_class_v);
    }


    public static void test_exceptions() {
        section(string("Exceptions"));
        int[4][] inputs = new Object[]{5, -1, 0, 5000};
        for (int in : inputs) {
            try {
                System.out.println("risky(" + " " + in + " " + ")=" + " " + risky(in));
            } catch (const CustomError & e) {
                System.out.println("CustomError: " + " " + e.what() + " " + " code=" + " " + e.code());
            } catch (const std::invalid_argument & e) {
                System.out.println("invalid_argument: " + " " + e.what());
            } catch (const std::exception & e) {
                System.out.println("std::exception: " + " " + e.what());
            } catch (Exception e) {
                System.out.print("unknown\n");
            }
        }
        try {
            try {
                0;
            } catch (const std::exception & ) {
                System.out.print("rethrowing\n");
                throw new RuntimeException();
            }
        } catch (const std::runtime_error & e) {
            System.out.println("outer caught " + " " + e.what());
        }
        try {
            List<int> v = vector(2);
            v.at(10);
        } catch (const std::out_of_range & ) {
            System.out.print("vector out_of_range\n");
        }
        try {
            throw 42;
        } catch (int x) {
            System.out.println("int thrown " + " " + x);
        }
        try {
            0;
        } catch (const std::string & s) {
            System.out.println(s);
        }
        (lambda at main.cpp:738:17) safe = 0;
        System.out.println(noexceptsafe());
        ((void)(assert(1 + 1 == 2)));
    }


    public static void test_smart_pointers_and_memory() {
        section(string("Smart pointers & memory"));
        std::unique_ptr<Resource> u = Resource("unique");
        u.use();
        typename std::remove_reference<unique_ptr<Resource> >::type u2 = u;
        System.out.println((u == null));
        std::shared_ptr<Resource> s1 = Resource("shared");
        std::shared_ptr<Resource> s2 = s1;
        std::weak_ptr<Resource> w = weak_ptr(s1);
        System.out.println("use_count=" + " " + s1.use_count() + " " + " expired=" + " " + w.expired());
        s1.reset();
        shared_ptr<Resource> locked = w.lock();
        if (locked) {
            locked.use();
        }
        Node head = null;
        for (int i = 1; (i <= 4); ++i) {
            head = push_front(head, i);
        }
        for (Node n = head; n; n = n.next) {
            System.out.print(n.data + " " + " ");
        }
        System.out.println("");
        free_list(head);
        std::unique_ptr<TreeNode> root = unique_ptr();
        for (int x : new Object[]{5, 3, 8, 1, 4, 9}) {
            tree_insert(root, x);
        }
        List<int> sorted = vector();
        tree_inorder(root, sorted);
        for (int x : sorted) {
            System.out.print(x + " " + " ");
        }
        System.out.println("");
        unique_ptr<int[]> arr = (new Object[]{0} * 3);
        arr[0] = 1;
        arr[2] = 3;
        System.out.println((arr[0] + arr[2]));
        char[8][] buffer;
        Point placed = Point(8, 9);
        System.out.println(placed.x + " " + placed.y);
        placed.~Point();
    }


    public static void test_optional_variant_any() {
        section(string("optional / variant / any"));
        std::optional<int> o1 = optional(5);
        std::optional<int> o2 = optional();
        System.out.println(o1.has_value() + " " + o2.has_value() + " " + o1.value_or(0) + " " + o2.value_or(-1));
        if (o1) {
            System.out.println(*o1);
        }
        std::variant<int, double, String> var = variant(3.14);
        System.out.println(var.index() + " " + get(var));
        var = variant(((String)(string("now string"))));
        visit(0, var);
        if (holds_alternative(var)) {
            System.out.print("holds string\n");
        }
        std::any a = any(10);
        System.out.println(any_cast(a));
        a = any(((String)(string("any-string"))));
        System.out.println(any_cast(a));
    }


    public static void test_chrono_random_regex() {
        section(string("chrono / random / regex"));
        time_point start = chrono.now();
        this_thread.sleep_for(((std::chrono::milliseconds)(milliseconds(5))));
        time_point end = chrono.now();
        long long ms = chrono.chrono.duration_cast((end - start)).count();
        System.out.println("elapsed>=5ms: " + " " + (ms >= 4));
        std::mt19937 gen = mt19937(12345);
        std::uniform_int_distribution<int> dist = uniform_int_distribution(1, 6);
        std::uniform_real_distribution<double> rdist = uniform_real_distribution(0.0, 1.0);
        std::normal_distribution<double> ndist = normal_distribution(0.0, 1.0);
        int roll = dist(gen);
        double r = rdist(gen);
        ((void)(ndist));
        System.out.println(((roll >= 1) && (roll <= 6)) + " " + ((r >= 0) && (r < 1)));
        List<int> shuf = vector(new Object[]{1, 2, 3, 4, 5});
        shuffle(shuf.begin(), shuf.end(), gen);
        srand(1);
        int rr = rand();
        ((void)(rr));
        std::regex re = regex("(\w+)@(\w+)\.com");
        std::smatch m = smatch();
        String email = string("contact: alice@example.com now");
        if (regex_search(email, m, re)) {
            System.out.println(m[1] + " " + " at " + " " + m[2]);
        }
        System.out.println(regex_replace(string("a1b22c333"), ((std::regex)(regex("[0-9]+"))), string("#")));
        System.out.println(regex_match(string("abc123"), ((std::regex)(regex("[a-z]+[0-9]+")))));
        std::time_t now = time(null);
        ((void)(now));
        std::clock_t clk = clock();
        ((void)(clk));
    }


    public static void test_math() {
        section(string("cmath"));
        System.out.print(fixed + " " + setprecision(4));
        System.out.println(sqrt(16.0) + " " + " " + " " + pow(2, 10) + " " + " " + " " + abs(-3.5) + " " + " " + " " + floor(2.7) + " " + " " + " " + ceil(2.1) + " " + " " + " " + round(2.5) + " " + " " + " " + fmod(7.5, 2));
        System.out.println(sin((math_utils.PI / 2)) + " " + " " + " " + cos(0.0) + " " + " " + " " + tan(0.0) + " " + " " + " " + atan2(1, 1) + " " + " " + " " + exp(1.0) + " " + " " + " " + log(exp(2.0)) + " " + " " + " " + log10(1000.0) + " " + " " + " " + hypot(3, 4));
        cout.unsetf(ios_base.floatfield);
        System.out.println(abs(-7) + " " + " " + " " + isnan(nan("")) + " " + " " + " " + isinf(__builtin_inff()));
        System.out.println(math_utils.add(1, 2) + " " + " " + " " + math_utils.add(1.5, 2.5) + " " + " " + " " + alias_target.triple(4) + " " + " " + " " + math_utils.nested.triple(2));
        System.out.println(factorial(6) + " " + " " + " " + gcd(48, 18) + " " + " " + " " + is_prime(97) + " " + " " + " " + with_default(1) + " " + with_default(1, 2) + " " + with_default(1, 2, 3) + " " + " " + " " + cube(3) + " " + " " + " " + file_local_fn(1) + " " + " " + " " + trailing(2, 3) + " " + " " + " " + must_use() + " " + " " + " " + G_CONST + " " + G_CONSTEXPR + " " + s_static_global + " " + g_extern_decl);
    }


    public static void test_file_io() {
        section(string("File I/O"));
        char path = "transpiler_test_tmp.txt";
        std::ofstream out = ofstream(path);
        (out << "line one\nline two\n42 3.14\n");
        std::ifstream in = ifstream(path);
        String line = string();
        while (getline(in, line)) {
            System.out.println("read: " + " " + line);
        }
        std::ofstream app = ofstream(path, app);
        (app << "appended\n");
        std::ifstream in = ifstream(path);
        String word = string();
        int count = 0;
        while ((in >> word)) {
            ++count;
        }
        System.out.println("words=" + " " + count);
        remove(path);
        System.out.print("(this line goes to stderr)\n");
        System.out.print("(this line goes to clog)\n");
    }


    public static void test_threads() {
        section(string("Threads / async / sync"));
        g_counter = 0;
        g_atomic_counter = atomic(0);
        List<std::thread> threads = vector();
        for (int i = 1; (i <= 4); ++i) {
            threads.emplace_back(thread(thread_worker, i, 1000));
        }
        for (std::thread t : threads) {
            t.join();
        }
        System.out.println("atomic=" + " " + g_atomic_counter + " " + " guarded=" + " " + 0);
        std::future<int> fut = async(async, 0);
        System.out.println("async result=" + " " + fut.get());
        std::promise<int> prom = promise();
        std::future<int> pf = prom.get_future();
        std::thread t = thread(0);
        System.out.println("promise=" + " " + pf.get());
        t.join();
        std::mutex m = mutex();
        std::condition_variable cv = condition_variable();
        boolean ready = false;
        std::thread waiter = thread(0);
        std::lock_guard<std::mutex> lk = lock_guard(m);
        ready = true;
        cv.notify_one();
        waiter.join();
        int tls = 0;
        ++tls;
        System.out.println("tls=" + " " + 0);
    }


    public static class Range {
        public int lo_;
        public int hi_;
        public Range(int lo, int hi) {
            this.lo_ = lo;
            this.hi_ = hi;
        }

        public Iter begin() {
            return new Object[]{this.lo_};
        }

        public Iter end() {
            return new Object[]{this.hi_};
        }

        public static class Iter {
            public int v;
            public int op_*() {
                return this.v;
            }

            public Iter op_++() {
                ++this.v;
                return *this;
            }

            public boolean op_notEquals(Iter o) {
                return (this.v != o.v);
            }

        }
    }

    public static void test_custom_iterables_and_misc() {
        section(string("Custom iterables & misc"));
        for (int x : Range(0, 5)) {
            System.out.print(x + " " + " ");
        }
        System.out.println("");
        std::initializer_list<int> init = initializer_list<int>(1, 2, 3);
        System.out.println(init.size());
        (lambda at main.cpp:912:20) lst_sum = 0;
        System.out.println(lst_sum(new Object[]{1, 2, 3, 4}));
        int dref = g_counter;
        ((void)(dref));
        int ()(int) fptr = &factorial;
        System.out.println(fptr(4));
        int Point:: member_ptr = "x";
        Point pt = Point(11, 22);
        System.out.println((pt .* member_ptr));
        System.out.println(__LINE__ + " " + " " + " " + ("__FILE__" != null) + " " + " " + " " + "__func__" + " " + " " + " " + __cplusplus);
        System.out.print("debug on\n");
        volatile int vol = 3;
        /* register_hint:; */;
        System.out.println(3);
        Point p1 = Point(1, 2);
        Point p2 = Point(1, 2);
        System.out.println((p1 == p2));
        System.out.println(boolalpha + " " + (p1 == p2) + " " + noboolalpha);
    }


    public static void main(String[] args) {
        ios_base.sync_with_stdio(false);
        System.out.println("argc=" + " " + argc + " " + " argv0_present=" + " " + (argv[0] != null));
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
        System.out.print("\nAll sections completed.\n");
    }

}
