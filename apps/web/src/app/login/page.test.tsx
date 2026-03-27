import { describe, expect, it } from "vitest";

import { mapLoginErrorMessage } from "@/lib/login_messages";

describe("mapLoginErrorMessage", () => {
  it("maps callback failures", () => {
    expect(mapLoginErrorMessage("callback_failed")).toBe(
      "로그인 처리에 실패했습니다. 다시 시도하세요.",
    );
  });

  it("maps missing codes", () => {
    expect(mapLoginErrorMessage("missing_code")).toBe("인증 코드가 없습니다. 다시 시도하세요.");
  });

  it("returns undefined for unknown values", () => {
    expect(mapLoginErrorMessage("other")).toBeUndefined();
  });
});
