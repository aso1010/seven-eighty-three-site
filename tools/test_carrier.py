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
def ready(page):
    page.locator('.carrier-item:not([hidden]) summary').wait_for(state='visible')
    # Open programmatically to isolate audio preference tests from activation gestures.
    page.locator('.carrier-panel').evaluate('(e)=>e.open=true')
    page.locator('.carrier-toggle:not([disabled])').wait_for(state='visible')
def sound(page,on):page.wait_for_function('(on)=>document.querySelector(".carrier-toggle").textContent===(on?"[ SOUND: ON ]":"[ SOUND: OFF ]")',arg=on)
def frequency(page,hz):page.wait_for_function('(hz)=>Math.abs(carrierTest.contexts[0].oscillators[0].frequency.value-hz)<.001',arg=hz)
def quiet(page):page.wait_for_function('()=>carrierTest.contexts[0].state==="suspended"')
ROUTES=['/','/capabilities/','/structure/','/prospectus/','/work/','/intake/','/ventures/food-api/','/case-study/','/foundry/']
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce');context.add_init_script(TRACK);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(URL+'/');ready(page);sound(page,False)
    assert page.locator('.carrier-item button').count()==2
    page.mouse.click(1,1);assert page.evaluate('carrierTest.contexts.length')==0
    f=page.locator('.carrier-frequency');button=page.locator('.carrier-toggle')
    f.click();sound(page,False);assert f.text_content()=='[ FREQUENCY: 783 HZ ]'
    assert page.evaluate('carrierTest.contexts.length')==0
    f.click();button.click();sound(page,True);frequency(page,7.83);page.wait_for_timeout(80)
    assert abs(page.evaluate('carrierTest.contexts[0].gains[0].gain.value')-.018)<1e-6
    f.focus();page.keyboard.press('Enter');frequency(page,783);sound(page,True);page.wait_for_timeout(80)
    ramps=page.evaluate('carrierTest.ramps.slice(-2)')
    assert ramps[0]['value']==0 and abs(ramps[0]['duration']-.035)<.001,ramps
    assert ramps[1]['value']==.018 and abs(ramps[1]['duration']-.07)<.001,ramps
    page.keyboard.press('Space');frequency(page,7.83)
    button.click();sound(page,False);quiet(page);f.click();sound(page,False)
    for route in ROUTES:
        page.goto(URL+route);ready(page);sound(page,False)
        assert page.locator('.carrier-frequency').text_content()=='[ FREQUENCY: 783 HZ ]'
        page.mouse.click(1,1);assert page.evaluate('carrierTest.contexts.length')==0
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),route
    page.locator('.carrier-toggle').click();frequency(page,783)
    for route in ROUTES:
        page.goto(URL+route);ready(page);sound(page,True);assert page.evaluate('carrierTest.contexts.length')==0
        page.mouse.click(1,1);frequency(page,783)
    for _ in range(6):page.locator('.carrier-frequency').click(force=True)
    page.wait_for_timeout(100);frequency(page,783)
    assert page.evaluate('carrierTest.contexts.length')==1
    assert page.evaluate('carrierTest.contexts[0].oscillators.length')==1
    page.locator('.carrier-frequency').click();page.locator('.carrier-toggle').click();quiet(page)
    assert page.evaluate('carrierTest.contexts[0].gains[0].gain.value')==0
    assert not errors,errors
    context.close();print('PASS separate labeled controls, lazy OFF, frequency selection while muted, native synthesis, 35ms fades, keyboard control, rapid switching, session preferences and one oscillator across nine routes.')
    for storage_blocked in [False,True]:
        context=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);context.add_init_script(TRACK)
        if storage_blocked:context.add_init_script("Object.defineProperty(window,'sessionStorage',{get(){throw new Error('blocked')}})")
        page=context.new_page();page.goto(URL+'/case-study/');ready(page);page.locator('.carrier-frequency').tap();sound(page,False);page.locator('.carrier-toggle').tap();frequency(page,783);page.locator('.carrier-toggle').tap();sound(page,False);quiet(page);context.close()
    context=browser.new_context();context.add_init_script(TRACK);context.add_init_script('AudioParam.prototype.cancelAndHoldAtTime=undefined');page=context.new_page();page.goto(URL+'/');ready(page);page.locator('.carrier-toggle').click();frequency(page,7.83);page.locator('.carrier-frequency').click();frequency(page,783);page.locator('.carrier-toggle').click();quiet(page);context.close()
    context=browser.new_context(viewport={'width':390,'height':844});context.add_init_script(TRACK);page=context.new_page();page.goto(URL+'/');page.locator('.carrier-item:not([hidden]) summary').wait_for(state='visible')
    assert not page.locator('.carrier-panel').evaluate('(e)=>e.open')
    assert page.locator('.carrier-toggle').is_hidden() and page.locator('.carrier-cue').is_hidden()
    summary=page.locator('.carrier-panel summary');summary.focus();page.keyboard.press('Enter');assert page.locator('.carrier-toggle').is_visible()
    assert page.evaluate('carrierTest.contexts.length')==0
    summary.focus();page.keyboard.press('Space');assert page.locator('.carrier-toggle').is_hidden()
    context.close();print('PASS closed-by-default native Sound disclosure, hidden cue, Enter/Space opening and no sound allocation on opening.')
    context=browser.new_context();context.add_init_script('window.AudioContext=undefined;window.webkitAudioContext=undefined');page=context.new_page();page.goto(URL+'/');assert page.locator('.carrier-item').is_hidden();context.close()
    context=browser.new_context(java_script_enabled=False);page=context.new_page();page.goto(URL+'/');assert page.locator('.carrier-item').is_hidden();assert page.locator('main').is_visible();context.close()
    browser.close();print('PASS touch, blocked storage, fallback ramps, unsupported audio and no JavaScript.')
server.shutdown()
