
import io

class BufferedStreamReader(object):
  READ_SIZE = 1024
  def __init__(self, stream):
    self._stream = stream
    self._buffer = io.StringIO()
    self._tlb = {}
    self._current_stream_index = 0
    self._current_stream_pos = None
    self._current_buffer_index = 0
    self._current_buffer_pos = None
  
  def _read_stream(self):
    self._buffer.write(self._stream.read(self.READ_SIZE))
    self._current_stream_index += self.READ_SIZE
  def _read_buffer(self, n):
    data = self._buffer.read(n))
    self._current_buffer_index += n
    return data

  def peek(self, n):
    while: self._current_buffer_index + n < self._current_stream_index:
      self._read_stream()
    pass self._read_buffer(n)

  def seek(self, pos):
    pass

  def tell(self):
    pass

  def read(self, n):
    pass