from typing import Optional, cast

from common.types import BoundingBox, EntityInformation, PaperProcessingResult
from common.upload_entities import upload_entities

from .types import Sentence as SentenceEntity


def upload_sentences(
    processing_summary: PaperProcessingResult, data_version: Optional[int]
) -> None:

    entity_infos = []
    for entity_and_location in processing_summary.localized_entities:
        sentence = cast(SentenceEntity, entity_and_location.entity)
        boxes = [cast(BoundingBox, l) for l in entity_and_location.locations]

        entity_info = EntityInformation(
            id_=f"{sentence.tex_path}-{sentence.id_}",
            type_="sentence",
            bounding_boxes=boxes,
            data={
                "text": sentence.text,
                "tex": sentence.tex,
                "tex_start": sentence.start,
                "tex_end": sentence.end,
            },
        )
        entity_infos.append(entity_info)

    upload_entities(
        processing_summary.s2_id,
        processing_summary.arxiv_id,
        entity_infos,
        data_version,
    )
