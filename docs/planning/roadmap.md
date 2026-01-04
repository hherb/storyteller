# Development Roadmap

## Phase 1: Foundation (COMPLETED)

- [x] Project structure and configuration
- [x] MFLUX image generation prototype
- [x] Documentation structure
- [x] Ollama LLM integration prototype
- [x] Story conversation flow design

## Phase 2: Core Engine (COMPLETED)

- [x] Story and Page data models
- [x] Story persistence (save/load)
- [x] LLM-based story guidance engine
- [x] Prompt templates for story assistance

## Phase 3: Image Generation Integration (COMPLETED)

See [phase-3-image-generation.md](./phase-3-image-generation.md) for detailed plan.

- [x] MFLUX wrapper with error handling (`generation/image.py`)
- [x] Style presets module (`generation/styles.py`)
- [x] Illustration prompt generation from story context
- [x] Character dataclass and consistency tracking
- [x] Character definition dialog
- [x] UI integration with progress feedback

## Phase 4: User Interface (90% COMPLETE)

### Completed
- [x] Flet application shell with tabbed layout
- [x] App bar with project title and quick actions
- [x] Status bar with save/model/page indicators
- [x] Settings tab with all configuration cards
- [x] Create Story tab with conversation UI
- [x] Preview tab with image display and navigation
- [x] New Story dialog
- [x] Progress overlay dialog
- [x] State management
- [x] Character definition dialog

### Remaining
- [ ] Export dialog
- [ ] Fullscreen preview mode
- [ ] Keyboard shortcuts

## Phase 5: Export and Polish

- [ ] PDF export with proper formatting
- [ ] Print-ready output options
- [ ] Application packaging (PyInstaller)
- [ ] macOS DMG installer
- [ ] User documentation

## Phase 6: Future Enhancements

- [ ] Multiple character tracking
- [ ] Audio narration generation
- [ ] Story templates library
- [ ] Import existing stories
- [ ] Cloud backup (optional)

---

## Technical Decisions Log

### 2024-01-04: Package Manager
**Decision**: Use `uv` as the package manager throughout the project.
**Rationale**: Faster than pip, better dependency resolution, growing ecosystem support.

### 2024-01-04: Image Generation
**Decision**: Use MFLUX with FLUX models for image generation.
**Rationale**: Native Apple Silicon support via MLX, high-quality output, active development.
**Alternative Considered**: Diffusers library - slower on Apple Silicon, less optimized.

### 2024-01-04: GUI Framework
**Decision**: Use Flet for the user interface.
**Rationale**: Pure Python, Flutter-based modern UI, cross-platform potential, existing familiarity.
**Alternative Considered**: PyQt - steeper learning curve, licensing complexity.

### 2024-01-04: LLM Runtime
**Decision**: Use Ollama for local LLM inference.
**Rationale**: Simple API, good model selection, handles model management.
**Alternative Considered**: Direct llama.cpp - more complex setup, less user-friendly.
