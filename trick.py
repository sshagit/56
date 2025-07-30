"""
trick.py - Trick-taking logic for the 56 Card Game
"""

from typing import List, Optional, Dict, Tuple
from enum import Enum
from card import Card, Suit, Rank, calculate_hand_points
from player import Player, Team


class TrickCard:
    """Represents a card played in a trick with the player who played it"""
    
    def __init__(self, card: Card, player: Player):
        self.card = card
        self.player = player
    
    def __str__(self) -> str:
        return f"{self.player.name}: {self.card}"
    
    def __repr__(self) -> str:
        return f"TrickCard({self.card}, {self.player})"


class Trick:
    """Represents a single trick in the game"""
    
    def __init__(self, trick_number: int, leading_player: Player):
        self.trick_number = trick_number
        self.leading_player = leading_player
        self.cards_played: List[TrickCard] = []
        self.winner: Optional[Player] = None
        self.trump_suit: Optional[Suit] = None
        self.led_suit: Optional[Suit] = None
    
    def add_card(self, card: Card, player: Player, trump_suit: Optional[Suit] = None):
        """Add a card to the trick"""
        if len(self.cards_played) >= 4:
            raise ValueError("Trick already has 4 cards")
        
        trick_card = TrickCard(card, player)
        self.cards_played.append(trick_card)
        
        # Set trump suit and led suit
        if trump_suit:
            self.trump_suit = trump_suit
        
        if len(self.cards_played) == 1:
            self.led_suit = card.suit
        
        # Determine winner if trick is complete
        if len(self.cards_played) == 4:
            self.winner = self._determine_winner()
    
    def _determine_winner(self) -> Player:
        """Determine the winner of the trick"""
        if not self.cards_played or len(self.cards_played) != 4:
            raise ValueError("Cannot determine winner of incomplete trick")
        
        # Separate trump cards and non-trump cards
        trump_cards = []
        led_suit_cards = []
        other_cards = []
        
        for trick_card in self.cards_played:
            if self.trump_suit and trick_card.card.suit == self.trump_suit:
                trump_cards.append(trick_card)
            elif trick_card.card.suit == self.led_suit:
                led_suit_cards.append(trick_card)
            else:
                other_cards.append(trick_card)
        
        # Trump cards win over everything
        if trump_cards:
            winning_card = self._get_highest_card(trump_cards)
            return winning_card.player
        
        # If no trump, highest card of led suit wins
        if led_suit_cards:
            winning_card = self._get_highest_card(led_suit_cards)
            return winning_card.player
        
        # This shouldn't happen in a valid game
        raise ValueError("No valid cards found in trick")
    
    def _get_highest_card(self, trick_cards: List[TrickCard]) -> TrickCard:
        """Get the highest card from a list of trick cards"""
        if not trick_cards:
            raise ValueError("No cards to compare")
        
        # Use the rank_value from the card's rank enum (Jack=6 is highest)
        return max(trick_cards, key=lambda tc: tc.card.rank.rank_value)
    
    def get_points(self) -> int:
        """Get total points from cards in this trick"""
        return sum(trick_card.card.points for trick_card in self.cards_played)
    
    def get_cards(self) -> List[Card]:
        """Get all cards in this trick"""
        return [trick_card.card for trick_card in self.cards_played]
    
    def is_complete(self) -> bool:
        """Check if trick is complete (4 cards played)"""
        return len(self.cards_played) == 4
    
    def __str__(self) -> str:
        result = f"Trick {self.trick_number} (led by {self.leading_player.name}):\n"
        for trick_card in self.cards_played:
            result += f"  {trick_card}\n"
        if self.winner:
            result += f"  Winner: {self.winner.name} ({self.get_points()} points)"
        return result.strip()


class TrickManager:
    """Manages the trick-taking phase of the game"""
    
    def __init__(self, players: List[Player], teams: List[Team], trump_suit: Suit):
        self.players = players
        self.teams = teams
        self.trump_suit = trump_suit
        self.tricks: List[Trick] = []
        self.current_trick: Optional[Trick] = None
        self.current_player_index = 0
    
    def start_new_trick(self, leading_player: Player) -> Trick:
        """Start a new trick"""
        trick_number = len(self.tricks) + 1
        self.current_trick = Trick(trick_number, leading_player)
        self.current_trick.trump_suit = self.trump_suit
        
        # Set current player to the leading player
        self.current_player_index = self.players.index(leading_player)
        
        return self.current_trick
    
    def get_current_player(self) -> Player:
        """Get the current player who should play a card"""
        return self.players[self.current_player_index]
    
    def get_next_player(self) -> Player:
        """Get the next player in turn order"""
        next_index = (self.current_player_index + 1) % len(self.players)
        return self.players[next_index]
    
    def play_card(self, card: Card, player: Player) -> bool:
        """Play a card in the current trick"""
        if not self.current_trick:
            raise ValueError("No active trick")
        
        if player != self.get_current_player():
            raise ValueError(f"Not {player.name}'s turn")
        
        # Validate the card play
        if not self._is_valid_play(card, player):
            return False
        
        # Remove card from player's hand and add to trick
        player.play_card(card)
        self.current_trick.add_card(card, player, self.trump_suit)
        
        # Move to next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        
        # If trick is complete, award it to the winner
        if self.current_trick.is_complete():
            self._complete_trick()
        
        return True
    
    def _is_valid_play(self, card: Card, player: Player) -> bool:
        """Check if a card play is valid"""
        if card not in player.hand:
            return False
        
        if not self.current_trick or not self.current_trick.cards_played:
            # First card of trick - any card is valid
            return True
        
        led_suit = self.current_trick.led_suit
        valid_cards = player.get_valid_cards(led_suit, self.trump_suit)
        
        return card in valid_cards
    
    def _complete_trick(self):
        """Complete the current trick and award it to the winner"""
        if not self.current_trick or not self.current_trick.is_complete():
            return
        
        winner = self.current_trick.winner
        if winner:
            winner.add_trick(self.current_trick.get_cards())
        
        self.tricks.append(self.current_trick)
        
        # Winner leads the next trick
        if winner:
            self.current_player_index = self.players.index(winner)
        
        self.current_trick = None
    
    def get_team_points(self) -> Dict[Team, int]:
        """Get total points for each team"""
        team_points = {}
        for team in self.teams:
            team_points[team] = team.get_total_points()
        return team_points
    
    def is_round_complete(self) -> bool:
        """Check if all tricks have been played"""
        return len(self.tricks) == 12  # 12 tricks per round
    
    def get_round_summary(self) -> str:
        """Get a summary of the round"""
        summary = f"Round Summary (Trump: {self.trump_suit.value}):\n"
        summary += f"Tricks played: {len(self.tricks)}/12\n\n"
        
        for trick in self.tricks:
            summary += f"{trick}\n\n"
        
        team_points = self.get_team_points()
        summary += "Team Points:\n"
        for team, points in team_points.items():
            summary += f"  {team.name}: {points} points\n"
        
        return summary.strip()


# Test the trick-taking system if run directly
if __name__ == "__main__":
    from card import Deck
    from player import GameSetup
    
    # Create a standard game
    players, teams = GameSetup.create_standard_game(["Alice", "Bob", "Carol", "Dave"])
    
    # Deal cards
    deck = Deck()
    deck.shuffle()
    for player in players:
        hand = deck.deal_hand(12)
        player.receive_cards(hand)
    
    # Set trump suit
    trump_suit = Suit.HEARTS
    
    # Create trick manager
    trick_manager = TrickManager(players, teams, trump_suit)
    
    print(f"Trump suit: {trump_suit.value}")
    print(f"Playing order: {' -> '.join(p.name for p in players)}")
    
    # Play one trick as demonstration
    print(f"\n=== Trick 1 ===")
    trick = trick_manager.start_new_trick(players[0])  # Alice leads
    
    for i in range(4):
        current_player = trick_manager.get_current_player()
        # Simple demo: play first valid card
        led_suit = trick.led_suit if trick.cards_played else None
        valid_cards = current_player.get_valid_cards(led_suit, trump_suit)
        
        if valid_cards:
            card_to_play = valid_cards[0]  # Play first valid card
            print(f"{current_player.name} plays {card_to_play}")
            trick_manager.play_card(card_to_play, current_player)
    
    print(f"\n{trick}")
    
    print(f"\nTeam points after 1 trick:")
    team_points = trick_manager.get_team_points()
    for team, points in team_points.items():
        print(f"  {team.name}: {points} points")
