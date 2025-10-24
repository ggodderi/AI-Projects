Create a game called FreeCell.  here are the instructions:

1 - Create the game in python using pygame.
2 - Make sure when the cards are drawn, enough of the card is visible to be able to tell what the card is.

Objective
Move all 52 cards from the tableau to the foundation piles, building each suit in ascending order from Ace to King.

🧱 Game Setup
- Deck: Standard 52-card deck (no Jokers)
- Tableau: 8 columns; first 4 have 7 cards, last 4 have 6 — all face-up
- Free Cells: 4 empty spaces used to temporarily hold single cards
- Foundation Piles: 4 piles (one per suit) to build sequences from Ace to King


Gameplay Rules
- Card Movement:
- Move one card at a time between tableau columns, free cells, and foundation piles
- Tableau builds down in alternating colors (e.g., red 6 on black 7)
- Foundation builds up by suit (Ace → King)
- Free Cells:
- Hold only one card each
- Used to temporarily store cards to facilitate moves
- Moving Sequences:
- You can move sequences of cards in descending order and alternating colors
- The number of cards you can move depends on available free cells and empty tableau columns:
- With 1 empty space: move 1 card
- With 2 empty spaces: move 2 cards
- And so on
- 
- Empty Columns:
- Any card or valid sequence can be moved to an empty tableau column
