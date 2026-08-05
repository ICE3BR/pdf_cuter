from __future__ import annotations

import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

from pdf_service import PdfCutError, get_pdf_info, split_pdf


class PdfCuterApp(TkinterDnD.Tk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.selected_path: Path | None = None
        self.cancel_event: threading.Event | None = None
        self.worker: threading.Thread | None = None

        self.title("PDF Cuter")
        self.geometry("620x450")
        self.minsize(560, 400)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._set_root_background("light")
        self._build_ui()

    def _set_root_background(self, mode: str) -> None:
        """Keep the TkinterDnD root background aligned with CustomTkinter."""
        self.configure(bg="#f2f2f2" if mode == "light" else "#1a1a1a")

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=("#f2f2f2", "#1a1a1a"))
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 8))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text="PDF Cuter",
            font=ctk.CTkFont(size=26, weight="bold"),
            fg_color=("#f2f2f2", "#1a1a1a"),
        ).grid(
            row=0, column=0, sticky="w"
        )
        self.theme_switch = ctk.CTkSwitch(
            header,
            text="Modo escuro",
            command=self._toggle_theme,
            onvalue=1,
            offvalue=0,
            bg_color=("#f2f2f2", "#1a1a1a"),
        )
        self.theme_switch.grid(row=0, column=1, padx=(12, 0))

        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=28, pady=8)
        content.grid_columnconfigure(0, weight=1)

        self.drop_area = ctk.CTkFrame(content, height=125, corner_radius=12)
        self.drop_area.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
        self.drop_area.grid_propagate(False)
        self.drop_area.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.drop_area, text="Selecione ou arraste um arquivo PDF", font=ctk.CTkFont(size=16)).grid(
            row=0, column=0, pady=(22, 10)
        )
        ctk.CTkButton(self.drop_area, text="Selecionar PDF", width=160, command=self._choose_file).grid(
            row=1, column=0
        )
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self._on_drop)

        self.file_info = ctk.CTkEntry(content, placeholder_text="Nenhum PDF selecionado", state="disabled")
        self.file_info.grid(row=1, column=0, sticky="ew", padx=24, pady=12)

        self.progress = ctk.CTkProgressBar(content)
        self.progress.grid(row=2, column=0, sticky="ew", padx=24, pady=(12, 4))
        self.progress.set(0)
        self.status = ctk.CTkLabel(content, text="Pronto para começar", anchor="w")
        self.status.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 18))

        buttons = ctk.CTkFrame(content, fg_color="transparent")
        buttons.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 24))
        buttons.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(buttons, text="Ajuda", width=100, command=self._show_help).grid(row=0, column=0, sticky="w")
        self.cancel_button = ctk.CTkButton(buttons, text="Cancelar", width=110, state="disabled", command=self._cancel)
        self.cancel_button.grid(row=0, column=1, padx=8)
        self.execute_button = ctk.CTkButton(buttons, text="Executar", width=130, command=self._execute)
        self.execute_button.grid(row=0, column=2)

    def _toggle_theme(self) -> None:
        mode = "dark" if self.theme_switch.get() else "light"
        ctk.set_appearance_mode(mode)
        self._set_root_background(mode)

    def _choose_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")])
        if path:
            self._load_pdf(Path(path))

    def _on_drop(self, event: tk.Event) -> None:
        paths = self.tk.splitlist(event.data)
        if paths:
            self._load_pdf(Path(paths[0]))

    def _load_pdf(self, path: Path) -> None:
        try:
            info = get_pdf_info(path)
        except (OSError, PdfCutError, ValueError) as exc:
            self._set_info("")
            messagebox.showerror("PDF inválido", str(exc), parent=self)
            return
        self.selected_path = path
        self._set_info(f"{path.name} — {info.page_count} página(s)")
        self.status.configure(text="PDF carregado. Pronto para executar.")

    def _set_info(self, value: str) -> None:
        self.file_info.configure(state="normal")
        self.file_info.delete(0, "end")
        if value:
            self.file_info.insert(0, value)
        self.file_info.configure(state="disabled")

    def _execute(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        if self.selected_path is None:
            messagebox.showwarning("Selecione um PDF", "Escolha um arquivo PDF antes de executar.", parent=self)
            return
        self.cancel_event = threading.Event()
        self.worker = threading.Thread(target=self._run_split, args=(self.selected_path, self.cancel_event), daemon=True)
        self._set_running(True)
        self.worker.start()

    def _run_split(self, source: Path, cancel_event: threading.Event) -> None:
        try:
            output = split_pdf(source, Path.home() / "Downloads" / "PDF_CUTER_RESULT", cancel_event, self._progress)
        except Exception as exc:  # noqa: BLE001 - forwarded safely to the GUI
            self.after(0, self._finished, False, str(exc))
        else:
            message = "Processamento cancelado." if cancel_event.is_set() else f"Concluído: {output}"
            self.after(0, self._finished, not cancel_event.is_set(), message)

    def _progress(self, current: int, total: int) -> None:
        self.after(0, lambda: (self.progress.set(current / total), self.status.configure(text=f"Processando página {current} de {total}...")))

    def _cancel(self) -> None:
        if self.cancel_event:
            self.cancel_event.set()
            self.status.configure(text="Cancelando...")
            self.cancel_button.configure(state="disabled")

    def _set_running(self, running: bool) -> None:
        self.execute_button.configure(state="disabled" if running else "normal")
        self.cancel_button.configure(state="normal" if running else "disabled")

    def _finished(self, success: bool, message: str) -> None:
        self._set_running(False)
        self.progress.set(1 if success else 0)
        self.status.configure(text=message)
        if success:
            messagebox.showinfo("PDF Cuter", message, parent=self)
        elif message != "Processamento cancelado.":
            messagebox.showerror("Erro", message, parent=self)

    def _show_help(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Ajuda")
        dialog.geometry("360x220")
        dialog.resizable(False, False)
        dialog.transient(self)
        ctk.CTkLabel(dialog, text="PDF Cuter", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(24, 12))
        ctk.CTkLabel(dialog, text="Criado por Gustavo de Amorim Quinup").pack(pady=4)
        self.help_link = ctk.CTkLabel(
            dialog,
            text="me.gaqtech.dev",
            text_color=("#1f6aa5", "#5da9e9"),
            cursor="hand2",
        )
        self.help_link.pack(pady=4)
        self.help_link.bind("<Button-1>", lambda _event: webbrowser.open_new_tab("https://me.gaqtech.dev"))
        self.help_link.bind(
            "<Enter>", lambda _event: self.help_link.configure(text_color=("#15527f", "#8bc7f5"))
        )
        self.help_link.bind(
            "<Leave>", lambda _event: self.help_link.configure(text_color=("#1f6aa5", "#5da9e9"))
        )
        ctk.CTkButton(dialog, text="Fechar", width=100, command=dialog.destroy).pack(pady=20)

    def _on_close(self) -> None:
        if self.worker and self.worker.is_alive() and self.cancel_event:
            self.cancel_event.set()
            self.after(100, self._on_close)
            return
        self.destroy()


def main() -> None:
    app = PdfCuterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
