---
name: london-weather-outfit
description: Fetch the current weather in London and recommend what to wear. Use this whenever the user asks about London weather, what to wear in London, whether they need a coat or umbrella in London, or is heading out in London and wants a clothing recommendation — even if they don't explicitly say "weather skill."
---

# London Weather Outfit

Get the current London weather and turn it into a concrete clothing recommendation.

## Steps

1. Fetch current conditions for London, UK using WebFetch or WebSearch.
   - Good source: `https://wttr.in/London?format=j1` (JSON, no key needed).
   - Pull temperature (°C), feels-like, precipitation/chance of rain, and wind.

2. Map conditions to an outfit. Use judgment, but roughly:
   - **< 5°C** → heavy coat, scarf, gloves.
   - **5–12°C** → warm jacket or coat, layers.
   - **12–18°C** → light jacket or jumper.
   - **18–24°C** → long sleeves or t-shirt.
   - **> 24°C** → t-shirt, light clothing.
   - **Rain or high chance** → always add umbrella + waterproof.
   - **Windy (> 25 km/h)** → windproof layer, skip the umbrella (it'll flip).

3. Report back: one line of current conditions, then the recommendation.

## Output format

```
🌦️ London now: <temp>°C (feels <feels>°C), <conditions>, <rain>% rain
👕 Wear: <concrete recommendation>
```

Keep it short and actionable — the user is probably about to walk out the door.
