import sys
import random
import pygame
from typing import List, Optional, Tuple

# ----------------------------
# FreeCell in Pygame
# Controls
#  - Drag & drop cards/sequences with mouse
#  - Double-click a card to try auto-move to foundation
#  - R: Restart / new deal
#  - U or Ctrl+Z: Undo last move
# ----------------------------

pygame.init()

# --- Display / Layout ---
WIDTH, HEIGHT = 1200, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FreeCell (Pygame)")
FPS = 60
CLOCK = pygame.time.Clock()

# --- Colors ---
GREEN = (20, 110, 20)
DARK_GREEN = (10, 70, 10)
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
RED = (210, 40, 40)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
YELLOW = (255, 210, 0)
SHADOW = (0, 0, 0, 60)

# --- Card dimensions ---
CARD_W, CARD_H = 90, 130
CARD_RADIUS = 10
CARD_SPACING_X = 16
CARD_SPACING_Y = 34  # default spacing; adaptive per column below

# --- Fonts ---
pygame.font.init()
RANK_FONT = pygame.font.SysFont("arial", 24, bold=True)
SUIT_FONT = pygame.font.SysFont("arial", 28)
BIG_FONT = pygame.font.SysFont("arial", 32, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 18)

# --- Suits & Ranks ---
SUITS = ["♠", "♥", "♦", "♣"]
SUIT_COLORS = {"♠": BLACK, "♣": BLACK, "♥": RED, "♦": RED}
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
RANK_TO_VAL = {r: i + 1 for i, r in enumerate(RANKS)}
VAL_TO_RANK = {v: r for r, v in RANK_TO_VAL.items()}

# --- Positions ---
TOP_MARGIN = 24
EDGE_MARGIN = 24

# Top row (Free cells and Foundations)
FREECELL_POS = [
    (EDGE_MARGIN + i * (CARD_W + CARD_SPACING_X), TOP_MARGIN)
    for i in range(4)
]
FOUNDATION_POS = [
    (WIDTH - EDGE_MARGIN - (4 - i) * (CARD_W + CARD_SPACING_X), TOP_MARGIN)
    for i in range(4)
]

# Tableau columns (8 columns)
TABLEAU_POS = [
    (EDGE_MARGIN + i * (CARD_W + CARD_SPACING_X), TOP_MARGIN + CARD_H + 70)
    for i in range(8)
]

# --- Helpers ---

def rounded_rect(surface, rect, color, radius):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, (x + radius, y, w - 2 * radius, h))
    pygame.draw.rect(surface, color, (x, y + radius, w, h - 2 * radius))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
    pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)

# --- Data Model ---
class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
        self.value = RANK_TO_VAL[rank]
        self.color = SUIT_COLORS[suit]
        self.face_up = True  # all cards are face-up in FreeCell
        self.pos = (0, 0)  # for rendering during drag
        self.offset = (0, 0)

    def can_stack_on_tableau(self, other: Optional["Card"]) -> bool:
        """Can this card be placed on top of 'other' in tableau rules?"""
        if other is None:
            return True  # empty column accepts any card
        # alternating colors and descending by 1
        return (self.color != other.color) and (self.value == other.value - 1)

    def can_place_on_foundation(self, other: Optional["Card"]) -> bool:
        """Can this card be placed on top of 'other' in foundation rules?"""
        if other is None:
            return self.value == 1  # Ace only
        return (self.suit == other.suit) and (self.value == other.value + 1)

    def draw(self, surface, x, y, highlight=False, shadow=False):
        rect = (x, y, CARD_W, CARD_H)
        # shadow
        if shadow:
            s = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
            pygame.draw.rect(s, (0, 0, 0, 70), (6, 6, CARD_W, CARD_H), border_radius=CARD_RADIUS)
            surface.blit(s, (x - 6, y - 6))
        # card body
        rounded_rect(surface, rect, WHITE, CARD_RADIUS)
        pygame.draw.rect(surface, LIGHT_GRAY, (x, y, CARD_W, CARD_H), width=2, border_radius=CARD_RADIUS)
        # highlight
        if highlight:
            pygame.draw.rect(surface, YELLOW, (x, y, CARD_W, CARD_H), width=3, border_radius=CARD_RADIUS)
        # rank & suit
        color = self.color
        rank_surf = RANK_FONT.render(self.rank, True, color)
        suit_surf = SUIT_FONT.render(self.suit, True, color)
        surface.blit(rank_surf, (x + 8, y + 6))
        surface.blit(suit_surf, (x + 8, y + 34))
        # big suit center
        big_suit = SUIT_FONT.render(self.suit, True, color)
        surface.blit(big_suit, (x + CARD_W // 2 - big_suit.get_width() // 2, y + CARD_H // 2 - big_suit.get_height() // 2))

    def __repr__(self):
        return f"{self.rank}{self.suit}"


class Move:
    """Represents a move for undo functionality."""
    def __init__(self, src, dst, cards: List[Card]):
        self.src = src
        self.dst = dst
        self.cards = cards


class Pile:
    def __init__(self, pos: Tuple[int, int]):
        self.pos = pos
        self.cards: List[Card] = []

    def top(self) -> Optional[Card]:
        return self.cards[-1] if self.cards else None

    def add_cards(self, cards: List[Card]):
        self.cards.extend(cards)

    def remove_cards(self, n: int) -> List[Card]:
        removed = self.cards[-n:]
        self.cards = self.cards[:-n]
        return removed

    def is_point_inside(self, x, y) -> bool:
        px, py = self.pos
        rect = pygame.Rect(px, py, CARD_W, CARD_H)
        return rect.collidepoint(x, y)

    def draw_placeholder(self, surface, label: str):
        x, y = self.pos
        rounded_rect(surface, (x, y, CARD_W, CARD_H), DARK_GREEN, CARD_RADIUS)
        pygame.draw.rect(surface, LIGHT_GRAY, (x, y, CARD_W, CARD_H), 2, border_radius=CARD_RADIUS)
        text = SMALL_FONT.render(label, True, LIGHT_GRAY)
        surface.blit(text, (x + CARD_W // 2 - text.get_width() // 2, y + CARD_H // 2 - text.get_height() // 2))


class FreeCell(Pile):
    def can_add(self, cards: List[Card]) -> bool:
        return len(cards) == 1 and len(self.cards) == 0

    def draw(self, surface):
        if self.cards:
            self.cards[-1].draw(surface, *self.pos)
        else:
            self.draw_placeholder(surface, "FREE")


class Foundation(Pile):
    def __init__(self, pos: Tuple[int, int], suit: Optional[str] = None):
        super().__init__(pos)
        self.suit = suit  # optional fixed suit, handled dynamically here

    def can_add(self, cards: List[Card]) -> bool:
        if len(cards) != 1:
            return False
        card = cards[0]
        top = self.top()
        return card.can_place_on_foundation(top)

    def draw(self, surface):
        if self.cards:
            self.cards[-1].draw(surface, *self.pos)
        else:
            self.draw_placeholder(surface, "FOUND")


class Tableau(Pile):
    def tableau_spacing(self) -> int:
        """Adaptive vertical spacing so enough of each card (rank/suit) stays visible.
        Tries to use a generous spacing, shrinks only if the column would overflow the screen.
        """
        n = len(self.cards)
        if n <= 1:
            return CARD_SPACING_Y
        MIN_SP = 26  # ensure rank/suit area is visible
        MAX_SP = 40  # comfortable spacing when room allows
        x, y = self.pos
        avail = HEIGHT - y - CARD_H - 20
        # If we can afford MAX_SP, use it; otherwise scale down but never below MIN_SP
        needed = (n - 1) * MAX_SP
        if needed <= avail:
            return MAX_SP
        sp = max(MIN_SP, int(avail / (n - 1)))
        return sp

    def can_add(self, cards: List[Card]) -> bool:
        if not cards:
            return False
        # incoming 'cards' must be a valid descending alternating sequence
        if not is_valid_descending_sequence(cards):
            return False
        top = self.top()
        return cards[0].can_stack_on_tableau(top)

    def get_click_index(self, x, y) -> Optional[int]:
        px, py = self.pos
        sp = self.tableau_spacing()
        # Determine which card index is clicked in this column
        for i, card in enumerate(self.cards):
            cx, cy = px, py + i * sp
            rect = pygame.Rect(cx, cy, CARD_W, CARD_H)
            if rect.collidepoint(x, y):
                return i
        # If below last card but inside column width, select last
        if self.cards:
            last_y = py + (len(self.cards) - 1) * sp
            if pygame.Rect(px, py, CARD_W, last_y - py + CARD_H).collidepoint(x, y):
                return len(self.cards) - 1
        return None

    def draw(self, surface):
        x, y = self.pos
        sp = self.tableau_spacing()
        if not self.cards:
            # empty placeholder
            rounded_rect(surface, (x, y, CARD_W, CARD_H), DARK_GREEN, CARD_RADIUS)
            pygame.draw.rect(surface, LIGHT_GRAY, (x, y, CARD_W, CARD_H), 2, border_radius=CARD_RADIUS)
        # stack
        for i, card in enumerate(self.cards):
            cy = y + i * sp
            card.draw(surface, x, cy, shadow=True)
        x, y = self.pos
        if not self.cards:
            # empty placeholder
            rounded_rect(surface, (x, y, CARD_W, CARD_H), DARK_GREEN, CARD_RADIUS)
            pygame.draw.rect(surface, LIGHT_GRAY, (x, y, CARD_W, CARD_H), 2, border_radius=CARD_RADIUS)
        # stack
        for i, card in enumerate(self.cards):
            cy = y + i * CARD_SPACING_Y
            card.draw(surface, x, cy, shadow=True)


# --- Utility functions ---
def is_valid_descending_sequence(cards: List[Card]) -> bool:
    if not cards:
        return False
    # Must be descending by 1 and alternating colors
    for i in range(len(cards) - 1):
        a, b = cards[i], cards[i + 1]
        if not (a.color != b.color and a.value == b.value + 1):
            return False
    return True


def count_empty_freecells(freecells: List[FreeCell]) -> int:
    return sum(1 for f in freecells if not f.cards)


def count_empty_tableau_columns(tableaus: List[Tableau], exclude: Optional[Tableau] = None) -> int:
    c = 0
    for t in tableaus:
        if t is not exclude and len(t.cards) == 0:
            c += 1
    return c


def max_movable_sequence_len(freecells: List[FreeCell], tableaus: List[Tableau], dest: Optional[Tableau]) -> int:
    """
    Movement capacity per the user's simplified rule:
      - You can move sequences of length N where N = total empty spaces + 1,
        where empty spaces = empty free cells + empty tableau columns (excluding the destination column if it's empty).
    This is a simpler variant of the classic rule and matches the provided instructions.
    """
    empty_free = count_empty_freecells(freecells)
    empty_tableau = count_empty_tableau_columns(tableaus, exclude=dest)
    return max(1, empty_free + empty_tableau + 1)


# --- Game State ---
class Game:
    def __init__(self):
        self.tableau: List[Tableau] = [Tableau(TABLEAU_POS[i]) for i in range(8)]
        self.freecells: List[FreeCell] = [FreeCell(FREECELL_POS[i]) for i in range(4)]
        self.foundations: List[Foundation] = [Foundation(FOUNDATION_POS[i]) for i in range(4)]

        self.drag_cards: List[Card] = []
        self.drag_src: Optional[Pile] = None
        self.drag_index: int = -1  # for tableau drag, index in column
        self.drag_offset: Tuple[int, int] = (0, 0)
        self.mouse_down_time: float = 0
        self.last_click_time: float = 0
        self.undo_stack: List[Move] = []

        self.new_deal()

    def new_deal(self):
        # reset
        for t in self.tableau:
            t.cards = []
        for f in self.freecells:
            f.cards = []
        for fo in self.foundations:
            fo.cards = []
        self.drag_cards = []
        self.drag_src = None
        self.undo_stack.clear()

        # create and shuffle deck
        deck = [Card(s, r) for s in SUITS for r in RANKS]
        random.shuffle(deck)

        # deal to 8 columns: first 4 get 7, last 4 get 6
        for i in range(52):
            col = i % 8
            self.tableau[col].cards.append(deck[i])

        # Adjust to 7/6 pattern by moving extra from last columns to first four
        # (Dealing i%8 already gives 7 on first four and 6 on last four with 52 cards.)

    # --- Rendering ---
    def draw(self):
        SCREEN.fill(GREEN)

        # Title
        title = BIG_FONT.render("FreeCell", True, WHITE)
        SCREEN.blit(title, (EDGE_MARGIN, 4))

        # Draw top row separators text
        tip = SMALL_FONT.render("Double-click to auto-move • R: New game • U/Ctrl+Z: Undo", True, WHITE)
        SCREEN.blit(tip, (EDGE_MARGIN, TOP_MARGIN + CARD_H + 30))

        # Draw Freecells
        for f in self.freecells:
            f.draw(SCREEN)

        # Draw Foundations
        for i, fo in enumerate(self.foundations):
            fo.draw(SCREEN)
            # little suit hint if empty
            if not fo.cards:
                hint = SMALL_FONT.render("A→K", True, LIGHT_GRAY)
                SCREEN.blit(hint, (fo.pos[0] + CARD_W // 2 - hint.get_width() // 2, fo.pos[1] + CARD_H // 2 + 16))

        # Draw Tableaus
        for t in self.tableau:
            t.draw(SCREEN)

        # Draw dragging cards on top
        if self.drag_cards:
            mx, my = pygame.mouse.get_pos()
            ox, oy = self.drag_offset
            base_x = mx - ox
            base_y = my - oy
            sp = getattr(self, 'current_drag_spacing', CARD_SPACING_Y)
            for i, c in enumerate(self.drag_cards):
                cy = base_y + i * sp
                c.draw(SCREEN, base_x, cy, highlight=True, shadow=True)

        # Victory check
        if self.is_victory():
            banner = BIG_FONT.render("You win! Press R for a new game.", True, YELLOW)
            SCREEN.blit(banner, (WIDTH // 2 - banner.get_width() // 2, 10))

    # --- Game Logic ---
    def is_victory(self) -> bool:
        return sum(len(f.cards) for f in self.foundations) == 52

    def pile_at_point(self, x, y) -> Optional[Pile]:
        # Check freecells
        for f in self.freecells:
            if f.is_point_inside(x, y):
                return f
        # Check foundations
        for fo in self.foundations:
            if fo.is_point_inside(x, y):
                return fo
        # Check tableau columns
        for t in self.tableau:
            tx, ty = t.pos
            sp = t.tableau_spacing()
            h = max(CARD_H, sp * (len(t.cards) - 1) + CARD_H)
            rect = pygame.Rect(tx, ty, CARD_W, h)
            if rect.collidepoint(x, y):
                return t
        return None

    def start_drag(self, x, y):
        if self.drag_cards:
            return
        pile = self.pile_at_point(x, y)
        if pile is None:
            return

        # store per-drag spacing to keep visual consistency during drag
        self.current_drag_spacing = CARD_SPACING_Y

        if isinstance(pile, FreeCell):
            if not pile.cards:
                return
            self.drag_cards = [pile.cards[-1]]
            self.drag_src = pile
            self.drag_index = -1
        elif isinstance(pile, Foundation):
            # Usually foundations are not dragged from in FreeCell
            return
        elif isinstance(pile, Tableau):
            idx = pile.get_click_index(x, y)
            if idx is None:
                return
            # take sequence starting at idx if valid
            seq = pile.cards[idx:]
            if idx < len(pile.cards) - 1 and not is_valid_descending_sequence(seq):
                # if the clicked card isn't the start of a valid sequence, restrict to that single top card
                seq = pile.cards[-1:]
                idx = len(pile.cards) - 1
            self.drag_cards = seq
            self.drag_src = pile
            self.drag_index = idx
            self.current_drag_spacing = pile.tableau_spacing()
        # set drag offset within first card
        mx, my = pygame.mouse.get_pos()
        top_pos = None
        if isinstance(self.drag_src, Tableau) and self.drag_index >= 0:
            top_pos = (self.drag_src.pos[0], self.drag_src.pos[1] + self.drag_index * self.current_drag_spacing)
        else:
            top_pos = (pile.pos[0], pile.pos[1])
        self.drag_offset = (mx - top_pos[0], my - top_pos[1])

    def cancel_drag(self):
        self.drag_cards = []
        self.drag_src = None
        self.drag_index = -1

    def finish_drag(self, x, y):
        if not self.drag_cards or self.drag_src is None:
            return
        dest = self.pile_at_point(x, y)
        if dest is None:
            # drop back
            self.cancel_drag()
            return

        moved = False
        cards = self.drag_cards

        # Determine allowed move size for tableau destination
        if isinstance(dest, Tableau):
            max_len = max_movable_sequence_len(self.freecells, self.tableau, dest)
        else:
            max_len = 1

        # Validate destination rule
        if isinstance(dest, FreeCell):
            if len(cards) == 1 and dest.can_add(cards):
                self._commit_move(self.drag_src, dest, 1)
                moved = True
        elif isinstance(dest, Foundation):
            if len(cards) == 1 and dest.can_add(cards):
                self._commit_move(self.drag_src, dest, 1)
                moved = True
        elif isinstance(dest, Tableau):
            # If moving from tableau, ensure the sequence is internally valid and within capacity
            if len(cards) <= max_len and dest.can_add(cards):
                n = len(cards)
                self._commit_move(self.drag_src, dest, n)
                moved = True

        # If not moved, snap back
        if not moved:
            # no state change needed; drag canceled
            pass

        self.cancel_drag()

    def _commit_move(self, src: Pile, dst: Pile, n: int):
        # remove from src
        moved_cards = []
        if isinstance(src, Tableau) and self.drag_index >= 0:
            moved_cards = src.cards[self.drag_index: self.drag_index + n]
            del src.cards[self.drag_index: self.drag_index + n]
        else:
            moved_cards = src.remove_cards(n)
        # add to dest
        dst.add_cards(moved_cards)
        # record undo
        self.undo_stack.append(Move(src, dst, moved_cards))

    def auto_move_to_foundation(self, card: Card, src: Pile) -> bool:
        if not card:
            return False
        for fo in self.foundations:
            if fo.can_add([card]):
                # move single card to this foundation
                if isinstance(src, Tableau):
                    # find card index (must be topmost selected)
                    if src.cards and src.cards[-1] is card:
                        src.remove_cards(1)
                        fo.add_cards([card])
                        self.undo_stack.append(Move(src, fo, [card]))
                        return True
                elif isinstance(src, FreeCell):
                    if src.cards and src.cards[-1] is card:
                        src.remove_cards(1)
                        fo.add_cards([card])
                        self.undo_stack.append(Move(src, fo, [card]))
                        return True
        return False

    def try_double_click(self, x, y):
        pile = self.pile_at_point(x, y)
        if pile is None:
            return
        if isinstance(pile, Tableau):
            if pile.cards:
                top = pile.cards[-1]
                self.auto_move_to_foundation(top, pile)
        elif isinstance(pile, FreeCell):
            if pile.cards:
                self.auto_move_to_foundation(pile.cards[-1], pile)

    def undo(self):
        if not self.undo_stack:
            return
        last = self.undo_stack.pop()
        # remove from dst
        n = len(last.cards)
        last.dst.cards = last.dst.cards[:-n]
        # add back to src
        last.src.cards.extend(last.cards)


# --- Main loop ---
def main():
    game = Game()
    running = True

    while running:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.new_deal()
                elif event.key == pygame.K_u or (event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL)):
                    game.undo()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                now = pygame.time.get_ticks()
                if now - game.last_click_time < 300:  # double click
                    game.try_double_click(*event.pos)
                    game.last_click_time = 0
                else:
                    game.last_click_time = now
                    game.start_drag(*event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                game.finish_drag(*event.pos)

        game.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
