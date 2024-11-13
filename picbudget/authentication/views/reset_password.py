from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.views.generic import FormView
from django.contrib.auth.forms import SetPasswordForm
from django.utils.encoding import force_str
from ..serializers.reset_password import PasswordResetSerializer
from django.http import HttpResponse
from picbudget.project.task import send_email_task

User = get_user_model()


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(
                reverse(
                    "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
                )
            )
            self.send_reset_email(email, reset_link)
            return Response(
                {"message": "Password reset link has been sent to your email."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_reset_email(self, email, reset_link):
        subject = "Password Reset Request"
        message = f"Click the link to reset your password: {reset_link}"
        recipient_list = [email]
        send_email_task.delay(
            subject=subject, message=message, recipient_list=recipient_list
        )


class PasswordResetConfirmView(FormView):
    template_name = "password_reset_confirm.html"
    form_class = SetPasswordForm

    def get_user(self, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.get_user(self.kwargs["uidb64"])
        return kwargs

    def form_valid(self, form):
        user = self.get_user(self.kwargs["uidb64"])
        if user is not None and default_token_generator.check_token(
            user, self.kwargs["token"]
        ):
            form.save()
            return HttpResponse("Password has been reset successfully.")
        else:
            return HttpResponse("Password reset link is invalid.")
