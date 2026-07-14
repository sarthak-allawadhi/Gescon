"""GestureMouse Reflex Web Application Implementation"""

import subprocess
import os
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
                venv_python = os.path.join(current_dir, "venv", "bin", "python")
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
            rx.el.a("GestureMouse", href="/"),
            class_name="logo"
        ),
        rx.el.nav(
            rx.el.a("Home", href="/"),
            rx.el.a("Gestures", href="/gestures"),
            rx.el.a("Live Demo", href="/demo"),
            rx.el.a("Install", href="/install"),
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
                    rx.el.div("Computer Vision · Python · MediaPipe", class_name="eyebrow"),
                    rx.el.h1("Control your cursor", rx.el.br(), "with your hand."),
                    rx.el.p("GestureMouse tracks your hand through a webcam feed and maps finger positions and pinches directly to cursor movement, clicks, and scroll — no mouse required.", class_name="lede"),
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

            # STACK STRIP
            rx.el.div(
                rx.el.span(rx.el.b("Python")),
                rx.el.span(rx.el.b("OpenCV")),
                rx.el.span(rx.el.b("MediaPipe Hands")),
                rx.el.span(rx.el.b("PyAutoGUI")),
                rx.el.span(rx.el.b("NumPy")),
                class_name="strip"
            ),

            # CORE PORTALS (LINKS TO PAGES)
            rx.el.section(
                rx.el.div("Explore Systems", class_name="eyebrow"),
                rx.el.h2("Interact with GestureMouse."),
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
                rx.el.div("Technical Pipeline", class_name="eyebrow"),
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

            # WHY GESTUREMOUSE
            rx.el.section(
                rx.el.div("System Benefits", class_name="eyebrow"),
                rx.el.h2("Designed for speed & accessibility."),
                rx.el.p("GestureMouse redefines desktop interaction without the need for expensive or bulky equipment.", class_name="lede"),
                rx.el.div(
                    # benefit 1
                    rx.el.div(
                        rx.el.div("♿", class_name="why-icon"),
                        rx.el.div("Accessibility", class_name="why-title"),
                        rx.el.p("Provides an ergonomic, hands-free computer control option for users with physical mobility constraints.", class_name="why-desc"),
                        class_name="why-card"
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
                        class_name="why-card"
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
                rx.el.div("Gesture Dictionary", class_name="eyebrow"),
                rx.el.h2("One hand, five controls."),
                rx.el.p("Each landmark relationship — the distance and position between fingertips — is translated into a distinct system-level action. Edit util.py to map your own gestures.", class_name="lede"),
                
                rx.el.div(
                    # card 1
                    rx.el.div(
                        rx.el.span("☝️", class_name="glyph"),
                        rx.el.div("Point", class_name="gname"),
                        rx.el.div("Index finger extended, others curled. Fingertip position drives cursor movement.", class_name="gdesc"),
                        rx.el.div("→ MOVE CURSOR", class_name="gaction"),
                        class_name="gcard"
                    ),
                    # card 2
                    rx.el.div(
                        rx.el.span("🤏", class_name="glyph"),
                        rx.el.div("Pinch", class_name="gname"),
                        rx.el.div("Thumb and index tip come within a threshold distance of each other.", class_name="gdesc"),
                        rx.el.div("→ LEFT CLICK", class_name="gaction"),
                        class_name="gcard"
                    ),
                    # card 3
                    rx.el.div(
                        rx.el.span("✌️", class_name="glyph"),
                        rx.el.div("Two-finger pinch", class_name="gname"),
                        rx.el.div("Thumb meets both index and middle fingertips simultaneously.", class_name="gdesc"),
                        rx.el.div("→ RIGHT CLICK", class_name="gaction"),
                        class_name="gcard"
                    ),
                    # card 4
                    rx.el.div(
                        rx.el.span("✊", class_name="glyph"),
                        rx.el.div("Fist hold", class_name="gname"),
                        rx.el.div("All fingertips curled toward the palm and held.", class_name="gdesc"),
                        rx.el.div("→ DRAG", class_name="gaction"),
                        class_name="gcard"
                    ),
                    # card 5
                    rx.el.div(
                        rx.el.span("🖐️", class_name="glyph"),
                        rx.el.div("Open palm", class_name="gname"),
                        rx.el.div("All five fingers extended and spread.", class_name="gdesc"),
                        rx.el.div("→ RELEASE / IDLE", class_name="gaction"),
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
                rx.el.div("Live Demo", class_name="eyebrow"),
                rx.el.h2("Webcam hand tracking."),
                rx.el.p("This runs real-time on-device landmark recognition using WebAssembly. Allow camera permissions, point with your index finger inside the camera viewport, and pinch your thumb and index together to click.", class_name="lede"),
                
                rx.el.div(
                    # Left Card: Browser Simulator Sandbox
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
                            # Video box
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
                            class_name="demo-grid"
                        ),
                        class_name="demo-wrap",
                        style={"marginTop": "0"}
                    ),
                    # Right Card: Native Desktop OS Control Center
                    rx.el.div(
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
                                class_name="control-status-box"
                            ),
                            rx.el.div(
                                rx.el.p("Control your actual operating system cursor using the native Python engine. This launches the computer vision tracking process on your machine, opening the OpenCV tracking monitor window."),
                                rx.el.p("To configure gesture action mappings or threshold ratios, adjust settings inside Project.py and util.py."),
                                rx.el.p(
                                    rx.el.span("⚠️ ", style={"marginRight": "4px"}),
                                    rx.el.b("Safety Fail-Safe: "),
                                    "Move your hand to the top-left corner of the monitor screen at any time to trigger an emergency stop."
                                ),
                                class_name="control-body"
                            ),
                            class_name="control-header"
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
                            class_name="control-actions"
                        ),
                        class_name="control-center"
                    ),
                    class_name="demo-split-grid"
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
                rx.el.div("Get Started", class_name="eyebrow"),
                rx.el.h2("Run native GestureMouse."),
                rx.el.p("The desktop utility controls your actual OS cursor. Clone the source repository, setup a virtual env, install requirements, and execute the python script.", class_name="lede"),
                
                rx.el.div(
                    rx.el.span("# clone and enter the project", class_name="c-muted"), rx.el.br(),
                    rx.el.span("git clone", class_name="c-text"), " https://github.com/your-username/gesture-mouse.git", rx.el.br(),
                    rx.el.span("cd", class_name="c-text"), " gesture-mouse", rx.el.br(), rx.el.br(),
                    rx.el.span("# set up environment", class_name="c-muted"), rx.el.br(),
                    rx.el.span("python -m venv venv && venv\\Scripts\\activate", class_name="c-text"), rx.el.br(),
                    rx.el.span("pip install", class_name="c-text"), " opencv-python mediapipe pyautogui numpy", rx.el.br(), rx.el.br(),
                    rx.el.span("# run it", class_name="c-muted"), rx.el.br(),
                    rx.el.span("python", class_name="c-text"), " gesture_mouse.py",
                    class_name="code-block"
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
