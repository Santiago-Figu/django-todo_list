from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'lastname', 'username', 'email', 'password', 'cellphone', 'team']
        extra_kwargs = {
            'username': {'required': True},
            'name': {'required': True},
            'lastname': {'required': True},
        }

    def validate_email(self, value):
        """
        Valida que el email sea único (excepto para el usuario actual en updates).
        """
        instance = getattr(self, 'instance', None)
        if instance and instance.email == value:
            return value  # Permite el mismo email si es el mismo usuario
        
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def create(self, validated_data):
        user = User(
            name=validated_data['name'],
            lastname=validated_data['lastname'],
            username=validated_data['username'],
            cellphone=validated_data.get('cellphone'),
            team=validated_data.get('team'),
        )
        user.set_email(validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def to_representation(self, instance):
        """Descifra el email al mostrar los datos."""
        data = super().to_representation(instance)
        try:
            data['email'] = instance.get_email()  # Descifra el email
        except Exception as e:
            print(f"Error al descifrar el email: {e}")
            data['email'] = None  # Opcional: manejar el error de forma elegante
        return data
    
    def update(self, instance, validated_data):
        """Actualización segura con cifrado."""
        password = validated_data.pop('password', None)
        email = validated_data.pop('email', None)

        # Actualización de campos no sensibles
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Campos sensibles (cifrados)
        if password:
            instance.set_password(password)
        if email:
            instance.set_email(email)

        instance.save()
        return instance