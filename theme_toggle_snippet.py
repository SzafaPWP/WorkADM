# theme_toggle_snippet.py
# Snippet to integrate into your main_window.py to add a theme toggle (two themes: dark and light)

# 1) Put theme_dark.py and theme_light.py next to your main_window.py
# 2) Add this snippet into MainWindow.__init__ after super().__init__() or at the end of setup.
# Example usage:
#     self.current_theme = 'dark'
#     import theme_dark, theme_light
#     theme_dark.apply_theme(self)

def init_theme_toggle(self):
    # self must be the tk.Tk root or a Toplevel used as main root
    import theme_dark, theme_light
    self._theme_modules = {'dark': theme_dark, 'light': theme_light}
    # start with dark by default
    self.current_theme = getattr(self, 'current_theme', 'dark')
    try:
        self._theme_modules[self.current_theme].apply_theme(self)
    except Exception:
        pass

def toggle_theme(self):
    # switch theme and reapply styles
    self.current_theme = 'light' if getattr(self, 'current_theme', 'dark') == 'dark' else 'dark'
    try:
        self._theme_modules[self.current_theme].apply_theme(self)
    except Exception:
        pass

# To hook into a menu or a button:
# btn = ttk.Button(toolbar, text='Toggle theme', command=lambda: toggle_theme(self))
# or add menu command that calls toggle_theme(self)
