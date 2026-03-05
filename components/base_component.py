from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    from game_map import GameMap

ParentT = TypeVar("ParentT", bound="Entity")


class BaseComponent(Generic[ParentT]):
    parent: ParentT  # Owning entity instance.

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap

    @property
    def engine(self) -> Engine:
        return self.gamemap.engine
    
    