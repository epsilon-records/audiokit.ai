from pydantic import BaseModel


class Metadata(BaseModel):
    """
    Model representing metadata of an audio file.
    """

    id: str
    duration: float
    format: str
    bitrate: int
