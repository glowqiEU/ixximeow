from enum import IntEnum


class AutonomyLevel(IntEnum):
    OBSERVE = 0
    PROPOSE = 1
    PREPARE = 2
    EXECUTE = 3
    PUBLISH = 4


def can_execute(current_level: AutonomyLevel, required_level: AutonomyLevel) -> bool:
    return current_level >= required_level


def requires_approval(
    current_level: AutonomyLevel,
    required_level: AutonomyLevel,
) -> bool:
    return not can_execute(current_level, required_level)
