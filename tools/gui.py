import os
import sys

import re

from abc import ABC, abstractmethod

import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer

from dataclasses import dataclass

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

FONT_PATH = os.path.join(
    CURRENT_PATH,
    "NotoSansJP.ttf"
)

with open(os.path.join(CURRENT_PATH, "verify.txt"), "r", encoding="utf-8") as verifier_data:
    verifier_text = verifier_data.read()

with open(os.path.join(CURRENT_PATH, "challenge.txt"), "r", encoding="utf-8") as verifier_data:
    challenge_text = verifier_data.read()

segments = re.split(r'[。，、「」『』？！\n]+', verifier_text)


class Drawable(ABC):
    needs_cjk: bool = False
    @abstractmethod
    def draw(self):
        pass


@dataclass
class TextEditor(Drawable):
    content: str = challenge_text
    seg_index: int = 0
    needs_cjk: bool = True
    open_saved_popup: bool = False
    
    save_path: str = None
    save_file: str = "output.txt"
    cursor_pos: int = 0

    def draw(self, cjk_font):
        imgui.set_next_window_size(800, 800, imgui.ONCE)
        with imgui.begin("Input"):

            imgui.push_font(cjk_font)

            imgui.separator()

            to_write = None
            current_segment = segments[self.seg_index]

            if imgui.button("<"):
                if self.seg_index != 0:
                    self.seg_index -= 1
            
            imgui.same_line()

            if imgui.button(">"):
                if self.seg_index != len(segments):
                    self.seg_index += 1

            imgui.same_line()

            imgui.text("Save data to ")
            imgui.same_line()
            imgui.push_id("save_file_name")
            changed, self.save_file = imgui.input_text(
                "", self.save_file, -1
            )
            imgui.pop_id()


            for index, character in enumerate(current_segment):
                imgui.push_id(f"index")
                if imgui.button(character):
                    to_write = character
                imgui.pop_id()
                imgui.same_line()

            imgui.separator()

            if to_write is not None:
                # self.content += to_write
                self._insert_chars(self.cursor_pos, "hello", )
                to_write = None
                imgui.set_keyboard_focus_here()

            changed, self.content = imgui.input_text_multiline(
                "", self.content, -1, 750, 750, imgui.INPUT_TEXT_CALLBACK_ALWAYS,
                self._set_cursor_pos)
            
            imgui.pop_font()

            if self.open_saved_popup:
                imgui.open_popup("Saved")
                self.open_saved_popup = False

            if imgui.begin_popup("Saved").opened:
                imgui.text(f"Saved to file {self.save_path}")
                imgui.end_popup()

    def save(self):
        self.save_path = os.path.join(
            CURRENT_PATH,
            self.save_file
        )

        with open(self.save_path, "w", encoding="utf-8") as save_file:
            save_file.write(self.content)
            self.open_saved_popup = True


    def _set_cursor_pos(self, event):
        self.cursor_pos = event.cursor_pos
        self._insert_chars = event.insert_chars
        print(self.cursor_pos)


def frame_commands(cjk_font):
    io = imgui.get_io()

    if io.key_ctrl and io.keys_down[glfw.KEY_Q]:
        sys.exit(0)

    if io.key_ctrl and io.keys_down[glfw.KEY_S]:
        drawables[0].save()

    with imgui.begin_main_menu_bar() as main_menu_bar:
        if main_menu_bar.opened:
            with imgui.begin_menu("File", True) as file_menu:
                if file_menu.opened:
                    clicked_quit, selected_quit = imgui.menu_item("Quit", "Ctrl+Q")
                    if clicked_quit:
                        sys.exit(0)
                    clicked_save, selected_save = imgui.menu_item("Save", "Ctrl+S")
                    if clicked_save:
                        drawables[0].save()

    for drawable in drawables:
        assert isinstance(drawable, Drawable)
        if drawable.needs_cjk:
            drawable.draw(cjk_font)
        else:
            drawable.draw()


drawables = [TextEditor()]

def render_frame(impl, window, cjk_font):
    glfw.poll_events()
    impl.process_inputs()
    imgui.new_frame()

    gl.glClearColor(0.1, 0.1, 0.1, 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    frame_commands(cjk_font)

    imgui.render()
    impl.render(imgui.get_draw_data())
    glfw.swap_buffers(window)


def impl_glfw_init():
    width, height = 1600, 900
    window_name = "minimal ImGui/GLFW3 example"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        sys.exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        sys.exit(1)

    return window


def main():
    imgui.create_context()
    window = impl_glfw_init()

    impl = GlfwRenderer(window)

    ranges = imgui.core.GlyphRanges([
        0x0020, 0x024f,     # Latin
        0x3000, 0x30ff,     # CJK Symbols + Kana
        0x3400, 0x4dbf,     # CJK Extension A
        0x4e00, 0x9fff,     # CJK Ideographs
        # 0x20000, 0x2B73F    # CJK Extension B, C
        0
    ])

    io = imgui.get_io()
    jb = io.fonts.add_font_from_file_ttf(FONT_PATH, 30, glyph_ranges=ranges) if FONT_PATH is not None else None
    impl.refresh_font_texture()

    while not glfw.window_should_close(window):
        render_frame(impl, window, jb)

    impl.shutdown()
    glfw.terminate()


if __name__ == "__main__":
    main()