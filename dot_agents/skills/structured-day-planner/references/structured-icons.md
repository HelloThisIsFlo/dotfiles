# Structured Icons

Structured task icons come from a curated in-app library. The public sources describe task icons as selected through Structured's picker, with hundreds of Apple and Android icons organized by category and searchable in the app.

Sources:

- Structured help: https://help.structured.app/en/articles/331138
- Structured 2.3 release notes: https://structured.app/blog/structured-2-3
- Structured customization help: https://help.structured.app/en/articles/1598722

## Rules

- Treat the in-app Structured icon picker as the exhaustive source of truth.
- Treat SF Symbols-style names as candidates, not guaranteed support.
- After updating a task `symbol`, read the task back and verify the value persisted.
- If a candidate fails or does not persist, fall back to a nearby known-good symbol from the same category.
- Use task titles without emoji prefixes unless the user asks otherwise.

## Category Starter Map

Use these as first-pass candidates. Prefer the most specific symbol that persists.

### Routine and recurring rituals

- `sunrise.fill`
- `moon.fill`
- `checklist`
- `calendar`

### Physical activity and sport

- `dumbbell.fill`
- `figure.walk`
- `figure.run`
- `figure.table.tennis`
- `bicycle`
- `sportscourt.fill`

### Personal care and hygiene

- `shower.fill`
- `drop.fill`
- `face.smiling`
- `sparkles`

### Travel and transit

- `car.fill`
- `tram.fill`
- `bus.fill`
- `airplane`
- `figure.walk`
- `map.fill`

### Health and appointments

- `cross.case.fill`
- `heart.fill`
- `stethoscope`
- `pills.fill`
- `bandage.fill`

### Work and focus

- `laptopcomputer`
- `briefcase.fill`
- `keyboard`
- `desktopcomputer`
- `brain.head.profile`

### Learning, reading, and audio

- `book.fill`
- `graduationcap.fill`
- `headphones`
- `pencil`
- `doc.text.fill`

### Admin, review, and planning

- `checklist`
- `calendar`
- `doc.text.fill`
- `tray.full.fill`
- `clock.fill`

### Household and chores

- `house.fill`
- `trash.fill`
- `washer.fill`
- `cart.fill`
- `wrench.fill`

### Food, meals, and errands

- `fork.knife`
- `cup.and.saucer.fill`
- `cart.fill`
- `takeoutbag.and.cup.and.straw.fill`

### Social, family, and care

- `person.2.fill`
- `phone.fill`
- `message.fill`
- `custom.baby`
- `heart.fill`

### Outdoor and nature

- `tree.fill`
- `leaf.fill`
- `figure.walk`
- `sun.max.fill`

### Creative and leisure

- `paintpalette.fill`
- `music.note`
- `gamecontroller.fill`
- `camera.fill`

### Rest and recovery

- `bed.double.fill`
- `moon.fill`
- `zzz`
- `heart.fill`

## Fallback Strategy

If a specific icon candidate is unsupported:

1. Try a less specific candidate in the same category.
2. Prefer known persisted symbols from the user's existing plan.
3. If none fit, keep the current symbol and still apply color/category updates.
4. Tell the user if icon support blocked a specific choice.
