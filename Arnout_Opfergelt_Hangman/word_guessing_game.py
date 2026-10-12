# Imports
import random
from wordfreq import top_n_list

# Basic Implementation of the word guessing game

# Enter name
name = input("Enter Your Name: ")
print(name)

# Print Good Luck
print("Good Luck!", name)

# Create list of words
words = top_n_list("en", 50_000)

selected_words = ["science", "python", "rainbow", "computer", "programming"]

word = random.choice(words)

selected_words = random.choice(words)

pick_word = input("Pick between selected words or random words: ")

if pick_word.strip().lower() == "selected words":
    selected_words = ["science", "python", "rainbow", "computer", "programming"]
    word = random.choice(selected_words)
elif pick_word.strip().lower() == "random words":
    word = random.choice(words)
else:
    print("Invalid choice. Using a random word.")
    word = random.choice(words)

print(word, " ")

guesses = ""
turns = 12

while turns > 0:
    missing = 0

    # Show guessed letters and hide the rest
    for letter in word:
        if letter in guesses:
            print(letter, end=" ")
        else:
            print("_", end=" ")
            missing += 1

    print()  # Start a new line

    if missing == 0:
        print("You Win!")
        break

    guess = input("Guess a letter: ").lower().strip()

    if len(guess) != 1 or not guess.isalpha():
        print("Please enter one letter.")
        continue

    if guess in guesses:
        print("You already guessed that letter.")
        continue

    guesses += guess

    if guess not in word:
        print("Wrong")
        turns -= 1
        print("Turns left:", turns)

    if turns == 0:
        print("You Lose.")
        print("The word was:", word)