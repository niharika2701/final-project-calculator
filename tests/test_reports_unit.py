"""
Unit tests for app/report_service.py.

No database, no HTTP server — just plain Python objects.
"""
import pytest
from app.report_service import compute_report_stats


class FakeCalc:
    """Minimal stand-in for a SQLAlchemy Calculation row."""
    def __init__(self, a: float, b: float, result: float, type_: str):
        self.a = a
        self.b = b
        self.result = result
        self.type = type_


def test_empty_list_returns_all_zeros():
    stats = compute_report_stats([])
    assert stats["total_calculations"] == 0
    assert stats["by_operation"] == {}
    assert stats["average_a"] == 0.0
    assert stats["average_b"] == 0.0
    assert stats["average_result"] == 0.0


def test_single_calculation_total():
    calcs = [FakeCalc(a=4, b=2, result=2.0, type_="Divide")]
    stats = compute_report_stats(calcs)
    assert stats["total_calculations"] == 1


def test_single_calculation_by_operation():
    calcs = [FakeCalc(a=4, b=2, result=2.0, type_="Divide")]
    stats = compute_report_stats(calcs)
    assert stats["by_operation"] == {"Divide": 1}


def test_single_calculation_averages():
    calcs = [FakeCalc(a=4, b=2, result=2.0, type_="Divide")]
    stats = compute_report_stats(calcs)
    assert stats["average_a"] == 4.0
    assert stats["average_b"] == 2.0
    assert stats["average_result"] == 2.0


def test_multiple_operations_counted_separately():
    calcs = [
        FakeCalc(a=2,  b=3, result=5.0,  type_="Add"),
        FakeCalc(a=10, b=2, result=5.0,  type_="Divide"),
        FakeCalc(a=4,  b=1, result=3.0,  type_="Sub"),
        FakeCalc(a=2,  b=3, result=6.0,  type_="Multiply"),
        FakeCalc(a=8,  b=2, result=6.0,  type_="Add"),
    ]
    stats = compute_report_stats(calcs)
    assert stats["total_calculations"] == 5
    assert stats["by_operation"]["Add"] == 2
    assert stats["by_operation"]["Divide"] == 1
    assert stats["by_operation"]["Sub"] == 1
    assert stats["by_operation"]["Multiply"] == 1


def test_averages_computed_correctly():
    calcs = [
        FakeCalc(a=2.0, b=4.0, result=6.0, type_="Add"),
        FakeCalc(a=4.0, b=2.0, result=2.0, type_="Sub"),
    ]
    stats = compute_report_stats(calcs)
    assert stats["average_a"] == 3.0
    assert stats["average_b"] == 3.0
    assert stats["average_result"] == 4.0


def test_averages_rounded_to_four_decimal_places():
    calcs = [
        FakeCalc(a=1, b=1, result=1, type_="Multiply"),
        FakeCalc(a=1, b=1, result=1, type_="Multiply"),
        FakeCalc(a=1, b=1, result=2, type_="Multiply"),
    ]
    stats = compute_report_stats(calcs)
    assert stats["average_result"] == 1.3333


def test_all_same_operation_type():
    calcs = [FakeCalc(a=1, b=1, result=2, type_="Add") for _ in range(5)]
    stats = compute_report_stats(calcs)
    assert stats["by_operation"] == {"Add": 5}
    assert len(stats["by_operation"]) == 1


def test_total_matches_list_length():
    calcs = [FakeCalc(a=i, b=1, result=i+1, type_="Add") for i in range(10)]
    stats = compute_report_stats(calcs)
    assert stats["total_calculations"] == 10


def test_returns_all_required_keys():
    required_keys = {
        "total_calculations", "by_operation",
        "average_a", "average_b", "average_result"
    }
    assert required_keys == required_keys & set(compute_report_stats([]).keys())
    calcs = [FakeCalc(a=1, b=2, result=3, type_="Add")]
    assert required_keys == required_keys & set(compute_report_stats(calcs).keys())