/* Native anchors own navigation and history; this index only observes position. */
(() => {
  const nav = document.querySelector('.page-index');
  if (!nav) return;
  const links = [...nav.querySelectorAll('ol a[href^="#"]')];
  const entries = links.map(link => ({link, target: document.getElementById(decodeURIComponent(link.hash.slice(1)))})).filter(entry => entry.target);
  let scheduled = false;
  const update = () => {
    scheduled = false;
    const boundary = nav.getBoundingClientRect().height + innerHeight * .21;
    let current = entries[0];
    for (const entry of entries) if (entry.target.getBoundingClientRect().top <= boundary) current = entry;
    for (const entry of entries) {
      if (entry === current) {
        if (!entry.link.hasAttribute('aria-current')) {
          entry.link.setAttribute('aria-current', 'location');
          const list = nav.querySelector('ol');
          const item = entry.link.getBoundingClientRect();
          const frame = list.getBoundingClientRect();
          if (item.left < frame.left) list.scrollLeft -= frame.left - item.left + 4;
          else if (item.right > frame.right) list.scrollLeft += item.right - frame.right + 4;
        }
      } else entry.link.removeAttribute('aria-current');
    }
  };
  const schedule = () => {
    if (!scheduled) { scheduled = true; requestAnimationFrame(update); }
  };
  addEventListener('scroll', schedule, {passive: true});
  addEventListener('resize', schedule);
  addEventListener('pageshow', schedule);
  addEventListener('hashchange', schedule);
  document.fonts.ready.then(schedule);
  schedule();
})();
