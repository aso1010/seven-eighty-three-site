#!/usr/bin/env python3
"""Browser checks for the native carrier. No audio assets or runtime packages."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import functools, http.server, threading, json
ROOT=Path(__file__).resolve().parents[1]/'seven-eighty-three-website'
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}'
TRACK='''(() => {
 const Native=window.AudioContext;
 window.carrierTest={contexts:[],ramps:[],starts:0};
 window.AudioContext=class extends Native {
  constructor(){super();this.oscillators=[];this.gains=[];carrierTest.contexts.push(this);}
  createOscillator(){const node=super.createOscillator();this.oscillators.push(node);const start=node.start.bind(node);node.start=(...args)=>{carrierTest.starts++;return start(...args)};return node;}
  createGain(){const node=super.createGain();this.gains.push(node);const ramp=node.gain.linearRampToValueAtTime.bind(node.gain);node.gain.linearRampToValueAtTime=(value,end)=>{carrierTest.ramps.push({value,duration:end-this.currentTime});return ramp(value,end)};return node;}
 };
})();'''
def ready(page):page.locator('.carrier-toggle:not([disabled])').wait_for(state='visible')
def state(page,value,hz=783):page.wait_for_function('(args)=>document.querySelector(".carrier-toggle").textContent==="[ "+args[1]+" HZ // "+args[0]+" ]"',arg=[value,hz])
def quiet(page):page.wait_for_function('()=>carrierTest.contexts[0].state==="suspended"')
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');context.add_init_script(TRACK);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL+'/');ready(page);state(page,'ARMED');width=page.locator('.carrier-toggle').evaluate('(e)=>e.getBoundingClientRect().width')
    assert page.evaluate('carrierTest.contexts.length')==0
    page.mouse.click(1,1);state(page,'ON');page.wait_for_timeout(70)
    info=page.evaluate('''()=>{let c=carrierTest.contexts[0];return {contexts:carrierTest.contexts.length,oscillators:c.oscillators.length,gains:c.gains.length,type:c.oscillators[0].type,frequency:c.oscillators[0].frequency.value,gain:c.gains[0].gain.value,starts:carrierTest.starts,ramps:carrierTest.ramps}}''')
    assert info['contexts']==info['oscillators']==info['gains']==info['starts']==1,info
    assert info['type']=='sine' and info['frequency']==783 and abs(info['gain']-.018)<1e-6,info
    assert abs(info['ramps'][0]['duration']-.035)<.001,info
    button=page.locator('.carrier-toggle');button.click();state(page,'OFF');quiet(page)
    assert page.evaluate('sessionStorage.getItem("lab783CarrierMuted")')=='true'
    assert page.evaluate('carrierTest.contexts[0].gains[0].gain.value')==0
    assert button.evaluate('(e)=>e.getBoundingClientRect().width')==width
    button.focus();page.keyboard.press('Enter');state(page,'ON');page.wait_for_timeout(60)
    assert page.evaluate('carrierTest.contexts.length')==1
    assert page.evaluate('sessionStorage.getItem("lab783CarrierMuted")')=='false'
    page.keyboard.press('Space');state(page,'OFF');quiet(page)
    assert button.evaluate('(e)=>getComputedStyle(e).outlineWidth')=='1px'
    assert all(abs(r['duration']-.035)<.001 and r['value'] in [0,.018] for r in page.evaluate('carrierTest.ramps'))
    # Muting survives every route and prevents gesture allocation of a new context.
    routes=['/capabilities/','/structure/','/prospectus/','/work/','/intake/','/ventures/food-api/','/case-study/','/foundry/','/']
    for route in routes:
        page.goto(URL+route);ready(page);state(page,'OFF');page.mouse.click(1,1)
        assert page.evaluate('carrierTest.contexts.length')==0,route
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),route
    # A direct click from armed creates one context and stays on, without the document gesture double toggle.
    page.evaluate('sessionStorage.removeItem("lab783CarrierMuted")');page.reload();ready(page);state(page,'ARMED')
    button=page.locator('.carrier-toggle');button.click();state(page,'ON')
    assert page.evaluate('carrierTest.contexts.length')==1
    for _ in range(6):button.click(force=True)
    state(page,'ON');page.wait_for_timeout(70);assert page.evaluate('carrierTest.contexts[0].oscillators.length')==1
    button.click();state(page,'OFF');quiet(page)
    assert not errors,errors;context.close();print('PASS: lazy allocation, 783 Hz sine, peak 0.018, 35ms ramps, pointer/keyboard control, fixed width, one-node reuse, rapid toggles, session mute on nine routes.')
    # A non-control key is also an activation gesture.
    context=browser.new_context(reduced_motion='reduce');context.add_init_script(TRACK);page=context.new_page();page.goto(URL+'/intake/');ready(page);page.locator('#intake-name').focus();page.keyboard.press('a');state(page,'ON');assert page.locator('#intake-name').input_value()=='a';context.close()
    # Touch gets the same single-context state machine on a narrow viewport.
    context=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');context.add_init_script(TRACK);page=context.new_page();page.goto(URL+'/case-study/');ready(page);page.touchscreen.tap(1,1);state(page,'ON');assert page.evaluate('carrierTest.contexts.length')==1;page.locator('.carrier-toggle').tap();state(page,'OFF');quiet(page);assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');context.close()
    # Failed or blocked storage never prevents the toggle from working.
    context=browser.new_context(reduced_motion='reduce');context.add_init_script(TRACK);context.add_init_script("Object.defineProperty(window,'sessionStorage',{get(){throw new Error('Storage blocked')}})");page=context.new_page();page.goto(URL+'/case-study/');ready(page);page.locator('.carrier-toggle').click();state(page,'ON');page.locator('.carrier-toggle').click();state(page,'OFF');quiet(page);context.close()
    # The fallback ramp path works without cancelAndHoldAtTime.
    context=browser.new_context(reduced_motion='reduce');context.add_init_script(TRACK);context.add_init_script('AudioParam.prototype.cancelAndHoldAtTime=undefined');page=context.new_page();page.goto(URL+'/');ready(page);page.locator('.carrier-toggle').click();state(page,'ON');page.wait_for_timeout(60);page.locator('.carrier-toggle').click();state(page,'OFF');quiet(page);context.close()
    # Frequency selection is lazy, persists across pages, and never overrides mute.
    context=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce');context.add_init_script(TRACK);page=context.new_page();page.goto(URL+'/');ready(page)
    frequency=page.locator('.carrier-frequency');frequency.click();state(page,'ARMED',7.83)
    assert page.evaluate('carrierTest.contexts.length')==0
    assert page.evaluate('sessionStorage.getItem("lab783CarrierFrequency")')=='7.83'
    page.locator('.carrier-toggle').click();state(page,'ON',7.83);page.wait_for_timeout(80)
    assert abs(page.evaluate('carrierTest.contexts[0].oscillators[0].frequency.value')-7.83)<.001
    frequency.focus();page.keyboard.press('Enter');state(page,'ON',783);page.wait_for_timeout(110)
    assert page.evaluate('carrierTest.contexts[0].oscillators[0].frequency.value')==783
    assert abs(page.evaluate('carrierTest.contexts[0].gains[0].gain.value')-.018)<1e-6
    switch_ramps=page.evaluate('carrierTest.ramps.slice(-2)')
    assert switch_ramps[0]['value']==0 and abs(switch_ramps[0]['duration']-.035)<.001
    assert switch_ramps[1]['value']==.018 and abs(switch_ramps[1]['duration']-.07)<.001
    page.keyboard.press('Space');state(page,'ON',7.83)
    page.locator('.carrier-toggle').click();state(page,'OFF',7.83);quiet(page)
    frequency.click();state(page,'OFF',783);assert page.evaluate('carrierTest.contexts[0].state')=='suspended'
    frequency.click();state(page,'OFF',7.83)
    for route in routes:
        page.goto(URL+route);ready(page);state(page,'OFF',7.83)
        assert page.evaluate('carrierTest.contexts.length')==0
        assert page.locator('.carrier-frequency').is_visible()
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
    page.locator('.carrier-toggle').click();state(page,'ON',7.83)
    for _ in range(7):page.locator('.carrier-frequency').click(force=True)
    page.wait_for_timeout(110);state(page,'ON',783)
    assert page.evaluate('carrierTest.contexts.length')==1
    assert page.evaluate('carrierTest.contexts[0].oscillators.length')==1
    assert page.evaluate('carrierTest.contexts[0].oscillators[0].frequency.value')==783
    page.locator('.carrier-frequency').click();page.locator('.carrier-toggle').click();state(page,'OFF',7.83);quiet(page)
    assert page.evaluate('carrierTest.contexts[0].gains[0].gain.value')==0
    context.close();print('PASS: 7.83/783 Hz pointer and keyboard selection, 35ms crossfade legs, rapid switching, mute during switching, lazy selection and frequency persistence on nine routes.')
    # Unsupported audio and no JavaScript expose no unusable control.
    context=browser.new_context();context.add_init_script('window.AudioContext=undefined;window.webkitAudioContext=undefined');page=context.new_page();page.goto(URL+'/');assert page.locator('.carrier-item').is_hidden();assert page.locator('.site-nav a').count()==6;context.close()
    context=browser.new_context(java_script_enabled=False);page=context.new_page();page.goto(URL+'/case-study/');assert page.locator('.carrier-item').is_hidden();assert page.locator('main').is_visible();context.close()
    browser.close();print('PASS: typing, mobile touch, strict case-study policy, blocked storage, fallback ramps, unsupported audio and no-JavaScript navigation.')
server.shutdown()
