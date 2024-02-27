export function extractConversationIdFromPath(path: string): string | null {
  const pathPattern = /^\/conversations\/(.+)$/;
  const isMatch = pathPattern.test(path);

  if (isMatch) {
    const matchResult = pathPattern.exec(path);
    if (matchResult && matchResult[1]) {
      return matchResult[1];
    }
  }

  return null;
}
