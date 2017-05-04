class GenericError(Exception):
  def __init__(self, *causes):
    super(GenericError, self).__init__("\n"+ "\ncaused by\n".join(str(cause) for cause in causes))
    self.causes = causes