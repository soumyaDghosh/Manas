from enum import Enum


class MoodCategory(str, Enum):
    """Enumeration of supported mood categories."""

    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"
    UNDETERMINED = "undetermined"
