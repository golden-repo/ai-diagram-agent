import os, asyncio, sys
from concurrent.futures import ThreadPoolExecutor
from playwright.async_api import async_playwright
import base64

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def _render_mermaid(html, path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await page.locator("#diagram-container").screenshot(path=path)
        await browser.close()

async def _render_drawio(xml, path):
    """Render Draw.io XML to PNG by loading it in draw.io embed viewer"""
    # Encode XML for URL
    xml_encoded = base64.b64encode(xml.encode('utf-8')).decode('utf-8')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 20px; background: white; }}
            #diagram {{ width: 100%; height: 800px; border: none; }}
        </style>
    </head>
    <body>
        <iframe id="diagram" src="https://viewer.diagrams.net/?embed=1&proto=json&spin=1#R{xml_encoded}"></iframe>
    </body>
    </html>
    """
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1200, "height": 900})
        await page.set_content(html, wait_until="networkidle")
        
        # Wait for iframe to load and diagram to render
        await page.wait_for_timeout(2000)
        
        # Wait for the loading spinner to disappear (check if iframe content is loaded)
        try:
            iframe = page.frame_locator("#diagram")
            # Wait longer for draw.io to fully render
            await page.wait_for_timeout(5000)
        except:
            # If we can't access iframe, just wait longer
            await page.wait_for_timeout(5000)
        
        await page.screenshot(path=path, full_page=False)
        await browser.close()

def _run_in_thread(render_func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(render_func(*args))
    loop.close()

def image_gen_agent(state):
    print("🖼️ [Image Gen] Rendering PNG...")
    session_id = state.get('session_id', 'unknown')
    code = state["diagram_code"]
    output_format = state.get('output_format', 'mermaid').lower()
    
    # Save image with session ID (no iteration number)
    os.makedirs("output", exist_ok=True)
    path = f"output/{session_id}_diagram.png"
    
    try:
        if output_format == 'drawio':
            print("   ⚠️ Draw.io image generation is slow/unreliable via iframe.")
            print("   ℹ️ Please open the .drawio file directly in https://app.diagrams.net")
            diagram_file = state.get('diagram_file', 'output file')
            print(f"   💾 Diagram file available: {diagram_file}")
            # Skip image generation for draw.io, return the diagram file path
            return {"image_file": diagram_file}
        else:
            print("   Rendering Mermaid diagram...")
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                <script>mermaid.initialize({{startOnLoad:true}});</script>
            </head>
            <body>
                <div id="diagram-container" class="mermaid">{code}</div>
            </body>
            </html>
            """
            with ThreadPoolExecutor() as executor:
                executor.submit(_run_in_thread, _render_mermaid, html, path).result()
        
        print(f"   ✅ Image saved to: {path}")
        return {"image_file": path}
    except Exception as e:
        print(f"❌ [Image Gen] Failed: {e}")
        return {}