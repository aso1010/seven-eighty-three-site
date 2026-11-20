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
    if (scrollY > 0 && scrollY + innerHeight >= document.documentElement.scrollHeight - 1) current = entries.at(-1);
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

/* A single native oscillator. Explicit mute always overrides gesture activation. */
(() => {
  const button = document.querySelector('.carrier-toggle');
  const AudioEngine = window.AudioContext || window.webkitAudioContext;
  if (!button || !AudioEngine) return;

  const preferenceKey = 'lab783CarrierMuted';
  const peak = 0.018;
  const fade = 0.035;
  let muted = false;
  let wanted = false;
  let context;
  let oscillator;
  let gain;
  let revision = 0;
  let quietTimer;

  const readPreference = () => {
    try { return sessionStorage.getItem(preferenceKey) === 'true'; }
    catch { return muted; }
  };
  muted = readPreference();

  const render = () => {
    const on = wanted && context && context.state === 'running';
    const state = muted ? 'OFF' : on ? 'ON' : 'ARMED';
    button.textContent = '[ 783 HZ // ' + state + ' ]';
    button.setAttribute('aria-pressed', String(!!on));
    button.setAttribute('aria-label', button.textContent);
    button.title = state === 'ARMED' ? 'Sound starts on your first interaction. Click to activate.' : state === 'ON' ? 'Mute the 783 Hz carrier.' : 'Activate the 783 Hz carrier.';
  };

  const build = () => {
    if (context) return;
    context = new AudioEngine();
    oscillator = context.createOscillator();
    oscillator.type = 'sine';
    oscillator.frequency.value = 783;
    gain = context.createGain();
    gain.gain.value = 0;
    oscillator.connect(gain);
    gain.connect(context.destination);
    oscillator.start();
    context.addEventListener('statechange', render);
  };

  const ramp = (value) => {
    const now = context.currentTime;
    const parameter = gain.gain;
    if (parameter.cancelAndHoldAtTime) parameter.cancelAndHoldAtTime(now);
    else {
      const current = parameter.value;
      parameter.cancelScheduledValues(now);
      parameter.setValueAtTime(current, now);
    }
    parameter.linearRampToValueAtTime(value, now + fade);
    return now + fade;
  };

  const suspendWhenQuiet = (deadline) => {
    const check = () => {
      if (wanted || !context || context.state !== 'running') return;
      const remaining = deadline - context.currentTime;
      if (remaining > 0) {
        quietTimer = setTimeout(check, remaining * 1000 + 8);
        return;
      }
      context.suspend().catch(() => {});
    };
    quietTimer = setTimeout(check, fade * 1000 + 8);
  };

  const setSound = async (enabled, explicit = false) => {
    if (explicit) {
      muted = !enabled;
      try { sessionStorage.setItem(preferenceKey, String(muted)); } catch {}
    }
    if (enabled && wanted && context && context.state === 'running') {
      render();
      return;
    }
    wanted = enabled;
    const request = ++revision;
    clearTimeout(quietTimer);
    if (!enabled) {
      if (context && context.state === 'running') suspendWhenQuiet(ramp(0));
      render();
      return;
    }
    try {
      build();
      if (context.state !== 'running') await context.resume();
      if (request !== revision || !wanted || muted) return;
      ramp(peak);
    } catch {
      /* A blocked context can retry on the next trusted gesture. */
    }
    render();
  };

  const activate = (event) => {
    if (muted || button.contains(event.target)) return;
    setSound(true);
  };
  document.addEventListener('pointerdown', activate, {capture: true, passive: true});
  document.addEventListener('keydown', activate, {capture: true, passive: true});
  /* Touch activation may become available when the first press is released. */
  document.addEventListener('pointerup', (event) => {
    if (event.pointerType !== 'mouse') activate(event);
  }, {capture: true, passive: true});
  button.addEventListener('click', () => setSound(!wanted, true));

  addEventListener('pagehide', () => {
    wanted = false;
    revision++;
    clearTimeout(quietTimer);
    if (context && context.state === 'running') suspendWhenQuiet(ramp(0));
  });
  addEventListener('pageshow', (event) => {
    if (!event.persisted) return;
    wanted = false;
    revision++;
    muted = readPreference();
    if (context && context.state === 'running') suspendWhenQuiet(ramp(0));
    render();
  });

  button.disabled = false;
  button.closest('.carrier-item').hidden = false;
  render();
})();
