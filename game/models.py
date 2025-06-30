from django.db import models
import json
import uuid


class GameSession(models.Model):
    """
    Model to store game session data including conversation history
    """
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    conversation_history = models.JSONField(default=list)
    question_count = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'game_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.session_id} - {self.question_count} questions"
    
    def add_question_answer(self, question, answer):
        """Add a question-answer pair to the conversation history"""
        if not isinstance(self.conversation_history, list):
            self.conversation_history = []
        
        self.conversation_history.append({
            'question': question,
            'answer': answer,
            'timestamp': models.DateTimeField(auto_now_add=True).value_from_object(self)
        })
        self.question_count += 1
        self.save()
    
    def get_conversation_context(self):
        """Get formatted conversation context for AI"""
        if not self.conversation_history:
            return "This is a 20 questions game. I'm thinking of something and you need to guess what it is by asking yes/no questions. You can ask up to 20 questions."
        
        context = "This is a 20 questions game. Here's our conversation so far:\n\n"
        for i, qa in enumerate(self.conversation_history, 1):
            context += f"Q{i}: {qa['question']}\n"
            context += f"A{i}: {qa['answer']}\n\n"
        
        context += f"You've asked {self.question_count} questions so far. "
        if self.question_count >= 20:
            context += "This is your final chance to guess!"
        else:
            context += f"You have {20 - self.question_count} questions remaining."
        
        return context
    
    def reset_session(self):
        """Reset the session to start a new game"""
        self.conversation_history = []
        self.question_count = 0
        self.is_completed = False
        self.is_active = True
        self.save()
