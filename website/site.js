// Ravengram site behaviour: theme toggle, copy buttons, tabs, guide TOC highlighting.
// Everything degrades to a readable static page when this file doesn't load.

(function () {
  const root = document.documentElement;

  function readTheme() {
    try {
      return localStorage.getItem("theme");
    } catch (e) {
      return null;
    }
  }

  function writeTheme(value) {
    try {
      localStorage.setItem("theme", value);
    } catch (e) {
      /* storage blocked: the toggle still works for this page view */
    }
  }

  const saved = readTheme();
  if (saved === "light" || saved === "dark") root.dataset.theme = saved;

  function currentTheme() {
    if (root.dataset.theme) return root.dataset.theme;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.querySelector("[data-theme-toggle]");
    if (toggle) {
      toggle.addEventListener("click", function () {
        const next = currentTheme() === "dark" ? "light" : "dark";
        root.dataset.theme = next;
        writeTheme(next);
      });
    }

    document.querySelectorAll("[data-copy]").forEach(function (button) {
      button.addEventListener("click", function () {
        const target = document.getElementById(button.dataset.copy);
        if (!target || !navigator.clipboard) return;
        navigator.clipboard.writeText(target.innerText.trim()).then(function () {
          const label = button.textContent;
          button.textContent = "Copied";
          setTimeout(function () {
            button.textContent = label;
          }, 1400);
        });
      });
    });

    document.querySelectorAll("[role=tablist]").forEach(function (list) {
      const tabs = Array.from(list.querySelectorAll("[role=tab]"));
      function select(tab) {
        tabs.forEach(function (t) {
          const on = t === tab;
          t.setAttribute("aria-selected", String(on));
          t.tabIndex = on ? 0 : -1;
          document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
        });
      }
      tabs.forEach(function (tab, i) {
        tab.addEventListener("click", function () {
          select(tab);
        });
        tab.addEventListener("keydown", function (e) {
          let j = null;
          if (e.key === "ArrowRight") j = (i + 1) % tabs.length;
          if (e.key === "ArrowLeft") j = (i - 1 + tabs.length) % tabs.length;
          if (j === null) return;
          e.preventDefault();
          tabs[j].focus();
          select(tabs[j]);
        });
      });
    });

    const tocLinks = Array.from(document.querySelectorAll(".toc a[href^='#']"));
    if (tocLinks.length && "IntersectionObserver" in window) {
      const byId = new Map(tocLinks.map((a) => [a.getAttribute("href").slice(1), a]));
      const observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            tocLinks.forEach((a) => a.classList.remove("active"));
            const link = byId.get(entry.target.id);
            if (link) link.classList.add("active");
          });
        },
        { rootMargin: "-80px 0px -70% 0px" }
      );
      byId.forEach(function (_, id) {
        const el = document.getElementById(id);
        if (el) observer.observe(el);
      });
    }
  });
})();
