# DigiClassroom - Email Configuration Guide

## Current Setup
By default, DigiClassroom uses the **console email backend**, which means password reset emails and other notifications will be printed to the terminal/console instead of being sent via email.

## Email Backend Options

### 1. Console Backend (Current - Development)
Emails are printed to the console/terminal. No configuration needed.
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### 2. File-Based Backend (Testing)
Emails are saved as files in a directory. Good for testing without needing SMTP.
```python
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
```

### 3. SMTP Backend (Production)
Sends actual emails via an SMTP server.

#### Gmail Configuration
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Update `digiclassrooms/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-16-character-app-password'
DEFAULT_FROM_EMAIL = 'DigiClassroom <your-email@gmail.com>'
```

#### Other Email Providers

**Outlook/Office 365:**
```python
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

**Yahoo:**
```python
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

**SendGrid (Recommended for Production):**
```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
```

## Testing Email Configuration

After configuring, you can test by:

1. Using the password reset feature in the application
2. Running this in Django shell:
```python
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test email from DigiClassroom.',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

## Security Best Practices

1. **Never commit email credentials to version control**
2. Use environment variables for sensitive data:
   ```python
   import os
   EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
   ```
3. For Gmail, always use App Passwords, never your actual password
4. Consider using dedicated email services like SendGrid for production
