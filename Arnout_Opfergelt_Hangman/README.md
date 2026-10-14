# Word Guessing Game

A simple Python word guessing game. The player guesses one letter at a time and can make up to 12 wrong guesses before losing.

## Requirements

- Python 3
- The `wordfreq` library

Install the library with:

```bash
pip install wordfreq
```

## How to Run

Open a terminal in the folder containing `word_guessing_game.py` and run:

```bash
python word_guessing_game.py
```

## How to Play

1. Enter your name.
2. Choose a word list by typing:
   - `selected words`: picks from science, python, rainbow, computer, and programming.
   - `random words`: picks from the 50,000 most common English entries provided by `wordfreq`.
3. Guess one letter at a time.
4. Correct guesses reveal letters in the word.
5. Each wrong guess removes one turn.
6. Reveal every letter to win. If you run out of turns, you lose.

An invalid word-list choice defaults to a random word.

## How the Code Works

### Choosing a Word

The program uses `top_n_list("en", 50_000)` to get a list of English words.
The `random.choice()` function picks a word from the chosen list.

### Tracking Guesses

- `word` stores the word to guess.
- `guesses` stores the letters already guessed.
- `turns` starts at 12 and decreases after each wrong guess.

### The Game Loop

A `while` loop keeps the game running while turns remain.

Inside the loop, a `for` loop checks each letter in the word:
- If the letter has been guessed, it is displayed.
- Otherwise, an underscore (`_`) is displayed.

The `missing` variable counts the letters still hidden. When it reaches zero,
the program prints `You Win!` and ends the loop.

### Checking Input

The program removes surrounding spaces and converts guesses to lowercase.
Only one alphabetic character is accepted at a time.

Invalid input and repeated guesses do not cost a turn.

### Ending the Game

If all letters are revealed, the player wins.
If the number of turns reaches zero, the player loses and the word is displayed.

## Current Behaviour

The code currently prints the answer before the guessing starts:

```python
print(word, " ")
```

Remove this line if you want the answer to stay hidden during the game.