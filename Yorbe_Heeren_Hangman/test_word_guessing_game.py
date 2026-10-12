"""Unit tests for :mod:`word_guessing_game`.

Run with ``python -m unittest discover``.
"""

from __future__ import annotations

import random
import unittest

from word_guessing_game import (
    ConsoleGameRunner,
    DifficultyWordSource,
    FixedWordSource,
    GameState,
    GuessOutcome,
    RandomWordSource,
    WordGuessingGame,
)


def make_game(word: str, max_wrong_guesses: int = 12) -> WordGuessingGame:
    """Build a game with a known secret word."""
    return WordGuessingGame(
        FixedWordSource([word]), max_wrong_guesses=max_wrong_guesses
    )


class ScriptedInput:
    """Replays a fixed list of answers in place of :func:`input`."""

    def __init__(self, answers: list[str]) -> None:
        self._answers = list(answers)
        self.prompts: list[str] = []

    def __call__(self, prompt: str = "") -> str:
        self.prompts.append(prompt)
        if not self._answers:
            raise AssertionError("The runner asked for more input than expected.")
        return self._answers.pop(0)


class WordSourceNormalisationTests(unittest.TestCase):
    def test_words_are_trimmed_and_lowercased(self) -> None:
        source = FixedWordSource(["  Python  "])
        self.assertEqual(source.next_word(), "python")

    def test_empty_word_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            FixedWordSource(["   "])

    def test_non_alphabetic_word_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            FixedWordSource(["hello world"])

    def test_empty_word_list_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            FixedWordSource([])


class FixedWordSourceTests(unittest.TestCase):
    def test_words_are_returned_in_order_then_cycled(self) -> None:
        source = FixedWordSource(["alpha", "beta"])
        self.assertEqual(
            [source.next_word() for _ in range(3)], ["alpha", "beta", "alpha"]
        )


class RandomWordSourceTests(unittest.TestCase):
    def test_selection_is_reproducible_with_a_seeded_generator(self) -> None:
        words = ["alpha", "beta", "gamma", "delta"]
        first = RandomWordSource(words, rng=random.Random(42))
        second = RandomWordSource(words, rng=random.Random(42))
        self.assertEqual(
            [first.next_word() for _ in range(5)],
            [second.next_word() for _ in range(5)],
        )

    def test_selected_word_comes_from_the_candidate_list(self) -> None:
        source = RandomWordSource(["alpha", "beta"])
        self.assertIn(source.next_word(), source.words)


class DifficultyWordSourceTests(unittest.TestCase):
    def test_only_words_within_the_length_range_are_kept(self) -> None:
        source = DifficultyWordSource(
            ["at", "python", "encapsulation"], min_length=3, max_length=8
        )
        self.assertEqual(source.words, ("python",))

    def test_empty_result_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            DifficultyWordSource(["python"], min_length=20)

    def test_invalid_range_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            DifficultyWordSource(["python"], min_length=5, max_length=3)


class MaskedWordTests(unittest.TestCase):
    def test_all_letters_are_hidden_before_any_guess(self) -> None:
        game = make_game("science")
        self.assertEqual(game.masked_word(), "_ _ _ _ _ _ _")

    def test_a_correct_guess_reveals_every_occurrence(self) -> None:
        game = make_game("science")
        game.guess("c")
        self.assertEqual(game.masked_word(), "_ c _ _ _ c _")

    def test_placeholder_and_separator_are_configurable(self) -> None:
        game = make_game("cat")
        self.assertEqual(game.masked_word(placeholder="*", separator=""), "***")


class GuessOutcomeTests(unittest.TestCase):
    def test_correct_guess_does_not_cost_a_turn(self) -> None:
        game = make_game("python", max_wrong_guesses=3)
        self.assertIs(game.guess("p"), GuessOutcome.CORRECT)
        self.assertEqual(game.remaining_turns, 3)

    def test_wrong_guess_costs_one_turn(self) -> None:
        game = make_game("python", max_wrong_guesses=3)
        self.assertIs(game.guess("z"), GuessOutcome.INCORRECT)
        self.assertEqual(game.remaining_turns, 2)

    def test_repeated_guess_is_free(self) -> None:
        game = make_game("python", max_wrong_guesses=3)
        game.guess("z")
        self.assertIs(game.guess("z"), GuessOutcome.ALREADY_GUESSED)
        self.assertEqual(game.remaining_turns, 2)

    def test_multi_character_input_is_invalid(self) -> None:
        game = make_game("python", max_wrong_guesses=3)
        self.assertIs(game.guess("py"), GuessOutcome.INVALID)
        self.assertEqual(game.remaining_turns, 3)

    def test_digit_input_is_invalid(self) -> None:
        game = make_game("python", max_wrong_guesses=3)
        self.assertIs(game.guess("4"), GuessOutcome.INVALID)

    def test_invalid_input_is_not_recorded(self) -> None:
        game = make_game("python")
        game.guess("!")
        self.assertEqual(game.guessed_letters, frozenset())

    def test_guesses_are_case_insensitive_and_trimmed(self) -> None:
        game = make_game("python")
        self.assertIs(game.guess("  P  "), GuessOutcome.CORRECT)

    def test_only_incorrect_outcomes_cost_a_turn(self) -> None:
        costly = {outcome for outcome in GuessOutcome if outcome.costs_turn}
        self.assertEqual(costly, {GuessOutcome.INCORRECT})


class GameStateTests(unittest.TestCase):
    def test_game_starts_in_progress(self) -> None:
        self.assertIs(make_game("cat").state, GameState.IN_PROGRESS)

    def test_guessing_every_letter_wins(self) -> None:
        game = make_game("cat")
        for letter in "cat":
            game.guess(letter)
        self.assertIs(game.state, GameState.WON)
        self.assertTrue(game.is_over)

    def test_running_out_of_turns_loses(self) -> None:
        game = make_game("cat", max_wrong_guesses=2)
        game.guess("x")
        game.guess("y")
        self.assertIs(game.state, GameState.LOST)

    def test_win_is_possible_on_the_last_turn(self) -> None:
        game = make_game("cat", max_wrong_guesses=1)
        game.guess("c")
        game.guess("a")
        game.guess("t")
        self.assertIs(game.state, GameState.WON)

    def test_guessing_after_the_round_is_over_raises(self) -> None:
        game = make_game("cat", max_wrong_guesses=1)
        game.guess("x")
        with self.assertRaises(RuntimeError):
            game.guess("c")


class EncapsulationTests(unittest.TestCase):
    def test_word_cannot_be_revealed_while_the_round_runs(self) -> None:
        with self.assertRaises(RuntimeError):
            make_game("cat").reveal_word()

    def test_word_is_revealed_once_the_round_ends(self) -> None:
        game = make_game("cat", max_wrong_guesses=1)
        game.guess("x")
        self.assertEqual(game.reveal_word(), "cat")

    def test_guessed_letters_cannot_be_mutated_from_outside(self) -> None:
        game = make_game("cat")
        game.guess("c")
        self.assertIsInstance(game.guessed_letters, frozenset)
        self.assertEqual(game.guessed_letters, {"c"})

    def test_wrong_letters_exclude_correct_guesses(self) -> None:
        game = make_game("cat")
        game.guess("c")
        game.guess("z")
        game.guess("b")
        self.assertEqual(game.wrong_letters, ("b", "z"))

    def test_invalid_turn_limit_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            WordGuessingGame(FixedWordSource(["cat"]), max_wrong_guesses=0)


class PolymorphismTests(unittest.TestCase):
    def test_the_game_accepts_any_word_source(self) -> None:
        sources = [
            FixedWordSource(["python"]),
            RandomWordSource(["python"]),
            DifficultyWordSource(["python"], min_length=3),
        ]
        for source in sources:
            with self.subTest(source=type(source).__name__):
                game = WordGuessingGame(source, max_wrong_guesses=1)
                game.guess("x")
                self.assertEqual(game.reveal_word(), "python")


class ConsoleGameRunnerTests(unittest.TestCase):
    def test_a_winning_round_reports_the_word(self) -> None:
        game = make_game("cat")
        output: list[str] = []
        runner = ConsoleGameRunner(
            game,
            player_name="Yorbe",
            input_fn=ScriptedInput(["c", "a", "t"]),
            output_fn=output.append,
        )
        self.assertIs(runner.run(), GameState.WON)
        self.assertIn("You win, Yorbe! The word was 'cat'.", "\n".join(output))

    def test_a_losing_round_reports_the_word(self) -> None:
        game = make_game("cat", max_wrong_guesses=1)
        output: list[str] = []
        runner = ConsoleGameRunner(
            game, input_fn=ScriptedInput(["x"]), output_fn=output.append
        )
        self.assertIs(runner.run(), GameState.LOST)
        self.assertIn("The word was 'cat'.", "\n".join(output))

    def test_invalid_input_is_reported_without_ending_the_round(self) -> None:
        game = make_game("cat")
        output: list[str] = []
        runner = ConsoleGameRunner(
            game, input_fn=ScriptedInput(["12", "c", "a", "t"]), output_fn=output.append
        )
        runner.run()
        joined = "\n".join(output)
        self.assertIn("Please enter exactly one letter.", joined)
        self.assertIn("You win", joined)

    def test_blank_player_name_falls_back_to_default(self) -> None:
        game = make_game("cat", max_wrong_guesses=1)
        output: list[str] = []
        runner = ConsoleGameRunner(
            game,
            player_name="   ",
            input_fn=ScriptedInput(["x"]),
            output_fn=output.append,
        )
        runner.run()
        self.assertIn("Good luck, Player!", "\n".join(output))

    def test_wrong_letters_are_shown_back_to_the_player(self) -> None:
        game = make_game("cat")
        output: list[str] = []
        runner = ConsoleGameRunner(
            game, input_fn=ScriptedInput(["z", "c", "a", "t"]), output_fn=output.append
        )
        runner.run()
        self.assertIn("Wrong letters: z", "\n".join(output))


if __name__ == "__main__":
    unittest.main()
