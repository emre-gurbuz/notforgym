// NotForGym sitesi — tek ayar dosyası. Yayından önce aşağıdaki iki değeri doldur.
const SITE = {
  // Destek e-postası (uygulamadaki AppLinks.supportEmail ile aynı olmalı).
  supportEmail: "",
  // App Store bağlantısı; boşken düğme "Yakında" olarak görünür.
  // Örnek: "https://apps.apple.com/app/id1234567890"
  appStoreURL: "",
};

(function () {
  const KEY = "nfg-lang";
  const SUPPORTED = ["en", "tr", "de", "es", "pt-br", "fr", "it", "ja"];
  const current = document.documentElement.lang.toLowerCase();

  // İngilizce sayfalar kökte durur. Kökteki bir sayfaya ilk kez gelen ziyaretçiyi
  // daha önce seçtiği ya da tarayıcısının diline yönlendir. Diğer dillerdeki
  // bağlantılar paylaşılabilsin diye orada yönlendirme yapılmaz.
  // Safari dosyadan (file://) açılınca localStorage hata verebilir; site yine çalışsın.
  const store = {
    get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
    set: (k, v) => { try { localStorage.setItem(k, v); } catch {} },
  };

  function preferred() {
    const saved = store.get(KEY);
    if (SUPPORTED.includes(saved)) return saved;
    for (const raw of navigator.languages || [navigator.language || "en"]) {
      const l = raw.toLowerCase();
      if (l === "pt-br" || l.startsWith("pt")) return "pt-br";
      const base = l.split("-")[0];
      if (SUPPORTED.includes(base)) return base;
    }
    return "en";
  }
  if (current === "en" && !document.documentElement.hasAttribute("data-noredirect")) {
    const want = preferred();
    const alt = want !== "en" && document.querySelector(`link[rel="alternate"][hreflang="${want === "pt-br" ? "pt-BR" : want}"]`);
    if (alt) {
      location.replace(alt.getAttribute("href") + location.hash);
      return;
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".lang-select").forEach((sel) =>
      sel.addEventListener("change", () => {
        const opt = sel.selectedOptions[0];
        store.set(KEY, opt.value);
        location.href = opt.dataset.href;
      })
    );

    // E-posta adresini yerleştir.
    document.querySelectorAll(".js-email").forEach((el) => {
      if (!SITE.supportEmail) return;
      el.textContent = SITE.supportEmail;
      if (el.tagName === "A") el.href = "mailto:" + SITE.supportEmail;
    });
    document.querySelectorAll(".js-mail-btn").forEach((el) => {
      if (SITE.supportEmail) el.href = "mailto:" + SITE.supportEmail + "?subject=NotForGym";
    });

    // App Store düğmesi.
    document.querySelectorAll(".store-btn").forEach((el) => {
      if (SITE.appStoreURL) {
        el.href = SITE.appStoreURL;
        el.removeAttribute("aria-disabled");
        el.querySelectorAll(".soon").forEach((s) => s.remove());
      } else {
        el.querySelectorAll(".live").forEach((s) => s.remove());
      }
    });

    document.querySelectorAll(".js-year").forEach((el) => (el.textContent = new Date().getFullYear()));
  });
})();
