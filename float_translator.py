"""
桌面悬浮翻译窗 — 配合 Zotero 或任何 PDF 阅读器使用
用法：
1. 先启动 api_server.py
2. 再启动本脚本：python float_translator.py
3. 在 Zotero/PDF里选中英文 → Ctrl+C → 翻译窗自动显示结果
"""
import sys, io, os, json, threading, time
import tkinter as tk
import requests

# UTF-8
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

API = "http://127.0.0.1:8765"

# ============================================================
class FloatingTranslator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Medical Translator")
        self.root.geometry("480x400+100+100")
        self.root.attributes("-topmost", True)  # 始终置顶
        self.root.configure(bg="#1A5276")

        # 标题栏
        title = tk.Label(
            self.root, text="🩺 Medical Translator",
            font=("Microsoft YaHei", 14, "bold"),
            bg="#1A5276", fg="white",
        )
        title.pack(fill=tk.X, padx=2, pady=(4, 0))

        # 原文区
        tk.Label(
            self.root, text="📄 Source (Paste or auto-detect clipboard)",
            font=("Microsoft YaHei", 10), bg="#1A5276", fg="#AED6F1",
            anchor="w",
        ).pack(fill=tk.X, padx=8)

        self.source_text = tk.Text(
            self.root, height=6, wrap=tk.WORD,
            font=("Calibri", 12), bg="#F8F9FA", fg="#333",
            relief=tk.FLAT, padx=6, pady=6,
        )
        self.source_text.pack(fill=tk.BOTH, expand=False, padx=8, pady=4)

        # 按钮行
        btn_frame = tk.Frame(self.root, bg="#1A5276")
        btn_frame.pack(fill=tk.X, padx=8, pady=2)

        tk.Button(
            btn_frame, text="🔄 Translate", font=("Microsoft YaHei", 10, "bold"),
            bg="#2E86C1", fg="white", relief=tk.FLAT,
            padx=12, pady=4, cursor="hand2",
            command=self.do_translate,
        ).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(
            btn_frame, text="📋 Paste & Translate", font=("Microsoft YaHei", 10),
            bg="#27AE60", fg="white", relief=tk.FLAT,
            padx=12, pady=4, cursor="hand2",
            command=self.paste_and_translate,
        ).pack(side=tk.LEFT, padx=(0, 6))

        tk.Button(
            btn_frame, text="🗑 Clear", font=("Microsoft YaHei", 10),
            bg="#7F8C8D", fg="white", relief=tk.FLAT,
            padx=12, pady=4, cursor="hand2",
            command=self.clear_all,
        ).pack(side=tk.LEFT)

        # 译文区
        tk.Label(
            self.root, text="📝 Translation",
            font=("Microsoft YaHei", 10), bg="#1A5276", fg="#AED6F1",
            anchor="w",
        ).pack(fill=tk.X, padx=8)

        self.result_text = tk.Text(
            self.root, height=10, wrap=tk.WORD,
            font=("Microsoft YaHei", 12), bg="white", fg="#333",
            relief=tk.FLAT, padx=6, pady=6,
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # 状态栏
        self.status = tk.Label(
            self.root, text="Ready. Select English text in PDF -> Ctrl+C -> Click Translate",
            font=("Microsoft YaHei", 9), bg="#154360", fg="#AED6F1",
            anchor="w",
        )
        self.status.pack(fill=tk.X, padx=2, pady=(0, 2))

        # 快捷键
        self.root.bind("<Control-Return>", lambda e: self.do_translate())
        self.root.bind("<Control-v>", lambda e: self.paste_and_translate())

        # 关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 定时检查剪贴板
        self._last_clipboard = ""
        self._check_clipboard()

        self.running = True

    def _check_clipboard(self):
        """每2秒检查剪贴板，自动填入新复制的英文"""
        if not self.running:
            return
        try:
            clip = self.root.clipboard_get()
            if clip and clip != self._last_clipboard and len(clip) > 20:
                # Check if it looks like English
                ascii_chars = sum(1 for c in clip if ord(c) < 128)
                if ascii_chars / max(len(clip), 1) > 0.7:
                    self._last_clipboard = clip
                    self.source_text.delete("1.0", tk.END)
                    self.source_text.insert("1.0", clip)
                    self.status.config(text="Clipboard detected! Click Translate (Ctrl+Enter)")
        except Exception:
            pass
        if self.running:
            self.root.after(2000, self._check_clipboard)

    def paste_and_translate(self):
        try:
            clip = self.root.clipboard_get()
            if clip:
                self.source_text.delete("1.0", tk.END)
                self.source_text.insert("1.0", clip)
        except Exception:
            pass
        self.do_translate()

    def do_translate(self):
        text = self.source_text.get("1.0", tk.END).strip()
        if not text or len(text) < 3:
            self.status.config(text="Please enter at least 3 characters")
            return

        self.status.config(text="Translating...")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "Translating...")
        self.root.update()

        def _translate():
            try:
                resp = requests.post(
                    f"{API}/api/translate",
                    json={"text": text},
                    timeout=60,
                )
                data = resp.json()
                if resp.status_code == 200:
                    result = data.get("translation", "")
                    if data.get("abbreviations"):
                        result += "\n\n=== Abbreviations ===\n"
                        for ab in data["abbreviations"]:
                            result += f"[{ab['abbr']}: {ab['en']}, {ab['cn']}]\n"
                    self.root.after(0, lambda: self._show_result(result))
                else:
                    msg = data.get("error", str(resp.status_code))
                    self.root.after(0, lambda: self._show_error(msg))
            except Exception as e:
                self.root.after(0, lambda: self._show_error(str(e)))

        threading.Thread(target=_translate, daemon=True).start()

    def _show_result(self, text):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", text)
        self.status.config(text="Done! Select new text -> Ctrl+C -> Click Translate")

    def _show_error(self, msg):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", f"Error: {msg}\n\nMake sure api_server.py is running.")
        self.status.config(text="Error - check api_server.py is running")

    def clear_all(self):
        self.source_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)
        self._last_clipboard = ""
        self.status.config(text="Cleared")

    def on_close(self):
        self.running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    print("[Floating Translator] Starting...")
    print("  Tips: Select text in Zotero -> Ctrl+C -> switch to this window -> Ctrl+Enter")
    print("  Or: Paste text and click Translate")
    app = FloatingTranslator()
    app.run()
