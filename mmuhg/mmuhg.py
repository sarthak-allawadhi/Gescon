"""Gescon Reflex Web Application Implementation"""

import subprocess
import os
import sys
import signal
import atexit
import reflex as rx

active_processes = {}

def kill_native_controller():
    proc = active_processes.get("desktop_control")
    if proc:
        try:
            if os.name == 'nt':
                proc.terminate()
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=2)
        except:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except:
                try:
                    proc.kill()
                except:
                    pass
        active_processes["desktop_control"] = None

atexit.register(kill_native_controller)


class State(rx.State):
    """The app state."""
    theme: str = "light"
    desktop_control_active: bool = False

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"

    @rx.event(background=True)
    async def monitor_desktop_control(self):
        import asyncio
        while True:
            await asyncio.sleep(1)
            async with self:
                if not self.desktop_control_active:
                    break
                proc = active_processes.get("desktop_control")
                if proc and proc.poll() is not None:
                    # Process has exited (e.g. user pressed 'q' in OpenCV window)
                    self.desktop_control_active = False
                    active_processes["desktop_control"] = None
                    break

    def toggle_desktop_control(self):
        if self.desktop_control_active:
            self.desktop_control_active = False
            kill_native_controller()
        else:
            self.desktop_control_active = True
            try:
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                project_py_path = os.path.join(current_dir, "Project.py")
                
                if os.name == 'nt':
                    venv_python = os.path.join(current_dir, "venv", "Scripts", "python.exe")
                else:
                    venv_python = os.path.join(current_dir, "venv", "bin", "python")
                
                if not os.path.exists(venv_python):
                    venv_python = sys.executable
                
                preexec = None if os.name == 'nt' else os.setsid
                
                proc = subprocess.Popen(
                    [venv_python, project_py_path],
                    cwd=current_dir,
                    preexec_fn=preexec
                )
                active_processes["desktop_control"] = proc
                return State.monitor_desktop_control
            except Exception as e:
                print(f"Error starting native controller: {e}")
                self.desktop_control_active = False


def header_section() -> rx.Component:
    """Shared header section across pages."""
    return rx.el.header(
        rx.el.div(
            rx.html(
                '<svg viewBox="0 0 26 26" fill="none" style="width:26px; height:26px;">'
                '<circle cx="13" cy="13" r="12" stroke="var(--cyan)" stroke-width="1.4"/>'
                '<path d="M13 3V9M13 17V23M3 13H9M17 13H23" stroke="var(--cyan)" stroke-width="1.4"/>'
                '<circle cx="13" cy="13" r="2.4" fill="var(--amber)"/>'
                '</svg>'
            ),
            rx.el.a("Gescon", href="/"),
            class_name="logo"
        ),
        rx.el.nav(
            rx.el.a("Home", href="/"),
            rx.el.a("Gestures", href="/gestures"),
            rx.el.a("Live Demo", href="/demo"),
            rx.el.a("Install", href="/install"),
            rx.el.a("Roadmap", href="/roadmap"),
            rx.el.button(
                rx.cond(State.theme == "light", "🌙 Dark", "☀️ Light"),
                class_name="btn btn-ghost",
                on_click=State.toggle_theme,
                style={"marginLeft": "18px", "padding": "8px 14px", "fontSize": "12.5px"}
            )
        ),
    )


def footer_section() -> rx.Component:
    """Shared footer section across pages."""
    return rx.el.footer(
        "Built with OpenCV + MediaPipe · ",
        rx.el.a("View on GitHub", href="#"),
    )


def index() -> rx.Component:
    """Homepage: Immersive landing, tech stack, feature routes, and how it works."""
    return rx.el.div(
        rx.el.div(class_name="grid-bg"),
        header_section(),
        rx.el.main(
            # HERO
            rx.el.section(
                rx.el.div(
                    rx.el.h1("Control your cursor", rx.el.br(), "with your hand."),
                    rx.el.p("Gescon tracks your hand through a webcam feed and maps finger positions and pinches directly to cursor movement, clicks, and scroll — no mouse required.", class_name="lede"),
                    rx.el.div(
                        rx.el.a("Try the live demo →", href="/demo", class_name="btn btn-primary"),
                        rx.el.a("Run it locally", href="/install", class_name="btn btn-ghost"),
                        class_name="hero-actions"
                    ),
                ),
                rx.el.div(
                    rx.el.div("TRACKING ", rx.el.span("●"), " 21 LANDMARKS", class_name="visual-tag"),
                    rx.el.canvas(id="ambientCanvas"),
                    class_name="hero-visual"
                ),
                class_name="hero"
            ),


            # CORE PORTALS (LINKS TO PAGES)
            rx.el.section(
                rx.el.h2("Interact with Gescon."),
                rx.el.p("Explore the gesture mapping database, launch the camera tool directly in your browser, or install the native package for full OS system control.", class_name="lede"),
                rx.el.div(
                    # Link 1: Gestures
                    rx.el.a(
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("☝️", class_name="card-icon"),
                                rx.el.div("Gesture Dictionary", class_name="card-title"),
                                rx.el.p("Browse our gesture-to-action database mapping hand landmarks and shapes to cursor, scroll, clicks, screenshots, and typing events.", class_name="card-desc"),
                                class_name="card-top"
                            ),
                            rx.el.div("View gesture map →", class_name="card-action"),
                        ),
                        href="/gestures",
                        class_name="glow-card"
                    ),
                    # Link 2: Live Demo
                    rx.el.a(
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("◎", class_name="card-icon", style={"color": "var(--cyan)"}),
                                rx.el.div("Live Browser Demo", class_name="card-title"),
                                rx.el.p("Test camera recognition inside your browser using MediaPipe WebAssembly. Move a target dot and simulate clicking via real-time pinches.", class_name="card-desc"),
                                class_name="card-top"
                            ),
                            rx.el.div("Open camera demo →", class_name="card-action"),
                        ),
                        href="/demo",
                        class_name="glow-card"
                    ),
                    # Link 3: Install
                    rx.el.a(
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("💻", class_name="card-icon"),
                                rx.el.div("Developer Guide", class_name="card-title"),
                                rx.el.p("Run our native app locally to control your operating system mouse cursor. View prerequisites, clone commands, and activate envs.", class_name="card-desc"),
                                class_name="card-top"
                            ),
                            rx.el.div("Get setup instructions →", class_name="card-action"),
                        ),
                        href="/install",
                        class_name="glow-card"
                    ),
                    class_name="features-grid"
                )
            ),

            # HOW IT WORKS (STEPPER)
            rx.el.section(
                rx.el.h2("How the mapping pipeline works."),
                rx.el.p("A multi-stage pipelines translates physical hand joints into responsive, smooth cursor inputs.", class_name="lede"),
                rx.el.div(
                    # Step 1
                    rx.el.div(
                        rx.el.div("01", class_name="step-num"),
                        rx.el.div(
                            rx.el.div("Image Capture", class_name="step-title"),
                            rx.el.p("Webcam feeds frame-by-frame images into the processing pipeline at a target rate of 30 frames per second, mirroring the coordinates horizontally for intuitive navigation.", class_name="step-desc"),
                            class_name="step-content"
                        ),
                        class_name="step-item"
                    ),
                    # Step 2
                    rx.el.div(
                        rx.el.div("02", class_name="step-num"),
                        rx.el.div(
                            rx.el.div("Landmark Localization", class_name="step-title"),
                            rx.el.p("MediaPipe parses the hand contours to calculate 21 distinct 3D landmarks (joint coordinates) on a single tracking target with high spatial resolution.", class_name="step-desc"),
                            class_name="step-content"
                        ),
                        class_name="step-item"
                    ),
                    # Step 3
                    rx.el.div(
                        rx.el.div("03", class_name="step-num"),
                        rx.el.div(
                            rx.el.div("Normalizing Distances", class_name="step-title"),
                            rx.el.p("Angles and fingertip distances are normalized based on hand size (wrist to middle joint distance), rendering controls invariant to camera distance.", class_name="step-desc"),
                            class_name="step-content"
                        ),
                        class_name="step-item"
                    ),
                    # Step 4
                    rx.el.div(
                        rx.el.div("04", class_name="step-num"),
                        rx.el.div(
                            rx.el.div("Smoothing & Output Execution", class_name="step-title"),
                            rx.el.p("Exponential Moving Average (EMA) filters cursor movements to avoid hand jitter, while OS level commands (click, drag, double-click, screenshot, type) execute via PyAutoGUI.", class_name="step-desc"),
                            class_name="step-content"
                        ),
                        class_name="step-item"
                    ),
                    class_name="stepper"
                )
            ),

            # WHY GESCON
            rx.el.section(
                rx.el.h2("Designed for speed & accessibility."),
                rx.el.p("Gescon redefines desktop interaction without the need for expensive or bulky equipment.", class_name="lede"),
                rx.el.div(
                    # benefit 1
                    rx.el.div(
                        rx.el.div("♿", class_name="why-icon"),
                        rx.el.div("Accessibility", class_name="why-title"),
                        rx.el.p("Provides an ergonomic, hands-free computer control option for users with physical mobility constraints.", class_name="why-desc"),
                        class_name="why-card span-2"
                    ),
                    # benefit 2
                    rx.el.div(
                        rx.el.div("⚡", class_name="why-icon"),
                        rx.el.div("Ultra Low Latency", class_name="why-title"),
                        rx.el.p("MediaPipe compiles optimized WASM and C++ threads to track hand motion in milliseconds.", class_name="why-desc"),
                        class_name="why-card"
                    ),
                    # benefit 3
                    rx.el.div(
                        rx.el.div("⚙️", class_name="why-icon"),
                        rx.el.div("Customizable", class_name="why-title"),
                        rx.el.p("Easily adjust threshold limits, map custom fingers configurations, or assign new hotkeys inside local config files.", class_name="why-desc"),
                        class_name="why-card"
                    ),
                    # benefit 4
                    rx.el.div(
                        rx.el.div("🎥", class_name="why-icon"),
                        rx.el.div("Zero Extras", class_name="why-title"),
                        rx.el.p("Works on any standard computer webcam — no specialized hardware, infrared cameras, or ring markers required.", class_name="why-desc"),
                        class_name="why-card span-2"
                    ),
                    class_name="why-grid"
                )
            ),
        ),
        footer_section(),
        rx.script(src="/main.js"),
        class_name=State.theme
    )


def gestures_page() -> rx.Component:
    """Detailed Gesture Map Page."""
    return rx.el.div(
        rx.el.div(class_name="grid-bg"),
        header_section(),
        rx.el.main(
            rx.el.section(
                rx.el.a("← Back to Homepage", href="/", class_name="back-btn"),
                rx.el.h2("One hand, eight controls."),
                rx.el.p("Each landmark relationship — the distance and position between fingertips — is translated into a distinct system-level action. Customize settings inside Project.py.", class_name="lede"),
                
                rx.el.div(
                    # card 1
                    rx.el.div(
                        rx.el.span("☝️", class_name="glyph"),
                        rx.el.div("Point", class_name="gname"),
                        rx.el.div("Index finger extended, others curled. Drives smooth, responsive cursor movement.", class_name="gdesc"),
                        rx.el.div("→ MOVE CURSOR", class_name="gaction"),
                        class_name="gcard"
                    ),
                    # card 2
                    rx.el.div(
                        rx.el.span("🤏", class_name="glyph"),
                        rx.el.div("Single Pinch", class_name="gname"),
                        rx.el.div("Thumb and index fingertip pinch together. Simulates a standard single left click.", class_name="gdesc"),
                        rx.el.div("→ LEFT CLICK", class_name="gaction"),
                        class_name="gcard"
                    ),
                    # card 3
                    rx.el.div(
                        rx.el.span("⚡", class_name="glyph"),
                        rx.el.div("Double Pinch", class_name="gname"),
                        rx.el.div("Two quick thumb-and-index pinches within 0.4 seconds triggers double click.", class_name="gdesc"),
                        rx.el.div("→ DOUBLE CLICK", class_name="gaction"),
                        class_name="gcard"
                    ),
                    # card 4
                    rx.el.div(
                        rx.el.span("👆", class_name="glyph"),
                        rx.el.div("Right Click", class_name="gname"),
                        rx.el.div("Pinch thumb and middle finger together. Simulates a standard single right click.", class_name="gdesc"),
                        rx.el.div("→ RIGHT CLICK", class_name="gaction"),
                        class_name="gcard"
                    ),
                    # card 5
                    rx.el.div(
                        rx.el.span("🎯", class_name="glyph"),
                        rx.el.div("Drag & Drop", class_name="gname"),
                        rx.el.div("Pinch thumb and index finger, then hold and move your hand to drag items.", class_name="gdesc"),
                        rx.el.div("→ DRAG & DROP", class_name="gaction"),
                        class_name="gcard"
                    ),
                    # card 6
                    rx.el.div(
                        rx.el.span("↕️", class_name="glyph"),
                        rx.el.div("Scroll Mode", class_name="gname"),
                        rx.el.div("Extend all 4 fingers. Upper zone of active area scrolls up, lower zone scrolls down.", class_name="gdesc"),
                        rx.el.div("→ SCROLL UP / DOWN", class_name="gaction"),
                        class_name="gcard"
                    ),
                    # card 7
                    rx.el.div(
                        rx.el.span("📸", class_name="glyph"),
                        rx.el.div("Screenshot", class_name="gname"),
                        rx.el.div("Pinch thumb and pinky finger (peace sign with pinky touch) to capture the screen.", class_name="gdesc"),
                        rx.el.div("→ TAKE SCREENSHOT", class_name="gaction"),
                        class_name="gcard"
                    ),
                    # card 8
                    rx.el.div(
                        rx.el.span("⌨️", class_name="glyph"),
                        rx.el.div("Type Letter", class_name="gname"),
                        rx.el.div("Make a fist, then release specific fingers: Index (types A), Index+Middle (types B), Index+Middle+Ring (types C).", class_name="gdesc"),
                        rx.el.div("→ TYPE KEYBOARD A/B/C", class_name="gaction"),
                        class_name="gcard"
                    ),
                    class_name="gesture-grid"
                )
            )
        ),
        footer_section(),
        rx.script(src="/main.js"),
        class_name=State.theme
    )


def demo_page() -> rx.Component:
    """Live Hand Tracking Webcam Canvas Demo."""
    return rx.el.div(
        rx.el.div(class_name="grid-bg"),
        header_section(),
        rx.el.main(
            rx.el.section(
                rx.el.a("← Back to Homepage", href="/", class_name="back-btn"),
                rx.el.h2("Webcam hand tracking."),
                rx.el.p("This runs real-time on-device landmark recognition using WebAssembly. Allow camera permissions, point with your index finger inside the camera viewport, and pinch your thumb and index together to click.", class_name="lede"),
                
                rx.el.div(
                    # Combined Sandbox & Native Control Card
                    rx.el.div(
                        # Toolbar
                        rx.el.div(
                            rx.el.span(
                                rx.el.span(class_name="dot"),
                                rx.el.span("Camera off", id="statusText"),
                                class_name="status-pill",
                                id="statusPill"
                            ),
                            rx.el.button("Enable camera", class_name="btn btn-primary", id="startBtn", style={"cursor": "pointer", "border": "none"}),
                            style={"display": "flex", "alignItems": "center", "justifyContent": "space-between", "flexWrap": "wrap", "gap": "12px"}
                        ),
                        # Demo grid
                        rx.el.div(
                            # Video box (Left column)
                            rx.el.div(
                                rx.el.video(id="video", autoplay=True, playsinline=True, muted=True),
                                rx.el.canvas(id="overlay"),
                                rx.el.div(
                                    rx.el.span("◎"),
                                    rx.el.span("Camera feed appears here.", rx.el.br(), "Nothing is recorded or sent anywhere — tracking runs entirely on-device."),
                                    class_name="video-placeholder",
                                    id="placeholder"
                                ),
                                class_name="video-box",
                                id="videoBox"
                            ),
                            # Stack box (Right column)
                            rx.el.div(
                                # Pad box
                                rx.el.div(
                                    rx.el.div("CURSOR PAD", class_name="pad-label"),
                                    rx.el.div(
                                        rx.el.div(id="cursorDot"),
                                        class_name="pad",
                                        id="pad"
                                    ),
                                    rx.el.div(
                                        rx.el.span("PINCH_DIST: ", rx.el.b("—", id="pinchVal")),
                                        rx.el.span("STATE: ", rx.el.b("IDLE", id="stateVal")),
                                        class_name="readout"
                                    ),
                                    class_name="pad-box"
                                ),
                                # Spacer
                                rx.el.div(style={"height": "24px"}),
                                # Native Desktop OS Control Center
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.div("Desktop OS Control", class_name="card-title"),
                                        rx.cond(
                                            State.desktop_control_active,
                                            rx.el.span(
                                                rx.el.span(class_name="badge-dot"),
                                                "ACTIVE (OS Control)",
                                                class_name="status-badge active"
                                            ),
                                            rx.el.span(
                                                rx.el.span(class_name="badge-dot"),
                                                "DISCONNECTED",
                                                class_name="status-badge"
                                            )
                                        ),
                                        class_name="control-status-box",
                                        style={"borderBottom": "1px solid var(--line)", "paddingBottom": "16px", "marginBottom": "16px"}
                                    ),
                                    rx.el.div(
                                        rx.cond(
                                            State.desktop_control_active,
                                            rx.el.button(
                                                "Terminate Control Session",
                                                on_click=State.toggle_desktop_control,
                                                class_name="btn btn-danger",
                                                style={"width": "100%", "justifyContent": "center", "cursor": "pointer"}
                                            ),
                                            rx.el.button(
                                                "Launch OS Controller",
                                                on_click=State.toggle_desktop_control,
                                                class_name="btn btn-primary",
                                                style={"width": "100%", "justifyContent": "center", "cursor": "pointer"}
                                            )
                                        ),
                                        class_name="control-actions",
                                        style={"marginTop": "12px"}
                                    ),
                                    class_name="control-center",
                                    style={"padding": "24px", "borderRadius": "10px", "border": "1px solid var(--line)", "background": "var(--panel-2)", "boxShadow": "none", "minHeight": "auto"}
                                ),
                                style={"display": "flex", "flexDirection": "column"}
                            ),
                            class_name="demo-grid"
                        ),
                        class_name="demo-wrap",
                        style={"marginTop": "0"}
                    )
                )
            )
        ),
        footer_section(),
        rx.script(src="/main.js"),
        class_name=State.theme
    )


def install_page() -> rx.Component:
    """Prerequisites and Run Instructions."""
    return rx.el.div(
        rx.el.div(class_name="grid-bg"),
        header_section(),
        rx.el.main(
            rx.el.section(
                rx.el.a("← Back to Homepage", href="/", class_name="back-btn"),
                rx.el.h2("Run native Gescon."),
                rx.el.p("The desktop utility controls your actual OS cursor. Clone the source repository, setup a virtual env, install requirements, and execute the python script.", class_name="lede"),
                
                rx.el.div(
                    rx.el.span("# clone and enter the project", class_name="c-muted"), rx.el.br(),
                    rx.el.span("git clone", class_name="c-text"), " https://github.com/SilentShadowDev/Gescon.git", rx.el.br(),
                    rx.el.span("cd", class_name="c-text"), " Gescon",
                    class_name="code-block"
                ),
                rx.el.div(
                    rx.el.p(
                        "View the repository on GitHub: ",
                        rx.el.a(
                            "https://github.com/SilentShadowDev/Gescon/tree/main",
                            href="https://github.com/SilentShadowDev/Gescon/tree/main",
                            target="_blank",
                            style={"color": "var(--cyan)", "textDecoration": "underline", "fontWeight": "500"}
                        )
                    ),
                    rx.el.p(
                        "Note: A detailed installation guide, prerequisites, and system troubleshooting are documented in the repository's README.md file.",
                        style={"marginTop": "8px", "color": "var(--muted)"}
                    ),
                    style={"marginTop": "28px", "fontSize": "14.5px", "lineHeight": "1.6"}
                )
            )
        ),
        footer_section(),
        rx.script(src="/main.js"),
        class_name=State.theme
    )


def roadmap_page() -> rx.Component:
    """Roadmap and Vision Page showing current capabilities and future aspirations."""
    return rx.el.div(
        rx.el.div(class_name="grid-bg"),
        header_section(),
        rx.el.main(
            rx.el.section(
                rx.el.a("← Back to Homepage", href="/", class_name="back-btn"),
                rx.el.h2("Vision & Roadmap"),
                rx.el.p("Explore the current features of Gescon and our aspirations for the next generations of touchless interface systems.", class_name="lede"),
                
                rx.el.div(
                    # Left column: Current Capabilities
                    rx.el.div(
                        rx.el.h3("Current Capabilities", style={"fontFamily": "var(--disp)", "fontSize": "22px", "marginBottom": "20px", "color": "var(--cyan)", "fontWeight": "600"}),
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("🎯", class_name="glyph"),
                                rx.el.div("Precision Cursor Control", class_name="gname"),
                                rx.el.div("Horizontal mirroring, screen bounds calibration, and Exponential Moving Average smoothing algorithms.", class_name="gdesc"),
                                class_name="gcard",
                                style={"marginBottom": "16px"}
                            ),
                            rx.el.div(
                                rx.el.span("🤏", class_name="glyph"),
                                rx.el.div("Gestures & Clicking", class_name="gname"),
                                rx.el.div("Supports single click pinch, double-pinch, drag and drop, scrolling, and screenshots.", class_name="gdesc"),
                                class_name="gcard",
                                style={"marginBottom": "16px"}
                            ),
                            rx.el.div(
                                rx.el.span("⌨️", class_name="glyph"),
                                rx.el.div("Virtual Keyboard Input", class_name="gname"),
                                rx.el.div("Gesture signature mapping enabling touchless key typing (e.g. typing characters by releasing specific curled fingers).", class_name="gdesc"),
                                class_name="gcard"
                            ),
                        ),
                        style={"flex": "1", "minWidth": "280px"}
                    ),
                    
                    # Right column: Future Aspirations
                    rx.el.div(
                        rx.el.h3("Future Aspirations", style={"fontFamily": "var(--disp)", "fontSize": "22px", "marginBottom": "20px", "color": "var(--amber)", "fontWeight": "600"}),
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("⚙️", class_name="glyph"),
                                rx.el.div("Visual Customization Engine", class_name="gname"),
                                rx.el.div("Planned web dashboard allowing users to record dynamic gesture profiles and map them to custom macros and apps.", class_name="gdesc"),
                                class_name="gcard",
                                style={"marginBottom": "16px"}
                            ),
                            rx.el.div(
                                rx.el.span("🧠", class_name="glyph"),
                                rx.el.div("Deep Learning Models", class_name="gname"),
                                rx.el.div("Transitioning from threshold angles to lightweight neural networks to recognize sequential, continuous hand shapes.", class_name="gdesc"),
                                class_name="gcard",
                                style={"marginBottom": "16px"}
                            ),
                            rx.el.div(
                                rx.el.span("👐", class_name="glyph"),
                                rx.el.div("Two-Handed Interactions", class_name="gname"),
                                rx.el.div("Expanding recognition targets to multiple hands for natural zooming, scaling, rotation, and complex gaming controls.", class_name="gdesc"),
                                class_name="gcard"
                            ),
                        ),
                        style={"flex": "1", "minWidth": "280px"}
                    ),
                    style={"display": "flex", "gap": "32px", "marginTop": "48px", "flexWrap": "wrap"}
                )
            )
        ),
        footer_section(),
        rx.script(src="/main.js"),
        class_name=State.theme
    )


app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap",
        "/style.css"
    ]
)

app.add_page(index, route="/")
app.add_page(gestures_page, route="/gestures")
app.add_page(demo_page, route="/demo")
app.add_page(install_page, route="/install")
app.add_page(roadmap_page, route="/roadmap")
