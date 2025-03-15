from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class Captions(BaseModel):
    caption_tracks: list[CaptionTrack] = Field(..., validation_alias="captionTracks")
    audio_tracks: list[AudioTrack] = Field(..., validation_alias="audioTracks")
    default_audio_track_index: int = Field(..., validation_alias="defaultAudioTrackIndex")


class Name(BaseModel):
    simple_text: str = Field(..., validation_alias="simpleText")


class CaptionTrack(BaseModel):
    base_url: str = Field(..., validation_alias="baseUrl")
    name: Name = Field(..., validation_alias="name")
    vss_id: str = Field(..., validation_alias="vssId")
    language_code: str = Field(..., validation_alias="languageCode")
    kind: str = Field(..., validation_alias="kind")
    is_translatable: bool = Field(..., validation_alias="isTranslatable")
    track_name: str = Field(..., validation_alias="trackName")


class AudioTrack(BaseModel):
    caption_track_indices: list[int] = Field(..., validation_alias="captionTrackIndices")
    audio_track_id: str = Field(..., validation_alias="audioTrackId")


class TranslationLanguage(BaseModel):
    language_code: str = Field(..., validation_alias="languageCode")
    language_name: Name = Field(..., validation_alias="languageName")
