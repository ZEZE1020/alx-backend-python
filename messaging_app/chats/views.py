from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Prefetch
from .models import Conversation, Message, CustomUser
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    
    list:
    Return all conversations for the authenticated user.

    create:
    Start a new conversation by posting participant_ids.
    
    retrieve:
    Get a specific conversation with its messages.
    
    destroy:
    Delete a conversation (only if user is a participant).
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return conversations where the user is a participant."""
        user = self.request.user
        return Conversation.objects.filter(
            participants=user
        ).prefetch_related(
            'participants',
            Prefetch('messages', queryset=Message.objects.select_related('sender').order_by('-sent_at'))
        ).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        """Ensure the current user is added to the conversation."""
        conversation = serializer.save()
        # Add the current user as a participant if not already included
        if self.request.user not in conversation.participants.all():
            conversation.participants.add(self.request.user)

    def perform_destroy(self, instance):
        """Only allow deletion if user is a participant."""
        if self.request.user not in instance.participants.all():
            raise PermissionDenied("You can only delete conversations you participate in.")
        super().perform_destroy(instance)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a new participant to the conversation."""
        conversation = self.get_object()
        
        # Check if user is already a participant
        if request.user not in conversation.participants.all():
            raise PermissionDenied("Only participants can add new members.")
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_add = CustomUser.objects.get(user_id=user_id)
            conversation.participants.add(user_to_add)
            return Response(
                {'message': f'User {user_to_add.email} added to conversation'}, 
                status=status.HTTP_200_OK
            )
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def leave_conversation(self, request, pk=None):
        """Allow a user to leave a conversation."""
        conversation = self.get_object()
        
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not a participant in this conversation'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation.participants.remove(request.user)
        
        # If no participants left, delete the conversation
        if conversation.participants.count() == 0:
            conversation.delete()
            return Response(
                {'message': 'Left conversation and conversation was deleted'}, 
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'message': 'Left conversation successfully'}, 
            status=status.HTTP_200_OK
        )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages within conversations.
    
    list:
    List all messages for a given conversation (only for participants).

    create:
    Send a new message to an existing conversation.
    
    retrieve:
    Get a specific message.
    
    update/destroy:
    Update or delete messages (only by sender within time limit).
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return messages for a conversation if user is a participant."""
        convo_id = self.kwargs.get("conversation_pk")
        
        try:
            conversation = Conversation.objects.get(conversation_id=convo_id)
        except Conversation.DoesNotExist:
            raise NotFound(detail="Conversation not found.")
        
        # Check if user is a participant in the conversation
        if self.request.user not in conversation.participants.all():
            raise PermissionDenied("You must be a participant to view messages.")
        
        return Message.objects.filter(
            conversation__conversation_id=convo_id
        ).select_related('sender').order_by("sent_at")

    def perform_create(self, serializer):
        """Create a new message in the conversation."""
        convo_id = self.kwargs.get("conversation_pk")
        
        try:
            conversation = Conversation.objects.get(conversation_id=convo_id)
        except Conversation.DoesNotExist:
            raise NotFound(detail="Conversation not found.")
        
        # Check if user is a participant
        if self.request.user not in conversation.participants.all():
            raise PermissionDenied("You must be a participant to send messages.")
        
        # Set the sender to the current user
        serializer.save(conversation=conversation, sender=self.request.user)

    def perform_update(self, serializer):
        """Allow message updates only by the sender."""
        message = self.get_object()
        
        if message.sender != self.request.user:
            raise PermissionDenied("You can only edit your own messages.")
        
        # Optional: Add time limit for editing (e.g., 15 minutes)
        from django.utils import timezone
        from datetime import timedelta
        
        time_limit = timezone.now() - timedelta(minutes=15)
        if message.sent_at < time_limit:
            raise ValidationError("Messages can only be edited within 15 minutes of sending.")
        
        serializer.save()

    def perform_destroy(self, instance):
        """Allow message deletion only by the sender."""
        if instance.sender != self.request.user:
            raise PermissionDenied("You can only delete your own messages.")
        
        super().perform_destroy(instance)

    @action(detail=False, methods=['get'])
    def unread(self, request, conversation_pk=None):
        """Get unread messages for the user in this conversation."""
        # This would require adding a read status tracking system
        # For now, return all messages (implementation placeholder)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, conversation_pk=None, pk=None):
        """Mark a message as read by the current user."""
        # This would require adding a read status tracking system
        # Implementation placeholder
        return Response(
            {'message': 'Message marked as read'}, 
            status=status.HTTP_200_OK
        )
