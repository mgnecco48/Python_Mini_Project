# Project Submission

This repository contains our submission for the mandatory assignment. There are three folders containing three different games, two exploring different approaches for the Hangman game, and one implementation of Tic-Tac-Toe.

Each directory contains its own README, with a more detailed description of the code and the design. There are also instructions to run the scripts locally or to play the games remotely via SSH.

## File structure

```text
Python_Mini_Project/
├── .gitignore
├── Arnout_Opfergelt_Hangman/       # Hangman implementation
│   ├── README.md
│   └── word_guessing_game.py
├── Yorbe_Heeren_Hangman/           # Hangman implementation
│   ├── Mini_Project_1_Code_Explanation.md
│   ├── Mini_Project_1.ipynb
│   └── word_guessing_game.py
├── tic_tac_toe/                    # Tic-Tac-Toe implementation
│   ├── README.md
│   ├── main.py
│   ├── playground.py
│   ├── pyproject.toml
│   ├── uv.lock
│   └── ssh_server/                 # SSH server for remote play
│       ├── go.mod
│       ├── go.sum
│       └── main.go
└── README.md
```

## Trying out the games

The three games are accesible to play from any terminal, by running:

```bash
ssh -p 23234 terminal.martingneccoh.io # For tic tac toe
ssh -p 23235 terminal.martingneccoh.io # For hangman v1
ssh -p 23236 terminal.martingneccoh.io # For hangman v2

```

