# Mini Project 1: Code Explanation

**PGR211 Advanced Programming for Data Science**
Word Guessing Game — mandatory coursework requirement

---

## 1. Overview

The program plays one round of a word guessing game. A secret word is selected
from a list, the player guesses one letter at a time, and correct letters are
revealed in their correct positions. A wrong letter costs one of the twelve
turns. The round ends when every letter has been guessed or the turns run out.

The implementation is object-oriented because the assignment sits under the Learning
Outcomes, which covers classes, objects, methods, inheritance, polymorphism and
encapsulation. 

## 2. Structure

| Layer | Types | Responsibility |
| --- | --- | --- |
| Word selection | `WordSource`, `FixedWordSource`, `RandomWordSource`, `DifficultyWordSource` | Decide which word is played |
| Game rules | `WordGuessingGame`, `GuessOutcome`, `GameState` | Hold the state and enforce the rules |
| Presentation | `ConsoleGameRunner`, `main` | Read from and write to the console |

## 3. Learning Outcome coverage

| Concept | Demonstration |
| --- | --- |
| Class and object | `WordGuessingGame`, `ConsoleGameRunner` and the four word source classes; each round is a separate object with its own state |
| Method | `guess()`, `masked_word()`, `reveal_word()`, `run()`, `next_word()` |
| Inheritance | `FixedWordSource` and `RandomWordSource` derive from `WordSource`; `DifficultyWordSource` derives from `RandomWordSource` and extends its constructor with `super()` |
| Polymorphism | `WordGuessingGame` depends only on the `WordSource` abstraction and calls `next_word()` without knowing which concrete class it holds |
| Encapsulation | Private state, read-only properties returning immutable copies, a single mutating method, and `reveal_word()` refusing to disclose the answer while the round is live |
| Abstraction | `WordSource` is an abstract base class with an abstract method and shared concrete validation |

## 4. Edge cases handled

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

## 5. AI-useage transparency

- AI was used to structure and organize my code, to provide comments, and to 
  explain how the game covers the learning outcomes.
- I retain the ownership of the code as the written author, AI was not used to 
  write the code outright, but used to present the code in a professional manner, 
  and handle cases where I got stuck or wanted to improve upon my work. 

## 6. Running the game

As a script:

```
python word_guessing_game.py
```

In the notebook: set `PLAY_INTERACTIVELY = True` in the entry point cell and run it.
