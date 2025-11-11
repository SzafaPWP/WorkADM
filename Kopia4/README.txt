TTK Themes Toggle - README
--------------------------

Files in this ZIP:
- theme_dark.py         : modern dark ttk theme (apply_theme(root))
- theme_light.py        : clean light ttk theme (apply_theme(root))
- theme_toggle_snippet.py: helper snippet to integrate with MainWindow (init and toggle functions)

Quick install:
1) Unzip into your project folder (next to main_window.py).
2) In MainWindow.__init__ (after super().__init__()), call:
       import theme_dark, theme_light
       self._theme_modules = {'dark': theme_dark, 'light': theme_light}
       self.current_theme = 'dark'  # or 'light'
       self._theme_modules[self.current_theme].apply_theme(self)
   OR use the init_theme_toggle(self) helper from theme_toggle_snippet.py.

3) Add a Toggle Theme button or menu that calls toggle_theme(self) (from snippet).

Notes:
- Themes use 'clam' ttk theme as base which is widely available.
- Colors, fonts and paddings are tuned for Windows; you can adjust font families if needed.
- Backup your original main_window.py before integrating; the snippet is non-destructive.
