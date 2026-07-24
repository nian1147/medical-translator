// Medical Translator - Zotero 7/8/9 Plugin
// Features: selected-text translation, abbreviation lookup
// Requires api_server.py running locally or deployed to Render

var API_BASE = "http://localhost:8765";

// ============================================================
// Plugin object
// ============================================================
var MedicalTranslator = {
  _loaded: false,
  _popup: null,
};

MedicalTranslator.init = function () {
  if (this._loaded) return;
  this._loaded = true;

  Zotero.debug("[Medical Translator] Loaded");

  // Inject toolbar button and register keyboard shortcut
  // in both existing and future main windows
  for (let win of Zotero.getMainWindows()) {
    this._injectUI(win);
  }
};

MedicalTranslator._injectUI = function (win) {
  try {
    // Add keyboard shortcut via Zotero keyset
    let keyset = win.document.getElementById("mainKeyset");
    if (keyset && !win.document.getElementById("med-translator-key")) {
      let key = win.document.createXULElement("key");
      key.setAttribute("id", "med-translator-key");
      key.setAttribute("modifiers", "accel,shift");
      key.setAttribute("key", "T");
      key.addEventListener("command", () => MedicalTranslator.translateSelected());
      keyset.appendChild(key);
    }
  } catch (e) {
    Zotero.debug("[Medical Translator] Key registration failed: " + e);
  }

  // Try to inject a toolbar button
  try {
    let container = win.document.querySelector("#zotero-toolbar")
                 || win.document.querySelector('[class*="toolbar"]');
    if (container && !win.document.getElementById("med-translator-toolbtn")) {
      let btn = win.document.createXULElement("toolbarbutton");
      btn.setAttribute("id", "med-translator-toolbtn");
      btn.setAttribute("label", "Translate");
      btn.setAttribute("tooltiptext", "Medical Translator - Translate selected text (Ctrl+Shift+T)");
      btn.setAttribute("image", "chrome://zotero/skin/16/universal/book_lookup.svg");
      btn.addEventListener("command", () => MedicalTranslator.translateSelected());
      container.appendChild(btn);
    }
  } catch (e) {
    Zotero.debug("[Medical Translator] Toolbar injection failed: " + e);
  }
};

// Get selected text
MedicalTranslator.getSelectedText = function () {
  try {
    let win = Services.wm.getMostRecentWindow("navigator:browser");
    if (!win) return "";
    // Try main browser area
    let sel = win.getSelection().toString().trim();
    if (sel) return sel;
    // Try PDF.js viewer inside iframes
    let viewers = win.document.querySelectorAll(".pdfViewer, #viewerContainer, browser");
    for (let v of viewers) {
      try {
        if (v.contentWindow) {
          sel = v.contentWindow.getSelection().toString().trim();
          if (sel) return sel;
        }
      } catch (e) { /* cross-origin */ }
    }
    return "";
  } catch (e) {
    return "";
  }
};

// Translate selected text
MedicalTranslator.translateSelected = async function () {
  let text = this.getSelectedText();
  if (!text || text.length < 3) {
    this._showPopup("Please select at least 3 characters of English medical text.", "");
    return;
  }

  this._showPopup("Translating...", text);

  try {
    let resp = await Zotero.HTTP.request("POST", API_BASE + "/api/translate", {
      body: JSON.stringify({ text: text }),
      headers: { "Content-Type": "application/json" },
      responseType: "json",
    });

    if (!resp || !resp.response) throw new Error("No response");

    let data = resp.response;
    let content = data.translation || "No translation returned.";

    if (data.abbreviations && data.abbreviations.length > 0) {
      content += "\n\n--- Abbreviations Found ---\n";
      for (let ab of data.abbreviations) {
        content += "[" + ab.abbr + ": " + ab.en + ", " + ab.cn + "]\n";
      }
    }

    this._showPopup(content, text);
  } catch (e) {
    this._showPopup(
      "Translation failed: " + e.message +
      "\n\nMake sure api_server.py is running locally." +
      "\n\ncd medical-translator && python api_server.py",
      text
    );
  }
};

// Show popup
MedicalTranslator._showPopup = function (content, originalText) {
  // Remove old popup
  if (this._popup) {
    try { this._popup.hidePopup(); } catch (e) {}
    this._popup = null;
  }

  try {
    let win = Services.wm.getMostRecentWindow("navigator:browser");
    if (!win) return;

    let panel = win.document.createXULElement("panel");
    panel.setAttribute("id", "medical-translator-popup");
    panel.setAttribute("noautohide", "true");
    panel.setAttribute("level", "floating");
    panel.setAttribute("style", "min-width:450px; max-width:600px; max-height:500px;");

    let vbox = win.document.createXULElement("vbox");
    vbox.setAttribute("style", "padding:16px; font-size:14px; line-height:1.6; overflow-y:auto; max-height:480px;");

    let title = win.document.createXULElement("label");
    title.setAttribute("value", "Medical Translator");
    title.setAttribute("style", "font-weight:bold; font-size:16px; color:#1A5276; margin-bottom:8px;");
    vbox.appendChild(title);

    if (originalText && originalText !== content) {
      let origLabel = win.document.createXULElement("label");
      origLabel.setAttribute("value", "Original:");
      origLabel.setAttribute("style", "font-weight:bold; margin-top:8px;");
      vbox.appendChild(origLabel);

      let origText = win.document.createXULElement("description");
      origText.setAttribute("style", "color:#777; margin-bottom:8px; white-space:pre-wrap; max-height:100px; overflow-y:auto;");
      origText.textContent = originalText.substring(0, 500);
      vbox.appendChild(origText);
    }

    let result = win.document.createXULElement("description");
    result.setAttribute("style", "white-space:pre-wrap;");
    result.textContent = content;
    vbox.appendChild(result);

    let closeBtn = win.document.createXULElement("button");
    closeBtn.setAttribute("label", "Close");
    closeBtn.setAttribute("style", "margin-top:12px;");
    closeBtn.addEventListener("command", () => panel.hidePopup());
    vbox.appendChild(closeBtn);

    panel.appendChild(vbox);
    win.document.documentElement.appendChild(panel);

    panel.openPopup(null, "overlap", win.screen.width / 2 - 250, win.screen.height / 2 - 250);
    this._popup = panel;
  } catch (e) {
    Zotero.debug("[Medical Translator] Popup failed: " + e);
  }
};

// ============================================================
// Zotero Plugin Lifecycle
// ============================================================
function install(data, reason) {
  Zotero.debug("[Medical Translator] Installed");
}

function startup(data, reason) {
  Zotero.debug("[Medical Translator] Startup v" + (data.version || "1.0.0"));
  MedicalTranslator.init();
}

function onMainWindowLoad({ window }) {
  Zotero.debug("[Medical Translator] Main window loaded");
  MedicalTranslator._injectUI(window);
}

function onMainWindowUnload({ window }) {
  Zotero.debug("[Medical Translator] Main window unloaded");
  // Clean up injected elements
  try {
    let btn = window.document.getElementById("med-translator-toolbtn");
    if (btn) btn.remove();
    let key = window.document.getElementById("med-translator-key");
    if (key) key.remove();
  } catch (e) {}
}

function shutdown(data, reason) {
  Zotero.debug("[Medical Translator] Shutdown");

  // Remove popup
  if (MedicalTranslator._popup) {
    try { MedicalTranslator._popup.hidePopup(); } catch (e) {}
    MedicalTranslator._popup = null;
  }
  MedicalTranslator._loaded = false;

  // Clean up all windows
  for (let win of Zotero.getMainWindows()) {
    onMainWindowUnload({ window: win });
  }
}

function uninstall(data, reason) {
  Zotero.debug("[Medical Translator] Uninstalled");
}
