const API = ""; // same origin (served from /ui by the API)
const q = document.getElementById("q");
const suggestBox = document.getElementById("suggest");
let page = 1, debounce = null;

function checkedValues(id) {
  return [...document.querySelectorAll(`#${id} input:checked`)].map(el => el.value);
}

async function doSearch() {
  const body = {
    query: q.value,
    category: checkedValues("f-cat"),
    brand: checkedValues("f-brand"),
    price_min: null, price_max: null,
    in_stock_only: document.getElementById("f-stock").checked,
    sort: document.getElementById("sort").value,
    page, page_size: 20,
  };
  const pr = document.querySelector('#f-price input:checked');
  if (pr) {
    const [lo, hi] = pr.value.split(":").map(v => v === "" ? null : Number(v));
    body.price_min = lo; body.price_max = hi;
  }
  const r = document.getElementById("f-rating").value;
  if (r) body.min_rating = Number(r);

  const res = await fetch(`${API}/search`, {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body),
  }).then(r => r.json());
  render(res);
}

function render(res) {
  document.getElementById("meta").textContent =
    `${res.total.toLocaleString()} results (${res.took_ms} ms in OpenSearch)`;
  document.getElementById("results").innerHTML = res.hits.map(h => `
    <div class="card">
      <h2>${esc(h.title)}</h2>
      <div class="sub">${esc(h.brand)} · ${esc(h.category)} / ${esc(h.subcategory)}</div>
      <div><span class="price">$${h.price.toFixed(2)}</span>
        <span class="rating">★ ${h.rating} (${h.review_count})</span>
        ${h.in_stock ? "" : '<span class="oos">out of stock</span>'}</div>
    </div>`).join("");
  renderFacets(res.facets);
  const pages = Math.max(1, Math.ceil(res.total / res.page_size));
  document.getElementById("pager").innerHTML = `
    <button id="prev" ${page <= 1 ? "disabled" : ""}>← Prev</button>
    <span>Page ${page} of ${pages}</span>
    <button id="next" ${page >= pages ? "disabled" : ""}>Next →</button>`;
  document.getElementById("prev").onclick = () => { page--; doSearch(); };
  document.getElementById("next").onclick = () => { page++; doSearch(); };
}

function renderFacets(f) {
  document.getElementById("f-cat").innerHTML = f.categories.map(b => `
    <label><input type="checkbox" value="${esc(b.key)}" onchange="resetPage()"> ${esc(b.key)}
    <span class="count">(${b.count})</span></label>`).join("");
  document.getElementById("f-brand").innerHTML = f.brands.slice(0, 12).map(b => `
    <label><input type="checkbox" value="${esc(b.key)}" onchange="resetPage()"> ${esc(b.key)}
    <span class="count">(${b.count})</span></label>`).join("");
  const labels = {"under-25": "Under $25", "25-to-100": "$25 – $100",
                  "100-to-500": "$100 – $500", "over-500": "Over $500"};
  document.getElementById("f-price").innerHTML = f.price_ranges.map(b => `
    <label><input type="radio" name="pr" value="${prVal(b.key)}" onchange="resetPage()">
    ${labels[b.key] || b.key} <span class="count">(${b.count})</span></label>`).join("");
}

function prVal(key) {
  return {"under-25": ":25", "25-to-100": "25:100",
          "100-to-500": "100:500", "over-500": "500:"}[key] || ":";
}
function resetPage() { page = 1; doSearch(); }
function esc(s) { return String(s).replace(/[&<>"']/g, c =>
  ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c])); }

q.addEventListener("input", () => {
  clearTimeout(debounce);
  const v = q.value.trim();
  if (v.length < 2) { suggestBox.classList.add("hidden"); return; }
  debounce = setTimeout(async () => {
    const items = await fetch(`${API}/suggest?q=${encodeURIComponent(v)}`).then(r => r.json());
    if (!items.length) { suggestBox.classList.add("hidden"); return; }
    suggestBox.innerHTML = items.map(s =>
      `<li data-t="${esc(s.title)}">${esc(s.title)} <span class="count">— $${s.price.toFixed(2)}</span></li>`).join("");
    suggestBox.classList.remove("hidden");
    suggestBox.querySelectorAll("li").forEach(li => li.onclick = () => {
      q.value = li.dataset.t; suggestBox.classList.add("hidden"); resetPage();
    });
  }, 200);
});
document.addEventListener("click", e => {
  if (!e.target.closest(".searchbox")) suggestBox.classList.add("hidden");
});
document.getElementById("go").onclick = resetPage;
q.addEventListener("keydown", e => { if (e.key === "Enter") resetPage(); });
document.getElementById("sort").onchange = resetPage;
document.getElementById("f-stock").onchange = resetPage;
document.getElementById("f-rating").onchange = resetPage;

doSearch(); // initial load: match_all browsing
