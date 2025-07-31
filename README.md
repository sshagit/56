# 🃏 Ultimate 56 Card Game

A complete implementation of the classic Indian 56 card game! Play against 3 intelligent AI opponents in this strategic trick-taking card game.

## 🎮 [Play Online Now!](https://sshastri.github.io/14.56/)

*Live demo hosted on GitHub Pages - no installation required!*

## ✨ Features

🌐 **Pure Web Game** - HTML/CSS/JavaScript only, no server needed  
📱 **Mobile Responsive** - Optimized for all screen sizes  
🎨 **Modern UI** - Beautiful glassmorphism design with smooth animations  
🤖 **Smart AI** - Strategic AI opponents following proper 56 game rules  
🎯 **Team Play** - North-South vs East-West team partnerships  
� **Authentic Gameplay** - Traditional 56 card game with proper bidding and scoring  
⚡ **Instant Play** - Click and play immediately in your browser  

## 🎯 Game Rules

- **Players**: 4 players in 2 teams (North-South vs East-West)
- **Cards**: Traditional 56 deck (2 copies of J, 9, A, 10, K, Q in all 4 suits)
- **Deal**: 12 cards per player
- **Bidding**: Teams bid points they expect to score (32-56 points)
- **Trump**: Winning bidder selects trump suit
- **Play**: Trick-taking game where you must follow suit
- **Scoring**: Points for tricks won, bonus for making bid

## 🚀 Quick Start for GitHub Pages

1. **Fork this repository**
2. **Enable GitHub Pages** in repository settings  
3. **Play online** at `https://yourusername.github.io/14.56/`

## 📱 How to Play

1. **Enter your name** and click "Start Game"
2. **Bidding happens automatically** - AI handles the bidding phase
3. **Trump suit is announced** - pay attention to the trump display
4. **Play your cards** - click on highlighted cards when it's your turn
5. **Follow suit rules** - you must play the same suit if you have it
6. **Use trump wisely** - trump cards beat non-trump cards
7. **Team scoring** - work with your North partner against East-West

## 🎮 Controls

- **Click cards** to play them when highlighted in green
- **Hover effects** show which cards you can play
- **Scores update** automatically after each trick
- **Game status** shows current player and game state

## 🔧 Technical Details

- **Self-contained** - Single HTML file with embedded CSS and JavaScript
- **No dependencies** - Runs in any modern web browser
- **Responsive design** - Works on desktop, tablet, and mobile
- **Smart AI** - Implements proper 56 strategy including trump conservation
- **Team coordination** - AI players understand partnership play

## 📝 Project Structure

```
📁 14.56/
├── 📄 index.html          # Complete game (single file)
├── 📄 README.md           # This file
├── 📁 .github/            # GitHub configuration
└── 📄 .gitignore         # Git ignore rules
```

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

## 📜 License

This project is open source. Feel free to use and modify as needed.

---

**🎉 Enjoy playing the Ultimate 56 Card Game!**

2. **For local testing:**
   ```bash
   # Simply open index.html in your browser
   open index.html
   
   # Or serve with a local server
   python -m http.server 8000
   # Then visit http://localhost:8000
   ```

### 🐍 Python CLI Version

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

### 🌐 Python Flask Web Version

1. Install requirements:
   ```
   pip install flask
   ```

2. Run the web server:
   ```
   python interactive_web.py
   ```

3. Open your browser to `http://localhost:5000`

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
