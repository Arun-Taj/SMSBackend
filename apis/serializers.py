from rest_framework import serializers
from .models import *
from PIL import Image
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom user data
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            # 'email': self.user.email,
            # Add any other fields you want
        }
        # Remove the refresh token from the response data
        return data

class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)  # Only for writing, not reading
    photo = serializers.ImageField(required=False, allow_null=True)
    passport_photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = AdminUser
        fields = ['id', 'url','username', 'full_name', 'password','gender', 'dob','photo', 'aadhar_no', 'address', 'town_village_city', 'district', 'state', 'country', 'pincode', 'nationality', 'religion', 'passport_photo', 'phone_number', 'alt_phone_number']

    def create(self, validated_data):
        # Create a new user and set the password securely
        user = AdminUser.objects.create(
            username=validated_data['username'],
            full_name=validated_data.get('full_name', ''),
            gender=validated_data.get('gender', ''),
            dob=validated_data.get('dob', ''),
            photo=validated_data.get('photo', ''),
            aadhar_no=validated_data.get('aadhar_no', ''),
            address=validated_data.get('address', ''),
            town_village_city=validated_data.get('town_village_city', ''),
            district=validated_data.get('district', ''),
            state=validated_data.get('state', ''),
            country=validated_data.get('country', ''),
            pincode=validated_data.get('pincode', ''),
            nationality=validated_data.get('nationality', ''),
            religion=validated_data.get('religion', ''),
            passport_photo=validated_data.get('passport_photo', ''),
            phone_number=validated_data.get('phone_number', ''),
            alt_phone_number=validated_data.get('alt_phone_number', ''),
        )
        user.set_password(validated_data['password'])  # Set the password securely
        user.save()
        return user
    

    def validate_photo(self, value):
        """Validate the uploaded image"""
        try:
            img = Image.open(value)
            img.verify()
        except (IOError, SyntaxError):
            raise serializers.ValidationError("Invalid image file")
        return value
    

    def validate_passport_photo(self, value):
        """Validate the uploaded image"""
        try:
            img = Image.open(value)
            img.verify()
        except (IOError, SyntaxError):
            raise serializers.ValidationError("Invalid image file")
        return value
    

    def update(self, instance, validated_data):
        # Check if the password is being updated
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    


class UpdateAdminUserSerializer(AdminUserSerializer):
    password = serializers.CharField(write_only=True, required=False)  # Only for writing, not reading
    username = serializers.CharField(write_only=True, required=False)  # Only for writing, not reading




class SchoolSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = School
        fields = '__all__'







class StudentSerializer(serializers.HyperlinkedModelSerializer):
    # rollNo = serializers.IntegerField(read_only=True)  # Add rollNo as a read-only field
    id = serializers.IntegerField(read_only=True)



    class Meta:
        model = Student
        fields = '__all__'



    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # representation['rollNo'] = self.context.get('rollNo', None)  # Use context if needed
        representation['id'] = instance.id  # or representation['id'] = instance.pk for primary key
        return representation


    def save(self, *args, **kwargs):
        request = self.context.get("request")  # Get request from context
        if request:
            # If this is a new instance, set the school
            if self.instance is None:
                self.validated_data['school'] = request.user.school
            else:
                # Only set the school if the instance already exists
                if not self.instance.school:
                    self.instance.school = request.user.school
        super().save(*args, **kwargs)


    