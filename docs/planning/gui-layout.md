# Interactive GUI Layout Plan

This document defines the layout and interaction design for the Storyteller interactive GUI built with Flet.

## Overview

The application uses a **tabbed layout** where each major section gets full screen width for comfortable work:

```
+------------------------------------------------------------------+
|  STORYTELLER                    [New] [Open] [Save]    [Export]  |
+------------------------------------------------------------------+
|  [ Settings ]    [ Create Story ]    [ Preview ]                 |
+==================================================================+
|                                                                  |
|                                                                  |
|                    FULL-WIDTH TAB CONTENT                        |
|                                                                  |
|                                                                  |
+------------------------------------------------------------------+
|  Status: Ready                              Page 3 of 10         |
+------------------------------------------------------------------+
```

**Design Principles:**
- Each tab gets full width for proper workspace
- Quick access toolbar for common actions (New, Open, Save, Export)
- Status bar shows current state and page position
- Seamless navigation between tabs while preserving state
- Story creation is the default/primary tab

---

## Application Structure

### App Bar (Top)

```
+------------------------------------------------------------------+
|  📖 STORYTELLER                                                  |
|  "Luna's Forest Adventure"              [New] [Open] [Save] [⚙]  |
+------------------------------------------------------------------+
```

**Components:**
- **App Logo/Title**: "Storyteller" branding
- **Project Title**: Current story name (editable inline)
- **Quick Actions**:
  - New Story: Opens new story dialog
  - Open: Opens file picker / recent stories
  - Save: Saves current project
  - Settings Gear: Opens settings tab

### Tab Bar

```
+------------------------------------------------------------------+
|  [⚙ Settings]     [✏️ Create Story]     [👁 Preview]              |
+------------------------------------------------------------------+
```

Three main tabs with icons for quick recognition.

### Status Bar (Bottom)

```
+------------------------------------------------------------------+
|  ✓ Saved 2 min ago    |    Ollama: phi4    |    Page 3 of 10     |
+------------------------------------------------------------------+
```

**Components:**
- Save status indicator
- Current LLM model
- Page position (clickable to jump)
- Generation status during AI operations

---

## Tab 1: Settings

Full-width configuration panel organized in logical sections.

### Layout

```
+------------------------------------------------------------------+
|  SETTINGS                                                        |
+------------------------------------------------------------------+
|                                                                  |
|  +---------------------------+    +---------------------------+  |
|  | 📖 STORY SETTINGS         |    | 🤖 TEXT GENERATION        |  |
|  +---------------------------+    +---------------------------+  |
|  |                           |    |                           |  |
|  |  Title:                   |    |  Model:                   |  |
|  |  [Luna's Forest Adventure]|    |  [▼ phi4              ]   |  |
|  |                           |    |  [Refresh Models]         |  |
|  |  Author:                  |    |                           |  |
|  |  [Parent Name           ] |    |  Temperature:   0.7       |  |
|  |                           |    |  ──────────●─────────     |  |
|  |  Target Age:              |    |  Precise      Creative    |  |
|  |  [▼ 5-8 years           ] |    |                           |  |
|  |                           |    |  Max Tokens:              |  |
|  |  Total Pages:             |    |  [▼ Auto (recommended) ]  |  |
|  |  [▼ 10                  ] |    |                           |  |
|  |                           |    +---------------------------+  |
|  +---------------------------+                                   |
|                                                                  |
|  +---------------------------+    +---------------------------+  |
|  | 🎨 ILLUSTRATION STYLE     |    | 🖼 IMAGE GENERATION        |  |
|  +---------------------------+    +---------------------------+  |
|  |                           |    |                           |  |
|  |  Style Preset:            |    |  Model:                   |  |
|  |  ( ) Watercolor           |    |  (●) FLUX.1-schnell       |  |
|  |  (●) Cartoon              |    |  ( ) FLUX.1-dev           |  |
|  |  ( ) Storybook Classic    |    |                           |  |
|  |  ( ) Modern Digital       |    |  Quantization:            |  |
|  |  ( ) Pencil Sketch        |    |  (●) 4-bit (~6GB RAM)     |  |
|  |                           |    |  ( ) 8-bit (~12GB RAM)    |  |
|  |  [Preview Style]          |    |                           |  |
|  |                           |    |  Steps: [4]               |  |
|  |                           |    |  ────●───────────         |  |
|  |                           |    |  Fast          Quality    |  |
|  |                           |    |                           |  |
|  |                           |    |  [ ] Auto-generate after  |  |
|  |                           |    |      page text            |  |
|  +---------------------------+    +---------------------------+  |
|                                                                  |
+------------------------------------------------------------------+
```

### Settings Sections

#### 1. Story Settings (Top Left)
| Field | Type | Options |
|-------|------|---------|
| Title | Text input | Free text |
| Author | Text input | Free text |
| Target Age | Dropdown | "2-5" (Pre-readers), "5-8" (Early readers), "6-10" (Primary) |
| Total Pages | Dropdown | 6, 8, 10, 12, 16 |

#### 2. Text Generation (Top Right)
| Field | Type | Options |
|-------|------|---------|
| Model | Dropdown | Available Ollama models (from `list_models()`) |
| Refresh | Button | Re-fetches available models |
| Temperature | Slider | 0.0 - 1.0 (default 0.7) |
| Max Tokens | Dropdown | Auto, 256, 512, 1024, 2048 |

#### 3. Illustration Style (Bottom Left)
| Field | Type | Options |
|-------|------|---------|
| Style Preset | Radio | watercolor, cartoon, storybook_classic, modern_digital, pencil_sketch |
| Preview | Button | Shows sample image in selected style |

#### 4. Image Generation (Bottom Right)
| Field | Type | Options |
|-------|------|---------|
| Model | Radio | schnell (fast), dev (quality) |
| Quantization | Radio | 4-bit (~6GB), 8-bit (~12GB) |
| Steps | Slider | 2-8 (schnell), 15-30 (dev) |
| Auto-generate | Toggle | Generate images after page text |

---

## Tab 2: Create Story (Default Tab)

The main interactive workspace for creating the story through conversation with the AI.

### Layout

```
+------------------------------------------------------------------+
|  CREATE STORY                                                    |
+------------------------------------------------------------------+
|                                                                  |
|  +---------------------------------------------+  +-----------+  |
|  |                                             |  | PAGES     |  |
|  |  CONVERSATION                               |  +-----------+  |
|  |                                             |  | [1] ✓     |  |
|  |  ┌─────────────────────────────────────┐    |  | [2] ✓     |  |
|  |  │ 🤖 Let's create your story! What    │    |  | [3] ●     |  |
|  |  │    would you like it to be about?   │    |  | [4] ○     |  |
|  |  └─────────────────────────────────────┘    |  | [5] ○     |  |
|  |                                             |  | ...       |  |
|  |  ┌─────────────────────────────────────┐    |  | [+] Add   |  |
|  |  │ 👤 A brave little mouse who lives   │    |  +-----------+  |
|  |  │    in a cozy treehouse in the forest│    |  |CHARACTERS |  |
|  |  └─────────────────────────────────────┘    |  +-----------+  |
|  |                                             |  | 🐭 Luna   |  |
|  |  ┌─────────────────────────────────────┐    |  | 🦊 Felix  |  |
|  |  │ 🤖 What a wonderful idea! Luna the  │    |  | [+] Add   |  |
|  |  │    mouse sounds like a great hero..│    |  +-----------+  |
|  |  └─────────────────────────────────────┘    |                 |
|  |                                             |                 |
|  +---------------------------------------------+                 |
|                                                                  |
|  +--------------------------------------------------------------+|
|  | PAGE 3 CONTENT                                     [Expand]  ||
|  +--------------------------------------------------------------+|
|  | Text: Luna scampered through the forest, her tiny paws       ||
|  |       crunching on fallen leaves...                  [Edit]  ||
|  | Prompt: A small brown mouse walking through sunlit   [Edit]  ||
|  |         forest, autumn leaves, watercolor style...           ||
|  +--------------------------------------------------------------+|
|                                                                  |
|  +--------------------------------------------------------------+|
|  | Type your message...                                         ||
|  |                                                              ||
|  +--------------------------------------------------------------+|
|  [Send]  [Generate Page Text]  [Generate Illustration]  [Ideas] |
|                                                                  |
+------------------------------------------------------------------+
```

### Main Components

#### Conversation Panel (Left, ~70% width)
- Scrollable message history
- Clear bubbles for AI (left-aligned) and User (right-aligned)
- Typing indicator during AI generation
- Markdown rendering for formatted responses

**Message Bubble Styling:**
```
AI Messages:     User Messages:
┌──────────┐     ┌──────────┐
│ 🤖 ...   │     │    ... 👤│
└──────────┘     └──────────┘
  Light gray       Light blue
  Left-aligned     Right-aligned
```

#### Side Panel (Right, ~30% width)

**Pages Section:**
- Vertical list of page numbers
- Status indicators:
  - ✓ = Has text and illustration
  - ◐ = Has text only
  - ○ = Empty page
  - ● = Currently selected
- Click to navigate
- [+] Add Page button

**Characters Section:**
- List of defined characters with icons
- Click to view/edit details
- [+] Add Character button

#### Current Page Panel (Bottom, collapsible)
- Shows current page text (editable)
- Shows illustration prompt (editable)
- Expand button for full editing mode

#### Input Area (Bottom)
- Multi-line text input
- Action buttons:
  - **Send**: Submit to AI conversation
  - **Generate Page Text**: Create text for current page
  - **Generate Illustration**: Create image for current page
  - **Ideas**: Get AI suggestions

---

## Tab 3: Preview

Visual preview of the complete story with all illustrations.

### Layout

```
+------------------------------------------------------------------+
|  PREVIEW                                                         |
+------------------------------------------------------------------+
|                                                                  |
|  +--------------------------------------------------------------+|
|  |                                                              ||
|  |                                                              ||
|  |           +--------------------------------+                 ||
|  |           |                                |                 ||
|  |           |                                |                 ||
|  |           |      PAGE ILLUSTRATION         |                 ||
|  |           |         (Large View)           |                 ||
|  |           |                                |                 ||
|  |           |                                |                 ||
|  |           +--------------------------------+                 ||
|  |                                                              ||
|  |     Luna scampered through the forest, her tiny paws         ||
|  |     crunching on fallen leaves. The morning sun painted      ||
|  |     golden stripes through the trees.                        ||
|  |                                                              ||
|  +--------------------------------------------------------------+|
|                                                                  |
|  +--------------------------------------------------------------+|
|  |  PAGE NAVIGATION                                             ||
|  |  [◀ Prev]  [1] [2] [3] [4] [5] [6] [7] [8] [9] [10] [Next ▶] ||
|  |             ✓   ✓   ●   ◐   ○   ○   ○   ○   ○   ○            ||
|  +--------------------------------------------------------------+|
|                                                                  |
|  [Regenerate Image]  [Edit Text]  [Full Screen]  [Export PDF]   |
|                                                                  |
+------------------------------------------------------------------+
```

### Components

#### Main Preview Area
- Large illustration display (centered)
- Page text below illustration
- Mimics final book layout

**Image States:**
| State | Display |
|-------|---------|
| No illustration | Placeholder with "Generate" button |
| Generating | Progress bar + spinner + "Generating..." |
| Complete | Full illustration |
| Error | Error message + "Retry" button |

#### Page Navigation Strip
- Horizontal row of page number buttons
- Status indicators below each number
- Previous/Next buttons at ends
- Current page highlighted

#### Action Buttons
- **Regenerate Image**: Create new illustration
- **Edit Text**: Jump to Create tab with this page
- **Full Screen**: Expand to full-screen preview mode
- **Export PDF**: Open export dialog

### Full-Screen Preview Mode

```
+------------------------------------------------------------------+
|                                              [ESC to exit]   [X] |
+------------------------------------------------------------------+
|                                                                  |
|                                                                  |
|                                                                  |
|              +------------------------------------+               |
|              |                                    |               |
|              |                                    |               |
|              |        FULL SIZE IMAGE             |               |
|              |                                    |               |
|              |                                    |               |
|              +------------------------------------+               |
|                                                                  |
|              Luna scampered through the forest,                  |
|              her tiny paws crunching on fallen leaves.           |
|                                                                  |
|                                                                  |
|  [◀ Previous]                                        [Next ▶]    |
|                           Page 3 of 10                           |
+------------------------------------------------------------------+
```

---

## Dialogs

### New Story Dialog

```
+----------------------------------------------------------+
|  Create New Story                                    [X]  |
+----------------------------------------------------------+
|                                                          |
|  What would you like to call your story?                 |
|  +----------------------------------------------------+  |
|  |                                                    |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Who is the author?                                      |
|  +----------------------------------------------------+  |
|  |                                                    |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Who will read this story?                               |
|  +----------------------------------------------------+  |
|  | ( ) Toddlers & Pre-readers (ages 2-5)              |  |
|  | (●) Early Readers (ages 5-8)                       |  |
|  | ( ) Primary School (ages 6-10)                     |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Illustration style:                                     |
|  +----------------------------------------------------+  |
|  | [▼ Watercolor - Soft, dreamy, pastel colors    ]   |  |
|  +----------------------------------------------------+  |
|                                                          |
|  How many pages?                                         |
|  +----------------------------------------------------+  |
|  | [▼ 10 pages                                    ]   |  |
|  +----------------------------------------------------+  |
|                                                          |
|        [Cancel]                        [Create Story]    |
+----------------------------------------------------------+
```

### Character Definition Dialog

```
+----------------------------------------------------------+
|  Define Character                                    [X]  |
+----------------------------------------------------------+
|                                                          |
|  Character Name:                                         |
|  +----------------------------------------------------+  |
|  | Luna                                               |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Description (who are they? what are they like?):        |
|  +----------------------------------------------------+  |
|  | A small, brave field mouse who dreams of adventure.|  |
|  | She wears a tiny red scarf her grandmother made.   |  |
|  | She's curious and kind, always helping friends.    |  |
|  |                                                    |  |
|  +----------------------------------------------------+  |
|                                                          |
|  [✨ Extract Visual Traits with AI]                      |
|                                                          |
|  Visual Traits (for consistent illustrations):           |
|  +----------------------------------------------------+  |
|  | [small brown mouse        ] [×]                    |  |
|  | [red knitted scarf        ] [×]                    |  |
|  | [bright curious eyes      ] [×]                    |  |
|  | [+ Add trait...]                                   |  |
|  +----------------------------------------------------+  |
|                                                          |
|        [Cancel]                              [Save]      |
+----------------------------------------------------------+
```

### Export Dialog

```
+----------------------------------------------------------+
|  Export Story                                        [X]  |
+----------------------------------------------------------+
|                                                          |
|  Export Format:                                          |
|  ( ) PDF - Print Ready (high resolution)                 |
|  (●) PDF - Screen (smaller file size)                    |
|  ( ) Images Only (PNG folder)                            |
|                                                          |
|  Page Size:                                              |
|  [▼ A4 Landscape                                     ]   |
|                                                          |
|  Include:                                                |
|  [✓] Cover page with title                               |
|  [✓] Page numbers                                        |
|  [ ] Author bio on back                                  |
|                                                          |
|  Export Location:                                        |
|  +--------------------------------------------------+    |
|  | ~/Documents/Stories/luna_adventure.pdf           |    |
|  +--------------------------------------------------+    |
|  [Browse...]                                             |
|                                                          |
|        [Cancel]                             [Export]     |
+----------------------------------------------------------+
```

### Generation Progress Overlay

```
+----------------------------------------------------------+
|                                                          |
|                    🎨 Generating...                       |
|                                                          |
|         Creating illustration for Page 3                 |
|                                                          |
|         ████████████████░░░░░░░░░░  67%                  |
|                                                          |
|         Estimated time remaining: 45 seconds             |
|                                                          |
|                      [Cancel]                            |
|                                                          |
+----------------------------------------------------------+
```

---

## Component Hierarchy

```
App (app.py)
├── AppBar
│   ├── Logo
│   ├── ProjectTitle (editable)
│   └── QuickActions (New, Open, Save, Settings)
│
├── TabBar
│   ├── SettingsTab
│   ├── CreateTab (default)
│   └── PreviewTab
│
├── TabContent
│   │
│   ├── SettingsView (when Settings tab active)
│   │   ├── StorySettingsCard
│   │   ├── TextGenerationCard
│   │   ├── IllustrationStyleCard
│   │   └── ImageGenerationCard
│   │
│   ├── CreateView (when Create tab active)
│   │   ├── ConversationPanel
│   │   │   ├── MessageList
│   │   │   │   └── MessageBubble (multiple)
│   │   │   └── TypingIndicator
│   │   ├── SidePanel
│   │   │   ├── PageList
│   │   │   └── CharacterList
│   │   ├── CurrentPagePanel (collapsible)
│   │   │   ├── PageTextEditor
│   │   │   └── PromptEditor
│   │   └── InputArea
│   │       ├── TextInput
│   │       └── ActionButtons
│   │
│   └── PreviewView (when Preview tab active)
│       ├── IllustrationDisplay
│       ├── PageTextDisplay
│       ├── PageNavigationStrip
│       └── ActionButtons
│
└── StatusBar
    ├── SaveStatus
    ├── ModelIndicator
    └── PageIndicator
```

---

## File Structure

```
src/storyteller/ui/
├── __init__.py           # Public exports
├── app.py                # Main application entry, tab container
├── state.py              # Application state management
│
├── views/
│   ├── __init__.py
│   ├── settings.py       # Settings tab content
│   ├── create.py         # Create Story tab content
│   └── preview.py        # Preview tab content
│
├── components/
│   ├── __init__.py
│   ├── app_bar.py        # Top application bar
│   ├── status_bar.py     # Bottom status bar
│   ├── message_bubble.py # Chat message component
│   ├── page_list.py      # Page navigation list
│   ├── character_list.py # Character list component
│   ├── page_editor.py    # Page text/prompt editor
│   ├── image_display.py  # Image with loading states
│   └── settings_card.py  # Settings section card
│
├── dialogs/
│   ├── __init__.py
│   ├── new_story.py      # New story creation dialog
│   ├── character.py      # Character definition dialog
│   ├── export.py         # Export options dialog
│   └── progress.py       # Generation progress overlay
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
    project_path: Path | None

    # Engine and conversation
    engine: StoryEngine | None
    conversation_messages: list[ConversationMessage]

    # UI state
    active_tab: Literal["settings", "create", "preview"]
    current_page_number: int
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
    """User configuration - persisted between sessions."""

    # LLM settings
    llm_model: str = "phi4"
    llm_temperature: float = 0.7
    llm_max_tokens: int | None = None

    # Image settings
    image_model: str = "schnell"
    image_quantization: str = "4-bit"
    image_steps: int = 4
    auto_generate_images: bool = False
```

---

## Tab Navigation Behavior

### State Preservation
- All tabs maintain their state when switching
- Conversation history persists across tab switches
- Current page selection syncs between Create and Preview tabs

### Tab Indicators
- Badge on Create tab if there are unsaved changes
- Badge on Preview tab if illustrations are missing

### Auto-Navigation
- After generating page text: stay on Create tab
- After generating illustration: optionally jump to Preview
- On "Edit Text" from Preview: jump to Create tab

---

## Data Flow

### Story Creation Flow

```
User types message → InputArea
         ↓
    [Send] clicked
         ↓
StoryEngine.process_user_input()
         ↓
    OllamaClient.chat()
         ↓
AI Response → Update conversation_messages
         ↓
Update MessageList display
```

### Page Generation Flow

```
[Generate Page Text] clicked
         ↓
StoryEngine.generate_page_text(current_page)
         ↓
Update story.pages[current]
         ↓
Update CurrentPagePanel
         ↓
    (If auto_generate_images)
         ↓
Show progress overlay
         ↓
MFLUX.generate_image(prompt)
         ↓
Save to project_path/pages/page_XX.png
         ↓
Update Preview tab
```

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
| `Cmd+1` | Switch to Settings tab |
| `Cmd+2` | Switch to Create tab |
| `Cmd+3` | Switch to Preview tab |
| `Escape` | Close dialog / Cancel generation |

---

## Implementation Priority

### Phase 1: Core Shell
1. Main app with tab navigation
2. App bar with project title
3. Status bar with indicators
4. Placeholder content in each tab

### Phase 2: Settings Tab
1. Four settings cards layout
2. Story settings form
3. LLM model selection (with refresh)
4. Image generation settings
5. Style preset selection

### Phase 3: Create Tab
1. Conversation panel with message bubbles
2. Input area with action buttons
3. Side panel (pages + characters lists)
4. Current page panel (collapsible)

### Phase 4: Preview Tab
1. Large image display with states
2. Page text display
3. Page navigation strip
4. Action buttons

### Phase 5: Dialogs
1. New story dialog
2. Character definition dialog
3. Export dialog
4. Progress overlay

### Phase 6: Integration
1. Connect to StoryEngine
2. Real-time generation updates
3. Save/load functionality
4. Auto-save

### Phase 7: Polish
1. Keyboard shortcuts
2. Error handling UI
3. Animations and transitions
4. Persistence of user preferences

---

## Technical Notes

### Flet Tab Implementation

```python
import flet as ft

def main(page: ft.Page):
    page.title = "Storyteller"
    page.window.width = 1200
    page.window.height = 800

    # Create tab content views
    settings_view = SettingsView()
    create_view = CreateView()
    preview_view = PreviewView()

    # Tab container
    tabs = ft.Tabs(
        selected_index=1,  # Start on Create tab
        tabs=[
            ft.Tab(
                text="Settings",
                icon=ft.icons.SETTINGS,
                content=settings_view,
            ),
            ft.Tab(
                text="Create Story",
                icon=ft.icons.EDIT,
                content=create_view,
            ),
            ft.Tab(
                text="Preview",
                icon=ft.icons.VISIBILITY,
                content=preview_view,
            ),
        ],
        expand=True,
    )

    # Main layout
    page.add(
        AppBar(),
        tabs,
        StatusBar(),
    )

ft.app(target=main)
```

---

## Next Steps

1. Create `src/storyteller/ui/app.py` with tab shell
2. Implement `state.py` for state management
3. Build Settings tab with four cards
4. Implement Create tab conversation UI
5. Add Preview tab with image display
6. Create dialog components
7. Connect to StoryEngine
8. Add keyboard shortcuts and polish
