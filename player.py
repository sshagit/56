"""
player.py - Player and Team classes for the 56 Card Game
"""

from typing import List, Optional, Dict
from enum import Enum
from card import Card, Suit, calculate_hand_points


class Position(Enum):
    """Player positions around the table"""
    NORTH = "North"
    EAST = "East"
    SOUTH = "South"
    WEST = "West"


class Player:
    """Represents a player in the 56 card game"""
    
    def __init__(self, name: str, position: Position):
        self.name = name
        self.position = position
        self.hand: List[Card] = []
        self.tricks_won: List[List[Card]] = []  # List of tricks (each trick is a list of 4 cards)
    
    def receive_cards(self, cards: List[Card]):
        """Add cards to the player's hand"""
        self.hand.extend(cards)
    
    def play_card(self, card: Card) -> Card:
        """Play a card from hand (remove and return it)"""
        if card in self.hand:
            self.hand.remove(card)
            return card
        raise ValueError(f"Card {card} not in hand")
    
    def can_follow_suit(self, suit: Suit) -> bool:
        """Check if player can follow the led suit"""
        return any(card.suit == suit for card in self.hand)
    
    def get_valid_cards(self, led_suit: Optional[Suit], trump_suit: Optional[Suit]) -> List[Card]:
        """Get list of valid cards to play"""
        if led_suit is None:
            # First player can play any card
            return self.hand.copy()
        
        # Must follow suit if possible
        same_suit_cards = [card for card in self.hand if card.suit == led_suit]
        if same_suit_cards:
            return same_suit_cards
        
        # Can play any card if can't follow suit
        return self.hand.copy()
    
    def has_trump(self, trump_suit: Suit) -> bool:
        """Check if player has trump cards"""
        return any(card.suit == trump_suit for card in self.hand)
    
    def get_trump_cards(self, trump_suit: Suit) -> List[Card]:
        """Get all trump cards in hand"""
        return [card for card in self.hand if card.suit == trump_suit]
    
    def add_trick(self, trick: List[Card]):
        """Add a won trick to the player's collection"""
        self.tricks_won.append(trick)
    
    def get_total_points(self) -> int:
        """Calculate total points from won tricks"""
        total = 0
        for trick in self.tricks_won:
            total += calculate_hand_points(trick)
        return total
    
    def get_hand_points(self) -> int:
        """Calculate points in current hand"""
        return calculate_hand_points(self.hand)
    
    def reset_for_new_round(self):
        """Reset player for a new round"""
        self.hand = []
        self.tricks_won = []
    
    def __str__(self) -> str:
        return f"{self.name} ({self.position.value})"
    
    def __repr__(self) -> str:
        return f"Player('{self.name}', {self.position})"


class Team:
    """Represents a team of two players"""
    
    def __init__(self, name: str, player1: Player, player2: Player):
        self.name = name
        self.players = [player1, player2]
        self.bid = 0
        self.is_bidding_team = False
    
    def get_total_points(self) -> int:
        """Calculate total points for the team from won tricks"""
        return sum(player.get_total_points() for player in self.players)
    
    def get_combined_hand_points(self) -> int:
        """Calculate total points in both players' hands"""
        return sum(player.get_hand_points() for player in self.players)
    
    def set_bid(self, bid: int):
        """Set the team's bid"""
        self.bid = bid
        self.is_bidding_team = True
    
    def clear_bid(self):
        """Clear the team's bid (when they lose bidding)"""
        self.bid = 0
        self.is_bidding_team = False
    
    def has_made_bid(self) -> bool:
        """Check if team has made their bid"""
        return self.get_total_points() >= self.bid
    
    def get_partner(self, player: Player) -> Player:
        """Get the partner of the given player"""
        for p in self.players:
            if p != player:
                return p
        raise ValueError("Player not in this team")
    
    def reset_for_new_round(self):
        """Reset team for a new round"""
        for player in self.players:
            player.reset_for_new_round()
        self.clear_bid()
    
    def __str__(self) -> str:
        return f"Team {self.name}: {self.players[0].name} & {self.players[1].name}"
    
    def __repr__(self) -> str:
        return f"Team('{self.name}', {self.players[0]}, {self.players[1]})"


class GameSetup:
    """Helper class to set up players and teams"""
    
    @staticmethod
    def create_standard_game(player_names: List[str] = None) -> tuple[List[Player], List[Team]]:
        """Create 4 players and 2 teams in standard positions"""
        if player_names is None:
            player_names = ["North", "East", "South", "West"]
        
        if len(player_names) != 4:
            raise ValueError("Need exactly 4 player names")
        
        # Create players in standard positions
        players = [
            Player(player_names[0], Position.NORTH),
            Player(player_names[1], Position.EAST),
            Player(player_names[2], Position.SOUTH),
            Player(player_names[3], Position.WEST)
        ]
        
        # Create teams (North-South vs East-West)
        team1 = Team("North-South", players[0], players[2])  # North & South
        team2 = Team("East-West", players[1], players[3])   # East & West
        
        teams = [team1, team2]
        
        return players, teams
    
    @staticmethod
    def get_player_by_position(players: List[Player], position: Position) -> Player:
        """Get player by their position"""
        for player in players:
            if player.position == position:
                return player
        raise ValueError(f"No player found at position {position}")


# Test the classes if run directly
if __name__ == "__main__":
    # Create a standard game setup
    players, teams = GameSetup.create_standard_game(["Alice", "Bob", "Carol", "Dave"])
    
    print("Players:")
    for player in players:
        print(f"  {player}")
    
    print("\nTeams:")
    for team in teams:
        print(f"  {team}")
    
    # Test with some mock cards
    from card import Deck
    deck = Deck()
    deck.shuffle()
    
    # Deal 12 cards to each player
    for player in players:
        hand = deck.deal_hand(12)
        player.receive_cards(hand)
        print(f"\n{player.name}'s hand ({player.get_hand_points()} points):")
        for card in player.hand:
            print(f"  {card}")
    
    print(f"\nTeam points before play:")
    for team in teams:
        print(f"  {team.name}: {team.get_combined_hand_points()} points in hands")
