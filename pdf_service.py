from __future__ import annotations

import re
import shutil
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError


class PdfCutError(Exception):
    """Expected error while reading or splitting a PDF."""


@dataclass(frozen=True)
class PdfInfo:
    page_count: int


def _read_pdf(path: Path) -> PdfReader:
    if not path.is_file():
        raise PdfCutError("O arquivo selecionado não existe.")
    if path.suffix.lower() != ".pdf":
        raise PdfCutError("Selecione um arquivo com extensão .pdf.")
    try:
        reader = PdfReader(str(path), strict=False)
        if reader.is_encrypted and reader.decrypt("") == 0:
            raise PdfCutError("Este PDF está protegido por senha e não pode ser aberto.")
        if len(reader.pages) == 0:
            raise PdfCutError("O PDF não possui páginas.")
        return reader
    except PdfCutError:
        raise
    except (OSError, PdfReadError, ValueError, KeyError) as exc:
        raise PdfCutError(f"Não foi possível ler o PDF: {exc}") from exc


def get_pdf_info(path: Path) -> PdfInfo:
    return PdfInfo(page_count=len(_read_pdf(path).pages))


def _safe_stem(stem: str) -> str:
    cleaned = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", stem).strip(" .")
    return cleaned or "pdf"


def _new_output_dir(root: Path, stem: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    base = root / _safe_stem(stem)
    candidate = base
    index = 2
    while candidate.exists():
        candidate = root / f"{base.name}_{index}"
        index += 1
    candidate.mkdir()
    return candidate


def split_pdf(
    source: Path,
    output_root: Path,
    cancel_event: threading.Event,
    progress_callback: Callable[[int, int], None] | None = None,
) -> Path:
    reader = _read_pdf(source)
    total = len(reader.pages)
    output_dir = _new_output_dir(output_root, source.stem)
    created: list[Path] = []
    try:
        for index, page in enumerate(reader.pages, start=1):
            if cancel_event.is_set():
                raise InterruptedError
            output_path = output_dir / f"{_safe_stem(source.stem)}_pagina_{index:03d}.pdf"
            writer = PdfWriter()
            writer.add_page(page)
            with output_path.open("wb") as stream:
                writer.write(stream)
            created.append(output_path)
            if progress_callback:
                progress_callback(index, total)
        return output_dir
    except InterruptedError:
        raise PdfCutError("Processamento cancelado.")
    except (OSError, ValueError, PdfReadError) as exc:
        raise PdfCutError(f"Não foi possível salvar a página: {exc}") from exc
    finally:
        if cancel_event.is_set() or len(created) != total:
            for output_path in created:
                output_path.unlink(missing_ok=True)
            shutil.rmtree(output_dir, ignore_errors=True)
