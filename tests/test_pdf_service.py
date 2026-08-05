from __future__ import annotations

import threading
from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from pdf_service import PdfCutError, get_pdf_info, split_pdf


def make_pdf(path: Path, pages: int) -> None:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    with path.open("wb") as stream:
        writer.write(stream)


def test_get_pdf_info_and_split_pages(tmp_path: Path) -> None:
    source = tmp_path / "relatorio final.pdf"
    make_pdf(source, 3)
    assert get_pdf_info(source).page_count == 3

    output = split_pdf(source, tmp_path / "Downloads", threading.Event())
    files = sorted(output.glob("*.pdf"))
    assert [file.name for file in files] == [
        "relatorio final_pagina_001.pdf",
        "relatorio final_pagina_002.pdf",
        "relatorio final_pagina_003.pdf",
    ]
    assert [len(PdfReader(str(file)).pages) for file in files] == [1, 1, 1]


def test_repeated_processing_uses_a_new_directory(tmp_path: Path) -> None:
    source = tmp_path / "arquivo.pdf"
    make_pdf(source, 1)
    root = tmp_path / "output"
    first = split_pdf(source, root, threading.Event())
    second = split_pdf(source, root, threading.Event())
    assert first.name == "arquivo"
    assert second.name == "arquivo_2"


def test_cancel_removes_partial_output(tmp_path: Path) -> None:
    source = tmp_path / "arquivo.pdf"
    make_pdf(source, 4)
    event = threading.Event()

    def cancel_after_first(current: int, _total: int) -> None:
        if current == 1:
            event.set()

    with pytest.raises(PdfCutError, match="cancelado"):
        split_pdf(source, tmp_path / "output", event, cancel_after_first)
    assert not list((tmp_path / "output").rglob("*.pdf"))


def test_invalid_input_is_rejected(tmp_path: Path) -> None:
    invalid = tmp_path / "arquivo.pdf"
    invalid.write_text("não é um pdf", encoding="utf-8")
    with pytest.raises(PdfCutError):
        get_pdf_info(invalid)


def test_missing_and_non_pdf_inputs_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(PdfCutError, match="não existe"):
        get_pdf_info(tmp_path / "ausente.pdf")
    text_file = tmp_path / "arquivo.txt"
    text_file.write_text("conteúdo", encoding="utf-8")
    with pytest.raises(PdfCutError, match=".pdf"):
        get_pdf_info(text_file)
