def convert_file_size(file_size_bytes) -> str:
  match file_size_bytes:
    case num if num > 1000000000:
      return f'{file_size_bytes / 1000000000:.1f}GB'
    case num if num > 1000000:
      return f'{file_size_bytes / 1000000:.1f}MB'
    case num if num > 1000:
      return f'{file_size_bytes / 1000:.1f}KB'