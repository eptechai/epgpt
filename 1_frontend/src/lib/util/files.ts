export function formatFileInfo(file: File): string {
  const fileNameWithoutExt = file.name.replace(/\.[^/.]+$/, '');

  let fileSize: string;
  if (file.size < 1024) {
    fileSize = `${file.size} b`;
  } else if (file.size < 1024 * 1024) {
    fileSize = `${(file.size / 1024).toFixed(2)} kb`;
  } else {
    fileSize = `${(file.size / (1024 * 1024)).toFixed(2)} mb`;
  }

  return `${fileNameWithoutExt} | ${fileSize}`;
}

export function getFileExtension(file: File): string {
  return file.name.split('.').pop() ?? '';
}
