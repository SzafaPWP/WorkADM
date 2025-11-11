# theme_toggle_snippet.py
def init_theme_toggle(self):
    import theme_dark, theme_light
    self._theme_modules = {'dark': theme_dark, 'light': theme_light}
    # start with dark by default if available
    self.current_theme = getattr(self, 'current_theme', 'dark')
    try:
        self._theme_modules[self.current_theme].apply_theme(self)
    except Exception:
        pass

def toggle_theme(self):
    self.current_theme = 'light' if getattr(self, 'current_theme', 'dark') == 'dark' else 'dark'
    try:
        self._theme_modules[self.current_theme].apply_theme(self)
    except Exception:
        pass
