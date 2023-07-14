from django.core.exceptions import ValidationError


def validate_image(image):
    if not image.name.endswith('.jpg') and not image.name.endswith('.png'):
        raise ValidationError('Изображение должно быть в формате JPG или PNG.')
