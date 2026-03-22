"""
Tests for course shuffle logic.
"""
from . import MkddTestBase
from worlds.mario_kart_double_dash import game_data


class TestCourseShuffleVanilla(MkddTestBase):
    options = {"course_shuffle": "vanilla"}

    def test_four_cups_each_with_four_courses(self) -> None:
        self.assertEqual(len(self.world.cups_courses), 4)
        for cup_id, courses in enumerate(self.world.cups_courses):
            self.assertEqual(len(courses), 4)

    def test_vanilla_order_preserved(self) -> None:
        for cup_id, courses in enumerate(self.world.cups_courses):
            expected = list(range(cup_id * 4, cup_id * 4 + 4))
            self.assertEqual(courses, expected)

    def test_all_sixteen_courses_present(self) -> None:
        all_courses = [c for cup in self.world.cups_courses for c in cup]
        self.assertEqual(sorted(all_courses), list(range(16)))


class TestCourseShuffleOnce(MkddTestBase):
    options = {"course_shuffle": "shuffle_once"}

    def test_four_cups_each_with_four_courses(self) -> None:
        self.assertEqual(len(self.world.cups_courses), 4)
        for cup_id, courses in enumerate(self.world.cups_courses):
            self.assertEqual(len(courses), 4)

    def test_all_sixteen_courses_present_exactly_once(self) -> None:
        all_courses = [c for cup in self.world.cups_courses for c in cup]
        self.assertEqual(len(all_courses), 16)
        self.assertEqual(len(set(all_courses)), 16) # Checks no courses appear more than once

    def test_all_course_indices_valid(self) -> None:
        all_courses = [c for cup in self.world.cups_courses for c in cup]
        for course_id in all_courses:
            self.assertIn(course_id, range(16))

    def test_courses_reference_valid_race_courses(self) -> None:
        for cup_id, courses in enumerate(self.world.cups_courses):
            for course_id in courses:
                course = game_data.RACE_COURSES[course_id]
                self.assertIsNotNone(course.name)
