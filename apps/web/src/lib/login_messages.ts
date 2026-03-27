export function mapLoginErrorMessage(error?: string) {
  if (error === "callback_failed") {
    return "로그인 처리에 실패했습니다. 다시 시도하세요.";
  }

  if (error === "missing_code") {
    return "인증 코드가 없습니다. 다시 시도하세요.";
  }

  return undefined;
}
