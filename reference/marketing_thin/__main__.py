from __future__ import annotations

import argparse

from .runtime import MarketingThinRuntime, summary_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Intent OS marketing Thin Reference Implementation")
    parser.add_argument(
        "--goal",
        default="윈터스쿨 모집을 위한 조사 근거가 있는 마케팅 문서를 작성하고 최종 검수까지 완료한다",
    )
    parser.add_argument("--rating", type=int, choices=range(1, 6), default=5)
    args = parser.parse_args()

    bundle = MarketingThinRuntime().run(args.goal, user_rating=args.rating)
    print(summary_json(bundle))
    print("\n--- final artifact ---\n")
    print(bundle["artifact_contents"][bundle["final_artifact_id"]])


if __name__ == "__main__":
    main()
