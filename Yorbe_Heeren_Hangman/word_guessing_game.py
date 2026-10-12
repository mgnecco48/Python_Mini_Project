"""Word guessing game built with object-oriented Python.

The module is split into three layers so that the game rules can be tested
without touching the console:

* ``WordSource`` and its subclasses decide *which* word is played.
* ``WordGuessingGame`` owns the rules and the mutable game state.
* ``ConsoleGameRunner`` handles all input and output.

Run ``python word_guessing_game.py`` to play.
"""

from __future__ import annotations

import random
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
    """Supplies secret words to a :class:`WordGuessingGame`.

    Subclasses decide the selection strategy. The game only depends on this
    abstract type, so any source can be substituted without changing the rules.
    """

    @abstractmethod
    def next_word(self) -> str:
        """Return the next secret word in normalised (lowercase) form."""

    @staticmethod
    def normalise(word: str) -> str:
        """Trim and lowercase a word, rejecting anything that is not alphabetic.

        Raises:
            ValueError: If the word is empty or contains non-letter characters.
        """
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
    """Cycles through a fixed sequence of words.

    Deterministic by design, which makes it the source of choice for tests and
    for reproducible demonstrations.
    """

    def __init__(self, words: Iterable[str]) -> None:
        self._words = self._normalise_all(words)
        self._index = 0

    def next_word(self) -> str:
        word = self._words[self._index % len(self._words)]
        self._index += 1
        return word


class RandomWordSource(WordSource):
    """Picks a word uniformly at random.

    Args:
        words: Candidate words.
        rng: Optional random generator. Injecting a seeded ``random.Random``
            makes the selection reproducible in tests.
    """

    def __init__(self, words: Iterable[str], rng: random.Random | None = None) -> None:
        self._words = self._normalise_all(words)
        self._rng = rng if rng is not None else random.Random()

    @property
    def words(self) -> tuple[str, ...]:
        """The candidate words, exposed read-only."""
        return tuple(self._words)

    def next_word(self) -> str:
        return self._rng.choice(self._words)


class DifficultyWordSource(RandomWordSource):
    """A random source restricted to words of a given length range.

    Shorter words are easier to guess, so word length is used here as a simple
    proxy for difficulty.
    """

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
    """The result of a single guess."""

    CORRECT = auto()
    INCORRECT = auto()
    ALREADY_GUESSED = auto()
    INVALID = auto()

    @property
    def costs_turn(self) -> bool:
        """Whether this outcome consumes one of the player's turns."""
        return self is GuessOutcome.INCORRECT


class GameState(Enum):
    """Where the game currently stands."""

    IN_PROGRESS = auto()
    WON = auto()
    LOST = auto()


# ---------------------------------------------------------------------------
# Game rules (encapsulation)
# ---------------------------------------------------------------------------


class WordGuessingGame:
    """The rules and state of one round of the game.

    The secret word, the guessed letters and the turn counter are private. All
    reads go through read-only properties, and the only way to change state is
    :meth:`guess`, so the game can never be driven into an inconsistent state
    from the outside.

    Args:
        word_source: Supplies the secret word for this round.
        max_wrong_guesses: How many wrong guesses the player may make.
    """

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
        """Number of letters in the secret word."""
        return len(self._secret_word)

    @property
    def remaining_turns(self) -> int:
        """Wrong guesses still available before the round is lost."""
        return self._max_wrong_guesses - self._wrong_guesses

    @property
    def guessed_letters(self) -> frozenset[str]:
        """Every letter guessed so far, as an immutable set."""
        return frozenset(self._guessed_letters)

    @property
    def wrong_letters(self) -> tuple[str, ...]:
        """Guessed letters that are not in the secret word, alphabetically."""
        return tuple(
            sorted(
                letter
                for letter in self._guessed_letters
                if letter not in self._secret_word
            )
        )

    @property
    def state(self) -> GameState:
        """Whether the round is won, lost or still running."""
        if self._is_word_complete():
            return GameState.WON
        if self.remaining_turns <= 0:
            return GameState.LOST
        return GameState.IN_PROGRESS

    @property
    def is_over(self) -> bool:
        """True once the round has been won or lost."""
        return self.state is not GameState.IN_PROGRESS

    def masked_word(self, placeholder: str = "_", separator: str = " ") -> str:
        """Render the secret word with unguessed letters hidden.

        Example:
            ``"s c i e _ c e"`` once every letter but ``n`` has been guessed.
        """
        return separator.join(
            letter if letter in self._guessed_letters else placeholder
            for letter in self._secret_word
        )

    def guess(self, letter: str) -> GuessOutcome:
        """Register a guess and report the outcome.

        Only a single alphabetic character counts as a guess. Invalid and
        repeated guesses are reported back but cost the player nothing.

        Raises:
            RuntimeError: If the round is already over.
        """
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
        """Return the secret word, but only after the round has finished.

        Raises:
            RuntimeError: If the round is still in progress.
        """
        if not self.is_over:
            raise RuntimeError("The word can only be revealed once the round is over.")
        return self._secret_word

    def _is_word_complete(self) -> bool:
        return all(letter in self._guessed_letters for letter in self._secret_word)


# ---------------------------------------------------------------------------
# Presentation layer
# ---------------------------------------------------------------------------


class ConsoleGameRunner:
    """Plays a :class:`WordGuessingGame` through a text interface.

    Input and output are injected rather than hard-coded, so the whole loop can
    be exercised in a unit test with scripted keystrokes.

    Args:
        game: The round to play.
        player_name: Name used in the prompts.
        input_fn: Called with a prompt, returns the player's raw input.
        output_fn: Called with each line of output.
    """

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
        """Play the round to completion and return the final state."""
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
    """Prompt for a name and play one round with a random word."""
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
