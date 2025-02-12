from pydantic import BaseModel


class Audio(BaseModel):
    """
    Model representing an audio file.
    """

    id: str
    file_path: str
    duration: float
    format: str
