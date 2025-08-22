from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    list:
    Return all conversations.

    create:
    Start a new conversation by posting participant_ids.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer


class MessageViewSet(viewsets.ModelViewSet):
    """
    list:
    List all messages for a given conversation.

    create:
    Send a new message to an existing conversation.
    """
    serializer_class = MessageSerializer

    def get_queryset(self):
        convo_id = self.kwargs.get("conversation_pk")
        try:
            # ensure the parent conversation exists
            Conversation.objects.get(conversation_id=convo_id)
        except Conversation.DoesNotExist:
            raise NotFound(detail="Conversation not found.")
        # filter messages by conversation
        return Message.objects.filter(conversation__conversation_id=convo_id).order_by("sent_at")

    def perform_create(self, serializer):
        convo_id = self.kwargs.get("conversation_pk")
        try:
            conversation = Conversation.objects.get(conversation_id=convo_id)
        except Conversation.DoesNotExist:
            raise NotFound(detail="Conversation not found.")
        # attach the conversation FK before saving
        serializer.save(conversation=conversation)
