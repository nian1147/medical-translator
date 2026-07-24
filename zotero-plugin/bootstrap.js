// Medical Translator - Zotero 7 Plugin
// Features: selected-text translation, abbreviation lookup
// Requires api_server.py running locally or deployed to Render

const API_BASE = "http://localhost:8765";
// Change to your Render URL if deployed: const API_BASE = "https://your-app.onrender.com";

var MedicalTranslator = {
  _loaded: false,
  _popup: null,
};

MedicalTranslator.init = function () {
  if (this._loaded) return;
  this._loaded = true;
  Zotero.debug("[Medical Translator] Plugin loaded");

  // Add right-click menu items
  this._addContextMenu();

  // Add keyboard shortcut: Ctrl+Shift+T
  this._addShortcut();

  // Inject toolbar button into PDF reader
  this._injectToolbarButton();
};

// Right-click context menu
MedicalTranslator._addContextMenu = function () {
  // Zotero 7 uses item pane context menu
  // We hook into the reader selection context menu
  document.addEventListener("contextmenu", function(e) {
    let selection = window.getSelection().toString().trim();
    if (!selection || selection.length < 3) return;
    // Menu items are dynamically shown based on text selection
  });
};

// Keyboard shortcut
MedicalTranslator._addShortcut = function () {
  document.addEventListener("keydown", function(e) {
    if (e.ctrlKey && e.shiftKey && e.key === "T") {
      e.preventDefault();
      MedicalTranslator.translateSelected();
    }
  });
};

// Inject toolbar button
MedicalTranslator._injectToolbarButton = function () {
  let attempts = 0;
  let interval = setInterval(function() {
    attempts++;
    // Try to find Zotero's toolbar area
    let toolbar = document.querySelector(".zotero-view-toolbar")
               || document.querySelector("#zotero-toolbar")
               || document.querySelector('[class*="toolbar"]');

    if (toolbar && !document.getElementById("med-translator-btn")) {
      let div = document.createElement("div");
      div.id = "med-translator-btn";
      div.innerHTML = '<button style="padding:4px 12px;cursor:pointer;background:#2E86C1;color:white;border:none;border-radius:4px;font-size:13px;">Translate</button>';
      div.querySelector("button").onclick = function() { MedicalTranslator.translateSelected(); };
      div.querySelector("button").title = "Medical Translator - Translate selected text (Ctrl+Shift+T)";
      toolbar.appendChild(div);
      clearInterval(interval);
    }
    if (attempts > 30) clearInterval(interval);
  }, 1000);
};

// Get selected text from PDF reader or any element
MedicalTranslator.getSelectedText = function () {
  let text = window.getSelection().toString().trim();
  // Also try PDF.js viewer
  if (!text) {
    let viewer = document.querySelector(".pdfViewer") || document.querySelector("#viewerContainer");
    if (viewer && viewer.contentWindow) {
      text = viewer.contentWindow.getSelection().toString().trim();
    }
  }
  return text;
};

// Translate selected text
MedicalTranslator.translateSelected = async function () {
  let text = this.getSelectedText();
  if (!text || text.length < 3) {
    alert("[Medical Translator] Please select at least 3 characters of English text first.");
    return;
  }

  // Show loading popup
  this._showPopup("Translating...", text);

  try {
    let resp = await fetch(API_BASE + "/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text }),
    });

    if (!resp.ok) {
      let err = await resp.text();
      throw new Error("HTTP " + resp.status + ": " + err);
    }

    let data = await resp.json();
    let content = data.translation || "No translation returned.";

    // Append abbreviations
    if (data.abbreviations && data.abbreviations.length > 0) {
      content += "\n\n--- Abbreviations Found ---\n";
      for (let ab of data.abbreviations) {
        content += "[" + ab.abbr + ": " + ab.full_en + ", " + ab.cn + "]\n";
      }
    }

    this._showPopup(content, text);
  } catch (e) {
    let msg = "Translation failed: " + e.message;
    msg += "\n\nMake sure api_server.py is running (python api_server.py)";
    this._showPopup(msg, text);
  }
};

// Lookup abbreviation or term
MedicalTranslator.lookupSelected = async function () {
  let text = this.getSelectedText();
  if (!text) {
    text = prompt("Enter medical abbreviation or term to lookup:", "");
    if (!text) return;
  }

  this._showPopup("Looking up: " + text, "");

  try {
    let resp = await fetch(API_BASE + "/api/lookup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: text }),
    });

    if (!resp.ok) throw new Error("HTTP " + resp.status);

    let data = await resp.json();
    let content = "Query: " + data.query + "\n\n";

    if (data.local_results && data.local_results.length > 0) {
      content += "=== Local Library Match ===\n";
      for (let r of data.local_results) {
        if (r.abbr) content += "[" + r.abbr + "] " + r.full_en + " -> " + r.cn + "\n";
        else if (r.en) content += r.en + " -> " + r.cn + "\n";
        else if (r.cn) content += r.cn + " -> " + r.full_en + " (" + r.abbr + ")\n";
      }
    }

    if (data.ai_result) {
      content += "\n=== AI Supplement ===\n" + data.ai_result;
    }

    this._showPopup(content, text);
  } catch (e) {
    this._showPopup("Lookup failed: " + e.message, text);
  }
};

// Show result popup
MedicalTranslator._showPopup = function (content, originalText) {
  // Remove old popup
  if (this._popup) {
    this._popup.remove();
    this._popup = null;
  }

  let popup = document.createElement("div");
  popup.id = "medical-translator-popup";
  popup.style.cssText = `
    position: fixed; top: 10%; left: 50%; transform: translateX(-50%);
    width: 520px; max-height: 70vh; background: #fff; border: 2px solid #2E86C1;
    border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.2);
    z-index: 999999; padding: 20px; font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px; line-height: 1.7; overflow-y: auto; color: #333;
  `;

  let html = '<h3 style="margin:0 0 4px 0;color:#1A5276;">Medical Translator</h3>';

  if (originalText && originalText !== content) {
    html += '<div style="margin-bottom:12px;color:#777;font-size:12px;max-height:80px;overflow-y:auto;word-wrap:break-word;">'
         + '<b>Original:</b> ' + MedicalTranslator._escapeHTML(originalText.substring(0, 400))
         + '</div>';
  }

  html += '<pre style="white-space:pre-wrap;word-wrap:break-word;font-family:inherit;margin:0;">'
        + MedicalTranslator._escapeHTML(content)
        + '</pre>';

  html += '<button onclick="document.getElementById(\'medical-translator-popup\').remove();" '
        + 'style="margin-top:12px;padding:6px 16px;background:#E74C3C;color:#fff;border:none;border-radius:6px;cursor:pointer;">Close</button>';

  popup.innerHTML = html;
  document.body.appendChild(popup);
  this._popup = popup;

  // Click outside to close
  setTimeout(() => {
    document.addEventListener("click", function closePopup(e) {
      if (!popup.contains(e.target)) {
        popup.remove();
        document.removeEventListener("click", closePopup);
      }
    });
  }, 100);
};

MedicalTranslator._escapeHTML = function (str) {
  let div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
};

// ============================================================
// Zotero 7 Bootstrap Lifecycle
// ============================================================
function install() {
  Zotero.debug("[Medical Translator] Installed");
}

function startup({ id, version, resourceURI, rootURI }) {
  Zotero.debug("[Medical Translator] Starting v" + version);
  MedicalTranslator.init();
}

function shutdown() {
  Zotero.debug("[Medical Translator] Shutting down");
  if (MedicalTranslator._popup) MedicalTranslator._popup.remove();
  MedicalTranslator._loaded = false;
  let btn = document.getElementById("med-translator-btn");
  if (btn) btn.remove();
}

function uninstall() {
  Zotero.debug("[Medical Translator] Uninstalled");
}
