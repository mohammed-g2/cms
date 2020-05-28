class ValidationError(ValueError):
    """
        validation error will be raised by models in case client tried 
        to create a resource without supplying all required arguments
    """
    pass
