# Tic Tac Toe:

This is a very simple simulator for a tic tac toe game. Two players take turns and choose a random empty place on the board.

Whenever a player gets three contiguos marks, they get a point. In the case of no one being able to get a whole line before the board runs out of empty places, there is a tie and nobody gets a point.

To win a whole game, a player must reach a certain number of points. As soon as a player gets to the points goal, the game stops.

There is also a maximum number of rounds to be played. If none of the players get enough points to win before the rounds limit is reached, the game stops and the player with the most points wind the game. There could also be a tied game.

---

## Download and run locally

This project uses `uv` to manage the Python environment and dependencies. After cloning or downloading the repository, install the dependencies with:

```bash
uv sync
```

Then run the game with:

```bash
uv run python main.py
```

In order to see the game in action without downloading and running the script, it is served via `SSH` and can be accessed from a terminal by running:

```bash
ssh -p 23234 terminal.martingneccoh.io
```

When trying it for the first time, SSH may warn that the host is not in the `known_hosts` file. By typing `yes`, the server's host key is added to your machine, so future connections are smoother. You do not need to copy your own public key to the host or specify a particular username.

---

## Libraries used

- [Numpy](https://numpy.org/) was used to model the board as a two dimensional array. This comes with some convenient methods for checking for a winner efficiently.
- [Rich](https://github.com/textualize/rich) is a powerful library to generate nicer terminal outputs, and comes in with simple functions to clear the screen, align text and print tables, among many others.
- [Wish](https://github.com/charmbracelet/wish) is a `Go` library that makes it very easy to serve applications via ssh. For this project, it listens on a specific port in a VPS that I own, and when there is a connection, it immediately launches the python game and terminates the connection once the program exits, without giving access to a shell in the server. It removes the need to authenticate as an existing user and handles the public key authentication securely.

---

## Code design

The code for the game follows an Object Oriented Programming approach. This allows for an easy way to model the individual _objects_ that I was trying to represent (a `player`, the `board` and the `game` itself) and defines clear responsibilities for each one of them.

Using this approach helped specially at the moment of defining the behaviour of each entity, as it is easier to define it for each individual _object_, which in turns allows for a clear way to model the relationships between them.

In the end, the integration of all of the elements turned out to be very simple once each individual _object's_ state and behaviour was developed and tested in isolation.

The classes and their attributes and methods are listed here:

- `Player`: represents one player in the game.
  - **Attributes**
    - `symbol`: holds the player's mark that will go on the board.
    - `points`: holds the player's score.
    - `name`: holds the player's display name.
  - **Methods**
    - `play_turn()`: chooses a random empty square from an empty space.
    - `add_point()`: adds one point to the player.
- `Board`: represents the tic tac toe board.
  - **Attributes**
    - `size`: holds the board size.
    - `squares`: holds the current board marks.
    - `empty`: holds the available empty squares.
  - **Methods**
    - `show_possibilities()`: finds the empty squares.
    - `check_row()`: checks for a winning row.
    - `check_col()`: checks for a winning column.
    - `check_diag()`: checks for a winning diagonal.
    - `check_winner()`: checks if a player won. It calls the three previous
      functions and gives a simpler interface when implementing the game.
    - `reset()`: clears the board for a new round.
    - `__str__()`: formats the board for display.
- `Game`: controls the whole game flow.
  - **Attributes**
    - `board`: holds the game board.
    - `players`: holds both players.
    - `console`: is used to interact with Rich.
    - `max_points`: sets the points needed to win.
    - `max_rounds`: sets the round limit.
    - `rounds_played`: is used to determine whether the game must stop.
  - **Methods**
    - `enter_full_screen()`: helper used to switch to full screen mode, by printing the correct ANSI escape code.
    - `leave_full_screen()`: helper used to exit full screen mode, by printing the correct ANSI escape code.
    - `printc()`: helper used to print centered text with Rich.
    - `play_round()`: plays one round of the game.
    - `check_player_points()`: gets the highest player score.
    - `leaderboard()`: creates a Rich table for the scores.
    - `game_over_reason()`: explains why the game stopped.
    - `get_winner()`: determines which player won.
    - `winner_message()`: creates the final winner message.
    - `play_game()`: runs the full game and interacts with Rich.

---

## Running the SSH server

The SSH server is optional and is only needed if you want to serve the game through SSH yourself. The server code is inside `ssh_server/` and uses `Wish` to start the Python game when a client connects.

To avoid publishing local machine paths, the server reads its configuration from a local `.env` file. That file should not be committed, because it contains machine-specific paths such as the Python interpreter, the game file, and the project folder.

Create a `.env` file inside `ssh_server/` and use this as a starting point:

```env
PYTHON_PATH=/absolute/path/to/.venv/bin/python
GAME_PATH=/absolute/path/to/main.py
PROJECT_PATH=/absolute/path/to/tic_tac_toe
HOST=0.0.0.0
PORT=23234
```

Update the values so they match your own machine before starting the server.

The server expects a host key in the same directory; this key identifies the server and should not be committed to the repository. Note that `Wish` can automatically manage the creation of a new host key if there is not one, so you can skip creating it manually.

To start the server locally, run:

```bash
cd ssh_server
go run .
```

With the example values above, the server listens on port `23234`, so it can be tested with:

```bash
ssh -p 23234 localhost
```

You can change the port, host, paths, and host key location by editing your local `.env` file.

---
