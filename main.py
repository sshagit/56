"""
main.py - Entry point for the 56 Card Game (Fifty-Six)
"""

from game import Game56
from player import GameSetup


def get_player_names():
    """Get player names from user input"""
    print("Enter player names (or press Enter for default names):")
    names = []
    positions = ["North", "East", "South", "West"]
    
    for position in positions:
        name = input(f"Player {position} (default: {position}): ").strip()
        if not name:
            name = position
        names.append(name)
    
    return names


def get_target_score():
    """Get target score from user input"""
    while True:
        try:
            score = input("Enter target score (default: 500): ").strip()
            if not score:
                return 500
            score = int(score)
            if score < 50:
                print("Target score must be at least 50.")
                continue
            return score
        except ValueError:
            print("Please enter a valid number.")


def show_menu():
    """Show the main menu"""
    print("\n" + "="*50)
    print("56 (Fifty-Six) Card Game")
    print("="*50)
    print("1. Start New Game")
    print("2. Play Demo Round")
    print("3. Show Rules")
    print("4. Exit")
    print("="*50)


def show_rules():
    """Display game rules"""
    rules = """
=== 56 (Fifty-Six) Card Game Rules ===

PLAYERS: 4 players in 2 teams (North-South vs East-West)

DECK: 2 standard 24-card decks (48 cards total)
Cards: 9, 10, J, Q, K, A from each suit

CARD VALUES:
- Jack (J): 3 points
- Nine (9): 2 points  
- Ace (A): 1 point
- Ten (10): 1 point
- King (K), Queen (Q): 0 points

TOTAL POINTS: 56 per round (7 points per suit × 4 suits × 2 decks)

BIDDING:
- Starts at 28, can go up to 56
- Players bid in rotation or pass
- Highest bidder chooses trump suit
- Bidding team must win at least their bid amount

GAMEPLAY:
1. Deal 12 cards to each player
2. Conduct bidding
3. Winning bidder declares trump
4. Play 12 tricks
5. Follow suit if possible
6. Trump beats non-trump
7. Highest card of led suit wins if no trump

SCORING:
- If bidding team makes bid: they get bid points
- If bidding team fails: opponents get 56 points
- Game continues until a team reaches target score

STRATEGY:
- Strong hands with Jacks and 9s enable higher bids
- Count points as tricks are played
- Communicate with partner through legal gameplay
"""
    print(rules)


def main():
    """Main game loop"""
    print("Welcome to 56 (Fifty-Six) Card Game!")
    
    while True:
        show_menu()
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            # Start new game
            print("\nSetting up new game...")
            player_names = get_player_names()
            target_score = get_target_score()
            
            print(f"\nStarting game with players: {', '.join(player_names)}")
            print(f"Target score: {target_score}")
            print(f"Teams: {player_names[0]} & {player_names[2]} vs {player_names[1]} & {player_names[3]}")
            
            game = Game56(player_names, target_score)
            game.play_game()
            
        elif choice == "2":
            # Play demo round
            print("\nPlaying demo round with default players...")
            game = Game56(["Alice", "Bob", "Carol", "Dave"], target_score=500)
            game.play_round()
            
        elif choice == "3":
            # Show rules
            show_rules()
            
        elif choice == "4":
            # Exit
            print("Thanks for playing 56 (Fifty-Six) Card Game!")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
