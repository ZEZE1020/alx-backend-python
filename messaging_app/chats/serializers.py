from rest_framework import serializers
from .models import CustomUser, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    """
    Serialize CustomUser instances.
    """
    class Meta:
        model = CustomUser
        fields = (
            'user_id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'created_at',
        )
        read_only_fields = ('user_id', 'created_at')


class MessageSerializer(serializers.ModelSerializer):
    """
    Serialize Message instances, nesting sender details.
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        write_only=True,
        source='sender',
        help_text="ID of the user sending this message"
    )

    class Meta:
        model = Message
        fields = (
            'message_id',
            'sender',
            'sender_id',
            'message_body',
            'sent_at',
        )
        read_only_fields = ('message_id', 'sent_at')


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serialize Conversation instances, nesting participants and their messages.
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        many=True,
        write_only=True,
        source='participants',
        help_text="List of user IDs participating in the conversation"
    )
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = (
            'conversation_id',
            'participants',
            'participant_ids',
            'created_at',
            'messages',
        )
        read_only_fields = ('conversation_id', 'created_at')

    def create(self, validated_data):
        participants = validated_data.pop('participants', [])
        convo = Conversation.objects.create(**validated_data)
        convo.participants.set(participants)
        return convo
