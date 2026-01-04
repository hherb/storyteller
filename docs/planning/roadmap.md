# Development Roadmap

## Phase 1: Foundation (Current)

### Completed
- [x] Project structure and configuration
- [x] MFLUX image generation prototype
- [x] Documentation structure

### In Progress
- [ ] Evaluate MFLUX image quality for children's illustrations
- [ ] Test different illustration styles

### Next
- [ ] Ollama LLM integration prototype
- [ ] Story conversation flow design

## Phase 2: Core Engine

- [ ] Story and Page data models
- [ ] Story persistence (save/load)
- [ ] LLM-based story guidance engine
- [ ] Prompt templates for story assistance

## Phase 3: Image Generation Integration

- [ ] MFLUX wrapper with error handling
- [ ] Illustration prompt generation from story context
- [ ] Character consistency tracking
- [ ] Style presets (watercolor, cartoon, etc.)

## Phase 4: User Interface

- [ ] Flet application shell
- [ ] Home screen / project browser
- [ ] Story editor with page navigation
- [ ] Illustration preview and regeneration
- [ ] Settings and preferences

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
