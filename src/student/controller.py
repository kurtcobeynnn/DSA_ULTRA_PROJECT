"""TODO: select one public action from each immutable world observation."""

from collections import deque

from src.api import (
    Position,
    WorldAction,
    WorldActionType,
    WorldSnapshot,
)

_DIRECTIONS: tuple[tuple[WorldActionType, int, int], ...] = (
    (WorldActionType.MOVE_NORTH, -1, 0),
    (WorldActionType.MOVE_SOUTH, 1, 0),
    (WorldActionType.MOVE_WEST, 0, -1),
    (WorldActionType.MOVE_EAST, 0, 1),
)


class AgentController:
    """A new controller is constructed for each run; arrival still needs EXIT."""

    def __init__(self, algorithm: str = "bfs") -> None:
        self.algorithm = algorithm.lower()

    def _can_step_to(self, state: WorldSnapshot, pos: Position, goal: Position) -> bool:
        if not state.is_in_bounds(pos):
            return False
        # Allow stepping onto goal even if goal is the exit tile or another non-"." marker
        if pos == goal:
            return True
        return state.is_traversable(pos)

    def _next_step_bfs(self, state: WorldSnapshot, goal: Position) -> WorldActionType | None:
        start = state.agent_position
        if start == goal:
            return None

        queue: deque[Position] = deque([start])
        came_from: dict[Position, tuple[Position | None, WorldActionType | None]] = {
            start: (None, None)
        }

        while queue:
            curr = queue.popleft()
            if curr == goal:
                break

            for action_type, d_row, d_col in _DIRECTIONS:
                nxt = Position(curr.row + d_row, curr.column + d_col)
                if nxt in came_from or not self._can_step_to(state, nxt, goal):
                    continue
                came_from[nxt] = (curr, action_type)
                queue.append(nxt)

        if goal not in came_from:
            return None

        step_pos = goal
        first_action: WorldActionType | None = None
        while came_from[step_pos][0] is not None:
            parent, action_type = came_from[step_pos]
            first_action = action_type
            step_pos = parent  # type: ignore[assignment]

        return first_action

    def _next_step_dfs(self, state: WorldSnapshot, goal: Position) -> WorldActionType | None:
        start = state.agent_position
        if start == goal:
            return None

        visited: set[Position] = {start}
        path: list[tuple[Position, WorldActionType]] = []

        def dfs(curr: Position) -> bool:
            if curr == goal:
                return True
            for action_type, d_row, d_col in _DIRECTIONS:
                nxt = Position(curr.row + d_row, curr.column + d_col)
                if nxt in visited or not self._can_step_to(state, nxt, goal):
                    continue
                visited.add(nxt)
                path.append((nxt, action_type))
                if dfs(nxt):
                    return True
                path.pop()
            return False

        if not dfs(start) or not path:
            return None

        return path[0][1]

    def _next_step_toward(self, state: WorldSnapshot, goal: Position) -> WorldActionType | None:
        if self.algorithm == "dfs":
            return self._next_step_dfs(state, goal)
        return self._next_step_bfs(state, goal)

    def choose_action(self, state: WorldSnapshot, agent_id: str) -> WorldAction:
        current_pos = state.agent_position
        exit_pos = state.exit_position
        allowed = set(state.allowed_actions)

        collected = set(state.collected_artifact_ids)
        defeated = set(state.defeated_enemy_ids)

        # 1. Collect an artifact if standing on an uncollected one.
        for artifact in state.level.artifacts:
            if artifact.artifact_id not in collected and artifact.position == current_pos:
                if WorldActionType.COLLECT in allowed:
                    return WorldAction(WorldActionType.COLLECT, target_id=artifact.artifact_id)

        # 2. Engage an adjacent undefeated enemy if allowed.
        for enemy in state.level.enemies:
            if enemy.enemy_id not in defeated and current_pos.manhattan_distance(enemy.position) == 1:
                if WorldActionType.ENGAGE in allowed:
                    return WorldAction(WorldActionType.ENGAGE, target_id=enemy.enemy_id)

        # 3. Exit once at the exit tile.
        if current_pos == exit_pos and WorldActionType.EXIT in allowed:
            return WorldAction(WorldActionType.EXIT)

        # 4. Target nearest remaining artifact first, then the exit.
        remaining_artifacts = [
            a for a in state.level.artifacts if a.artifact_id not in collected
        ]
        if remaining_artifacts:
            target = min(
                remaining_artifacts,
                key=lambda a: current_pos.manhattan_distance(a.position),
            ).position
        else:
            target = exit_pos

        # 5. Find next move toward target using BFS or DFS.
        move_action = self._next_step_toward(state, target)
        if move_action is not None and move_action in allowed:
            return WorldAction(move_action)

        # Fallback to any valid traversable move if blocked.
        for action_type, d_row, d_col in _DIRECTIONS:
            if action_type in allowed:
                nxt = Position(current_pos.row + d_row, current_pos.column + d_col)
                if state.is_traversable(nxt):
                    return WorldAction(action_type)

        return WorldAction.wait()