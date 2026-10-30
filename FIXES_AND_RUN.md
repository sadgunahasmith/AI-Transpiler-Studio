# Transpiler fixes in this revision

## Changes
- Disabled identifier-to-literal constant propagation in the AST optimizer. Literal-only arithmetic such as `2 + 3` can still be folded internally, but `a + b` remains a variable expression in generated source.
- After a successful transpilation, the frontend automatically executes source and generated code with the same standard input and shows both outputs plus the equivalence result in **Output & Verification**.
- Updated the frontend global theme with a more polished dark IDE appearance, improved contrast, typography, focus states, responsive spacing, and editor surfaces.

## Run
1. Start the backend using the project's existing README instructions.
2. In `frontend/`, run `npm install` and `npm run dev`.
3. Keep required language runtimes installed. Output comparison is only meaningful when both programs execute successfully. If the sandbox blocks execution or a runtime is missing, the UI displays that status instead of claiming equivalence.

## Important limitation
Transpilation is not a proof of semantic equivalence for every possible program. The comparison feature checks observed standard output for the provided input; it does not prove equivalence for all inputs. Header names, grammar and type rules are language-specific, so unsupported constructs should be reported rather than silently guessed.
