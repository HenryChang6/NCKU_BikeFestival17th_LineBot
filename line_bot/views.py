from django.shortcuts import render

# Create your views here.

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
#csrf_exempt: A decorator to disable CSRF (Cross-Site Request Forgery) protection for a specific view.
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

# Initializing the LINE Bot API with access token.
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
# Initializing the webhook parser with channel secret.
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

# The @csrf_exempt is a decorator that disables CSRF protection for this view. 
# This is necessary because webhooks typically don't provide CSRF tokens.
@csrf_exempt
def callback(request):
    # Check if the incoming request is a POST request.
    if request.method == 'POST':
        # Get the LINE signature from the request header. Used to validate the source.
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        # Decode the body of the request from bytes to string.
        body = request.body.decode('utf-8')

        try:
            # Validate the request body against the signature for its authenticity.
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            # If the signature doesn't match, it's a forbidden request.
            return HttpResponseForbidden()
        except LineBotApiError:
            # If there's an API error, send a bad request response.
            return HttpResponseBadRequest()

        # Process each event received from LINE.
        for event in events:
            if isinstance(event, MessageEvent):
                # Extract the text from the incoming message.
                mtext = event.message.text
                # Prepare the reply with the same message text.
                message = [TextSendMessage(text=mtext)]
                # Send the reply back to the user.
                line_bot_api.reply_message(event.reply_token, message)

        # If all events are processed successfully, return an OK response.
        return HttpResponse()
    else:
        # If the request method is not POST, it's a bad request.
        return HttpResponseBadRequest()
