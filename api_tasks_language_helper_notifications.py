from django.utils import timezone as dj_timezone
from api.models import User, Chat, UserChat
from django_cron import CronJobBase, Schedule
from django.db.models import Q
import mail


class LanguageHelperNotifications(CronJobBase):
    RUN_EVERY_MINS = 15
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'api.language_helper_notifications'

    def do(self):  # NOQA
        print('checking for language helper notifications')
        chats_to_notify = Chat.objects.filter(
            Q(notify_new_message=True) | Q(notify_to_answer=True),
            message_seen=False,
            chat_type=Chat.LANGUAGE_HELPER_CHAT
        )
        for chat in chats_to_notify:
            last_chat_message = chat.messages.all().last()
            student_name = last_chat_message.user.first_name
            last_message_date = last_chat_message.created_datetime
            diff = dj_timezone.now() - last_message_date
            total_mins = diff.seconds / 60

            if total_mins > 15 and total_mins < 900 and chat.notify_new_message:
                chat.notify_new_message = False
                chat.save()
                languageHelperChat = UserChat.objects.get(
                    user__user_type=User.LANGUAGE_HELPER,
                    chat__id=chat.id
                )
                languageHelper = languageHelperChat.user

                context = {
                    'studentName': student_name,
                    'languageHelperName': languageHelper.first_name,
                    'languageHelperId': languageHelper.id,
                    'language': chat.language,
                    'chatId': chat.id,
                    'campaign_name': 'newMessageNotification'
                }
                new_message_email = mail.notifyNewMessageLanguageHelper(
                    context,
                    [languageHelper.email],
                    ['emma@chatterbox.io']
                )

                new_message_email.send()
            elif total_mins > 900 and chat.notify_to_answer:
                chat.notify_to_answer = False
                chat.save()
                languageHelperChat = UserChat.objects.get(
                    user__user_type=User.LANGUAGE_HELPER,
                    chat__id=chat.id
                )
                languageHelper = languageHelperChat.user

                context = {
                    'studentName': student_name,
                    'languageHelperName': languageHelper.first_name,
                    'languageHelperId': languageHelper.id,
                    'language': chat.language,
                    'chatId': chat.id,
                    'campaign_name': 'newMessageNotification'
                }
                new_message_email = mail.notifyToAnswerLanguageHelper(
                    context,
                    [languageHelper.email],
                    ['emma@chatterbox.io']
                )

                new_message_email.send()
