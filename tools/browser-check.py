#!/usr/bin/env python3
"""Development-only regression checks. No browser tooling is shipped to the site."""
from pathlib import Path
import functools, http.server, json, threading, re, os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]/'seven-eighty-three-website'
BASELINE=Path('/workspace/work/refactor-baseline')
PREVIEWS=Path(os.environ.get('PREVIEW_DIR','/tmp/lab783-previews'));PREVIEWS.mkdir(parents=True,exist_ok=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
servers=[]
for root in [ROOT]+([BASELINE] if BASELINE.exists() else []):
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start();servers.append(server)
URL=f'http://127.0.0.1:{servers[0].server_port}'
ROUTES=['/','/capabilities/','/structure/','/prospectus/','/work/','/intake/','/ventures/food-api/']
def ready(page):
    page.evaluate('document.fonts.ready');page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in [390,899,900,1200,1440,2048]:
        context=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        for route in ROUTES:
            response=page.goto(URL+route);ready(page);assert response.status==200
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,route,'overflow')
            assert page.get_by_role('heading',level=1).count()==1,(width,route,'H1')
            assert page.locator('.site-nav [aria-current="page"]').count()==1
            assert page.locator('.page-index [aria-current="location"]').count()==1
            assert page.locator('main').is_visible()
            if width in [390,1440,2048]:
                page.screenshot(path=str(PREVIEWS/(f'{width}-'+('home' if route=='/' else route.strip('/').replace('/','-'))+'.png')))
            if route=='/' and BASELINE.exists():
                selectors=['.opening-display','.cap','.mark','.mark svg','.foundation','.foundation-statement']
                measure='''selectors=>Object.fromEntries(selectors.map(q=>[q,[...document.querySelectorAll(q)].map(e=>{let r=e.getBoundingClientRect(),s=getComputedStyle(e);return {rect:[r.x,r.y,r.width,r.height],font:s.fontFamily,size:s.fontSize,line:s.lineHeight,spacing:s.letterSpacing}})]))'''
                current=page.evaluate(measure,selectors);old=context.new_page();old.goto(f'http://127.0.0.1:{servers[1].server_port}/');ready(old);original=old.evaluate(measure,selectors);old.close();assert current==original,(width,'opening changed',current,original)
            if width>=900 and route not in ['/intake/']:
                assert page.locator('main > section').first.evaluate('(e)=>getComputedStyle(e).gridTemplateColumns.split(" ").length')==12
        assert not errors,errors;context.close();print(f'PASS {width}px: all seven pages, navigation state, headings, overflow, protected opening dimensions.')
    # Native anchors and browser history; the observational index does not intercept navigation.
    page=browser.new_page(viewport={'width':1440,'height':900},reduced_motion='reduce');page.goto(URL+'/capabilities/');ready(page)
    links=page.locator('.page-index ol a');link=links.nth(1);fragment=link.get_attribute('href');link.click();ready(page)
    assert page.evaluate('location.hash')==fragment
    assert page.locator('.page-index [aria-current="location"]').get_attribute('href')==fragment
    page.go_back();assert page.url==URL+'/capabilities/'
    page.locator('.skip-link').focus();page.keyboard.press('Enter');assert page.evaluate('document.activeElement.id')=='main-content'
    # One native button; original Web Animations API physics and live preference changes.
    page.emulate_media(reduced_motion='no-preference');page.goto(URL+'/');ready(page)
    assert page.locator('.monolith-trigger').count()==1 and page.locator('.monolith-trigger').is_enabled()
    assert page.locator('.mark').evaluate('(e)=>e.getAnimations().length')==1
    assert page.locator('.mark').evaluate('(e)=>e.getAnimations()[0].effect.getTiming().duration')==1000
    page.emulate_media(reduced_motion='reduce');ready(page);assert page.locator('.mark').evaluate('(e)=>e.getAnimations().length')==0
    page.locator('.monolith-trigger').click();assert page.locator('.mark').evaluate('(e)=>e.getAnimations().length')==0
    page.emulate_media(reduced_motion='no-preference');ready(page)
    trigger=page.locator('.monolith-trigger');trigger.click();trigger.click(force=True)
    assert page.locator('.mark').evaluate('(e)=>e.getAnimations().length')==1
    assert page.locator('.mark').evaluate('(e)=>e.getAnimations()[0].effect.getTiming().duration')==860
    for key in ['Enter','Space']:
        page.locator('.mark').evaluate('(e)=>e.getAnimations().forEach(a=>a.finish())');trigger.focus();page.keyboard.press(key)
        assert page.locator('.mark').evaluate('(e)=>e.getAnimations().filter(a=>a.playState==="running").length')==1
    page.emulate_media(reduced_motion='reduce');ready(page);assert page.locator('.mark').evaluate('(e)=>e.getAnimations().length')==0
    # Intake stays local; verify the draft URI without opening an email app or sending anything.
    page.goto(URL+'/intake/?interest=food-api');ready(page)
    assert 'Food API specification' in page.locator('#intake-objective').input_value()
    assert not page.locator('form').evaluate('(e)=>e.checkValidity()')
    fields=page.locator('.intake-form input,.intake-form textarea');assert fields.count()==3
    for i in range(3):fields.nth(i).fill('   ')
    page.locator('.intake-form button').click();assert not page.locator('form').evaluate('(e)=>e.checkValidity()')
    fields.nth(0).fill('Test visitor');fields.nth(1).fill('Evaluate the Food API specification');fields.nth(2).fill('Existing chef network')
    page.evaluate('window.open=(uri)=>{window.__draft=uri;return null}')
    page.locator('.intake-form button').click()
    draft=page.evaluate('window.__draft');assert draft.startswith('mailto:hello@seveneightythree.com?') and 'Food%20API' in draft
    assert fields.nth(0).input_value()=='Test visitor'
    fields.nth(0).focus();assert fields.nth(0).evaluate('(e)=>getComputedStyle(e).outlineWidth')=='1px'
    page.close();print('PASS: anchors/history, skip link, pointer/Enter/Space recoil, repeat guard, live reduced-motion changes, intake validation and draft URI.')
    for width in [390,1440,2048]:
        context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=False);page=context.new_page()
        for route in ROUTES:
            page.goto(URL+route);page.evaluate('document.fonts.ready')
            assert page.locator('main').is_visible() and page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('.site-nav a').count()==6
            if route=='/':assert page.locator('.monolith-trigger').is_disabled()
            if route=='/intake/':assert page.locator('form').get_attribute('action')=='mailto:hello@seveneightythree.com'
        page.goto(URL+'/capabilities/');page.locator('.page-index ol a').nth(1).click();assert page.evaluate('location.hash')
        context.close();print(f'PASS {width}px no JavaScript: content, navigation, native anchors and form fallback.')
    browser.close()
for server in servers:server.shutdown()
