from rest_framework import serializers
from .models import CustomUser, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "created_at",
        )
        read_only_fields = ("user_id", "created_at")


class MessageSerializer(serializers.ModelSerializer):
    message_body = serializers.CharField()

    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        write_only=True,
        source="sender"
    )

    class Meta:
        model = Message
        fields = (
            "message_id",
            "sender",
            "sender_id",
            "message_body",
            "sent_at",
        )
        read_only_fields = ("message_id", "sent_at")

    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be blank.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        many=True,
        write_only=True,
        source="participants"
    )

    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            "conversation_id",
            "participants",
            "participant_ids",
            "created_at",
            "last_message",
            "messages",
        )
        read_only_fields = ("conversation_id", "created_at", "last_message")

    def get_last_message(self, obj):
        last = obj.messages.order_by("-sent_at").first()
        return last.message_body[:100] if last else None

    def validate_participant_ids(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                "A conversation requires at least two participants."
            )
        return value

    def create(self, validated_data):
        participants = validated_data.pop("participants", [])
        convo = Conversation.objects.create(**validated_data)
        convo.participants.set(participants)
        return convo
