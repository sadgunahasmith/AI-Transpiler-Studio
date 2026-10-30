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
      return "Science";
    case Fiction:
      return "Fiction";
    case History:
      return "History";
    case Computing:
      return "Computing";
    default:
      return "Arts";
  }
}

class Book {
  constructor(i, t, a, c, n, r) {
    self.id = i;
    self.title = title;
    string(t);
    self.author = author;
    string(a);
    self.category = c;
    self.copies = n;
    self.borrowed = 0;
    self.rating = r;
  }
  available() {
    return (null.copies - null.borrowed);
  }
  operator_lt(other) {
    return (null.id < other.id);
  }
  description() {
    let out = ostringstream();
    (((((out << null.id) << " | ") << null.title) << " | ") << null.author);
    (((out << " | ") << categoryName(null.category)) << " | ");
    (((out << available()) << "/") << null.copies);
    return out.str();
  }
}

class Person {
  constructor(id, name) {
    self.id_ = id;
    self.name_ = name_;
    string(name);
  }
  destructor_Person() {
  }
  id() {
    return null.id_;
  }
  name() {
    return string(null.name_);
  }
  role() {
  }
  print() {
    console.log(role(), " #", null.id_, " ", null.name_, "\n");
  }
}

class Loan {
  constructor(b, d) {
    self.bookId = b;
    self.days = d;
    self.returned = false;
  }
}

class Member extends Person {
  constructor(id, name) {
    new Person(id, string(name));
    self.points_ = 0;
  }
  role() {
    return "Member";
  }
  canBorrow() {
    return (activeLoans() < MAX_LOANS);
  }
  activeLoans() {
    let count = 0;
    for (const loan of null.loans_) {
      if (!loan.returned) {
        ++count;
      }
    }
    return count;
  }
  borrow(bookId, days) {
    if (!canBorrow()) {
      null;
    }
    loans_.emplace_back(bookId, days);
    null.points_ += 10;
  }
  giveBack(bookId) {
    for (const loan of null.loans_) {
      if (((loan.bookId == bookId) && !loan.returned)) {
        loan.returned = true;
        return true;
      }
    }
    return false;
  }
  fine() {
    let total = 0;
    for (const loan of null.loans_) {
      if ((!loan.returned && (loan.days > 14))) {
        total += ((loan.days - 14) * FINE_PER_DAY);
      }
    }
    return total;
  }
  points() {
    return null.points_;
  }
  loans() {
    return null.loans_;
  }
  print() {
    Person.print();
    console.log("  Active loans: ", activeLoans());
    console.log(" | Points: ", null.points_);
    console.log(" | Fine: ", fixed, setprecision(2), fine(), "\n");
  }
}

class Librarian extends Person {
  constructor(id, name, shift) {
    new Person(id, string(name));
    self.shift_ = shift_;
    string(shift);
  }
  role() {
    return "Librarian";
  }
  shift() {
    return string(null.shift_);
  }
  print() {
    Person.print();
    console.log("  Shift: ", null.shift_, "\n");
  }
}

class Library {
  constructor() {
    this.books_ = null;
    this.members_ = null;
    this.events_ = null;
  }
  addBook(b) {
    if (books_.count(b.id)) {
      null;
    }
    books_.emplace(b.id, b);
    events_.push_back(("Added book " + to_string(b.id)));
  }
  addMember(m) {
    if (members_.count(m.id())) {
      null;
    }
    members_.emplace(m.id(), m);
    events_.push_back(("Added member " + to_string(m.id())));
  }
  findBook(id) {
    let it = books_.find(id);
    return ((it == books_.end()) ? null : it.second);
  }
  findMember(id) {
    it = members_.find(id);
    return ((it == members_.end()) ? null : it.second);
  }
  findBook(id) {
    it = books_.find(id);
    return ((it == books_.end()) ? null : it.second);
  }
  borrowBook(memberId, bookId, days) {
    let member = findMember(memberId);
    let book = findBook(bookId);
    if ((!member || !book)) {
      null;
    }
    if ((book.available() == 0)) {
      null;
    }
    member.borrow(bookId, days);
    ++book.borrowed;
    events_.push_back(("Borrowed " + to_string(bookId)));
  }
  returnBook(memberId, bookId) {
    member = findMember(memberId);
    book = findBook(bookId);
    if ((!member || !book)) {
      null;
    }
    if (!member.giveBack(bookId)) {
      null;
    }
    --book.borrowed;
    events_.push_back(("Returned " + to_string(bookId)));
  }
  allBooks() {
    let result = vector();
    for (const item of null.books_) {
      result.push_back(item.second);
    }
    return vector(result);
  }
  search(text) {
    result = vector();
    for (const item of null.books_) {
      let b = item.second;
      if (((b.title.find(text, /*  */) != npos) || (b.author.find(text, /*  */) != npos))) {
        result.push_back(b);
      }
    }
    return vector(result);
  }
  byCategory(category) {
    result = vector();
    for (const item of null.books_) {
      if ((item.second.category == category)) {
        result.push_back(item.second);
      }
    }
    return vector(result);
  }
  topRated(limit) {
    result = allBooks();
    sort(result.begin(), result.end(), null);
    if ((result.size() > limit)) {
      result.erase((result.begin() + limit), result.end());
    }
    return vector(result);
  }
  totalCopies() {
    let sum = 0;
    for (const item of null.books_) {
      sum += item.second.copies;
    }
    return sum;
  }
  totalBorrowed() {
    sum = 0;
    for (const item of null.books_) {
      sum += item.second.borrowed;
    }
    return sum;
  }
  averageRating() {
    if (books_.empty()) {
      return 0.0;
    }
    sum = 0;
    for (const item of null.books_) {
      sum += item.second.rating;
    }
    return (sum / books_.size());
  }
  outstandingFines() {
    sum = 0;
    for (const item of null.members_) {
      sum += item.second.fine();
    }
    return sum;
  }
  memberCount() {
    return members_.size();
  }
  bookCount() {
    return books_.size();
  }
  events() {
    return null.events_;
  }
  printMembers() {
    for (const item of null.members_) {
      item.second.print();
    }
  }
  printBooks() {
    for (const item of null.books_) {
      console.log(item.second.description(), "\n");
    }
  }
  saveCatalog(filename) {
    let file = ofstream(filename, /*  */);
    if (!file) {
      null;
    }
    for (const item of null.books_) {
      b = item.second;
      ((((((file << b.id) << ",") << b.title) << ",") << b.author) << ",");
      ((((file << b.copies) << ",") << b.borrowed) << "\n");
    }
  }
  saveEvents(filename) {
    file = ofstream(filename, /*  */);
    if (!file) {
      null;
    }
    for (const event of null.events_) {
      ((file << event) << "\n");
    }
  }
}

function maximumOf(values) {
  if (values.empty()) {
    null;
  }
  return max_element(values.begin(), values.end());
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
  while ((input >> word)) {
    ++counts[word];
  }
  return map(counts);
}

function rollingTotals(values) {
  let totals = vector(values.size(), /*  */);
  partial_sum(values.begin(), values.end(), totals.begin());
  return vector(totals);
}

function evenSquares(values) {
  result = vector();
  for (const x of values) {
    if (((x % 2) == 0)) {
      result.push_back((x * x));
    }
  }
  return vector(result);
}

function printNumbers(values, label) {
  console.log(label, ":");
  for (const value of values) {
    console.log(" ", value);
  }
  console.log("\n");
}

function printBooks(books, label) {
  console.log(label, " (", books.size(), ")\n");
  for (const b of books) {
    console.log("  ", b.description(), "\n");
  }
}

function populate(library) {
  library.addBook(new Book(101, "C++ Fundamentals", "Ada", Computing, 4, 4.8));
  library.addBook(new Book(102, "Algorithms", "Knuth", Computing, 3, 4.9));
  library.addBook(new Book(103, "Physics", "Feynman", Science, 5, 4.7));
  library.addBook(new Book(104, "Astronomy", "Carl", Science, 2, 4.3));
  library.addBook(new Book(105, "Ancient Worlds", "Mira", History, 3, 4.1));
  library.addBook(new Book(106, "Modern History", "Lena", History, 2, 4.0));
  library.addBook(new Book(107, "Stories", "Orwell", Fiction, 6, 4.6));
  library.addBook(new Book(108, "Poetry", "Rita", Arts, 3, 4.2));
  library.addBook(new Book(109, "Machine Learning", "Ravi", Computing, 2, 4.5));
  library.addBook(new Book(110, "Painting", "Nora", Arts, 4, 4.4));
  library.addMember(new Member(1, "Alice"));
  library.addMember(new Member(2, "Bob"));
  library.addMember(new Member(3, "Charlie"));
  library.addMember(new Member(4, "Diana"));
  library.addMember(new Member(5, "Ethan"));
}

function runLoans(library) {
  library.borrowBook(1, 101, 5);
  library.borrowBook(1, 102, 18);
  library.borrowBook(2, 103, 21);
  library.borrowBook(3, 107, 7);
  library.borrowBook(4, 109, 15);
  library.borrowBook(5, 108, 3);
  console.log("Borrowed copies: ", library.totalBorrowed(), "\n");
  library.returnBook(3, 107);
  console.log("After return: ", library.totalBorrowed(), "\n");
  try {
    library.borrowBook(99, 101, 1);
  } catch (error) {
    console.log("Expected missing member: ", error.what(), "\n");
  }
  try {
    library.returnBook(3, 107);
  } catch (error) {
    console.log("Expected repeated return: ", error.what(), "\n");
  }
}

function showAnalytics(library) {
  console.log("=== Library analytics ===\n");
  console.log("Books: ", library.bookCount(), "\n");
  console.log("Members: ", library.memberCount(), "\n");
  console.log("Copies: ", library.totalCopies(), "\n");
  console.log("Borrowed: ", library.totalBorrowed(), "\n");
  console.log("Average rating: ", fixed, setprecision(2));
  console.log(library.averageRating(), "\n");
  console.log("Fines due: ", library.outstandingFines(), "\n");
  printBooks(library.topRated(3), "Top rated books");
  printBooks(library.search("History"), "History title search");
  printBooks(library.byCategory(Science), "Science books");
  console.log("=== Member records ===\n");
  library.printMembers();
}

function algorithmDemos() {
  console.log("=== STL algorithm demonstrations ===\n");
  let values = vector([7, 2, 7, 4, 9, 2, 10, 3, 6, 4]);
  printNumbers(values, "Input");
  printNumbers(uniqueSorted(vector(values)), "Unique sorted");
  printNumbers(rollingTotals(values), "Running totals");
  printNumbers(evenSquares(values), "Even squares");
  console.log("Maximum: ", maximumOf(values), "\n");
  console.log("Mean: ", meanOf(values), "\n");
  console.log("Count even: ", count_if(values.begin(), values.end(), null), "\n");
  let copied = vector(values.size(), /*  */);
  transform(values.begin(), values.end(), copied.begin(), null);
  printNumbers(copied, "Tripled");
  reverse(copied.begin(), copied.end());
  printNumbers(copied, "Reversed");
  let histogram = wordHistogram("red blue red green blue red");
  for (const item of histogram) {
    console.log(item.first, "=", item.second, " ");
  }
  console.log("\n");
}

function containerDemos() {
  console.log("=== Additional containers ===\n");
  let doubleEnded = deque([2, 3, 4]);
  doubleEnded.push_front(1);
  doubleEnded.push_back(5);
  console.log("Deque front/back: ", doubleEnded.front());
  console.log("/", doubleEnded.back(), "\n");
  let pending = queue();
  pending.push("request-A");
  pending.push("request-B");
  while (!pending.empty()) {
    console.log("Queue: ", pending.front(), "\n");
    pending.pop();
  }
  let history = stack();
  for (let i = 1; (i <= 3); i++) {
    history.push((i * 10));
  }
  while (!history.empty()) {
    console.log("Stack: ", history.top(), "\n");
    history.pop();
  }
  let ids = set([4, 2, 2, 1, 3]);
  console.log("Unique IDs:");
  for (const id of ids) {
    console.log(" ", id);
  }
  console.log("\n");
}

function pointerAndPolymorphismDemo() {
  console.log("=== Smart pointers and polymorphism ===\n");
  let people = vector();
  people.push_back(unique_ptr(make_unique<Member>(11, "Nina")));
  people.push_back(unique_ptr(make_unique<Librarian>(20, "Oliver", "Morning")));
  people.push_back(unique_ptr(make_unique<Member>(12, "Priya")));
  for (const person of people) {
    person.print();
  }
  let counter = make_shared<int>(5);
  let alias = shared_ptr(counter);
  alias += 3;
  console.log("Shared value: ", counter, "\n");
  console.log("Reference count: ", counter.use_count(), "\n");
}

function exceptionDemo() {
  console.log("=== Exception handling ===\n");
  let data = vector([10, 20, 30]);
  try {
    console.log("Value at index 1: ", data.at(1), "\n");
    console.log(data.at(20), "\n");
  } catch (error) {
    console.log("Caught range exception: ", error.what(), "\n");
  }
  try {
    let empty = vector();
    console.log(maximumOf(empty), "\n");
  } catch (error) {
    console.log("Caught invalid argument: ", error.what(), "\n");
  }
}

function exportReports(library) {
  console.log("=== File output ===\n");
  try {
    library.saveCatalog("library_catalog.csv");
    library.saveEvents("library_events.txt");
    console.log("Saved catalog and event log\n");
  } catch (error) {
    console.log("File error: ", error.what(), "\n");
  }
}

const campus = { categoryName: categoryName, Book: Book, Person: Person, Loan: Loan, Member: Member, Librarian: Librarian, Library: Library, maximumOf: maximumOf, meanOf: meanOf, uniqueSorted: uniqueSorted, wordHistogram: wordHistogram, rollingTotals: rollingTotals, evenSquares: evenSquares, printNumbers: printNumbers, printBooks: printBooks, populate: populate, runLoans: runLoans, showAnalytics: showAnalytics, algorithmDemos: algorithmDemos, containerDemos: containerDemos, pointerAndPolymorphismDemo: pointerAndPolymorphismDemo, exceptionDemo: exceptionDemo, exportReports: exportReports };

function main() {
  console.log("UNIVERSALTRANSPILER C++17 STRESS TEST\n");
  let library = new Library();
  populate(library);
  runLoans(library);
  showAnalytics(library);
  algorithmDemos();
  containerDemos();
  pointerAndPolymorphismDemo();
  exceptionDemo();
  exportReports(library);
  console.log("Completed successfully\n");
  return 0;
}


main();
