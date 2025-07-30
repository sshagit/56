# 56 Card Game (Fifty-Six)

A complete Python implementation of the card game "56" for 4 players (two teams of two). 

## Features

✅ **Complete Game Implementation**
- Full deck logic (2x24-card decks = 48 cards)
- 4-player setup with team partnerships (North-South vs East-West)
- Bidding system (28-56 points)
- Trump suit selection
- Trick-taking with proper card ranking
- Accurate scoring system
- CLI interface with menu system

✅ **Game Components**
- `card.py` - Card, Suit, Rank, and Deck classes
- `player.py` - Player, Team, and game setup logic  
- `bidding.py` - Complete bidding system with validation
- `trick.py` - Trick-taking logic with trump handling
- `game.py` - Main game flow and round management
- `main.py` - CLI interface and menu system

## How to Run

1. Ensure you have Python 3.8+ installed
2. Run the game:
   ```
   python main.py
   ```

3. Choose from the menu:
   - **Start New Game** - Play a full game with custom settings
   - **Play Demo Round** - Quick demonstration round
   - **Show Rules** - View complete game rules
   - **Exit** - Quit the game

## Game Rules Summary

- **Players**: 4 (two teams of two, sitting opposite)
- **Deck**: 48 cards (2x24-card decks: 9,10,J,Q,K,A of each suit)
- **Points**: J=3, 9=2, A=1, 10=1, K=0, Q=0 (total 56 points)
- **Bidding**: 28-56, highest bidder chooses trump
- **Goal**: Bidding team must win ≥ their bid in tricks

## Architecture

The game is built with a modular design:

```
Card System → Player/Team System → Bidding → Trick-Taking → Game Logic → CLI
```

Each module is independently testable and can be run standalone for debugging.

## Development

Run individual components for testing:
```bash
python card.py      # Test card and deck logic
python player.py    # Test player and team setup
python bidding.py   # Test bidding system
python trick.py     # Test trick-taking logic
python game.py      # Test complete game round
```

## Future Enhancements

- [ ] Web interface (Flask/Streamlit)
- [ ] AI players with different difficulty levels
- [ ] Game statistics and replay system
- [ ] Network multiplayer support
- [ ] Advanced bidding strategies

---

Enjoy playing 56 (Fifty-Six)!
