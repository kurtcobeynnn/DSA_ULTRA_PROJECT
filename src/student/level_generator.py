"""TODO: build a canonical level using the injected terrain generator."""
from src.api import LevelDefinition, LevelSpecification, TerrainGeneratorContract
from src.student.character import Character
from src.student.artifact import Artifact
from src.student.enemy import Enemy


class LevelGenerator:
    """Use the supplied TerrainGeneratorContract; do not instantiate a replacement."""

    def __init__(self, terrain_generator: TerrainGeneratorContract) -> None:
        self._terrain_generator = terrain_generator


    def generate_level(self, specification: LevelSpecification, seed: int) -> LevelDefinition:
        # Preserve specification identities and seed; choose valid opposite endpoints.
        terrain = self._terrain_generator.generate_terrain(specification.terrain_spec, seed)
        character = Character(specification.agent_id)
        artifacts = tuple(
            Artifact(a.artifact_id, a.position, a.value)
            for a in specification.artifact_specs
        )
        enemies = tuple(
            Enemy(e.enemy_id, e.position, e.encounter_penalty)
            for e in specification.enemy_specs
        )
        return LevelDefinition(
            level_id=specification.level_id,
            seed=seed,
            terrain=terrain,
            start=specification.start,
            exit=specification.exit,
            character=character,
            artifacts=artifacts,
            enemies=enemies
        )
