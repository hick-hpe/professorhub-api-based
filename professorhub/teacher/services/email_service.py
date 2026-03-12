from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import datetime


def enviar_email_para_recuperar_conta(email, codigo):

    try:
        # dados do email
        subject = 'Redefinição de senha'
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [email]
        data = datetime.date.today().year

        text_content = f'Quase lá!'
        html_content = f"""
            <div style="font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 30px;">
                <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <tr>
                        <td style="background-color: #1C6EA4; padding: 20px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0;">Redefinição de senha</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 30px;">
                            <p style="font-size: 16px; color: #333;">Olá,</p>
                            <p style="font-size: 16px; color: #333; line-height: 1.5;">
                                Você solicitou uma redefinição de senha. Seu código de verificação é:
                            </p>
                            <p style="text-align: center; margin: 30px 0; font-size: 30px; font-weight: bold; letter-spacing: 2px;">
                                {codigo}
                            </p>
                            <p style="font-size: 14px; color: #777; text-align: center; margin-top: 40px;">
                                &copy; {data} ProfessorHub. Todos os direitos reservados.
                            </p>
                        </td>
                    </tr>
                </table>
            </div>
        """

        # criar email
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)

        msg.attach_alternative(html_content, "text/html")
        
        # enviar email
        msg.send(fail_silently=False)

    except Exception as e:
        print("Erro ao enviar email de recuperação de conta:", e)
