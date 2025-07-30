"""
card.py - Card and Deck classes for the 56 Card Game
"""

from enum import Enum
import random
from typing import List, Optional


class Suit(Enum):
    """Card suits"""
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"


class Rank(Enum):
    """Card ranks with their point values and playing order"""
    JACK = ("J", 3, 6)      # Highest rank, 3 points
    NINE = ("9", 2, 5)      # Second highest, 2 points  
    ACE = ("A", 1, 4)       # Third highest, 1 point
    TEN = ("10", 1, 3)      # Fourth highest, 1 point
    KING = ("K", 0, 2)      # Fifth highest, 0 points
    QUEEN = ("Q", 0, 1)     # Lowest rank, 0 points
    
    def __init__(self, display_name: str, points: int, rank_value: int):
        self.display_name = display_name
        self.points = points
        self.rank_value = rank_value  # For comparison purposes (higher rank_value = higher rank)


class Card:
    """Represents a single playing card"""
    
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
    
    @property
    def points(self) -> int:
        """Get the point value of this card"""
        return self.rank.points
    
    def __str__(self) -> str:
        return f"{self.rank.display_name} of {self.suit.value}"
    
    def __repr__(self) -> str:
        return f"Card({self.suit}, {self.rank})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank
    
    def __hash__(self) -> int:
        return hash((self.suit, self.rank))


class Deck:
    """Represents a deck of cards for the 56 game (2 x 24-card decks = 48 cards)"""
    
    def __init__(self):
        self.cards: List[Card] = []
        self._create_deck()
    
    def _create_deck(self):
        """Create 2 standard 24-card decks (48 cards total)"""
        self.cards = []
        
        # Create 2 identical 24-card decks
        for _ in range(2):
            for suit in Suit:
                for rank in Rank:
                    self.cards.append(Card(suit, rank))
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
    
    def deal_card(self) -> Optional[Card]:
        """Deal one card from the top of the deck"""
        if self.cards:
            return self.cards.pop()
        return None
    
    def deal_hand(self, num_cards: int) -> List[Card]:
        """Deal a hand of cards"""
        hand = []
        for _ in range(num_cards):
            card = self.deal_card()
            if card:
                hand.append(card)
        return hand
    
    def cards_remaining(self) -> int:
        """Get the number of cards remaining in the deck"""
        return len(self.cards)
    
    def reset(self):
        """Reset the deck to full 48 cards"""
        self._create_deck()
    
    def __len__(self) -> int:
        return len(self.cards)
    
    def __str__(self) -> str:
        return f"Deck with {len(self.cards)} cards"


def calculate_hand_points(cards: List[Card]) -> int:
    """Calculate total points in a hand of cards"""
    return sum(card.points for card in cards)


def calculate_suit_points(cards: List[Card], suit: Suit) -> int:
    """Calculate points for cards of a specific suit"""
    return sum(card.points for card in cards if card.suit == suit)


# Test the classes if run directly
if __name__ == "__main__":
    # Create and test a deck
    deck = Deck()
    print(f"Created deck with {len(deck)} cards")
    print(f"Total points in full deck: {calculate_hand_points(deck.cards)}")
    
    # Verify we have the right number of each card
    suit_counts = {suit: 0 for suit in Suit}
    rank_counts = {rank: 0 for rank in Rank}
    
    for card in deck.cards:
        suit_counts[card.suit] += 1
        rank_counts[card.rank] += 1
    
    print("\nSuit distribution:")
    for suit, count in suit_counts.items():
        print(f"  {suit.value}: {count} cards")
    
    print("\nRank distribution:")
    for rank, count in rank_counts.items():
        print(f"  {rank.display_name}: {count} cards ({rank.points} points each)")
    
    # Test dealing cards
    deck.shuffle()
    hand = deck.deal_hand(12)
    print(f"\nDealt hand of {len(hand)} cards:")
    for card in hand:
        print(f"  {card}")
    print(f"Hand points: {calculate_hand_points(hand)}")
