/* EGD 질환 서브탭 — 기관 → 양성/악성 → 질환 칩 */
(function () {
  var host = document.getElementById("dxnav");
  var dataEl = document.getElementById("dx-data");
  if (!host || !dataEl) return;

  var data;
  try {
    data = JSON.parse(dataEl.textContent);
  } catch (e) {
    return;
  }

  var isGeneral = data.nature === "공통";

  /* 표지 배경으로 기관별 색을 살짝 바꾼다 */
  var accent = getComputedStyle(document.documentElement).getPropertyValue("--acc").trim();

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  var bar = el("div", "dxbar");

  /* 브랜드 표기 통일 */
  var brand = document.querySelector(".topbar .brand");
  if (brand) brand.textContent = "Endoscopy Study";

  /* --- 1단: 기관 + 양성/악성 --- */
  var row1 = el("div", "dxrow");
  var organs = el("div", "dxseg");
  organs.appendChild(
    (function () {
      var a = el("a", "dxseg-item" + (isGeneral ? " on" : ""), data.general.label);
      a.href = data.general.file;
      return a;
    })()
  );
  data.organs.forEach(function (o) {
    var a = el("a", "dxseg-item" + (o.label === data.organ ? " on" : ""), o.label);
    a.href = o.label === data.organ ? data.file : data.nature === "악성" ? o.malignant : o.benign;
    organs.appendChild(a);
  });
  row1.appendChild(organs);

  if (!isGeneral) {
    row1.appendChild(el("span", "dxsep", "›"));
    var nature = el("div", "dxseg dxseg-nature");
    ["양성", "악성"].forEach(function (n) {
      var o = data.organs.filter(function (x) { return x.label === data.organ; })[0];
      var file = n === "양성" ? o.benign : o.malignant;
      var a = el("a", "dxseg-item" + (n === data.nature ? " on" : ""), n);
      a.href = file;
      if (n === data.nature) a.setAttribute("aria-current", "page");
      nature.appendChild(a);
    });
    row1.appendChild(nature);
  }

  var home = el("a", "dxhome", "목차");
  home.href = "index.html";
  row1.appendChild(home);

  bar.appendChild(row1);

  /* --- 2단: 질환 칩 --- */
  var chips = el("div", "dxchips");
  if (isGeneral) {
    data.sections.forEach(function (s) {
      var a = el("a", "dxchip", s.title);
      a.href = "#" + s.id;
      chips.appendChild(a);
    });
  } else {
    data.sections.forEach(function (s) {
      var a = el("a", "dxchip" + (s.note ? " has-note" : ""), s.title);
      a.href = "#" + s.id;
      a.dataset.target = s.id;
      chips.appendChild(a);
    });
  }
  bar.appendChild(chips);
  host.appendChild(bar);

  /* --- 활성 칩 표시 --- */
  var links = {};
  chips.querySelectorAll(".dxchip").forEach(function (a) {
    links[a.dataset.target] = a;
  });

  var heads = Array.prototype.slice.call(
    document.querySelectorAll("main h2[id]")
  );

  var current = null;

  function activate(id, scroll) {
    if (current === id) return;
    current = id;
    Object.keys(links).forEach(function (k) {
      links[k].classList.toggle("on", k === id);
    });
    var a = links[id];
    if (a && scroll) {
      var left = a.offsetLeft - chips.clientWidth / 2 + a.offsetWidth / 2;
      chips.scrollTo({ left: Math.max(left, 0), behavior: "smooth" });
    }
  }

  function spy() {
    var y = window.scrollY + 180;
    var hit = heads.length ? heads[0].id : null;
    heads.forEach(function (h) {
      if (h.getBoundingClientRect().top + window.scrollY <= y) hit = h.id;
    });
    if (hit) activate(hit, true);
  }

  window.addEventListener("scroll", spy, { passive: true });
  spy();

  /* --- 인라인 학회노트: 해설 펼치기 --- */
  document.querySelectorAll(".note-inline details").forEach(function (d) {
    d.open = false;
  });

  /* 인쇄 시에는 모든 노트가 펼쳐진 채로 나온다 (book.css @media print) */
})();
