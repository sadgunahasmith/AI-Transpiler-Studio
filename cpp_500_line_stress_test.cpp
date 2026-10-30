#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <set>
#include <deque>
#include <queue>
#include <stack>
#include <algorithm>
#include <numeric>
#include <functional>
#include <stdexcept>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <memory>
#include <cmath>
#include <limits>
#include <utility>
using namespace std;

// A C++17 campus library management and analytics stress test.
// TRANSPILER COVERAGE NOTE: This source is intentionally C++17.
// COVERAGE: Virtual dispatch should preserve dynamic types.
// COVERAGE: Constructors and initializer lists require correct lowering.
// COVERAGE: Member access should work through smart pointers.
// COVERAGE: std::map keys require stable ordering and lookup.
// COVERAGE: std::vector supports push_back, iterators and indexing.
// COVERAGE: std::deque supports front and back operations.
// COVERAGE: std::queue and std::stack use FIFO and LIFO behavior.
// COVERAGE: std::set automatically removes duplicates.
// COVERAGE: std::sort and std::transform invoke lambdas.
// COVERAGE: Range-based for loops include const references.
// COVERAGE: Standard exceptions must preserve catch selection.
// COVERAGE: File output must write content rather than a stub.
// COVERAGE: I/O format manipulators influence numeric text.
// COVERAGE: No input is required; output is deterministic aside from errors.
// COVERAGE: The source can be built with g++ -std=c++17.
// COVERAGE: Exceptions require inheritance-aware handling.
// COVERAGE: Map emplacement constructs non-default-constructible objects.
// COVERAGE: Pointers returned from findBook and findMember may be null.
// COVERAGE: std::string::find returns std::string::npos on misses.
// COVERAGE: std::ostringstream concatenates formatted fields.
// COVERAGE: std::istringstream tokenizes text with operator>>.
// COVERAGE: Copy operations preserve values and map contents.
// COVERAGE: Sorting uses a strict weak ordering comparator.
// COVERAGE: Functions can return vectors and maps by value.
// COVERAGE: Template specialization is not needed for numeric mean.
// COVERAGE: Accumulate and partial_sum are different algorithms.
namespace campus {
constexpr int MAX_LOANS = 3;
constexpr double FINE_PER_DAY = 2.5;

enum class Category { Science, Fiction, History, Computing, Arts };
string categoryName(Category c) {
    switch (c) {
        case Category::Science: return "Science";
        case Category::Fiction: return "Fiction";
        case Category::History: return "History";
        case Category::Computing: return "Computing";
        default: return "Arts";
    }
}

struct Book {
    int id;
    string title;
    string author;
    Category category;
    int copies;
    int borrowed;
    double rating;
    Book(int i, string t, string a, Category c, int n, double r)
        : id(i), title(t), author(a), category(c), copies(n),
          borrowed(0), rating(r) {}
    int available() const { return copies - borrowed; }
    bool operator<(const Book& other) const { return id < other.id; }
    string description() const {
        ostringstream out;
        out << id << " | " << title << " | " << author;
        out << " | " << categoryName(category) << " | ";
        out << available() << "/" << copies;
        return out.str();
    }
};

class Person {
protected:
    int id_;
    string name_;
public:
    Person(int id, string name) : id_(id), name_(name) {}
    virtual ~Person() = default;
    int id() const { return id_; }
    string name() const { return name_; }
    virtual string role() const = 0;
    virtual void print() const {
        cout << role() << " #" << id_ << " " << name_ << "\n";
    }
};

struct Loan {
    int bookId;
    int days;
    bool returned;
    Loan(int b, int d) : bookId(b), days(d), returned(false) {}
};

class Member : public Person {
private:
    vector<Loan> loans_;
    int points_;
public:
    Member(int id, string name) : Person(id, name), points_(0) {}
    string role() const override { return "Member"; }
    bool canBorrow() const { return activeLoans() < MAX_LOANS; }
    int activeLoans() const {
        int count = 0;
        for (const auto& loan : loans_)
            if (!loan.returned) ++count;
        return count;
    }
    void borrow(int bookId, int days) {
        if (!canBorrow()) throw runtime_error("Loan limit reached");
        loans_.emplace_back(bookId, days);
        points_ += 10;
    }
    bool giveBack(int bookId) {
        for (auto& loan : loans_) {
            if (loan.bookId == bookId && !loan.returned) {
                loan.returned = true;
                return true;
            }
        }
        return false;
    }
    double fine() const {
        double total = 0;
        for (const auto& loan : loans_)
            if (!loan.returned && loan.days > 14)
                total += (loan.days - 14) * FINE_PER_DAY;
        return total;
    }
    int points() const { return points_; }
    const vector<Loan>& loans() const { return loans_; }
    void print() const override {
        Person::print();
        cout << "  Active loans: " << activeLoans();
        cout << " | Points: " << points_;
        cout << " | Fine: " << fixed << setprecision(2) << fine() << "\n";
    }
};

class Librarian : public Person {
    string shift_;
public:
    Librarian(int id, string name, string shift)
        : Person(id, name), shift_(shift) {}
    string role() const override { return "Librarian"; }
    string shift() const { return shift_; }
    void print() const override {
        Person::print();
        cout << "  Shift: " << shift_ << "\n";
    }
};

class Library {
private:
    map<int, Book> books_;
    map<int, Member> members_;
    vector<string> events_;
public:
    void addBook(const Book& b) {
        if (books_.count(b.id)) throw invalid_argument("Duplicate book");
        books_.emplace(b.id, b);
        events_.push_back("Added book " + to_string(b.id));
    }
    void addMember(const Member& m) {
        if (members_.count(m.id())) throw invalid_argument("Duplicate member");
        members_.emplace(m.id(), m);
        events_.push_back("Added member " + to_string(m.id()));
    }
    Book* findBook(int id) {
        auto it = books_.find(id);
        return it == books_.end() ? nullptr : &it->second;
    }
    Member* findMember(int id) {
        auto it = members_.find(id);
        return it == members_.end() ? nullptr : &it->second;
    }
    const Book* findBook(int id) const {
        auto it = books_.find(id);
        return it == books_.end() ? nullptr : &it->second;
    }
    void borrowBook(int memberId, int bookId, int days) {
        Member* member = findMember(memberId);
        Book* book = findBook(bookId);
        if (!member || !book) throw out_of_range("Unknown ID");
        if (book->available() == 0) throw runtime_error("Out of stock");
        member->borrow(bookId, days);
        ++book->borrowed;
        events_.push_back("Borrowed " + to_string(bookId));
    }
    void returnBook(int memberId, int bookId) {
        Member* member = findMember(memberId);
        Book* book = findBook(bookId);
        if (!member || !book) throw out_of_range("Unknown ID");
        if (!member->giveBack(bookId)) throw runtime_error("No active loan");
        --book->borrowed;
        events_.push_back("Returned " + to_string(bookId));
    }
    vector<Book> allBooks() const {
        vector<Book> result;
        for (const auto& item : books_) result.push_back(item.second);
        return result;
    }
    vector<Book> search(const string& text) const {
        vector<Book> result;
        for (const auto& item : books_) {
            const Book& b = item.second;
            if (b.title.find(text) != string::npos ||
                b.author.find(text) != string::npos)
                result.push_back(b);
        }
        return result;
    }
    vector<Book> byCategory(Category category) const {
        vector<Book> result;
        for (const auto& item : books_)
            if (item.second.category == category)
                result.push_back(item.second);
        return result;
    }
    vector<Book> topRated(size_t limit) const {
        vector<Book> result = allBooks();
        sort(result.begin(), result.end(), [](const Book& a, const Book& b) {
            return a.rating == b.rating ? a.id < b.id : a.rating > b.rating;
        });
        if (result.size() > limit) result.erase(result.begin() + limit, result.end());
        return result;
    }
    int totalCopies() const {
        int sum = 0;
        for (const auto& item : books_) sum += item.second.copies;
        return sum;
    }
    int totalBorrowed() const {
        int sum = 0;
        for (const auto& item : books_) sum += item.second.borrowed;
        return sum;
    }
    double averageRating() const {
        if (books_.empty()) return 0.0;
        double sum = 0;
        for (const auto& item : books_) sum += item.second.rating;
        return sum / books_.size();
    }
    double outstandingFines() const {
        double sum = 0;
        for (const auto& item : members_) sum += item.second.fine();
        return sum;
    }
    size_t memberCount() const { return members_.size(); }
    size_t bookCount() const { return books_.size(); }
    const vector<string>& events() const { return events_; }
    void printMembers() const {
        for (const auto& item : members_) item.second.print();
    }
    void printBooks() const {
        for (const auto& item : books_) cout << item.second.description() << "\n";
    }
    void saveCatalog(const string& filename) const {
        ofstream file(filename);
        if (!file) throw runtime_error("Cannot create catalog");
        for (const auto& item : books_) {
            const Book& b = item.second;
            file << b.id << "," << b.title << "," << b.author << ",";
            file << b.copies << "," << b.borrowed << "\n";
        }
    }
    void saveEvents(const string& filename) const {
        ofstream file(filename);
        if (!file) throw runtime_error("Cannot create event log");
        for (const auto& event : events_) file << event << "\n";
    }
};

template <typename T>
T maximumOf(const vector<T>& values) {
    if (values.empty()) throw invalid_argument("Empty collection");
    return *max_element(values.begin(), values.end());
}

template <typename T>
double meanOf(const vector<T>& values) {
    if (values.empty()) return 0.0;
    return accumulate(values.begin(), values.end(), 0.0) / values.size();
}

vector<int> uniqueSorted(vector<int> data) {
    sort(data.begin(), data.end());
    data.erase(unique(data.begin(), data.end()), data.end());
    return data;
}

map<string, int> wordHistogram(const string& text) {
    istringstream input(text);
    map<string, int> counts;
    string word;
    while (input >> word) ++counts[word];
    return counts;
}

vector<int> rollingTotals(const vector<int>& values) {
    vector<int> totals(values.size());
    partial_sum(values.begin(), values.end(), totals.begin());
    return totals;
}

vector<int> evenSquares(const vector<int>& values) {
    vector<int> result;
    for (int x : values)
        if (x % 2 == 0) result.push_back(x * x);
    return result;
}

void printNumbers(const vector<int>& values, const string& label) {
    cout << label << ":";
    for (int value : values) cout << " " << value;
    cout << "\n";
}

void printBooks(const vector<Book>& books, const string& label) {
    cout << label << " (" << books.size() << ")\n";
    for (const auto& b : books) cout << "  " << b.description() << "\n";
}

void populate(Library& library) {
    library.addBook(Book(101, "C++ Fundamentals", "Ada", Category::Computing, 4, 4.8));
    library.addBook(Book(102, "Algorithms", "Knuth", Category::Computing, 3, 4.9));
    library.addBook(Book(103, "Physics", "Feynman", Category::Science, 5, 4.7));
    library.addBook(Book(104, "Astronomy", "Carl", Category::Science, 2, 4.3));
    library.addBook(Book(105, "Ancient Worlds", "Mira", Category::History, 3, 4.1));
    library.addBook(Book(106, "Modern History", "Lena", Category::History, 2, 4.0));
    library.addBook(Book(107, "Stories", "Orwell", Category::Fiction, 6, 4.6));
    library.addBook(Book(108, "Poetry", "Rita", Category::Arts, 3, 4.2));
    library.addBook(Book(109, "Machine Learning", "Ravi", Category::Computing, 2, 4.5));
    library.addBook(Book(110, "Painting", "Nora", Category::Arts, 4, 4.4));
    library.addMember(Member(1, "Alice"));
    library.addMember(Member(2, "Bob"));
    library.addMember(Member(3, "Charlie"));
    library.addMember(Member(4, "Diana"));
    library.addMember(Member(5, "Ethan"));
}

void runLoans(Library& library) {
    library.borrowBook(1, 101, 5);
    library.borrowBook(1, 102, 18);
    library.borrowBook(2, 103, 21);
    library.borrowBook(3, 107, 7);
    library.borrowBook(4, 109, 15);
    library.borrowBook(5, 108, 3);
    cout << "Borrowed copies: " << library.totalBorrowed() << "\n";
    library.returnBook(3, 107);
    cout << "After return: " << library.totalBorrowed() << "\n";
    try {
        library.borrowBook(99, 101, 1);
    } catch (const out_of_range& error) {
        cout << "Expected missing member: " << error.what() << "\n";
    }
    try {
        library.returnBook(3, 107);
    } catch (const runtime_error& error) {
        cout << "Expected repeated return: " << error.what() << "\n";
    }
}

void showAnalytics(const Library& library) {
    cout << "=== Library analytics ===\n";
    cout << "Books: " << library.bookCount() << "\n";
    cout << "Members: " << library.memberCount() << "\n";
    cout << "Copies: " << library.totalCopies() << "\n";
    cout << "Borrowed: " << library.totalBorrowed() << "\n";
    cout << "Average rating: " << fixed << setprecision(2);
    cout << library.averageRating() << "\n";
    cout << "Fines due: " << library.outstandingFines() << "\n";
    printBooks(library.topRated(3), "Top rated books");
    printBooks(library.search("History"), "History title search");
    printBooks(library.byCategory(Category::Science), "Science books");
    cout << "=== Member records ===\n";
    library.printMembers();
}

void algorithmDemos() {
    cout << "=== STL algorithm demonstrations ===\n";
    vector<int> values = {7, 2, 7, 4, 9, 2, 10, 3, 6, 4};
    printNumbers(values, "Input");
    printNumbers(uniqueSorted(values), "Unique sorted");
    printNumbers(rollingTotals(values), "Running totals");
    printNumbers(evenSquares(values), "Even squares");
    cout << "Maximum: " << maximumOf(values) << "\n";
    cout << "Mean: " << meanOf(values) << "\n";
    cout << "Count even: " << count_if(values.begin(), values.end(),
        [](int x) { return x % 2 == 0; }) << "\n";
    vector<int> copied(values.size());
    transform(values.begin(), values.end(), copied.begin(),
        [](int x) { return x * 3; });
    printNumbers(copied, "Tripled");
    reverse(copied.begin(), copied.end());
    printNumbers(copied, "Reversed");
    auto histogram = wordHistogram("red blue red green blue red");
    for (const auto& item : histogram)
        cout << item.first << "=" << item.second << " ";
    cout << "\n";
}

void containerDemos() {
    cout << "=== Additional containers ===\n";
    deque<int> doubleEnded = {2, 3, 4};
    doubleEnded.push_front(1);
    doubleEnded.push_back(5);
    cout << "Deque front/back: " << doubleEnded.front();
    cout << "/" << doubleEnded.back() << "\n";
    queue<string> pending;
    pending.push("request-A");
    pending.push("request-B");
    while (!pending.empty()) {
        cout << "Queue: " << pending.front() << "\n";
        pending.pop();
    }
    stack<int> history;
    for (int i = 1; i <= 3; ++i) history.push(i * 10);
    while (!history.empty()) {
        cout << "Stack: " << history.top() << "\n";
        history.pop();
    }
    set<int> ids = {4, 2, 2, 1, 3};
    cout << "Unique IDs:";
    for (int id : ids) cout << " " << id;
    cout << "\n";
}

void pointerAndPolymorphismDemo() {
    cout << "=== Smart pointers and polymorphism ===\n";
    vector<unique_ptr<Person>> people;
    people.push_back(make_unique<Member>(11, "Nina"));
    people.push_back(make_unique<Librarian>(20, "Oliver", "Morning"));
    people.push_back(make_unique<Member>(12, "Priya"));
    for (const auto& person : people) person->print();
    shared_ptr<int> counter = make_shared<int>(5);
    shared_ptr<int> alias = counter;
    *alias += 3;
    cout << "Shared value: " << *counter << "\n";
    cout << "Reference count: " << counter.use_count() << "\n";
}

void exceptionDemo() {
    cout << "=== Exception handling ===\n";
    vector<int> data = {10, 20, 30};
    try {
        cout << "Value at index 1: " << data.at(1) << "\n";
        cout << data.at(20) << "\n";
    } catch (const out_of_range& error) {
        cout << "Caught range exception: " << error.what() << "\n";
    }
    try {
        vector<int> empty;
        cout << maximumOf(empty) << "\n";
    } catch (const invalid_argument& error) {
        cout << "Caught invalid argument: " << error.what() << "\n";
    }
}

void exportReports(const Library& library) {
    cout << "=== File output ===\n";
    try {
        library.saveCatalog("library_catalog.csv");
        library.saveEvents("library_events.txt");
        cout << "Saved catalog and event log\n";
    } catch (const exception& error) {
        cout << "File error: " << error.what() << "\n";
    }
}
} // namespace campus

int main() {
    using namespace campus;
    cout << "UNIVERSALTRANSPILER C++17 STRESS TEST\n";
    Library library;
    populate(library);
    runLoans(library);
    showAnalytics(library);
    algorithmDemos();
    containerDemos();
    pointerAndPolymorphismDemo();
    exceptionDemo();
    exportReports(library);
    cout << "Completed successfully\n";
    return 0;
}
