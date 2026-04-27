
from login.models import Agent
from .models import Notification


def user_notifications(request):
    """
    Injects notifications relevant to the current user into every template context.
    - Admin: sees all notifications (limit 10)
    - Agent: sees general (agent=None) + agent-specific notifications
    - Customer: sees general (agent=None) notifications
    """
    notifications = []
    if request.user.is_authenticated:
        try:
            user_agent = Agent.objects.get(login=request.user)
        except Agent.DoesNotExist:
            user_agent = None

        if request.user.is_staff:
            notifications = Notification.objects.filter(status='Active').select_related('agent')[:10]
        elif user_agent:
            notifications = Notification.objects.filter(
                status='Active'
            ).filter(
                agent__isnull=True
            ) | Notification.objects.filter(
                status='Active',
                agent=user_agent
            )
            notifications = notifications.select_related('agent').distinct()[:10]
        else:
            # Customer — only general broadcasts
            notifications = Notification.objects.filter(
                status='Active',
                agent__isnull=True
            ).select_related('agent')[:10]

    return {'user_notifications': notifications}

