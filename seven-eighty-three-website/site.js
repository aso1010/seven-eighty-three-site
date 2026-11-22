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

/* One native oscillator with separate frequency and sound controls. */
(() => {
  const button = document.querySelector('.carrier-toggle');
  const frequencyButton = document.querySelector('.carrier-frequency');
  const AudioEngine = window.AudioContext || window.webkitAudioContext;
  if (!button || !frequencyButton || !AudioEngine) return;
  const key = 'lab783CarrierMode';
  const frequencyKey = 'lab783CarrierFrequency';
  let frequency = 7.83;
  const readFrequency = () => {
    try { return sessionStorage.getItem(frequencyKey) === '783' ? 783 : 7.83; }
    catch { return frequency; }
  };
  const peak = 0.018;
  const fade = 0.035;
  let mode = 0;
  let wanted = false;
  let context, oscillator, gain, quietTimer;
  let revision = 0;
  const readMode = () => {
    try {
      const value = sessionStorage.getItem(key);
      if (['0', '7.83', '783'].includes(value)) return Number(value);
      if (sessionStorage.getItem('lab783CarrierMuted') === 'false') {
        return sessionStorage.getItem('lab783CarrierFrequency') === '7.83' ? 7.83 : 783;
      }
      return 0;
    } catch { return mode; }
  };
  mode = readMode();
  frequency = mode || readFrequency();
  const render = () => {
    button.textContent = mode ? '[ SOUND: ON ]' : '[ SOUND: OFF ]';
    button.setAttribute('aria-pressed', String(!!mode));
    button.setAttribute('aria-label', mode ? 'Turn sound off' : 'Turn sound on at ' + frequency + ' Hz');
    button.title = 'Toggle sound on or off. Selected sound resumes on your next interaction after navigation.';
    frequencyButton.textContent = '[ FREQUENCY: ' + frequency + ' HZ ]';
    frequencyButton.setAttribute('aria-label', 'Switch frequency to ' + (frequency === 7.83 ? 783 : 7.83) + ' Hz');
    frequencyButton.title = 'Switch between 7.83 Hz and 783 Hz without changing sound on or off.';
  };
  const ramp = value => {
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
  const suspendWhenQuiet = deadline => {
    const check = () => {
      if (wanted || !context || context.state !== 'running') return;
      const remaining = deadline - context.currentTime;
      if (remaining > 0) { quietTimer = setTimeout(check, remaining * 1000 + 8); return; }
      context.suspend().catch(() => {});
    };
    quietTimer = setTimeout(check, fade * 1000 + 8);
  };
  const applyMode = async () => {
    const request = ++revision;
    clearTimeout(quietTimer);
    wanted = mode !== 0;
    render();
    if (!wanted) {
      if (context && context.state === 'running') suspendWhenQuiet(ramp(0));
      return;
    }
    try {
      if (!context) {
        context = new AudioEngine();
        oscillator = context.createOscillator();
        oscillator.type = 'sine';
        oscillator.frequency.value = mode;
        gain = context.createGain();
        gain.gain.value = 0;
        oscillator.connect(gain);
        gain.connect(context.destination);
        oscillator.start();
        context.addEventListener('statechange', render);
      }
      if (context.state !== 'running') await context.resume();
      if (request !== revision || !wanted || !mode) return;
      const now = context.currentTime;
      const current = oscillator.frequency.value;
      oscillator.frequency.cancelScheduledValues(now);
      oscillator.frequency.setValueAtTime(current, now);
      if (current !== mode && gain.gain.value > 0) {
        const deadline = ramp(0);
        oscillator.frequency.setValueAtTime(mode, deadline);
        gain.gain.linearRampToValueAtTime(peak, deadline + fade);
      } else {
        oscillator.frequency.setValueAtTime(mode, now);
        ramp(peak);
      }
    } catch { /* Retry after the next trusted interaction. */ }
    render();
  };
  button.addEventListener('click', () => {
    mode = mode ? 0 : frequency;
    try { sessionStorage.setItem(key, String(mode)); } catch {}
    applyMode();
  });
  frequencyButton.addEventListener('click', () => {
    frequency = frequency === 7.83 ? 783 : 7.83;
    try { sessionStorage.setItem(frequencyKey, String(frequency)); } catch {}
    if (mode) {
      mode = frequency;
      try { sessionStorage.setItem(key, String(mode)); } catch {}
      applyMode();
    } else render();
  });
  const activate = event => {
    if (!mode || button.contains(event.target) || frequencyButton.contains(event.target) || wanted && context && context.state === 'running') return;
    applyMode();
  };
  document.addEventListener('pointerdown', activate, {capture: true, passive: true});
  document.addEventListener('keydown', activate, {capture: true, passive: true});
  document.addEventListener('pointerup', event => {
    if (event.pointerType !== 'mouse') activate(event);
  }, {capture: true, passive: true});
  addEventListener('pagehide', () => {
    wanted = false;
    revision++;
    clearTimeout(quietTimer);
    if (context && context.state === 'running') suspendWhenQuiet(ramp(0));
  });
  addEventListener('pageshow', event => {
    if (!event.persisted) return;
    wanted = false;
    revision++;
    mode = readMode();
    frequency = mode || readFrequency();
    if (context && context.state === 'running') suspendWhenQuiet(ramp(0));
    render();
  });
  frequencyButton.disabled = false;
  button.disabled = false;
  button.closest('.carrier-item').hidden = false;
  render();
})();
