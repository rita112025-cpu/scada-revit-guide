(function () {
  "use strict";

  var STORAGE_KEY = "scada-revit-guide-checklist-v1";

  /* ---- Mobile sidebar toggle ---- */
  var navToggle = document.getElementById("navToggle");
  var sidebar = document.getElementById("sidebar");
  var scrim = document.getElementById("scrim");

  function closeSidebar() {
    sidebar.classList.remove("open");
    scrim.classList.remove("open");
    navToggle.setAttribute("aria-expanded", "false");
  }

  function openSidebar() {
    sidebar.classList.add("open");
    scrim.classList.add("open");
    navToggle.setAttribute("aria-expanded", "true");
  }

  if (navToggle) {
    navToggle.addEventListener("click", function () {
      if (sidebar.classList.contains("open")) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });
  }
  if (scrim) scrim.addEventListener("click", closeSidebar);

  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a"));
  tocLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      if (window.matchMedia("(max-width: 900px)").matches) closeSidebar();
    });
  });

  /* ---- Scrollspy: highlight active TOC link ---- */
  var sections = tocLinks
    .map(function (link) {
      var id = link.getAttribute("href").slice(1);
      var el = document.getElementById(id);
      return el ? { link: link, el: el } : null;
    })
    .filter(Boolean);

  function updateActiveLink() {
    var scrollPos = window.scrollY + 120;
    var current = null;
    sections.forEach(function (s) {
      if (s.el.offsetTop <= scrollPos) current = s;
    });
    tocLinks.forEach(function (l) { l.classList.remove("active"); });
    if (current) current.link.classList.add("active");
  }
  window.addEventListener("scroll", updateActiveLink, { passive: true });
  updateActiveLink();

  /* ---- Checklist persistence ---- */
  var checklistEl = document.getElementById("checklist");
  var progressEl = document.getElementById("checklistProgress");
  var resetBtn = document.getElementById("resetChecklist");
  var checkboxes = checklistEl
    ? Array.prototype.slice.call(checklistEl.querySelectorAll("input[type=checkbox]"))
    : [];

  function loadState() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }

  function saveState(state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      /* private mode / storage blocked: ignore, page still works */
    }
  }

  function refreshRowClass(cb) {
    var li = cb.closest("li");
    if (li) li.classList.toggle("is-checked", cb.checked);
  }

  function updateProgress() {
    if (!progressEl) return;
    var total = checkboxes.length;
    var done = checkboxes.filter(function (cb) { return cb.checked; }).length;
    progressEl.textContent = done + " / " + total;
  }

  function applyState() {
    var state = loadState();
    checkboxes.forEach(function (cb) {
      var key = cb.getAttribute("data-key");
      cb.checked = !!state[key];
      refreshRowClass(cb);
    });
    updateProgress();
  }

  if (checkboxes.length) {
    applyState();
    checkboxes.forEach(function (cb) {
      cb.addEventListener("change", function () {
        var state = loadState();
        state[cb.getAttribute("data-key")] = cb.checked;
        saveState(state);
        refreshRowClass(cb);
        updateProgress();
      });
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      saveState({});
      checkboxes.forEach(function (cb) {
        cb.checked = false;
        refreshRowClass(cb);
      });
      updateProgress();
    });
  }
})();
