from __future__ import annotations


def rank_results(results: list[dict]) -> list[dict]:
    eligible = [item for item in results if item["eligible"]]
    ineligible = [item for item in results if not item["eligible"]]
    eligible.sort(key=lambda item: (-item["total"], item["name"]))
    for index, item in enumerate(eligible, start=1):
        item["rank"] = index
    for item in ineligible:
        item["rank"] = None
    return eligible + ineligible
