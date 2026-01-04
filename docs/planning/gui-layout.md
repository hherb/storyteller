# Interactive GUI Layout Plan

This document defines the layout and interaction design for the Storyteller interactive GUI built with Flet.

## Overview

The application uses a **three-panel layout** optimized for the story creation workflow:

```
+------------------+------------------------+------------------+
|                  |                        |                  |
|   CONFIGURATION  |    STORY CREATION      |     PREVIEW      |
|      PANEL       |        PANEL           |      PANEL       |
|                  |                        |                  |
|   (Left Rail)    |   (Center - Main)      |   (Right Panel)  |
|                  |                        |                  |
+------------------+------------------------+------------------+
         250px            flexible                  350px
```

**Design Principles:**
- Configuration is accessible but not distracting (collapsible left rail)
- Story creation is the primary focus (largest area, center)
- Preview provides constant visual feedback (right panel)
- Responsive: panels can collapse on smaller screens

---

## Panel 1: Configuration Panel (Left Rail)

A collapsible left sidebar containing all settings and model configuration.

### 1.1 Project Section

```
+----------------------------------+
|  [+] New Story    [📁] Open      |
+----------------------------------+
|  Current Project:                |
|  "Luna's Forest Adventure"       |
|  Last saved: 2 min ago           |
+----------------------------------+
```

**Components:**
- **New Story Button**: Opens story creation dialog
- **Open Button**: Opens file picker / recent stories list
- **Project Info**: Current story title and save status

### 1.2 Story Metadata Section

```
+----------------------------------+
|  📖 STORY SETTINGS               |
+----------------------------------+
|  Title:                          |
|  [Luna's Forest Adventure    ]   |
|                                  |
|  Author:                         |
|  [Parent Name                ]   |
|                                  |
|  Target Age:                     |
|  [▼ 5-8 years (Early Readers)]   |
|                                  |
|  Illustration Style:             |
|  [▼ Watercolor               ]   |
|                                  |
|  Total Pages: [▼ 10]             |
+----------------------------------+
```

**Fields:**
| Field | Type | Options |
|-------|------|---------|
| Title | Text input | Free text |
| Author | Text input | Free text |
| Target Age | Dropdown | "2-5" (Pre-readers), "5-8" (Early readers), "6-10" (Primary) |
| Style | Dropdown | watercolor, cartoon, storybook_classic, modern_digital, pencil_sketch |
| Total Pages | Dropdown/Spinner | 6, 8, 10, 12, 16 |

### 1.3 LLM Configuration Section

```
+----------------------------------+
|  🤖 AI MODEL SETTINGS            |
+----------------------------------+
|  Text Model:                     |
|  [▼ phi4                     ]   |
|  [⟳ Refresh Models]              |
|                                  |
|  Temperature:     [0.7]          |
|  ─────────●──────────            |
|  Precise          Creative       |
|                                  |
|  Max Tokens:                     |
|  [▼ Auto (recommended)       ]   |
+----------------------------------+
```

**Components:**
- **Model Dropdown**: Lists available Ollama models (populated via `OllamaClient.list_models()`)
- **Refresh Button**: Re-fetches available models
- **Temperature Slider**: 0.0 to 1.0 (default 0.7)
- **Max Tokens**: Auto, 256, 512, 1024, 2048

### 1.4 Image Generation Section

```
+----------------------------------+
|  🎨 IMAGE SETTINGS               |
+----------------------------------+
|  Model:                          |
|  [▼ FLUX.1-schnell (fast)    ]   |
|                                  |
|  Quality:                        |
|  [▼ 4-bit quantized (~6GB)   ]   |
|                                  |
|  Generation Steps: [4]           |
|  ─────●──────────────            |
|  Fast            Quality         |
|                                  |
|  [ ] Auto-generate illustrations |
+----------------------------------+
```

**Components:**
- **Model Selection**: schnell (fast), dev (quality)
- **Quantization**: 4-bit, 8-bit
- **Steps Slider**: 2-8 for schnell, 15-30 for dev
- **Auto-generate Toggle**: Generate images automatically after page text

### 1.5 Actions Section

```
+----------------------------------+
|  💾 ACTIONS                      |
+----------------------------------+
|  [     Save Project      ]       |
|  [     Export to PDF     ]       |
|  [     Print Preview     ]       |
+----------------------------------+
```

---

## Panel 2: Story Creation Panel (Center)

The main interactive workspace for creating the story through conversation with the AI.

### 2.1 Layout Structure

```
+------------------------------------------------+
|  STORY CREATION                    Page 3 of 10|
+------------------------------------------------+
|                                                |
|  +------------------------------------------+  |
|  |                                          |  |
|  |         CONVERSATION HISTORY             |  |
|  |         (Scrollable Area)                |  |
|  |                                          |  |
|  |  [AI] Let's create your story! What      |  |
|  |       would you like your story to be    |  |
|  |       about?                             |  |
|  |                                          |  |
|  |  [User] A brave little mouse who lives   |  |
|  |         in a cozy treehouse              |  |
|  |                                          |  |
|  |  [AI] What a wonderful idea! Let me      |  |
|  |       help you develop this...           |  |
|  |                                          |  |
|  +------------------------------------------+  |
|                                                |
+------------------------------------------------+
|  +------------------------------------------+  |
|  |  Type your ideas here...                 |  |
|  |                                          |  |
|  +------------------------------------------+  |
|  [Send] [Generate Page Text] [Add Character]   |
+------------------------------------------------+
```

### 2.2 Conversation Area

**Features:**
- Scrollable message history
- Clear visual distinction between AI and user messages
- Messages grouped by story phase (brainstorming, character, pages)
- Typing indicator during AI generation
- Markdown rendering for formatted responses

**Message Types:**
```python
@dataclass
class ConversationMessage:
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    phase: Literal["brainstorm", "characters", "page_writing", "revision"]
```

### 2.3 Input Area

**Components:**
- **Text Input**: Multi-line text area for user input
- **Send Button**: Submit message for AI response
- **Quick Actions**:
  - **Generate Page Text**: Create text for current page
  - **Add Character**: Open character definition dialog
  - **Suggest Ideas**: Get AI suggestions for next steps

### 2.4 Page Navigation Bar

```
+------------------------------------------------+
|  ◀ Prev |  Page [3] of [10]  | Next ▶  | [+]  |
+------------------------------------------------+
```

- Navigate between pages
- Current page indicator
- Add new page button
- Visual indicator for pages with/without text and illustrations

### 2.5 Current Page Editor

When in page-editing mode, displays editable page content:

```
+------------------------------------------------+
|  PAGE 3 TEXT                          [Edit]   |
+------------------------------------------------+
|  Luna scampered through the forest, her tiny   |
|  paws crunching on fallen leaves. The morning  |
|  sun painted golden stripes through the trees. |
+------------------------------------------------+
|  ILLUSTRATION PROMPT                  [Edit]   |
+------------------------------------------------+
|  A small brown mouse with a red scarf walking  |
|  through a sunlit forest, autumn leaves on the |
|  ground, watercolor style, children's book...  |
+------------------------------------------------+
|  [Regenerate Text] [Generate Illustration]     |
+------------------------------------------------+
```

---

## Panel 3: Preview Panel (Right)

Visual preview of the story being created.

### 3.1 Layout Structure

```
+----------------------------------+
|  PREVIEW               [⛶ Full] |
+----------------------------------+
|                                  |
|  +----------------------------+  |
|  |                            |  |
|  |    CURRENT PAGE IMAGE      |  |
|  |        (Large View)        |  |
|  |                            |  |
|  |      [Generating...]       |  |
|  |        ████████░░ 80%      |  |
|  |                            |  |
|  +----------------------------+  |
|                                  |
|  "Luna scampered through the     |
|   forest, her tiny paws..."      |
|                                  |
+----------------------------------+
|  PAGE THUMBNAILS                 |
+----------------------------------+
|  [1] [2] [3*] [4] [5] [6] ...   |
|   ✓   ✓   ●    ○   ○   ○        |
+----------------------------------+
|  CHARACTERS                      |
+----------------------------------+
|  [🐭] Luna   [🦊] Felix          |
|  [+] Add Character               |
+----------------------------------+
```

### 3.2 Current Page Preview

**Features:**
- Large image preview (current page illustration)
- Page text below image (as it would appear in book)
- Generation progress bar during image creation
- Placeholder for pages without illustrations
- Click to expand to full-screen view

**States:**
| State | Display |
|-------|---------|
| No illustration | Placeholder with "Generate" button |
| Generating | Progress bar + estimated time |
| Complete | Full illustration |
| Error | Error message + "Retry" button |

### 3.3 Page Thumbnail Strip

**Features:**
- Horizontal scrollable thumbnail strip
- Visual indicators:
  - ✓ = Has text and illustration
  - ◐ = Has text, no illustration
  - ○ = Empty page
  - ● = Currently selected
- Click to navigate to page
- Drag to reorder pages

### 3.4 Characters Panel

**Features:**
- Grid/list of defined characters
- Character avatar (generated or placeholder icon)
- Click to view/edit character details
- Quick-add button for new characters

**Character Card:**
```
+------------------+
| [🐭 Avatar]      |
| Luna             |
| Brave little     |
| mouse            |
| [Edit] [Delete]  |
+------------------+
```

---

## Dialogs and Overlays

### New Story Dialog

```
+------------------------------------------+
|  Create New Story                   [X]  |
+------------------------------------------+
|                                          |
|  Story Title:                            |
|  [                                   ]   |
|                                          |
|  Your Name (Author):                     |
|  [                                   ]   |
|                                          |
|  Target Age Group:                       |
|  ( ) Pre-readers (ages 2-5)              |
|  (●) Early readers (ages 5-8)            |
|  ( ) Primary school (ages 6-10)          |
|                                          |
|  Illustration Style:                     |
|  [▼ Watercolor                       ]   |
|                                          |
|  Number of Pages:                        |
|  [▼ 10                               ]   |
|                                          |
|  [Cancel]                  [Create Story]|
+------------------------------------------+
```

### Character Definition Dialog

```
+------------------------------------------+
|  Define Character                   [X]  |
+------------------------------------------+
|                                          |
|  Character Name:                         |
|  [Luna                               ]   |
|                                          |
|  Description:                            |
|  [A small, brave field mouse who      ]  |
|  [dreams of adventure. She wears a    ]  |
|  [tiny red scarf her grandmother made ]  |
|  [                                    ]  |
|                                          |
|  [Extract Visual Traits with AI]         |
|                                          |
|  Visual Traits (for consistent images):  |
|  [small brown mouse] [x]                 |
|  [red knitted scarf] [x]                 |
|  [bright curious eyes] [x]               |
|  [+ Add Trait]                           |
|                                          |
|  [Cancel]                         [Save] |
+------------------------------------------+
```

### Full-Screen Preview

```
+--------------------------------------------------+
|  Luna's Forest Adventure - Page 3          [X]   |
+--------------------------------------------------+
|                                                  |
|                                                  |
|          +---------------------------+           |
|          |                           |           |
|          |                           |           |
|          |     FULL SIZE IMAGE       |           |
|          |                           |           |
|          |                           |           |
|          +---------------------------+           |
|                                                  |
|     Luna scampered through the forest, her       |
|     tiny paws crunching on fallen leaves.        |
|                                                  |
|  [◀ Previous]                       [Next ▶]     |
|                                                  |
+--------------------------------------------------+
```

### Generation Progress Overlay

```
+------------------------------------------+
|  Generating Illustration                 |
+------------------------------------------+
|                                          |
|            🎨                            |
|                                          |
|    Creating illustration for Page 3...   |
|                                          |
|    ████████████████░░░░░░░░  67%         |
|                                          |
|    Estimated time remaining: 45 seconds  |
|                                          |
|    [Cancel]                              |
|                                          |
+------------------------------------------+
```

---

## Component Hierarchy

```
App (main.py)
├── AppBar
│   ├── Title
│   ├── ProjectName
│   └── MenuButton
│
├── NavigationRail (Left - Collapsible)
│   ├── ProjectSection
│   ├── StoryMetadataSection
│   ├── LLMConfigSection
│   ├── ImageConfigSection
│   └── ActionsSection
│
├── MainContent (Center)
│   ├── ConversationView
│   │   ├── MessageList
│   │   │   └── MessageBubble (multiple)
│   │   └── TypingIndicator
│   │
│   ├── InputArea
│   │   ├── TextInput
│   │   └── ActionButtons
│   │
│   ├── PageNavigator
│   │   └── PageIndicator
│   │
│   └── PageEditor
│       ├── TextEditor
│       └── PromptEditor
│
└── PreviewPanel (Right)
    ├── CurrentPagePreview
    │   ├── ImageView
    │   ├── ProgressBar
    │   └── PageText
    │
    ├── ThumbnailStrip
    │   └── PageThumbnail (multiple)
    │
    └── CharacterPanel
        └── CharacterCard (multiple)
```

---

## File Structure

```
src/storyteller/ui/
├── __init__.py           # Public exports
├── app.py                # Main application entry, layout composition
├── state.py              # Application state management
│
├── panels/
│   ├── __init__.py
│   ├── config_panel.py   # Left configuration rail
│   ├── creation_panel.py # Center story creation
│   └── preview_panel.py  # Right preview panel
│
├── components/
│   ├── __init__.py
│   ├── message_bubble.py # Chat message component
│   ├── page_thumbnail.py # Page thumbnail in strip
│   ├── character_card.py # Character display card
│   ├── image_preview.py  # Image with loading states
│   └── progress_bar.py   # Generation progress
│
├── dialogs/
│   ├── __init__.py
│   ├── new_story.py      # New story creation dialog
│   ├── character.py      # Character definition dialog
│   └── export.py         # Export options dialog
│
└── theme.py              # Colors, typography, styling
```

---

## State Management

### Application State

```python
@dataclass
class AppState:
    """Global application state."""

    # Current story
    current_story: Story | None
    is_modified: bool

    # Engine and conversation
    engine: StoryEngine | None
    conversation_messages: list[ConversationMessage]

    # UI state
    current_page_number: int
    selected_panel: Literal["config", "creation", "preview"]
    is_generating_text: bool
    is_generating_image: bool
    generation_progress: float  # 0.0 to 1.0

    # Configuration
    config: AppConfig
```

### Configuration State

```python
@dataclass
class AppConfig:
    """User configuration."""

    # LLM settings
    llm_model: str = "phi4"
    llm_temperature: float = 0.7
    llm_max_tokens: int | None = None

    # Image settings
    image_model: str = "schnell"
    image_quantization: str = "4-bit"
    image_steps: int = 4
    auto_generate_images: bool = False

    # UI preferences
    left_panel_collapsed: bool = False
    right_panel_collapsed: bool = False
```

---

## Data Flow

### Story Creation Flow

```
User Input → StoryEngine.process_user_input()
                    ↓
           OllamaClient.chat()
                    ↓
           AI Response → Update conversation_messages
                    ↓
           Update UI (ConversationView)
```

### Page Generation Flow

```
User clicks "Generate Page Text"
            ↓
StoryEngine.generate_page_text()
            ↓
Update story.pages[current]
            ↓
Update PageEditor display
            ↓
(If auto_generate_images)
            ↓
MFLUX.generate_image(illustration_prompt)
            ↓
Save to project_path/pages/page_XX.png
            ↓
Update PreviewPanel
```

### Save/Load Flow

```
User clicks "Save"
      ↓
save_story(current_story, project_path)
      ↓
Update is_modified = False
      ↓
Show save confirmation

User clicks "Open"
      ↓
Show list_stories() results
      ↓
User selects story
      ↓
load_story(selected_path)
      ↓
Initialize StoryEngine with loaded story
      ↓
Populate all UI panels
```

---

## Responsive Behavior

### Large Screen (> 1400px)
- All three panels visible
- Left rail: 250px
- Right panel: 350px
- Center: flexible

### Medium Screen (1000px - 1400px)
- Left rail collapsed to icons only (60px)
- Right panel: 300px
- Center: flexible

### Small Screen (< 1000px)
- Tab-based navigation between panels
- Only one panel visible at a time
- Bottom navigation bar

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+N` | New Story |
| `Cmd+O` | Open Story |
| `Cmd+S` | Save Story |
| `Cmd+E` | Export to PDF |
| `Cmd+Enter` | Send message / Generate |
| `Cmd+Left/Right` | Previous/Next Page |
| `Cmd+1/2/3` | Focus Config/Creation/Preview panel |
| `Escape` | Close dialog / Cancel generation |

---

## Implementation Priority

### Phase 1: Core Layout
1. Main app shell with three-panel layout
2. Basic navigation rail (collapsible)
3. Placeholder content in each panel

### Phase 2: Configuration Panel
1. Story metadata form
2. LLM model selection (with refresh)
3. Image generation settings

### Phase 3: Story Creation Panel
1. Conversation view with message display
2. Input area with send button
3. Basic page navigation

### Phase 4: Preview Panel
1. Current page image display
2. Thumbnail strip
3. Character cards

### Phase 5: Integration
1. Connect to StoryEngine
2. Real-time updates during generation
3. Save/load functionality

### Phase 6: Polish
1. Progress indicators
2. Error handling UI
3. Keyboard shortcuts
4. Responsive behavior

---

## Technical Notes

### Flet-Specific Considerations

1. **Layout**: Use `ft.Row` and `ft.Column` for the three-panel layout
2. **State Updates**: Use `page.update()` for UI refreshes
3. **Async**: Use `asyncio` for long-running operations
4. **Theming**: Use `ft.Theme` for consistent styling
5. **Dialogs**: Use `ft.AlertDialog` for modal dialogs

### Example App Structure

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Storyteller"
    page.window.width = 1400
    page.window.height = 900

    # Create panels
    config_panel = ConfigPanel()
    creation_panel = CreationPanel()
    preview_panel = PreviewPanel()

    # Main layout
    page.add(
        ft.Row(
            controls=[
                config_panel,       # Left rail
                ft.VerticalDivider(),
                creation_panel,     # Center (expand=True)
                ft.VerticalDivider(),
                preview_panel,      # Right panel
            ],
            expand=True,
        )
    )

ft.app(target=main)
```

---

## Next Steps

1. Create `src/storyteller/ui/app.py` with basic shell
2. Implement state management in `state.py`
3. Build configuration panel components
4. Implement conversation view
5. Add preview panel with image display
6. Connect all panels to StoryEngine
7. Add persistence integration
8. Implement progress indicators and error handling
