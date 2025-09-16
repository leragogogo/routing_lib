from abc import ABC, abstractmethod
from dataclasses import dataclass
from graph.core import Graph


@dataclass(frozen=True)
class JSONSource:
    filepath: str


@dataclass(frozen=True)
class CSVSource:
    node_filepath: str
    edge_filepath: str


@dataclass()
class OSMSource:
    filepath: str
    filter_name: str = None
    way_filter: callable([[dict], bool]) = None


@dataclass(frozen=True)
class LoadOptions:
    directed: bool = False
    strategy: str = "all"


class AbstractLoader(ABC):
    """Contract for all loaders that build a Graph from some source."""

    @abstractmethod
    def load(self, source: any, options: LoadOptions) -> Graph:
        """Load a Graph from the given source object."""
        raise NotImplementedError
