# Accessibility

Semantic header, main, sections, aside, article, form, labels, headings, status region, and dialog-like evidence drawer structure the page. Focus-visible styling is global and card controls are keyboard operable with Enter/Space. Mode buttons expose `aria-pressed`; loading and errors use `role=status`/`aria-live`.

Temperature is always written numerically beside color. Candidate cards provide map-equivalent text controls; polygon clicks supplement, rather than replace, textual data. Colors are paired with labels and source-role copy. Reduced motion disables smooth transitions/scroll behavior.

Playwright verified keyboard-compatible candidate focus/click behavior, evidence drawer interaction, semantic mode state, and no horizontal overflow at mobile/desktop widths. Axe was not run; external basemap contrast remains a separate review item.
