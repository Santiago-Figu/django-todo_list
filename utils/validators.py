import re

def clear_input_characters(cadena):
    """Elimina caracteres que no sean alfanumericos"""
    return re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]', '', cadena).strip()

def clear_input_num(cadena):
    """Elimina caracteres que no sean numericos"""
    return re.sub(r'[^0-9]', '', cadena).strip()