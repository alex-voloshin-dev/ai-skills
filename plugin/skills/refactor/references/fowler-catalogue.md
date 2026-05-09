# Fowler Refactoring Catalogue (Reference)

Curated subset from Martin Fowler, *Refactoring: Improving the Design of Existing Code* (2nd ed., 2018). Use canonical names in `REFACTOR-PLAN.md` so reviewers can map each step to a known mechanic. This is a pointer, not a replacement for the book.

Format per entry: **Trigger** → **Mechanics** (numbered) → **When NOT** → **Example**.

---

## Composing Methods

### Extract Function
- **Trigger:** A code fragment can be grouped together and given a self-explaining name.
- **Mechanics:** (1) Create a new function named after intent. (2) Copy the fragment in. (3) Identify variables used → pass as parameters. (4) Replace the original fragment with a call. (5) Run tests.
- **NOT when:** Fragment is one line and the name adds no clarity over the expression.
- **Example:** `printBanner(); print('Owed: ' + total);` → `printBanner(); printDetails(total);`

### Inline Function
- **Trigger:** A function body is as clear as its name; indirection adds noise.
- **Mechanics:** (1) Verify single dispatch (not polymorphic). (2) Find all callers. (3) Replace each call with the body. (4) Delete the function. (5) Run tests.
- **NOT when:** Function is polymorphic or called from many places where the name carries meaning.
- **Example:** `return moreThanFive(n);` where `moreThanFive(n) { return n > 5; }` → `return n > 5;`

### Extract Variable
- **Trigger:** A complex expression is hard to follow; intermediate names would help.
- **Mechanics:** (1) Ensure the expression has no side effects. (2) Declare an immutable variable. (3) Replace expression with the variable. (4) Run tests.
- **NOT when:** Expression has observable side effects (use Extract Function instead).
- **Example:** `if (order.qty * order.price - max(0, order.qty - 500) * 0.05 > 100)` → extract `basePrice`, `quantityDiscount`.

### Inline Variable
- **Trigger:** A variable name adds no information beyond the expression itself.
- **Mechanics:** (1) Confirm the right-hand side has no side effects. (2) Replace each use with the expression. (3) Remove the declaration. (4) Run tests.
- **Example:** `let basePrice = order.basePrice; return basePrice > 1000;` → `return order.basePrice > 1000;`

### Change Function Declaration
- **Trigger:** Function name or parameter list is misleading or incomplete.
- **Mechanics:** (1) If small scope, just rename + update callers. (2) If wide scope: add new function alongside old, migrate callers, remove old. (3) Run tests after each step.
- **NOT when:** The function is part of a published API without a deprecation policy.
- **Example:** `circum(r)` → `circumference(radius)`.

### Encapsulate Variable
- **Trigger:** A widely-used data field needs a control point (validation, logging, lazy init).
- **Mechanics:** (1) Create getter/setter. (2) Replace direct reads/writes with calls. (3) Make the field private. (4) Run tests.
- **Example:** `defaultOwner.firstName = "Jo"` → `setDefaultOwner({firstName: "Jo", lastName: "..."})`.

### Rename Variable
- **Trigger:** Variable name no longer reflects its role.
- **Mechanics:** Use IDE rename when scope is local. For wider scope, encapsulate first then rename the underlying field.
- **Example:** `tpHd` → `telephoneNumberOfHeadquarters`.

### Introduce Parameter Object
- **Trigger:** Same group of parameters travels together across multiple functions ("data clump").
- **Mechanics:** (1) Create a class/record for the clump. (2) Use Change Function Declaration to add the new parameter. (3) Migrate callers one at a time. (4) Remove old parameters. (5) Run tests.
- **Example:** `amountInRange(low, high)` × 5 callsites → `amountInRange(NumberRange)`.

---

## Moving Features

### Move Function
- **Trigger:** Function references another module's data more than its own.
- **Mechanics:** (1) Examine all program elements used by the function in its current home. (2) Check polymorphism. (3) Copy function to target. (4) Adjust references. (5) Replace original with delegating call or remove. (6) Run tests.
- **NOT when:** Function is part of a stable public interface with external consumers.

### Move Field
- **Trigger:** A field is updated/read mostly by another class.
- **Mechanics:** (1) Encapsulate the field if not already. (2) Add field + accessors to target. (3) Adjust source's accessors to delegate. (4) Migrate callers. (5) Remove the original. (6) Run tests.

### Move Statements into Function
- **Trigger:** The same prep statements appear before every call to a function.
- **Mechanics:** (1) Move the duplicated statements inside the called function. (2) Run tests after each call site updated.
- **Example:** Every caller of `renderPerson()` first calls `result.push(header)` → push header inside `renderPerson()`.

### Slide Statements
- **Trigger:** Related code is scattered; bringing it together aids the next refactor (often a precursor to Extract Function).
- **Mechanics:** (1) Identify slide direction. (2) Verify no data-flow dependency violation. (3) Move statement up or down. (4) Run tests.
- **NOT when:** A side effect or shared variable would change ordering semantics.

---

## Organizing Data

### Encapsulate Field (a.k.a. Self-Encapsulate Field)
- **Trigger:** Public mutable field with growing usage.
- **Mechanics:** (1) Add accessors. (2) Find all direct accesses; replace. (3) Make field private. (4) Run tests.

### Encapsulate Collection
- **Trigger:** A class returns a raw collection that callers mutate directly.
- **Mechanics:** (1) Add `add` / `remove` methods. (2) Make getter return a copy or unmodifiable view. (3) Migrate callers. (4) Run tests.
- **Example:** `course.getCourses().push(c)` → `course.addCourse(c)`.

### Replace Magic Number with Symbolic Constant
- **Trigger:** A literal number or string with implicit meaning is sprinkled through code.
- **Mechanics:** (1) Declare a named constant. (2) Replace each occurrence. (3) Run tests.
- **NOT when:** The literal's meaning is captured by the surrounding name (`for i in range(2)` for a pair).
- **Example:** `9.81` → `STANDARD_GRAVITY`.

### Replace Type Code with Subclasses
- **Trigger:** A type code (string/enum) drives several `if`/`switch` branches that have type-specific behavior.
- **Mechanics:** (1) Encapsulate the type field. (2) Create a subclass per code value. (3) Replace constructor with factory. (4) Move type-specific behavior into subclasses. (5) Run tests after each move.
- **NOT when:** The type can change at runtime → use Replace Type Code with Strategy instead.

### Replace Type Code with Strategy
- **Trigger:** Like above, but the type can change for a given object during its lifetime.
- **Mechanics:** Inject a strategy object instead of subclassing; swap strategy on type change.

---

## Simplifying Conditional Logic

### Decompose Conditional
- **Trigger:** A complex `if/then/else` makes the predicate and branches hard to read.
- **Mechanics:** (1) Extract the predicate to a named function. (2) Extract each branch body to a named function. (3) Run tests.
- **Example:** `if (date < SUMMER_START || date > SUMMER_END) charge = qty * winterRate + winterServiceCharge; else charge = qty * summerRate;` → `charge = isSummer(date) ? summerCharge(qty) : winterCharge(qty);`

### Consolidate Conditional Expression
- **Trigger:** Multiple sequential `if`s with the same body.
- **Mechanics:** (1) Combine predicates into one boolean expression. (2) Extract the combined predicate to a function. (3) Run tests.

### Replace Nested Conditional with Guard Clauses
- **Trigger:** Deeply nested `if/else` obscures the normal path.
- **Mechanics:** (1) Identify exceptional cases. (2) Convert each to a guarded early return. (3) Leave the main flow at the bottom. (4) Run tests.
- **NOT when:** All branches are equally important (then keep the if/else symmetric).

### Replace Conditional with Polymorphism
- **Trigger:** A conditional selects behavior by type or kind, repeatedly.
- **Mechanics:** (1) Create class hierarchy. (2) Use Replace Type Code with Subclasses. (3) Push each conditional branch into the matching subclass method. (4) Make the base method abstract. (5) Run tests.
- **NOT when:** Only a single conditional uses the type (overhead exceeds benefit).

### Introduce Special Case (Null Object pattern)
- **Trigger:** Same null-check repeated across callers.
- **Mechanics:** (1) Create a special-case object that responds to the same methods with safe defaults. (2) Return it instead of null. (3) Remove null checks. (4) Run tests.
- **Example:** `customer ?? UnknownCustomer.instance`.

### Introduce Assertion
- **Trigger:** Code silently relies on an invariant that, if violated, would cause subtle failures.
- **Mechanics:** (1) Add an assertion at the section start. (2) Run tests. (3) Keep only assertions for genuine invariants — not user input checks.

---

## Refactoring APIs

### Separate Query from Modifier
- **Trigger:** A function returns a value AND has observable side effects.
- **Mechanics:** (1) Copy function, rename to a pure query. (2) Remove side effects from the query. (3) Update callers that used the return value to call the query, then the modifier. (4) Run tests.
- **NOT when:** Side effect and return are atomically tied (e.g., `pop()` on a stack — leave alone).

### Parameterize Function
- **Trigger:** Two functions differ only by literal values.
- **Mechanics:** (1) Pick one function. (2) Add a parameter for the literal. (3) Migrate callers. (4) Remove the duplicate. (5) Run tests.

### Remove Flag Argument
- **Trigger:** A boolean flag selects between two behaviors inside a function.
- **Mechanics:** (1) Create a function per flag value. (2) Migrate callers. (3) Remove the flag function. (4) Run tests.
- **Example:** `book(customer, false)` / `book(customer, true)` → `regularBook(customer)` / `premiumBook(customer)`.

### Preserve Whole Object
- **Trigger:** Caller passes several values from the same object.
- **Mechanics:** (1) Change function to accept the whole object. (2) Update body to access fields. (3) Migrate callers. (4) Run tests.
- **NOT when:** It would create an unwanted dependency on the larger object.

### Replace Parameter with Query
- **Trigger:** Caller passes a value that the function could compute itself.
- **Mechanics:** (1) Move the lookup inside the function. (2) Remove the parameter. (3) Update callers. (4) Run tests.
- **NOT when:** The query has side effects or breaks function purity.

---

## Dealing with Inheritance

### Pull Up Method
- **Trigger:** Two subclasses have an identical method.
- **Mechanics:** (1) Inspect for tiny differences. (2) Move to superclass. (3) Run tests.

### Push Down Method
- **Trigger:** A superclass method is used by only one subclass.
- **Mechanics:** (1) Move the method to the using subclass. (2) Remove from superclass. (3) Run tests.

### Replace Inheritance with Delegation
- **Trigger:** Subclass uses only part of the superclass's interface, or inheritance creates a fragile coupling.
- **Mechanics:** (1) Add a field for the delegated object. (2) Forward needed methods. (3) Remove `extends`. (4) Run tests.
- **NOT when:** Subclass genuinely "is-a" the superclass and uses most of it.

---

## Automated Tooling — Use AST-Correct Tools by Default

Hand edits drift; AST refactoring tools preserve semantics. Pick the right one for the language:

| Language | Tool |
|---|---|
| JS / TS | **jscodeshift** (codemods), ts-morph; VSCode/IntelliJ rename + extract |
| Python | **bowler**, **libcst** (Instagram), **rope**; PyCharm refactoring menu |
| Java / Kotlin | **OpenRewrite** (recipe-driven), IntelliJ |
| C# | Roslyn analyzers; Rider / Visual Studio |
| Go | `gopls` rename, `gofmt -r` for pattern rewrites |
| Ruby | RuboCop autocorrect; RubyMine |
| Rust | rust-analyzer rename + extract |

**Default rule:** if the target language has an AST refactoring tool, use it. Resort to line-edits only when no AST tool exists for the construct, and document the deviation in `REFACTOR-LOG.md`.
