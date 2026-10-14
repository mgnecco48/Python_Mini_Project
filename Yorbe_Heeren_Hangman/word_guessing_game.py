# Word Guessing Game - Mandatory Mini Project 1

import random
from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from enum import Enum, auto

DEFAULT_WORDS: tuple[str, ...] = (
    "kristiania",
    "computer",
    "science",
    "programming",
    "python",
    "inheritance",
    "polymorphism",
    "encapsulation",
)

DEFAULT_MAX_WRONG_GUESSES = 12

# ---------------------------------------------------------------------------
# Word sources (inheritance and polymorphism)
# ---------------------------------------------------------------------------

class WordSource(ABC):

    @abstractmethod
    def next_word(self) -> str:

    @staticmethod
    def normalise(word: str) -> str:
        cleaned = word.strip().lower()
        if not cleaned:
            raise ValueError("Words must not be empty.")
        if not cleaned.isalpha():
            raise ValueError(f"Words must contain letters only, got {word!r}.")
        return cleaned

    @classmethod
    def _normalise_all(cls, words: Iterable[str]) -> list[str]:
        normalised = [cls.normalise(word) for word in words]
        if not normalised:
            raise ValueError("At least one word is required.")
        return normalised

class FixedWordSource(WordSource):

    def __init__(self, words: Iterable[str]) -> None:
        self._words = self._normalise_all(words)
        self._index = 0

    def next_word(self) -> str:
        word = self._words[self._index % len(self._words)]
        self._index += 1
        return word

class RandomWordSource(WordSource):

    def __init__(self, words: Iterable[str], rng: random.Random | None = None) -> None:
        self._words = self._normalise_all(words)
        self._rng = rng if rng is not None else random.Random()

    @property
    def words(self) -> tuple[str, ...]:
        return tuple(self._words)

    def next_word(self) -> str:
        return self._rng.choice(self._words)

class DifficultyWordSource(RandomWordSource):

    def __init__(
        self,
        words: Iterable[str],
        min_length: int = 1,
        max_length: int | None = None,
        rng: random.Random | None = None,
    ) -> None:
        if min_length < 1:
            raise ValueError("min_length must be at least 1.")
        if max_length is not None and max_length < min_length:
            raise ValueError("max_length must not be smaller than min_length.")

        upper_bound = max_length if max_length is not None else float("inf")
        candidates = [
            word
            for word in self._normalise_all(words)
            if min_length <= len(word) <= upper_bound
        ]
        if not candidates:
            raise ValueError(
                f"No words between {min_length} and {max_length} letters long."
            )
        super().__init__(candidates, rng=rng)

# ---------------------------------------------------------------------------
# Value types
# ---------------------------------------------------------------------------

class GuessOutcome(Enum):

    CORRECT = auto()
    INCORRECT = auto()
    ALREADY_GUESSED = auto()
    INVALID = auto()

    @property
    def costs_turn(self) -> bool:
        return self is GuessOutcome.INCORRECT

class GameState(Enum):

    IN_PROGRESS = auto()
    WON = auto()
    LOST = auto()

# ---------------------------------------------------------------------------
# Game rules (encapsulation)
# ---------------------------------------------------------------------------

class WordGuessingGame:

    def __init__(
        self,
        word_source: WordSource,
        max_wrong_guesses: int = DEFAULT_MAX_WRONG_GUESSES,
    ) -> None:
        if max_wrong_guesses < 1:
            raise ValueError("max_wrong_guesses must be at least 1.")
        self._secret_word = word_source.next_word()
        self._max_wrong_guesses = max_wrong_guesses
        self._wrong_guesses = 0
        self._guessed_letters: set[str] = set()

    @property
    def word_length(self) -> int:
        return len(self._secret_word)

    @property
    def remaining_turns(self) -> int:
        return self._max_wrong_guesses - self._wrong_guesses

    @property
    def guessed_letters(self) -> frozenset[str]:
        return frozenset(self._guessed_letters)

    @property
    def wrong_letters(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                letter
                for letter in self._guessed_letters
                if letter not in self._secret_word
            )
        )

    @property
    def state(self) -> GameState:
        if self._is_word_complete():
            return GameState.WON
        if self.remaining_turns <= 0:
            return GameState.LOST
        return GameState.IN_PROGRESS

    @property
    def is_over(self) -> bool:
        return self.state is not GameState.IN_PROGRESS

    def masked_word(self, placeholder: str = "_", separator: str = " ") -> str:
        return separator.join(
            letter if letter in self._guessed_letters else placeholder
            for letter in self._secret_word
        )

    def guess(self, letter: str) -> GuessOutcome:
        if self.is_over:
            raise RuntimeError("The round is already over; start a new game.")

        candidate = letter.strip().lower()
        if len(candidate) != 1 or not candidate.isalpha():
            return GuessOutcome.INVALID
        if candidate in self._guessed_letters:
            return GuessOutcome.ALREADY_GUESSED

        self._guessed_letters.add(candidate)
        if candidate in self._secret_word:
            return GuessOutcome.CORRECT

        self._wrong_guesses += 1
        return GuessOutcome.INCORRECT

    def reveal_word(self) -> str:
        if not self.is_over:
            raise RuntimeError("The word can only be revealed once the round is over.")
        return self._secret_word

    def _is_word_complete(self) -> bool:
        return all(letter in self._guessed_letters for letter in self._secret_word)

# ---------------------------------------------------------------------------
# Presentation layer
# ---------------------------------------------------------------------------

class ConsoleGameRunner:

    _MESSAGES: dict[GuessOutcome, str] = {
        GuessOutcome.CORRECT: "Correct!",
        GuessOutcome.INCORRECT: "Wrong!",
        GuessOutcome.ALREADY_GUESSED: "You already guessed that letter.",
        GuessOutcome.INVALID: "Please enter exactly one letter.",
    }

    def __init__(
        self,
        game: WordGuessingGame,
        player_name: str = "Player",
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self._game = game
        self._player_name = player_name.strip() or "Player"
        self._input_fn = input_fn
        self._output_fn = output_fn

    def run(self) -> GameState:
        self._announce_start()
        while not self._game.is_over:
            self._show_status()
            guess = self._input_fn("Guess a letter: ")
            outcome = self._game.guess(guess)
            self._output_fn(self._MESSAGES[outcome])
        self._announce_result()
        return self._game.state

    def _announce_start(self) -> None:
        self._output_fn(f"\nGood luck, {self._player_name}!")
        self._output_fn(
            f"The word has {self._game.word_length} letters. "
            "Guess it one letter at a time."
        )

    def _show_status(self) -> None:
        self._output_fn(f"\nWord: {self._game.masked_word()}")
        self._output_fn(f"Turns remaining: {self._game.remaining_turns}")
        wrong_letters = self._game.wrong_letters
        if wrong_letters:
            self._output_fn(f"Wrong letters: {', '.join(wrong_letters)}")

    def _announce_result(self) -> None:
        word = self._game.reveal_word()
        if self._game.state is GameState.WON:
            self._output_fn(f"\nYou win, {self._player_name}! The word was '{word}'.")
        else:
            self._output_fn(f"\nYou lose, {self._player_name}. The word was '{word}'.")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        name = input("Enter your name: ")
    except (EOFError, KeyboardInterrupt):
        print("\nNo input received; exiting.")
        return

    game = WordGuessingGame(RandomWordSource(DEFAULT_WORDS))
    runner = ConsoleGameRunner(game, player_name=name)

    try:
        runner.run()
    except (EOFError, KeyboardInterrupt):
        print("\nGame interrupted. Goodbye.")

if __name__ == "__main__":
    main()