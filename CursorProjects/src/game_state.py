from enum import Enum, auto
from typing import Callable, Optional


class GameState(Enum):
	TITLE = auto()
	PLAYING = auto()
	PAUSED = auto()
	WAVE_CLEARED = auto()
	GAME_OVER = auto()


class GameStateManager:
	def __init__(self) -> None:
		self.current: GameState = GameState.TITLE
		self.on_enter: dict[GameState, Callable[[], None]] = {}
		self.on_exit: dict[GameState, Callable[[], None]] = {}

	def set_on_enter(self, state: GameState, handler: Callable[[], None]) -> None:
		self.on_enter[state] = handler

	def set_on_exit(self, state: GameState, handler: Callable[[], None]) -> None:
		self.on_exit[state] = handler

	def set_state(self, next_state: GameState) -> None:
		if next_state == self.current:
			return
		if old_exit := self.on_exit.get(self.current):
			old_exit()
		self.current = next_state
		if new_enter := self.on_enter.get(self.current):
			new_enter()
