from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from .services.agent import Agent
import json
import time

agent = Agent()

@csrf_exempt
def chat_view(request):
    if request.method != "POST":
        return render(request, "chat.html")
    try:
        data = json.loads(request.body)
        user_input = data.get("user_input", "")
        reset = data.get("reset", False)
        reply = agent.handle_message(user_input, reset=reset)
        return JsonResponse({"reply": reply})
    except Exception as e:
        return JsonResponse({"reply": f"[Error: {str(e)}]"})

@csrf_exempt
def stream_chat_view(request):
    user_input = request.GET.get("user_input", "")
    reset = request.GET.get("reset", "false").lower() == "true"

    def event_stream():
        try:
            for chunk in agent.stream_message(user_input, reset=reset):
                if chunk is None:
                    continue
                yield f"data: {chunk}\n\n"

            # To avoid false positives, we explicitly say that the stream is done
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [Error streaming: {str(e)}]\n\n"

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

def stream_test(request):
    # Small test for SSE stream
    def gen():
        yield "data: [TEST START]\n\n"
        for i in range(6):
            yield f"data: test-chunk-{i}\n\n"
            time.sleep(0.5)
        yield "data: [TEST END]\n\n"
    return StreamingHttpResponse(gen(), content_type="text/event-stream")