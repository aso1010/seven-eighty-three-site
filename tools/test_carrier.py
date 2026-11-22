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
def state(page,value):
    label='[ SOUND // OFF ]' if value==0 else '[ '+str(value)+' HZ ]'
    page.wait_for_function('(label)=>document.querySelector(".carrier-toggle").textContent===label',arg=label)
def quiet(page):page.wait_for_function('()=>carrierTest.contexts[0].state==="suspended"')
def frequency(page,hz):
    page.wait_for_function('(hz)=>Math.abs(carrierTest.contexts[0].oscillators[0].frequency.value-hz)<.001',arg=hz)
ROUTES=['/','/capabilities/','/structure/','/prospectus/','/work/','/intake/','/ventures/food-api/','/case-study/','/foundry/']
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');context.add_init_script(TRACK);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL+'/');ready(page);state(page,0)
    assert page.locator('.carrier-item button').count()==1
    assert page.locator('.carrier-frequency').count()==0
    page.mouse.click(1,1);state(page,0);assert page.evaluate('carrierTest.contexts.length')==0
    button=page.locator('.carrier-toggle');width=button.evaluate('(e)=>e.getBoundingClientRect().width')
    button.click();state(page,7.83);frequency(page,7.83);page.wait_for_timeout(80)
    info=page.evaluate('''()=>{let c=carrierTest.contexts[0];return {type:c.oscillators[0].type,gain:c.gains[0].gain.value,starts:carrierTest.starts}}''')
    assert info['type']=='sine' and abs(info['gain']-.018)<1e-6 and info['starts']==1,info
    assert page.evaluate('sessionStorage.getItem("lab783CarrierMode")')=='7.83'
    button.focus();page.keyboard.press('Enter');state(page,783);frequency(page,783);page.wait_for_timeout(80)
    ramps=page.evaluate('carrierTest.ramps.slice(-2)')
    assert ramps[0]['value']==0 and abs(ramps[0]['duration']-.035)<.001,ramps
    assert ramps[1]['value']==.018 and abs(ramps[1]['duration']-.07)<.001,ramps
    page.keyboard.press('Space');state(page,0);quiet(page)
    assert page.evaluate('carrierTest.contexts[0].gains[0].gain.value')==0
    assert button.evaluate('(e)=>getComputedStyle(e).outlineWidth')=='1px'
    assert button.evaluate('(e)=>e.getBoundingClientRect().width')==width
    for route in ROUTES:
        page.goto(URL+route);ready(page);state(page,0);page.mouse.click(1,1)
        assert page.evaluate('carrierTest.contexts.length')==0,route
        assert page.locator('.carrier-item button').count()==1
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),route
    page.locator('.carrier-toggle').click();state(page,7.83)
    for route in ROUTES:
        page.goto(URL+route);ready(page);state(page,7.83)
        assert page.evaluate('carrierTest.contexts.length')==0
        page.mouse.click(1,1);frequency(page,7.83)
        assert page.locator('.carrier-toggle').get_attribute('aria-pressed')=='true'
    button=page.locator('.carrier-toggle')
    for _ in range(9):button.click(force=True)
    state(page,7.83);page.wait_for_timeout(110);frequency(page,7.83)
    assert page.evaluate('carrierTest.contexts.length')==1
    assert page.evaluate('carrierTest.contexts[0].oscillators.length')==1
    button.click();button.click();state(page,0);quiet(page)
    page.evaluate("window.dispatchEvent(new PageTransitionEvent('pagehide'))")
    page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))");state(page,0)
    assert not errors,errors
    context.close();print('PASS single-control cycle, lazy OFF, 7.83/783 Hz synthesis, gain and 35ms fades, keyboard access, rapid clicks, one oscillator, session OFF and active choice on nine routes.')
    # Touch activation advances exactly once, including from the first press.
    context=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');context.add_init_script(TRACK);page=context.new_page();page.goto(URL+'/case-study/');ready(page)
    for value in [7.83,783,0]:page.locator('.carrier-toggle').tap();state(page,value)
    quiet(page);assert not page.evaluate('document.documentElement.scrollWidth>innerWidth');context.close()
    # Storage failures preserve a usable local cycle.
    context=browser.new_context();context.add_init_script(TRACK);context.add_init_script("Object.defineProperty(window,'sessionStorage',{get(){throw new Error('Storage blocked')}})");page=context.new_page();page.goto(URL+'/');ready(page)
    for value in [7.83,783,0]:page.locator('.carrier-toggle').click();state(page,value)
    quiet(page);context.close()
    # Existing explicit mute and active frequency migrate without creating audio on load.
    for muted,expected in [('true',0),('false',7.83)]:
        context=browser.new_context();context.add_init_script(TRACK);context.add_init_script("sessionStorage.setItem('lab783CarrierMuted','"+muted+"');sessionStorage.setItem('lab783CarrierFrequency','7.83')");page=context.new_page();page.goto(URL+'/');ready(page);state(page,expected);assert page.evaluate('carrierTest.contexts.length')==0;context.close()
    # Fallback AudioParam path retains click-free gain scheduling.
    context=browser.new_context();context.add_init_script(TRACK);context.add_init_script('AudioParam.prototype.cancelAndHoldAtTime=undefined');page=context.new_page();page.goto(URL+'/');ready(page)
    for value in [7.83,783,0]:page.locator('.carrier-toggle').click();state(page,value);page.wait_for_timeout(80)
    quiet(page);context.close()
    # No unsupported or scriptless controls are exposed.
    context=browser.new_context();context.add_init_script('window.AudioContext=undefined;window.webkitAudioContext=undefined');page=context.new_page();page.goto(URL+'/');assert page.locator('.carrier-item').is_hidden();context.close()
    context=browser.new_context(java_script_enabled=False);page=context.new_page();page.goto(URL+'/case-study/');assert page.locator('.carrier-item').is_hidden();assert page.locator('main').is_visible();context.close()
    browser.close();print('PASS touch, blocked storage, legacy preference migration, fallback ramps, strict policy, unsupported audio and no JavaScript.')
server.shutdown()
