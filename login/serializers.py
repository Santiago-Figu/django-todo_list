from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    """Clase para crear un formulario sencillo de login aprocechando lo serializadores de Django sin utilizar un archivo html"""
    username = serializers.CharField(label="Usuario o Email")
    password = serializers.CharField(
        style={'input_type': 'password'},  # Para que se muestre como campo de contraseña
        write_only=True
    )

    def add_error(self, field, error):
        if field is None:
            field = 'non_field_errors'
        if field not in self._errors:
            self._errors[field] = []
        self._errors[field].append(error)