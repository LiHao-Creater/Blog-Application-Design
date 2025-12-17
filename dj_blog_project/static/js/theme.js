(function () {
  const KEY = "theme";

  function applyTheme(theme) {
    const t = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", t);
    document.documentElement.setAttribute("data-bs-theme", t); // Bootstrap 5.3
    localStorage.setItem(KEY, t);
  }

  function getInitialTheme() {
    const saved = localStorage.getItem(KEY);
    if (saved === "dark" || saved === "light") return saved;

    // 跟随系统
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  }

  document.addEventListener("DOMContentLoaded", () => {
    applyTheme(getInitialTheme());

    const btn = document.getElementById("themeToggle");
    if (btn) {
      btn.addEventListener("click", () => {
        const cur = document.documentElement.getAttribute("data-theme") || "light";
        applyTheme(cur === "dark" ? "light" : "dark");
      });
    }
  });
})();
