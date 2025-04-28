import dataclasses


@dataclasses.dataclass
class RunAlgorithmParams:
    island_count: int
    number_of_emigrants: int
    migration_interval: int
    dda: str
    tta: str
    series_number: int
    blocking: bool
