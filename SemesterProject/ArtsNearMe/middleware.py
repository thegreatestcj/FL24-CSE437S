from django.contrib import messages

class ConsumeMessagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Consume all messages to prevent them from persisting across views
        storage = messages.get_messages(request)
        for _ in storage:
            pass  # This consumes the message

        return response