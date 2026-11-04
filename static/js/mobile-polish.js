(function () {
  "use strict";
  const mobileView = window.matchMedia("(max-width: 760px)");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function setupTicker(grid) {
    if (!grid || grid.dataset.mobileTickerReady === "true" ||
        !mobileView.matches || reduceMotion.matches) return;

    const cards = Array.from(grid.children).filter((node) =>
      node.classList && node.classList.contains("donor-stat-card")
    );
    if (cards.length < 2) return;

    const track = document.createElement("div");
    track.className = "mobile-ticker-track";
    cards.forEach((card) => track.appendChild(card));

    cards.forEach((card) => {
      const copy = card.cloneNode(true);
      copy.setAttribute("aria-hidden", "true");
      copy.querySelectorAll("[id]").forEach((node) => node.removeAttribute("id"));
      track.appendChild(copy);
    });

    grid.replaceChildren(track);
    grid.classList.add("mobile-ticker");
    track.style.setProperty("--ticker-duration", String(Math.max(14, cards.length * 3.2)) + "s");
    grid.dataset.mobileTickerReady = "true";
  }

  function initialise() {
    if (!mobileView.matches || reduceMotion.matches) return;
    document.querySelectorAll(".donor-public-grid").forEach(setupTicker);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialise, { once: true });
  } else {
    initialise();
  }

  mobileView.addEventListener("change", initialise);
  reduceMotion.addEventListener("change", initialise);
})();