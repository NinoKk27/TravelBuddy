import unittest
from itertools import product

from chatbot import ACTIVITIES, ACCOMMODATIONS, TRIP_TYPES, Step, TravelBuddy


class PlanningTests(unittest.TestCase):
    def test_all_27_routes_and_ordered_history(self):
        for trip, stay, activity in product(range(3), repeat=3):
            with self.subTest(trip=trip, stay=stay, activity=activity):
                bot = TravelBuddy()
                bot.start()
                bot.respond(str(trip + 1))
                bot.respond(str(stay + 1))
                bot.respond(str(activity + 1))
                self.assertEqual(bot.state.step, Step.SUMMARY)
                self.assertEqual(bot.state.trip_type, TRIP_TYPES[trip])
                self.assertEqual(bot.state.accommodation, ACCOMMODATIONS[stay])
                self.assertEqual(bot.state.activity, ACTIVITIES[TRIP_TYPES[trip]][activity])
                self.assertEqual([item['role'] for item in bot.state.history], ['assistant', 'user', 'assistant', 'user', 'assistant', 'user', 'assistant'])

    def test_full_names_with_case_and_whitespace(self):
        bot = TravelBuddy()
        bot.respond('  MOUNTAIN   adventure ')
        bot.respond(' VACATION   RENTAL ')
        bot.respond(' mountain   BIKING ')
        self.assertEqual(bot.state.step, Step.SUMMARY)
        self.assertEqual(bot.state.activity, 'Mountain biking')

    def test_invalid_input_at_each_stage_preserves_choices(self):
        for prefix in ([], ['1'], ['1', '2']):
            for invalid in ('', '  ', '0', '4', '-1', '1.0', '1 or 2', 'something else'):
                with self.subTest(prefix=prefix, invalid=invalid):
                    bot = TravelBuddy()
                    for answer in prefix:
                        bot.respond(answer)
                    previous = (bot.state.step, bot.state.trip_type, bot.state.accommodation, bot.state.activity)
                    options = bot.current_options()
                    reply = bot.respond(invalid)
                    self.assertEqual(previous, (bot.state.step, bot.state.trip_type, bot.state.accommodation, bot.state.activity))
                    for option in options:
                        self.assertIn(option, reply)
                    bot.respond('1')
                    self.assertNotEqual(bot.state.step, previous[0])

    def test_activities_are_specific_to_trip(self):
        expected = {
            '1': ('Swimming', 'Snorkeling', 'Sunset beach walk'),
            '2': ('Hiking', 'Mountain biking', 'Stargazing'),
            '3': ('Museum visit', 'Food tour', 'Walking tour'),
        }
        for trip, options in expected.items():
            bot = TravelBuddy()
            bot.respond(trip)
            reply = bot.respond('1')
            self.assertEqual(bot.current_options(), options)
            for option in options:
                self.assertIn(option, reply)
        bot = TravelBuddy()
        bot.respond('1')
        bot.respond('1')
        bot.respond('Museum visit')
        self.assertEqual(bot.state.step, Step.ACTIVITIES)
        self.assertIsNone(bot.state.activity)

    def test_exit_at_each_stage_keeps_previous_choices(self):
        for prefix in ([], ['2'], ['2', '3']):
            bot = TravelBuddy()
            for answer in prefix:
                bot.respond(answer)
            previous = (bot.state.trip_type, bot.state.accommodation, bot.state.activity)
            self.assertIn('Goodbye', bot.respond(' EXIT '))
            self.assertEqual(bot.state.step, Step.EXITED)
            self.assertEqual(previous, (bot.state.trip_type, bot.state.accommodation, bot.state.activity))

    def test_completed_choices_cannot_be_overwritten(self):
        bot = TravelBuddy()
        for answer in ('3', '2', '1'):
            bot.respond(answer)
        bot.respond('3')
        self.assertEqual(bot.state.activity, 'Museum visit')
        self.assertEqual(bot.state.step, Step.SUMMARY)


if __name__ == '__main__':
    unittest.main()
