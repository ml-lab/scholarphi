import logging
import os.path
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Iterator, List

from command.command import ArxivBatchCommand, add_one_entity_at_a_time_arg
from common import directories, file_utils
from common.colorize_tex import ColorizedEntity, colorize_equations
from common.types import ArxivId, EquationColorizationRecord, FileContents, RelativePath
from common.unpack import unpack


@dataclass(frozen=True)
class ColorizationTask:
    arxiv_id: ArxivId
    tex_path: RelativePath
    file_contents: FileContents


@dataclass(frozen=True)
class ColorizationResult:
    iteration: int
    tex: str
    colorized_equations: List[ColorizedEntity]


class ColorizeEquations(ArxivBatchCommand[ColorizationTask, ColorizationResult]):
    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        super(ColorizeEquations, ColorizeEquations).init_parser(parser)
        add_one_entity_at_a_time_arg(parser)

    @staticmethod
    def get_name() -> str:
        return "colorize-equations"

    @staticmethod
    def get_description() -> str:
        return "Instrument TeX to colorize equations."

    @staticmethod
    def get_entity_type() -> str:
        return "symbols"

    def get_arxiv_ids_dirkey(self) -> str:
        return "sources"

    def load(self) -> Iterator[ColorizationTask]:
        for arxiv_id in self.arxiv_ids:

            output_root = directories.arxiv_subdir(
                "sources-with-colorized-equations", arxiv_id
            )
            file_utils.clean_directory(output_root)

            original_sources_path = directories.arxiv_subdir("sources", arxiv_id)
            for tex_path in file_utils.find_files(
                original_sources_path, [".tex"], relative=True
            ):
                file_contents = file_utils.read_file_tolerant(
                    os.path.join(original_sources_path, tex_path)
                )
                if file_contents is not None:
                    yield ColorizationTask(arxiv_id, tex_path, file_contents)

    def process(self, item: ColorizationTask) -> Iterator[ColorizationResult]:
        batch_size = 1 if self.args.one_entity_at_a_time else None
        for i, batch in enumerate(
            colorize_equations(item.file_contents.contents, batch_size=batch_size)
        ):
            yield ColorizationResult(i, batch.tex, batch.entities)

    def save(self, item: ColorizationTask, result: ColorizationResult) -> None:
        iteration = result.iteration
        colorized_tex = result.tex
        colorized_equations = result.colorized_equations

        iteration_id = directories.tex_iteration(item.tex_path, str(iteration))
        output_sources_path = directories.iteration(
            "sources-with-colorized-equations", item.arxiv_id, iteration_id,
        )
        logging.debug("Outputting to %s", output_sources_path)

        # Create new directory for each colorization iteration for each TeX file.
        unpack_path = unpack(item.arxiv_id, output_sources_path)
        sources_unpacked = unpack_path is not None
        if unpack_path is None:
            logging.warning("Could not unpack sources into %s", output_sources_path)

        if sources_unpacked:
            tex_path = os.path.join(output_sources_path, item.tex_path)
            with open(tex_path, "w", encoding=item.file_contents.encoding) as tex_file:
                tex_file.write(colorized_tex)

            hues_path = os.path.join(output_sources_path, "equation_hues.csv")
            for c in colorized_equations:
                record = EquationColorizationRecord(
                    arxiv_id=item.arxiv_id,
                    tex_path=item.tex_path,
                    i=c.identifier["index"],
                    iteration=iteration_id,
                    hue=c.hue,
                    tex=c.tex,
                    content_start=c.data["content_start"],
                    content_end=c.data["content_end"],
                    content_tex=c.data["content_tex"],
                    depth=c.data["depth"],
                    start=c.data["start"],
                    end=c.data["end"],
                )
                file_utils.append_to_csv(hues_path, record)
