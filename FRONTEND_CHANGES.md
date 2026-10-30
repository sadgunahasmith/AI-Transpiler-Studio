# AI Transpiler Studio — Frontend updates

Only frontend files were updated. Backend source was not intentionally changed.

Included:
- Added an animated intro page as the first screen, with a compiler-stage visualization and direct navigation into the existing workspace. The workspace Home button returns to the intro.
- About Us dialog accessible from the top navigation.
- Light/dark theme toggle with saved preference.
- Dark charcoal surfaces with cinematic amber/orange lighting inspired by the supplied animation reference.
- Improved UI motion, animated button hover/press/focus feedback, dialog transitions, and responsive behavior.
- Broader light-theme styling for existing hard-coded utility classes.

## Run the updated frontend
1. Open a terminal in `frontend/`.
2. Run `npm install`.
3. Run `npm run dev`.
4. Open the local URL printed by Vite.

Use the frontend source in `frontend/src/`. Run `npm run build` in `frontend/` to regenerate `dist/` before serving a production build. Start the backend using the project's existing instructions.

## Compiler pipeline visualization
- Added an animated diagram that maps the project's six actual compiler stages from source tokens through target-code generation. It appears before analysis and alongside stage details, using the reference's warm glow treatment.
- Added consistent hover, press, and keyboard-focus feedback across frontend buttons while preserving their existing React event handlers.
- Included responsive layout and reduced-motion support for the new animation.




