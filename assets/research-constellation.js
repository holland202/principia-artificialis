// Provenance: data/dashboard/research_constellation.json.
(() => {
  "use strict";

  const section = document.getElementById("research-constellation");
  if (!section) return;

  const links = Array.from(section.querySelectorAll(".rc-node"));
  const panels = links.map(link => document.getElementById(link.hash.slice(1)));
  if (!links.length || panels.some(panel => !panel)) return;

  function select(selected) {
    links.forEach((link, index) => {
      const active = index === selected;
      if (active) link.setAttribute("aria-current", "true");
      else link.removeAttribute("aria-current");
      panels[index].hidden = !active;
    });
  }

  function followFragment() {
    const selected = links.findIndex(link => link.hash === location.hash);
    if (selected !== -1) select(selected);
  }

  section.classList.add("rc-enhanced");
  select(0);
  followFragment();
  window.addEventListener("hashchange", followFragment);

  links.forEach((link, index) => {
    link.addEventListener("click", event => {
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      event.preventDefault();
      select(index);
      if (location.hash !== link.hash) history.replaceState(null, "", link.hash);
      const heading = panels[index].querySelector("h3");
      heading.focus({ preventScroll: true });
      heading.scrollIntoView({ block: "nearest" });
    });

    panels[index].querySelector(".rc-back").addEventListener("click", event => {
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      event.preventDefault();
      history.replaceState(null, "", "#rc-map");
      link.focus({ preventScroll: true });
      link.scrollIntoView({ block: "nearest" });
    });
  });
})();
