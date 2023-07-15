from re import match

from django.core.exceptions import ValidationError


def validate_color(color):
    hex_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    if not match(hex_pattern, color):
        raise ValidationError('Цвет должен быть в формате HEX.')
