import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    """
    Extends Django’s AbstractUser to replace the default PK with a UUID,
    enforce unique email logins, and add phone_number, role, and created_at.
    """
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Primary key as UUID"
    )
    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
        help_text="User’s email address (used as username field)"
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Optional phone contact"
    )

    password_changed_at = models.DateTimeField(
            null=True,
            blank=True,
            help_text="Timestamp of last password change"
        )
    force_password_change = models.BooleanField(
            default=False,
            help_text="Flag to force user to change password on next login"
        )
    
    def save(self, *args, **kwargs):
            if self._password is not None:
                self.password_changed_at = timezone.now()
            super().save(*args, **kwargs)

    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        null=False,
        blank=False,
        help_text="Role of the user in the system"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the user was created"
    )

    # Tell Django to use email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        indexes = [
            models.Index(fields=['email']),
        ]
        verbose_name = "User"
        verbose_name_plural = "Users"


class Conversation(models.Model):
    """
    Represents a chat between two or more users.
    Tracks participants via a ManyToMany relation.
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Primary key as UUID"
    )
    participants = models.ManyToManyField(
        CustomUser,
        related_name='conversations',
        help_text="Users involved in this conversation"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the conversation was created"
    )

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    """
    Each message is tied to a sender and a conversation.
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Primary key as UUID"
    )
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="User who sent the message"
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="Conversation this message belongs to"
    )
    message_body = models.TextField(
        null=False,
        blank=False,
        help_text="Content of the message"
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the message was sent"
    )

    class Meta:
        indexes = [
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
        ]
        ordering = ['sent_at']
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Msg {self.message_id} from {self.sender.email}"
