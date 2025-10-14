# VAREON Ecosystem Design Guidelines

## Design Approach: Hybrid System

**Primary Approach**: Material Design 3 + OpenAI/NVIDIA Aesthetic Fusion
- **Rationale**: This is a technical AI platform requiring both visual sophistication (OpenAI-inspired) and functional clarity (Material Design)
- **Key References**: OpenAI Platform Dashboard, NVIDIA Developer Portal, Linear App, Vercel Dashboard
- The ecosystem demands enterprise-grade polish with technical precision

## Core Design Principles

1. **Technical Sophistication**: Convey cutting-edge AI capabilities through refined, precise visual language
2. **Functional Clarity**: Complex AI operations must be immediately understandable
3. **Professional Authority**: Establish VAREON as an enterprise-grade AI platform
4. **Seamless Integration**: Legacy NeuroNet components must feel native to new design system

---

## Color Palette

### Dark Mode Foundation (Primary Theme)
- **Background Layers**: 
  - Base: 220 15% 9% (deep charcoal)
  - Elevated: 220 15% 12% (slightly lighter panels)
  - Accent surfaces: 220 20% 16% (cards, modals)

- **Primary Brand Colors**:
  - VAREON Blue: 217 91% 60% (vibrant, AI-forward)
  - Secondary Teal: 180 75% 50% (technical accent)
  - Success Green: 142 76% 46% (operational status)

- **Semantic Colors**:
  - Error: 0 84% 60% (destructive actions, failures)
  - Warning: 38 92% 50% (caution, pending approvals)
  - Info: 199 89% 48% (system information)

- **Text Hierarchy**:
  - Primary text: 0 0% 98% (headings, critical info)
  - Secondary text: 0 0% 70% (body, descriptions)
  - Tertiary text: 0 0% 50% (metadata, timestamps)

### Light Mode (Optional Support)
- Background: 0 0% 100%
- Cards: 0 0% 98%
- Text inverted from dark mode

### Accent Usage Rules
- **Sparingly**: Use vibrant blues/teals ONLY for primary CTAs, active states, and critical data points
- **NO gradients** except subtle radial glows behind key interactive elements
- **Status indicators**: Color-coded borders (green=running, yellow=pending, red=error, blue=ready)

---

## Typography

### Font Families
**Primary**: Inter (via Google Fonts)
- Headings: 500-700 weight
- Body: 400-500 weight
- Code/Technical: 400 weight

**Monospace**: JetBrains Mono (for code blocks, terminal, technical data)

### Type Scale (Tailwind)
- **Hero**: text-5xl md:text-6xl lg:text-7xl (48-72px, weight 700)
- **H1**: text-4xl md:text-5xl (36-48px, weight 600)
- **H2**: text-3xl md:text-4xl (30-36px, weight 600)
- **H3**: text-2xl md:text-3xl (24-30px, weight 600)
- **Body Large**: text-lg (18px, weight 400)
- **Body**: text-base (16px, weight 400)
- **Small**: text-sm (14px, weight 400)
- **Caption**: text-xs (12px, weight 500, uppercase tracking-wide for labels)

---

## Layout System

### Spacing Primitives (Tailwind Units)
- **Micro spacing**: 2, 3 (8px, 12px - tight elements)
- **Standard spacing**: 4, 6, 8 (16px, 24px, 32px - component padding, gaps)
- **Section spacing**: 12, 16, 20, 24 (48-96px - vertical rhythm)
- **Container max-widths**: max-w-7xl (1280px main content)

### Grid Patterns
- **Dashboard layouts**: 12-column grid with gap-4 to gap-6
- **Card grids**: grid-cols-1 md:grid-cols-2 lg:grid-cols-3 for feature cards
- **Split layouts**: 2-column (60/40 split) for content + sidebar

### Viewport Strategy
- **Full viewport sections**: ONLY for VAREON homepage hero (h-screen)
- **Natural height sections**: All dashboard content uses min-h-screen with natural flow
- **Component heights**: Auto-sizing with max-h constraints for scrollable areas

---

## Component Library

### Navigation
- **Top Nav Bar**: 
  - Sticky, backdrop-blur-md, bg-background/80
  - Logo (left), main nav (center), user/settings (right)
  - Height: h-16 (64px)
  - Border-bottom with subtle divider

- **Sidebar (Dashboard)**:
  - Fixed left, w-64 (256px)
  - Collapsible to w-16 (icon-only mode)
  - Active state: bg-accent/10 with left border-l-2 border-primary

### Cards & Containers
- **Standard Card**: 
  - Rounded: rounded-xl (12px)
  - Background: bg-elevated
  - Border: border border-white/10
  - Padding: p-6
  - Shadow: shadow-lg with colored glow on hover

- **Dashboard Panels**:
  - Same as cards but with header section (border-b divider)
  - Scrollable content area with max-h-[600px] overflow-y-auto

### Buttons
- **Primary**: bg-primary text-white hover:bg-primary/90 px-6 py-3 rounded-lg font-medium
- **Secondary**: border-2 border-primary text-primary hover:bg-primary/10
- **Ghost**: text-secondary hover:bg-white/5
- **Icon Buttons**: Square with hover:bg-white/10 rounded-lg p-2

### Form Inputs
- **Text Fields**: 
  - bg-background border border-white/20 rounded-lg px-4 py-3
  - Focus: ring-2 ring-primary border-primary
  - Placeholder: text-tertiary

- **Code/Terminal Inputs**:
  - font-mono bg-black/50 border border-white/30
  - Syntax highlighting for generated code

### Data Display
- **Tables**: 
  - Alternating row backgrounds (bg-white/5)
  - Hover: bg-white/10
  - Header: bg-elevated sticky top-0

- **Charts (Chart.js)**:
  - Dark theme config
  - Grid lines: rgba(255,255,255,0.1)
  - Tooltip: bg-elevated with border
  - Primary color: VAREON Blue

### Status Indicators
- **Badges**: 
  - Rounded-full px-3 py-1 text-xs font-semibold
  - Success: bg-green-500/20 text-green-400 border border-green-500/30
  - Error: bg-red-500/20 text-red-400 border border-red-500/30
  - Pending: bg-yellow-500/20 text-yellow-400 border border-yellow-500/30

- **Progress Bars**: 
  - h-2 rounded-full bg-white/10
  - Fill: bg-primary with animated shimmer

---

## Page-Specific Designs

### VAREON Homepage
- **Hero Section**: Full viewport (h-screen) with:
  - Large hero image: Abstract AI neural network visualization (dark, subtle particle effects)
  - Centered headline + tagline overlay
  - CTA buttons with backdrop-blur backgrounds
  - Subtle animated grid background

- **Features Grid**: 3-column cards showcasing NEOSYNTIS, MYNTRIX, NeuroNet AI
- **Architecture Diagram**: SVG flowchart with animated connections
- **Footer**: Multi-column (About, Products, Resources, Contact)

### NEOSYNTIS Dashboard
- **Layout**: Sidebar + main content area
- **Chat Interface**: 
  - Message bubbles (user: right-aligned bg-primary/20, AI: left-aligned bg-elevated)
  - Code blocks with syntax highlighting and copy button
  - File attachment previews

- **Control Panel**: Top toolbar with:
  - Model selector dropdown
  - Token usage meter (visual bar)
  - Settings gear icon

- **File Manager**: Split view (tree on left, content viewer on right)

### MYNTRIX Page
- **Architecture Visualization**: Large interactive SVG diagram
- **Component Cards**: Planner, Validator, Executor modules with icons
- **Code Examples**: Tabbed interface showing API usage

### NeuroNet AI Page
- **Capabilities Showcase**: 
  - Intent detection demo (interactive)
  - Reasoning system explanation with examples
  - Model comparison table

- **Live Demo Section**: 
  - Terminal-style interface
  - Real-time output streaming
  - WebSocket connection indicator

---

## Images & Media

### Hero Images
- **VAREON Homepage**: Abstract AI/neural network visualization (dark theme, particle effects, 1920x1080)
- **NeuroNet AI Page**: Code matrix/digital brain concept (cinematic, futuristic)

### Component Icons
- Use Heroicons (outline style) via CDN
- Color: text-primary for active, text-secondary for inactive
- Size: w-5 h-5 (20px) for inline, w-6 h-6 (24px) for standalone

### Illustrations
- Minimal line-art style diagrams for architecture flows
- Isometric 3D icons for feature cards (optional, use CSS transforms)

---

## Animations

**Minimal & Purposeful Only**:
- **Page transitions**: Fade in content with duration-300
- **Loading states**: Pulse animation on skeleton loaders
- **Interactive feedback**: Scale-95 on button active state
- **Chart reveals**: Animate-in data points on load
- **NO**: Background animations, parallax effects, or autoplay videos

---

## Accessibility

- **Contrast**: WCAG AAA for primary text (21:1 ratio on dark backgrounds)
- **Focus states**: Ring-2 ring-primary outline on all interactive elements
- **Form labels**: Always visible, text-sm text-secondary above inputs
- **Dark mode inputs**: Ensure bg-background (not transparent) for text fields
- **Keyboard navigation**: Full support with visible focus indicators

---

## Technical Integration Notes

- **Legacy NeuroNet UI**: Apply new color scheme to existing React components
- **WebSocket Terminal**: Use xterm.js with custom dark theme matching VAREON palette
- **Chart.js Config**: Custom theme with VAREON colors, dark gridlines
- **Code Highlighting**: Prism.js with "Tomorrow Night" theme adapted to VAREON blues

**Consistency Rule**: All legacy components MUST use new spacing primitives (p-4, m-6, gap-4) and color tokens (bg-elevated, text-primary) - no hardcoded values.