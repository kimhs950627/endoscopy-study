/* EndoTODAY 참고서 — TOC builder + scrollspy + back-to-top */
(function () {
  function slug(s) {
    return s.trim().toLowerCase().replace(/[^\w가-힣]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60);
  }
  var main = document.querySelector("main");
  if (!main) return;
  var heads = main.querySelectorAll("h2, h3");
  var toc = document.getElementById("toc");
  var links = [];
  heads.forEach(function (h, i) {
    if (!h.id) {
      var base = slug(h.textContent) || ("sec-" + i);
      var id = base, k = 2;
      while (document.getElementById(id)) { id = base + "-" + k++; }
      h.id = id;
    }
    if (toc) {
      var a = document.createElement("a");
      a.href = "#" + h.id;
      a.textContent = h.textContent;
      a.className = h.tagName === "H2" ? "h2" : "h3";
      toc.appendChild(a);
      links.push(a);
    }
  });
  function spy() {
    var y = window.scrollY + 90, cur = null;
    heads.forEach(function (h) {
      if (h.getBoundingClientRect().top + window.scrollY <= y) cur = h.id;
    });
    links.forEach(function (a) { a.classList.toggle("active", a.getAttribute("href") === "#" + cur); });
  }
  window.addEventListener("scroll", spy, { passive: true });
  spy();
  var btn = document.getElementById("totop");
  if (btn) btn.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
})();
