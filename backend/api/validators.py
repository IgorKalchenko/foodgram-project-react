from django.core.validators import RegexValidator


class OnlyLettersValidator(RegexValidator):
    '''
    Validates if First and Last name
    are spelled correctly.
    '''
    regex = r'^\D*$'
    message = ('Numeric characters are not allowd '
               'in First name and Last name fields.')
