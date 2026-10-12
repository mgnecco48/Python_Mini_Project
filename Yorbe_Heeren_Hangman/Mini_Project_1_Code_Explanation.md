# Mini Project 1: Code Explanation

**PGR211 Advanced Programming for Data Science**
Word Guessing Game — mandatory coursework requirement, Week 38

---

## 1. Overview

The program plays one round of a word guessing game. A secret word is selected
from a list, the player guesses one letter at a time, and correct letters are
revealed in their correct positions. A wrong letter costs one of the twelve
turns. The round ends when every letter has been guessed or the turns run out.

The implementation is object-oriented because the assignment sits under Learning
Outcome 1, which covers classes, objects, methods, inheritance, polymorphism and
encapsulation. Section 6 maps each of those concepts to the code that
demonstrates it.

## 2. Structure

The program is divided into three layers, each with one responsibility:

| Layer | Types | Responsibility |
| --- | --- | --- |
| Word selection | `WordSource`, `FixedWordSource`, `RandomWordSource`, `DifficultyWordSource` | Decide which word is played |
| Game rules | `WordGuessingGame`, `GuessOutcome`, `GameState` | Hold the state and enforce the rules |
| Presentation | `ConsoleGameRunner`, `main` | Read from and write to the console |

The separation is what makes the game testable. `WordGuessingGame` never calls
`input()` or `print()`, so its rules can be exercised directly, and
`ConsoleGameRunner` receives its input and output functions as arguments, so a
full round can be played with scripted keystrokes in a test.

## 3. Word selection

### `WordSource`

An abstract base class, declared with `ABC` and one `@abstractmethod`,
`next_word()`. It cannot be instantiated directly; it defines the contract every
source must satisfy.

The class also provides `normalise()`, which trims a word, lowercases it, and
raises `ValueError` if the result is empty or contains anything other than
letters. Putting validation in the base class means no subclass repeats it, and
a malformed word list fails immediately with a clear message rather than
producing a confusing game later.

### `FixedWordSource`

Returns words from a list in order, cycling back to the start when the list is
exhausted. Because it is completely predictable it is used throughout the tests
and in the notebook demonstration, where a known secret word is required.

### `RandomWordSource`

Selects a word uniformly at random. The random generator is a constructor
argument defaulting to a fresh `random.Random`. Injecting a seeded generator
instead makes the selection reproducible, which is what allows the demonstration
cell in the notebook to produce identical output on every run.

### `DifficultyWordSource`

Inherits from `RandomWordSource` rather than from `WordSource` directly. It
filters the candidate words by length — shorter words are easier to guess — then
calls `super().__init__()` with the filtered list, reusing the random selection
it already inherits. It raises `ValueError` if the filter leaves nothing to
choose from, rather than failing later with an obscure error from
`random.choice`.

## 4. Game rules

### `GuessOutcome` and `GameState`

Two enumerations replace the loose strings and flags a procedural version would
use. `GuessOutcome` has four members: `CORRECT`, `INCORRECT`, `ALREADY_GUESSED`
and `INVALID`. `GameState` has three: `IN_PROGRESS`, `WON` and `LOST`.

`GuessOutcome` also exposes a `costs_turn` property. Keeping the scoring rule on
the outcome, rather than spreading `if` statements through the game loop, means
there is exactly one place to change if the rules change.

### `WordGuessingGame`

The class owns three pieces of mutable state, all private: the secret word, the
set of guessed letters, and the count of wrong guesses. Nothing outside the
class can modify them.

Reads go through read-only properties:

- `word_length` — how many letters the word has.
- `remaining_turns` — wrong guesses still available.
- `guessed_letters` — returned as a `frozenset`, so a caller cannot add to the
  internal set by accident.
- `wrong_letters` — guessed letters not in the word, sorted, for display.
- `state` — computed on demand from the current state rather than stored, so it
  can never fall out of sync.
- `is_over` — true once the round is won or lost.

Two methods produce output without changing anything:

- `masked_word()` builds the display string by walking the secret word and
  emitting each letter if it has been guessed, or a placeholder if it has not.
  For the word `science` with everything but `n` guessed, it returns
  `s c i e _ c e`.
- `reveal_word()` returns the secret word, but raises `RuntimeError` if the
  round is still running. The interface layer therefore cannot leak the answer
  mid-game, even by mistake.

`guess()` is the only method that changes state. It:

1. Raises `RuntimeError` if the round is already over.
2. Trims and lowercases the input, so `" P "` and `p` are the same guess.
3. Returns `INVALID` if the result is not exactly one alphabetic character. The
   letter is not recorded and no turn is lost.
4. Returns `ALREADY_GUESSED` if the letter has been guessed before. Again, no
   turn is lost — the player gains nothing from a repeat, but is not punished
   for it either.
5. Records the letter, then returns `CORRECT` if it is in the word, or
   decrements the turn counter and returns `INCORRECT` if it is not.

A correct guess reveals every occurrence of that letter at once, because
`masked_word()` checks membership of the guessed set for each position
independently.

## 5. Presentation

### `ConsoleGameRunner`

The only class that interacts with the user. Its constructor takes the game, the
player name, and two functions: `input_fn` and `output_fn`, defaulting to the
built-in `input` and `print`.

`run()` drives the round: announce the start, then loop while the game is not
over — show the masked word, remaining turns and any wrong letters, read a
guess, pass it to the game, and print the message for the outcome returned. When
the loop ends it calls `reveal_word()` and announces the result. The final
`GameState` is returned so a caller can act on it.

Outcome messages live in a class-level dictionary keyed by `GuessOutcome`, so
adding an outcome is a compile-time-visible change rather than a missed branch.

### `main()`

Prompts for a name, falling back to `Player` if the input is blank, builds a
game with a `RandomWordSource` over the default word list, and runs it.
`EOFError` and `KeyboardInterrupt` are caught so that closing the input stream
or pressing Ctrl-C produces a short message instead of a traceback.

## 6. Learning Outcome 1 coverage

| Concept | Demonstration |
| --- | --- |
| Class and object | `WordGuessingGame`, `ConsoleGameRunner` and the four word source classes; each round is a separate object with its own state |
| Method | `guess()`, `masked_word()`, `reveal_word()`, `run()`, `next_word()` |
| Inheritance | `FixedWordSource` and `RandomWordSource` derive from `WordSource`; `DifficultyWordSource` derives from `RandomWordSource` and extends its constructor with `super()` |
| Polymorphism | `WordGuessingGame` depends only on the `WordSource` abstraction and calls `next_word()` without knowing which concrete class it holds |
| Encapsulation | Private state, read-only properties returning immutable copies, a single mutating method, and `reveal_word()` refusing to disclose the answer while the round is live |
| Abstraction | `WordSource` is an abstract base class with an abstract method and shared concrete validation |

## 7. Edge cases handled

- Empty word lists, blank words, and words containing spaces, digits or
  punctuation are rejected when a source is constructed.
- A turn limit below one is rejected.
- Multi-character input, digits and punctuation are reported as invalid and cost
  nothing.
- Repeated guesses are reported and cost nothing.
- Guesses are case-insensitive and surrounding whitespace is ignored.
- A win is still possible on the final turn: the state is recomputed after every
  guess, and the win condition is checked before the loss condition.
- Guessing after the round has ended raises rather than silently doing nothing.
- A blank player name falls back to a default.

## 8. Testing

The suite contains 37 tests using only `unittest` from the standard library. 
It covers word validation, all three concrete sources, masking, every guess
outcome, the win and lose transitions, the encapsulation guarantees, and the
console loop itself via a scripted input helper.

Run the tests from the project directory:

```
python -m unittest discover -v
```

Or run the last cell of the notebook, which executes the same suite in place.

## 9. Running the game

As a script:

```
python word_guessing_game.py
```

In the notebook: set `PLAY_INTERACTIVELY = True` in the entry point cell and run it.
