from matching.service import normalize

STATUSES = ("strong", "partial", "missing")


def score(items):
    weights = {"strong": 1, "partial": 0.5, "missing": 0}
    total = sum(2 if item["required"] else 1 for item in items)
    return round(100 * sum((2 if item["required"] else 1) * weights[item["status"]] for item in items) / total)


def measure(cases, predictions):
    confusion = {actual: {predicted: 0 for predicted in (*STATUSES, "unmatched")} for actual in STATUSES}
    expected_count = predicted_count = aligned = correct = rejected = 0
    score_errors, priority_correct = [], 0
    for case in cases:
        prediction = predictions.get(case["id"], {})
        valid = "error" not in prediction and bool(prediction.get("skills"))
        skills = prediction.get("skills", []) if valid else []
        rejected += not valid
        predicted_count += len(skills)
        used = set()
        for expected in case["expected"]:
            expected_count += 1
            # Align by a canonical requirement passage, never by model-invented skill names.
            matches = [index for index, item in enumerate(skills) if index not in used and
                       normalize(expected["requirement_quote"]) in normalize(item["requirement_quote"])]
            predicted = "unmatched"
            if matches:
                index = matches[0]
                used.add(index)
                predicted = skills[index]["status"]
                aligned += 1
                correct += predicted == expected["status"]
                priority_correct += skills[index]["required"] == expected["required"]
            confusion[expected["status"]][predicted] += 1
        if valid:
            score_errors.append(abs(prediction.get("match_score", score(skills)) - score(case["expected"])))
    f1 = {}
    for status in STATUSES:
        tp = confusion[status][status]
        fn = sum(confusion[status].values()) - tp
        fp = sum(confusion[other][status] for other in STATUSES if other != status)
        f1[status] = round(2 * tp / (2 * tp + fp + fn), 4) if 2 * tp + fp + fn else 0
    return {
        "cases": len(cases), "requirements": expected_count, "rejected_cases": rejected,
        "valid_response_rate": round(1 - rejected / len(cases), 4),
        "requirement_recall": round(aligned / expected_count, 4),
        "requirement_precision": round(aligned / predicted_count, 4) if predicted_count else 0,
        "label_accuracy_all_requirements": round(correct / expected_count, 4),
        "priority_accuracy_aligned": round(priority_correct / aligned, 4) if aligned else None,
        "macro_f1": round(sum(f1.values()) / len(f1), 4), "per_class_f1": f1,
        "score_mae_valid_cases": round(sum(score_errors) / len(score_errors), 2) if score_errors else None,
        "confusion": confusion,
    }
