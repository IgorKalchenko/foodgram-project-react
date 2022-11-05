from django.core.validators import RegexValidator


class OnlyLettersValidator(RegexValidator):
    regex = r'^\D*$'
    message = '''Numeric characters are not allowd 
    in First name and Last name fields.'''
