from common.rules import AutomationRule
from typing import List
import operator

OPERATORS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

def evaluate_rule(rule: AutomationRule, metric_value: float) -> bool:
    op = OPERATORS[rule.operator]
    return op(metric_value, rule.threshold)

def evaluate_event(event, rules: List[AutomationRule]):

    triggered = []

    for rule in rules:

        if rule.sensor_name != event.sensor_name:
            continue

        for m in event.measurements:

            if m.metric != rule.metric_name:
                continue

            if evaluate_rule(rule, m.value):
                triggered.append(rule)

    return triggered