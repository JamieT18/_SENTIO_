"""
Accessibility and multi-language support utilities for Sentio 2.0
"""
from typing import Dict

class Accessibility:
    def __init__(self, language: str = 'en'):
        self.language = language
        self.translations = {
            'en': {
                'dashboard': 'Dashboard',
                'risk': 'Risk',
                'optimizer': 'Optimizer',
                'settings': 'Settings',
            },
            'es': {
                'dashboard': 'Tablero',
                'risk': 'Riesgo',
                'optimizer': 'Optimizador',
                'settings': 'Configuraciones',
            },
            # Add more languages as needed
        }

    def translate(self, key: str) -> str:
        return self.translations.get(self.language, {}).get(key, key)

    def set_language(self, language: str):
        if language in self.translations:
            self.language = language

    def get_available_languages(self) -> Dict[str, str]:
        return {lang: self.translations[lang]['dashboard'] for lang in self.translations}
