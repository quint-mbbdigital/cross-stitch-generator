Here is the formal UI/UX specification report. It is written in the language of a Design System document, ready to be interpreted by an LLM or a frontend engineer.

---

# UI/UX Specification: The Modern Atelier

**Project:** Cross-Stitch Generator Interface
**Design Language:** Minimalist Utility / "Invisible Interface"
**Version:** 1.0

## 1. Design Ethos

The "Modern Atelier" aesthetic is defined by **chromatic restraint** and **high data density** without visual clutter. The interface acts as a silent frame for the user’s artwork. We adhere to the principle of "Tools, not Toys"—every pixel must serve a functional purpose.

* **Cognitive Load:** Minimized. Configuration controls are isolated from the visualization layer to prevent context switching.
* **Visual Hierarchy:** The source image and generated pattern are the protagonists; the UI is the supporting cast.
* **Tactility:** Despite being digital, interactions should mimic the precision of physical tools (snappy toggles, precise sliders, instant feedback).

## 2. Interface Architecture

The viewport is governed by a **Split-Pane Workspace** pattern, dividing the screen into two distinct functional regions that maintain state independently.

### 2.1 The Control Rail (Sidebar)

* **Position:** Fixed Left, `width: 320px`.
* **Role:** The "Configuration Context." It houses all parametric inputs (colors, dimensions, quantization settings).
* **Behavior:** Scrollable independent of the main canvas. Changes here do not trigger a full page reload but update the local state in preparation for generation.
* **Visuals:** `bg-zinc-50` (subtle contrast against the white canvas). Separated by a `1px` border (`border-zinc-200`).

### 2.2 The Canvas (Main Viewport)

* **Position:** Fluid Right, filling remaining width.
* **Role:** The "Visualization Context." It serves three distinct modes: **Input** (Upload), **Processing** (Loading), and **Review** (Pattern Interaction).
* **Behavior:** Pan and Zoom capabilities for the generated pattern.
* **Visuals:** `bg-white` or a subtle "dot grid" pattern (`bg-grid-zinc-100`) to evoke the concept of Aida cloth.

---

## 3. Workflow Patterns & Interaction Choreography

### 3.1 State I: The Invitation (Empty State)

The user is greeted not by a blank screen, but by a clear **Affordance of Action**.

* **Center Stage:** A large, elegant "Dropzone" component.
* *Visual:* Dashed border `border-dashed border-2 border-zinc-300`, rounded corners `rounded-xl`.
* *Micro-interaction:* On file drag-over, the border transitions to `border-indigo-500` and the background tints `bg-indigo-50/20`.


* **Sidebar State:** Inactive/Dimmed. Input fields are disabled (opacity 50%) until a valid asset is mounted.

### 3.2 State II: The Configuration (Parameter Tuning)

Once an asset is mounted, the Sidebar becomes active.

* **The "Liveness" Feedback:** As the user adjusts a slider (e.g., "Max Colors: 30"), the "Generate" button pulses or updates its label to reflect the "stale" state of the current view versus the new parameters.
* **Input Components:**
* **Sliders:** Minimal track height, thumb size `16px`, tooltips showing exact values.
* **Palette Selection:** A visual stack of color swatches representing the selected thread family (DMC/Anchor).



### 3.3 State III: The Reveal (Generation & Review)

The transition from image to pattern is the "Magic Moment."

* **Transition:** Use a Skeleton Loader that mimics the grid structure of the final output, preventing layout shift.
* **The Review Layer:**
* **The Switch:** A segmented control (toggle) at the top of the canvas allows the user to switch views: `[ "Virtual Stitch" | "Symbol Map" ]`.
* **Virtual Stitch View:** Renders pixels with a slight "X" texture to simulate thread.
* **Symbol Map View:** Overlays high-contrast vector symbols for readability.


* **The Legend:** A "Floating Panel" or "Drawer" that slides in from the right, listing the Thread IDs, Color Names, and Stitch Counts.

---

## 4. Visual Identity System

### 4.1 Color Theory: "Cold Utility"

We avoid warm UI colors to prevent clashing with the user's uploaded art.

* **Canvas:** `#FFFFFF` (White)
* **Surface:** `#F8FAFC` (Slate-50)
* **Ink (Primary Text):** `#1E293B` (Slate-800) — *Never pure black.*
* **Ink (Secondary Text):** `#64748B` (Slate-500)
* **Accent (Interactive):** `#4F46E5` (Indigo-600) — Used strictly for primary buttons and active states.
* **Borders:** `#E2E8F0` (Slate-200)

### 4.2 Typography: "Data Elegant"

* **Typeface:** `Inter` (Variable).
* **Hierarchy:**
* *Headers:* Light weight (`font-light`), tight tracking (`-0.025em`).
* *Body:* Regular weight, standard tracking.
* *Data/Labels:* Uppercase, small size (`text-xs`), wide tracking (`0.05em`), Medium weight.



### 4.3 Iconography

* **Style:** Stroke-based, 1.5px width. (Recommended: Lucide React or Heroicons Outline).
* **Consistency:** Icons should always be accompanied by a text label in tooltips to ensure clarity.

---

## 5. Component Specifications (Frontend Developer Ready)

### The Primary Action Button (`<GenerateButton />`)

* **Placement:** Fixed at the bottom of the Sidebar (Sticky Footer) or Top Right of Navbar.
* **Styling:** Full width (in sidebar context), `bg-indigo-600`, `text-white`, `rounded-md`, `shadow-sm`.
* **States:**
* *Default:* "Generate Pattern"
* *Loading:* "Processing..." (with spinner)
* *Disabled:* Grayed out if no image is present.



### The Quantization Sliders (`<ParameterSlider />`)

* **Behavior:** "Snap" to integer values (you cannot have 14.5 stitches).
* **Visuals:** The track fill matches the Accent color.
* **UX Note:** Include a text input alongside the slider for users who prefer typing "100" over sliding to it.

### The Export Modal (`<ExportDialog />`)

* **Trigger:** Triggered by a "Download" icon.
* **Content:** A clean list of options:
* [ ] Export PDF (Chart + Key)
* [ ] Export PNG (Preview)
* [ ] Export JSON (Raw Data)


* **Visuals:** A centered modal with a backdrop blur (`backdrop-blur-sm`) to focus attention.

---

## 6. Responsiveness & Mobile Strategy

While primarily a desktop productivity tool, the layout must adapt.

* **Tablet/Mobile:** The **Split-Pane** collapses. The Sidebar becomes a "Sheet" or "Drawer" triggerable by a "Settings" button. The Main Canvas takes 100% width.
* **Touch Targets:** All interactive elements must meet the 44px minimum touch target size on mobile viewports.