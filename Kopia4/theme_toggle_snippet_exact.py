# theme_toggle_snippet_exact.py
def init_theme_toggle_exact(self, default='dark'):
    try:
        import theme_dark_exact as dark_mod
        import theme_light_improved as light_mod
        self._theme_modules = {'dark': dark_mod, 'light': light_mod}
    except Exception:
        self._theme_modules = {}
    self.current_theme = default if default in self._theme_modules else next(iter(self._theme_modules), 'none')
    if self.current_theme != 'none':
        try:
            self._theme_modules[self.current_theme].apply_theme(self)
        except Exception:
            pass

def toggle_theme_exact(self):
    if not getattr(self, '_theme_modules', None):
        return
    self.current_theme = 'light' if getattr(self, 'current_theme', 'dark') == 'dark' else 'dark'
    try:
        self._theme_modules[self.current_theme].apply_theme(self)
    except Exception:
        pass
