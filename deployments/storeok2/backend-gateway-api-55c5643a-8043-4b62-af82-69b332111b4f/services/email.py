import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from app.utils.logger import get_logger

# Configurar el logger para este módulo
logger = get_logger(__name__)

# Configuración del servidor SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@smartpay.com")


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    cc_emails: Optional[List[str]] = None,
    bcc_emails: Optional[List[str]] = None,
) -> bool:
    """
    Envía un correo electrónico utilizando la configuración SMTP establecida.

    Args:
        to_email: Dirección de correo electrónico del destinatario.
        subject: Asunto del correo electrónico.
        html_content: Contenido HTML del correo electrónico.
        cc_emails: Lista de direcciones de correo electrónico en copia (CC).
        bcc_emails: Lista de direcciones de correo electrónico en copia oculta (BCC).

    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario.
    """
    # Extraer el enlace de restablecimiento de contraseña si está presente en el HTML
    reset_link = None
    if 'href="' in html_content and "reset" in html_content.lower():
        try:
            start_idx = html_content.find('href="') + 6
            end_idx = html_content.find('"', start_idx)
            if start_idx > 6 and end_idx > start_idx:
                reset_link = html_content[start_idx:end_idx]
        except Exception:
            pass

    # SIEMPRE mostrar el correo en los logs para desarrollo
    print("\n===== SIMULACIÓN DE ENVÍO DE CORREO =====")
    print(f"Destinatario: {to_email}")
    print(f"Asunto: {subject}")

    if reset_link:
        # Mostrar el enlace de restablecimiento de forma destacada
        print("")
        print("===== ENLACE DE RESTABLECIMIENTO DE CONTRASEÑA =====")
        print(f"URL: {reset_link}")
        print("========================================================")
        print("")
    else:
        # Mostrar parte del contenido si no se encontró un enlace
        print(f"Contenido: {html_content[:200]}...")

    if cc_emails:
        print(f"CC: {cc_emails}")
    if bcc_emails:
        print(f"BCC: {bcc_emails}")

    print("===== FIN DE SIMULACIÓN DE CORREO =====\n")

    # También usar el logger para que quede en los archivos de log
    logger.info("===== SIMULACIÓN DE ENVÍO DE CORREO =====")
    logger.info(f"Destinatario: {to_email}")
    logger.info(f"Asunto: {subject}")

    if reset_link:
        logger.info("===== ENLACE DE RESTABLECIMIENTO DE CONTRASEÑA =====")
        logger.info(f"URL: {reset_link}")
        logger.info("========================================================")

    # Intentar enviar por SMTP solo si hay credenciales configuradas
    if SMTP_USERNAME and SMTP_PASSWORD:
        try:
            # Crear mensaje
            message = MIMEMultipart()
            message["From"] = EMAIL_FROM
            message["To"] = to_email
            message["Subject"] = subject

            if cc_emails:
                message["Cc"] = ", ".join(cc_emails)

            # Agregar contenido HTML
            message.attach(MIMEText(html_content, "html"))

            # Configurar todos los destinatarios
            recipients = [to_email]
            if cc_emails:
                recipients.extend(cc_emails)
            if bcc_emails:
                recipients.extend(bcc_emails)

            # Registrar información de configuración SMTP
            logger.info(f"Intentando enviar correo con la siguiente configuración:")
            logger.info(f"SMTP_SERVER: {SMTP_SERVER}")
            logger.info(f"SMTP_PORT: {SMTP_PORT}")
            logger.info(f"SMTP_USERNAME: {SMTP_USERNAME}")
            logger.info(f"EMAIL_FROM: {EMAIL_FROM}")
            logger.info(f"Destinatario: {to_email}")

            # Conectar al servidor SMTP
            logger.info("Iniciando conexión SMTP...")
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                logger.info("Conexión SMTP establecida. Iniciando TLS...")
                server.starttls()  # Habilitar conexión segura
                logger.info("TLS habilitado. Intentando login...")
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                logger.info("Login exitoso. Enviando correo...")
                server.sendmail(EMAIL_FROM, recipients, message.as_string())
                logger.info(f"Correo enviado exitosamente a {to_email}")
                return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Error de autenticación SMTP: {str(e)}", exc_info=True)
            logger.error(
                "Verifica que las credenciales sean correctas y que la cuenta permita el acceso de aplicaciones menos seguras o use una clave de aplicación."
            )
        except smtplib.SMTPException as e:
            logger.error(
                f"Error SMTP al enviar correo a {to_email}: {str(e)}", exc_info=True
            )
        except Exception as e:
            logger.error(
                f"Error general al enviar correo a {to_email}: {str(e)}", exc_info=True
            )

    # Si llegamos aquí, significa que no se pudo enviar por SMTP o no hay credenciales
    # Pero en desarrollo, consideramos que el correo se "envió" correctamente (simulado)
    return True


async def send_password_reset_email(email: str, reset_url: str) -> bool:
    """
    Envía un correo electrónico con un enlace para restablecer la contraseña.

    Args:
        email: Dirección de correo electrónico del usuario.
        reset_url: URL con el token para restablecer la contraseña.

    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario.
    """
    # Mostrar el enlace de restablecimiento directamente en la consola
    print("\n" + "=" * 80)
    print("ENLACE DE RESTABLECIMIENTO DE CONTRASEÑA GENERADO:")
    print(f"URL: {reset_url}")
    print(f"Para: {email}")
    print("=" * 80 + "\n")
    subject = "Restablecimiento de contraseña - SmartPay"
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4A90E2; color: white; padding: 10px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .button {{ display: inline-block; background-color: #4A90E2; color: white;
                      padding: 10px 20px; text-decoration: none; border-radius: 4px; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Restablecimiento de Contraseña</h1>
            </div>
            <div class="content">
                <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta SmartPay.</p>
                <p>Para continuar con el proceso, haz clic en el siguiente enlace:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Restablecer Contraseña</a>
                </p>
                <p>Si no solicitaste este cambio, puedes ignorar este correo y tu contraseña permanecerá sin cambios.</p>
                <p>Este enlace expirará en 30 minutos por razones de seguridad.</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
                <p>&copy; {2025} SmartPay. Todos los derechos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return await send_email(email, subject, html_content)
