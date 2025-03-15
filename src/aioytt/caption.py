from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class Captions(BaseModel):
    caption_tracks: list[CaptionTrack] = Field(default_factory=list, validation_alias="captionTracks")
    audio_tracks: list[AudioTrack] = Field(default_factory=list, validation_alias="audioTracks")
    default_audio_track_index: int | None = Field(default=None, validation_alias="defaultAudioTrackIndex")


class Name(BaseModel):
    simple_text: str | None = Field(default=None, validation_alias="simpleText")


class CaptionTrack(BaseModel):
    base_url: str | None = Field(default=None, validation_alias="baseUrl")
    name: Name | None = Field(default=None, validation_alias="name")
    vss_id: str | None = Field(default=None, validation_alias="vssId")
    language_code: str | None = Field(default=None, validation_alias="languageCode")
    kind: str | None = Field(default=None, validation_alias="kind")
    is_translatable: bool | None = Field(default=None, validation_alias="isTranslatable")
    track_name: str | None = Field(default=None, validation_alias="trackName")


class AudioTrack(BaseModel):
    caption_track_indices: list[int] = Field(default_factory=list, validation_alias="captionTrackIndices")
    audio_track_id: str | None = Field(default=None, validation_alias="audioTrackId")


class TranslationLanguage(BaseModel):
    language_code: str | None = Field(default=None, validation_alias="languageCode")
    language_name: Name | None = Field(default=None, validation_alias="languageName")
