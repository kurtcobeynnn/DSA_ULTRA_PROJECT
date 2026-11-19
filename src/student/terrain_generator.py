"""TODO: generate canonical terrain deterministically from specification and seed."""
from src.api import Terrain, TerrainGenerationSpec
import random


class TerrainGenerator:
    """Keep state local; identical inputs must also agree across fresh instances."""

    def __init__(self) -> None:
        pass


    def generate_terrain(self, specification: TerrainGenerationSpec, seed: int) -> Terrain:
        # This workbench accepts only its documented public introductory family.
        rng = random.Random(seed)          # random number generator.
        rows = specification.rows
        cols = specification.columns
        terrain_rows = tuple("." * cols for _ in range(rows))
        return Terrain(terrain_rows = terrain_rows)



    