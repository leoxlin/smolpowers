from fixtures.tests import lifecycle_eval


EXPECTED = ["smol-activate", "smol-design", "smol-plan"]


def trajectory(*calls: dict) -> dict:
    return {
        "steps": [
            {"step_id": index, "tool_calls": [call]}
            for index, call in enumerate(calls, 1)
        ]
    }


def path_call(skill: str) -> dict:
    return {
        "function_name": "exec_command",
        "arguments": {"cmd": f"sed -n '1,200p' /tmp/skills/{skill}/SKILL.md"},
    }


def skill_call(skill: str, function_name: str = "Skill") -> dict:
    return {
        "function_name": function_name,
        "arguments": {"skill": skill},
    }


def test_extracts_path_reads_and_native_skill_calls_with_namespaces() -> None:
    evidence = lifecycle_eval.activation_evidence(
        trajectory(
            path_call("smol-activate"),
            skill_call("smolpowers:smol-design", "plugin__Skill"),
            skill_call("smol-plan"),
        )
    )

    assert evidence == [
        {"skill": "smol-activate", "step_id": 1, "source": "path"},
        {"skill": "smol-design", "step_id": 2, "source": "tool"},
        {"skill": "smol-plan", "step_id": 3, "source": "tool"},
    ]


def test_ignores_skill_availability_in_messages() -> None:
    data = trajectory(path_call("smol-activate"))
    data["steps"][0]["message"] = "/available/skills/smol-design/SKILL.md"
    data["steps"][0]["tool_calls"][0]["arguments"]["cmd"] += (
        " /tmp/skills/smol-plan/SKILL.md"
    )

    assert [item["skill"] for item in lifecycle_eval.activation_evidence(data)] == [
        "smol-activate",
        "smol-plan",
    ]


def test_duplicates_and_unrelated_skills_remain_visible_without_failing() -> None:
    result = lifecycle_eval.evaluate_lifecycle(
        trajectory(
            path_call("smol-activate"),
            path_call("unrelated"),
            skill_call("smol-design"),
            path_call("smol-design"),
            path_call("smol-plan"),
        ),
        EXPECTED,
    )

    assert [item["skill"] for item in result["observed"]] == [
        "smol-activate",
        "unrelated",
        "smol-design",
        "smol-design",
        "smol-plan",
    ]
    assert result["missing"] == []
    assert result["passed"] is True


def test_missing_and_inverted_required_skills_fail() -> None:
    missing = lifecycle_eval.evaluate_lifecycle(
        trajectory(path_call("smol-activate"), path_call("smol-plan")),
        EXPECTED,
    )
    inverted = lifecycle_eval.evaluate_lifecycle(
        trajectory(
            path_call("smol-design"),
            path_call("smol-activate"),
            path_call("smol-plan"),
        ),
        EXPECTED,
    )

    assert missing["missing"] == ["smol-design"]
    assert missing["passed"] is False
    assert inverted["missing"] == []
    assert inverted["passed"] is False


def test_required_skills_in_the_same_parallel_step_are_not_inverted() -> None:
    data = trajectory(path_call("smol-activate"))
    data["steps"].append(
        {
            "step_id": 2,
            "tool_calls": [
                path_call("smol-plan"),
                path_call("smol-design"),
            ],
        }
    )

    assert lifecycle_eval.evaluate_lifecycle(data, EXPECTED)["passed"] is True


def test_named_check_and_legacy_normalization() -> None:
    assert lifecycle_eval.normalize_checks(
        {"skills_in_order": 1, "requested_change_completed": 1}
    ) == {
        "kind": "named",
        "skills_in_order": 1,
        "requested_change_completed": 1,
        "passed": True,
    }
    assert lifecycle_eval.normalize_checks({"reward": 1}) == {
        "kind": "legacy",
        "skills_in_order": None,
        "requested_change_completed": None,
        "passed": True,
    }
    assert lifecycle_eval.normalize_checks({"skills_in_order": 1})["passed"] is False
    assert lifecycle_eval.normalize_checks(None)["kind"] == "missing"
