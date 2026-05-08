# Day 17: Autonomous Web Agents

## Learning Objectives
- Build agents that browse and interact with web pages
- Implement DOM-aware navigation and interaction
- Use Playwright for browser automation
- Design visual grounding for element selection
- Handle dynamic content and multi-step web tasks

---

## 1. Web Agent Architecture

```
┌─────────────────────────────────────────────────┐
│                  WEB AGENT                        │
│                                                  │
│  Observation: page screenshot / DOM / text       │
│       ↓                                          │
│  Planning: what action to take next              │
│       ↓                                          │
│  Action: click, type, scroll, navigate           │
│       ↓                                          │
│  Verification: did the action succeed?           │
└─────────────────────────────────────────────────┘

Action space:
- click(element)      - Type text into field
- navigate(url)       - Scroll up/down
- go_back()          - Extract text
- wait(seconds)      - Submit form
```

---

## 2. Browser Control with Playwright

```python
from playwright.async_api import async_playwright, Page
from dataclasses import dataclass
import asyncio

@dataclass
class BrowserAction:
    action_type: str  # click, type, navigate, scroll, extract
    selector: str | None = None
    value: str | None = None
    url: str | None = None

class BrowserController:
    """Controls browser via Playwright."""
    
    def __init__(self):
        self.browser = None
        self.page: Page | None = None
    
    async def start(self, headless: bool = True):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=headless)
        context = await self.browser.new_context(viewport={"width": 1280, "height": 720})
        self.page = await context.new_page()
    
    async def execute_action(self, action: BrowserAction) -> str:
        """Execute a browser action, return observation."""
        try:
            if action.action_type == "navigate":
                await self.page.goto(action.url, wait_until="domcontentloaded")
                return f"Navigated to {action.url}"
            
            elif action.action_type == "click":
                await self.page.click(action.selector, timeout=5000)
                await self.page.wait_for_load_state("domcontentloaded")
                return f"Clicked: {action.selector}"
            
            elif action.action_type == "type":
                await self.page.fill(action.selector, action.value)
                return f"Typed '{action.value}' into {action.selector}"
            
            elif action.action_type == "scroll":
                direction = -500 if action.value == "up" else 500
                await self.page.evaluate(f"window.scrollBy(0, {direction})")
                return f"Scrolled {action.value}"
            
            elif action.action_type == "extract":
                text = await self.page.inner_text(action.selector or "body")
                return text[:2000]
            
            elif action.action_type == "screenshot":
                path = "/tmp/screenshot.png"
                await self.page.screenshot(path=path)
                return f"Screenshot saved to {path}"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def get_page_state(self) -> dict:
        """Get current page state for agent observation."""
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "text": await self.page.inner_text("body"),
        }
    
    async def get_interactive_elements(self) -> list[dict]:
        """Get all clickable/interactive elements."""
        elements = await self.page.evaluate("""() => {
            const interactable = document.querySelectorAll(
                'a, button, input, select, textarea, [role="button"], [onclick]'
            );
            return Array.from(interactable).map((el, i) => ({
                index: i,
                tag: el.tagName.toLowerCase(),
                type: el.type || '',
                text: el.innerText?.slice(0, 50) || '',
                placeholder: el.placeholder || '',
                href: el.href || '',
                selector: el.id ? `#${el.id}` : `${el.tagName.toLowerCase()}:nth-of-type(${i})`,
            }));
        }""")
        return elements[:50]  # Limit to prevent context overflow
    
    async def close(self):
        if self.browser:
            await self.browser.close()
```

---

## 3. Web Agent with LLM Decision Making

```python
from openai import OpenAI

client = OpenAI()

class WebAgent:
    """LLM-powered web browsing agent."""
    
    def __init__(self):
        self.browser = BrowserController()
        self.history: list[dict] = []
        self.max_steps = 15
    
    async def run(self, task: str) -> str:
        """Execute a web task."""
        await self.browser.start(headless=True)
        
        try:
            for step in range(self.max_steps):
                # Get observation
                state = await self.browser.get_page_state()
                elements = await self.browser.get_interactive_elements()
                
                # Decide action
                action = self._decide_action(task, state, elements)
                
                if action.action_type == "done":
                    return action.value  # Final answer
                
                # Execute
                result = await self.browser.execute_action(action)
                self.history.append({"step": step, "action": action, "result": result})
                
            return "Max steps reached without completing task"
        finally:
            await self.browser.close()
    
    def _decide_action(self, task: str, state: dict, elements: list[dict]) -> BrowserAction:
        """LLM decides next action."""
        elements_text = "\n".join(
            f"[{e['index']}] <{e['tag']}> {e['text']} {e['placeholder']} {e['href'][:50]}"
            for e in elements[:30]
        )
        
        history_text = "\n".join(
            f"Step {h['step']}: {h['action'].action_type} → {h['result'][:100]}"
            for h in self.history[-5:]
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": """You are a web browsing agent. Given a task, current page state, and available elements, decide the next action.

Available actions:
- navigate: go to a URL
- click: click an element (use selector)
- type: type text into a field
- scroll: scroll up or down
- extract: get text from page
- done: task is complete (provide final answer as value)

Reply as JSON: {"action_type": "...", "selector": "...", "value": "...", "url": "..."}"""
            }, {"role": "user", "content": f"""Task: {task}

Current URL: {state['url']}
Page title: {state['title']}
Page text (truncated): {state['text'][:500]}

Interactive elements:
{elements_text}

History:
{history_text}

What's the next action?"""}],
        )
        
        import json
        data = json.loads(response.choices[0].message.content)
        return BrowserAction(**{k: v for k, v in data.items() if v})
```

---

## 4. DOM-Aware Navigation

```python
class DOMNavigator:
    """Structured DOM understanding for better element selection."""
    
    async def get_simplified_dom(self, page: Page) -> str:
        """Get simplified, agent-friendly DOM representation."""
        dom = await page.evaluate("""() => {
            function simplify(el, depth = 0) {
                if (depth > 5) return '';
                const tag = el.tagName?.toLowerCase();
                if (!tag || ['script', 'style', 'svg', 'path'].includes(tag)) return '';
                
                const attrs = [];
                if (el.id) attrs.push(`id="${el.id}"`);
                if (el.className) attrs.push(`class="${String(el.className).slice(0, 30)}"`);
                if (el.href) attrs.push(`href="${el.href.slice(0, 50)}"`);
                if (el.type) attrs.push(`type="${el.type}"`);
                
                const text = el.childNodes.length === 1 && el.childNodes[0].nodeType === 3 
                    ? el.childNodes[0].textContent?.trim().slice(0, 50) : '';
                
                const indent = '  '.repeat(depth);
                let result = `${indent}<${tag}${attrs.length ? ' ' + attrs.join(' ') : ''}>`;
                if (text) result += text;
                
                for (const child of el.children) {
                    const childResult = simplify(child, depth + 1);
                    if (childResult) result += '\\n' + childResult;
                }
                
                return result;
            }
            return simplify(document.body);
        }""")
        return dom[:3000]  # Truncate for context window
    
    async def find_element_by_description(self, page: Page, description: str) -> str | None:
        """Use LLM to find the best selector for a described element."""
        elements = await page.evaluate("""() => {
            const all = document.querySelectorAll('*');
            return Array.from(all).filter(el => {
                const rect = el.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
            }).map(el => ({
                tag: el.tagName.toLowerCase(),
                id: el.id,
                text: el.innerText?.slice(0, 50),
                ariaLabel: el.getAttribute('aria-label'),
            })).slice(0, 100);
        }""")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Find the element matching: '{description}'\n\nElements: {elements}\n\nReturn the best CSS selector."}],
        )
        return response.choices[0].message.content.strip()
```

---

## 5. Visual Grounding (Screenshot-Based)

```python
import base64

class VisualWebAgent:
    """Uses screenshots for visual understanding of pages."""
    
    async def get_screenshot_observation(self, page: Page) -> str:
        """Take screenshot and send to vision model."""
        screenshot_bytes = await page.screenshot()
        base64_image = base64.b64encode(screenshot_bytes).decode()
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "Describe what you see on this web page. List all interactive elements (buttons, links, inputs) with their approximate positions."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
            ]}],
        )
        return response.choices[0].message.content
    
    async def click_by_coordinates(self, page: Page, description: str) -> str:
        """Use vision to find and click an element by description."""
        screenshot_bytes = await page.screenshot()
        base64_image = base64.b64encode(screenshot_bytes).decode()
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": f"Where on this page is the element: '{description}'? Give approximate x,y pixel coordinates (page is 1280x720). Reply as JSON: {{\"x\": ..., \"y\": ...}}"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
            ]}],
        )
        
        import json
        coords = json.loads(response.choices[0].message.content)
        await page.mouse.click(coords["x"], coords["y"])
        return f"Clicked at ({coords['x']}, {coords['y']})"
```

---

## 6. Multi-Step Task Execution

```python
class WebTaskRunner:
    """Handles complex multi-step web tasks with error recovery."""
    
    def __init__(self):
        self.agent = WebAgent()
    
    async def execute_with_retry(self, task: str, max_retries: int = 2) -> str:
        """Execute task with retry on failure."""
        for attempt in range(max_retries + 1):
            try:
                result = await self.agent.run(task)
                if "error" not in result.lower():
                    return result
            except Exception as e:
                if attempt == max_retries:
                    return f"Failed after {max_retries} retries: {e}"
                # Wait before retry
                await asyncio.sleep(2)
        return "Task failed"
    
    async def execute_plan(self, steps: list[str]) -> list[str]:
        """Execute a series of web steps."""
        results = []
        for step in steps:
            result = await self.agent.run(step)
            results.append(result)
            if "error" in result.lower():
                break  # Stop on error
        return results

# Example tasks:
# "Go to GitHub, search for 'langgraph', find the star count of the top repository"
# "Fill out the contact form at example.com with name=Test, email=test@test.com"
# "Compare prices of iPhone 15 on Amazon and Best Buy"
```

---

## Interview Questions

### Beginner
1. **What is a web agent?** An AI agent that can browse the internet: navigate pages, click buttons, fill forms, extract information. Uses browser automation (Playwright/Selenium) for actions and LLM for decision-making. Observes page state, plans next action, executes, verifies.
2. **Why use Playwright over Selenium for web agents?** Playwright: faster, better async support, auto-wait for elements, network interception, multiple browser contexts, better for modern SPAs. Built-in screenshot/video capture. Better TypeScript/Python APIs. More reliable element detection.
3. **What are the main challenges with web agents?** Dynamic content (SPAs, AJAX). CAPTCHAs. Anti-bot detection. Changing page layouts. Handling popups/modals. Large DOMs exceeding context windows. Knowing when task is complete. Error recovery when elements aren't found.

### Intermediate
4. **Compare DOM-based vs screenshot-based approaches for web agents.** DOM-based: structured data, precise selectors, faster, but misses visual layout and rendered state. Screenshot-based: sees what human sees, handles canvas/images, but slower (vision model), less precise clicking. Hybrid: use DOM for interaction, screenshots for understanding complex layouts.
5. **How do you handle pages that exceed the LLM context window?** Truncate page text (first N chars). Simplify DOM (remove scripts, styles, deep nesting). Focus on interactive elements only. Use summarization for long text. Chunk page into sections. Prioritize visible viewport. Filter to task-relevant elements.
6. **How do you prevent web agents from taking harmful actions?** Allowlist of permitted domains. Block form submissions with payment info. Require approval for: purchases, account changes, posting content. Rate limiting requests. No credential storage. Read-only mode by default. Log all actions for audit.

### Advanced
7. **Design a web agent for automated price comparison.** Steps: 1) Navigate to each retailer. 2) Search for product. 3) Extract price, availability, shipping. 4) Handle variations (sizes, colors). 5) Normalize data. 6) Compare. Challenges: different site structures, anti-scraping, dynamic pricing. Use: site-specific adapters + fallback generic agent.
8. **How would you evaluate web agent performance?** Benchmarks: WebArena, Mind2Web. Metrics: task success rate, steps to completion, error recovery rate. Custom eval: define task + expected outcome, run N times, measure success%. A/B test: DOM vs visual approaches. Track: which site types are hardest, common failure modes.
9. **How do you make web agents robust to website changes?** Avoid brittle selectors (prefer aria-labels, data-testid over CSS classes). Fallback strategies: try multiple selectors. Self-healing: if selector fails, use visual grounding to re-locate element. Monitor: alert when success rate drops. Adaptive: update strategies based on recent failures.

---

## Hands-On Exercise
1. Set up Playwright browser controller with basic actions (navigate, click, type)
2. Build page observation (get interactive elements, simplified DOM)
3. Implement LLM-driven decision making (observe → decide → act)
4. Add visual grounding using screenshots with GPT-4o vision
5. Build multi-step task: "Search for a product on a website and extract price"
6. Add error recovery and retry logic
7. Benchmark: measure success rate on 5 different web tasks
